from __future__ import annotations

from ai_pipeline.agents import ApiMapperAgent


def test_api_mapper_profile_requires_expanding_incomplete_document_interfaces():
    profile = ApiMapperAgent().role_profile()
    text = "\n".join(
        [
            *profile["responsibilities"],
            *profile["quality_gates"],
            *profile["handoff_rules"],
        ]
    )

    assert "文档中已出现接口但信息不完整" in text
    assert "Agent 2" in text
    assert "候选接口" in text
    assert "主接口、前置接口、验证接口、清理接口和依赖接口" in text
