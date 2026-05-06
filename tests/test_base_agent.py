from __future__ import annotations

from ai_pipeline.agents import (
    ApiMapperAgent,
    AutomationAgent,
    BaseAgent,
    RequirementAgent,
    TestcaseAgent,
)


class TestBaseAgentInheritance:
    def test_requirement_agent_inherits_base(self):
        agent = RequirementAgent()
        assert isinstance(agent, BaseAgent)

    def test_testcase_agent_inherits_base(self):
        agent = TestcaseAgent()
        assert isinstance(agent, BaseAgent)

    def test_api_mapper_agent_inherits_base(self):
        agent = ApiMapperAgent()
        assert isinstance(agent, BaseAgent)

    def test_automation_agent_inherits_base(self):
        agent = AutomationAgent()
        assert isinstance(agent, BaseAgent)


class TestBaseAgentInterface:
    def test_agent_name_attribute(self):
        for cls in [RequirementAgent, TestcaseAgent, ApiMapperAgent, AutomationAgent]:
            agent = cls()
            assert hasattr(agent, "agent_name")
            assert isinstance(agent.agent_name, str)

    def test_role_profile_returns_dict(self):
        for cls in [RequirementAgent, TestcaseAgent, ApiMapperAgent, AutomationAgent]:
            agent = cls()
            profile = agent.role_profile()
            assert isinstance(profile, dict)
            assert "mission" in profile
            assert "responsibilities" in profile
            assert "forbidden_actions" in profile

    def test_repr(self):
        agent = RequirementAgent()
        assert "RequirementAgent" in repr(agent)
        assert "requirement_agent" in repr(agent)
