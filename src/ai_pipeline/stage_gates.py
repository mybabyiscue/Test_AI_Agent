from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_store import StageWorkspace
from .agents.role_profiles import get_role_profile


def check_required_input_file(path: Path, agent_name: str) -> list[dict[str, str]]:
    if path.exists() and path.is_file():
        return []
    return [
        {
            "code": "missing_input_file",
            "message": f"{agent_name} 的输入文件不存在或不是文件。",
            "required": str(path),
        }
    ]


def check_requirement_gate(
    stage: StageWorkspace,
    outputs: dict[str, object],
    requirement_path: Path,
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    requirement_model = outputs.get("requirement_model")
    if not isinstance(requirement_model, dict):
        blockers.append(
            {
                "code": "missing_requirement_model",
                "message": "Agent 1 未输出结构化 requirement_model.json。",
                "required": "requirement_model.json",
            }
        )
    else:
        for field in ["requirement_id", "title", "scenarios"]:
            if not requirement_model.get(field):
                blockers.append(
                    {
                        "code": "incomplete_requirement_model",
                        "message": f"Agent 1 的 requirement_model.json 缺少必要字段：{field}。",
                        "required": field,
                    }
                )

    acceptance_criteria = outputs.get("acceptance_criteria")
    criteria = acceptance_criteria.get("criteria") if isinstance(acceptance_criteria, dict) else None
    if not isinstance(criteria, list):
        blockers.append(
            {
                "code": "missing_acceptance_criteria",
                "message": "Agent 1 未输出可供 Agent 2 消费的验收关注点。",
                "required": "acceptance_criteria.criteria",
            }
        )

    if requirement_path.suffix.lower() == ".pdf":
        for required_file in ["pdf_source_snapshot.json", "pdf_extracted_text.md"]:
            if not (stage.output_dir / required_file).exists():
                blockers.append(
                    {
                        "code": "missing_pdf_artifact",
                        "message": f"PDF 输入必须由 Agent 1 产出 {required_file}，否则不能进入 Agent 2。",
                        "required": required_file,
                    }
                )
    return blockers


def check_testcase_gate(
    stage: StageWorkspace,
    outputs: dict[str, object],
    *,
    require_test_points: bool,
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    test_cases = outputs.get("test_cases")
    cases = test_cases.get("cases") if isinstance(test_cases, dict) else None
    if not isinstance(cases, list) or not cases:
        blockers.append(
            {
                "code": "missing_test_cases",
                "message": "Agent 2 未输出可供 Agent 3 消费的测试用例集合。",
                "required": "test_cases.cases",
            }
        )
    else:
        for case in cases:
            missing_fields = [
                field
                for field in ["test_case_id", "requirement_id", "title", "priority", "expected_status_codes"]
                if not isinstance(case, dict) or not case.get(field)
            ]
            if missing_fields:
                blockers.append(
                    {
                        "code": "incomplete_test_case",
                        "message": f"Agent 2 存在字段不完整的测试用例：{', '.join(missing_fields)}。",
                        "required": ",".join(missing_fields),
                    }
                )
                break

    if require_test_points and not (stage.output_dir / "test_points.json").exists():
        blockers.append(
            {
                "code": "missing_test_points",
                "message": "Agent 2 必须输出 test_points.json，建立需求点、测试点和用例之间的追溯关系。",
                "required": "test_points.json",
            }
        )
    return blockers


def check_api_mapper_gate(
    stage: StageWorkspace,
    outputs: dict[str, object],
    *,
    require_database_context: bool,
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    endpoint_mapping = outputs.get("endpoint_mapping")
    mappings = endpoint_mapping.get("mappings") if isinstance(endpoint_mapping, dict) else None
    if not isinstance(mappings, list) or not mappings:
        blockers.append(
            {
                "code": "missing_endpoint_mapping",
                "message": "Agent 3 未输出测试用例到真实接口的映射关系。",
                "required": "endpoint_mapping.mappings",
            }
        )
    else:
        for mapping in mappings:
            missing_fields = [
                field
                for field in ["test_case_id", "path", "method", "request_body", "response_body", "auth_type"]
                if not isinstance(mapping, dict) or field not in mapping
            ]
            if missing_fields:
                blockers.append(
                    {
                        "code": "incomplete_interface_mapping",
                        "message": f"Agent 3 的接口映射缺少必要契约字段：{', '.join(missing_fields)}。",
                        "required": ",".join(missing_fields),
                    }
                )
                break

    if require_database_context:
        for required_file in ["database_mapping.json", "missing_database_report.md"]:
            if not (stage.output_dir / required_file).exists():
                blockers.append(
                    {
                        "code": "missing_database_context",
                        "message": f"Agent 3 必须输出数据库结构上下文产物 {required_file}，否则 Agent 4 不能造数或验证状态。",
                        "required": required_file,
                    }
                )
    return blockers


def check_automation_input_gate(
    stage: StageWorkspace,
    *,
    require_agent4_excel: bool,
    agent4_excel_confirmed: bool,
) -> list[dict[str, str]]:
    if not require_agent4_excel:
        return []
    from .config import project_root

    template_name = "Agent4自动化执行输入模板_鉴权约束修正版.xlsx"
    template_path = project_root() / "workspace" / "templates" / template_name
    if not agent4_excel_confirmed:
        return [
            {
                "code": "agent4_excel_not_confirmed",
                "message": "Agent 4 到达自动化阶段后必须先等待用户填写并确认 Excel 输入模板，不能直接生成脚本或执行。",
                "required": str(template_path),
            }
        ]
    if not template_path.exists():
        return [
            {
                "code": "agent4_excel_template_missing",
                "message": "用户未上传模板时，统一路径下必须存在 Agent 4 Excel 输入模板。",
                "required": str(template_path),
            }
        ]
    return []


def stage_required_output_files(agent_name: str) -> list[str]:
    return {
        "requirement_agent": [
            "responsibility_confirmation.json",
            "requirement_model.json",
            "acceptance_criteria.json",
            "business_flow.md",
            "risk_points.json",
        ],
        "testcase_agent": [
            "responsibility_confirmation.json",
            "test_points.json",
            "test_cases.json",
            "test_case_matrix.csv",
            "coverage_report.md",
        ],
        "api_mapper_agent": [
            "responsibility_confirmation.json",
            "apis/api_source_request.md",
            "api_catalog.json",
            "apis/api_catalog.md",
            "database/database_catalog.json",
            "database/database_catalog.md",
            "database_mapping.json",
            "mappings/database_mapping.md",
            "missing_database_report.md",
            "mappings/missing_database_report.md",
            "endpoint_mapping.json",
            "mappings/endpoint_mapping.md",
            "request_schema.json",
            "apis/request_schema.md",
            "dependency_graph.json",
            "mappings/dependency_graph.md",
        ],
        "automation_agent": [
            "responsibility_confirmation.json",
            "automation_plan.json",
            "generated_tests/test_generated_api_cases.py",
            "execution_report.json",
            "allure_report_viewing_guide.md",
        ],
    }[agent_name]


def stage_blocking_conditions(role_profile: dict[str, Any]) -> list[str]:
    return [
        "required input or precondition is missing",
        "responsibility boundary is unclear",
        "continuing would cause role overreach or distorted results",
        "downstream stage cannot consume this stage's output",
        *role_profile["quality_gates"],
        *role_profile.get("blocking_conditions", []),
    ]


def detect_responsibility_overreach(stage: StageWorkspace) -> list[str]:
    forbidden_by_stage = {
        "requirement_agent": ["generated_tests/", "automation_plan.json", "endpoint_mapping.json"],
        "testcase_agent": ["generated_tests/", "automation_plan.json", "api_catalog.json", "endpoint_mapping.json"],
        "api_mapper_agent": ["generated_tests/", "automation_plan.json", "execution_report.json"],
        "automation_agent": [],
    }
    forbidden_patterns = forbidden_by_stage.get(stage.agent_name, [])
    output_files = [
        str(path.relative_to(stage.output_dir)).replace("\\", "/")
        for path in stage.output_dir.rglob("*")
        if path.is_file()
    ]
    return [
        output_file
        for output_file in output_files
        if any(pattern in output_file for pattern in forbidden_patterns)
    ]


def identify_responsibility(
    stage: StageWorkspace,
    blockers: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    role_profile = get_role_profile(stage.agent_name)
    blockers = blockers or []
    input_files = sorted(str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file())
    output_requirements = stage_required_output_files(stage.agent_name)
    can_start = not blockers
    self_check = {
        "responsibility_boundary_is_clear": True,
        "attempting_out_of_scope_work": False,
        "input_is_sufficient": can_start,
        "must_block": not can_start,
        "continuing_would_cause_overreach_or_distortion": not can_start,
    }
    confirmation = {
        "agent_name": stage.agent_name,
        "responsibility_positioning": role_profile["mission"],
        "responsibility_confirmation": role_profile["mission"],
        "should_do": role_profile["responsibilities"],
        "should_not_do": role_profile["forbidden_actions"],
        "input_dependencies": role_profile["input_contract"],
        "current_input_files": input_files,
        "output_requirements": output_requirements,
        "completion_criteria": role_profile["quality_gates"],
        "blocking_conditions": stage_blocking_conditions(role_profile),
        "can_start": can_start,
        "missing_inputs_or_preconditions": blockers,
        "responsibility_self_check": self_check,
        "policy": {
            "must_identify_responsibility_before_run": True,
            "must_block_when_key_input_missing": True,
            "no_partial_execution_with_missing_input": True,
        },
    }
    stage.write_output_json("responsibility_confirmation.json", confirmation)
    stage.write_output_text("responsibility_confirmation.md", render_responsibility_confirmation(confirmation))
    stage.event_log.record(
        stage.agent_name,
        "responsibility_identified",
        can_start=can_start,
        blockers=blockers,
    )
    return confirmation


def validate_completion(
    stage: StageWorkspace,
    blockers: list[dict[str, str]],
) -> dict[str, object]:
    required_outputs = stage_required_output_files(stage.agent_name)
    missing_outputs = [
        output_path
        for output_path in required_outputs
        if not (stage.output_dir / output_path).exists()
    ]
    overreach_outputs = detect_responsibility_overreach(stage)
    remaining_blockers = list(blockers)
    for missing_output in missing_outputs:
        remaining_blockers.append(
            {
                "code": "missing_required_stage_output",
                "message": f"{stage.agent_name} did not produce required output: {missing_output}",
                "required": missing_output,
            }
        )
    for overreach_output in overreach_outputs:
        remaining_blockers.append(
            {
                "code": "responsibility_overreach",
                "message": f"{stage.agent_name} produced an out-of-scope artifact: {overreach_output}",
                "required": "remove out-of-scope artifact before handoff",
            }
        )

    can_enter_next_stage = not remaining_blockers
    completion = {
        "agent_name": stage.agent_name,
        "can_enter_next_stage": can_enter_next_stage,
        "completion_check": {
            "required_outputs_complete": not missing_outputs,
            "responsibility_overreach_detected": bool(overreach_outputs),
            "overreach_outputs": overreach_outputs,
            "required_responsibilities_missing": bool(missing_outputs or blockers),
            "missing_outputs": missing_outputs,
            "remaining_blockers": remaining_blockers,
            "next_stage_ready": can_enter_next_stage,
        },
        "policy": {
            "success_is_not_file_existence_only": True,
            "must_validate_role_completion_before_next_stage": True,
        },
    }
    stage.write_output_json("completion_validation.json", completion)
    stage.write_output_text("completion_validation.md", render_completion_validation(completion))
    stage.event_log.record(
        stage.agent_name,
        "completion_validated",
        can_enter_next_stage=can_enter_next_stage,
        blockers=remaining_blockers,
    )
    blockers[:] = remaining_blockers
    return completion


def render_responsibility_confirmation(confirmation: dict[str, object]) -> str:
    lines = [
        "# Current Responsibility Confirmation",
        "",
        f"- Agent: {confirmation['agent_name']}",
        f"- Can start: {confirmation['can_start']}",
        "",
        "## Responsibility Positioning",
        "",
        str(confirmation["responsibility_positioning"]),
        "",
        "## Should Do",
    ]
    lines.extend(f"- {item}" for item in confirmation["should_do"])  # type: ignore[index]
    lines.extend(["", "## Should Not Do"])
    lines.extend(f"- {item}" for item in confirmation["should_not_do"])  # type: ignore[index]
    lines.extend(["", "## Input Dependencies"])
    lines.extend(f"- {item}" for item in confirmation["input_dependencies"])  # type: ignore[index]
    lines.extend(["", "## Output Requirements"])
    lines.extend(f"- {item}" for item in confirmation["output_requirements"])  # type: ignore[index]
    lines.extend(["", "## Blocking Conditions"])
    lines.extend(f"- {item}" for item in confirmation["blocking_conditions"])  # type: ignore[index]
    lines.extend(["", "## Missing Inputs Or Preconditions"])
    missing = confirmation["missing_inputs_or_preconditions"]  # type: ignore[index]
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def render_completion_validation(completion: dict[str, object]) -> str:
    check = completion["completion_check"]  # type: ignore[index]
    lines = [
        "# Responsibility Completion Validation",
        "",
        f"- Agent: {completion['agent_name']}",
        f"- Can enter next stage: {completion['can_enter_next_stage']}",
        f"- Required outputs complete: {check['required_outputs_complete']}",
        f"- Responsibility overreach detected: {check['responsibility_overreach_detected']}",
        f"- Required responsibilities missing: {check['required_responsibilities_missing']}",
        f"- Next stage ready: {check['next_stage_ready']}",
        "",
        "## Remaining Blockers",
    ]
    blockers = check["remaining_blockers"]
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"
