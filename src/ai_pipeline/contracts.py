from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PipelineRunResult:
    run_id: str
    run_dir: Path
    manifest_path: Path
    status: str = "success"
    blocked_stage: str | None = None
    blocking_report_path: Path | None = None
