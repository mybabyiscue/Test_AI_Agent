from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import pymysql

from .config import project_root
from .credentials import CredentialNotFoundError, EnvCredentialProvider
from .platforms.apifox import ApifoxClient


BASIC_API_INDEX_SYNC_MODE = "basic_api_index"
BASIC_API_INDEX_DETAIL_FETCH_POLICY = (
    "接口请求头、请求参数、请求体、响应体、示例和 schema 不保存在接口主索引中，"
    "只能由 Agent3 在处理具体接口时，针对本次涉及的接口一对一从 Apifox、接口文档或代码实现中按需获取，"
    "不允许在知识库同步阶段全量拉取或保存所有接口详情。"
)


def sync_all_knowledge() -> dict[str, Any]:
    return KnowledgeSyncer.default().sync_all()


class KnowledgeSyncer:
    def __init__(
        self,
        *,
        knowledge_root: Path,
        sources_config_path: Path,
        credentials_file: Path,
    ) -> None:
        self.knowledge_root = knowledge_root
        self.sources_config_path = sources_config_path
        self.credential_provider = EnvCredentialProvider(credentials_file=credentials_file)

    @classmethod
    def default(cls) -> "KnowledgeSyncer":
        root = project_root()
        return cls(
            knowledge_root=root / "knowledge_base",
            sources_config_path=root / "config" / "knowledge_sources.example.json",
            credentials_file=root / "config" / "credentials.local.json",
        )

    def sync_all(self, *, sync_databases: bool = True, sync_apis: bool = True) -> dict[str, Any]:
        started_at = _now_iso()
        sources = json.loads(self.sources_config_path.read_text(encoding="utf-8-sig"))
        report: dict[str, Any] = {
            "file_info": {
                "file_name": "initial_sync_report.json",
                "purpose": "记录本次数据库结构与接口文档全量初始化同步结果。",
                "main_contents": "包含成功同步的数据库、成功同步的接口项目、生成文件、失败对象、失败原因和后续增量更新说明。",
                "stage": "接口获取 Agent 知识库同步阶段",
                "view_method": "使用文本编辑器或 JSON 查看器打开，也可以通过 Python/脚本读取。",
            },
            "sync_type": "initial_full_sync",
            "started_at": started_at,
            "finished_at": None,
            "summary": {
                "successful_databases": 0,
                "failed_databases": 0,
                "successful_api_projects": 0,
                "failed_api_projects": 0,
                "generated_files": 0,
            },
            "successful_databases": [],
            "failed_databases": [],
            "successful_api_projects": [],
            "failed_api_projects": [],
            "generated_files": [],
            "incremental_update_usage": {
                "by_system": "后续可指定 system，例如 silkroad、shark、saas、callcenter。",
                "by_database": "后续可指定 system + db_name，只更新某一个库的结构文件。",
                "by_apifox_project": "后续可指定 system + project_id，只更新某一个 Apifox 项目接口文件。",
            },
        }

        for system, config in sources.get("systems", {}).items():
            if sync_databases:
                self._sync_system_databases(system, config, report)
            if sync_apis:
                self._sync_system_apis(system, config, report)

        report["finished_at"] = _now_iso()
        report["summary"]["generated_files"] = len(report["generated_files"])
        self._write_sync_report(report)
        return report

    def _sync_system_databases(self, system: str, config: dict[str, Any], report: dict[str, Any]) -> None:
        database_config = config.get("databases")
        if not database_config:
            return

        profile = database_config.get("profile", system)
        try:
            credential = self.credential_provider.get_database(profile)
        except CredentialNotFoundError as exc:
            for db_name in database_config.get("schemas", []):
                self._record_failed_database(report, system, db_name, str(exc))
            return

        for db_name in database_config.get("schemas", []):
            try:
                payload = collect_mysql_schema(system=system, db_name=db_name, credential=credential)
                path = self.knowledge_root / system / "database" / f"{db_name}.json"
                self._write_json(path, payload)
                report["successful_databases"].append(
                    {
                        "system": system,
                        "db_name": db_name,
                        "file": str(path),
                        "table_count": len(payload["tables"]),
                    }
                )
                report["generated_files"].append(_file_record(path, "接口获取 Agent 数据库结构同步阶段"))
                report["summary"]["successful_databases"] += 1
            except Exception as exc:  # noqa: BLE001 - report each source without leaking secrets.
                self._record_failed_database(report, system, db_name, _safe_error(exc))

    def _sync_system_apis(self, system: str, config: dict[str, Any], report: dict[str, Any]) -> None:
        for api_config in config.get("apis", []) or []:
            if api_config.get("platform") != "apifox":
                continue

            project_id = str(api_config["project_id"])
            source_url = str(api_config["url"])
            credential_profile = str(api_config.get("credential_profile", "default"))
            try:
                credential = self.credential_provider.get("apifox", profile=credential_profile)
                payload = self._fetch_apifox_basic_index(
                    system=system,
                    project_id=project_id,
                    source_url=source_url,
                    credential=credential,
                )
                path = self.knowledge_root / system / "apis" / f"apifox_project_{project_id}.json"
                self._write_json(path, payload)
                report["successful_api_projects"].append(
                    {
                        "system": system,
                        "platform": "apifox",
                        "project_id": project_id,
                        "file": str(path),
                        "api_count": len(payload["apis"]),
                    }
                )
                report["generated_files"].append(_file_record(path, "接口获取 Agent 接口文档同步阶段"))
                report["summary"]["successful_api_projects"] += 1
            except Exception as exc:  # noqa: BLE001 - preserve sync continuity.
                report["failed_api_projects"].append(
                    {
                        "system": system,
                        "platform": "apifox",
                        "project_id": project_id,
                        "source_url": source_url,
                        "reason": _safe_error(exc),
                    }
                )
                report["summary"]["failed_api_projects"] += 1

    def _fetch_apifox_basic_index(
        self,
        *,
        system: str,
        project_id: str,
        source_url: str,
        credential: Any,
    ) -> dict[str, Any]:
        client = ApifoxClient(credential=credential)
        http_apis = client.list_http_apis(project_id)
        return normalize_http_apis_to_apifox_knowledge(
            system=system,
            project_id=project_id,
            source_url=source_url,
            http_apis=http_apis,
        )

    def _record_failed_database(
        self,
        report: dict[str, Any],
        system: str,
        db_name: str,
        reason: str,
    ) -> None:
        report["failed_databases"].append(
            {
                "system": system,
                "db_name": db_name,
                "reason": reason,
            }
        )
        report["summary"]["failed_databases"] += 1

    def _write_sync_report(self, report: dict[str, Any]) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.knowledge_root / "sync_reports"
        json_path = report_dir / f"{timestamp}_initial_sync_report.json"
        md_path = report_dir / f"{timestamp}_initial_sync_report.md"
        self._write_json(json_path, report)
        self._write_text(md_path, build_sync_report_markdown(report, json_path=json_path))

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def collect_mysql_schema(system: str, db_name: str, credential: Any) -> dict[str, Any]:
    collected_at = _now_iso()
    connection = pymysql.connect(
        host=credential.host,
        port=credential.port,
        user=credential.user,
        password=credential.password,
        database=db_name,
        charset="utf8mb4",
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT TABLE_NAME, COALESCE(TABLE_COMMENT, '') AS TABLE_COMMENT
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
                """,
                (db_name,),
            )
            table_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE, COLUMN_TYPE,
                       IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA,
                       COALESCE(COLUMN_COMMENT, '') AS COLUMN_COMMENT
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                (db_name,),
            )
            column_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE, COLUMN_NAME, SEQ_IN_INDEX, INDEX_TYPE
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
                """,
                (db_name,),
            )
            index_rows = cursor.fetchall()
    finally:
        connection.close()

    columns_by_table: dict[str, list[dict[str, Any]]] = {}
    for row in column_rows:
        columns_by_table.setdefault(str(row["TABLE_NAME"]), []).append(
            {
                "column_name": row["COLUMN_NAME"],
                "ordinal_position": int(row["ORDINAL_POSITION"]),
                "data_type": row["DATA_TYPE"],
                "column_type": row["COLUMN_TYPE"],
                "is_nullable": row["IS_NULLABLE"],
                "default_value": row["COLUMN_DEFAULT"],
                "column_key": row["COLUMN_KEY"],
                "extra": row["EXTRA"],
                "column_comment": row["COLUMN_COMMENT"],
            }
        )

    indexes_by_table: dict[str, dict[str, dict[str, Any]]] = {}
    for row in index_rows:
        table_indexes = indexes_by_table.setdefault(str(row["TABLE_NAME"]), {})
        index = table_indexes.setdefault(
            str(row["INDEX_NAME"]),
            {
                "index_name": row["INDEX_NAME"],
                "non_unique": bool(row["NON_UNIQUE"]),
                "columns": [],
                "index_type": row["INDEX_TYPE"],
            },
        )
        index["columns"].append(row["COLUMN_NAME"])

    tables = []
    for row in table_rows:
        table_name = str(row["TABLE_NAME"])
        tables.append(
            {
                "table_name": table_name,
                "table_comment": row["TABLE_COMMENT"],
                "columns": columns_by_table.get(table_name, []),
                "indexes": list(indexes_by_table.get(table_name, {}).values()),
            }
        )

    return {
        "file_info": {
            "file_name": f"{db_name}.json",
            "purpose": f"保存 {system} 系统 {db_name} 库的数据库结构知识，供接口获取 Agent 和自动化执行 Agent 使用。",
            "main_contents": "包含库名、表名、表注释、字段结构、字段类型、是否可为空、默认值、主键信息、索引信息和字段注释；不包含任何业务数据。",
            "stage": "接口获取 Agent 数据库结构同步阶段",
            "view_method": "使用文本编辑器或 JSON 查看器打开，也可由后续 Agent 直接读取。",
        },
        "system": system,
        "source_type": "mysql_schema",
        "db_name": db_name,
        "collected_at": collected_at,
        "collector_version": "mvp-v1",
        "tables": tables,
        "missing_fields": [],
        "warnings": [],
    }


def normalize_openapi_to_apifox_knowledge(
    *,
    system: str,
    project_id: str,
    source_url: str,
    openapi: dict[str, Any],
) -> dict[str, Any]:
    collected_at = _now_iso()
    apis = []
    for path, path_item in sorted(openapi.get("paths", {}).items()):
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            upper_method = str(method).upper()
            if upper_method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
                continue
            operation = operation if isinstance(operation, dict) else {}
            tags = [str(tag) for tag in operation.get("tags", [])]
            api_name = operation.get("summary") or operation.get("operationId") or f"{upper_method} {path}"
            missing_fields = []
            if not operation.get("description"):
                missing_fields.append("description")
            updated_at = operation.get("x-apifox-updated-at") or operation.get("updatedAt") or "待确认"
            if updated_at == "待确认":
                missing_fields.append("updated_at")

            apis.append(
                {
                    "module": tags[0] if tags else "",
                    "folder_path": tags,
                    "api_name": str(api_name),
                    "method": upper_method,
                    "path": path,
                    "description": str(operation.get("description", "")),
                    "operation_id": str(operation.get("operationId", "")),
                    "tags": tags,
                    "source": source_url,
                    "project_id": project_id,
                    "updated_at": str(updated_at),
                    "sync_mode": BASIC_API_INDEX_SYNC_MODE,
                    "detail_fetch_policy": BASIC_API_INDEX_DETAIL_FETCH_POLICY,
                    "missing_fields": missing_fields,
                }
            )

    return {
        "file_info": {
            "file_name": f"apifox_project_{project_id}.json",
            "purpose": f"保存 {system} 系统 Apifox 项目 {project_id} 的基础接口索引，供测试用例 Agent 和接口获取 Agent 快速检索相关接口。",
            "main_contents": "仅包含接口名称、所属模块、目录路径、请求方式、接口路径、接口说明、operationId 和缺失字段标记；请求头、请求参数、请求体和响应体在具体需求处理时由 Agent 3 按需从 Apifox 获取。",
            "stage": "接口获取 Agent 接口文档同步阶段",
            "view_method": "使用文本编辑器或 JSON 查看器打开，也可由后续 Agent 直接读取。",
        },
        "system": system,
        "platform": "apifox",
        "project_id": project_id,
        "source_url": source_url,
        "collected_at": _now_iso(),
        "collector_version": "mvp-v1",
        "sync_mode": BASIC_API_INDEX_SYNC_MODE,
        "detail_fetch_policy": BASIC_API_INDEX_DETAIL_FETCH_POLICY,
        "apis": apis,
        "missing_fields": [],
        "warnings": [],
    }


def normalize_http_apis_to_apifox_knowledge(
    *,
    system: str,
    project_id: str,
    source_url: str,
    http_apis: list[dict[str, Any]],
) -> dict[str, Any]:
    collected_at = _now_iso()
    apis = [
        _normalize_http_api_to_basic_index_item(item, project_id=project_id, source_url=source_url)
        for item in http_apis
        if isinstance(item, dict)
    ]
    return {
        "file_info": {
            "file_name": f"apifox_project_{project_id}.json",
            "purpose": (
                f"保存 {system} 系统 Apifox 项目 {project_id} 的基础接口索引，"
                "供候选接口定位与后续按需详情获取使用。"
            ),
            "main_contents": (
                "仅包含基础索引字段：module、folder_path、api_name、method、path、description、"
                "operation_id、tags、source、project_id、updated_at、sync_mode、detail_fetch_policy、missing_fields。"
            ),
            "stage": "接口获取 Agent 接口知识库同步阶段",
            "view_method": "使用文本编辑器或 JSON 查看器打开，也可由后续 Agent 直接读取。",
        },
        "system": system,
        "platform": "apifox",
        "project_id": project_id,
        "source_url": source_url,
        "collected_at": collected_at,
        "collector_version": "mvp-v1",
        "sync_mode": BASIC_API_INDEX_SYNC_MODE,
        "detail_fetch_policy": BASIC_API_INDEX_DETAIL_FETCH_POLICY,
        "apis": apis,
        "missing_fields": [],
        "warnings": [],
    }


def _normalize_http_api_to_basic_index_item(
    item: dict[str, Any],
    *,
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


def build_sync_report_markdown(report: dict[str, Any], *, json_path: Path) -> str:
    lines = [
        "# 数据库结构与接口文档初始化同步报告",
        "",
        "## 文件说明",
        "",
        "- 文件名称：初始化同步报告",
        "- 文件作用：记录本次数据库结构与接口文档同步结果。",
        "- 文件主要内容：成功对象、失败对象、生成文件、失败原因和后续增量更新方式。",
        "- 所属阶段：接口获取 Agent 知识库同步阶段。",
        f"- 查看方式：打开 `{json_path}` 查看结构化明细，或阅读本 Markdown 摘要。",
        "",
        "## 汇总",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}：{value}")

    lines.extend(["", "## 成功同步的数据库"])
    if report["successful_databases"]:
        for item in report["successful_databases"]:
            lines.append(f"- {item['system']} / {item['db_name']}：{item['table_count']} 张表，文件 `{item['file']}`")
    else:
        lines.append("- 无")

    lines.extend(["", "## 成功同步的接口项目"])
    if report["successful_api_projects"]:
        for item in report["successful_api_projects"]:
            lines.append(f"- {item['system']} / Apifox {item['project_id']}：{item['api_count']} 条接口，文件 `{item['file']}`")
    else:
        lines.append("- 无")

    lines.extend(["", "## 失败的数据库"])
    if report["failed_databases"]:
        for item in report["failed_databases"]:
            lines.append(f"- {item['system']} / {item['db_name']}：{item['reason']}")
    else:
        lines.append("- 无")

    lines.extend(["", "## 失败的接口项目"])
    if report["failed_api_projects"]:
        for item in report["failed_api_projects"]:
            lines.append(f"- {item['system']} / Apifox {item['project_id']}：{item['reason']}")
    else:
        lines.append("- 无")

    lines.extend(
        [
            "",
            "## 后续增量更新说明",
            "",
            "- 指定系统更新：提供 `system`，例如 `silkroad`。",
            "- 指定数据库更新：提供 `system + db_name`，例如 `silkroad + center`。",
            "- 指定接口项目更新：提供 `system + project_id`，例如 `silkroad + 776242`。",
        ]
    )
    return "\n".join(lines)


def _extract_examples(request_body: dict[str, Any], response_body: dict[str, Any]) -> dict[str, Any]:
    return {
        "request": _find_first_example(request_body),
        "response": _find_first_example(response_body),
    }


def _find_first_example(node: Any) -> Any:
    if isinstance(node, dict):
        if "example" in node:
            return node["example"]
        if "examples" in node:
            return node["examples"]
        for value in node.values():
            found = _find_first_example(value)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find_first_example(value)
            if found is not None:
                return found
    return None


def _infer_auth_type(openapi: dict[str, Any], operation: dict[str, Any]) -> str:
    security = operation.get("security", openapi.get("security", []))
    if not security:
        return ""
    return ",".join(sorted({key for item in security if isinstance(item, dict) for key in item.keys()}))


def _file_record(path: Path, stage: str) -> dict[str, str]:
    return {
        "file_name": path.name,
        "path": str(path),
        "purpose": "保存本次知识库同步产生的结构化结果文件。",
        "main_contents": "包含接口获取 Agent 同步得到的数据库结构、接口文档或同步报告。",
        "stage": stage,
        "view_method": "使用文本编辑器或 JSON/Markdown 查看器打开。",
    }


def _safe_error(exc: Exception) -> str:
    text = str(exc)
    for marker in ["password=", "passwd="]:
        if marker in text.lower():
            return exc.__class__.__name__
    return f"{exc.__class__.__name__}: {text}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()
