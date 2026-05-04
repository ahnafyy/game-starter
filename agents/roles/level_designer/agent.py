from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask


class LevelDesignerAgent(BaseAgent):
    """Places actors, lighting, blocking volumes, and encounters via MCP."""

    role = "level_designer"

    async def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError(
            "LevelDesignerAgent.run() is a stub. "
            "Implement by calling your LLM SDK with self._system_prompt, "
            "then dispatch MCP create_object / modify_object commands."
        )
