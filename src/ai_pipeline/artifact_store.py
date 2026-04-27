from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ArtifactStore:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir

    def write_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        target = self.run_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def write_text(self, relative_path: str, content: str) -> Path:
        target = self.run_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, agent_name: str, event: str, **details: Any) -> None:
        payload = {
            "timestamp": utc_now_iso(),
            "agent_name": agent_name,
            "event": event,
            "details": details,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


@dataclass(slots=True)
class StageWorkspace:
    run_id: str
    run_dir: Path
    agent_name: str
    event_log: EventLog
    root: Path = field(init=False)
    input_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    state_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.root = self.run_dir / self.agent_name
        self.input_dir = self.root / "input"
        self.output_dir = self.root / "output"
        self.logs_dir = self.root / "logs"
        self.state_path = self.root / "state.json"
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def copy_input(self, source: Path, relative_path: str | None = None) -> Path:
        target_name = relative_path or source.name
        target = self.input_dir / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        return target

    def write_input_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        return self._write_json(self.input_dir / relative_path, payload)

    def write_output_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        return self._write_json(self.output_dir / relative_path, payload)

    def write_output_text(self, relative_path: str, content: str) -> Path:
        target = self.output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def write_log(self, filename: str, content: str) -> Path:
        target = self.logs_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def update_state(
        self,
        *,
        status: str,
        input_files: list[str],
        output_files: list[str],
        prompt_version: str = "mvp-v1",
        error_message: str | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
        executor: dict[str, Any] | None = None,
        role_profile: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "agent_name": self.agent_name,
            "run_id": self.run_id,
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "input_files": input_files,
            "output_files": output_files,
            "prompt_version": prompt_version,
            "error_message": error_message,
            "executor": executor,
            "role_profile": role_profile,
        }
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_json(self, target: Path, payload: dict[str, Any]) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target
