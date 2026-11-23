---
name: fx-sheet
description: Make a frame-by-frame attack or hit effect (weapon swing trail, claw marks, bite flash, bullet impact, dust and debris) as one 8, 12 or 16-frame sheet drawn by Codex / GPT ("Astra"), timed to a character's attack frames, and cut it for the game. Use when a sprite attack looks static or has no effect, an effect "appears and vanishes in one beat", a weapon is cut off at the sprite cell edge, or the user asks for an effect sheet / 이펙트 시트 / 휘두르기 이펙트 / 피격 이펙트.
---

# FX sheet

One sheet per attack. Codex draws every frame on pure black from a **pose guide** (the character's own attack frames in the same grid), so the trail follows the weapon. The game plays it additively over the character, starting on a chosen attack frame. First used in Project-Vertex: a bat swing, a crystal claw, a bite and a shared bullet hit (`examples/gpt-vertex/FxSheet/`).

Codex runs through the `codex-art-request` skill (`scripts/run_codex_art.py`); follow its rules: one job at a time, workspace-write sandbox, no SVG, never read token files, show the user what came back. This is a single-stage request (the sheet is the deliverable; no split request), because the grid itself is the cut.

Scripts are in `scripts/` (Python 3 + Pillow + numpy; run with `python -I`).

## Frame count

| Frames | Grid, cell | Use for |
|---|---|---|
| 8 | 4×2, 480×540 | quick jab, light hit |
| 12 | 4×3, 480×360 | default: swing, impact, a slow tail of dust or smoke |
| 16 | 4×4, 480×270 | heavy slam with a long tail. Fewer pixels per frame; check it is sharp enough at the character's size |

Not fewer than 8: with 4 frames the effect appears and vanishes in one beat.

## Steps

1. **Pick the start frame.** Export the attack frames in play order as transparent PNGs (one per frame). Look at a numbered contact strip: the start is the first frame the weapon moves fast; the impact should land around frame 4–8 of the effect.
2. **Guide:** `make_guide.py <frames dir> <start> <8|12|16> <scope>/Reference/Guide.png [--side left|right]`. Note the printed `--canvas` and effect rectangle. The canvas is the character cell widened by 1/3 toward the target, so a weapon that leaves the cell has room.
3. **Request:** start from `references/request_template.md` (or the nearest file in `examples/gpt-vertex/FxSheet/`) and write the frame table for this attack: where the weapon tip is in each guide cell, which frame is the impact. Keep: pure black, alpha = max(R,G,B), one origin for all frames (no per-frame centring), ≥12 px black border, nearly colourless art (the game multiplies a colour), a tail that never goes empty, the forbidden list. Attach the guide and one or two style references (an approved earlier sheet is the best one).
4. **Run Codex** in the background. Then check it yourself: `cut_fx.py <sheet> <out> <n> --canvas … --overlay <guide> <check.jpg>` and open `check.jpg`. The trail must follow the weapon tip, the bright head must cover where the weapon leaves the cell, nothing of the character or the numbers may be drawn, border alpha must be all 0. If the trail runs one frame ahead or behind, shift the start frame instead of redrawing.
5. **Cut:** `cut_fx.py <sheet> <game texture.png> <n> --canvas … --gain …`. Image models draw the tail too dark; lift it (12 frames, typical: `1,1,1,1,1,1,1.15,1.4,1.8,2.2,2.8,3.2`). Peak alpha of the last frames around 20–100 reads well in game.
6. **Import:** Unity: copy `unity_slice_grid.cs`, set the path and grid, run it (`unity command eval_file` or an editor script).
7. **Play it** as in `references/runtime.md` (sync the swing frames, half-speed tail, place by the drawn sprite area) and record the attack in play to check (`unity-play-record`).

## Lessons

- Codex placed the effect correctly from the guide every time; when the effect looked off in game it was the game's placement rectangle (a `preserveAspect` Image is smaller than its box), not the art.
- A swing alone looks static. A swing trail plus an impact flash plus slow debris looks like a hit.
- Draw white, tint in game: one sheet serves several characters.
- A character sheet whose generator already drew a flash or a glowing trail does not need one; check the attack frames first.
