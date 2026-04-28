from __future__ import annotations


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
    )
