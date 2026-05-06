from __future__ import annotations

import json
from pathlib import Path

from ai_pipeline.agents.automation_agent import AutomationAgent
from ai_pipeline.orchestrator import run_demo_pipeline


def test_demo_pipeline_creates_manifest_and_stage_outputs(tmp_path):
    result = run_demo_pipeline(workspace_root=tmp_path)

    assert result.run_id == "demo-run"
    assert result.run_dir.exists()
    assert result.manifest_path.exists()
    summary_dir = result.run_dir / "summary"
    assert (summary_dir / "summary.md").exists()

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["run_id"] == "demo-run"
    assert manifest["record_policy"]["record_dir"] == str(result.run_dir)
    assert manifest["record_policy"]["storage_rule"] == "current_flow_files_must_stay_under_current_run_dir_with_fixed_agent_layout"
    assert manifest["record_policy"]["global_file_storage_policy"] == "config/agent_file_storage_policy.json"
    assert manifest["record_policy"]["file_types"] == [".json", ".md", ".csv", ".py", "directory"]
    assert manifest["record_policy"]["required_groups"] == [
        "inputs",
        "requirement_analysis",
        "testcases",
        "api_assets",
        "automation",
        "logs",
        "summary",
    ]
    assert manifest["stages"] == [
        "requirement_analysis",
        "testcase_design",
        "api_mapping",
        "automation_execution",
    ]
    assert (summary_dir / "run_log.jsonl").exists()

    required_artifacts = [
        result.run_dir / "requirement_agent" / "output" / "requirement_model.json",
        result.run_dir / "testcase_agent" / "output" / "test_cases.json",
        result.run_dir / "testcase_agent" / "output" / "test_points.json",
        result.run_dir / "api_mapper_agent" / "output" / "apis" / "api_source_request.md",
        result.run_dir / "api_mapper_agent" / "output" / "apis" / "api_catalog.md",
        result.run_dir / "api_mapper_agent" / "output" / "database" / "database_catalog.json",
        result.run_dir / "api_mapper_agent" / "output" / "database" / "database_catalog.md",
        result.run_dir / "api_mapper_agent" / "output" / "database_mapping.json",
        result.run_dir / "api_mapper_agent" / "output" / "missing_database_report.md",
        result.run_dir / "api_mapper_agent" / "output" / "mappings" / "endpoint_mapping.md",
        result.run_dir / "api_mapper_agent" / "output" / "mappings" / "database_mapping.md",
        result.run_dir / "api_mapper_agent" / "output" / "mappings" / "missing_database_report.md",
        result.run_dir / "api_mapper_agent" / "output" / "apis" / "request_schema.md",
        result.run_dir / "api_mapper_agent" / "output" / "mappings" / "dependency_graph.md",
        result.run_dir / "api_mapper_agent" / "output" / "endpoint_mapping.json",
        result.run_dir / "automation_agent" / "output" / "automation_plan.json",
        result.run_dir / "automation_agent" / "output" / "generated_tests" / "test_generated_api_cases.py",
        result.run_dir / "automation_agent" / "output" / "execution_report.json",
        result.run_dir / "automation_agent" / "output" / "allure_report_viewing_guide.md",
        summary_dir / "traceability_report.json",
        summary_dir / "artifact_inventory.json",
        summary_dir / "summary.md",
    ]

    for artifact_path in required_artifacts:
        assert artifact_path.exists(), f"Missing artifact: {artifact_path}"

    artifact_inventory = json.loads(
        (summary_dir / "artifact_inventory.json").read_text(encoding="utf-8")
    )
    assert artifact_inventory["explanation_rule"]["language"] == "中文"
    assert artifact_inventory["explanation_rule"]["required_fields"] == [
        "file_name",
        "purpose",
        "main_contents",
        "stage",
    ]
    for file_info in artifact_inventory["files"]:
        assert file_info["file_name"]
        assert file_info["purpose"]
        assert file_info["main_contents"]
        assert file_info["stage"]

    record_index_text = (summary_dir / "summary.md").read_text(encoding="utf-8")
    assert "文件名称" in record_index_text
    assert "文件作用" in record_index_text
    assert "主要内容" in record_index_text
    assert "所属阶段" in record_index_text

    for stage_dir_name in [
        "requirement_agent",
        "testcase_agent",
        "api_mapper_agent",
        "automation_agent",
    ]:
        stage_dir = result.run_dir / stage_dir_name
        assert (stage_dir / "input").exists()
        assert (stage_dir / "output").exists()
        assert (stage_dir / "log").exists()
        assert (stage_dir / "log" / "state.json").exists()
        state = json.loads((stage_dir / "log" / "state.json").read_text(encoding="utf-8"))
        assert state["status"] == "success"
        assert state["agent_name"] == stage_dir_name
        assert state["output_files"]
        assert state["role_profile"]["language"] == "中文"
        assert state["role_profile"]["strict_mode"] is True
        assert state["role_profile"]["title"].startswith("高级")
        assert not (stage_dir / "output" / "role_profile.json").exists()
        assert not (stage_dir / "output" / "role_profile.md").exists()
        assert (stage_dir / "log" / "role_profile.json").exists()
        assert (stage_dir / "log" / "llm_prompt.md").exists()
        assert (stage_dir / "log" / "llm_invocation.json").exists()
        role_profile_md = stage_dir / "log" / "role_profile.md"
        assert role_profile_md.exists()
        role_profile_text = role_profile_md.read_text(encoding="utf-8")
        assert role_profile_text.startswith("# 高级")
        assert "## 职责" in role_profile_text
        assert "## 可读取输入" in role_profile_text
        assert "## 必须输出" in role_profile_text
        assert "## 禁止事项" in role_profile_text
        llm_prompt_text = (stage_dir / "log" / "llm_prompt.md").read_text(encoding="utf-8")
        llm_invocation = json.loads((stage_dir / "log" / "llm_invocation.json").read_text(encoding="utf-8"))
        assert stage_dir_name in llm_prompt_text
        assert "当前 Agent 职责说明" in llm_prompt_text
        assert "当前阶段输出要求" in llm_prompt_text
        assert llm_invocation["agent_name"] == stage_dir_name
        assert isinstance(llm_invocation["backend"], str)
        assert llm_invocation["role_markdown_path"].replace("\\", "/").endswith(f"roles/{stage_dir_name}.md")
        assert llm_invocation["prompt_template_path"].endswith(".md")

    execution_report = json.loads(
        (result.run_dir / "automation_agent" / "output" / "execution_report.json").read_text(encoding="utf-8")
    )
    assert execution_report["run_id"] == "demo-run"
    assert execution_report["generated_test_count"] >= 1
    assert execution_report["pytest_exit_code"] == 0
    assert execution_report["summary"]["skipped"] >= 1
    assert execution_report["allure_html_report"]["index_path"].endswith("index.html")
    assert execution_report["allure_viewing_guide"].endswith("allure_report_viewing_guide.md")

    event_lines = (summary_dir / "run_log.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(event_lines) >= 8
    first_event = json.loads(event_lines[0])
    last_event = json.loads(event_lines[-1])
    assert first_event["event"] == "responsibility_identified"
    assert last_event["event"] == "completion_validated"

    api_catalog_md = (
        result.run_dir / "api_mapper_agent" / "output" / "apis" / "api_catalog.md"
    ).read_text(encoding="utf-8")
    assert "# API Catalog" in api_catalog_md
    assert "## Interface" in api_catalog_md

    endpoint_mapping_md = (
        result.run_dir / "api_mapper_agent" / "output" / "mappings" / "endpoint_mapping.md"
    ).read_text(encoding="utf-8")
    assert "# Endpoint Mapping" in endpoint_mapping_md


def test_generated_api_tests_reserve_allure_report_annotations(tmp_path):
    result = run_demo_pipeline(workspace_root=tmp_path)

    generated_test = (
        result.run_dir
        / "automation_agent"
        / "output"
        / "generated_tests"
        / "test_generated_api_cases.py"
    ).read_text(encoding="utf-8")

    assert "allure.dynamic.epic" in generated_test
    assert "allure.dynamic.feature" in generated_test
    assert "allure.dynamic.story" in generated_test
    assert "allure.dynamic.title" in generated_test
    assert "with allure.step" in generated_test
    assert "allure.attach" in generated_test
    assert "attachment_type.JSON" in generated_test


def test_generated_api_tests_can_embed_json_boolean_payloads():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-CART-SELECT-001",
                "automation_id": "AUTO-CASE-001",
                "title": "勾选购物车商品",
                "path": "/api/front/cart/items/1/selected",
                "method": "PUT",
                "payload": {"selected": True},
                "expected_status_codes": [200],
            }
        ]
    )

    exec(compile(generated_test, "test_generated_api_cases.py", "exec"), {})


def test_generated_api_tests_include_login_and_dynamic_data_helpers():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-CART-ADD-001",
                "automation_id": "AUTO-CASE-001",
                "title": "有效上架宠物加入购物车成功",
                "path": "/api/front/cart/items",
                "method": "POST",
                "payload": {"petId": "${valid_pet_id}", "quantity": 1},
                "expected_status_codes": [200, 201],
            }
        ]
    )

    assert "FRONT_USERNAME" in generated_test
    assert "def _login_front_user" in generated_test
    assert "AUTH_HEADER_NAME" in generated_test
    assert "Authorization" in generated_test
    assert "def _valid_pet_ids" in generated_test
    assert "def _ensure_cart_items" in generated_test
    assert "'pet_id': pet_id" in generated_test
    assert "def _reset_cart_once" in generated_test
    assert "TC-CART-CHECKOUT-001" in generated_test


def test_generated_api_tests_assert_business_code_when_response_enveloped():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-CART-AUTH-001",
                "automation_id": "AUTO-CASE-001",
                "title": "未登录用户不可操作购物车",
                "path": "/api/front/cart/items",
                "method": "POST",
                "payload": {"petId": "${valid_pet_id}", "quantity": 1},
                "expected_status_codes": [401],
            }
        ]
    )

    assert "def _effective_status_code" in generated_test
    assert "def _business_code" in generated_test
    assert "effective_status_code in expected_status_codes" in generated_test


def test_generated_api_tests_treat_string_business_success_code_as_success():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-LIVECODE-001",
                "automation_id": "AUTO-CASE-001",
                "title": "活码保存成功",
                "path": "/contact/way/save",
                "method": "POST",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            }
        ]
    )

    assert "SUCCESS_RESPONSE_CODE" in generated_test
    assert "code == SUCCESS_RESPONSE_CODE" in generated_test
    assert "return 599" in generated_test


def test_generated_api_tests_support_key_value_login_success_marker():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-LIVECODE-001",
                "automation_id": "AUTO-CASE-001",
                "title": "活码保存成功",
                "path": "/contact/way/save",
                "method": "POST",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            }
        ]
    )

    assert "def _matches_success_marker" in generated_test
    assert "marker.partition('=')" in generated_test
    assert "_extract_json_path(body, key)" in generated_test


def test_generated_api_tests_build_case_payload_from_request_schema():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-LIVECODE-001",
                "automation_id": "AUTO-CASE-001",
                "title": "活码保存成功",
                "path": "/contact/way/save",
                "method": "POST",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "request_body": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "state": {"type": "string"},
                                    "categoryId": {"type": "integer"},
                                    "nextAutoEnableTime": {"type": "string"},
                                },
                                "required": ["state", "categoryId"],
                            }
                        }
                    }
                },
                "expected_status_codes": [200],
            }
        ]
    )

    assert "def _build_case_payload" in generated_test
    assert "def _schema_example_value" in generated_test
    assert "case.get('request_body', {})" in generated_test
    assert "def _should_autofill_field" in generated_test


def test_generated_api_tests_support_raw_payload_strategy():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-LIVECODE-001",
                "automation_id": "AUTO-CASE-001",
                "title": "活码按真实参数发送",
                "path": "/contact/way/save",
                "method": "POST",
                "payload_strategy": "raw_payload",
                "payload": {
                    "name": "1111111111",
                    "categoryId": 16,
                    "corpId": "ww18a9d0bd0914df32",
                },
                "request_body": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "state": {"type": "string"},
                                    "userId": {"type": "integer"},
                                },
                                "required": ["state"],
                            }
                        }
                    }
                },
                "expected_status_codes": [200],
            }
        ]
    )

    assert "if case.get('payload_strategy') == 'raw_payload':" in generated_test


def test_generated_api_tests_skip_current_user_example_header():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-LIVECODE-001",
                "automation_id": "AUTO-CASE-001",
                "title": "活码登录鉴权请求",
                "path": "/contact/way/save",
                "method": "POST",
                "headers": [
                    {
                        "name": "CurrentUser",
                        "example": "example-current-user",
                    }
                ],
                "payload": {"name": "demo"},
                "expected_status_codes": [200],
            }
        ]
    )

    assert "if lowered in {'currentuser', 'authorization'}:" in generated_test


def test_generated_api_tests_support_case_skip_reason_and_base_url_override():
    generated_test = AutomationAgent()._build_generated_test_file(
        [
            {
                "test_case_id": "TC-LIVECODE-008",
                "automation_id": "AUTO-CASE-008",
                "title": "同步组织数据",
                "path": "/cp/org/synchro",
                "method": "GET",
                "base_url": "https://api.test.njxjjt.com/wx/mp/",
                "skip_reason": "no_data",
                "expected_status_codes": [200],
            }
        ]
    )

    assert "case.get('skip_reason')" in generated_test
    assert "pytest.skip(str(case['skip_reason']))" in generated_test
    assert "case.get('base_url')" in generated_test


def test_allure_viewing_guide_includes_actionable_commands(tmp_path):
    report_dir = tmp_path / "allure-report"
    results_dir = tmp_path / "allure-results"
    report_dir.mkdir()
    results_dir.mkdir()
    (report_dir / "index.html").write_text("<html></html>", encoding="utf-8")

    guide = AutomationAgent()._build_allure_viewing_guide(
        report_dir=report_dir,
        results_dir=results_dir,
        port=18088,
    )

    assert "index.html 的用途" in guide
    assert str(report_dir.resolve()) in guide
    assert str((report_dir / "index.html").resolve()) in guide
    assert "Set-Location -LiteralPath" in guide
    assert "python -m http.server 18088 --bind 127.0.0.1" in guide
    assert "http://127.0.0.1:18088/index.html" in guide
    assert "allure open" in guide
    assert "Start-Process" in guide


def test_automation_agent_reads_local_test_environment_config(tmp_path, monkeypatch):
    config_path = tmp_path / "test_environment.local.json"
    config_path.write_text(
        json.dumps(
            {
                "environments": {
                    "local": {
                        "api_base_url": "http://localhost:8000",
                        "auth": {
                            "front_user": {
                                "username": "testuser",
                                "password": "123456",
                                "login_path": "/api/front/auth/login",
                            },
                            "token": {
                                "json_path": "data.token",
                                "header_name": "Authorization",
                                "scheme": "Bearer",
                            },
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AI_PIPELINE_TEST_ENV_PROFILE", "local")

    env = AutomationAgent(test_environment_config_path=config_path)._build_pytest_env()

    assert env["API_BASE_URL"] == "http://localhost:8000"
    assert env["FRONT_USERNAME"] == "testuser"
    assert env["FRONT_PASSWORD"] == "123456"
    assert env["FRONT_LOGIN_PATH"] == "/api/front/auth/login"
    assert env["FRONT_TOKEN_JSON_PATH"] == "data.token"
    assert env["AUTH_HEADER_NAME"] == "Authorization"
    assert env["AUTH_SCHEME"] == "Bearer"


def test_automation_agent_template_config_overrides_runtime_env_defaults(tmp_path, monkeypatch):
    config_path = tmp_path / "test_environment.local.json"
    config_path.write_text(
        json.dumps(
            {
                "environments": {
                    "local": {
                        "api_base_url": "http://localhost:8000",
                        "auth": {
                            "front_user": {"username": "env-user", "password": "env-pass", "login_path": "/env/login"},
                            "token": {"json_path": "data.token", "header_name": "Authorization", "scheme": "Bearer"},
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AI_PIPELINE_TEST_ENV_PROFILE", "local")

    env = AutomationAgent(test_environment_config_path=config_path)._build_pytest_env(
        template_config={
            "API_BASE_URL": "https://api.test.njxjjt.com/operation/mp/",
            "FRONT_USERNAME": "template-user",
            "FRONT_LOGIN_PATH": "https://api.test.njxjjt.com/auth/ua/admin_login",
            "AUTH_SCHEME": "无前缀",
        }
    )

    assert env["API_BASE_URL"] == "https://api.test.njxjjt.com/operation/mp/"
    assert env["FRONT_USERNAME"] == "template-user"
    assert env["FRONT_LOGIN_PATH"] == "https://api.test.njxjjt.com/auth/ua/admin_login"
    assert env["AUTH_SCHEME"] == "无前缀"


def test_demo_pipeline_supports_relative_workspace_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = run_demo_pipeline(workspace_root=Path("workspace_rel"))
    execution_report = json.loads(
        (result.run_dir / "automation_agent" / "output" / "execution_report.json").read_text(encoding="utf-8")
    )

    assert execution_report["pytest_exit_code"] == 0
    assert execution_report["summary"]["skipped"] >= 1


def test_demo_pipeline_rebuilds_existing_run_directory(tmp_path):
    stale_run_dir = tmp_path / "runs" / "demo-run"
    stale_run_dir.mkdir(parents=True)
    stale_file = stale_run_dir / "stale.txt"
    stale_file.write_text("obsolete", encoding="utf-8")

    result = run_demo_pipeline(workspace_root=tmp_path)

    assert result.run_dir == stale_run_dir
    assert not stale_file.exists()
    assert (result.run_dir / "summary" / "manifest.json").exists()


def test_stage_state_records_subprocess_execution_metadata(tmp_path):
    result = run_demo_pipeline(workspace_root=tmp_path)

    for stage_dir_name in [
        "requirement_agent",
        "testcase_agent",
        "api_mapper_agent",
        "automation_agent",
    ]:
        state = json.loads((result.run_dir / stage_dir_name / "log" / "state.json").read_text(encoding="utf-8"))
        assert state["executor"]["mode"] == "subprocess"
        assert state["executor"]["exit_code"] == 0
        assert state["executor"]["command"]


def test_each_stage_runs_responsibility_lifecycle_before_and_after_execution(tmp_path):
    result = run_demo_pipeline(workspace_root=tmp_path)

    for stage_dir_name in [
        "requirement_agent",
        "testcase_agent",
        "api_mapper_agent",
        "automation_agent",
    ]:
        stage_dir = result.run_dir / stage_dir_name
        confirmation_path = stage_dir / "output" / "responsibility_confirmation.json"
        completion_path = stage_dir / "output" / "completion_validation.json"

        assert confirmation_path.exists()
        assert completion_path.exists()

        confirmation = json.loads(confirmation_path.read_text(encoding="utf-8"))
        completion = json.loads(completion_path.read_text(encoding="utf-8"))

        assert confirmation["agent_name"] == stage_dir_name
        assert confirmation["can_start"] is True
        assert confirmation["missing_inputs_or_preconditions"] == []
        assert confirmation["responsibility_self_check"]["input_is_sufficient"] is True
        assert confirmation["responsibility_self_check"]["must_block"] is False
        assert confirmation["responsibility_confirmation"]
        assert confirmation["should_do"]
        assert confirmation["should_not_do"]
        assert confirmation["input_dependencies"]
        assert confirmation["output_requirements"]
        assert confirmation["completion_criteria"]
        assert confirmation["blocking_conditions"]

        assert completion["agent_name"] == stage_dir_name
        assert completion["can_enter_next_stage"] is True
        assert completion["completion_check"]["required_outputs_complete"] is True
        assert completion["completion_check"]["responsibility_overreach_detected"] is False
        assert completion["completion_check"]["required_responsibilities_missing"] is False
        assert completion["completion_check"]["remaining_blockers"] == []
        assert completion["completion_check"]["next_stage_ready"] is True

    event_lines = [
        json.loads(line)
        for line in (result.run_dir / "summary" / "run_log.jsonl").read_text(encoding="utf-8").strip().splitlines()
    ]
    events_by_stage: dict[str, list[str]] = {}
    for event in event_lines:
        events_by_stage.setdefault(event["agent_name"], []).append(event["event"])

    for stage_dir_name in [
        "requirement_agent",
        "testcase_agent",
        "api_mapper_agent",
        "automation_agent",
    ]:
        stage_events = events_by_stage[stage_dir_name]
        assert stage_events.index("responsibility_identified") < stage_events.index("stage_started")
        assert stage_events.index("completion_validated") > stage_events.index("stage_completed")
