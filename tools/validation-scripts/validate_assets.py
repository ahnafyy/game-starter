"""validate_assets.py — Validates UE asset naming conventions.

Scans a content directory (default: Game/Content) and reports assets that
violate the naming prefix conventions defined in the Asset Pipeline Agent config.

Usage:
    python tools/validation-scripts/validate_assets.py [content-dir]
    uv run tools/validation-scripts/validate_assets.py Game/Content/GameStarter
"""

from __future__ import annotations

import sys
from pathlib import Path

# Maps Unreal asset type keywords (appear in .uasset filenames / folder context)
# to their required prefix. These are heuristic — full validation requires
# Unreal Python inside the editor.
NAMING_RULES: dict[str, str] = {
    "StaticMesh": "SM_",
    "SkeletalMesh": "SKM_",
    "Texture2D": "T_",
    "Material": "M_",
    "MaterialInstance": "MI_",
    "Blueprint": "BP_",
    "NiagaraSystem": "NS_",
    "SoundWave": "S_",
    "SoundCue": "SC_",
    "AnimSequence": "AS_",
    "AnimBlueprint": "ABP_",
    "PhysicsAsset": "PHYS_",
    "DataTable": "DT_",
    "Enum": "E_",
}

VALID_PREFIXES = tuple(NAMING_RULES.values())


def validate_directory(content_dir: Path) -> list[dict]:
    violations: list[dict] = []

    for asset_file in content_dir.rglob("*.uasset"):
        name = asset_file.stem
        if name.startswith("PH_"):
            # Placeholder prefix — allowed, skip
            continue
        if not name.startswith(VALID_PREFIXES):
            violations.append(
                {
                    "file": str(asset_file.relative_to(content_dir)),
                    "name": name,
                    "issue": (
                        f"Missing required prefix. Valid prefixes: {', '.join(VALID_PREFIXES)}"
                    ),
                }
            )

    return violations


def main() -> None:
    content_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Game/Content")

    if not content_dir.exists():
        print(f"Content directory not found: {content_dir}")
        print("This is expected if Lyra content is not yet copied locally.")
        sys.exit(0)

    violations = validate_directory(content_dir)

    if not violations:
        print(f"OK — no naming violations found in {content_dir}")
        sys.exit(0)

    print(f"VIOLATIONS ({len(violations)}) in {content_dir}:\n")
    for v in violations:
        print(f"  [{v['file']}]")
        print(f"    Asset: {v['name']}")
        print(f"    Issue: {v['issue']}")
        print()

    sys.exit(1)


if __name__ == "__main__":
    main()
