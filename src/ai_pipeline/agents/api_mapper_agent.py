from __future__ import annotations

import copy
from typing import Any

from ..platforms.apifox import parse_apifox_url
from .role_profiles import get_role_profile


class ApiMapperAgent:
    agent_name = "api_mapper_agent"
    stage_name = "api_mapping"

    def role_profile(self) -> dict[str, object]:
        return get_role_profile(self.agent_name)

    def declare_api_source(self, api_source_url: str) -> dict[str, object]:
        if "apifox" not in api_source_url.lower():
            raise ValueError("Agent 3 currently requires an Apifox URL as the API source.")
        return parse_apifox_url(api_source_url).to_declaration()

    def select_endpoints_from_index(
        self,
        test_cases: dict[str, Any],
        api_index: dict[str, Any],
        *,
        resource_id: str | None = None,
    ) -> list[dict[str, str]]:
        indexed_operations = [
            {
                "id": str(item.get("id", "")),
                "path": str(item.get("path", "")),
                "method": str(item.get("method", "")).upper(),
                "summary": str(item.get("api_name", "")),
                "description": str(item.get("description", "")),
                "module": str(item.get("module", "")),
            }
            for item in api_index.get("apis", [])
            if isinstance(item, dict)
        ]
        if resource_id:
            matched = [item for item in indexed_operations if item.get("id") == str(resource_id)]
            if matched:
                return [{"id": item["id"], "method": item["method"], "path": item["path"]} for item in matched]

        selected = []
        seen: set[tuple[str, str]] = set()
        for case in test_cases.get("cases", []):
            if not isinstance(case, dict):
                continue
            operation = self._select_operation(case, indexed_operations, allow_fallback=False)
            if not operation.get("path") or not operation.get("method"):
                continue
            key = (str(operation["method"]), str(operation["path"]))
            if key in seen:
                continue
            seen.add(key)
            selected.append(
                {
                    "id": str(operation.get("id", "")),
                    "method": str(operation["method"]),
                    "path": str(operation["path"]),
                }
            )
        if not selected and len(indexed_operations) == 1:
            only = indexed_operations[0]
            return [{"id": str(only.get("id", "")), "method": str(only.get("method", "")), "path": str(only.get("path", ""))}]
        return selected

    def run(self, test_cases: dict[str, Any], api_document: dict[str, Any]) -> dict[str, object]:
        paths = api_document.get("paths", {})
        operations = self._collect_operations(api_document)

        mappings = []
        for index, case in enumerate(test_cases["cases"], start=1):
            selected_operation = self._select_operation(case, operations, allow_fallback=True)
            payload = self._normalize_payload(selected_operation, case.get("payload", {}))
            mappings.append(
                {
                    "test_case_id": case["test_case_id"],
                    "automation_id": f"AUTO-CASE-00{index}",
                    "title": case.get("title", case["test_case_id"]),
                    "path": selected_operation["path"],
                    "method": selected_operation["method"],
                    "summary": selected_operation.get("summary", ""),
                    "description": selected_operation.get("description", ""),
                    "module": selected_operation.get("module", ""),
                    "headers": selected_operation.get("headers", []),
                    "query_params": selected_operation.get("query_params", []),
                    "path_params": selected_operation.get("path_params", []),
                    "request_body": selected_operation.get("request_body", {}),
                    "response_body": selected_operation.get("response_body", {}),
                    "auth_type": selected_operation.get("auth_type", "待确认"),
                    "interface_detail_status": selected_operation.get("detail_status", "待确认"),
                    "epic": "api_mapping",
                    "feature": "cart" if "CART" in str(case["test_case_id"]) else "api",
                    "story": case.get("title", case["test_case_id"]),
                    "payload": payload,
                    "expected_status_codes": case["expected_status_codes"],
                }
            )

        selected_interfaces = self._dedupe_operations(
            [self._selected_interface_from_mapping(mapping) for mapping in mappings]
        )
        first_mapping = mappings[0] if mappings else {"path": "/users", "method": "POST"}

        return {
            "api_catalog": {
                "service_name": api_document.get("info", {}).get("title", "Unknown Service"),
                "paths": list(paths.keys()),
                "selected_interfaces": selected_interfaces,
                "detail_source_policy": {
                    "knowledge_base_role": "locate candidate interfaces only",
                    "detail_fetch_scope": "only interfaces involved in this run",
                    "apifox_token_role": "fetch full interface details one by one before output",
                    "required_detail_fields": [
                        "headers",
                        "query_params",
                        "path_params",
                        "request_body",
                        "response_body",
                        "auth_type",
                        "description",
                    ],
                    "unknown_field_policy": "mark as 待确认",
                },
            },
            "endpoint_mapping": {
                "requirement_id": test_cases["requirement_id"],
                "mappings": mappings,
            },
            "request_schema": {
                "path": first_mapping["path"],
                "method": first_mapping["method"],
                "body_type": "application/json",
                "required_fields": self._infer_required_fields(first_mapping),
            },
            "dependency_graph": {
                "edges": [],
                "notes": [
                    "Agent 3 must locate candidate interfaces from knowledge base, then fetch and expand full details from Apifox before output."
                ],
            },
        }

    def _collect_operations(self, api_document: dict[str, Any]) -> list[dict[str, Any]]:
        paths = api_document.get("paths", {})
        operations: list[dict[str, Any]] = []
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                upper_method = str(method).upper()
                if upper_method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
                    continue
                operation = operation if isinstance(operation, dict) else {}
                parameters = self._expand_schema(
                    [
                        *self._list_or_empty(path_item.get("parameters")),
                        *self._list_or_empty(operation.get("parameters")),
                    ],
                    api_document,
                )
                request_body = self._expand_schema(operation.get("requestBody", {}), api_document)
                response_body = self._expand_schema(operation.get("responses", {}), api_document)
                security = operation.get("security", api_document.get("security", []))
                operations.append(
                    {
                        "path": path,
                        "method": upper_method,
                        "summary": str(operation.get("summary", "")),
                        "description": str(operation.get("description", "")),
                        "module": self._module_name(operation),
                        "headers": self._params_by_location(parameters, "header"),
                        "query_params": self._params_by_location(parameters, "query"),
                        "path_params": self._params_by_location(parameters, "path"),
                        "request_body": request_body if isinstance(request_body, dict) else {},
                        "response_body": response_body if isinstance(response_body, dict) else {},
                        "security": security,
                        "auth_type": self._auth_type(security, parameters),
                        "detail_status": self._detail_status(request_body, response_body, parameters),
                    }
                )
        return operations

    def _select_operation(
        self,
        case: dict[str, Any],
        operations: list[dict[str, Any]],
        *,
        allow_fallback: bool = True,
    ) -> dict[str, Any]:
        if not operations:
            return {
                "path": "/users",
                "method": "POST",
                "summary": "",
                "description": "",
                "module": "",
                "headers": [],
                "query_params": [],
                "path_params": [],
                "request_body": {},
                "response_body": {},
                "auth_type": "待确认",
                "detail_status": "待确认",
            }

        intent = str(case.get("related_api_intent", ""))
        case_text = " ".join(
            [
                str(case.get("test_case_id", "")),
                str(case.get("title", "")),
                intent,
            ]
        )
        rules = [
            (["checkout", "结算"], "POST", ["checkout", "结算"]),
            (["add_cart_item", "加入购物车"], "POST", ["cart/items", "加入购物车"]),
            (["list_cart_items", "列表", "查询"], "GET", ["cart/items", "查询购物车列表"]),
            (["update_cart_quantity", "数量"], "PUT", ["quantity", "修改购物车数量"]),
            (["select_all", "全选"], "PUT", ["select-all", "全选"]),
            (["select_cart_item", "勾选", "取消勾选"], "PUT", ["selected", "勾选"]),
            (["clear_invalid", "失效"], "DELETE", ["invalid-items", "清空失效"]),
            (["batch_delete", "批量删除"], "DELETE", ["cart/items", "批量删除"]),
            (["delete_cart_item", "删除单个"], "DELETE", ["cart/items/{id}", "删除购物车商品"]),
            (["create_order", "新增", "创建"], "POST", ["orders", "create", "新增", "创建"]),
        ]
        for case_keywords, method, operation_keywords in rules:
            if any(keyword in case_text for keyword in case_keywords):
                matched = self._find_operation(operations, method, operation_keywords)
                if matched:
                    return matched
        if allow_fallback:
            return operations[0]
        return {}

    def _find_operation(
        self,
        operations: list[dict[str, Any]],
        method: str,
        operation_keywords: list[str],
    ) -> dict[str, Any] | None:
        path_keywords = [keyword for keyword in operation_keywords if "/" in keyword or "{" in keyword]
        for operation in operations:
            if operation["method"] != method:
                continue
            if any(keyword in operation["path"] for keyword in path_keywords):
                return operation

        for operation in operations:
            if operation["method"] != method:
                continue
            operation_text = " ".join(
                [operation["path"], operation.get("summary", ""), operation.get("description", "")]
            )
            if any(keyword.lower() in operation_text.lower() for keyword in operation_keywords):
                return operation
        return None

    def _dedupe_operations(self, operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen = set()
        result = []
        for operation in operations:
            key = (operation["path"], operation["method"])
            if key in seen:
                continue
            seen.add(key)
            result.append(operation)
        return result

    def _infer_required_fields(self, mapping: dict[str, Any]) -> list[str]:
        schema = self._json_schema(mapping.get("request_body", {}))
        if isinstance(schema, dict):
            required = schema.get("required")
            if isinstance(required, list):
                return [str(field) for field in required]

        path = str(mapping.get("path", ""))
        if path.endswith("/cart/items"):
            return ["pet_id", "quantity"]
        if path.endswith("/quantity"):
            return ["quantity"]
        if path.endswith("/selected") or path.endswith("/select-all"):
            return ["selected"]
        return []

    def _normalize_payload(self, operation: dict[str, Any], payload: object) -> object:
        if not isinstance(payload, dict):
            return payload

        normalized = dict(payload)
        if operation["method"] == "POST" and operation["path"].endswith("/cart/items"):
            if "petId" in normalized and "pet_id" not in normalized:
                normalized["pet_id"] = normalized.pop("petId")
        if operation["method"] == "DELETE" and operation["path"].endswith("/cart/items"):
            if "cartItemIds" in normalized and "ids" not in normalized:
                normalized["ids"] = normalized.pop("cartItemIds")
        return normalized

    def _selected_interface_from_mapping(self, mapping: dict[str, Any]) -> dict[str, Any]:
        return {
            "path": mapping["path"],
            "method": mapping["method"],
            "summary": mapping.get("summary", ""),
            "description": mapping.get("description", ""),
            "module": mapping.get("module", ""),
            "headers": mapping.get("headers", []),
            "query_params": mapping.get("query_params", []),
            "path_params": mapping.get("path_params", []),
            "request_body": mapping.get("request_body", {}),
            "response_body": mapping.get("response_body", {}),
            "auth_type": mapping.get("auth_type", "待确认"),
            "interface_detail_status": mapping.get("interface_detail_status", "待确认"),
        }

    def _module_name(self, operation: dict[str, Any]) -> str:
        tags = operation.get("tags") or []
        if tags:
            return str(tags[0])
        return ""

    def _list_or_empty(self, value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    def _params_by_location(self, parameters: Any, location: str) -> list[dict[str, Any]]:
        if not isinstance(parameters, list):
            return []
        return [
            parameter
            for parameter in parameters
            if isinstance(parameter, dict) and parameter.get("in") == location
        ]

    def _json_schema(self, container: Any) -> Any:
        if not isinstance(container, dict):
            return None
        content = container.get("content")
        if not isinstance(content, dict):
            return None
        if "application/json" in content and isinstance(content["application/json"], dict):
            return content["application/json"].get("schema")
        for detail in content.values():
            if isinstance(detail, dict) and "schema" in detail:
                return detail.get("schema")
        return None

    def _expand_schema(
        self,
        value: Any,
        api_document: dict[str, Any],
        seen_refs: tuple[str, ...] = (),
        depth: int = 0,
    ) -> Any:
        if depth > 40:
            return {"resolution_note": "schema expansion stopped at depth limit"}
        if isinstance(value, list):
            return [self._expand_schema(item, api_document, seen_refs, depth + 1) for item in value]
        if not isinstance(value, dict):
            return value

        if "$ref" in value:
            ref = str(value["$ref"])
            if ref in seen_refs:
                return {
                    "schema_name": ref.rsplit("/", 1)[-1],
                    "resolution_note": "circular schema reference omitted",
                }
            resolved = self._resolve_ref(ref, api_document)
            expanded = self._expand_schema(resolved, api_document, (*seen_refs, ref), depth + 1)
            if isinstance(expanded, dict):
                expanded.setdefault("schema_name", ref.rsplit("/", 1)[-1])
                for key, subvalue in value.items():
                    if key != "$ref" and key not in expanded:
                        expanded[key] = self._expand_schema(subvalue, api_document, seen_refs, depth + 1)
            return expanded

        if "allOf" in value:
            return self._merge_all_of(value, api_document, seen_refs, depth)

        expanded: dict[str, Any] = {}
        for key, subvalue in value.items():
            if key in {"oneOf", "anyOf"} and isinstance(subvalue, list):
                expanded[key] = [
                    self._expand_schema(item, api_document, seen_refs, depth + 1) for item in subvalue
                ]
            else:
                expanded[key] = self._expand_schema(subvalue, api_document, seen_refs, depth + 1)
        return expanded

    def _merge_all_of(
        self,
        value: dict[str, Any],
        api_document: dict[str, Any],
        seen_refs: tuple[str, ...],
        depth: int,
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {key: copy.deepcopy(subvalue) for key, subvalue in value.items() if key != "allOf"}
        required: list[Any] = list(merged.get("required", []))
        properties: dict[str, Any] = dict(merged.get("properties", {}))
        for item in value.get("allOf", []):
            expanded = self._expand_schema(item, api_document, seen_refs, depth + 1)
            if not isinstance(expanded, dict):
                continue
            for key, subvalue in expanded.items():
                if key == "properties" and isinstance(subvalue, dict):
                    properties.update(subvalue)
                elif key == "required" and isinstance(subvalue, list):
                    for required_field in subvalue:
                        if required_field not in required:
                            required.append(required_field)
                elif key not in merged:
                    merged[key] = subvalue
        if properties:
            merged["properties"] = properties
        if required:
            merged["required"] = required
        return self._expand_schema(merged, api_document, seen_refs, depth + 1)

    def _resolve_ref(self, ref: str, api_document: dict[str, Any]) -> Any:
        if not ref.startswith("#/"):
            return {"unresolved_reference": ref}
        node: Any = api_document
        for raw_part in ref[2:].split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if not isinstance(node, dict) or part not in node:
                return {"unresolved_reference": ref}
            node = node[part]
        return copy.deepcopy(node)

    def _auth_type(self, security: Any, parameters: Any) -> str:
        if security:
            return "openapi_security"
        if self._params_by_location(parameters, "header"):
            return "header_context"
        return "待确认"

    def _detail_status(self, request_body: Any, response_body: Any, parameters: Any) -> str:
        if request_body or response_body or parameters:
            return "detail_fetched_from_apifox_openapi"
        return "待确认"
