#!/usr/bin/env bash
# package.sh — Package the GameStarter project for macOS (Shipping).
# Usage: bash tools/ue-command-scripts/package.sh [output-dir]
#
# Output defaults to Saved/Packages/Mac/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_FILE="$REPO_ROOT/Game/GameStarter.uproject"
OUTPUT_DIR="${1:-$REPO_ROOT/Saved/Packages/Mac}"

UE_ROOT="${UE_ROOT:-/Users/Shared/Epic Games/UE_5.7}"
UAT="$UE_ROOT/Engine/Build/BatchFiles/RunUAT.sh"

if [ ! -f "$UAT" ]; then
    echo "ERROR: RunUAT.sh not found at: $UAT"
    echo "Set the UE_ROOT environment variable to your UE 5.5 install path."
    exit 1
fi

echo "==> Packaging GameStarter → $OUTPUT_DIR"
"$UAT" BuildCookRun \
    -project="$PROJECT_FILE" \
    -noP4 \
    -platform=Mac \
    -clientconfig=Shipping \
    -cook \
    -allmaps \
    -build \
    -stage \
    -pak \
    -archive \
    -archivedirectory="$OUTPUT_DIR"

echo "==> Package complete: $OUTPUT_DIR"
