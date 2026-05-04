"""Thin launcher for the chongdashu/unreal-mcp Python MCP server.

The actual server lives in the UnrealMCP git submodule:
  Game/Plugins/UnrealMCP/Python/unreal_mcp_server.py

This launcher exists so mcp.json always points to a stable, repo-relative path
regardless of where the submodule content moves internally.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MCP_SERVER = REPO_ROOT / "Game" / "Plugins" / "UnrealMCP" / "Python" / "unreal_mcp_server.py"


def main() -> None:
    if not MCP_SERVER.exists():
        print(
            f"ERROR: MCP server not found at {MCP_SERVER}\n"
            "Did you run scripts/setup.sh to initialize submodules?",
            file=sys.stderr,
        )
        sys.exit(1)

    subprocess.run([sys.executable, str(MCP_SERVER)], check=True)


if __name__ == "__main__":
    main()
