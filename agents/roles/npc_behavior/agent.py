from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask


class NpcBehaviorAgent(BaseAgent):
    """Designs StateTree / Behavior Tree logic for NPC archetypes."""

    role = "npc_behavior"

    async def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError(
            "NpcBehaviorAgent.run() is a stub. "
            "Implement by calling your LLM SDK with self._system_prompt."
        )
