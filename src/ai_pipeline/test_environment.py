from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import project_root


def default_test_environment_path() -> Path:
    return project_root() / "config" / "test_environment.local.json"


def load_test_environment(profile: str, config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or default_test_environment_path()
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return dict(payload.get("environments", {}).get(profile, {}))
