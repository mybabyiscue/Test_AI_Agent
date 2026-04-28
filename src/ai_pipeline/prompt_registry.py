from __future__ import annotations

from pathlib import Path

from .config import prompts_root


AGENT_PROMPT_NAMES: dict[str, str] = {
    "requirement_agent": "requirement_analyst",
    "testcase_agent": "testcase_designer",
    "api_mapper_agent": "api_mapper",
    "automation_agent": "automation_engineer",
}


class PromptRegistry:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._prompts = {
            "requirement_analyst": self._root / "requirement_analyst.md",
            "testcase_designer": self._root / "testcase_designer.md",
            "api_mapper": self._root / "api_mapper.md",
            "automation_engineer": self._root / "automation_engineer.md",
        }

    @classmethod
    def default(cls) -> "PromptRegistry":
        return cls(prompts_root())

    def available_roles(self) -> list[str]:
        return list(self._prompts.keys())

    def get(self, role_name: str) -> Path:
        return self._prompts[role_name]

    def get_for_agent(self, agent_name: str) -> Path:
        return self.get(AGENT_PROMPT_NAMES[agent_name])
