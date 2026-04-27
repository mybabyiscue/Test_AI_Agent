from __future__ import annotations

import json

from ai_pipeline.credentials import EnvCredentialProvider
from ai_pipeline.knowledge_sync import (
    KnowledgeSyncer,
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


def test_openapi_is_normalized_to_apifox_knowledge_with_chinese_file_info():
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

    assert result["file_info"]["file_name"] == "apifox_project_776242.json"
    assert result["file_info"]["purpose"]
    assert result["system"] == "silkroad"
    assert result["apis"][0]["api_name"] == "查询用户"
    assert result["apis"][0]["method"] == "GET"
    assert result["apis"][0]["path"] == "/users/{id}"
    assert result["apis"][0]["module"] == "用户"
    assert result["sync_mode"] == "basic_api_index"
    assert "headers" not in result["apis"][0]
    assert "path_params" not in result["apis"][0]
    assert "query_params" not in result["apis"][0]
    assert "request_body" not in result["apis"][0]
    assert "response_body" not in result["apis"][0]


def test_openapi_normalization_keeps_only_basic_interface_index():
    openapi = {
        "paths": {
            "/contact/way/save": {
                "post": {
                    "summary": "新增 渠道活码",
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
                "WeworkContactWayDTO": {
                    "type": "object",
                    "properties": {
                        "nextAutoEnableTime": {
                            "type": "string",
                            "description": "次日自动上线触发时间",
                        }
                    },
                },
                "ServerResponseEntityLong": {
                    "type": "object",
                    "properties": {"data": {"type": "integer", "format": "int64"}},
                },
            }
        },
    }

    result = normalize_openapi_to_apifox_knowledge(
        system="saas",
        project_id="4152663",
        source_url="https://app.apifox.com/project/4152663",
        openapi=openapi,
    )

    assert "components" not in result
    assert result["apis"][0] == {
        "module": "渠道活码",
        "folder_path": ["渠道活码"],
        "api_name": "新增 渠道活码",
        "method": "POST",
        "path": "/contact/way/save",
        "description": "",
        "operation_id": "",
        "tags": ["渠道活码"],
        "missing_fields": ["description"],
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
        json.dumps(
            {
                "systems": {
                    "silkroad": {
                        "databases": {"profile": "silkroad", "schemas": ["center"]},
                        "apis": [],
                    }
                }
            }
        ),
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
