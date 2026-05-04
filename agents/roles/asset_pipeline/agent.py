from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask


class AssetPipelineAgent(BaseAgent):
    """Manages placeholder assets, naming conventions, and import validation."""

    role = "asset_pipeline"

    async def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError(
            "AssetPipelineAgent.run() is a stub. "
            "Implement by calling your LLM SDK with self._system_prompt."
        )
