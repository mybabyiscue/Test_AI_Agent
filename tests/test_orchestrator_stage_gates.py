from __future__ import annotations

import json
from pathlib import Path

from ai_pipeline.orchestrator import PipelineOrchestrator


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

        return parse_apifox_url(api_source_url), self.resolve_apifox_project("123456")


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

    blocking_report = json.loads((result.run_dir / "reports" / "blocking_report.json").read_text(encoding="utf-8"))
    requirement_state = json.loads((result.run_dir / "requirement_agent" / "state.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "requirement_agent"
    assert "pdf_source_snapshot.json" in json.dumps(blocking_report, ensure_ascii=False)
    assert "pdf_extracted_text.md" in json.dumps(blocking_report, ensure_ascii=False)
    assert requirement_state["status"] == "blocked"
    assert not (result.run_dir / "testcase_agent").exists()


def test_pipeline_blocks_before_agent3_when_test_points_are_missing(tmp_path):
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

    blocking_report = json.loads((result.run_dir / "reports" / "blocking_report.json").read_text(encoding="utf-8"))
    testcase_state = json.loads((result.run_dir / "testcase_agent" / "state.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "testcase_agent"
    assert "test_points.json" in json.dumps(blocking_report, ensure_ascii=False)
    assert testcase_state["status"] == "blocked"
    assert not (result.run_dir / "api_mapper_agent").exists()


def test_pipeline_blocks_after_agent3_when_database_context_is_missing(tmp_path):
    requirement_path = tmp_path / "购物车需求.md"
    requirement_path.write_text("# 宠物商店系统购物车功能\n- 将宠物加入购物车\n", encoding="utf-8")

    result = PipelineOrchestrator(api_document_resolver=FakeApiDocumentResolver()).run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="agent3-gate-run",
        api_source_url="https://app.apifox.com/project/123456",
        require_test_points=False,
    )

    blocking_report = json.loads((result.run_dir / "reports" / "blocking_report.json").read_text(encoding="utf-8"))
    api_mapper_state = json.loads((result.run_dir / "api_mapper_agent" / "state.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "api_mapper_agent"
    assert "database_mapping.json" in json.dumps(blocking_report, ensure_ascii=False)
    assert "missing_database_report.md" in json.dumps(blocking_report, ensure_ascii=False)
    assert api_mapper_state["status"] == "blocked"
    assert not (result.run_dir / "automation_agent").exists()


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

    blocking_report = json.loads((result.run_dir / "reports" / "blocking_report.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_stage"] == "automation_agent"
    assert "Agent4自动化执行输入模板_鉴权约束修正版.xlsx" in json.dumps(blocking_report, ensure_ascii=False)
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
    blocking_report = json.loads((result.run_dir / "reports" / "blocking_report.json").read_text(encoding="utf-8"))

    assert result.status == "blocked"
    assert blocking_report["blocked_at"] == "before"
    assert confirmation["agent_name"] == "requirement_agent"
    assert confirmation["can_start"] is False
    assert confirmation["responsibility_self_check"]["input_is_sufficient"] is False
    assert confirmation["responsibility_self_check"]["must_block"] is True
    assert confirmation["missing_inputs_or_preconditions"]
    assert not (result.run_dir / "requirement_agent" / "logs" / "worker_stdout.log").exists()
