# Agents

The dev workflow is split across six specialized agents. Each agent has a bounded role — no single agent "builds the game." This mirrors how a real team splits ownership across product, engineering, QA, and platform.

## Agent roles

| Agent | CLI name | Job | MCP tools allowed | Escalates to human when |
|---|---|---|---|---|
| **Game Director** | `game-director` | Game vision, GDD, feature backlog, scope | None (output only) | Scope creep, conflicts |
| **Gameplay Engineer** | `gameplay-engineer` | C++ systems, Blueprint logic | `create_object`, `modify_object`, `execute_python`, `get_scene_info` | Compile error after retry, missing Lyra API |
| **Level Designer** | `level-designer` | Actor placement, lighting, encounters, NavMesh | `create_object`, `modify_object`, `get_scene_info`, `execute_python` | NavMesh rebuild failure, out-of-bounds placement |
| **NPC Behavior** | `npc-behavior` | StateTree / Behavior Tree design for 6 NPC archetypes | `execute_python` | Missing perception config, animation state conflict |
| **QA Playtest** | `qa-playtest` | Scripted gameplay scenario checks, bug reports | `get_scene_info`, `execute_python` | Engine crash (immediate), flaky test (2 failures) |
| **Asset Pipeline** | `asset-pipeline` | Naming convention validation, bulk rename, import manifest | `execute_python` | Duplicate asset, referenced asset rename |

## Running an agent

The Unreal Editor must be open with the UnrealMCP plugin TCP server running before issuing any MCP commands.

```bash
# Start MCP server
uv run tools/mcp-server/server.py

# Run an agent
uv run python -m agents.run --agent <name> --task "<description>"

# Pass additional context as JSON
uv run python -m agents.run \
  --agent level-designer \
  --task "place three spawn points in the starting area" \
  --context '{"area": "start_zone", "count": 3}'
```

Output is a JSON `AgentResult` printed to stdout:

```json
{
  "agent": "level-designer",
  "task": { "description": "place three spawn points in the starting area", "context": {}, "priority": 1 },
  "status": "completed",
  "output": { "actors_placed": ["BP_SpawnPoint_01", "BP_SpawnPoint_02", "BP_SpawnPoint_03"] },
  "mcp_commands_issued": [ ... ],
  "error": null
}
```

## Implementing an agent's `run()` method

All agent stubs raise `NotImplementedError`. To wire up a real LLM:

```python
# agents/roles/level_designer/agent.py
from anthropic import Anthropic

from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import AgentResult, AgentTask, MCPCommand
from agents.shared.mcp_client import MCPClient


class LevelDesignerAgent(BaseAgent):
    role = "level_designer"

    async def run(self, task: AgentTask) -> AgentResult:
        client = Anthropic()
        issued_commands: list[MCPCommand] = []

        # 1. Ask the LLM what MCP commands to run
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self._system_prompt,
            messages=[{"role": "user", "content": task.description}],
        )

        # 2. Parse commands from LLM response (your schema here)
        commands = parse_commands(response.content[0].text)

        # 3. Execute via MCP
        async with MCPClient() as mcp:
            for cmd in commands:
                await mcp.send_command(cmd)
                issued_commands.append(cmd)

        return AgentResult(
            agent=self.role,
            task=task,
            status="completed",
            output={"notes": response.content[0].text},
            mcp_commands_issued=issued_commands,
        )
```

Install the Anthropic SDK:
```bash
uv add anthropic
```

## `config.yaml` schema

Each agent role has a `config.yaml` at `agents/roles/<role>/config.yaml`:

```yaml
role: level-designer           # matches the folder name (kebab-case)
model: claude-opus-4-5         # LLM model to use
allowed_tools:                 # MCP command types this agent may issue
  - create_object
  - modify_object
  - get_scene_info
  - execute_python
description: >                 # human-readable summary
  Places actors in UE maps via MCP.
escalation:                    # escalation conditions (informational — enforce in run())
  on_navmesh_failure: flag to human
  on_out_of_bounds_placement: auto-correct, then flag
```

`BaseAgent` reads this file at instantiation. Access it in `run()` via:
- `self.model` — the model string
- `self.allowed_tools` — list of permitted MCP command types
- `self._config` — the full dict

## Adding a new agent role

1. Create the folder: `agents/roles/<your_role>/`
2. Add three files:
   - `agent.py` — extend `BaseAgent`, set `role = "<your_role>"`, implement `run()`
   - `config.yaml` — fill in `role`, `model`, `allowed_tools`, `description`
   - `prompts/system.md` — LLM system prompt defining boundaries and output format
3. Register in `agents/run.py`:
   ```python
   AGENT_REGISTRY["your-role"] = "agents.roles.your_role.agent"
   ```
4. Add to `agents/__init__.py`:
   ```python
   from agents.roles.your_role.agent import YourRoleAgent
   ```
5. Add a smoke test in `tests/test_agents.py` — it will be picked up automatically by the parametrized tests if you add the class to `ALL_AGENT_CLASSES`
