from __future__ import annotations

from ai_pipeline.agents import ApiMapperAgent, AutomationAgent, RequirementAgent, TestcaseAgent
from ai_pipeline.agents.role_profiles import render_role_profile_markdown
from ai_pipeline.prompt_registry import PromptRegistry
from ai_pipeline.role_loader import RoleLoader


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
        assert profile["blocking_conditions"]
        assert profile["role_markdown_path"]
        markdown = render_role_profile_markdown(profile)
        assert markdown.startswith("# ")
        assert "## 职责" in markdown
        assert "## 可读取输入" in markdown
        assert "## 必须输出" in markdown
        assert "## 禁止事项" in markdown
        assert "## 质量门禁" in markdown


def test_prompt_templates_defer_role_definition_to_role_markdown():
    registry = PromptRegistry.default()

    for role_name in registry.available_roles():
        prompt_text = registry.get(role_name).read_text(encoding="utf-8")

        assert "职责由外部注入" in prompt_text
        assert "## 阶段任务" in prompt_text
        assert "## 输出格式要求" in prompt_text
        assert "## 职责" not in prompt_text
        assert "## 可读取输入" not in prompt_text
        assert "## 必须输出" not in prompt_text


def test_role_profile_markdown_renderer_creates_human_readable_agent_card():
    profile = RequirementAgent().role_profile()
    markdown = render_role_profile_markdown(profile)

    assert "# 高级需求分析工程师" in markdown
    assert "## 使命" in markdown
    assert "## 交接规则" in markdown
    assert "- 将原始业务需求转化为可测试、可追踪、可交付的结构化需求工件。" in markdown


def test_role_loader_reads_markdown_as_single_source_of_truth():
    loader = RoleLoader.default()

    profile = loader.load("api_mapper_agent")
    markdown = loader.load_markdown("api_mapper_agent")

    assert profile["title"] == "高级接口上下文获取工程师"
    assert "只针对本次涉及的接口一对一获取详情" in profile["mission"]
    assert "禁止全量拉取整个 Apifox 项目的所有接口详情。" in profile["forbidden_actions"]
    assert "## 阻塞条件" in markdown
    assert profile["role_markdown_path"].replace("\\", "/").endswith("roles/api_mapper_agent.md")
