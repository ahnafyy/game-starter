# Playing on Mac after MVP

When development on Shadow PC is done, you package the game as a macOS `.app` and run it on your MacBook Air. No Unreal Engine installation required to play.

## Step 1: Package from Shadow PC

On your Shadow PC, with the UE project open and built:

```bash
# Default output: Saved/Packages/Mac/ inside the repo
bash tools/ue-command-scripts/package.sh

# Or specify a custom output directory
bash tools/ue-command-scripts/package.sh "C:\Users\you\Desktop\GameStarterBuild"
```

This runs `BuildCookRun` with these flags:
- `-platform=Mac` — cross-compiles for macOS
- `-clientconfig=Shipping` — no debug overhead
- `-cook -allmaps -build -stage -pak -archive` — full cooked + archived build

The output is a folder containing `GameStarter.app`.

> **Cross-compilation note:** Packaging for Mac from Windows requires the **Mac cross-compilation toolchain** installed via the Epic Games Launcher.
> Launcher → Unreal Engine → Options → check **Mac** under Target Platforms.

## Step 2: Transfer the `.app` to your Mac

The packaged folder is typically 2–8 GB. Choose a transfer method:

| Method | How |
|---|---|
| **Google Drive / Dropbox** | Upload from Shadow PC, download on Mac |
| **scp over LAN** | `scp -r user@shadowpc-ip:/path/to/GameStarter.app ~/Desktop/` |
| **USB drive** | Copy on Shadow (via Remote USB passthrough), plug into Mac |

## Step 3: Run on Mac

```bash
# Option A: Double-click GameStarter.app in Finder

# Option B: Terminal
open ~/Desktop/GameStarter.app

# Option C: Run the binary directly (useful for seeing logs)
~/Desktop/GameStarter.app/Contents/MacOS/GameStarter
```

If macOS blocks the app ("can't be opened because it is from an unidentified developer"):
```bash
xattr -dr com.apple.quarantine ~/Desktop/GameStarter.app
```

## Lumen performance on MacBook Air

Lumen (hardware ray tracing GI) is enabled in `Game/Config/DefaultEngine.ini`. On a MacBook Air with Apple Silicon, Lumen runs via Metal but may cause low framerates.

**To switch to screen-space fallback** (better performance on integrated GPU), edit `Game/Config/DefaultEngine.ini`:

```ini
[/Script/Engine.RendererSettings]
; Change these two lines:
r.DynamicGlobalIlluminationMethod=0   ; 0 = Screen Space GI, 1 = Lumen
r.ReflectionMethod=0                  ; 0 = Screen Space Reflections, 1 = Lumen
```

This is a two-line change. Do it on a branch when testing on Mac — keep `r.DynamicGlobalIlluminationMethod=1` on main for Shadow PC development where Lumen runs properly.

Alternatively, leave Lumen on and test first — Apple Silicon (M2/M3/M4) handles Lumen reasonably well. MacBook Air (Intel) will struggle.

## Troubleshooting

**App crashes on launch**
- Check logs: `~/Library/Logs/Unreal Engine/GameStarter/`
- Most common cause: missing shader cache. Re-package with `-compressed` flag removed, or clear `Saved/` on Shadow PC before packaging.

**"damaged and can't be opened"**
```bash
xattr -dr com.apple.quarantine ~/Desktop/GameStarter.app
```

**Black screen / no rendering**
The Mac GPU may not support all renderer features used. Add to the launch args:
```bash
open GameStarter.app --args -dx11
# or force Metal
open GameStarter.app --args -metal
```

**Wrong resolution / fullscreen issues**
```bash
open GameStarter.app --args -ResX=1920 -ResY=1080 -windowed
```
