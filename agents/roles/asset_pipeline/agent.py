from __future__ import annotations

import json
import os

import anthropic

from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask, MCPCommand
from agents.shared.mcp_client import MCPClient


class AssetPipelineAgent(BaseAgent):
    """Manages placeholder assets, naming conventions, and import validation."""

    role = "asset_pipeline"

    async def run(self, task: AgentTask) -> AgentResult:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        issued_commands: list[MCPCommand] = []

        # Ask the LLM which Python snippet to run against the Unreal asset library
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self._system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Task: {task.description}\n"
                        f"Context: {json.dumps(task.context)}\n\n"
                        "Reply with a JSON object: "
                        '{"python_snippet": "<unreal python code>", "reasoning": "<brief>"}'
                    ),
                }
            ],
        )

        raw = response.content[0].text.strip()
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
