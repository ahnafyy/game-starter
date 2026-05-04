from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import yaml

from agents.shared.contracts import AgentResult, AgentTask


class BaseAgent(ABC):
    """Abstract base for all dev-workflow agents.

    Subclasses must set ``role`` to match the folder name under ``agents/roles/``
    and implement ``run()``.
    """

    role: str = ""

    def __init__(self) -> None:
        if not self.role:
            raise ValueError(
                f"{type(self).__name__} must define a non-empty 'role' class attribute."
            )
        self._config = self._load_config()
        self._system_prompt = self._load_system_prompt()

    # ── Config / prompts ─────────────────────────────────────────────────────

    def _roles_root(self) -> Path:
        return Path(__file__).resolve().parent.parent / "roles"

    def _load_config(self) -> dict:
        config_path = self._roles_root() / self.role / "config.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _load_system_prompt(self) -> str:
        prompt_path = self._roles_root() / self.role / "prompts" / "system.md"
        return prompt_path.read_text()

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def allowed_tools(self) -> list[str]:
        return self._config.get("allowed_tools", [])

    @property
    def model(self) -> str:
        return self._config.get("model", "claude-opus-4-5")

    # ── Interface ─────────────────────────────────────────────────────────────

    @abstractmethod
    async def run(self, task: AgentTask) -> AgentResult:
        """Execute a task and return a structured result."""
        ...
