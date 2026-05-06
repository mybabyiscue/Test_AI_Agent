from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


def parse_pytest_summary(output: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "skipped": 0}
    for key in summary:
        match = re.search(rf"(\d+) {key}", output)
        if match:
            summary[key] = int(match.group(1))
    return summary


def generate_allure_html_report(results_dir: Path, report_dir: Path) -> dict[str, object]:
    if not results_dir.exists() or not any(results_dir.iterdir()):
        return {
            "generated": False,
            "reason": "allure_results_missing",
            "results_dir": str(results_dir),
            "report_dir": str(report_dir),
            "index_path": None,
        }

    allure_command = shutil.which("allure")
    if not allure_command:
        return {
            "generated": False,
            "reason": "allure_cli_missing",
            "results_dir": str(results_dir),
            "report_dir": str(report_dir),
            "index_path": None,
        }

    completed = subprocess.run(
        [allure_command, "generate", str(results_dir), "-o", str(report_dir), "--clean"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    index_path = report_dir / "index.html"
    return {
        "generated": completed.returncode == 0 and index_path.exists(),
        "reason": None if completed.returncode == 0 and index_path.exists() else "allure_generate_failed",
        "results_dir": str(results_dir),
        "report_dir": str(report_dir),
        "index_path": str(index_path) if index_path.exists() else None,
        "command": [allure_command, "generate", str(results_dir), "-o", str(report_dir), "--clean"],
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def build_allure_viewing_guide(
    *,
    report_dir: Path,
    results_dir: Path,
    port: int = 18088,
) -> str:
    resolved_report_dir = report_dir.resolve()
    resolved_results_dir = results_dir.resolve()
    index_path = (resolved_report_dir / "index.html").resolve()
    return "\n".join(
        [
            "# Allure 报告查看方式说明",
            "",
            "## index.html 的用途",
            "`index.html` 是 Allure HTML 报告的前端入口文件，它会读取同目录下的 `widgets/`、`data/`、`history/` 等 JSON 数据来展示测试结果。",
            "",
            "## 报告文件所在目录",
            f"- 报告目录：`{resolved_report_dir}`",
            f"- 入口文件：`{index_path}`",
            f"- Allure 原始结果目录：`{resolved_results_dir}`",
            "",
            "## 查看方式 1：使用 Python 启动本地静态服务（推荐）",
            "直接用 `file://` 打开时，部分浏览器会因为本地文件安全策略导致页面一直 loading。推荐使用本地 HTTP 服务查看。",
            "",
            "```powershell",
            f"Set-Location -LiteralPath \"{resolved_report_dir}\"",
            f"python -m http.server {port} --bind 127.0.0.1",
            "```",
            "",
            "然后在浏览器访问：",
            "",
            f"`http://127.0.0.1:{port}/index.html`",
            "",
            "查看完成后，在启动服务的终端按 `Ctrl+C` 关闭。",
            "",
            "## 查看方式 2：使用 Allure CLI 直接打开原始结果",
            "如果本机已安装 Allure CLI，可以直接执行：",
            "",
            "```powershell",
            f"allure open \"{resolved_results_dir}\"",
            "```",
            "",
            "该命令会自动启动一个本地 Web 服务并打开浏览器。",
            "",
            "## 查看方式 3：直接打开 index.html（不推荐作为唯一方式）",
            "如果浏览器允许本地文件读取，可以执行：",
            "",
            "```powershell",
            f"Start-Process -FilePath \"{index_path}\"",
            "```",
            "",
            '如果页面一直停留在 loading，请改用"查看方式 1"。',
        ]
    )
