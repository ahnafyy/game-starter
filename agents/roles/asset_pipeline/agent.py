from __future__ import annotations

import json
import os

from openai import OpenAI

from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask, MCPCommand
from agents.shared.mcp_client import MCPClient

# Provider configuration via environment variables.
# Defaults target GitHub Models — swap base_url + key for OpenAI, Groq, or Ollama.
#
# GitHub Models (free, needs GITHUB_TOKEN):
#   LLM_BASE_URL=https://models.inference.ai.azure.com
#   LLM_API_KEY=<your GitHub PAT>
#   LLM_MODEL=gpt-4o-mini  (or openai/gpt-4.1, meta/llama-4-scout, etc.)
#
# OpenAI:  LLM_BASE_URL=https://api.openai.com/v1  LLM_API_KEY=sk-...
# Groq:    LLM_BASE_URL=https://api.groq.com/openai/v1  LLM_API_KEY=gsk_...
# Ollama:  LLM_BASE_URL=http://localhost:11434/v1  LLM_API_KEY=ollama

_DEFAULT_BASE_URL = "https://models.inference.ai.azure.com"
_DEFAULT_MODEL = "gpt-4o-mini"


class AssetPipelineAgent(BaseAgent):
    """Manages placeholder assets, naming conventions, and import validation."""

    role = "asset_pipeline"

    async def run(self, task: AgentTask) -> AgentResult:
        client = OpenAI(
            api_key=os.environ.get("LLM_API_KEY") or os.environ["GITHUB_TOKEN"],
            base_url=os.environ.get("LLM_BASE_URL", _DEFAULT_BASE_URL),
        )
        model = os.environ.get("LLM_MODEL", self.model)
        issued_commands: list[MCPCommand] = []

        # Ask the LLM which Python snippet to run against the Unreal asset library
        response = client.chat.completions.create(
            model=model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Task: {task.description}\n"
                        f"Context: {json.dumps(task.context)}\n\n"
                        "Reply with a JSON object: "
                        '{"python_snippet": "<unreal python code>", "reasoning": "<brief>"}'
                    ),
                },
            ],
        )

        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        python_snippet: str = parsed["python_snippet"]

        cmd = MCPCommand(type="execute_python", params={"code": python_snippet})
        issued_commands.append(cmd)

        async with MCPClient() as mcp:
            mcp_response = await mcp.send_command(cmd)

        if mcp_response.status == "error":
            return AgentResult(
                agent=self.role,
                task=task,
                status="blocked",
                output=mcp_response.result,
                mcp_commands_issued=issued_commands,
                error=mcp_response.error,
            )

        return AgentResult(
            agent=self.role,
            task=task,
            status="completed",
            output=mcp_response.result,
            mcp_commands_issued=issued_commands,
        )
