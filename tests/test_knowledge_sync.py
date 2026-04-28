from __future__ import annotations

import json
from ai_pipeline.credentials import EnvCredentialProvider
from ai_pipeline.knowledge_sync import (
    BASIC_API_INDEX_DETAIL_FETCH_POLICY,
    BASIC_API_INDEX_SYNC_MODE,
    KnowledgeSyncer,
    normalize_http_apis_to_apifox_knowledge,
    normalize_openapi_to_apifox_knowledge,
)


def test_database_credentials_are_read_from_local_file_and_redacted(tmp_path):
    credentials_file = tmp_path / "credentials.local.json"
    credentials_file.write_text(
        json.dumps(
            {
                "databases": {
                    "silkroad": {
                        "type": "mysql",
                        "host": "127.0.0.1",
                        "port": 3306,
                        "user": "tester",
                        "password": "secret-password",
                        "description": "测试数据库",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    credential = EnvCredentialProvider(credentials_file=credentials_file).get_database("silkroad")

    assert credential.host == "127.0.0.1"
    assert credential.password == "secret-password"
    assert credential.redacted()["password"] == "***word"


def test_openapi_is_normalized_to_basic_apifox_index():
    openapi = {
        "paths": {
            "/users/{id}": {
                "get": {
                    "summary": "查询用户",
                    "description": "根据用户 ID 查询用户详情",
                    "tags": ["用户"],
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                        {"name": "verbose", "in": "query", "required": False, "schema": {"type": "boolean"}},
                    ],
                    "responses": {"200": {"description": "成功"}},
                }
            }
        }
    }

    result = normalize_openapi_to_apifox_knowledge(
        system="silkroad",
        project_id="776242",
        source_url="https://app.apifox.com/project/776242",
        openapi=openapi,
    )

    interface = result["apis"][0]
    assert result["file_info"]["file_name"] == "apifox_project_776242.json"
    assert result["system"] == "silkroad"
    assert result["sync_mode"] == BASIC_API_INDEX_SYNC_MODE
    assert result["detail_fetch_policy"] == BASIC_API_INDEX_DETAIL_FETCH_POLICY
    assert interface["api_name"] == "查询用户"
    assert interface["method"] == "GET"
    assert interface["path"] == "/users/{id}"
    assert interface["module"] == "用户"
    assert interface["source"] == "https://app.apifox.com/project/776242"
    assert interface["project_id"] == "776242"
    assert interface["sync_mode"] == BASIC_API_INDEX_SYNC_MODE
    assert interface["detail_fetch_policy"] == BASIC_API_INDEX_DETAIL_FETCH_POLICY
    assert "headers" not in interface
    assert "path_params" not in interface
    assert "query_params" not in interface
    assert "request_body" not in interface
    assert "response_body" not in interface
    assert "components" not in result


def test_openapi_normalization_marks_unknown_fields_as_pending_confirmation():
    openapi = {
        "paths": {
            "/contact/way/save": {
                "post": {
                    "summary": "新增渠道活码",
                    "tags": ["渠道活码"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/WeworkContactWayDTO"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "成功",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ServerResponseEntityLong"}
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "WeworkContactWayDTO": {"type": "object", "properties": {"nextAutoEnableTime": {"type": "string"}}},
                "ServerResponseEntityLong": {"type": "object", "properties": {"data": {"type": "integer"}}},
            }
        },
    }

    result = normalize_openapi_to_apifox_knowledge(
        system="saas",
        project_id="4152663",
        source_url="https://app.apifox.com/project/4152663",
        openapi=openapi,
    )

    assert result["apis"][0] == {
        "module": "渠道活码",
        "folder_path": ["渠道活码"],
        "api_name": "新增渠道活码",
        "method": "POST",
        "path": "/contact/way/save",
        "description": "",
        "operation_id": "",
        "tags": ["渠道活码"],
        "source": "https://app.apifox.com/project/4152663",
        "project_id": "4152663",
        "updated_at": "待确认",
        "sync_mode": BASIC_API_INDEX_SYNC_MODE,
        "detail_fetch_policy": BASIC_API_INDEX_DETAIL_FETCH_POLICY,
        "missing_fields": ["description", "updated_at"],
    }


def test_syncer_writes_failure_report_without_secret_leakage(tmp_path):
    credentials_file = tmp_path / "credentials.local.json"
    credentials_file.write_text(
        json.dumps(
            {
                "databases": {
                    "silkroad": {
                        "type": "mysql",
                        "host": "127.0.0.1",
                        "port": 1,
                        "user": "tester",
                        "password": "secret-password",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    sources_file = tmp_path / "knowledge_sources.example.json"
    sources_file.write_text(
        json.dumps({"systems": {"silkroad": {"databases": {"profile": "silkroad", "schemas": ["center"]}, "apis": []}}}),
        encoding="utf-8",
    )

    report = KnowledgeSyncer(
        knowledge_root=tmp_path / "knowledge_base",
        sources_config_path=sources_file,
        credentials_file=credentials_file,
    ).sync_all(sync_apis=False)

    report_text = json.dumps(report, ensure_ascii=False)
    assert report["summary"]["failed_databases"] == 1
    assert "secret-password" not in report_text
    assert (tmp_path / "knowledge_base" / "sync_reports").exists()


def test_http_api_list_is_normalized_to_basic_index_without_detail_fields():
    result = normalize_http_apis_to_apifox_knowledge(
        system="saas",
        project_id="4152663",
        source_url="https://app.apifox.com/project/4152663",
        http_apis=[
            {
                "id": 101,
                "moduleName": "渠道活码",
                "name": "新增渠道活码",
                "method": "post",
                "path": "/contact/way/save",
                "updatedAt": "2026-04-27T16:00:00+08:00",
            }
        ],
    )

    assert result["sync_mode"] == BASIC_API_INDEX_SYNC_MODE
    assert result["detail_fetch_policy"] == BASIC_API_INDEX_DETAIL_FETCH_POLICY
    assert result["apis"][0] == {
        "module": "渠道活码",
        "folder_path": [],
        "api_name": "新增渠道活码",
        "method": "POST",
        "path": "/contact/way/save",
        "description": "",
        "operation_id": "",
        "tags": [],
        "source": "https://app.apifox.com/project/4152663",
        "project_id": "4152663",
        "updated_at": "2026-04-27T16:00:00+08:00",
        "sync_mode": BASIC_API_INDEX_SYNC_MODE,
        "detail_fetch_policy": BASIC_API_INDEX_DETAIL_FETCH_POLICY,
        "missing_fields": ["description"],
    }


def test_syncer_uses_http_api_list_for_basic_index_sync_without_export_openapi(tmp_path, monkeypatch):
    credentials_file = tmp_path / "credentials.local.json"
    credentials_file.write_text(
        json.dumps({"platforms": {"apifox": {"default": {"token": "secret-token"}}}}),
        encoding="utf-8",
    )
    sources_file = tmp_path / "knowledge_sources.example.json"
    sources_file.write_text(
        json.dumps(
            {
                "systems": {
                    "saas": {
                        "apis": [
                            {
                                "platform": "apifox",
                                "project_id": "4152663",
                                "url": "https://app.apifox.com/project/4152663",
                                "credential_profile": "default",
                            }
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    class ListOnlyClient:
        def __init__(self, credential) -> None:
            self.credential = credential

        def list_http_apis(self, project_id: str) -> list[dict[str, object]]:
            return [
                {"id": 101, "name": "Alpha", "method": "get", "path": "/alpha", "moduleName": "A"},
                {"id": 202, "name": "Beta", "method": "post", "path": "/beta", "moduleName": "B"},
            ]

        def export_openapi(self, project_id: str, **kwargs):
            raise AssertionError("knowledge sync must not call export_openapi for basic index sync")

    monkeypatch.setattr("ai_pipeline.knowledge_sync.ApifoxClient", ListOnlyClient)

    report = KnowledgeSyncer(
        knowledge_root=tmp_path / "knowledge_base",
        sources_config_path=sources_file,
        credentials_file=credentials_file,
    ).sync_all(sync_databases=False)

    target = tmp_path / "knowledge_base" / "saas" / "apis" / "apifox_project_4152663.json"
    payload = json.loads(target.read_text(encoding="utf-8"))

    assert report["summary"]["successful_api_projects"] == 1
    assert report["summary"]["failed_api_projects"] == 0
    assert len(payload["apis"]) == 2
    assert {(item["method"], item["path"]) for item in payload["apis"]} == {("GET", "/alpha"), ("POST", "/beta")}
