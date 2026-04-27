from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_api_document(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - optional path
            raise RuntimeError("PyYAML is required to load YAML API documents.") from exc
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    raise ValueError(f"Unsupported API document format: {path}")
