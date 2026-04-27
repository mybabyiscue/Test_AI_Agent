from __future__ import annotations

from ai_pipeline.agents import ApiMapperAgent, AutomationAgent, RequirementAgent, TestcaseAgent
from ai_pipeline.agents.role_profiles import render_role_profile_markdown
from ai_pipeline.prompt_registry import PromptRegistry


def test_each_agent_exposes_strict_chinese_senior_engineer_profile():
    agents = [
        RequirementAgent(),
        TestcaseAgent(),
        ApiMapperAgent(),
        AutomationAgent(),
    ]

    for agent in agents:
        profile = agent.role_profile()

        assert profile["title"].startswith("高级")
        assert profile["language"] == "中文"
        assert profile["strict_mode"] is True
        assert profile["responsibilities"]
        assert profile["input_contract"]
        assert profile["output_contract"]
        assert profile["forbidden_actions"]
        assert profile["quality_gates"]
        markdown = render_role_profile_markdown(profile)
        assert markdown.startswith("# ")
        assert "## 职责" in markdown
        assert "## 输入" in markdown
        assert "## 输出" in markdown
        assert "## 禁止" in markdown
        assert "## 质量门禁" in markdown


def test_prompt_templates_are_chinese_and_strict():
    registry = PromptRegistry.default()

    for role_name in registry.available_roles():
        prompt_text = registry.get(role_name).read_text(encoding="utf-8")

        assert "高级工程师" in prompt_text
        assert "职责" in prompt_text
        assert "输入" in prompt_text
        assert "输出" in prompt_text
        assert "严格要求" in prompt_text
        assert "禁止" in prompt_text


def test_role_profile_markdown_renderer_creates_human_readable_agent_card():
    profile = RequirementAgent().role_profile()
    markdown = render_role_profile_markdown(profile)

    assert "# 高级需求分析工程师" in markdown
    assert "## 使命" in markdown
    assert "## 交接规则" in markdown
    assert "- 将原始业务需求转化为可测试、可追踪、可交付的结构化需求工件。" in markdown
