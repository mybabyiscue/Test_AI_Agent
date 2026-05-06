from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .role_profiles import get_role_profile


class BaseAgent(ABC):
    """Base class for all pipeline agents."""

    agent_name: str

    def role_profile(self) -> dict[str, Any]:
        return get_role_profile(self.agent_name)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute the agent's primary task and return outputs."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(agent_name={self.agent_name!r})"
