from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError

from .credentials import EnvCredentialProvider, PlatformCredential
from .knowledge_sync import BASIC_API_INDEX_DETAIL_FETCH_POLICY, BASIC_API_INDEX_SYNC_MODE
from .platforms.apifox import ApifoxClient, ApifoxSource, parse_apifox_url


class CredentialProvider(Protocol):
    def get(self, platform: str, profile: str = "default") -> PlatformCredential:
        ...


@dataclass(slots=True)
class ApiDocumentResolver:
    credential_provider: CredentialProvider
    apifox_client_factory: Any = ApifoxClient

    @classmethod
    def default(cls) -> "ApiDocumentResolver":
        return cls(credential_provider=EnvCredentialProvider())

    def resolve_apifox_url(self, api_source_url: str) -> tuple[ApifoxSource, dict[str, Any]]:
        source = parse_apifox_url(api_source_url)
        return source, self.resolve_apifox_project_index(source.project_id, source.url)

    def resolve_apifox_project(self, project_id: str) -> dict[str, Any]:
        credential = self.credential_provider.get("apifox")
        client = self.apifox_client_factory(credential=credential)
        try:
            return client.export_openapi(project_id=project_id)
        except HTTPError as exc:
            reason = "token_or_permission_error" if exc.code in {401, 403} else "url_or_project_error"
            raise RuntimeError(f"Apifox detail fetch failed: {reason}; http_status={exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"Apifox detail fetch failed: network_or_url_error; reason={exc.reason}") from exc
        except KeyError as exc:
            raise RuntimeError(f"Apifox detail fetch failed: response_field_missing; field={exc}") from exc

    def resolve_apifox_project_index(self, project_id: str, source_url: str | None = None) -> dict[str, Any]:
        credential = self.credential_provider.get("apifox")
        client = self.apifox_client_factory(credential=credential)
        try:
            http_apis = client.list_http_apis(project_id=project_id)
            resolved_source = source_url or f"https://app.apifox.com/project/{project_id}"
            return {
                "platform": "apifox",
                "project_id": project_id,
                "source_url": resolved_source,
                "sync_mode": BASIC_API_INDEX_SYNC_MODE,
                "detail_fetch_policy": BASIC_API_INDEX_DETAIL_FETCH_POLICY,
                "apis": [_normalize_http_api_to_basic_index_item(item, project_id, resolved_source) for item in http_apis],
            }
        except HTTPError as exc:
            reason = "token_or_permission_error" if exc.code in {401, 403} else "url_or_project_error"
            raise RuntimeError(f"Apifox index fetch failed: {reason}; http_status={exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"Apifox index fetch failed: network_or_url_error; reason={exc.reason}") from exc

    def resolve_apifox_project_for_endpoints(
        self,
        *,
        project_id: str,
        endpoints: list[dict[str, str]],
    ) -> dict[str, Any]:
        credential = self.credential_provider.get("apifox")
        client = self.apifox_client_factory(credential=credential)
        try:
            http_apis = client.list_http_apis(project_id=project_id)
            selected = _select_http_apis(http_apis, endpoints)
            if not selected:
                raise RuntimeError("Apifox detail fetch failed: no_matching_endpoint_ids")
            endpoint_ids = [int(item["id"]) for item in selected if item.get("id") is not None]
            module_ids = {int(item["moduleId"]) for item in selected if item.get("moduleId") is not None}
            module_id = next(iter(module_ids)) if len(module_ids) == 1 else None
            kwargs: dict[str, Any] = {"endpoint_ids": endpoint_ids}
            if module_id is not None:
                kwargs["module_id"] = module_id
            return client.export_openapi(project_id=project_id, **kwargs)
        except HTTPError as exc:
            reason = "token_or_permission_error" if exc.code in {401, 403} else "url_or_project_error"
            raise RuntimeError(f"Apifox detail fetch failed: {reason}; http_status={exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"Apifox detail fetch failed: network_or_url_error; reason={exc.reason}") from exc
        except KeyError as exc:
            raise RuntimeError(f"Apifox detail fetch failed: response_field_missing; field={exc}") from exc


def _normalize_http_api_to_basic_index_item(
    item: dict[str, Any],
    project_id: str,
    source_url: str,
) -> dict[str, Any]:
    tags = _normalize_tags(item)
    description = str(item.get("description") or item.get("desc") or "")
    updated_at = item.get("updatedAt") or item.get("updated_at") or "待确认"
    missing_fields: list[str] = []
    if not description:
        missing_fields.append("description")
    if updated_at == "待确认":
        missing_fields.append("updated_at")
    return {
        "id": str(item.get("id", "")),
        "module": str(item.get("moduleName") or item.get("module") or (tags[0] if tags else "")),
        "folder_path": tags,
        "api_name": str(item.get("name") or item.get("summary") or item.get("title") or ""),
        "method": str(item.get("method", "")).upper(),
        "path": str(item.get("path", "")),
        "description": description,
        "operation_id": str(item.get("operationId") or item.get("operation_id") or ""),
        "tags": tags,
        "source": source_url,
        "project_id": project_id,
        "updated_at": str(updated_at),
        "sync_mode": BASIC_API_INDEX_SYNC_MODE,
        "detail_fetch_policy": BASIC_API_INDEX_DETAIL_FETCH_POLICY,
        "missing_fields": missing_fields,
    }


def _normalize_tags(item: dict[str, Any]) -> list[str]:
    raw = item.get("folderPath") or item.get("folder_path") or item.get("tags") or []
    if isinstance(raw, list):
        return [str(value) for value in raw]
    if isinstance(raw, str) and raw:
        return [raw]
    return []


def _select_http_apis(
    http_apis: list[dict[str, Any]],
    endpoints: list[dict[str, str]],
) -> list[dict[str, Any]]:
    requested = {
        (str(endpoint.get("method", "")).upper(), str(endpoint.get("path", "")))
        for endpoint in endpoints
    }
    requested_ids = {str(endpoint.get("id", "")) for endpoint in endpoints if endpoint.get("id")}
    selected = []
    seen: set[tuple[str, str, int]] = set()
    for item in http_apis:
        method = str(item.get("method", "")).upper()
        path = str(item.get("path", ""))
        api_id = item.get("id")
        id_match = str(api_id) in requested_ids if api_id is not None else False
        path_match = (method, path) in requested
        if not (id_match or path_match) or api_id is None:
            continue
        key = (method, path, int(api_id))
        if key in seen:
            continue
        seen.add(key)
        selected.append(item)
    return selected
