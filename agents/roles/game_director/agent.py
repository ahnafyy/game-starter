from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask


class GameDirectorAgent(BaseAgent):
    """Maintains game vision, design doc, feature scope, and backlog.

    Does not issue MCP commands directly — it produces structured output
    (GDD updates, feature tickets) consumed by other agents.
    """

    role = "game_director"

    async def run(self, task: AgentTask) -> AgentResult:
        # Plug in your LLM call here (Anthropic / OpenAI SDK).
        # The system prompt at prompts/system.md defines the agent's boundaries.
        raise NotImplementedError(
            "GameDirectorAgent.run() is a stub. "
            "Implement by calling your preferred LLM SDK with self._system_prompt."
        )
