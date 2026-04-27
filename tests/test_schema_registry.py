from __future__ import annotations

import json

from ai_pipeline.schema_registry import SchemaRegistry


def test_schema_registry_contains_required_schemas():
    registry = SchemaRegistry.default()

    expected_names = {
        "requirement_model",
        "test_cases",
        "endpoint_mapping",
        "automation_plan",
        "execution_report",
    }

    assert set(registry.available_names()) == expected_names

    for schema_name in expected_names:
        schema_path = registry.get(schema_name)
        assert schema_path.exists()

        payload = json.loads(schema_path.read_text(encoding="utf-8"))
        assert payload["type"] == "object"
