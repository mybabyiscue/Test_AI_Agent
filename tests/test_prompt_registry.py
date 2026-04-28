from __future__ import annotations

from ai_pipeline.prompt_registry import PromptRegistry


def test_prompt_registry_contains_four_agent_templates():
    registry = PromptRegistry.default()

    expected_roles = {
        "requirement_analyst",
        "testcase_designer",
        "api_mapper",
        "automation_engineer",
    }

    assert set(registry.available_roles()) == expected_roles

    for role_name in expected_roles:
        prompt_path = registry.get(role_name)
        assert prompt_path.exists()
        text = prompt_path.read_text(encoding="utf-8")
        assert "职责由外部注入" in text
        assert "阶段任务" in text
        assert "输出格式要求" in text
