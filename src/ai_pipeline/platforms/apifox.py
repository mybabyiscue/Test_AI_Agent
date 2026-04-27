from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

from ..credentials import PlatformCredential


@dataclass(frozen=True, slots=True)
class ApifoxSource:
    platform: str
    url: str
    project_id: str
    resource_type: str
    resource_id: str | None = None

    def to_declaration(self) -> dict[str, str | None]:
        return {
            "platform": self.platform,
            "url": self.url,
            "project_id": self.project_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
        }


@dataclass(frozen=True, slots=True)
class HttpRequestSpec:
    method: str
    url: str
    headers: dict[str, str]
    body: dict[str, Any]

    def redacted(self) -> dict[str, Any]:
        headers = dict(self.headers)
        if "Authorization" in headers:
            headers["Authorization"] = _redact_authorization(headers["Authorization"])
        return {
            "method": self.method,
            "url": self.url,
            "headers": headers,
            "body": self.body,
        }


class ApifoxClient:
    def __init__(
        self,
        credential: PlatformCredential,
        base_url: str = "https://api.apifox.com",
        api_version: str = "2024-03-28",
    ) -> None:
        self._credential = credential
        self._base_url = base_url.rstrip("/")
        self._api_version = api_version

    def build_export_openapi_request(
        self,
        project_id: str,
        *,
        endpoint_ids: list[int] | None = None,
        folder_ids: list[int] | None = None,
        selected_tags: list[str] | None = None,
        module_id: int | None = None,
    ) -> HttpRequestSpec:
        scope = self._build_export_scope(
            endpoint_ids=endpoint_ids,
            folder_ids=folder_ids,
            selected_tags=selected_tags,
        )
        body: dict[str, Any] = {
            "scope": scope,
            "options": {
                "includeApifoxExtensionProperties": False,
                "addFoldersToTags": True,
            },
            "oasVersion": "3.1",
            "exportFormat": "JSON",
        }
        if module_id is not None:
            body["moduleId"] = module_id
        return HttpRequestSpec(
            method="POST",
            url=f"{self._base_url}/v1/projects/{project_id}/export-openapi?locale=zh-CN",
            headers={
                "Authorization": f"Bearer {self._credential.token}",
                "Content-Type": "application/json",
                "X-Apifox-Api-Version": self._api_version,
            },
            body=body,
        )

    def export_openapi(
        self,
        project_id: str,
        *,
        endpoint_ids: list[int] | None = None,
        folder_ids: list[int] | None = None,
        selected_tags: list[str] | None = None,
        module_id: int | None = None,
    ) -> dict[str, Any]:
        spec = self.build_export_openapi_request(
            project_id,
            endpoint_ids=endpoint_ids,
            folder_ids=folder_ids,
            selected_tags=selected_tags,
            module_id=module_id,
        )
        request = urllib.request.Request(
            spec.url,
            data=json.dumps(spec.body).encode("utf-8"),
            headers=spec.headers,
            method=spec.method,
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_http_apis(self, project_id: str) -> list[dict[str, Any]]:
        request = urllib.request.Request(
            f"{self._base_url}/api/v1/projects/{project_id}/http-apis",
            headers={
                "Authorization": f"Bearer {self._credential.token}",
                "Accept": "application/json",
                "X-Apifox-Api-Version": self._api_version,
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data") if isinstance(payload, dict) else None
        return data if isinstance(data, list) else []

    def _build_export_scope(
        self,
        *,
        endpoint_ids: list[int] | None,
        folder_ids: list[int] | None,
        selected_tags: list[str] | None,
    ) -> dict[str, Any]:
        selected_modes = sum(bool(value) for value in [endpoint_ids, folder_ids, selected_tags])
        if selected_modes > 1:
            raise ValueError("Only one Apifox export scope selector can be provided.")
        if endpoint_ids:
            return {"type": "SELECTED_ENDPOINTS", "selectedEndpointIds": endpoint_ids}
        if folder_ids:
            return {"type": "SELECTED_FOLDERS", "selectedFolderIds": folder_ids}
        if selected_tags:
            return {"type": "SELECTED_TAGS", "selectedTags": selected_tags}
        return {"type": "ALL"}


def parse_apifox_url(url: str) -> ApifoxSource:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    path = parsed.path

    project_id = _first_query_value(query, "projectId", "project_id", "project")
    if not project_id:
        project_id = _first_regex_group(
            path,
            [
                r"/projects?/(\d+)",
                r"/apidoc/(?:docs-site/)?(\d+)",
                r"/project-(\d+)",
                r"/(\d+)",
            ],
        )

    if not project_id:
        raise ValueError(f"无法从 Apifox URL 中识别 project_id: {url}")

    api_id = _first_regex_group(path, [r"/api-(\d+)", r"/apis?/(\d+)"])
    folder_id = _first_regex_group(path, [r"/folder-(\d+)", r"/folders?/(\d+)"])

    if api_id:
        return ApifoxSource("apifox", url, project_id, "api", api_id)
    if folder_id:
        return ApifoxSource("apifox", url, project_id, "folder", folder_id)
    return ApifoxSource("apifox", url, project_id, "project", None)


def _first_query_value(query: dict[str, list[str]], *names: str) -> str | None:
    for name in names:
        values = query.get(name)
        if values:
            return values[0]
    return None


def _first_regex_group(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _redact_authorization(value: str) -> str:
    prefix = "Bearer "
    if value.startswith(prefix):
        token = value[len(prefix):]
        return f"{prefix}{_redact_token(token)}"
    return "***"


def _redact_token(token: str) -> str:
    if len(token) <= 4:
        return "***"
    return f"***{token[-4:]}"
