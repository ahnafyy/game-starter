from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask


class QaPlaytestAgent(BaseAgent):
    """Runs repeatable gameplay checks and produces bug reports."""

    role = "qa_playtest"

    async def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError(
            "QaPlaytestAgent.run() is a stub. "
            "Implement by calling your LLM SDK with self._system_prompt."
        )
