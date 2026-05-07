# Setup Guide

Two paths depending on your machine. **Shadow PC is recommended** — Unreal Engine 5.7 is too resource-heavy for a MacBook Air.

## Path A: Shadow PC (recommended)

### 1. Get a Shadow PC

1. Sign up at **[eu.shadow.tech](https://eu.shadow.tech/)** → choose the **Shadow** plan (~$29.99/mo)
2. Download the Shadow app on your Mac
3. Download and install **[Parsec](https://parsec.app)** on your Mac AND on the Shadow PC — use Parsec instead of the Shadow client for better latency when working in the UE viewport

### 2. On the Shadow PC — install Epic Games Launcher + Lyra

1. Go to [unrealengine.com/download](https://www.unrealengine.com/en-US/download) and download the Epic Games Launcher
2. Install it and sign in with a free Epic account
3. In the Launcher: **Unreal Engine** tab → **Library** → click **+** next to Engine Versions → select **5.7** → Install
   - UE 5.7 install is ~30–40GB, let it run
4. In the Launcher: **Unreal Engine** tab → **Samples** → find **Lyra Starter Game** → Create Project
   - Install it somewhere like `C:\UnrealProjects\LyraStarterGame`
   - You'll copy the `Content/` folder and required plugins from here into the game-starter repo in step 6

### 3. On the Shadow PC — clone this repo

Install Git if not present: [git-scm.com](https://git-scm.com/download/win)

```bash
git clone git@github.com:ahnafyy/game-starter.git
cd game-starter
```

### 4. Install Visual Studio 2022

1. Download [Visual Studio 2022 Community](https://visualstudio.microsoft.com/vs/community/) (free)
2. In the installer, select the **"Game development with C++"** workload
3. Complete the install (~15GB)

This is required to compile the `GameStarter` and `UnrealMCP` C++ modules.

### 5. Install Python + uv

Install Python 3.12 from [python.org](https://www.python.org/downloads/) then:

```bash
pip install uv
```

### 6. Run setup

```bash
bash scripts/setup.sh
```

This will:
- Initialize the `chongdashu/unreal-mcp` git submodule
- Create a Python virtual environment and install dependencies
- Generate `mcp.json` with the correct absolute paths

### 7. Copy Lyra content and plugins into the repo

These files are gitignored (Epic EULA prohibits redistribution) so they must be copied locally on every machine.

```powershell
# Replace <LyraPath> with where you installed Lyra in step 2 (e.g. C:\UnrealProjects\LyraStarterGame)
$lyra = "C:\UnrealProjects\LyraStarterGame"
$repo = "C:\Users\Shadow\appdev\repos\game-starter\Game"

# Game content (maps, assets, blueprints)
xcopy "$lyra\Content" "$repo\Content" /E /I /Y

# Lyra plugins required by GameStarter.uproject
xcopy "$lyra\Plugins\CommonGame"            "$repo\Plugins\CommonGame"            /E /I /Y
xcopy "$lyra\Plugins\CommonUser"            "$repo\Plugins\CommonUser"            /E /I /Y
xcopy "$lyra\Plugins\GameplayMessageRouter" "$repo\Plugins\GameplayMessageRouter" /E /I /Y
xcopy "$lyra\Plugins\ModularGameplayActors" "$repo\Plugins\ModularGameplayActors" /E /I /Y
```

`Game/Content/` and the four plugin folders are all gitignored — they stay local only.

### 8. Build the project

Run this from PowerShell (no need to open Visual Studio):

```powershell
& "C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" GameStarterEditor Win64 Development "$PWD\Game\GameStarter.uproject" -waitmutex
```

This compiles `GameStarter` and `UnrealMCP` (~2–5 min). You should see `Result: Succeeded`.

### 9. Open the UE project

Double-click `Game/GameStarter.uproject` — UE Editor will launch directly (no rebuild prompt).

### 10. Enable the UnrealMCP plugin

In the UE Editor: **Edit → Plugins** → search `UnrealMCP` → **Enable** → restart when prompted

### 11. Set UE_ROOT (for scripts)

In your shell / System Environment Variables:

```bash
# Git Bash / PowerShell
set UE_ROOT=C:\Program Files\Epic Games\UE_5.7
# or
$env:UE_ROOT = "C:\Program Files\Epic Games\UE_5.7"
```

## Path B: Native Mac (future — when you have a capable machine)

Follow the same steps as Path A but:

- Skip Shadow PC — everything runs locally
- UE install path is `/Users/Shared/Epic Games/UE_5.7` by default (what the scripts expect)
- Generate **Xcode** project files instead of Visual Studio:
  ```bash
  "/Users/Shared/Epic Games/UE_5.7/Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh" \
    -project="$(pwd)/Game/GameStarter.uproject" -game
  open Game/GameStarter.xcworkspace
  ```
- Build target in Xcode: **GameStarterEditor | My Mac | Development**

## MCP client configuration

### VS Code (recommended)

The repo ships a `.vscode/mcp.json` that wires the MCP server directly into VS Code Copilot — no manual config needed. Open the project in VS Code and the server starts automatically when you use an agent.

Six custom agents are available in `.github/agents/` and appear in the Copilot agent picker:

| Agent | Role |
|---|---|
| **Game Director** | GDD, feature backlog, scope decisions |
| **Gameplay Engineer** | C++ / Blueprint implementation via MCP |
| **Level Designer** | Actor placement, lighting, navmesh via MCP |
| **NPC Behavior** | StateTree / AI scaffolding via MCP |
| **QA Playtest** | Automated tests and bug reports via MCP |
| **Asset Pipeline** | Naming audits and bulk renames via MCP |

> **Note:** When using VS Code Copilot as your AI client, `GITHUB_TOKEN` / `LLM_API_KEY` in `.env` are **not required** — those are only used by the Python CLI (`agents/run.py`). The VS Code agents call MCP tools directly through Copilot.

### Other AI clients

`setup.sh` generates `mcp.json` in the repo root with correct absolute paths. Copy the contents into your client's config:

| Client | Config file location |
|---|---|
| **Cursor** | `.cursor/mcp.json` in your project root |
| **Claude Desktop (Mac)** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Desktop (Windows)** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |

The MCP server (`tools/mcp-server/server.py`) must be running AND the UnrealMCP plugin TCP server must be started from the UE Editor toolbar before your AI client can issue Unreal commands.

## Troubleshooting

**`git submodule update` fails / UnrealMCP folder is empty**
```bash
git submodule update --init --recursive --depth 1
```

**`uv` not found**
```bash
pip install uv
# then re-run
bash scripts/setup.sh
```

**UE project won't open / "engine version mismatch"**
Right-click `Game/GameStarter.uproject` → **Switch Unreal Engine version** → pick **5.7**

**UnrealMCP plugin fails to compile**
The submodule has been patched for UE 5.7 (`ANY_PACKAGE` → `nullptr`, C4459 warning suppressed). If you still see compile errors, make sure the submodule is fully initialized: `git submodule update --init --recursive`.

**UE project says "plugin could not be found" for CommonGame or GameplayMessageRouter**
These are Lyra plugins — not part of the base engine install. Copy them from your Lyra Starter Game project (see step 6 above). If you haven't installed Lyra yet: Epic Games Launcher → Unreal Engine → Samples → Lyra Starter Game → Create Project.

**`mcp.json` has wrong path**
Delete it and re-run `bash scripts/setup.sh` — it regenerates with the correct absolute path.
