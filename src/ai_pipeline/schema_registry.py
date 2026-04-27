from __future__ import annotations

from pathlib import Path

from .config import schemas_root


class SchemaRegistry:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._schemas = {
            "requirement_model": self._root / "requirement_model.schema.json",
            "test_cases": self._root / "test_cases.schema.json",
            "endpoint_mapping": self._root / "endpoint_mapping.schema.json",
            "automation_plan": self._root / "automation_plan.schema.json",
            "execution_report": self._root / "execution_report.schema.json",
        }

    @classmethod
    def default(cls) -> "SchemaRegistry":
        return cls(schemas_root())

    def available_names(self) -> list[str]:
        return list(self._schemas.keys())

    def get(self, schema_name: str) -> Path:
        return self._schemas[schema_name]
