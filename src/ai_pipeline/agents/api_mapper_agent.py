from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from ..config import project_root
from ..platforms.apifox import parse_apifox_url
from .base_agent import BaseAgent


INTENT_FIELD_HINTS: dict[str, list[str]] = {
    "save_contact_way": ["next_auto_enable_time", "enable"],
    "save_acquisition_link": ["next_auto_enable_time", "enable"],
    "list_online_status": ["status", "source"],
    "change_online_status": ["status", "source"],
    "sync_org": ["next_auto_enable_time", "status"],
}

INTENT_PREFERRED_PATHS: dict[str, list[str]] = {
    "save_contact_way": ["/contact/way/save", "/groupcontact/way/save"],
    "save_acquisition_link": ["/acquisition/link/saveOrUpdate"],
    "list_online_status": ["/acquisition/user/online/list"],
    "change_online_status": ["/acquisition/user/online/change"],
    "sync_org": ["/cp/org/synchro", "/cp/org/synchro/{corpId}"],
}

# intent → 知识库表名匹配关键词组（每组是 AND 关系，组间是 OR 关系）
# 例如 ["wework", "user"] 表示表名必须同时包含 "wework" 和 "user"
INTENT_TABLE_KEYWORDS: dict[str, list[list[str]]] = {
    "save_contact_way": [["wework", "contact_way"], ["wework", "acquisition_rule"]],
    "save_acquisition_link": [["wework", "acquisition_link"], ["wework", "acquisition_rule"]],
    "list_online_status": [["wework", "user"]],
    "change_online_status": [["wework", "user"]],
    "sync_org": [["wework", "user"], ["wework", "acquisition_rule"]],
}

# 接口路径 → 知识库表名匹配关键词组
PATH_TABLE_KEYWORDS: list[tuple[str, list[list[str]]]] = [
    ("contact/way", [["wework", "contact_way"]]),
    ("acquisition/link", [["wework", "acquisition_link"]]),
    ("online/list", [["wework", "user"]]),
    ("online/change", [["wework", "user"]]),
]


class ApiMapperAgent(BaseAgent):
    agent_name = "api_mapper_agent"
    stage_name = "api_mapping"

    def __init__(self, knowledge_root: Path | None = None, default_database_scope: str = "saas") -> None:
        self.knowledge_root = knowledge_root or project_root() / "knowledge_base"
        self.default_database_scope = default_database_scope

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
        if not selected:
            preferred = [
                item
                for item in indexed_operations
                if any(
                    keyword in item.get("path", "")
                    for keyword in [
                        "/contact/way/save",
                        "/acquisition/link/saveOrUpdate",
                        "/acquisition/user/online/list",
                        "/acquisition/user/online/change",
                    ]
                )
            ]
            fallback_items = preferred[:6] or indexed_operations[:6]
            return [
                {
                    "id": str(item.get("id", "")),
                    "method": str(item.get("method", "")),
                    "path": str(item.get("path", "")),
                }
                for item in fallback_items
            ]
        return selected

    def run(
        self,
        test_cases: dict[str, Any],
        api_document: dict[str, Any],
        *,
        database_scope: str | None = None,
    ) -> dict[str, object]:
        paths = api_document.get("paths", {})
        operations = self._collect_operations(api_document)

        mappings = []
        for index, case in enumerate(test_cases["cases"], start=1):
            selected_operation = self._select_operation(case, operations, allow_fallback=True)
            payload = self._normalize_payload(selected_operation, case.get("payload", {}))
            mappings.append(
                {
                    "test_case_id": case["test_case_id"],
                    "automation_id": f"AUTO-CASE-{index:03d}",
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
                    "auth_type": selected_operation.get("auth_type", "pending_confirmation"),
                    "interface_detail_status": selected_operation.get("detail_status", "pending_confirmation"),
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
        request_schema = self._build_request_schema_output(selected_interfaces)
        resolved_database_scope = database_scope or self.default_database_scope
        database_context = self._build_database_context(
            test_cases=test_cases,
            mappings=mappings,
            database_scope=resolved_database_scope,
        )

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
                    "unknown_field_policy": "mark as pending_confirmation",
                },
            },
            "endpoint_mapping": {
                "requirement_id": test_cases["requirement_id"],
                "mappings": mappings,
            },
            "request_schema": request_schema
            if request_schema["interfaces"]
            else {
                "path": first_mapping["path"],
                "method": first_mapping["method"],
                "body_type": "application/json",
                "required_fields": self._infer_required_fields(first_mapping),
                "interfaces": [],
            },
            "dependency_graph": {
                "edges": [],
                "notes": [
                    "Agent 3 must locate candidate interfaces from knowledge base, then fetch and expand full details from Apifox before output."
                ],
            },
            "database_catalog": database_context["database_catalog"],
            "database_mapping": database_context["database_mapping"],
            "missing_database_report": database_context["missing_database_report"],
        }

    def _build_database_context(
        self,
        *,
        test_cases: dict[str, Any],
        mappings: list[dict[str, Any]],
        database_scope: str,
    ) -> dict[str, object]:
        table_catalog = self._load_database_table_catalog(database_scope)
        mapping_by_case_id = {mapping["test_case_id"]: mapping for mapping in mappings if isinstance(mapping, dict)}
        matched_tables: dict[tuple[str, str], dict[str, Any]] = {}
        database_mappings: list[dict[str, Any]] = []
        missing_tables: set[str] = set()
        missing_fields: set[str] = set()
        unresolved_cases: list[dict[str, Any]] = []

        for case in test_cases.get("cases", []):
            if not isinstance(case, dict):
                continue
            table_names = self._expected_tables_for_case(case, mapping_by_case_id.get(str(case.get("test_case_id", "")), {}), table_catalog)
            field_hints = self._expected_fields_for_case(case)
            case_matches: list[dict[str, Any]] = []
            case_missing_tables: list[str] = []
            case_missing_fields: list[str] = []
            for table_name in table_names:
                table_info = table_catalog.get(table_name.lower())
                if table_info is None:
                    missing_tables.add(table_name)
                    case_missing_tables.append(table_name)
                    continue
                matched_fields, missing_for_table = self._match_fields_on_table(table_info, field_hints)
                case_missing_fields.extend(missing_for_table)
                matched_tables[(table_info["db_name"], table_info["table_name"])] = table_info
                case_matches.append(
                    {
                        "db_name": table_info["db_name"],
                        "table_name": table_info["table_name"],
                        "table_comment": table_info.get("table_comment", ""),
                        "source_file": table_info["source_file"],
                        "relationship": self._relationship_for_table(table_info["table_name"], case),
                        "usage": self._usage_for_table(table_info["table_name"], case),
                        "matched_columns": matched_fields,
                        "missing_columns": missing_for_table,
                    }
                )
            for field_name in case_missing_fields:
                missing_fields.add(field_name)
            case_mapping = {
                "test_case_id": str(case.get("test_case_id", "")),
                "title": str(case.get("title", "")),
                "related_api_intent": str(case.get("related_api_intent", "")),
                "interface_path": str(mapping_by_case_id.get(str(case.get("test_case_id", "")), {}).get("path", "")),
                "interface_method": str(mapping_by_case_id.get(str(case.get("test_case_id", "")), {}).get("method", "")),
                "matched_tables": case_matches,
                "missing_tables": case_missing_tables,
            }
            database_mappings.append(case_mapping)
            if not case_matches or case_missing_tables or case_missing_fields:
                unresolved_cases.append(
                    {
                        "test_case_id": case_mapping["test_case_id"],
                        "title": case_mapping["title"],
                        "missing_tables": case_missing_tables,
                        "missing_fields": sorted(set(case_missing_fields)),
                    }
                )

        catalog_tables = [self._serialize_table_for_output(table) for table in matched_tables.values()]
        catalog_tables.sort(key=lambda item: (str(item["db_name"]), str(item["table_name"])))
        database_catalog = {
            "knowledge_scope": database_scope,
            "knowledge_root": str(self.knowledge_root),
            "table_count": len(catalog_tables),
            "tables": catalog_tables,
        }
        database_mapping = {
            "requirement_id": test_cases.get("requirement_id", ""),
            "knowledge_scope": database_scope,
            "mappings": database_mappings,
            "summary": {
                "case_count": len(database_mappings),
                "matched_table_count": len(catalog_tables),
                "missing_tables": sorted(missing_tables),
                "missing_fields": sorted(missing_fields),
                "unresolved_case_count": len(unresolved_cases),
            },
            "unresolved_cases": unresolved_cases,
        }
        return {
            "database_catalog": database_catalog,
            "database_mapping": database_mapping,
            "missing_database_report": self._render_missing_database_report(database_mapping),
        }

    def _load_database_table_catalog(self, database_scope: str) -> dict[str, dict[str, Any]]:
        scope_dir = self.knowledge_root / database_scope / "database"
        if not scope_dir.exists():
            return {}

        table_catalog: dict[str, dict[str, Any]] = {}
        for db_file in sorted(scope_dir.glob("*.json")):
            if db_file.name.lower() == "readme.json":
                continue
            try:
                payload = json.loads(db_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            db_name = str(payload.get("db_name") or db_file.stem)
            for table in payload.get("tables", []):
                if not isinstance(table, dict):
                    continue
                table_name = str(table.get("table_name", "")).strip()
                if not table_name:
                    continue
                columns = table.get("columns", [])
                table_catalog[table_name.lower()] = {
                    "system": database_scope,
                    "db_name": db_name,
                    "source_file": str(db_file),
                    "table_name": table_name,
                    "table_comment": str(table.get("table_comment", "")),
                    "columns": columns if isinstance(columns, list) else [],
                }
        return table_catalog

    def _expected_tables_for_case(
        self,
        case: dict[str, Any],
        mapping: dict[str, Any],
        table_catalog: dict[str, dict[str, Any]],
    ) -> list[str]:
        """根据 intent 和接口路径，从知识库中动态匹配相关表名。

        使用 AND 关系的关键词组：每组内所有词都必须匹配（表名或表注释），
        组间是 OR 关系（匹配任一组即命中）。
        """
        keyword_groups: list[list[str]] = []
        intent = str(case.get("related_api_intent", ""))
        keyword_groups.extend(INTENT_TABLE_KEYWORDS.get(intent, []))

        mapping_path = str(mapping.get("path", ""))
        for path_keyword, path_kw_groups in PATH_TABLE_KEYWORDS:
            if path_keyword in mapping_path:
                keyword_groups.extend(path_kw_groups)

        # 如果没有预定义的关键词，自动从接口路径提取
        if not keyword_groups and mapping_path:
            auto_keywords = self._extract_keywords_from_path(mapping_path)
            if auto_keywords:
                keyword_groups.append(auto_keywords)

        if not keyword_groups:
            return []

        matched: list[str] = []
        seen: set[str] = set()
        for table_name_lower, table_info in table_catalog.items():
            table_name = str(table_info.get("table_name", ""))
            table_comment = str(table_info.get("table_comment", "")).lower()
            searchable = f"{table_name_lower} {table_comment}"
            for group in keyword_groups:
                if all(kw.lower() in searchable for kw in group):
                    if table_name not in seen:
                        seen.add(table_name)
                        matched.append(table_name)
                    break
        return matched

    def _extract_keywords_from_path(self, path: str) -> list[str]:
        """从接口路径自动提取关键词用于匹配表名。

        例如: /acquisition/user/online/change -> ["acquisition", "user"]
        """
        # 移除开头的斜杠和路径参数
        clean_path = path.strip("/")
        # 移除路径参数如 {id}
        clean_path = re.sub(r"\{[^}]+\}", "", clean_path)
        # 分割路径
        parts = [p for p in clean_path.split("/") if p]

        # 过滤掉常见的动词和无意义的词
        stop_words = {
            "api", "v1", "v2", "save", "update", "delete", "get", "list",
            "add", "remove", "change", "query", "select", "create", "edit",
            "batch", "import", "export", "sync", "check", "verify",
        }
        keywords = [p for p in parts if p.lower() not in stop_words and len(p) > 2]

        # 只返回前2个关键词，避免匹配太宽泛
        return keywords[:2] if keywords else []

    def _expected_fields_for_case(self, case: dict[str, Any]) -> list[str]:
        field_hints = []
        intent = str(case.get("related_api_intent", ""))
        field_hints.extend(INTENT_FIELD_HINTS.get(intent, []))
        payload = case.get("payload", {})
        if isinstance(payload, dict):
            field_hints.extend(str(key) for key in payload)
        return self._unique_preserve(field_hints)

    def _match_fields_on_table(
        self,
        table_info: dict[str, Any],
        field_hints: list[str],
    ) -> tuple[list[dict[str, Any]], list[str]]:
        columns = table_info.get("columns", [])
        normalized_columns = {
            self._normalize_identifier(str(column.get("column_name", ""))): column
            for column in columns
            if isinstance(column, dict)
        }
        matched = []
        missing = []
        for field_name in field_hints:
            normalized_field = self._normalize_identifier(field_name)
            column = normalized_columns.get(normalized_field)
            if column is None:
                missing.append(field_name)
                continue
            matched.append(
                {
                    "column_name": str(column.get("column_name", "")),
                    "column_type": str(column.get("column_type", "")),
                    "column_comment": str(column.get("column_comment", "")),
                }
            )
        return matched, self._unique_preserve(missing)

    def _serialize_table_for_output(self, table_info: dict[str, Any]) -> dict[str, Any]:
        return {
            "system": table_info["system"],
            "db_name": table_info["db_name"],
            "table_name": table_info["table_name"],
            "table_comment": table_info.get("table_comment", ""),
            "source_file": table_info["source_file"],
            "columns": table_info.get("columns", []),
        }

    def _relationship_for_table(self, table_name: str, case: dict[str, Any]) -> str:
        intent = str(case.get("related_api_intent", ""))
        if intent in {"save_contact_way", "save_acquisition_link"}:
            return "write_and_verify"
        if intent in {"list_online_status", "change_online_status"}:
            return "status_query_or_assert"
        if intent == "sync_org":
            return "scheduler_or_followup_assert"
        return "candidate"

    def _usage_for_table(self, table_name: str, case: dict[str, Any]) -> str:
        intent = str(case.get("related_api_intent", ""))
        if table_name.endswith("_log"):
            return "verify_operation_log"
        if "status" in table_name and intent in {"list_online_status", "change_online_status", "sync_org"}:
            return "verify_current_online_state"
        if "config" in table_name or "contact_way" in table_name or "link" in table_name:
            return "verify_persisted_configuration"
        return "candidate_context"

    def _render_missing_database_report(self, database_mapping: dict[str, Any]) -> str:
        summary = database_mapping.get("summary", {})
        lines = [
            "# Missing Database Report",
            "",
            f"- Knowledge Scope: `{database_mapping.get('knowledge_scope', '')}`",
            f"- Case Count: `{summary.get('case_count', 0)}`",
            f"- Matched Table Count: `{summary.get('matched_table_count', 0)}`",
            "",
            "## Missing Tables",
            "",
        ]
        missing_tables = summary.get("missing_tables", [])
        if isinstance(missing_tables, list) and missing_tables:
            lines.extend(f"- `{item}`" for item in missing_tables)
        else:
            lines.append("- None")

        lines.extend(["", "## Missing Fields", ""])
        missing_fields = summary.get("missing_fields", [])
        if isinstance(missing_fields, list) and missing_fields:
            lines.extend(f"- `{item}`" for item in missing_fields)
        else:
            lines.append("- None")

        lines.extend(["", "## Unresolved Cases", ""])
        unresolved_cases = database_mapping.get("unresolved_cases", [])
        if isinstance(unresolved_cases, list) and unresolved_cases:
            for item in unresolved_cases:
                if not isinstance(item, dict):
                    continue
                lines.append(f"- `{item.get('test_case_id', '')}` {item.get('title', '')}")
                missing_table_items = item.get("missing_tables", [])
                if missing_table_items:
                    lines.append(f"  - missing tables: {', '.join(str(value) for value in missing_table_items)}")
                missing_field_items = item.get("missing_fields", [])
                if missing_field_items:
                    lines.append(f"  - missing fields: {', '.join(str(value) for value in missing_field_items)}")
        else:
            lines.append("- None")
        return "\n".join(lines) + "\n"

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
                "auth_type": "pending_confirmation",
                "detail_status": "pending_confirmation",
            }

        intent = str(case.get("related_api_intent", ""))
        preferred_paths = INTENT_PREFERRED_PATHS.get(intent, [])
        preferred_match = self._match_preferred_path(operations, preferred_paths)
        if preferred_match:
            return preferred_match

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
            (["list_cart_items", "购物车列表", "查询购物车"], "GET", ["cart/items", "查询购物车"]),
            (["update_cart_quantity", "数量"], "PUT", ["quantity", "修改购物车数量"]),
            (["select_all", "select_all_cart_items", "全选"], "PUT", ["select-all", "全选"]),
            (["select_cart_item", "勾选", "取消勾选"], "PUT", ["selected", "勾选"]),
            (["clear_invalid", "clear_invalid_cart_items", "失效"], "DELETE", ["invalid-items", "清空失效"]),
            (["batch_delete", "batch_delete_cart_items", "批量删除"], "DELETE", ["cart/items", "批量删除"]),
            (["delete_cart_item", "删除单个"], "DELETE", ["cart/items/{id}", "删除购物车商品"]),
            (["create_order", "新增", "创建"], "POST", ["orders", "create", "新增", "创建"]),
            (["save_contact_way"], "POST", ["contact/way", "save"]),
            (["save_acquisition_link"], "POST", ["acquisition/link", "save", "update"]),
            (["list_online_status"], "GET", ["online/list"]),
            (["change_online_status"], "POST", ["online/change"]),
            (["sync_org"], "POST", ["sync", "org"]),
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

    def _match_preferred_path(
        self,
        operations: list[dict[str, Any]],
        preferred_paths: list[str],
    ) -> dict[str, Any] | None:
        if not preferred_paths:
            return None
        for preferred_path in preferred_paths:
            for operation in operations:
                if operation.get("path") == preferred_path:
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
            "auth_type": mapping.get("auth_type", "pending_confirmation"),
            "interface_detail_status": mapping.get("interface_detail_status", "pending_confirmation"),
        }

    def _build_request_schema_output(self, selected_interfaces: list[dict[str, Any]]) -> dict[str, Any]:
        interfaces: list[dict[str, Any]] = []
        for item in selected_interfaces:
            schema_entry = dict(item)
            schema_entry["body_type"] = self._body_type(schema_entry.get("request_body", {}))
            schema_entry["required_fields"] = self._infer_required_fields(
                {"request_body": schema_entry.get("request_body", {})}
            )
            interfaces.append(schema_entry)

        if interfaces:
            first_interface = interfaces[0]
            return {
                "path": first_interface.get("path", ""),
                "method": first_interface.get("method", ""),
                "body_type": first_interface.get("body_type", "application/json"),
                "required_fields": first_interface.get("required_fields", []),
                "interfaces": interfaces,
            }
        return {
            "path": "",
            "method": "",
            "body_type": "application/json",
            "required_fields": [],
            "interfaces": [],
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

    def _body_type(self, container: Any) -> str:
        if not isinstance(container, dict):
            return "application/json"
        content = container.get("content")
        if not isinstance(content, dict) or not content:
            return "application/json"
        if "application/json" in content:
            return "application/json"
        first_key = next(iter(content.keys()), None)
        return str(first_key or "application/json")

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
        return "pending_confirmation"

    def _detail_status(self, request_body: Any, response_body: Any, parameters: Any) -> str:
        if request_body or response_body or parameters:
            return "detail_fetched_from_apifox_openapi"
        return "pending_confirmation"

    def _normalize_identifier(self, value: str) -> str:
        return "".join(char.lower() for char in value if char.isalnum())

    def _unique_preserve(self, items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            normalized = str(item).strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result
