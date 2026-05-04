# Architecture

## Stack overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Your Mac (code editing + agent orchestration)                      │
│                                                                     │
│   VS Code / Cursor / Claude Desktop                                 │
│         │                                                           │
│         │  MCP protocol (JSON over stdio)                           │
│         ▼                                                           │
│   tools/mcp-server/server.py  ──────────────────────────────────┐  │
│         │                                                        │  │
│   agents/run.py  (CLI)                                           │  │
│         │                                                        │  │
│         ▼                                                        │  │
│   agents/roles/<role>/agent.py  →  agents/shared/mcp_client.py  │  │
└──────────────────────────────────────────────────────────────────┼──┘
                                                                   │
                                              TCP :55557           │
                                                                   │
┌──────────────────────────────────────────────────────────────────┼──┐
│  Shadow PC (Unreal Engine 5.7)                                    │  │
│                                                                   │  │
│   UnrealEditor                                                    │  │
│         │                                                         │  │
│         ▼                                                         │  │
│   UnrealMCP C++ plugin  ◄─────────────────────────────────────────┘  │
│   (Game/Plugins/UnrealMCP/)                                           │
│         │                                                             │
│         ▼                                                             │
│   Unreal Python / Editor subsystems                                   │
│         │                                                             │
│         ├── Actor placement / transforms                              │
│         ├── Blueprint creation / node graph                           │
│         ├── Asset management                                          │
│         └── Automation test runner                                    │
└───────────────────────────────────────────────────────────────────────┘
```


## UE project layout

```
Game/
├── GameStarter.uproject       Project descriptor — pins EngineAssociation: "5.7"
├── Config/
│   ├── DefaultEngine.ini      EngineVersion=5.7.0 (version guard), Lumen settings
│   ├── DefaultGame.ini        Project name / version
│   └── DefaultEditor.ini      Editor performance settings
├── Source/
│   └── GameStarter/
│       ├── GameStarter.Build.cs   Module dependencies (Core, EnhancedInput, GAS, etc.)
│       ├── GameStarter.h          Module header
│       └── GameStarter.cpp        IMPLEMENT_PRIMARY_GAME_MODULE entry point
├── Plugins/
│   └── UnrealMCP/             ← git submodule: chongdashu/unreal-mcp
│       ├── Source/UnrealMCP/  C++ TCP server plugin
│       └── Python/            Python MCP server (unreal_mcp_server.py)
└── Content/                   ← GITIGNORED — Lyra content, local only
```

### What's in Git vs. local only

| Path | In Git | Why |
|---|---|---|
| `Game/GameStarter.uproject` | Yes | Text JSON, version-pinned |
| `Game/Config/` | Yes | Text INI files |
| `Game/Source/` | Yes | C++ source |
| `Game/Plugins/UnrealMCP/` | Yes (submodule) | Plugin source |
| `Game/Content/` | **No** | Binary `.uasset` files, managed via Epic Launcher |
| `Game/Binaries/` | **No** | Build output |
| `Game/Saved/` | **No** | Editor state, logs |

## Agent layer

```
agents/
├── shared/
│   ├── contracts.py       Pydantic v2 models: AgentTask, AgentResult, MCPCommand, MCPResponse
│   ├── mcp_client.py      Async TCP client → UnrealMCP plugin (port 55557)
│   └── base_agent.py      Abstract BaseAgent: loads config.yaml + system prompt
│
└── roles/
    ├── game_director/     Vision, GDD, backlog — no MCP commands
    ├── gameplay_engineer/ C++ + Blueprint logic via execute_python + create_object
    ├── level_designer/    Actor placement via create_object + modify_object
    ├── npc_behavior/      StateTree / Behavior Tree scaffolding via execute_python
    ├── qa_playtest/       Automated scenario checks via execute_python
    └── asset_pipeline/    Naming validation + bulk rename via execute_python
```

### Data flow for a single agent task

```
User CLI call
     │
     ▼
agents/run.py  →  _load_agent("level-designer")
     │
     ▼
LevelDesignerAgent.run(AgentTask)
     │
     ├─ loads prompts/system.md + config.yaml
     ├─ calls LLM SDK (Anthropic / OpenAI) with system prompt + task
     │
     ▼
LLM response → parse → MCPCommand list
     │
     ▼
MCPClient.send_command(MCPCommand)  ──TCP──►  UnrealMCP plugin
     │                                               │
     │                                        executes in UE editor
     │                                               │
     ◄─────────── MCPResponse ──────────────────────┘
     │
     ▼
AgentResult  (printed as JSON to stdout)
```

## MCP protocol

The `chongdashu/unreal-mcp` plugin runs a TCP server on port **55557** inside the UE Editor. Commands are newline-delimited JSON:

**Request:**
```json
{"type": "create_object", "params": {"class_name": "StaticMeshActor", "asset_path": "/Engine/BasicShapes/Cube.Cube", "location": [0, 0, 100], "name": "SM_TestCube"}}
```

**Response:**
```json
{"status": "ok", "result": {"actor_name": "SM_TestCube", "location": [0, 0, 100]}}
```

Available command types (from chongdashu/unreal-mcp):

| Command | What it does |
|---|---|
| `get_scene_info` | List all actors in the current level |
| `create_object` | Spawn a new actor |
| `delete_object` | Remove an actor |
| `modify_object` | Change transform / properties |
| `execute_python` | Run arbitrary Unreal Python in the editor |
| `create_blueprint` | Create a new Blueprint class |
| `set_blueprint_property` | Set a Blueprint variable |
| `focus_viewport` | Move the editor camera |

## UE version guard

`Game/Config/DefaultEngine.ini` contains:

```ini
[Core.System]
EngineVersion=5.7.0
```

`Game/GameStarter.uproject` contains:

```json
"EngineAssociation": "5.7"
```

**Why both?** The `.uproject` association is the hard guard — UE refuses to open the project in a mismatched engine without prompting. The `DefaultEngine.ini` entry is the audit trail — if someone opens the project in UE 5.8 and re-saves, this line changes in the Git diff. That's your signal to treat it as a breaking change requiring a migration plan before merging.

## CI/CD

```
Push to main / PR
       │
       ├─ touches agents/ or tests/  ──► agent-tests.yml
       │                                   • ruff lint
       │                                   • pytest (29 tests)
       │
       └─ touches Game/              ──► ue-automation.yml (self-hosted macOS runner)
                                          • build (Development Editor)
                                          • run UE Automation Tests (GameStarter.*)
                                          • upload results artifact
```

The UE automation workflow requires a **self-hosted GitHub Actions runner** on a machine with UE 5.7 installed. To register one:
`GitHub repo → Settings → Actions → Runners → New self-hosted runner`
Label it: `self-hosted`, `macos`, `unreal`
