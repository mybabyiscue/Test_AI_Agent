from __future__ import annotations

import json
from typing import Any


def render_api_source_request_markdown(payload: dict[str, Any]) -> str:
    source_url = payload.get("source_url") or payload.get("url") or ""
    lines = [
        "# API Source Request",
        "",
        f"- Platform: `{payload.get('platform', '')}`",
        f"- Project ID: `{payload.get('project_id', '')}`",
        f"- Source URL: `{source_url}`",
        f"- Detail Fetch Mode: `{payload.get('detail_fetch_mode', '')}`",
        "",
        "## Requested Endpoints",
        "",
    ]
    endpoints = payload.get("requested_endpoints", [])
    if not endpoints and payload.get("resource_type"):
        resource_id = payload.get("resource_id")
        if resource_id:
            endpoints = [{"method": "", "path": f"{payload.get('resource_type')}:{resource_id}"}]
        else:
            endpoints = [{"method": "", "path": str(payload.get("resource_type", ""))}]
    if endpoints:
        for endpoint in endpoints:
            lines.append(f"- `{endpoint.get('method', '')} {endpoint.get('path', '')}`")
    else:
        lines.append("- None")
    credential = payload.get("credential")
    if isinstance(credential, dict):
        lines.extend(
            [
                "",
                "## Credential",
                "",
                f"- Source: `{credential.get('source', '')}`",
                f"- Token: `{credential.get('token', '')}`",
            ]
        )
    return "\n".join(lines) + "\n"


def render_api_catalog_markdown(payload: dict[str, Any]) -> str:
    interfaces = payload.get("interfaces") or payload.get("selected_interfaces") or []
    title = payload.get("service_name") or payload.get("project_id") or "Unknown Service"
    lines = [
        "# API Catalog",
        "",
        f"- Title: `{title}`",
    ]
    if payload.get("platform"):
        lines.append(f"- Platform: `{payload.get('platform', '')}`")
    if payload.get("project_id"):
        lines.append(f"- Project ID: `{payload.get('project_id', '')}`")
    if payload.get("source_url"):
        lines.append(f"- Source URL: `{payload.get('source_url', '')}`")
    lines.extend(["", "## Interfaces", ""])
    if not interfaces:
        lines.append("- None")
        return "\n".join(lines) + "\n"

    for item in interfaces:
        lines.extend(
            [
                "## Interface",
                "",
                f"- Name: {item.get('interface_name') or item.get('summary', '')}",
                f"- Module/Group: {_format_group(item.get('module_or_group') or item.get('module', ''))}",
                f"- Method: `{item.get('request_method') or item.get('method', '')}`",
                f"- Path: `{item.get('request_path') or item.get('path', '')}`",
                f"- Auth Type: `{item.get('auth_type', '')}`",
                f"- Detail Status: `{item.get('interface_detail_status', '')}`",
                f"- Description: {item.get('interface_description') or item.get('description', '') or 'None'}",
                "",
                "### Request Headers",
                "",
                _render_parameter_list(item.get("request_headers") or item.get("headers")),
                "",
                "### Query Parameters",
                "",
                _render_parameter_list(item.get("query_params")),
                "",
                "### Path Parameters",
                "",
                _render_parameter_list(item.get("path_params")),
                "",
                "### Request Body",
                "",
                "```json",
                json.dumps(item.get("request_body", {}), ensure_ascii=False, indent=2),
                "```",
                "",
                "### Response Body",
                "",
                "```json",
                json.dumps(item.get("response_body", {}), ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def render_endpoint_mapping_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Endpoint Mapping",
        "",
        f"- Requirement ID: `{payload.get('requirement_id', '')}`",
        "",
        "## Mappings",
        "",
    ]
    mappings = payload.get("mappings", [])
    if not mappings:
        lines.append("- None")
        return "\n".join(lines) + "\n"

    for mapping in mappings:
        lines.extend(
            [
                "## Mapping",
                "",
                f"- Test Case ID: `{mapping.get('test_case_id', '')}`",
                f"- Title: {mapping.get('test_case_title') or mapping.get('title', '')}",
                f"- Status: `{mapping.get('mapping_status', '已映射')}`",
                f"- Interface Name: {mapping.get('interface_name') or mapping.get('summary', '')}",
                f"- Method: `{mapping.get('request_method') or mapping.get('method', '')}`",
                f"- Path: `{mapping.get('request_path') or mapping.get('path', '')}`",
                f"- Auth Type: `{mapping.get('auth_type', '')}`",
            ]
        )
        notes = mapping.get("notes") or mapping.get("reason")
        if isinstance(notes, list) and notes:
            lines.extend(["- Notes:"])
            lines.extend([f"  - {note}" for note in notes])
        elif isinstance(notes, str) and notes:
            lines.append(f"- Notes: {notes}")
        lines.append("")
    return "\n".join(lines)


def render_request_schema_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Request Schema", "", "## Interfaces", ""]
    interfaces = payload.get("interfaces", [])
    if not interfaces:
        lines.append("- None")
        return "\n".join(lines) + "\n"
    for item in interfaces:
        lines.extend(
            [
                "## Interface",
                "",
                f"- Method: `{item.get('request_method') or item.get('method', '')}`",
                f"- Path: `{item.get('request_path') or item.get('path', '')}`",
                "",
                "### Request Headers",
                "",
                _render_parameter_list(item.get("request_headers") or item.get("headers")),
                "",
                "### Query Parameters",
                "",
                _render_parameter_list(item.get("query_params")),
                "",
                "### Path Parameters",
                "",
                _render_parameter_list(item.get("path_params")),
                "",
                "### Request Body",
                "",
                "```json",
                json.dumps(item.get("request_body", {}), ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def render_dependency_graph_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Dependency Graph", "", "## Nodes", ""]
    nodes = payload.get("nodes", [])
    if nodes:
        for node in nodes:
            node_name = node.get("name") or f"{node.get('method', '')} {node.get('path', '')}".strip()
            lines.append(f"- `{node.get('id', '')}`: {node_name}")
    else:
        lines.append("- None")
    lines.extend(["", "## Edges", ""])
    edges = payload.get("edges", [])
    if edges:
        for edge in edges:
            lines.append(
                f"- `{edge.get('from', '')}` -> `{edge.get('to', '')}` ({edge.get('type', '')}): {edge.get('note', '')}"
            )
    else:
        lines.append("- None")
    unresolved = payload.get("unresolved_dependencies", [])
    lines.extend(["", "## Unresolved Dependencies", ""])
    if unresolved:
        for item in unresolved:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def render_database_catalog_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Database Catalog",
        "",
        f"- Knowledge Scope: `{payload.get('knowledge_scope', '')}`",
        f"- Table Count: `{payload.get('table_count', 0)}`",
        "",
        "## Tables",
        "",
    ]
    tables = payload.get("tables", [])
    if not isinstance(tables, list) or not tables:
        lines.append("- None")
        return "\n".join(lines) + "\n"

    for table in tables:
        if not isinstance(table, dict):
            continue
        lines.extend(
            [
                "## Table",
                "",
                f"- Database: `{table.get('db_name', '')}`",
                f"- Table: `{table.get('table_name', '')}`",
                f"- Comment: {table.get('table_comment', '') or 'None'}",
                f"- Source File: `{table.get('source_file', '')}`",
                "",
                "### Columns",
                "",
            ]
        )
        columns = table.get("columns", [])
        if isinstance(columns, list) and columns:
            for column in columns:
                if not isinstance(column, dict):
                    continue
                lines.append(
                    f"- `{column.get('column_name', '')}` `{column.get('column_type', '')}` "
                    f"nullable={column.get('is_nullable', '')} default={column.get('default_value', '')} "
                    f"key={column.get('column_key', '')}: {column.get('column_comment', '') or 'None'}"
                )
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def render_database_mapping_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Database Mapping",
        "",
        f"- Requirement ID: `{payload.get('requirement_id', '')}`",
        f"- Knowledge Scope: `{payload.get('knowledge_scope', '')}`",
        "",
        "## Case Mapping",
        "",
    ]
    mappings = payload.get("mappings", [])
    if not isinstance(mappings, list) or not mappings:
        lines.append("- None")
        return "\n".join(lines) + "\n"

    for mapping in mappings:
        if not isinstance(mapping, dict):
            continue
        lines.extend(
            [
                "## Mapping",
                "",
                f"- Test Case ID: `{mapping.get('test_case_id', '')}`",
                f"- Title: {mapping.get('title', '')}",
                f"- Intent: `{mapping.get('related_api_intent', '')}`",
                f"- Interface: `{mapping.get('interface_method', '')} {mapping.get('interface_path', '')}`",
                "",
                "### Matched Tables",
                "",
            ]
        )
        matched_tables = mapping.get("matched_tables", [])
        if isinstance(matched_tables, list) and matched_tables:
            for table in matched_tables:
                if not isinstance(table, dict):
                    continue
                lines.append(
                    f"- `{table.get('db_name', '')}.{table.get('table_name', '')}` "
                    f"({table.get('relationship', '')}, {table.get('usage', '')})"
                )
        else:
            lines.append("- None")

        lines.extend(["", "### Missing Tables", ""])
        missing_tables = mapping.get("missing_tables", [])
        if isinstance(missing_tables, list) and missing_tables:
            for table_name in missing_tables:
                lines.append(f"- `{table_name}`")
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def _render_parameter_list(parameters: Any) -> str:
    if not isinstance(parameters, list) or not parameters:
        return "- None"
    lines: list[str] = []
    for parameter in parameters:
        if not isinstance(parameter, dict):
            lines.append(f"- {parameter}")
            continue
        name = parameter.get("name", "")
        required = parameter.get("required")
        description = parameter.get("description", "") or "None"
        required_label = "required" if required else "optional"
        lines.append(f"- `{name}` ({required_label}): {description}")
    return "\n".join(lines)


def _format_group(value: Any) -> str:
    if isinstance(value, list):
        return " / ".join(str(item) for item in value) or "None"
    return str(value or "None")
