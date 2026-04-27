from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(r"E:\xjcode\Test_AI_Agent")
PROJECTS = [
    ("silkroad", "776242", "丝路"),
    ("saas", "4152663", "SAAS / 享佳云 / 鲨域"),
    ("callcenter", "460082", "呼叫中心"),
]
CHUNK_SIZE = 500


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8-sig", newline="\n")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def schema_label(schema: Any) -> str:
    if isinstance(schema, dict):
        if "$ref" in schema:
            return schema["$ref"]
        if schema.get("type"):
            return str(schema["type"])
    return ""


def param_table(params: list[dict[str, Any]] | None) -> str:
    if not params:
        return "无"
    lines = ["| 名称 | 位置 | 必填 | 类型 | 说明 | 示例 |", "|---|---|---|---|---|---|"]
    for param in params:
        if not isinstance(param, dict):
            continue
        schema = param.get("schema") or {}
        lines.append(
            f"| {cell(param.get('name'))} | {cell(param.get('in'))} | {param.get('required', False)} | "
            f"{cell(schema.get('type'))} | {cell(param.get('description'))} | {cell(param.get('example'))} |"
        )
    return "\n".join(lines)


def headers_table(headers: Any) -> str:
    if not headers:
        return "无"
    if isinstance(headers, dict):
        return param_table(list(headers.values()))
    if isinstance(headers, list):
        return param_table(headers)
    return "无"


def request_body_summary(body: dict[str, Any]) -> str:
    if not body:
        return "无"
    content = body.get("content") if isinstance(body, dict) else None
    lines: list[str] = []
    if isinstance(content, dict):
        for media_type, detail in content.items():
            schema = detail.get("schema", {}) if isinstance(detail, dict) else {}
            lines.append(f"- Content-Type：`{media_type}`")
            lines.append(f"- Schema：`{schema_label(schema) or 'inline'}`")
            if isinstance(schema, dict) and "$ref" not in schema:
                lines.append("```json")
                lines.append(json.dumps(schema, ensure_ascii=False, indent=2))
                lines.append("```")
    else:
        lines.append("```json")
        lines.append(json.dumps(body, ensure_ascii=False, indent=2))
        lines.append("```")
    return "\n".join(lines) if lines else "无"


def response_summary(responses: dict[str, Any]) -> str:
    if not responses:
        return "无"
    lines: list[str] = []
    for status, response in responses.items():
        lines.append(f"#### HTTP {status}")
        if not isinstance(response, dict):
            lines.append(f"- 响应说明：{cell(response)}")
            continue
        if response.get("description"):
            lines.append(f"- 说明：{response.get('description')}")
        content = response.get("content") or {}
        if not content:
            lines.append("- 响应体：无")
            continue
        for media_type, detail in content.items():
            schema = detail.get("schema", {}) if isinstance(detail, dict) else {}
            lines.append(f"- Content-Type：`{media_type}`")
            lines.append(f"- Schema：`{schema_label(schema) or 'inline'}`")
    return "\n".join(lines)


def schema_fields_for_ref(components: dict[str, Any], ref: str) -> str:
    if not ref or not ref.startswith("#/components/schemas/"):
        return "未使用 components schema 或无法展开。"
    schema_name = ref.split("/")[-1]
    schema = (components.get("schemas") or {}).get(schema_name)
    if not schema:
        return f"未在 components.schemas 中找到 `{schema_name}`。"
    properties = schema.get("properties") or {}
    required = set(schema.get("required") or [])
    if not properties:
        return f"`{schema_name}` 未定义 properties。"
    lines = [
        f"Schema：`{schema_name}`",
        "",
        "| 字段 | 必填 | 类型 | 格式 | 说明 |",
        "|---|---|---|---|---|",
    ]
    for field_name, field_schema in properties.items():
        if not isinstance(field_schema, dict):
            continue
        lines.append(
            f"| {cell(field_name)} | {field_name in required} | {cell(field_schema.get('type'))} | "
            f"{cell(field_schema.get('format'))} | {cell(field_schema.get('description'))} |"
        )
    return "\n".join(lines)


def first_request_ref(api: dict[str, Any]) -> str:
    try:
        return (
            api.get("request_body", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
            .get("$ref", "")
        )
    except AttributeError:
        return ""


def response_refs(api: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for response in (api.get("response_body") or {}).values():
        try:
            ref = response.get("content", {}).get("application/json", {}).get("schema", {}).get("$ref", "")
        except AttributeError:
            ref = ""
        if ref:
            refs.append(ref)
    return refs


def render_chunk(
    *,
    system: str,
    project_id: str,
    display_name: str,
    part: int,
    total: int,
    start_index: int,
    apis: list[dict[str, Any]],
    all_count: int,
    components: dict[str, Any],
) -> str:
    lines: list[str] = [
        f"# {display_name} Apifox 项目 {project_id} 接口明细 Part {part:03d}",
        "",
        "## 文件说明",
        "",
        f"- 文件名称：`apifox_project_{project_id}_part_{part:03d}.md`",
        "- 文件作用：按每 500 条接口拆分展示接口明细，便于人工查看和后续 Agent 检索。",
        "- 文件主要内容：接口基础信息、请求头、Query 参数、Path 参数、请求体、请求体字段、响应体、响应字段和缺失项。",
        "- 所属阶段：接口获取 Agent 接口文档同步阶段。",
        "- 查看方式：使用 VS Code、Typora 或 Markdown Preview 打开。",
        "",
        "## 本文件范围",
        "",
        f"- 系统：`{system}`（{display_name}）",
        f"- Apifox 项目：`{project_id}`",
        f"- 接口范围：{start_index} - {start_index + len(apis) - 1} / {all_count}",
        f"- 当前分片：{part} / {total}",
        "",
    ]

    for offset, api in enumerate(apis, start=start_index):
        method = api.get("method", "")
        path = api.get("path", "")
        title = api.get("api_name") or f"{method} {path}"
        lines.extend(
            [
                f"## {offset}. {method} {path}",
                "",
                f"- 接口名称：{title}",
                f"- 所属模块：{api.get('module', '')}",
                f"- 目录路径：`{json.dumps(api.get('folder_path', []), ensure_ascii=False)}`",
                f"- 接口说明：{api.get('description') or '无'}",
                f"- 鉴权方式：{api.get('auth_type') or '未在文档中显式标注'}",
                f"- 缺失项：{', '.join(api.get('missing_fields', [])) or '无'}",
                "",
                "### 请求头",
                headers_table(api.get("headers")),
                "",
                "### Query 参数",
                param_table(api.get("query_params") or []),
                "",
                "### Path 参数",
                param_table(api.get("path_params") or []),
                "",
                "### 请求体",
                request_body_summary(api.get("request_body") or {}),
            ]
        )

        req_ref = first_request_ref(api)
        if req_ref:
            lines.extend(["", "### 请求体字段", schema_fields_for_ref(components, req_ref)])

        lines.extend(["", "### 响应体", response_summary(api.get("response_body") or {})])
        for ref in response_refs(api)[:3]:
            lines.extend(["", "### 响应字段", schema_fields_for_ref(components, ref)])
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    summary: list[dict[str, Any]] = []
    for system, project_id, display_name in PROJECTS:
        api_file = ROOT / "knowledge_base" / system / "apis" / f"apifox_project_{project_id}.json"
        data = json.loads(api_file.read_text(encoding="utf-8-sig"))
        apis = data.get("apis", [])
        components = data.get("components", {})
        chunk_dir = ROOT / "knowledge_base" / system / "apis" / f"apifox_project_{project_id}_chunks"
        chunk_dir.mkdir(parents=True, exist_ok=True)
        for old in chunk_dir.glob("*.md"):
            old.unlink()

        chunk_count = max(1, math.ceil(len(apis) / CHUNK_SIZE))
        for idx in range(chunk_count):
            chunk = apis[idx * CHUNK_SIZE : (idx + 1) * CHUNK_SIZE]
            part = idx + 1
            content = render_chunk(
                system=system,
                project_id=project_id,
                display_name=display_name,
                part=part,
                total=chunk_count,
                start_index=idx * CHUNK_SIZE + 1,
                apis=chunk,
                all_count=len(apis),
                components=components,
            )
            write_text(chunk_dir / f"apifox_project_{project_id}_part_{part:03d}.md", content)

        summary.append(
            {
                "system": system,
                "display_name": display_name,
                "project_id": project_id,
                "api_count": len(apis),
                "chunk_size": CHUNK_SIZE,
                "chunk_count": chunk_count,
                "chunk_dir": str(chunk_dir),
            }
        )

    report_dir = ROOT / "knowledge_base" / "sync_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_json = report_dir / f"{timestamp}_api_chunks_regenerated_report.json"
    report_md = report_dir / f"{timestamp}_api_chunks_regenerated_report.md"
    write_json(
        report_json,
        {
            "file_info": {
                "file_name": report_json.name,
                "purpose": "记录本次接口 chunks 文档重生成结果。",
                "main_contents": "包含重生成的接口库、每 500 条拆分目录、接口数量和文档数量。",
                "stage": "接口获取 Agent 接口文档同步阶段",
                "view_method": "使用 JSON 查看器打开。",
            },
            "finished_at": datetime.now().astimezone().isoformat(),
            "chunk_size": CHUNK_SIZE,
            "projects": summary,
        },
    )
    md_lines = [
        "# 接口 chunks 文档重生成报告",
        "",
        "## 文件说明",
        "",
        "- 文件名称：接口 chunks 文档重生成报告",
        "- 文件作用：记录本次修复乱码并补充请求/响应详情后的 chunks 文档生成结果。",
        "- 文件主要内容：系统、Apifox 项目、接口数量、拆分文档数量和输出目录。",
        "- 所属阶段：接口获取 Agent 接口文档同步阶段。",
        "- 查看方式：使用 Markdown 编辑器打开。",
        "",
        "## 生成结果",
        "",
        "| 系统 | Apifox 项目 | 接口数 | 拆分文档数 | 输出目录 |",
        "|---|---|---:|---:|---|",
    ]
    for item in summary:
        md_lines.append(
            f"| {item['display_name']} | {item['project_id']} | {item['api_count']} | "
            f"{item['chunk_count']} | `{item['chunk_dir']}` |"
        )
    write_text(report_md, "\n".join(md_lines))
    print(json.dumps({"projects": summary, "report": str(report_md)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
