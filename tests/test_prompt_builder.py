from __future__ import annotations

from ai_pipeline.prompt_builder import build_stage_prompt


def test_build_stage_prompt_injects_role_markdown_and_stage_context():
    prompt = build_stage_prompt(
        agent_name="testcase_agent",
        role_markdown="# 高级测试用例设计工程师\n\n## 职责\n- 只负责测试用例设计\n",
        stage_input="requirement_model.json: {...}",
        output_requirement="- test_cases.json",
        blocking_conditions="- 输入缺失时必须阻塞",
        previous_output="acceptance_criteria.json: {...}",
        template_text="## 阶段任务\n- 输出结构化测试用例\n",
    )

    assert "你现在进入 testcase_agent 阶段" in prompt
    assert "高级测试用例设计工程师" in prompt
    assert "当前 Agent 职责说明" in prompt
    assert "当前阶段输入" in prompt
    assert "上一阶段输出" in prompt
    assert "当前阶段输出要求" in prompt
    assert "当前阶段阻塞条件" in prompt
    assert "只负责测试用例设计" in prompt
    assert "输出结构化测试用例" in prompt
