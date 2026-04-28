from __future__ import annotations

import json
from pathlib import Path

from ai_pipeline.orchestrator import PipelineOrchestrator
from ai_pipeline.platforms.apifox import parse_apifox_url


class FakeApiDocumentResolver:
    def __init__(self) -> None:
        self.full_project_calls: list[str] = []
        self.index_calls: list[str] = []
        self.endpoint_calls: list[dict[str, object]] = []

    def resolve_apifox_url(self, api_source_url: str):
        source = parse_apifox_url(api_source_url)
        return source, self.resolve_apifox_project_index(source.project_id, source.url)

    def resolve_apifox_project(self, project_id: str):
        self.full_project_calls.append(project_id)
        return {"openapi": "3.1.0", "paths": {}}

    def resolve_apifox_project_index(self, project_id: str, source_url: str | None = None):
        self.index_calls.append(project_id)
        return {
            "platform": "apifox",
            "project_id": project_id,
            "source_url": source_url or f"https://app.apifox.com/project/{project_id}",
            "sync_mode": "basic_api_index",
            "detail_fetch_policy": "index only",
            "apis": [
                {
                    "id": "101",
                    "api_name": "Create order",
                    "method": "POST",
                    "path": "/orders",
                    "module": "Order",
                    "folder_path": ["Order"],
                    "description": "",
                    "operation_id": "",
                    "tags": ["Order"],
                    "source": source_url or f"https://app.apifox.com/project/{project_id}",
                    "project_id": project_id,
                    "updated_at": "待确认",
                    "sync_mode": "basic_api_index",
                    "detail_fetch_policy": "index only",
                    "missing_fields": ["description", "updated_at"],
                }
            ],
        }

    def resolve_apifox_project_for_endpoints(self, *, project_id: str, endpoints: list[dict[str, str]]):
        self.endpoint_calls.append({"project_id": project_id, "endpoints": endpoints})
        return {
            "openapi": "3.1.0",
            "info": {"title": "Fake Apifox Service", "version": "1.0.0"},
            "paths": {
                "/orders": {
                    "post": {
                        "summary": "创建订单",
                        "responses": {"201": {"description": "Created"}},
                    }
                }
            },
        }


def test_orchestrator_fetches_selected_endpoint_detail_from_apifox_source_without_exposing_token(tmp_path):
    requirement_path = Path("examples/requirements/sample_requirement.md").resolve()
    resolver = FakeApiDocumentResolver()
    orchestrator = PipelineOrchestrator(api_document_resolver=resolver)

    result = orchestrator.run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="apifox-run",
        api_source_url="https://app.apifox.com/project/123456/api-789",
        require_test_points=False,
    )

    api_mapper_input = result.run_dir / "api_mapper_agent" / "input"
    api_mapper_output = result.run_dir / "api_mapper_agent" / "output"
    source_request = json.loads((api_mapper_input / "api_source_request.json").read_text(encoding="utf-8"))
    output_source_request = json.loads((api_mapper_output / "api_source_request.json").read_text(encoding="utf-8"))
    fetched_document = json.loads((api_mapper_input / "api_document.json").read_text(encoding="utf-8"))
    endpoint_mapping = json.loads((result.run_dir / "api_mapper_agent" / "output" / "endpoint_mapping.json").read_text(encoding="utf-8"))
    api_catalog_md = (api_mapper_output / "apis" / "api_catalog.md").read_text(encoding="utf-8")
    source_request_md = (api_mapper_output / "apis" / "api_source_request.md").read_text(encoding="utf-8")

    assert source_request["platform"] == "apifox"
    assert source_request["project_id"] == "123456"
    assert "token" not in json.dumps(source_request, ensure_ascii=False)
    assert "Authorization" not in json.dumps(source_request, ensure_ascii=False)
    assert output_source_request == source_request
    assert fetched_document["info"]["title"] == "Fake Apifox Service"
    assert endpoint_mapping["mappings"][0]["path"] == "/orders"
    assert "Fake Apifox Service" in api_catalog_md
    assert "https://app.apifox.com/project/123456/api-789" in source_request_md
    assert resolver.full_project_calls == []
    assert resolver.endpoint_calls
    assert resolver.endpoint_calls[0]["endpoints"] == [{"id": "101", "method": "POST", "path": "/orders"}]


def test_orchestrator_expands_basic_knowledge_index_through_endpoint_only_detail_fetch(tmp_path):
    requirement_path = Path("examples/requirements/sample_requirement.md").resolve()
    api_index_path = tmp_path / "apifox_project_123456.json"
    api_index_path.write_text(
        json.dumps(
            {
                "platform": "apifox",
                "project_id": "123456",
                "source_url": "https://app.apifox.com/project/123456",
                "sync_mode": "basic_api_index",
                "detail_fetch_policy": "index only",
                "apis": [
                    {
                        "id": "101",
                        "api_name": "Create order",
                        "method": "POST",
                        "path": "/orders",
                        "module": "Order",
                        "folder_path": ["Order"],
                        "description": "",
                        "operation_id": "",
                        "tags": ["Order"],
                        "source": "https://app.apifox.com/project/123456",
                        "project_id": "123456",
                        "updated_at": "待确认",
                        "sync_mode": "basic_api_index",
                        "detail_fetch_policy": "index only",
                        "missing_fields": ["description", "updated_at"],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    resolver = FakeApiDocumentResolver()
    orchestrator = PipelineOrchestrator(api_document_resolver=resolver)

    result = orchestrator.run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="apifox-index-run",
        api_doc_path=api_index_path,
        require_test_points=False,
    )

    api_mapper_input = result.run_dir / "api_mapper_agent" / "input"
    api_mapper_output = result.run_dir / "api_mapper_agent" / "output"
    fetched_document = json.loads((api_mapper_input / "api_document.json").read_text(encoding="utf-8"))
    knowledge_index = json.loads((api_mapper_input / "api_knowledge_index.json").read_text(encoding="utf-8"))
    selected_candidates = json.loads((api_mapper_input / "selected_endpoint_candidates.json").read_text(encoding="utf-8"))
    api_catalog = json.loads((api_mapper_output / "api_catalog.json").read_text(encoding="utf-8"))
    interface = api_catalog["selected_interfaces"][0]

    assert knowledge_index["sync_mode"] == "basic_api_index"
    assert fetched_document["paths"]["/orders"]["post"]["summary"] == "创建订单"
    assert interface["response_body"]["201"]["description"] == "Created"
    assert interface["interface_detail_status"] == "detail_fetched_from_apifox_openapi"
    assert selected_candidates["endpoints"] == [{"id": "101", "method": "POST", "path": "/orders"}]
    assert resolver.full_project_calls == []


def test_orchestrator_handles_utf8_agent_output_for_chinese_cart_requirement(tmp_path):
    requirement_path = tmp_path / "购物车需求.md"
    requirement_path.write_text(
        "\n".join(
            [
                "# 宠物商店系统购物车功能 PRD",
                "- 将宠物加入购物车",
                "- 从购物车发起结算并生成订单",
            ]
        ),
        encoding="utf-8",
    )
    orchestrator = PipelineOrchestrator(api_document_resolver=FakeApiDocumentResolver())

    result = orchestrator.run(
        requirement_path=requirement_path,
        workspace_root=tmp_path,
        run_id="utf8-cart-run",
        api_source_url="https://app.apifox.com/project/123456",
    )

    requirement_model = json.loads((result.run_dir / "requirement_agent" / "output" / "requirement_model.json").read_text(encoding="utf-8"))

    assert requirement_model["title"] == "宠物商店系统购物车功能"
