"""知识库同步脚本 - 支持全量同步和增量同步。

用法:
    # 全量同步（数据库 + 接口）
    python scripts/sync_knowledge.py

    # 只同步数据库
    python scripts/sync_knowledge.py --db-only

    # 只同步接口
    python scripts/sync_knowledge.py --api-only

    # 同步指定系统（如 silkroad）
    python scripts/sync_knowledge.py --system silkroad

    # 只同步指定系统的数据库
    python scripts/sync_knowledge.py --system silkroad --db-only

    # 只同步指定系统的接口
    python scripts/sync_knowledge.py --system saas --api-only

    # 同步指定数据库
    python scripts/sync_knowledge.py --system silkroad --db center

    # 同步指定接口项目
    python scripts/sync_knowledge.py --system saas --project 4152663
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_pipeline.knowledge_sync import KnowledgeSyncer, collect_mysql_schema
from ai_pipeline.config import project_root


def main() -> int:
    parser = argparse.ArgumentParser(description="知识库同步工具")
    parser.add_argument("--system", help="指定系统: silkroad, shark, saas, callcenter")
    parser.add_argument("--db", help="指定数据库名（需配合 --system）")
    parser.add_argument("--project", help="指定 Apifox 项目 ID（需配合 --system）")
    parser.add_argument("--db-only", action="store_true", help="只同步数据库")
    parser.add_argument("--api-only", action="store_true", help="只同步接口")
    args = parser.parse_args()

    sync_databases = not args.api_only
    sync_apis = not args.db_only

    syncer = KnowledgeSyncer.default()
    sources = json.loads(syncer.sources_config_path.read_text(encoding="utf-8-sig"))
    systems = sources.get("systems", {})

    # Validate --system
    if args.system and args.system not in systems:
        print(f"错误: 未知系统 '{args.system}'，可选: {', '.join(systems.keys())}")
        return 1

    # Specific database sync
    if args.system and args.db:
        return sync_single_database(syncer, systems, args.system, args.db)

    # Specific API project sync
    if args.system and args.project:
        return sync_single_project(syncer, systems, args.system, args.project)

    # System-level or full sync
    if args.system:
        return sync_system(syncer, systems, args.system, sync_databases, sync_apis)

    # Full sync
    report = syncer.sync_all(sync_databases=sync_databases, sync_apis=sync_apis)
    print_report(report)
    return 0


def sync_single_database(syncer: KnowledgeSyncer, systems: dict, system: str, db_name: str) -> int:
    config = systems.get(system, {})
    db_config = config.get("databases")
    if not db_config:
        print(f"错误: 系统 '{system}' 没有数据库配置")
        return 1

    schemas = db_config.get("schemas", [])
    if db_name not in schemas:
        print(f"错误: 系统 '{system}' 中没有数据库 '{db_name}'，可选: {', '.join(schemas)}")
        return 1

    profile = db_config.get("profile", system)
    try:
        credential = syncer.credential_provider.get_database(profile)
    except Exception as exc:
        print(f"错误: 获取数据库凭证失败 - {exc}")
        return 1

    print(f"正在同步 {system}/{db_name} ...")
    try:
        payload = collect_mysql_schema(system=system, db_name=db_name, credential=credential)
        path = syncer.knowledge_root / system / "database" / f"{db_name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"完成: {system}/{db_name} - {len(payload['tables'])} 张表 -> {path}")
        return 0
    except Exception as exc:
        print(f"错误: {exc}")
        return 1


def sync_single_project(syncer: KnowledgeSyncer, systems: dict, system: str, project_id: str) -> int:
    config = systems.get(system, {})
    apis_config = config.get("apis", [])
    target = None
    for api in apis_config:
        if str(api.get("project_id")) == str(project_id):
            target = api
            break

    if not target:
        available = [str(a.get("project_id")) for a in apis_config]
        print(f"错误: 系统 '{system}' 中没有项目 '{project_id}'，可选: {', '.join(available)}")
        return 1

    credential_profile = target.get("credential_profile", "default")
    try:
        credential = syncer.credential_provider.get("apifox", profile=credential_profile)
    except Exception as exc:
        print(f"错误: 获取 Apifox 凭证失败 - {exc}")
        return 1

    print(f"正在同步 {system}/apifox/{project_id} ...")
    try:
        payload = syncer._fetch_apifox_basic_index(
            system=system,
            project_id=str(project_id),
            source_url=str(target["url"]),
            credential=credential,
        )
        path = syncer.knowledge_root / system / "apis" / f"apifox_project_{project_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"完成: {system}/apifox/{project_id} - {len(payload['apis'])} 条接口 -> {path}")
        return 0
    except Exception as exc:
        print(f"错误: {exc}")
        return 1


def sync_system(syncer: KnowledgeSyncer, systems: dict, system: str, sync_databases: bool, sync_apis: bool) -> int:
    started_at = datetime.now(timezone.utc).astimezone().isoformat()
    report = {
        "sync_type": "incremental",
        "system": system,
        "started_at": started_at,
        "finished_at": None,
        "summary": {"successful_databases": 0, "failed_databases": 0, "successful_api_projects": 0, "failed_api_projects": 0, "generated_files": 0},
        "successful_databases": [],
        "failed_databases": [],
        "successful_api_projects": [],
        "failed_api_projects": [],
        "generated_files": [],
    }

    config = systems[system]
    if sync_databases:
        syncer._sync_system_databases(system, config, report)
    if sync_apis:
        syncer._sync_system_apis(system, config, report)

    report["finished_at"] = datetime.now(timezone.utc).astimezone().isoformat()
    print_report(report)
    return 0 if not report["failed_databases"] and not report["failed_api_projects"] else 1


def print_report(report: dict) -> None:
    print("\n=== 同步结果 ===")
    if "system" in report:
        print(f"系统: {report['system']}")

    s = report.get("summary", {})
    if s.get("successful_databases"):
        print(f"数据库: {s['successful_databases']} 成功, {s.get('failed_databases', 0)} 失败")
    if s.get("successful_api_projects"):
        print(f"接口项目: {s['successful_api_projects']} 成功, {s.get('failed_api_projects', 0)} 失败")

    for item in report.get("successful_databases", []):
        print(f"  [OK] {item['system']}/{item['db_name']}: {item['table_count']} 张表")
    for item in report.get("failed_databases", []):
        print(f"  [FAIL] {item['system']}/{item['db_name']}: {item['reason']}")
    for item in report.get("successful_api_projects", []):
        print(f"  [OK] {item['system']}/apifox/{item['project_id']}: {item['api_count']} 条接口")
    for item in report.get("failed_api_projects", []):
        print(f"  [FAIL] {item['system']}/apifox/{item['project_id']}: {item['reason']}")


if __name__ == "__main__":
    sys.exit(main())
