from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .agents import ApiMapperAgent, AutomationAgent, RequirementAgent, TestcaseAgent
from .agents.role_profiles import render_role_profile_markdown
from .artifact_store import EventLog, StageWorkspace
from .openapi_loader import load_api_document


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
        event_log=EventLog(run_dir / "event_log.jsonl"),
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
    _write_role_profile(stage, agent.role_profile())
    outputs = agent.run(requirement_path)
    stage.write_output_json("requirement_model.json", outputs["requirement_model"])
    stage.write_output_json("acceptance_criteria.json", outputs["acceptance_criteria"])
    stage.write_output_text("business_flow.md", str(outputs["business_flow"]))
    stage.write_output_json("risk_points.json", outputs["risk_points"])
    stage.write_log("stage.log", "Requirement analysis completed in worker process.\n")
    return outputs


def _run_testcase_stage(stage: StageWorkspace) -> dict[str, Any]:
    agent = TestcaseAgent()
    _write_role_profile(stage, agent.role_profile())
    requirement_model = json.loads((stage.input_dir / "requirement_model.json").read_text(encoding="utf-8"))
    acceptance_criteria = json.loads((stage.input_dir / "acceptance_criteria.json").read_text(encoding="utf-8"))
    outputs = agent.run(requirement_model, acceptance_criteria)
    stage.write_output_json("test_cases.json", outputs["test_cases"])
    stage.write_output_text("test_case_matrix.csv", str(outputs["test_case_matrix"]))
    stage.write_output_text("coverage_report.md", str(outputs["coverage_report"]))
    stage.write_log("stage.log", "Testcase design completed in worker process.\n")
    return outputs


def _run_api_mapper_stage(stage: StageWorkspace, api_doc_path: Path) -> dict[str, Any]:
    agent = ApiMapperAgent()
    _write_role_profile(stage, agent.role_profile())
    source_request_path = stage.input_dir / "api_source_request.json"
    if source_request_path.exists():
        source_request = json.loads(source_request_path.read_text(encoding="utf-8"))
        stage.write_output_json("api_source_request.json", source_request)
    test_cases = json.loads((stage.input_dir / "test_cases.json").read_text(encoding="utf-8"))
    api_document = load_api_document(api_doc_path)
    outputs = agent.run(test_cases, api_document)
    stage.write_output_json("api_catalog.json", outputs["api_catalog"])
    stage.write_output_json("endpoint_mapping.json", outputs["endpoint_mapping"])
    stage.write_output_json("request_schema.json", outputs["request_schema"])
    stage.write_output_json("dependency_graph.json", outputs["dependency_graph"])
    stage.write_log("stage.log", "API mapping completed in worker process.\n")
    return outputs


def _run_automation_stage(stage: StageWorkspace, run_dir: Path) -> dict[str, Any]:
    agent = AutomationAgent()
    _write_role_profile(stage, agent.role_profile())
    endpoint_mapping = json.loads((stage.input_dir / "endpoint_mapping.json").read_text(encoding="utf-8"))
    outputs = agent.run(
        run_id=stage.run_id,
        run_dir=run_dir,
        endpoint_mapping=endpoint_mapping,
        stage_workspace=stage,
    )
    return outputs


def _write_role_profile(stage: StageWorkspace, profile: dict[str, Any]) -> None:
    stage.write_output_text("role_profile.md", render_role_profile_markdown(profile))
    stage.write_output_json("role_profile.json", profile)


if __name__ == "__main__":
    main()
