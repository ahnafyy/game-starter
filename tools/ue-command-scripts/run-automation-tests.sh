#!/usr/bin/env bash
# run-automation-tests.sh — Run UE Automation Tests headlessly on macOS.
# Usage: bash tools/ue-command-scripts/run-automation-tests.sh [TestFilter]
#
# TestFilter defaults to "GameStarter." which runs all tests in the GameStarter module.
# Example: bash run-automation-tests.sh "GameStarter.NPC"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_FILE="$REPO_ROOT/Game/GameStarter.uproject"
REPORT_DIR="$REPO_ROOT/Saved/AutomationResults"

TEST_FILTER="${1:-GameStarter.}"

UE_ROOT="${UE_ROOT:-/Users/Shared/Epic Games/UE_5.7}"
UE_EDITOR="$UE_ROOT/Engine/Binaries/Mac/UnrealEditor"

if [ ! -f "$UE_EDITOR" ]; then
    echo "ERROR: UnrealEditor not found at: $UE_EDITOR"
    echo "Set the UE_ROOT environment variable to your UE 5.5 install path."
    exit 1
fi

mkdir -p "$REPORT_DIR"

echo "==> Running automation tests: filter='$TEST_FILTER'"
"$UE_EDITOR" \
    "$PROJECT_FILE" \
    -nullrhi \
    -nosplash \
    -unattended \
    -nopause \
    -log \
    -ExecCmds="Automation RunTests $TEST_FILTER; Quit" \
    -ReportOutputPath="$REPORT_DIR"

echo "==> Test results written to: $REPORT_DIR"
