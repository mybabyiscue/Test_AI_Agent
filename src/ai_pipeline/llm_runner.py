from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .artifact_store import StageWorkspace


class LocalPythonLLMRunner:
    backend_name = "local_python_backend"

    def invoke(
        self,
        *,
        stage: StageWorkspace,
        agent_name: str,
        role_markdown_path: Path,
        prompt_template_path: Path,
        prompt: str,
        stage_input: str,
        previous_output: str | None,
        output_requirement: list[str],
        blocking_conditions: list[str],
        execute: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        stage.write_log("llm_prompt.md", prompt)
        stage.write_log_json(
            "llm_invocation.json",
            {
                "agent_name": agent_name,
                "backend": self.backend_name,
                "role_markdown_path": str(role_markdown_path),
                "prompt_template_path": str(prompt_template_path),
                "stage_input": stage_input,
                "previous_output": previous_output or "无",
                "output_requirement": output_requirement,
                "blocking_conditions": blocking_conditions,
            },
        )
        return execute()
