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
from .report_renderer import (
    build_artifact_inventory,
    build_file_compliance_check,
    build_final_summary,
    build_record_index,
    build_traceability_report,
)
from .stage_gates import (
    check_api_mapper_gate,
    check_automation_input_gate,
    check_requirement_gate,
    check_required_input_file,
    check_testcase_gate,
    identify_responsibility,
    validate_completion,
)


def _remove_readonly(func: Any, path: str, exc_info: Any) -> None:
    import stat

    Path(path).chmod(stat.S_IWRITE)
    func(path)


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
        if api_doc_path and api_source_url:
            raise ValueError("api_doc_path 和 api_source_url 只能提供其中一个，不能同时提供。")

        run_dir = workspace_root.resolve() / "runs" / run_id
        if run_dir.exists():
            shutil.rmtree(run_dir, onerror=_remove_readonly)
        run_dir.mkdir(parents=True, exist_ok=True)
        summary_dir = run_dir / "summary"
        store = ArtifactStore(summary_dir)
        event_log = EventLog(summary_dir / "run_log.jsonl")

        requirement_stage = StageWorkspace(run_id, run_dir, "requirement_agent", event_log)
        precheck_blockers = check_required_input_file(requirement_path, self.requirement_agent.agent_name)
        if precheck_blockers:
            identify_responsibility(requirement_stage, blockers=precheck_blockers)
            return self._block_pipeline(
                store=store,
                stage=requirement_stage,
                blocked_at="before",
                blockers=precheck_blockers,
                executed_stages=[],
            )
        staged_requirement_path = requirement_stage.copy_input(requirement_path)
        identify_responsibility(requirement_stage)
        requirement_outputs = self._run_requirement_stage(requirement_stage, staged_requirement_path)
        blockers = check_requirement_gate(requirement_stage, requirement_outputs, staged_requirement_path)
        validate_completion(requirement_stage, blockers)
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
        identify_responsibility(testcase_stage)
        testcase_outputs = self._run_testcase_stage(
            testcase_stage,
            requirement_outputs["requirement_model"],
            requirement_outputs["acceptance_criteria"],
        )
        blockers = check_testcase_gate(testcase_stage, testcase_outputs, require_test_points=require_test_points)
        validate_completion(testcase_stage, blockers)
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
            test_cases=testcase_outputs["test_cases"],
            api_doc_path=api_doc_path,
            api_source_url=api_source_url,
        )
        identify_responsibility(api_mapper_stage)
        mapping_outputs = self._run_api_mapper_stage(api_mapper_stage, staged_api_doc_path)
        blockers = check_api_mapper_gate(
            api_mapper_stage,
            mapping_outputs,
            require_database_context=require_database_context,
        )
        validate_completion(api_mapper_stage, blockers)
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
        automation_stage.write_input_json("database_mapping.json", mapping_outputs["database_mapping"])
        blockers = check_automation_input_gate(
            automation_stage,
            require_agent4_excel=require_agent4_excel,
            agent4_excel_confirmed=agent4_excel_confirmed,
        )
        identify_responsibility(automation_stage, blockers=blockers)
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
        validate_completion(automation_stage, [])
        traceability_report = build_traceability_report(
            run_id,
            requirement_outputs["requirement_model"],
            testcase_outputs["test_cases"],
            mapping_outputs["endpoint_mapping"],
        )
        store.write_json("traceability_report.json", traceability_report)
        store.write_text(
            "final_summary.md",
            build_final_summary(automation_outputs["execution_report"]),
        )
        inventory = build_artifact_inventory(run_dir)
        store.write_json("artifact_inventory.json", inventory)
        store.write_text("file_compliance_check.md", build_file_compliance_check(inventory))

        manifest = self._build_manifest(run_id, run_dir)
        manifest_path = store.write_json("manifest.json", manifest)
        store.write_text("summary.md", build_record_index(manifest, inventory))
        return PipelineRunResult(run_id=run_id, run_dir=run_dir, manifest_path=manifest_path)

    def _build_manifest(self, run_id: str, run_dir: Path) -> dict[str, object]:
        return {
            "run_id": run_id,
            "record_policy": {
                "record_dir": str(run_dir),
                "storage_rule": "current_flow_files_must_stay_under_current_run_dir_with_fixed_agent_layout",
                "global_file_storage_policy": "config/agent_file_storage_policy.json",
                "policy_effective_notice": "文件管理规范已生效：本次流程所有文件位于专属总文件夹内；每个 Agent 固定使用 input/output/log；全局汇总写入 summary。",
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
                    "summary",
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
                "report": "summary/traceability_report.json",
                "record_index": "summary/summary.md",
                "artifact_inventory": "summary/artifact_inventory.json",
                "file_compliance_check": "summary/file_compliance_check.md",
            },
            "stage_workspaces": {
                "requirement_agent": "requirement_agent",
                "testcase_agent": "testcase_agent",
                "api_mapper_agent": "api_mapper_agent",
                "automation_agent": "automation_agent",
            },
        }

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
        blocking_report_path = store.write_json("blocking_report.json", blocking_report)
        inventory = build_artifact_inventory(stage.run_dir)
        store.write_json("artifact_inventory.json", inventory)
        store.write_text("file_compliance_check.md", build_file_compliance_check(inventory))

        manifest = {
            "run_id": stage.run_id,
            "status": "blocked",
            "blocked_stage": stage.agent_name,
            "blocking_report": "summary/blocking_report.json",
            "stages": executed_stages,
            "record_policy": {
                "record_dir": str(stage.run_dir),
                "storage_rule": "current_flow_files_must_stay_under_current_run_dir_with_fixed_agent_layout",
                "global_file_storage_policy": "config/agent_file_storage_policy.json",
                "policy_effective_notice": "文件管理规范已生效：本次流程所有文件位于专属总文件夹内；每个 Agent 固定使用 input/output/log；全局汇总写入 summary。",
                "output_file_explanation_rule": {
                    "language": "中文",
                    "required_fields": ["file_name", "purpose", "main_contents", "stage"],
                    "rule": "流程阻断时必须输出阻塞原因，禁止继续推进下游 Agent。",
                },
                "file_types": [".json", ".md", ".csv", ".py", "directory"],
                "required_groups": ["inputs", "logs", "summary"],
            },
            "artifacts": {
                "blocking_report": "summary/blocking_report.json",
                "artifact_inventory": "summary/artifact_inventory.json",
                "file_compliance_check": "summary/file_compliance_check.md",
            },
            "stage_workspaces": {
                stage.agent_name: stage.agent_name,
            },
        }
        manifest_path = store.write_json("manifest.json", manifest)
        store.write_text("summary.md", build_record_index(manifest, inventory))
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
        self._run_stage_subprocess(stage, started_at, input_files, [requirement_path])
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
        api_doc_path: Path | None,
    ) -> dict[str, object]:
        input_files = [str(path.relative_to(stage.run_dir)) for path in stage.input_dir.rglob("*") if path.is_file()]
        started_at = utc_now_iso()
        self._run_stage_subprocess(stage, started_at, input_files, [api_doc_path] if api_doc_path else [])
        return self._load_api_mapper_outputs(stage)

    def _prepare_api_mapper_input(
        self,
        stage: StageWorkspace,
        *,
        test_cases: dict[str, Any],
        api_doc_path: Path | None,
        api_source_url: str | None,
    ) -> Path | None:
        if api_doc_path is not None:
            staged_api_doc = stage.copy_input(api_doc_path)
            api_document = json.loads(staged_api_doc.read_text(encoding="utf-8-sig"))
            if self._is_basic_apifox_index(api_document):
                project_id = str(api_document["project_id"])
                source_url = str(api_document.get("source_url") or f"https://app.apifox.com/project/{project_id}")
                declaration = self.api_mapper_agent.declare_api_source(source_url)
                selected_endpoints = self.api_mapper_agent.select_endpoints_from_index(test_cases, api_document)
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
                stage.write_input_json(
                    "selected_endpoint_candidates.json",
                    {
                        "project_id": project_id,
                        "selection_mode": "knowledge_index_match",
                        "endpoints": selected_endpoints,
                    },
                )
                if not selected_endpoints:
                    raise ValueError("Agent 3 could not confirm any endpoint from the knowledge index; all details remain 待确认.")
                detailed_document = self.api_document_resolver.resolve_apifox_project_for_endpoints(
                    project_id=project_id,
                    endpoints=selected_endpoints,
                )
                return stage.write_input_json("api_document.json", detailed_document)
            return staged_api_doc

        if api_source_url is None:
            # 无显式 API 来源，从知识库加载基础索引
            knowledge_index = self._load_knowledge_base_index()
            if knowledge_index is None:
                return None
            project_id = str(knowledge_index.get("project_id", ""))
            source_url = str(knowledge_index.get("source_url", ""))
            selected_endpoints = self.api_mapper_agent.select_endpoints_from_index(test_cases, knowledge_index)
            stage.write_input_json("api_source_request.json", {
                "platform": "apifox",
                "url": source_url,
                "project_id": project_id,
                "source": "knowledge_base_auto",
            })
            stage.write_input_json("api_source_resolved.json", {
                "platform": "apifox",
                "url": source_url,
                "project_id": project_id,
                "resource_type": "project",
                "resource_id": None,
                "source": "knowledge_base_auto",
            })
            stage.write_input_json("api_knowledge_index.json", knowledge_index)
            stage.write_input_json("selected_endpoint_candidates.json", {
                "project_id": project_id,
                "selection_mode": "knowledge_index_auto",
                "endpoints": selected_endpoints,
            })
            if not selected_endpoints:
                raise ValueError("Agent 3 could not confirm any endpoint from the knowledge base; all details remain 待确认.")
            detailed_document = self.api_document_resolver.resolve_apifox_project_for_endpoints(
                project_id=project_id,
                endpoints=selected_endpoints,
            )
            return stage.write_input_json("api_document.json", detailed_document)

        declaration = self.api_mapper_agent.declare_api_source(api_source_url)
        source, api_index = self.api_document_resolver.resolve_apifox_url(api_source_url)
        if source.resource_type == "api" and source.resource_id:
            selected_endpoints = self.api_mapper_agent.select_endpoints_from_index(
                test_cases,
                api_index,
                resource_id=source.resource_id,
            )
        else:
            selected_endpoints = self.api_mapper_agent.select_endpoints_from_index(test_cases, api_index)
        api_document = self.api_document_resolver.resolve_apifox_project_for_endpoints(
            project_id=source.project_id,
            endpoints=selected_endpoints,
        )
        stage.write_input_json("api_source_request.json", declaration)
        stage.write_input_json("api_source_resolved.json", source.to_declaration())
        stage.write_input_json("api_knowledge_index.json", api_index)
        stage.write_input_json(
            "selected_endpoint_candidates.json",
            {
                "project_id": source.project_id,
                "selection_mode": "apifox_index_match",
                "endpoints": selected_endpoints,
            },
        )
        if not selected_endpoints:
            raise ValueError("Agent 3 could not confirm any endpoint from the Apifox index; all details remain 待确认.")
        return stage.write_input_json("api_document.json", api_document)

    def _is_basic_apifox_index(self, api_document: dict[str, Any]) -> bool:
        return (
            api_document.get("platform") == "apifox"
            and bool(api_document.get("project_id"))
            and "paths" not in api_document
            and isinstance(api_document.get("apis"), list)
        )

    def _load_knowledge_base_index(self) -> dict[str, Any] | None:
        knowledge_root = self.api_mapper_agent.knowledge_root
        default_scope = self.api_mapper_agent.default_database_scope
        # 优先加载默认作用域（saas），再兜底其他作用域
        scope_order = [default_scope] + [
            scope_dir.name
            for scope_dir in sorted(knowledge_root.iterdir())
            if scope_dir.is_dir() and not scope_dir.name.startswith("_") and scope_dir.name != default_scope
        ]
        for scope_name in scope_order:
            apis_dir = knowledge_root / scope_name / "apis"
            if not apis_dir.exists():
                continue
            for index_file in sorted(apis_dir.glob("apifox_project_*.json")):
                try:
                    data = json.loads(index_file.read_text(encoding="utf-8-sig"))
                except (json.JSONDecodeError, OSError):
                    continue
                if isinstance(data.get("apis"), list) and data.get("apis"):
                    return data
        return None

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
            "test_points": json.loads((stage.output_dir / "test_points.json").read_text(encoding="utf-8")),
            "test_cases": json.loads((stage.output_dir / "test_cases.json").read_text(encoding="utf-8")),
            "test_case_matrix": (stage.output_dir / "test_case_matrix.csv").read_text(encoding="utf-8"),
            "coverage_report": (stage.output_dir / "coverage_report.md").read_text(encoding="utf-8"),
        }

    def _load_api_mapper_outputs(self, stage: StageWorkspace) -> dict[str, object]:
        return {
            "api_catalog": json.loads((stage.output_dir / "api_catalog.json").read_text(encoding="utf-8")),
            "database_catalog": json.loads((stage.output_dir / "database" / "database_catalog.json").read_text(encoding="utf-8")),
            "database_mapping": json.loads((stage.output_dir / "database_mapping.json").read_text(encoding="utf-8")),
            "missing_database_report": (stage.output_dir / "missing_database_report.md").read_text(encoding="utf-8"),
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


def run_demo_pipeline(workspace_root: Path) -> PipelineRunResult:
    os.environ.setdefault("AI_PIPELINE_LLM_ENABLED", "0")
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
