from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .api_document_resolver import ApiDocumentResolver
from .artifact_store import ArtifactStore, EventLog, StageWorkspace, utc_now_iso
from .config import examples_root, project_root
from .contracts import PipelineRunResult
from .agents import ApiMapperAgent, AutomationAgent, RequirementAgent, TestcaseAgent
from .agents.role_profiles import get_role_profile


class PipelineOrchestrator:
    def __init__(self, api_document_resolver: Any | None = None) -> None:
        self.requirement_agent = RequirementAgent()
        self.testcase_agent = TestcaseAgent()
        self.api_mapper_agent = ApiMapperAgent()
        self.automation_agent = AutomationAgent()
        self.api_document_resolver = api_document_resolver or ApiDocumentResolver.default()

    def run(
        self,
        requirement_path: Path,
        workspace_root: Path,
        run_id: str,
        api_doc_path: Path | None = None,
        api_source_url: str | None = None,
        test_env_profile: str | None = None,
        require_test_points: bool = True,
        require_database_context: bool = True,
        require_agent4_excel: bool = True,
        agent4_excel_confirmed: bool = False,
    ) -> PipelineRunResult:
        if bool(api_doc_path) == bool(api_source_url):
            raise ValueError("必须且只能提供 api_doc_path 或 api_source_url 其中一个。")

        run_dir = workspace_root.resolve() / "runs" / run_id
        if run_dir.exists():
            shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        store = ArtifactStore(run_dir)
        event_log = EventLog(run_dir / "event_log.jsonl")

        requirement_stage = StageWorkspace(run_id, run_dir, "requirement_agent", event_log)
        precheck_blockers = self._check_required_input_file(requirement_path, self.requirement_agent.agent_name)
        if precheck_blockers:
            self._identify_responsibility(requirement_stage, blockers=precheck_blockers)
            return self._block_pipeline(
                store=store,
                stage=requirement_stage,
                blocked_at="before",
                blockers=precheck_blockers,
                executed_stages=[],
            )
        staged_requirement_path = requirement_stage.copy_input(requirement_path)
        self._identify_responsibility(requirement_stage)
        requirement_outputs = self._run_requirement_stage(requirement_stage, staged_requirement_path)
        blockers = self._check_requirement_gate(requirement_stage, requirement_outputs, staged_requirement_path)
        self._validate_completion(requirement_stage, blockers)
        if blockers:
            return self._block_pipeline(
                store=store,
                stage=requirement_stage,
                blocked_at="after",
                blockers=blockers,
                executed_stages=[self.requirement_agent.stage_name],
            )

        testcase_stage = StageWorkspace(run_id, run_dir, "testcase_agent", event_log)
        testcase_stage.write_input_json("requirement_model.json", requirement_outputs["requirement_model"])
        testcase_stage.write_input_json("acceptance_criteria.json", requirement_outputs["acceptance_criteria"])
        self._identify_responsibility(testcase_stage)
        testcase_outputs = self._run_testcase_stage(
            testcase_stage,
            requirement_outputs["requirement_model"],
            requirement_outputs["acceptance_criteria"],
        )
        blockers = self._check_testcase_gate(testcase_stage, testcase_outputs, require_test_points=require_test_points)
        self._validate_completion(testcase_stage, blockers)
        if blockers:
            return self._block_pipeline(
                store=store,
                stage=testcase_stage,
                blocked_at="after",
                blockers=blockers,
                executed_stages=[self.requirement_agent.stage_name, self.testcase_agent.stage_name],
            )

        api_mapper_stage = StageWorkspace(run_id, run_dir, "api_mapper_agent", event_log)
        api_mapper_stage.write_input_json("test_cases.json", testcase_outputs["test_cases"])
        staged_api_doc_path = self._prepare_api_mapper_input(
            api_mapper_stage,
            api_doc_path=api_doc_path,
            api_source_url=api_source_url,
        )
        self._identify_responsibility(api_mapper_stage)
        mapping_outputs = self._run_api_mapper_stage(api_mapper_stage, staged_api_doc_path)
        blockers = self._check_api_mapper_gate(
            api_mapper_stage,
            mapping_outputs,
            require_database_context=require_database_context,
        )
        self._validate_completion(api_mapper_stage, blockers)
        if blockers:
            return self._block_pipeline(
                store=store,
                stage=api_mapper_stage,
                blocked_at="after",
                blockers=blockers,
                executed_stages=[
                    self.requirement_agent.stage_name,
                    self.testcase_agent.stage_name,
                    self.api_mapper_agent.stage_name,
                ],
            )

        automation_stage = StageWorkspace(run_id, run_dir, "automation_agent", event_log)
        automation_stage.write_input_json("endpoint_mapping.json", mapping_outputs["endpoint_mapping"])
        automation_stage.write_input_json("test_cases.json", testcase_outputs["test_cases"])
        blockers = self._check_automation_input_gate(
            automation_stage,
            require_agent4_excel=require_agent4_excel,
            agent4_excel_confirmed=agent4_excel_confirmed,
        )
        self._identify_responsibility(automation_stage, blockers=blockers)
        if blockers:
            return self._block_pipeline(
                store=store,
                stage=automation_stage,
                blocked_at="before",
                blockers=blockers,
                executed_stages=[
                    self.requirement_agent.stage_name,
                    self.testcase_agent.stage_name,
                    self.api_mapper_agent.stage_name,
                ],
            )
        automation_outputs = self._run_automation_stage(
            automation_stage,
            run_id=run_id,
            run_dir=run_dir,
            endpoint_mapping=mapping_outputs["endpoint_mapping"],
            test_env_profile=test_env_profile,
        )
        self._validate_completion(automation_stage, [])
        traceability_report = self._build_traceability_report(
            run_id,
            requirement_outputs["requirement_model"],
            testcase_outputs["test_cases"],
            mapping_outputs["endpoint_mapping"],
        )
        store.write_json("reports/traceability_report.json", traceability_report)
        store.write_text(
            "reports/final_summary.md",
            self._build_final_summary(automation_outputs["execution_report"]),
        )
        artifact_inventory = self._build_artifact_inventory(run_dir)
        store.write_json("reports/artifact_inventory.json", artifact_inventory)

        manifest = {
            "run_id": run_id,
            "record_policy": {
                "record_dir": str(run_dir),
                "storage_rule": "all_outputs_must_stay_under_requirement_record_dir",
                "output_file_explanation_rule": {
                    "language": "中文",
                    "required_fields": ["file_name", "purpose", "main_contents", "stage"],
                    "rule": "后续所有输出文件都必须在产物清单和记录索引中附带中文解释说明，禁止只输出文件路径或文件名。",
                },
                "file_types": [".json", ".md", ".csv", ".py", "directory"],
                "required_groups": [
                    "inputs",
                    "requirement_analysis",
                    "testcases",
                    "api_assets",
                    "automation",
                    "logs",
                    "reports",
                ],
            },
            "stages": [
                self.requirement_agent.stage_name,
                self.testcase_agent.stage_name,
                self.api_mapper_agent.stage_name,
                self.automation_agent.stage_name,
            ],
            "artifacts": {
                "requirements": "requirement_agent/output/requirement_model.json",
                "testcases": "testcase_agent/output/test_cases.json",
                "api_mapping": "api_mapper_agent/output/endpoint_mapping.json",
                "automation": "automation_agent/output/automation_plan.json",
                "report": "reports/traceability_report.json",
                "record_index": "record_index.md",
                "artifact_inventory": "reports/artifact_inventory.json",
            },
            "stage_workspaces": {
                "requirement_agent": "requirement_agent",
                "testcase_agent": "testcase_agent",
                "api_mapper_agent": "api_mapper_agent",
                "automation_agent": "automation_agent",
            },
        }
        manifest_path = run_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        store.write_text("record_index.md", self._build_record_index(manifest, artifact_inventory))
        return PipelineRunResult(run_id=run_id, run_dir=run_dir, manifest_path=manifest_path)

    def _identify_responsibility(
        self,
        stage: StageWorkspace,
        blockers: list[dict[str, str]] | None = None,
    ) -> dict[str, object]:
        role_profile = get_role_profile(stage.agent_name)
        blockers = blockers or []
        input_files = sorted(str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file())
        output_requirements = self._stage_required_output_files(stage.agent_name)
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
            "blocking_conditions": self._stage_blocking_conditions(role_profile),
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
        stage.write_output_text("responsibility_confirmation.md", self._render_responsibility_confirmation(confirmation))
        stage.event_log.record(
            stage.agent_name,
            "responsibility_identified",
            can_start=can_start,
            blockers=blockers,
        )
        return confirmation

    def _validate_completion(
        self,
        stage: StageWorkspace,
        blockers: list[dict[str, str]],
    ) -> dict[str, object]:
        required_outputs = self._stage_required_output_files(stage.agent_name)
        missing_outputs = [
            output_path
            for output_path in required_outputs
            if not (stage.output_dir / output_path).exists()
        ]
        overreach_outputs = self._detect_responsibility_overreach(stage)
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
        stage.write_output_text("completion_validation.md", self._render_completion_validation(completion))
        stage.event_log.record(
            stage.agent_name,
            "completion_validated",
            can_enter_next_stage=can_enter_next_stage,
            blockers=remaining_blockers,
        )
        blockers[:] = remaining_blockers
        return completion

    def _stage_required_output_files(self, agent_name: str) -> list[str]:
        return {
            "requirement_agent": [
                "responsibility_confirmation.json",
                "requirement_model.json",
                "acceptance_criteria.json",
                "business_flow.md",
                "risk_points.json",
                "role_profile.md",
                "role_profile.json",
            ],
            "testcase_agent": [
                "responsibility_confirmation.json",
                "test_cases.json",
                "test_case_matrix.csv",
                "coverage_report.md",
                "role_profile.md",
                "role_profile.json",
            ],
            "api_mapper_agent": [
                "responsibility_confirmation.json",
                "api_catalog.json",
                "endpoint_mapping.json",
                "request_schema.json",
                "dependency_graph.json",
                "role_profile.md",
                "role_profile.json",
            ],
            "automation_agent": [
                "responsibility_confirmation.json",
                "automation_plan.json",
                "generated_tests/test_generated_api_cases.py",
                "execution_report.json",
                "allure_report_viewing_guide.md",
                "role_profile.md",
                "role_profile.json",
            ],
        }[agent_name]

    def _stage_blocking_conditions(self, role_profile: dict[str, Any]) -> list[str]:
        return [
            "required input or precondition is missing",
            "responsibility boundary is unclear",
            "continuing would cause role overreach or distorted results",
            "downstream stage cannot consume this stage's output",
            *role_profile["quality_gates"],
        ]

    def _detect_responsibility_overreach(self, stage: StageWorkspace) -> list[str]:
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

    def _render_responsibility_confirmation(self, confirmation: dict[str, object]) -> str:
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

    def _render_completion_validation(self, completion: dict[str, object]) -> str:
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

    def _check_required_input_file(self, path: Path, agent_name: str) -> list[dict[str, str]]:
        if path.exists() and path.is_file():
            return []
        return [
            {
                "code": "missing_input_file",
                "message": f"{agent_name} 的输入文件不存在或不是文件。",
                "required": str(path),
            }
        ]

    def _check_requirement_gate(
        self,
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

    def _check_testcase_gate(
        self,
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

    def _check_api_mapper_gate(
        self,
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

    def _check_automation_input_gate(
        self,
        stage: StageWorkspace,
        *,
        require_agent4_excel: bool,
        agent4_excel_confirmed: bool,
    ) -> list[dict[str, str]]:
        if not require_agent4_excel:
            return []
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

    def _block_pipeline(
        self,
        *,
        store: ArtifactStore,
        stage: StageWorkspace,
        blocked_at: str,
        blockers: list[dict[str, str]],
        executed_stages: list[str],
    ) -> PipelineRunResult:
        finished_at = utc_now_iso()
        input_files = sorted(str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file())
        output_files = sorted(str(path.relative_to(stage.run_dir)) for path in stage.output_dir.rglob("*") if path.is_file())
        role_profile = get_role_profile(stage.agent_name)
        stage.update_state(
            status="blocked",
            input_files=input_files,
            output_files=output_files,
            finished_at=finished_at,
            error_message="; ".join(blocker["message"] for blocker in blockers),
            executor={"mode": "gate", "blocked_at": blocked_at},
            role_profile=role_profile,
        )
        stage.event_log.record(
            stage.agent_name,
            "stage_blocked",
            finished_at=finished_at,
            blocked_at=blocked_at,
            blockers=blockers,
        )

        blocking_report = {
            "run_id": stage.run_id,
            "status": "blocked",
            "blocked_stage": stage.agent_name,
            "blocked_at": blocked_at,
            "blockers": blockers,
            "executed_stages": executed_stages,
            "policy": {
                "rule": "按职责推进、按门禁放行、缺失即阻断。",
                "no_default_or_hardcoded_fallback": True,
            },
        }
        blocking_report_path = store.write_json("reports/blocking_report.json", blocking_report)
        artifact_inventory = self._build_artifact_inventory(stage.run_dir)
        store.write_json("reports/artifact_inventory.json", artifact_inventory)

        manifest = {
            "run_id": stage.run_id,
            "status": "blocked",
            "blocked_stage": stage.agent_name,
            "blocking_report": "reports/blocking_report.json",
            "stages": executed_stages,
            "record_policy": {
                "record_dir": str(stage.run_dir),
                "storage_rule": "all_outputs_must_stay_under_requirement_record_dir",
                "output_file_explanation_rule": {
                    "language": "中文",
                    "required_fields": ["file_name", "purpose", "main_contents", "stage"],
                    "rule": "流程阻断时必须输出阻塞原因，禁止继续推进下游 Agent。",
                },
                "file_types": [".json", ".md", ".csv", ".py", "directory"],
                "required_groups": ["inputs", "logs", "reports"],
            },
            "artifacts": {
                "blocking_report": "reports/blocking_report.json",
                "artifact_inventory": "reports/artifact_inventory.json",
            },
            "stage_workspaces": {
                stage.agent_name: stage.agent_name,
            },
        }
        manifest_path = stage.run_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        store.write_text("record_index.md", self._build_record_index(manifest, artifact_inventory))
        return PipelineRunResult(
            run_id=stage.run_id,
            run_dir=stage.run_dir,
            manifest_path=manifest_path,
            status="blocked",
            blocked_stage=stage.agent_name,
            blocking_report_path=blocking_report_path,
        )

    def _run_requirement_stage(self, stage: StageWorkspace, requirement_path: Path) -> dict[str, object]:
        input_files = [str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file()]
        started_at = utc_now_iso()
        executor = self._run_stage_subprocess(stage, started_at, input_files, [requirement_path])
        return self._load_requirement_outputs(stage)

    def _run_testcase_stage(
        self,
        stage: StageWorkspace,
        requirement_model: dict[str, object],
        acceptance_criteria: dict[str, object],
    ) -> dict[str, object]:
        input_files = [str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file()]
        started_at = utc_now_iso()
        self._run_stage_subprocess(stage, started_at, input_files, [])
        return self._load_testcase_outputs(stage)

    def _run_api_mapper_stage(
        self,
        stage: StageWorkspace,
        api_doc_path: Path,
    ) -> dict[str, object]:
        input_files = [str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file()]
        started_at = utc_now_iso()
        self._run_stage_subprocess(stage, started_at, input_files, [api_doc_path])
        return self._load_api_mapper_outputs(stage)

    def _prepare_api_mapper_input(
        self,
        stage: StageWorkspace,
        *,
        api_doc_path: Path | None,
        api_source_url: str | None,
    ) -> Path:
        if api_doc_path is not None:
            staged_api_doc = stage.copy_input(api_doc_path)
            api_document = json.loads(staged_api_doc.read_text(encoding="utf-8-sig"))
            if self._is_basic_apifox_index(api_document):
                project_id = str(api_document["project_id"])
                source_url = str(api_document.get("source_url") or f"https://app.apifox.com/project/{project_id}")
                declaration = self.api_mapper_agent.declare_api_source(source_url)
                detailed_document = self.api_document_resolver.resolve_apifox_project(project_id)
                stage.write_input_json("api_source_request.json", declaration)
                stage.write_input_json(
                    "api_source_resolved.json",
                    {
                        "platform": "apifox",
                        "url": source_url,
                        "project_id": project_id,
                        "resource_type": "project",
                        "resource_id": None,
                    },
                )
                stage.write_input_json("api_knowledge_index.json", api_document)
                return stage.write_input_json("api_document.json", detailed_document)
            return staged_api_doc

        if api_source_url is None:
            raise ValueError("缺少接口来源，请提供 api_doc_path 或 api_source_url。")

        declaration = self.api_mapper_agent.declare_api_source(api_source_url)
        source, api_document = self.api_document_resolver.resolve_apifox_url(api_source_url)
        stage.write_input_json("api_source_request.json", declaration)
        stage.write_input_json("api_source_resolved.json", source.to_declaration())
        return stage.write_input_json("api_document.json", api_document)

    def _is_basic_apifox_index(self, api_document: dict[str, Any]) -> bool:
        return (
            api_document.get("platform") == "apifox"
            and bool(api_document.get("project_id"))
            and "paths" not in api_document
            and isinstance(api_document.get("apis"), list)
        )

    def _run_automation_stage(
        self,
        stage: StageWorkspace,
        *,
        run_id: str,
        run_dir: Path,
        endpoint_mapping: dict[str, object],
        test_env_profile: str | None,
    ) -> dict[str, object]:
        input_files = [str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file()]
        started_at = utc_now_iso()
        extra_env = {"AI_PIPELINE_TEST_ENV_PROFILE": test_env_profile} if test_env_profile else None
        self._run_stage_subprocess(stage, started_at, input_files, [], extra_env=extra_env)
        return self._load_automation_outputs(stage)

    def _run_stage_subprocess(
        self,
        stage: StageWorkspace,
        started_at: str,
        input_files: list[str],
        input_paths: list[Path],
        extra_env: dict[str, str | None] | None = None,
    ) -> dict[str, Any]:
        command = [
            sys.executable,
            "-m",
            "ai_pipeline.agent_runner",
            "--stage",
            stage.agent_name,
            "--run-id",
            stage.run_id,
            "--run-dir",
            str(stage.run_dir),
        ]
        for input_path in input_paths:
            command.extend(["--input-path", str(input_path)])

        role_profile = get_role_profile(stage.agent_name)
        stage.update_state(
            status="running",
            input_files=input_files,
            output_files=[],
            started_at=started_at,
            executor={"mode": "subprocess", "command": command, "pid": None, "exit_code": None},
            role_profile=role_profile,
        )
        stage.event_log.record(stage.agent_name, "stage_started", started_at=started_at, command=command)

        env = dict(os.environ)
        src_path = str(project_root() / "src")
        env["PYTHONPATH"] = src_path + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        env["PYTHONIOENCODING"] = "utf-8"
        if extra_env:
            env.update({key: value for key, value in extra_env.items() if value is not None})

        process = subprocess.Popen(
            command,
            cwd=project_root(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        stdout, stderr = process.communicate()
        stage.write_log("worker_stdout.log", stdout)
        stage.write_log("worker_stderr.log", stderr)

        output_files = sorted(str(path.relative_to(stage.run_dir)) for path in stage.output_dir.rglob("*") if path.is_file())
        finished_at = utc_now_iso()
        executor = {
            "mode": "subprocess",
            "command": command,
            "pid": process.pid,
            "exit_code": process.returncode,
        }

        if process.returncode != 0:
            error_message = stderr.strip() or stdout.strip() or f"Stage {stage.agent_name} failed."
            stage.update_state(
                status="failed",
                input_files=input_files,
                output_files=output_files,
                started_at=started_at,
                finished_at=finished_at,
                error_message=error_message,
                executor=executor,
                role_profile=role_profile,
            )
            stage.event_log.record(
                stage.agent_name,
                "stage_failed",
                finished_at=finished_at,
                exit_code=process.returncode,
            )
            raise RuntimeError(error_message)

        stage.update_state(
            status="success",
            input_files=input_files,
            output_files=output_files,
            started_at=started_at,
            finished_at=finished_at,
            executor=executor,
            role_profile=role_profile,
        )
        stage.event_log.record(
            stage.agent_name,
            "stage_completed",
            finished_at=finished_at,
            output_files=output_files,
            exit_code=process.returncode,
            pid=process.pid,
        )
        return {"stdout": stdout, "stderr": stderr, "executor": executor}

    def _load_requirement_outputs(self, stage: StageWorkspace) -> dict[str, object]:
        return {
            "requirement_model": json.loads((stage.output_dir / "requirement_model.json").read_text(encoding="utf-8")),
            "acceptance_criteria": json.loads((stage.output_dir / "acceptance_criteria.json").read_text(encoding="utf-8")),
            "business_flow": (stage.output_dir / "business_flow.md").read_text(encoding="utf-8"),
            "risk_points": json.loads((stage.output_dir / "risk_points.json").read_text(encoding="utf-8")),
        }

    def _load_testcase_outputs(self, stage: StageWorkspace) -> dict[str, object]:
        return {
            "test_cases": json.loads((stage.output_dir / "test_cases.json").read_text(encoding="utf-8")),
            "test_case_matrix": (stage.output_dir / "test_case_matrix.csv").read_text(encoding="utf-8"),
            "coverage_report": (stage.output_dir / "coverage_report.md").read_text(encoding="utf-8"),
        }

    def _load_api_mapper_outputs(self, stage: StageWorkspace) -> dict[str, object]:
        return {
            "api_catalog": json.loads((stage.output_dir / "api_catalog.json").read_text(encoding="utf-8")),
            "endpoint_mapping": json.loads((stage.output_dir / "endpoint_mapping.json").read_text(encoding="utf-8")),
            "request_schema": json.loads((stage.output_dir / "request_schema.json").read_text(encoding="utf-8")),
            "dependency_graph": json.loads((stage.output_dir / "dependency_graph.json").read_text(encoding="utf-8")),
        }

    def _load_automation_outputs(self, stage: StageWorkspace) -> dict[str, object]:
        generated_test_file = next(stage.output_dir.glob("generated_tests/test_generated_api_cases.py"))
        return {
            "automation_plan": json.loads((stage.output_dir / "automation_plan.json").read_text(encoding="utf-8")),
            "execution_report": json.loads((stage.output_dir / "execution_report.json").read_text(encoding="utf-8")),
            "generated_test_file": str(generated_test_file),
        }

    def _build_traceability_report(
        self,
        run_id: str,
        requirement_model: dict[str, object],
        test_cases: dict[str, object],
        endpoint_mapping: dict[str, object],
    ) -> dict[str, object]:
        mappings_by_test_case = {
            mapping["test_case_id"]: mapping for mapping in endpoint_mapping["mappings"]
        }
        chains = []
        for case in test_cases["cases"]:
            mapping = mappings_by_test_case[case["test_case_id"]]
            chains.append(
                {
                    "requirement_id": requirement_model["requirement_id"],
                    "test_case_id": case["test_case_id"],
                    "automation_id": mapping["automation_id"],
                    "path": mapping["path"],
                    "method": mapping["method"],
                }
            )
        return {"run_id": run_id, "chains": chains}

    def _build_final_summary(self, execution_report: dict[str, object]) -> str:
        summary = execution_report["summary"]
        return "\n".join(
            [
                "# Final Summary",
                "",
                f"- pytest exit code: {execution_report['pytest_exit_code']}",
                f"- passed: {summary['passed']}",
                f"- failed: {summary['failed']}",
                f"- skipped: {summary['skipped']}",
            ]
        )

    def _build_artifact_inventory(self, run_dir: Path) -> dict[str, object]:
        files = []
        for path in sorted(run_dir.rglob("*")):
            if path.is_file():
                relative_path = path.relative_to(run_dir).as_posix()
                group = self._classify_artifact_group(relative_path)
                description = self._describe_artifact(relative_path, group)
                files.append(
                    {
                        "path": relative_path,
                        "type": path.suffix or "no_suffix",
                        "size_bytes": path.stat().st_size,
                        "group": group,
                        **description,
                    }
                )
        return {
            "record_dir": str(run_dir),
            "file_count": len(files),
            "explanation_rule": {
                "language": "中文",
                "required_fields": ["file_name", "purpose", "main_contents", "stage"],
                "rule": "每个输出文件必须明确说明文件名称、文件作用、文件主要内容、所属流程阶段。",
            },
            "files": files,
        }

    def _classify_artifact_group(self, relative_path: str) -> str:
        if relative_path.endswith("/state.json") or "/logs/" in relative_path or relative_path == "event_log.jsonl":
            return "logs"
        if "/input/" in relative_path:
            return "inputs"
        if relative_path.startswith("requirement_agent/"):
            return "requirement_analysis"
        if relative_path.startswith("testcase_agent/"):
            return "testcases"
        if relative_path.startswith("api_mapper_agent/"):
            return "api_assets"
        if relative_path.startswith("automation_agent/"):
            return "automation"
        if relative_path.startswith("reports/"):
            return "reports"
        return "record_metadata"

    def _describe_artifact(self, relative_path: str, group: str) -> dict[str, str]:
        path = Path(relative_path)
        file_name = path.name
        stage = self._artifact_stage_label(group)
        lower_path = relative_path.lower()

        known_files: dict[str, tuple[str, str]] = {
            "manifest.json": (
                "记录本次需求执行的全局元信息和产物入口，便于后续追溯整条流程。",
                "包含运行编号、记录目录、强制记录规则、Agent 阶段列表、核心产物路径和各 Agent 工作区。",
            ),
            "record_index.md": (
                "作为本次需求的中文总目录，帮助最终使用者快速理解每个输出文件的用途。",
                "包含记录规则、文件类型、产物分组、核心入口文件以及全量产物的中文说明。",
            ),
            "event_log.jsonl": (
                "记录整条流程中各 Agent 的执行事件，用于排查执行顺序和失败原因。",
                "按行保存阶段启动、完成、失败等事件，以及对应时间、命令和输出文件信息。",
            ),
            "state.json": (
                "记录当前 Agent 工作区的执行状态，便于确认该阶段是否成功完成。",
                "包含 Agent 名称、运行编号、状态、输入文件、输出文件、执行命令、开始结束时间和角色职责。",
            ),
            "role_profile.json": (
                "保存当前 Agent 的机器可读角色职责定义，确保后续执行时职责边界清晰。",
                "包含 Agent 角色名称、职责范围、输入输出、约束规则和严格模式要求。",
            ),
            "role_profile.md": (
                "保存当前 Agent 的中文角色说明文档，方便人工查看和后续扩展。",
                "包含 Agent 职责、输入、输出、禁止事项和执行要求。",
            ),
            "worker_stdout.log": (
                "保存当前 Agent 子进程的标准输出，用于复盘执行过程。",
                "包含该阶段运行时打印的普通日志和调试输出。",
            ),
            "worker_stderr.log": (
                "保存当前 Agent 子进程的错误输出，用于定位异常和失败原因。",
                "包含该阶段运行时打印的错误、警告或异常堆栈。",
            ),
            "stage.log": (
                "保存当前阶段的人工可读执行日志，用于快速了解阶段处理过程。",
                "包含阶段内部关键步骤、处理结果和可能的提示信息。",
            ),
            "execution.log": (
                "保存自动化测试执行日志，用于复盘 pytest、Allure 和接口请求执行情况。",
                "包含自动化执行命令、运行输出、失败信息和报告生成过程。",
            ),
            "requirement_model.json": (
                "保存结构化需求分析结果，供测试用例 Agent 继续消费。",
                "包含需求名称、背景、目标、角色、流程、规则、异常场景、影响范围、风险和待确认问题。",
            ),
            "acceptance_criteria.json": (
                "保存需求验收关注点，作为后续测试点和测试用例设计依据。",
                "包含可验收条件、关键校验点、通过标准和需要确认的验收缺口。",
            ),
            "business_flow.md": (
                "用中文描述需求核心业务流程，帮助后续 Agent 和人工快速理解业务链路。",
                "包含主流程、分支流程、异常流程以及上下游系统交互说明。",
            ),
            "risk_points.json": (
                "保存需求分析阶段识别出的风险点，提醒后续测试设计重点关注。",
                "包含需求缺失、歧义、接口依赖、数据风险、权限风险和阻塞点。",
            ),
            "test_cases.json": (
                "保存结构化测试用例，供接口获取和自动化阶段继续使用。",
                "包含用例编号、标题、优先级、前置条件、步骤、预期结果和自动化候选标记。",
            ),
            "test_case_matrix.csv": (
                "保存测试用例矩阵，便于人工审阅、筛选和导入其他测试管理工具。",
                "包含测试点、用例、优先级、场景类型、自动化适配性和覆盖关系。",
            ),
            "coverage_report.md": (
                "说明测试用例对需求点的覆盖情况，帮助识别遗漏和覆盖不足。",
                "包含需求点覆盖、异常场景覆盖、自动化候选覆盖和待补充范围。",
            ),
            "api_catalog.json": (
                "保存从接口平台或接口文档提取出的标准接口资产清单。",
                "包含接口路径、方法、分组、参数、响应、认证方式和接口来源信息。",
            ),
            "endpoint_mapping.json": (
                "保存测试用例与接口之间的映射关系，供自动化阶段生成脚本使用。",
                "包含用例编号、接口路径、请求方法、请求数据、期望状态码和自动化编号。",
            ),
            "request_schema.json": (
                "保存接口请求结构说明，便于自动化脚本生成请求参数和测试数据。",
                "包含路径参数、查询参数、请求体字段、必填项和字段类型。",
            ),
            "dependency_graph.json": (
                "保存接口依赖关系，帮助自动化阶段安排登录、造数、清理和业务链路顺序。",
                "包含接口之间的数据依赖、前置依赖、后置清理依赖和调用顺序建议。",
            ),
            "api_source_request.json": (
                "保存接口来源请求声明，说明本次希望从哪个平台或地址获取接口信息。",
                "包含平台类型、来源 URL、项目或接口定位信息以及 Agent 的接口获取意图。",
            ),
            "api_source_resolved.json": (
                "保存接口来源解析结果，说明平台接入层实际解析出的项目、分组或接口范围。",
                "包含平台项目标识、接口范围、解析状态和标准化来源信息。",
            ),
            "api_document.json": (
                "保存平台接入层拉取并标准化后的接口文档，作为接口获取 Agent 的真实输入。",
                "包含接口基础信息、请求响应定义、分组结构和平台原始数据摘要。",
            ),
            "automation_plan.json": (
                "保存接口自动化设计方案，说明哪些用例可以自动化以及如何执行。",
                "包含自动化范围、脚本生成策略、环境依赖、断言规则、Allure 报告设计和阻塞条件。",
            ),
            "execution_report.json": (
                "保存自动化执行结果，供最终报告和问题复盘使用。",
                "包含 pytest 退出码、通过失败跳过数量、生成脚本数量、Allure 结果目录和报告路径。",
            ),
            "allure_report_viewing_guide.md": (
                "说明 Allure HTML 报告的查看方式，确保最终使用者能直接打开报告。",
                "包含 index.html 用途、报告目录、PowerShell 查看命令、Python 静态服务命令和 Allure CLI 命令。",
            ),
            "traceability_report.json": (
                "保存需求、测试用例、接口和自动化脚本之间的追溯链路。",
                "包含需求编号、用例编号、自动化编号、接口路径和请求方法的对应关系。",
            ),
            "final_summary.md": (
                "保存本次流程最终摘要，便于快速查看自动化执行结论。",
                "包含 pytest 退出码、通过数、失败数和跳过数等关键结果。",
            ),
            "artifact_inventory.json": (
                "保存本次需求的全量产物清单和中文解释说明，是后续查找文件的机器可读索引。",
                "包含每个文件的路径、类型、大小、分组、文件名称、文件作用、主要内容和所属阶段。",
            ),
        }

        if file_name in known_files:
            purpose, main_contents = known_files[file_name]
        elif "generated_tests/" in lower_path and file_name.endswith(".py"):
            purpose = "保存自动生成的接口自动化测试脚本，供 pytest 和 Allure 执行展示。"
            main_contents = "包含接口请求逻辑、断言逻辑、Allure epic/feature/story/title/step/attachment 标注和测试数据处理。"
        elif "allure-results/" in lower_path:
            purpose = "保存 Allure 原始执行结果数据，供生成 HTML 报告使用。"
            main_contents = "包含测试用例结果、步骤、附件、容器信息和 Allure 识别的执行元数据。"
        elif "allure-report/" in lower_path:
            purpose = "保存 Allure 生成的 HTML 静态报告文件，供最终查看和共享测试结果。"
            main_contents = "包含报告页面资源、测试结果展示数据、样式脚本和 index.html 入口。"
        elif "/input/" in lower_path:
            purpose = "保存当前阶段的输入文件，保证后续可以复盘该 Agent 当时基于什么内容处理。"
            main_contents = "包含上游阶段传入的数据、用户提供的原始资料或平台接入层解析后的输入。"
        elif path.suffix == ".json":
            purpose = "保存当前流程产出的结构化 JSON 数据，供后续 Agent 或工具读取。"
            main_contents = "包含与该文件名对应的结构化字段、处理结果、状态信息或配置数据。"
        elif path.suffix == ".md":
            purpose = "保存当前流程产出的中文说明文档，供人工审阅、交接和复盘使用。"
            main_contents = "包含与该文件名对应的分析说明、设计说明、报告说明或查看说明。"
        elif path.suffix == ".csv":
            purpose = "保存当前流程产出的表格化数据，便于人工筛选、导入或二次处理。"
            main_contents = "包含与该文件名对应的行列数据和覆盖关系。"
        elif path.suffix == ".log":
            purpose = "保存当前流程的日志信息，便于定位执行过程和异常原因。"
            main_contents = "包含运行命令输出、阶段处理信息、错误提示或调试日志。"
        else:
            purpose = "保存当前流程运行过程中生成的辅助产物，便于追溯和复盘。"
            main_contents = "包含与该文件类型对应的运行数据、页面资源、附件或中间结果。"

        return {
            "file_name": file_name,
            "purpose": purpose,
            "main_contents": main_contents,
            "stage": stage,
        }

    def _artifact_stage_label(self, group: str) -> str:
        return {
            "inputs": "输入准备阶段",
            "requirement_analysis": "需求分析 Agent 阶段",
            "testcases": "测试用例 Agent 阶段",
            "api_assets": "接口获取 Agent 阶段",
            "automation": "接口自动化 Agent 阶段",
            "logs": "执行日志阶段",
            "reports": "流程汇总与报告阶段",
            "record_metadata": "需求记录元数据阶段",
        }.get(group, "未分类阶段")

    def _build_record_index(
        self,
        manifest: dict[str, object],
        artifact_inventory: dict[str, object],
    ) -> str:
        record_policy = manifest["record_policy"]
        files = artifact_inventory["files"]
        files_by_group: dict[str, list[dict[str, object]]] = {}
        for file_info in files:
            files_by_group.setdefault(str(file_info["group"]), []).append(file_info)

        explanation_rule = record_policy.get("output_file_explanation_rule", {})

        lines = [
            "# 需求记录目录索引",
            "",
            "## 强制记录规则",
            f"- 记录目录：`{record_policy['record_dir']}`",
            "- 该需求相关的所有输入、输出、日志、报告和 Allure 产物必须集中保存在本目录下。",
            "- 不允许只在对话中给出结果而不落盘保存。",
            "- 不允许把同一需求的核心产物分散到记录目录之外。",
            "- 后续所有输出文件必须附带中文解释说明，不能只输出文件路径或文件名。",
            "",
            "## 输出文件中文说明规则",
            f"- 说明语言：{explanation_rule.get('language', '中文')}",
            "- 必须说明：文件名称、文件作用、文件主要内容、所属阶段。",
            "",
            "## 文件类型",
        ]
        lines.extend([f"- `{file_type}`" for file_type in record_policy["file_types"]])
        lines.extend(["", "## 产物分组"])
        for group in record_policy["required_groups"]:
            group_files = files_by_group.get(str(group), [])
            lines.append(f"- {group}：{len(group_files)} 个文件")

        lines.extend(["", "## 核心入口文件"])
        artifacts = manifest["artifacts"]
        for name, path in artifacts.items():
            lines.append(f"- {name}：`{path}`")

        lines.extend(["", "## 全量产物清单"])
        for file_info in files:
            lines.extend(
                [
                    f"### {file_info['path']}",
                    f"- 文件名称：{file_info['file_name']}",
                    f"- 文件作用：{file_info['purpose']}",
                    f"- 文件主要内容：{file_info['main_contents']}",
                    f"- 所属阶段：{file_info['stage']}",
                    f"- 文件分组：{file_info['group']}",
                    f"- 文件类型：`{file_info['type']}`",
                    f"- 文件大小：{file_info['size_bytes']} bytes",
                    "",
                ]
            )
        return "\n".join(lines)


def run_demo_pipeline(workspace_root: Path) -> PipelineRunResult:
    orchestrator = PipelineOrchestrator()
    requirement_path = examples_root() / "requirements" / "sample_requirement.md"
    api_doc_path = examples_root() / "apis" / "sample_openapi.json"
    return orchestrator.run(
        requirement_path=requirement_path,
        workspace_root=workspace_root,
        run_id="demo-run",
        api_doc_path=api_doc_path,
        require_test_points=False,
        require_database_context=False,
        require_agent4_excel=False,
    )
