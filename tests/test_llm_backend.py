from __future__ import annotations

import json
import os

from ai_pipeline.llm_backend import FallbackBackend, LLMConfig, _extract_json, create_backend, load_llm_config


class TestExtractJson:
    def test_raw_json(self):
        assert _extract_json('{"a": 1}') == {"a": 1}

    def test_json_in_text(self):
        assert _extract_json('Here is the result: {"a": 1} done') == {"a": 1}

    def test_markdown_code_fence_json(self):
        assert _extract_json('```json\n{"a": 1}\n```') == {"a": 1}

    def test_markdown_code_fence_without_json_tag(self):
        assert _extract_json('```\n{"a": 1}\n```') == {"a": 1}

    def test_multiple_json_objects_takes_largest(self):
        text = '{"small": 1} some text {"large": {"nested": true, "value": 42}}'
        result = _extract_json(text)
        assert result == {"large": {"nested": True, "value": 42}}

    def test_non_dict_json_returns_none(self):
        assert _extract_json("[1, 2, 3]") is None

    def test_no_json_returns_none(self):
        assert _extract_json("no json here") is None

    def test_nested_json(self):
        text = 'Result: {"data": {"items": [1, 2, 3]}, "count": 3}'
        result = _extract_json(text)
        assert result == {"data": {"items": [1, 2, 3]}, "count": 3}

    def test_json_with_special_characters(self):
        text = '{"message": "你好世界", "code": 0}'
        result = _extract_json(text)
        assert result == {"message": "你好世界", "code": 0}


class TestCreateBackend:
    def test_fallback_when_disabled(self, monkeypatch):
        monkeypatch.setenv("AI_PIPELINE_LLM_ENABLED", "0")
        backend = create_backend()
        assert isinstance(backend, FallbackBackend)

    def test_fallback_when_no_config(self, monkeypatch):
        monkeypatch.delenv("AI_PIPELINE_LLM_ENABLED", raising=False)
        monkeypatch.setenv("AI_PIPELINE_LLM_API_KEY", "")
        monkeypatch.setenv("AI_PIPELINE_LLM_BASE_URL", "")
        # Patch load_llm_config to return None
        monkeypatch.setattr("ai_pipeline.llm_backend.load_llm_config", lambda: None)
        backend = create_backend()
        assert isinstance(backend, FallbackBackend)


class TestLLMConfig:
    def test_default_values(self):
        config = LLMConfig(base_url="https://api.example.com", api_key="test-key", model="test-model")
        assert config.max_tokens == 8192
        assert config.timeout == 10.0

    def test_custom_values(self):
        config = LLMConfig(base_url="https://api.example.com", api_key="test-key", model="test-model", max_tokens=4096, timeout=30.0)
        assert config.max_tokens == 4096
        assert config.timeout == 30.0


class TestFallbackBackend:
    def test_invoke_returns_none(self):
        backend = FallbackBackend()
        assert backend.invoke("test prompt") is None

    def test_invoke_json_returns_none(self):
        backend = FallbackBackend()
        assert backend.invoke_json("test prompt") is None
