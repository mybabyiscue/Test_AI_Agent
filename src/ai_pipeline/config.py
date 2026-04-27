from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def prompts_root() -> Path:
    return project_root() / "prompts"


def schemas_root() -> Path:
    return project_root() / "schemas"


def examples_root() -> Path:
    return project_root() / "examples"
