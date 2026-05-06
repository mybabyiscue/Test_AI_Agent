from __future__ import annotations

import json
from pathlib import Path

from ai_pipeline.artifact_store import EventLog, StageWorkspace
from ai_pipeline.orchestrator import PipelineOrchestrator
from ai_pipeline.stage_gates import check_testcase_gate


class FakeApiDocumentResolver:
    def resolve_apifox_project(self, project_id: str):
        return {
            "openapi": "3.0.0",
            "info": {"title": "Fake Service", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "post": {
                        "summary": "Create user",
                        "responses": {"201": {"description": "Created"}},
                    }
                }
            },
        }

    def resolve_apifox_url(self, api_source_url: str):
        from ai_pipeline.platforms.apifox import parse_apifox_url

        source = parse_apifox_url(api_source_url)
        return source, self.resolve_apifox_project_index(source.project_id, api_source_url)

    def resolve_apifox_project_index(self, project_id: str, source_url: str | None = None):
        return {
            "platform": "apifox",
            "project_id": project_id,
            "source_url": source_url or f"https://app.apifox.com/project/{project_id}",
            "sync_mode": "basic_api_index",
            "detail_fetch_policy": "index only",
            "apis": [
                {
                    "id": "101",
                    "api_name": "Create user",
                    "method": "POST",
                    "path": "/users",
                    "module": "User",
                    "folder_path": ["User"],
                    "description": "",
                    "operation_id": "",
                    "tags": ["User"],
                    "source": source_url or f"https://app.apifox.com/project/{project_id}",
                    "project_id": project_id,
                    "updated_at": "pending_confirmation",
                    "sync_mode": "basic_api_index",
                    "detail_fetch_policy": "index only",
                    "missing_fields": ["description", "updated_at"],
                }
            ],
        }

    def resolve_apifox_project_for_endpoints(self, *, project_id: str, endpoints: list[dict[str, str]]):
        return self.resolve_apifox_project(project_id)


def test_pdf_requirement_blocks_after_agent1_when_pdf_snapshot_outputs_are_missing(tmp_path):
    requirement_path = tmp_path / "requirement.pdf"
    requirement_path.write_bytes(b"%PDF-1.4\nnot a real pdf, but enough to exercise source-type gate\n")
    api_doc_path = tmp_path / "api.json"
    api_doc_path.write_text(
        json.dumps({"openapi": "3.0.0", "info": {"title": "x"}, "paths": {}}),
        encoding="utf-8",
    )

    result = PipelineOrchestrator().run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="pdf-gate-run",
        api_doc_path=api_doc_path,
    )

    blocking_report = json.loads((result.run_dir / "summary" / "blocking_report.json").read_text(encoding="utf-8"))
    requirement_state = json.loads(
        (result.run_dir / "requirement_agent" / "log" / "state.json").read_text(encoding="utf-8")
    )

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "requirement_agent"
    assert "pdf_source_snapshot.json" in json.dumps(blocking_report, ensure_ascii=False)
    assert "pdf_extracted_text.md" in json.dumps(blocking_report, ensure_ascii=False)
    assert requirement_state["status"] == "blocked"
    assert not (result.run_dir / "testcase_agent").exists()


def test_pdf_requirement_with_non_utf8_bytes_does_not_crash_pipeline(tmp_path):
    requirement_path = tmp_path / "requirement.pdf"
    requirement_path.write_bytes(b"%PDF-1.4\nbinary:\xd3\xd4\xd5\xd0\n%%EOF\n")
    api_doc_path = tmp_path / "api.json"
    api_doc_path.write_text(
        json.dumps({"openapi": "3.0.0", "info": {"title": "x"}, "paths": {}}),
        encoding="utf-8",
    )

    result = PipelineOrchestrator().run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="pdf-binary-run",
        api_doc_path=api_doc_path,
    )

    assert result.run_dir.exists()
    assert (result.run_dir / "summary" / "manifest.json").exists()
    assert result.status in {"blocked", "success"}


def test_pipeline_advances_past_agent2_when_test_points_are_present(tmp_path):
    requirement_path = tmp_path / "requirement.md"
    requirement_path.write_text(
        "\n".join(
            [
                "# 用户注册",
                "- 用户使用合法资料发起注册",
                "- 重复邮箱注册失败",
            ]
        ),
        encoding="utf-8",
    )
    api_doc_path = tmp_path / "api.json"
    api_doc_path.write_text(
        json.dumps({"openapi": "3.0.0", "info": {"title": "x"}, "paths": {}}),
        encoding="utf-8",
    )

    result = PipelineOrchestrator().run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="testcase-gate-run",
        api_doc_path=api_doc_path,
    )

    blocking_report = json.loads((result.run_dir / "summary" / "blocking_report.json").read_text(encoding="utf-8"))
    testcase_state = json.loads((result.run_dir / "testcase_agent" / "log" / "state.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "automation_agent"
    assert testcase_state["status"] == "success"
    assert (result.run_dir / "testcase_agent" / "output" / "test_points.json").exists()
    assert (result.run_dir / "api_mapper_agent").exists()


def test_testcase_gate_blocks_when_test_points_file_is_missing(tmp_path):
    run_dir = tmp_path / "run"
    stage = StageWorkspace(
        run_id="gate-check-run",
        run_dir=run_dir,
        agent_name="testcase_agent",
        event_log=EventLog(run_dir / "summary" / "run_log.jsonl"),
    )
    stage.write_output_json(
        "test_cases.json",
        {
            "requirement_id": "REQ-001",
            "cases": [
                {
                    "test_case_id": "TC-001",
                    "requirement_id": "REQ-001",
                    "title": "用户使用合法资料发起注册",
                    "priority": "P0",
                    "expected_status_codes": [201],
                }
            ],
        },
    )

    blockers = check_testcase_gate(
        stage,
        outputs={
            "test_cases": {
                "requirement_id": "REQ-001",
                "cases": [
                    {
                        "test_case_id": "TC-001",
                        "requirement_id": "REQ-001",
                        "title": "用户使用合法资料发起注册",
                        "priority": "P0",
                        "expected_status_codes": [201],
                    }
                ],
            }
        },
        require_test_points=True,
    )

    assert any(blocker["code"] == "missing_test_points" for blocker in blockers)


def test_pipeline_advances_past_agent3_when_database_context_is_loaded_from_knowledge_base(tmp_path):
    requirement_path = tmp_path / "livecode_requirement.md"
    requirement_path.write_text("# 活码和链接自动上线与手动上下线\n- 活码支持次日自动上线与手动上下线\n", encoding="utf-8")

    result = PipelineOrchestrator(api_document_resolver=FakeApiDocumentResolver()).run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="agent3-gate-run",
        api_source_url="https://app.apifox.com/project/123456",
        require_test_points=False,
    )

    blocking_report = json.loads((result.run_dir / "summary" / "blocking_report.json").read_text(encoding="utf-8"))
    api_mapper_state = json.loads(
        (result.run_dir / "api_mapper_agent" / "log" / "state.json").read_text(encoding="utf-8")
    )

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "automation_agent"
    assert api_mapper_state["status"] == "success"
    assert (result.run_dir / "api_mapper_agent" / "output" / "database_mapping.json").exists()
    assert (result.run_dir / "api_mapper_agent" / "output" / "missing_database_report.md").exists()
    assert (result.run_dir / "automation_agent").exists()


def test_pipeline_blocks_before_agent4_when_excel_template_is_not_confirmed(tmp_path):
    requirement_path = Path("examples/requirements/sample_requirement.md").resolve()
    api_doc_path = Path("examples/apis/sample_openapi.json").resolve()

    result = PipelineOrchestrator().run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="agent4-gate-run",
        api_doc_path=api_doc_path,
        require_test_points=False,
        require_database_context=False,
    )

    blocking_report = json.loads((result.run_dir / "summary" / "blocking_report.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "automation_agent"
    assert "Agent4" in json.dumps(blocking_report, ensure_ascii=False)
    assert not (result.run_dir / "automation_agent" / "output" / "generated_tests").exists()


def test_pipeline_blocks_before_agent1_when_responsibility_identification_finds_missing_input(tmp_path):
    requirement_path = tmp_path / "missing_requirement.md"
    api_doc_path = tmp_path / "api.json"
    api_doc_path.write_text(
        json.dumps({"openapi": "3.0.0", "info": {"title": "x"}, "paths": {}}),
        encoding="utf-8",
    )

    result = PipelineOrchestrator().run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="missing-input-responsibility-gate",
        api_doc_path=api_doc_path,
    )

    confirmation = json.loads(
        (result.run_dir / "requirement_agent" / "output" / "responsibility_confirmation.json").read_text(
            encoding="utf-8"
        )
    )
    blocking_report = json.loads((result.run_dir / "summary" / "blocking_report.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_at"] == "before"
    assert confirmation["agent_name"] == "requirement_agent"
    assert confirmation["can_start"] is False
    assert confirmation["responsibility_self_check"]["input_is_sufficient"] is False
    assert confirmation["responsibility_self_check"]["must_block"] is True
    assert confirmation["missing_inputs_or_preconditions"]
    assert not (result.run_dir / "requirement_agent" / "log" / "worker_stdout.log").exists()
