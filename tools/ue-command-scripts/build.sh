#!/usr/bin/env bash
# build.sh — Build the GameStarter UE project (Development Editor, macOS).
# Usage: bash tools/ue-command-scripts/build.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_FILE="$REPO_ROOT/Game/GameStarter.uproject"

# ── Locate UE 5.5 ────────────────────────────────────────────────────────────
UE_ROOT="${UE_ROOT:-/Users/Shared/Epic Games/UE_5.7}"
BUILD_SCRIPT="$UE_ROOT/Engine/Build/BatchFiles/Mac/Build.sh"

if [ ! -f "$BUILD_SCRIPT" ]; then
    echo "ERROR: UE build script not found at: $BUILD_SCRIPT"
    echo "Set the UE_ROOT environment variable to your UE 5.5 install path."
    exit 1
fi

echo "==> Building GameStarter (Development Editor | Mac)..."
"$BUILD_SCRIPT" \
    GameStarterEditor \
    Mac \
    Development \
    "$PROJECT_FILE" \
    -waitmutex

echo "==> Build complete."
