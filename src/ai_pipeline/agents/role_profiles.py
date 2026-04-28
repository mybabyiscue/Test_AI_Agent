from __future__ import annotations

from copy import deepcopy
from typing import Any

from ..role_loader import RoleLoader


GLOBAL_FILE_STORAGE_POLICY: dict[str, Any] = {
    "status": "enabled",
    "config_path": "config/agent_file_storage_policy.json",
    "must_announce_before_task": True,
    "flow_files_must_stay_under_current_run_dir": True,
    "agent_directory_structure": ["input", "output", "log"],
    "summary_dir": "summary",
    "forbid_project_root_task_artifacts": True,
    "cleanup_non_compliant_files_after_task": True,
    "delete_requires_user_confirmation": True,
}


def get_role_profile(agent_name: str) -> dict[str, Any]:
    loader = RoleLoader.default()
    profile = deepcopy(loader.load(agent_name))
    profile["file_storage_policy"] = deepcopy(GLOBAL_FILE_STORAGE_POLICY)
    return profile


def render_role_profile_markdown(profile: dict[str, Any]) -> str:
    markdown = str(profile.get("role_markdown", "")).rstrip()
    if not markdown:
        markdown = RoleLoader.default().load_markdown(str(profile["agent_name"])).rstrip()
    if "file_storage_policy" not in profile:
        return markdown + "\n"

    policy = profile["file_storage_policy"]
    extra = [
        "",
        "## 文件生成与存储规范",
        "",
        f"- 规范状态：{policy['status']}",
        f"- 全局配置：`{policy['config_path']}`",
        "- 任务开始前必须明确注明该规范已生效。",
        "- 每次新流程必须先创建本次流程专属总文件夹。",
        "- 本次流程产生的所有文件只能位于本次流程总文件夹内。",
        "- 每个 Agent 固定使用 `input/`、`output/`、`log/` 三类目录。",
        "- 全局汇总文件固定写入 `summary/`。",
        "- 禁止在项目根目录、临时目录或本次流程总文件夹之外创建任务产物。",
        "- 执行完成后必须检查并清理不符合目录规范的文件；删除前必须获得用户确认。",
    ]
    return markdown + "\n" + "\n".join(extra).rstrip() + "\n"
