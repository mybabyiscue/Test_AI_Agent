from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError

from .credentials import EnvCredentialProvider, PlatformCredential
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
        return source, self.resolve_apifox_project(source.project_id)

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


def _select_http_apis(
    http_apis: list[dict[str, Any]],
    endpoints: list[dict[str, str]],
) -> list[dict[str, Any]]:
    requested = {
        (str(endpoint.get("method", "")).upper(), str(endpoint.get("path", "")))
        for endpoint in endpoints
    }
    selected = []
    seen: set[tuple[str, str, int]] = set()
    for item in http_apis:
        method = str(item.get("method", "")).upper()
        path = str(item.get("path", ""))
        api_id = item.get("id")
        if (method, path) not in requested or api_id is None:
            continue
        key = (method, path, int(api_id))
        if key in seen:
            continue
        seen.add(key)
        selected.append(item)
    return selected
