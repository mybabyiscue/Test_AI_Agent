from __future__ import annotations

from typing import Any


_LLM_OUTPUT_SCHEMAS: dict[str, dict[str, str]] = {
    "requirement_agent": {
        "requirement_model": "结构化需求模型 JSON，包含 requirement_id, title, scenarios 等字段",
        "acceptance_criteria": "验收标准 JSON，包含 criteria 数组",
        "business_flow": "业务流程 Markdown 文本",
        "risk_points": "风险点 JSON，包含 risks 数组",
    },
    "testcase_agent": {
        "test_cases": "测试用例 JSON，包含 cases 数组，每个 case 需有 test_case_id, requirement_id, title, priority, expected_status_codes",
        "test_points": "测试点 JSON，包含 test_points 数组",
        "test_case_matrix": "CSV 格式的测试矩阵文本",
        "coverage_report": "覆盖报告 Markdown 文本",
    },
    "api_mapper_agent": {
        "api_catalog": "接口目录 JSON",
        "endpoint_mapping": "接口映射 JSON，包含 mappings 数组，每个 mapping 需有 test_case_id, path, method, request_body, response_body, auth_type, automation_id",
        "request_schema": "请求结构 JSON",
        "dependency_graph": "依赖关系 JSON",
        "database_catalog": "数据库目录 JSON",
        "database_mapping": "数据库映射 JSON",
        "missing_database_report": "缺失数据库报告 Markdown 文本",
    },
    "automation_agent": {
        "automation_plan": "自动化方案 JSON",
        "execution_report": "执行报告 JSON，需包含 pytest_exit_code, summary(passed, failed, skipped)",
    },
}

_LLM_OUTPUT_EXAMPLES: dict[str, str] = {
    "requirement_agent": (
        '{\n'
        '  "requirement_model": {\n'
        '    "requirement_id": "REQ-001",\n'
        '    "title": "用户注册",\n'
        '    "scenarios": [{"id": "S1", "name": "正常注册", "steps": ["填写邮箱", "提交注册"]}],\n'
        '    "rules": ["邮箱唯一"],\n'
        '    "exception_scenarios": [{"id": "E1", "name": "重复邮箱", "expected": "注册失败"}]\n'
        '  },\n'
        '  "acceptance_criteria": {\n'
        '    "criteria": [{"id": "AC-1", "description": "合法资料注册成功", "priority": "P0"}]\n'
        '  },\n'
        '  "business_flow": "# 注册流程\\n1. 用户填写资料\\n2. 提交注册",\n'
        '  "risk_points": {"risks": [{"id": "R1", "description": "邮箱格式校验", "severity": "medium"}]}\n'
        '}'
    ),
    "testcase_agent": (
        '{\n'
        '  "test_cases": {\n'
        '    "cases": [{\n'
        '      "test_case_id": "TC-001",\n'
        '      "requirement_id": "REQ-001",\n'
        '      "title": "用户使用合法资料注册",\n'
        '      "priority": "P0",\n'
        '      "expected_status_codes": [201]\n'
        '    }]\n'
        '  },\n'
        '  "test_points": {\n'
        '    "test_points": [{"id": "TP-1", "requirement_id": "REQ-001", "case_ids": ["TC-001"]}]\n'
        '  },\n'
        '  "test_case_matrix": "test_point,test_case_id,priority\\nTP-1,TC-001,P0",\n'
        '  "coverage_report": "# 覆盖报告\\n- REQ-001: 已覆盖"\n'
        '}'
    ),
}


def build_stage_prompt(
    *,
    agent_name: str,
    role_markdown: str,
    stage_input: str,
    output_requirement: str,
    blocking_conditions: str,
    previous_output: str | None = None,
    template_text: str | None = None,
) -> str:
    previous_output_text = previous_output or "无"
    template_block = template_text.strip() if template_text else "无额外模板要求。"
    return (
        f"你现在进入 {agent_name} 阶段。\n\n"
        "【当前 Agent 职责说明】\n"
        f"{role_markdown.strip()}\n\n"
        "【阶段执行模板】\n"
        f"{template_block}\n\n"
        "【当前阶段输入】\n"
        f"{stage_input.strip()}\n\n"
        "【上一阶段输出】\n"
        f"{previous_output_text.strip()}\n\n"
        "【当前阶段输出要求】\n"
        f"{output_requirement.strip()}\n\n"
        "【当前阶段阻塞条件】\n"
        f"{blocking_conditions.strip()}\n\n"
        "【执行要求】\n"
        "1. 你必须严格遵守当前 Agent 职责说明。\n"
        "2. 你只能完成当前 Agent 职责范围内的任务。\n"
        "3. 你不能越权执行其他 Agent 的职责。\n"
        "4. 如果当前输入不足以完成任务，必须明确阻塞并说明需要补充什么。\n"
        "5. 输出内容必须符合当前阶段要求。\n"
        f"\n{build_llm_output_instruction(agent_name)}"
    )


def build_llm_output_instruction(agent_name: str) -> str:
    schema = _LLM_OUTPUT_SCHEMAS.get(agent_name)
    if not schema:
        return ""

    lines = [
        "【LLM 输出格式要求】\n",
        "你必须以纯 JSON 格式返回结果，不要包含任何解释性文字。",
        "JSON 顶层 key 如下：",
    ]
    for key, desc in schema.items():
        lines.append(f'  "{key}": {desc}')

    example = _LLM_OUTPUT_EXAMPLES.get(agent_name)
    if example:
        lines.extend(["", "【输出示例】", example])

    lines.extend(["", "直接返回 JSON 对象，不要用 markdown 代码块包裹。"])
    return "\n".join(lines)
