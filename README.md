<div align="center">

# 🎮 game-starter

**Production-grade Unreal Engine 5.7 game template**  
Built on Lyra · driven by a 6-agent AI dev workflow · controlled via MCP

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Unreal Engine 5.7](https://img.shields.io/badge/Unreal_Engine-5.7-313131?style=flat-square&logo=unrealengine&logoColor=white)](https://unrealengine.com)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=flat-square)](https://docs.astral.sh/uv/)
[![MCP](https://img.shields.io/badge/MCP-protocol-FF6B35?style=flat-square)](https://modelcontextprotocol.io)
[![CI](https://img.shields.io/github/actions/workflow/status/ahnafyy/game-starter/agent-tests.yml?style=flat-square&label=agent%20tests)](https://github.com/ahnafyy/game-starter/actions/workflows/agent-tests.yml)

</div>

Lyra provides the gameplay framework — abilities, input, UI, multiplayer patterns, modular game modes. The agents handle development automation. **Replace the game concept with your own.**

## 📦 What's in this repo

| Layer | What | Where |
|---|---|---|
| 🎮 UE project stub | `.uproject`, `Config/`, `Source/` | `Game/` |
| 🔌 Unreal MCP plugin | chongdashu/unreal-mcp (git submodule) | `Game/Plugins/UnrealMCP/` |
| 🤖 Python agent layer | 6 dev agents + shared MCP client | `agents/` |
| 🛠️ Dev tools | Build, test, package scripts | `tools/` |
| ⚙️ CI | GitHub Actions (Python lint/test + UE automation) | `.github/workflows/` |

> **⚠️ Lyra content is NOT in this repo.** The `Game/Content/` folder is gitignored. You download Lyra separately via the Epic Games Launcher and copy it in locally. See [docs/setup.md](docs/setup.md).

## 🤖 Six-agent dev workflow

```mermaid
graph TD
    H(["👤 Human"])

    GD["🎯 Game Director\ngame-director"]
    GE["⚙️ Gameplay Engineer\ngameplay-engineer"]
    LD["🗺️ Level Designer\nlevel-designer"]
    NPC["🧠 NPC Behavior\nnpc-behavior"]
    QA["🔍 QA Playtest\nqa-playtest"]
    AP["📁 Asset Pipeline\nasset-pipeline"]

    MCP[["⚡ MCP Server\nTCP :55557"]]
    UE[("🎮 Unreal Editor")]

    H -->|task| GD
    GD -->|design specs| GE & LD & NPC & QA & AP
    GE -->|create_object · execute_python| MCP
    LD -->|create_object · modify_object| MCP
    NPC -->|execute_python| MCP
    QA -->|get_scene_info · execute_python| MCP
    AP -->|execute_python| MCP
    MCP <-->|"JSON over TCP"| UE
```

## 🏗️ Architecture

```mermaid
flowchart LR
    subgraph mac["💻 Your Machine"]
        AI["🤖 AI Client\nCursor · Claude Desktop"]
        CLI["agents/run.py"]
        SRV["tools/mcp-server/server.py"]
    end

    subgraph shadow["🖥️ Shadow PC"]
        PLUGIN["UnrealMCP C++ Plugin\nTCP :55557"]
        PY["Unreal Python\nEditor APIs"]
        UE["🎮 UnrealEditor"]
    end

    AI -->|"MCP stdio"| SRV
    CLI --> SRV
    SRV -->|"TCP :55557"| PLUGIN
    PLUGIN --> PY --> UE
```

## ⚡ Prerequisites

| | Requirement | Version | Notes |
|---|---|---|---|
| 🎮 | Unreal Engine | 5.7 | Via Epic Games Launcher — [docs/setup.md](docs/setup.md) |
| 🐍 | Python | 3.12+ | |
| 📦 | uv | latest | `pip install uv` |
| 🔀 | Git | 2.x | With submodule support |
| 🖥️ | Shadow PC or capable machine | — | UE 5.7 is too heavy for MacBook Air |

## 🚀 Quick start

```bash
# 1. Clone
git clone git@github.com:ahnafyy/game-starter.git
cd game-starter

# 2. Bootstrap (submodules + Python venv + mcp.json)
bash scripts/setup.sh

# 3. Open the UE project (requires UE 5.7 installed)
#    Right-click Game/GameStarter.uproject → Generate Xcode/VS project files
#    Then build with Development Editor target
```

After the UE project builds, enable the **UnrealMCP** plugin:
`Edit → Plugins → search "UnrealMCP" → Enable → Restart Editor`

## 🎮 Running an agent

```bash
# Start the MCP server (Unreal Editor must be open and MCP plugin running)
uv run tools/mcp-server/server.py

# In another terminal, run any agent
uv run python -m agents.run --agent game-director   --task "describe the core gameplay loop"
uv run python -m agents.run --agent level-designer  --task "place a spawn point in the starting area"
uv run python -m agents.run --agent qa-playtest     --task "verify the player spawns correctly"
```

Available agents: `game-director` · `gameplay-engineer` · `level-designer` · `npc-behavior` · `qa-playtest` · `asset-pipeline`

See [docs/agents.md](docs/agents.md) for the full reference.

## 🗂️ Repo structure

```
game-starter/
├── Game/
│   ├── GameStarter.uproject        UE 5.7 project descriptor
│   ├── Config/                     DefaultEngine.ini (version-pinned), DefaultGame.ini, DefaultEditor.ini
│   ├── Source/GameStarter/         C++ module shell (Build.cs, .h, .cpp)
│   └── Plugins/UnrealMCP/          ← git submodule: chongdashu/unreal-mcp
│
├── agents/
│   ├── shared/                     mcp_client.py, base_agent.py, contracts.py
│   ├── roles/                      6 agent roles (game_director, gameplay_engineer, ...)
│   │   └── <role>/
│   │       ├── agent.py            extend BaseAgent, implement run()
│   │       ├── config.yaml         role, model, allowed_tools, escalation
│   │       └── prompts/system.md   LLM system prompt
│   └── run.py                      CLI entry point
│
├── tools/
│   ├── mcp-server/server.py        Launches the UnrealMCP Python server
│   ├── ue-command-scripts/         build.sh, run-automation-tests.sh, package.sh
│   └── validation-scripts/         validate_assets.py
│
├── tests/                          pytest suite (29 tests)
├── scripts/setup.sh                one-command bootstrap
├── mcp.json.template               MCP client config template (filled in by setup.sh)
├── .github/workflows/
│   ├── agent-tests.yml             ruff + pytest on push/PR
│   └── ue-automation.yml           UE headless automation tests (self-hosted runner)
└── pyproject.toml
```

## 🔧 Development setup

Full step-by-step for Shadow PC (recommended) and native Mac: [docs/setup.md](docs/setup.md)

## 🍎 Playing on your Mac after MVP

Once development is done on Shadow PC, you package the game and run the `.app` on your Mac — no UE install required. See [docs/playing-on-mac.md](docs/playing-on-mac.md).

## ✅ CI

| Workflow | Trigger | What it does |
|---|---|---|
| `agent-tests.yml` | push / PR touching `agents/` or `tests/` | ruff lint + pytest |
| `ue-automation.yml` | push / PR touching `Game/` | build + UE Automation Tests (self-hosted macOS runner) |
