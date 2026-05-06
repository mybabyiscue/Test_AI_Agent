from __future__ import annotations

from pathlib import Path
from typing import Any


def build_traceability_report(
    run_id: str,
    requirement_model: dict[str, object],
    test_cases: dict[str, object],
    endpoint_mapping: dict[str, object],
) -> dict[str, object]:
    mappings_by_test_case = {
        mapping["test_case_id"]: mapping for mapping in endpoint_mapping["mappings"]
    }
    chains = []
    for case in test_cases["cases"]:
        mapping = mappings_by_test_case[case["test_case_id"]]
        chains.append(
            {
                "requirement_id": requirement_model["requirement_id"],
                "test_case_id": case["test_case_id"],
                "automation_id": mapping["automation_id"],
                "path": mapping["path"],
                "method": mapping["method"],
            }
        )
    return {"run_id": run_id, "chains": chains}


def build_final_summary(execution_report: dict[str, object]) -> str:
    summary = execution_report["summary"]
    return "\n".join(
        [
            "# Final Summary",
            "",
            f"- pytest exit code: {execution_report['pytest_exit_code']}",
            f"- passed: {summary['passed']}",
            f"- failed: {summary['failed']}",
            f"- skipped: {summary['skipped']}",
        ]
    )


def build_artifact_inventory(run_dir: Path) -> dict[str, object]:
    files = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_file():
            relative_path = path.relative_to(run_dir).as_posix()
            group = _classify_artifact_group(relative_path)
            description = _describe_artifact(relative_path, group)
            files.append(
                {
                    "path": relative_path,
                    "type": path.suffix or "no_suffix",
                    "size_bytes": path.stat().st_size,
                    "group": group,
                    **description,
                }
            )
    return {
        "record_dir": str(run_dir),
        "file_count": len(files),
        "explanation_rule": {
            "language": "中文",
            "required_fields": ["file_name", "purpose", "main_contents", "stage"],
            "rule": "每个输出文件必须明确说明文件名称、文件作用、文件主要内容、所属流程阶段。",
        },
        "files": files,
    }


def build_file_compliance_check(artifact_inventory: dict[str, object]) -> str:
    files = artifact_inventory["files"]
    unexpected = [
        file_info["path"]
        for file_info in files
        if str(file_info["group"]) == "record_metadata"
    ]
    status = "通过" if not unexpected else "存在异常"
    lines = [
        "# 文件合规检查",
        "",
        "## 检查结论",
        f"- 状态：{status}",
        "- 规则：本次流程所有文件必须位于本次流程总文件夹内。",
        "- 规则：每个 Agent 只能使用自己的 input、output、log 文件夹。",
        "- 规则：全局汇总文件必须位于 summary 文件夹。",
        "",
        "## 异常文件",
    ]
    if unexpected:
        lines.extend(f"- `{path}`" for path in unexpected)
    else:
        lines.append("- 无")
    return "\n".join(lines) + "\n"


def build_record_index(
    manifest: dict[str, object],
    artifact_inventory: dict[str, object],
) -> str:
    record_policy = manifest["record_policy"]
    files = artifact_inventory["files"]
    files_by_group: dict[str, list[dict[str, object]]] = {}
    for file_info in files:
        files_by_group.setdefault(str(file_info["group"]), []).append(file_info)

    explanation_rule = record_policy.get("output_file_explanation_rule", {})

    lines = [
        "# 需求记录目录索引",
        "",
        "## 强制记录规则",
        f"- 记录目录：`{record_policy['record_dir']}`",
        "- 该需求相关的所有输入、输出、日志、报告和 Allure 产物必须集中保存在本目录下。",
        "- 不允许只在对话中给出结果而不落盘保存。",
        "- 不允许把同一需求的核心产物分散到记录目录之外。",
        "- 后续所有输出文件必须附带中文解释说明，不能只输出文件路径或文件名。",
        "",
        "## 输出文件中文说明规则",
        f"- 说明语言：{explanation_rule.get('language', '中文')}",
        "- 必须说明：文件名称、文件作用、文件主要内容、所属阶段。",
        "",
        "## 文件类型",
    ]
    lines.extend([f"- `{file_type}`" for file_type in record_policy["file_types"]])
    lines.extend(["", "## 产物分组"])
    for group in record_policy["required_groups"]:
        group_files = files_by_group.get(str(group), [])
        lines.append(f"- {group}：{len(group_files)} 个文件")

    lines.extend(["", "## 核心入口文件"])
    artifacts = manifest["artifacts"]
    for name, path in artifacts.items():
        lines.append(f"- {name}：`{path}`")

    lines.extend(["", "## 全量产物清单"])
    for file_info in files:
        lines.extend(
            [
                f"### {file_info['path']}",
                f"- 文件名称：{file_info['file_name']}",
                f"- 文件作用：{file_info['purpose']}",
                f"- 文件主要内容：{file_info['main_contents']}",
                f"- 所属阶段：{file_info['stage']}",
                f"- 文件分组：{file_info['group']}",
                f"- 文件类型：`{file_info['type']}`",
                f"- 文件大小：{file_info['size_bytes']} bytes",
                "",
            ]
        )
    return "\n".join(lines)


def _classify_artifact_group(relative_path: str) -> str:
    if relative_path.endswith("/log/state.json") or "/log/" in relative_path:
        return "logs"
    if "/input/" in relative_path:
        return "inputs"
    if relative_path.startswith("requirement_agent/"):
        return "requirement_analysis"
    if relative_path.startswith("testcase_agent/"):
        return "testcases"
    if relative_path.startswith("api_mapper_agent/"):
        return "api_assets"
    if relative_path.startswith("automation_agent/"):
        return "automation"
    if relative_path.startswith("summary/"):
        return "summary"
    return "record_metadata"


def _artifact_stage_label(group: str) -> str:
    return {
        "inputs": "输入准备阶段",
        "requirement_analysis": "需求分析 Agent 阶段",
        "testcases": "测试用例 Agent 阶段",
        "api_assets": "接口获取 Agent 阶段",
        "automation": "接口自动化 Agent 阶段",
        "logs": "执行日志阶段",
        "reports": "流程汇总与报告阶段",
        "record_metadata": "需求记录元数据阶段",
    }.get(group, "未分类阶段")


_KNOWN_FILES: dict[str, tuple[str, str]] = {
    "manifest.json": (
        "记录本次需求执行的全局元信息和产物入口，便于后续追溯整条流程。",
        "包含运行编号、记录目录、强制记录规则、Agent 阶段列表、核心产物路径和各 Agent 工作区。",
    ),
    "record_index.md": (
        "作为本次需求的中文总目录，帮助最终使用者快速理解每个输出文件的用途。",
        "包含记录规则、文件类型、产物分组、核心入口文件以及全量产物的中文说明。",
    ),
    "run_log.jsonl": (
        "记录整条流程中各 Agent 的执行事件，用于排查执行顺序和失败原因。",
        "按行保存阶段启动、完成、失败等事件，以及对应时间、命令和输出文件信息。",
    ),
    "state.json": (
        "记录当前 Agent 工作区的执行状态，便于确认该阶段是否成功完成。",
        "包含 Agent 名称、运行编号、状态、输入文件、输出文件、执行命令、开始结束时间和角色职责。",
    ),
    "role_profile.json": (
        "保存当前 Agent 的机器可读角色职责定义，确保后续执行时职责边界清晰。",
        "包含 Agent 角色名称、职责范围、输入输出、约束规则和严格模式要求。",
    ),
    "role_profile.md": (
        "保存当前 Agent 的中文角色说明文档，方便人工查看和后续扩展。",
        "包含 Agent 职责、输入、输出、禁止事项和执行要求。",
    ),
    "llm_prompt.md": (
        "保存当前阶段实际注入模型的最终 Prompt，确保职责注入链路可追踪。",
        "包含当前 Agent 职责 Markdown、阶段任务模板、阶段输入、上一阶段输出、输出要求和阻塞条件。",
    ),
    "llm_invocation.json": (
        "保存当前阶段的 Prompt 注入元数据，便于核对职责文件、模板文件和执行后端。",
        "包含 Agent 名称、后端类型、职责 Markdown 路径、Prompt 模板路径、阶段输入摘要和阻塞条件。",
    ),
    "worker_stdout.log": (
        "保存当前 Agent 子进程的标准输出，用于复盘执行过程。",
        "包含该阶段运行时打印的普通日志和调试输出。",
    ),
    "worker_stderr.log": (
        "保存当前 Agent 子进程的错误输出，用于定位异常和失败原因。",
        "包含该阶段运行时打印的错误、警告或异常堆栈。",
    ),
    "stage.log": (
        "保存当前阶段的人工可读执行日志，用于快速了解阶段处理过程。",
        "包含阶段内部关键步骤、处理结果和可能的提示信息。",
    ),
    "execution.log": (
        "保存自动化测试执行日志，用于复盘 pytest、Allure 和接口请求执行情况。",
        "包含自动化执行命令、运行输出、失败信息和报告生成过程。",
    ),
    "requirement_model.json": (
        "保存结构化需求分析结果，供测试用例 Agent 继续消费。",
        "包含需求名称、背景、目标、角色、流程、规则、异常场景、影响范围、风险和待确认问题。",
    ),
    "acceptance_criteria.json": (
        "保存需求验收关注点，作为后续测试点和测试用例设计依据。",
        "包含可验收条件、关键校验点、通过标准和需要确认的验收缺口。",
    ),
    "business_flow.md": (
        "用中文描述需求核心业务流程，帮助后续 Agent 和人工快速理解业务链路。",
        "包含主流程、分支流程、异常流程以及上下游系统交互说明。",
    ),
    "risk_points.json": (
        "保存需求分析阶段识别出的风险点，提醒后续测试设计重点关注。",
        "包含需求缺失、歧义、接口依赖、数据风险、权限风险和阻塞点。",
    ),
    "test_cases.json": (
        "保存结构化测试用例，供接口获取和自动化阶段继续使用。",
        "包含用例编号、标题、优先级、前置条件、步骤、预期结果和自动化候选标记。",
    ),
    "test_points.json": (
        "保存需求点、测试点与测试用例之间的追溯关系，供阶段门禁和后续审计使用。",
        "包含测试点编号、关联需求编号、关联验收标准、覆盖类型、自动化候选状态和关联用例编号。",
    ),
    "test_case_matrix.csv": (
        "保存测试用例矩阵，便于人工审阅、筛选和导入其他测试管理工具。",
        "包含测试点、用例、优先级、场景类型、自动化适配性和覆盖关系。",
    ),
    "coverage_report.md": (
        "说明测试用例对需求点的覆盖情况，帮助识别遗漏和覆盖不足。",
        "包含需求点覆盖、异常场景覆盖、自动化候选覆盖和待补充范围。",
    ),
    "api_catalog.json": (
        "保存从接口平台或接口文档提取出的标准接口资产清单。",
        "包含接口路径、方法、分组、参数、响应、认证方式和接口来源信息。",
    ),
    "endpoint_mapping.json": (
        "保存测试用例与接口之间的映射关系，供自动化阶段生成脚本使用。",
        "包含用例编号、接口路径、请求方法、请求数据、期望状态码和自动化编号。",
    ),
    "request_schema.json": (
        "保存接口请求结构说明，便于自动化脚本生成请求参数和测试数据。",
        "包含路径参数、查询参数、请求体字段、必填项和字段类型。",
    ),
    "dependency_graph.json": (
        "保存接口依赖关系，帮助自动化阶段安排登录、造数、清理和业务链路顺序。",
        "包含接口之间的数据依赖、前置依赖、后置清理依赖和调用顺序建议。",
    ),
    "api_source_request.json": (
        "保存接口来源请求声明，说明本次希望从哪个平台或地址获取接口信息。",
        "包含平台类型、来源 URL、项目或接口定位信息以及 Agent 的接口获取意图。",
    ),
    "api_source_resolved.json": (
        "保存接口来源解析结果，说明平台接入层实际解析出的项目、分组或接口范围。",
        "包含平台项目标识、接口范围、解析状态和标准化来源信息。",
    ),
    "api_document.json": (
        "保存平台接入层拉取并标准化后的接口文档，作为接口获取 Agent 的真实输入。",
        "包含接口基础信息、请求响应定义、分组结构和平台原始数据摘要。",
    ),
    "automation_plan.json": (
        "保存接口自动化设计方案，说明哪些用例可以自动化以及如何执行。",
        "包含自动化范围、脚本生成策略、环境依赖、断言规则、Allure 报告设计和阻塞条件。",
    ),
    "execution_report.json": (
        "保存自动化执行结果，供最终报告和问题复盘使用。",
        "包含 pytest 退出码、通过失败跳过数量、生成脚本数量、Allure 结果目录和报告路径。",
    ),
    "allure_report_viewing_guide.md": (
        "说明 Allure HTML 报告的查看方式，确保最终使用者能直接打开报告。",
        "包含 index.html 用途、报告目录、PowerShell 查看命令、Python 静态服务命令和 Allure CLI 命令。",
    ),
    "traceability_report.json": (
        "保存需求、测试用例、接口和自动化脚本之间的追溯链路。",
        "包含需求编号、用例编号、自动化编号、接口路径和请求方法的对应关系。",
    ),
    "final_summary.md": (
        "保存本次流程最终摘要，便于快速查看自动化执行结论。",
        "包含 pytest 退出码、通过数、失败数和跳过数等关键结果。",
    ),
    "artifact_inventory.json": (
        "保存本次需求的全量产物清单和中文解释说明，是后续查找文件的机器可读索引。",
        "包含每个文件的路径、类型、大小、分组、文件名称、文件作用、主要内容和所属阶段。",
    ),
}


def _describe_artifact(relative_path: str, group: str) -> dict[str, str]:
    path = Path(relative_path)
    file_name = path.name
    stage = _artifact_stage_label(group)
    lower_path = relative_path.lower()

    if file_name in _KNOWN_FILES:
        purpose, main_contents = _KNOWN_FILES[file_name]
    elif "generated_tests/" in lower_path and file_name.endswith(".py"):
        purpose = "保存自动生成的接口自动化测试脚本，供 pytest 和 Allure 执行展示。"
        main_contents = "包含接口请求逻辑、断言逻辑、Allure epic/feature/story/title/step/attachment 标注和测试数据处理。"
    elif "allure-results/" in lower_path:
        purpose = "保存 Allure 原始执行结果数据，供生成 HTML 报告使用。"
        main_contents = "包含测试用例结果、步骤、附件、容器信息和 Allure 识别的执行元数据。"
    elif "allure-report/" in lower_path:
        purpose = "保存 Allure 生成的 HTML 静态报告文件，供最终查看和共享测试结果。"
        main_contents = "包含报告页面资源、测试结果展示数据、样式脚本和 index.html 入口。"
    elif "/input/" in lower_path:
        purpose = "保存当前阶段的输入文件，保证后续可以复盘该 Agent 当时基于什么内容处理。"
        main_contents = "包含上游阶段传入的数据、用户提供的原始资料或平台接入层解析后的输入。"
    elif path.suffix == ".json":
        purpose = "保存当前流程产出的结构化 JSON 数据，供后续 Agent 或工具读取。"
        main_contents = "包含与该文件名对应的结构化字段、处理结果、状态信息或配置数据。"
    elif path.suffix == ".md":
        purpose = "保存当前流程产出的中文说明文档，供人工审阅、交接和复盘使用。"
        main_contents = "包含与该文件名对应的分析说明、设计说明、报告说明或查看说明。"
    elif path.suffix == ".csv":
        purpose = "保存当前流程产出的表格化数据，便于人工筛选、导入或二次处理。"
        main_contents = "包含与该文件名对应的行列数据和覆盖关系。"
    elif path.suffix == ".log":
        purpose = "保存当前流程的日志信息，便于定位执行过程和异常原因。"
        main_contents = "包含运行命令输出、阶段处理信息、错误提示或调试日志。"
    else:
        purpose = "保存当前流程运行过程中生成的辅助产物，便于追溯和复盘。"
        main_contents = "包含与该文件类型对应的运行数据、页面资源、附件或中间结果。"

    return {
        "file_name": file_name,
        "purpose": purpose,
        "main_contents": main_contents,
        "stage": stage,
    }
