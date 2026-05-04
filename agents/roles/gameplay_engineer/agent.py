from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask


class GameplayEngineerAgent(BaseAgent):
    """Writes C++ and Blueprint gameplay logic via MCP + execute_python."""

    role = "gameplay_engineer"

    async def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError(
            "GameplayEngineerAgent.run() is a stub. "
            "Implement by calling your LLM SDK with self._system_prompt, "
            "then dispatch generated MCP commands via MCPClient."
        )
