---
name: unity-play-record
description: Record a moment of a Unity game in play mode (a character's idle and attack, an effect, a UI transition) at a fixed 30 fps and turn it into an mp4, optionally side by side with an earlier recording or with a zoomed close-up. One script call that reads no images, so a cheap subagent (Haiku) can run it. Use after changing a sprite sheet, effect or timing, when the user wants to see it in game, or for "녹화해서 보여줘" / before-after videos. Needs the Unity CLI connected to an open Editor.
---

# Unity play record

```
bash ~/.claude/skills/unity-play-record/scripts/record.sh --scene <scene.unity> --scenario <scenario.cs> --tag <name> [--arg <value>]... [options]
```

Run from the Unity project root in Git Bash. It enters play mode in `--scene`, runs the project's **scenario** script (which sets up the moment and records frames), leaves play mode, reopens the scene the editor was on, and encodes with Unity's own `MediaEncoder` (no ffmpeg). About 1–2 minutes. The last line is `RESULT ok <mp4> (...)` or `RESULT fail <reason>`.

Options: `--arg <value>` (repeatable, passed to the scenario), `--return <scene>`, `--compare <old tag>` (side by side, same moment), `--zoom x,y,w,h` (right half = this region of the 960×540 frame, enlarged; used when there is no compare), `--labels "left|right"`, `--part attack|idle|both`, `--loops N`.

Output in `Temp/PlayRec/` (Unity ignores `Temp/`): `<tag>.mp4`, `<tag>_sheet.jpg` (16 stills of the attack, to look at without the video), `<tag>/` frames and `done.txt`.

## The scenario (once per project)

Copy `scripts/scenario_template.cs` and fill in the two TODOs: how to set up the moment (start a battle, spawn a character) and how to trigger the action. It records `idle` (120 frames) then `attack` (105 frames) with `Time.captureFramerate = 30`, and ends by writing `done.txt`. `examples/vertex-play-record/battle_scenario.cs` is a complete one: it starts a deck-builder battle from an encounter asset (`--arg`), hides a pop-up, records the idle, ends turns with extra block until an enemy attacks, records the attack.

Rules for scenarios: exit early if the marker object exists (a retried eval must not record twice); always write `done.txt`, also on failure, so the script does not wait for nothing.

## Running it through Haiku

Give a Haiku subagent the exact command and ask for the `RESULT` line and `done:` line only. Tell it: no retry on `fail` (report the reason), don't open images or videos, don't modify files, never open `~/.claude.json` or other credential files. The main session sends the mp4 to the user and looks at `<tag>_sheet.jpg` only when it must judge the result itself. Recording and encoding cost almost nothing; reading images is what costs tokens.

## Rules (the script enforces the first two)

- Never stop someone's play session: it refuses when the editor is already playing.
- It refuses when the open scene has unsaved changes.
- Tell the user before running it: the editor will enter play mode and switch scenes.
- If every `unity` call times out, the editor window is probably in the background or the CLI server died; ask the user to bring the Editor to the front. Don't change the editor's background-throttling settings on your own.
- Long calls (encode) log "Main thread operation timed out" in the Editor log; that is the CLI waiting, not a game error. The script waits for the result file instead.
