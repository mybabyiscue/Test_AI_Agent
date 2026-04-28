from __future__ import annotations

import json

from ai_pipeline.agents import ApiMapperAgent
from ai_pipeline.api_document_resolver import ApiDocumentResolver
from ai_pipeline.credentials import PlatformCredential
from ai_pipeline.knowledge_sync import BASIC_API_INDEX_DETAIL_FETCH_POLICY, BASIC_API_INDEX_SYNC_MODE
from ai_pipeline.platforms.apifox import ApifoxClient, parse_apifox_url


class FakeCredentialProvider:
    def get(self, platform: str, profile: str = "default") -> PlatformCredential:
        return PlatformCredential(platform=platform, token="secret-token", profile=profile, source="test")


class RecordingApifoxClient:
    def __init__(self, credential: PlatformCredential) -> None:
        self.credential = credential
        self.export_calls: list[dict[str, object]] = []

    def list_http_apis(self, project_id: str) -> list[dict[str, object]]:
        return [
            {
                "id": 101,
                "name": "Create order",
                "method": "post",
                "path": "/orders",
                "moduleId": 303,
                "moduleName": "Order",
                "updatedAt": "2026-04-27T10:00:00+08:00",
            },
            {"id": 202, "name": "Get order", "method": "get", "path": "/orders/{id}", "moduleId": 303},
            {"id": 909, "name": "Unrelated", "method": "post", "path": "/unrelated", "moduleId": 303},
        ]

    def export_openapi(self, project_id: str, **kwargs):
        self.export_calls.append({"project_id": project_id, **kwargs})
        return {"openapi": "3.1.0", "paths": {"/orders": {"post": {"summary": "Create order"}}}}


def test_api_mapper_agent_declares_apifox_source_without_token():
    declaration = ApiMapperAgent().declare_api_source("https://app.apifox.com/project/123456/api-789")

    assert declaration["platform"] == "apifox"
    assert declaration["project_id"] == "123456"
    assert declaration["resource_type"] == "api"
    assert "token" not in json.dumps(declaration, ensure_ascii=False)
    assert "Authorization" not in json.dumps(declaration, ensure_ascii=False)


def test_parse_apifox_url_supports_project_and_api_ids():
    source = parse_apifox_url("https://app.apifox.com/project/123456/api-789")

    assert source.platform == "apifox"
    assert source.project_id == "123456"
    assert source.resource_type == "api"
    assert source.resource_id == "789"


def test_parse_apifox_url_supports_shared_apidoc_url():
    source = parse_apifox_url("https://s.apifox.cn/apidoc/docs-site/4478210/api-173411997")

    assert source.platform == "apifox"
    assert source.project_id == "4478210"
    assert source.resource_type == "api"
    assert source.resource_id == "173411997"


def test_apifox_client_builds_export_openapi_request_without_persisting_token():
    credential = PlatformCredential(platform="apifox", token="secret-token", profile="default", source="test")
    client = ApifoxClient(credential=credential)

    request_spec = client.build_export_openapi_request(project_id="123456")

    assert request_spec.method == "POST"
    assert request_spec.url == "https://api.apifox.com/v1/projects/123456/export-openapi?locale=zh-CN"
    assert request_spec.headers["Authorization"] == "Bearer secret-token"
    assert request_spec.headers["X-Apifox-Api-Version"] == "2024-03-28"
    assert request_spec.body["exportFormat"] == "JSON"
    assert request_spec.redacted()["headers"]["Authorization"] == "Bearer ***oken"


def test_apifox_client_builds_selected_endpoint_export_request():
    credential = PlatformCredential(platform="apifox", token="secret-token", profile="default", source="test")
    client = ApifoxClient(credential=credential)

    request_spec = client.build_export_openapi_request(project_id="123456", endpoint_ids=[101, 202], module_id=303)

    assert request_spec.body["scope"] == {"type": "SELECTED_ENDPOINTS", "selectedEndpointIds": [101, 202]}
    assert request_spec.body["moduleId"] == 303


def test_apifox_client_builds_selected_folder_export_request():
    credential = PlatformCredential(platform="apifox", token="secret-token", profile="default", source="test")
    client = ApifoxClient(credential=credential)

    request_spec = client.build_export_openapi_request(project_id="123456", folder_ids=[11, 22])

    assert request_spec.body["scope"] == {"type": "SELECTED_FOLDERS", "selectedFolderIds": [11, 22]}


def test_api_document_resolver_fetches_only_matched_endpoint_details():
    clients: list[RecordingApifoxClient] = []

    def make_client(credential: PlatformCredential) -> RecordingApifoxClient:
        client = RecordingApifoxClient(credential)
        clients.append(client)
        return client

    resolver = ApiDocumentResolver(credential_provider=FakeCredentialProvider(), apifox_client_factory=make_client)

    document = resolver.resolve_apifox_project_for_endpoints(
        project_id="123456",
        endpoints=[{"method": "POST", "path": "/orders"}],
    )

    assert document["paths"]["/orders"]["post"]["summary"] == "Create order"
    assert clients[0].export_calls == [{"project_id": "123456", "endpoint_ids": [101], "module_id": 303}]


def test_api_document_resolver_builds_basic_index_without_detail_fields():
    resolver = ApiDocumentResolver(credential_provider=FakeCredentialProvider(), apifox_client_factory=RecordingApifoxClient)

    index = resolver.resolve_apifox_project_index("123456", "https://app.apifox.com/project/123456")
    interface = index["apis"][0]

    assert index["sync_mode"] == BASIC_API_INDEX_SYNC_MODE
    assert index["detail_fetch_policy"] == BASIC_API_INDEX_DETAIL_FETCH_POLICY
    assert interface["source"] == "https://app.apifox.com/project/123456"
    assert interface["project_id"] == "123456"
    assert interface["sync_mode"] == BASIC_API_INDEX_SYNC_MODE
    assert interface["detail_fetch_policy"] == BASIC_API_INDEX_DETAIL_FETCH_POLICY
    assert "headers" not in interface
    assert "request_body" not in interface
    assert "response_body" not in interface
