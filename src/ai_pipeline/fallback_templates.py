from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base" / "fallback_templates"


def load_template(agent_name: str, template_name: str) -> dict[str, Any] | None:
    template_path = _TEMPLATES_DIR / agent_name / f"{template_name}.json"
    if not template_path.exists():
        return None
    try:
        return json.loads(template_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def render_template(agent_name: str, template_name: str, **variables: str) -> dict[str, Any] | None:
    template = load_template(agent_name, template_name)
    if template is None:
        return None
    return _render_value(template, variables)


def _render_value(value: Any, variables: dict[str, str]) -> Any:
    if isinstance(value, str):
        for key, replacement in variables.items():
            value = value.replace(f"{{{key}}}", replacement)
        return value
    if isinstance(value, dict):
        return {k: _render_value(v, variables) for k, v in value.items()}
    if isinstance(value, list):
        return [_render_value(item, variables) for item in value]
    return value
