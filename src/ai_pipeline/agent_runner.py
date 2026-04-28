from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .agents import ApiMapperAgent, AutomationAgent, RequirementAgent, TestcaseAgent
from .agents.role_profiles import render_role_profile_markdown
from .api_mapper_markdown import (
    render_api_catalog_markdown,
    render_api_source_request_markdown,
    render_dependency_graph_markdown,
    render_endpoint_mapping_markdown,
    render_request_schema_markdown,
)
from .artifact_store import EventLog, StageWorkspace
from .llm_runner import LocalPythonLLMRunner
from .openapi_loader import load_api_document
from .prompt_builder import build_stage_prompt
from .prompt_registry import PromptRegistry
from .role_loader import RoleLoader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute one pipeline agent stage in an isolated subprocess")
    parser.add_argument("--stage", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--input-path", action="append", default=[])
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    stage = StageWorkspace(
        run_id=args.run_id,
        run_dir=run_dir,
        agent_name=args.stage,
        event_log=EventLog(run_dir / "summary" / "run_log.jsonl"),
    )
    input_paths = [Path(path).resolve() for path in args.input_path]

    if args.stage == "requirement_agent":
        outputs = _run_requirement_stage(stage, input_paths[0])
    elif args.stage == "testcase_agent":
        outputs = _run_testcase_stage(stage)
    elif args.stage == "api_mapper_agent":
        outputs = _run_api_mapper_stage(stage, input_paths[0])
    elif args.stage == "automation_agent":
        outputs = _run_automation_stage(stage, run_dir)
    else:  # pragma: no cover - defensive branch
        raise ValueError(f"Unsupported stage: {args.stage}")

    print(json.dumps(outputs, ensure_ascii=False))


def _run_requirement_stage(stage: StageWorkspace, requirement_path: Path) -> dict[str, Any]:
    agent = RequirementAgent()
    profile = agent.role_profile()
    _write_role_profile(stage, profile)
    requirement_text = _read_stage_input_file(requirement_path)
    outputs = _invoke_with_stage_prompt(
        stage=stage,
        profile=profile,
        stage_input=_serialize_items({"requirement_document": requirement_text}),
        previous_output=None,
        execute=lambda: agent.run(requirement_path),
    )
    stage.write_output_json("requirement_model.json", outputs["requirement_model"])
    stage.write_output_json("acceptance_criteria.json", outputs["acceptance_criteria"])
    stage.write_output_text("business_flow.md", str(outputs["business_flow"]))
    stage.write_output_json("risk_points.json", outputs["risk_points"])
    stage.write_log("stage.log", "Requirement analysis completed in worker process.\n")
    return outputs


def _run_testcase_stage(stage: StageWorkspace) -> dict[str, Any]:
    agent = TestcaseAgent()
    profile = agent.role_profile()
    _write_role_profile(stage, profile)
    requirement_model = json.loads((stage.input_dir / "requirement_model.json").read_text(encoding="utf-8"))
    acceptance_criteria = json.loads((stage.input_dir / "acceptance_criteria.json").read_text(encoding="utf-8"))
    input_snapshot = {
        "requirement_model.json": requirement_model,
        "acceptance_criteria.json": acceptance_criteria,
    }
    outputs = _invoke_with_stage_prompt(
        stage=stage,
        profile=profile,
        stage_input=_serialize_items(input_snapshot),
        previous_output=_serialize_items(input_snapshot),
        execute=lambda: agent.run(requirement_model, acceptance_criteria),
    )
    stage.write_output_json("test_cases.json", outputs["test_cases"])
    stage.write_output_text("test_case_matrix.csv", str(outputs["test_case_matrix"]))
    stage.write_output_text("coverage_report.md", str(outputs["coverage_report"]))
    stage.write_log("stage.log", "Testcase design completed in worker process.\n")
    return outputs


def _run_api_mapper_stage(stage: StageWorkspace, api_doc_path: Path) -> dict[str, Any]:
    agent = ApiMapperAgent()
    profile = agent.role_profile()
    _write_role_profile(stage, profile)
    source_request_path = stage.input_dir / "api_source_request.json"
    if source_request_path.exists():
        source_request = json.loads(source_request_path.read_text(encoding="utf-8"))
    else:
        source_request = {
            "platform": "local_file",
            "project_id": "",
            "source_url": str(api_doc_path),
            "detail_fetch_mode": "local_api_document",
            "requested_endpoints": [],
        }
    stage.write_output_json("api_source_request.json", source_request)
    stage.write_output_text("apis/api_source_request.md", render_api_source_request_markdown(source_request))
    test_cases = json.loads((stage.input_dir / "test_cases.json").read_text(encoding="utf-8"))
    api_document = load_api_document(api_doc_path)
    input_snapshot = {
        "test_cases.json": test_cases,
        "api_source_request.json": source_request,
        "api_document": api_document,
    }
    outputs = _invoke_with_stage_prompt(
        stage=stage,
        profile=profile,
        stage_input=_serialize_items(input_snapshot),
        previous_output=_serialize_items({"test_cases.json": test_cases}),
        execute=lambda: agent.run(test_cases, api_document),
    )
    stage.write_output_json("api_catalog.json", outputs["api_catalog"])
    stage.write_output_json("endpoint_mapping.json", outputs["endpoint_mapping"])
    stage.write_output_json("request_schema.json", outputs["request_schema"])
    stage.write_output_json("dependency_graph.json", outputs["dependency_graph"])
    stage.write_output_text("apis/api_catalog.md", render_api_catalog_markdown(outputs["api_catalog"]))
    stage.write_output_text("apis/request_schema.md", render_request_schema_markdown(outputs["request_schema"]))
    stage.write_output_text("mappings/endpoint_mapping.md", render_endpoint_mapping_markdown(outputs["endpoint_mapping"]))
    stage.write_output_text("mappings/dependency_graph.md", render_dependency_graph_markdown(outputs["dependency_graph"]))
    stage.write_log("stage.log", "API mapping completed in worker process.\n")
    return outputs


def _run_automation_stage(stage: StageWorkspace, run_dir: Path) -> dict[str, Any]:
    agent = AutomationAgent()
    profile = agent.role_profile()
    _write_role_profile(stage, profile)
    endpoint_mapping = json.loads((stage.input_dir / "endpoint_mapping.json").read_text(encoding="utf-8"))
    test_cases = json.loads((stage.input_dir / "test_cases.json").read_text(encoding="utf-8"))
    input_snapshot = {
        "endpoint_mapping.json": endpoint_mapping,
        "test_cases.json": test_cases,
    }
    outputs = _invoke_with_stage_prompt(
        stage=stage,
        profile=profile,
        stage_input=_serialize_items(input_snapshot),
        previous_output=_serialize_items({"endpoint_mapping.json": endpoint_mapping}),
        execute=lambda: agent.run(
            run_id=stage.run_id,
            run_dir=run_dir,
            endpoint_mapping=endpoint_mapping,
            stage_workspace=stage,
        ),
    )
    return outputs


def _write_role_profile(stage: StageWorkspace, profile: dict[str, Any]) -> None:
    stage.write_log("role_profile.md", render_role_profile_markdown(profile))
    stage.write_log_json("role_profile.json", profile)


def _invoke_with_stage_prompt(
    *,
    stage: StageWorkspace,
    profile: dict[str, Any],
    stage_input: str,
    previous_output: str | None,
    execute,
) -> dict[str, Any]:
    prompt_registry = PromptRegistry.default()
    role_loader = RoleLoader.default()
    prompt_template_path = prompt_registry.get_for_agent(stage.agent_name)
    role_markdown_path = role_loader.role_path(stage.agent_name)
    prompt_template = prompt_template_path.read_text(encoding="utf-8")
    prompt = build_stage_prompt(
        agent_name=stage.agent_name,
        role_markdown=role_loader.load_markdown(stage.agent_name),
        stage_input=stage_input,
        previous_output=previous_output,
        output_requirement=_serialize_list(profile["output_contract"]),
        blocking_conditions=_serialize_list(profile["blocking_conditions"]),
        template_text=prompt_template,
    )
    return LocalPythonLLMRunner().invoke(
        stage=stage,
        agent_name=stage.agent_name,
        role_markdown_path=role_markdown_path,
        prompt_template_path=prompt_template_path,
        prompt=prompt,
        stage_input=stage_input,
        previous_output=previous_output,
        output_requirement=list(profile["output_contract"]),
        blocking_conditions=list(profile["blocking_conditions"]),
        execute=execute,
    )


def _serialize_items(payload: dict[str, Any]) -> str:
    parts = []
    for name, value in payload.items():
        if isinstance(value, str):
            rendered = value
        else:
            rendered = json.dumps(value, ensure_ascii=False, indent=2)
        parts.append(f"[{name}]\n{rendered}")
    return "\n\n".join(parts)


def _serialize_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _read_stage_input_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return f"[binary input omitted] {path.name}"


if __name__ == "__main__":
    main()
