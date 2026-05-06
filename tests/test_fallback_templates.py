from __future__ import annotations

from pathlib import Path

from ai_pipeline.fallback_templates import load_template, render_template


class TestLoadTemplate:
    def test_load_existing_template(self):
        template = load_template("requirement_agent", "default")
        assert template is not None
        assert "requirement_model" in template
        assert template["requirement_model"]["requirement_id"] == "REQ-001"

    def test_load_livecode_template(self):
        template = load_template("requirement_agent", "livecode_online_offline")
        assert template is not None
        assert template["requirement_model"]["requirement_id"] == "REQ-SAAS-LIVECODE-ONLINE-OFFLINE-001"
        assert len(template["requirement_model"]["scenarios"]) == 4

    def test_load_nonexistent_template(self):
        template = load_template("requirement_agent", "nonexistent")
        assert template is None

    def test_load_from_nonexistent_agent(self):
        template = load_template("nonexistent_agent", "default")
        assert template is None


class TestRenderTemplate:
    def test_render_with_variables(self):
        result = render_template("requirement_agent", "default", requirement_path="/tmp/test.md")
        assert result is not None
        assert result["requirement_model"]["source_path"] == "/tmp/test.md"

    def test_render_without_variables(self):
        result = render_template("requirement_agent", "livecode_online_offline", requirement_path="/tmp/test.pdf")
        assert result is not None
        assert result["requirement_model"]["source_path"] == "/tmp/test.pdf"

    def test_render_nonexistent_returns_none(self):
        result = render_template("requirement_agent", "nonexistent")
        assert result is None
