#!/usr/bin/env bash
# setup.sh — One-command bootstrap for the game-starter repo.
# Run once after cloning: bash scripts/setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "================================================================"
echo " game-starter setup"
echo "================================================================"
echo ""

# ── 1. Submodules ────────────────────────────────────────────────────
echo "==> Initializing git submodules..."
git submodule update --init --recursive --depth 1
echo "    Done."
echo ""

# ── 2. Python / uv ──────────────────────────────────────────────────
echo "==> Checking for uv..."
if ! command -v uv &>/dev/null; then
    echo "    uv not found — installing via pip..."
    pip install uv
fi
echo "    uv: $(uv --version)"
echo ""

echo "==> Syncing Python dependencies..."
uv sync --dev
echo "    Done."
echo ""

# ── 3. mcp.json ──────────────────────────────────────────────────────
echo "==> Configuring mcp.json..."
if [ ! -f "$REPO_ROOT/mcp.json" ]; then
    cp "$REPO_ROOT/mcp.json.template" "$REPO_ROOT/mcp.json"
    # macOS sed requires an empty string argument for -i
    sed -i '' "s|<ABSOLUTE_PATH_TO_REPO>|$REPO_ROOT|g" "$REPO_ROOT/mcp.json"
    echo "    Created mcp.json and filled in repo path: $REPO_ROOT"
else
    echo "    mcp.json already exists — skipping."
fi
echo ""

# ── 4. Validate UE plugin submodule ──────────────────────────────────
MCP_PLUGIN="$REPO_ROOT/Game/Plugins/UnrealMCP"
if [ -f "$MCP_PLUGIN/Python/unreal_mcp_server.py" ]; then
    echo "==> UnrealMCP plugin submodule: OK"
else
    echo "    WARNING: UnrealMCP Python server not found at $MCP_PLUGIN/Python/"
    echo "    Try: git submodule update --init --recursive"
fi
echo ""

# ── 5. Next steps ────────────────────────────────────────────────────
echo "================================================================"
echo " Setup complete! Next steps:"
echo "================================================================"
echo ""
echo "  1. Open UE project (requires UE 5.5):"
echo "     open Game/GameStarter.uproject"
echo "     Then: right-click .uproject → Generate Xcode project files"
echo "     Then: build in Xcode (Development Editor target)"
echo ""
echo "  2. Enable the UnrealMCP plugin in UE Editor:"
echo "     Edit → Plugins → search 'UnrealMCP' → Enable → Restart"
echo ""
echo "  3. Lyra content is NOT in this repo."
echo "     Copy your Lyra project's Content/ into Game/Content/"
echo "     (download Lyra via Epic Games Launcher → Library)"
echo ""
echo "  4. Start the MCP server:"
echo "     uv run tools/mcp-server/server.py"
echo ""
echo "  5. Run an agent:"
echo "     uv run python -m agents.run --agent game-director --task 'describe the game'"
echo ""
echo "  6. Configure your MCP client (Claude Desktop / Cursor / Windsurf):"
echo "     Config file written to: $REPO_ROOT/mcp.json"
echo "     Cursor:        .cursor/mcp.json"
echo "     Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "     Windsurf:       ~/.codeium/windsurf/mcp_config.json"
echo ""
