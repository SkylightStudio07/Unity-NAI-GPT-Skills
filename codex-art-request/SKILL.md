---
name: codex-art-request
description: Make raster game/app art with the local Codex CLI and its GPT image tool (the user calls it "Astra" / 아스트라) in two stages — a finished mockup from REQUEST.md, then cut pieces with alpha, layout.json and a contact sheet from SPLIT_REQUEST.md — then review and integrate. Use when the user wants UI, VFX or sprite pieces drawn by GPT / Codex / Astra in any project, or asks for a 요청서, 목업 or 분절. Not for NovelAI images (use nai-image). If the project has its own art-request skill, prefer that.
---

# Codex art request (Astra)

Astra is the Codex app on this PC with its built-in `imagegen` tool. Claude writes the request, runs Codex, reviews what comes back and integrates it, instead of the user carrying request files by hand.

`references/workflow.md` is the full method: request contents, split rules, piece table, `layout.json`, review checks and engine import. Read it before writing the first request in a project. If the project already has earlier requests, copy the nearest one's format.

## Rules

1. **Two stages, always.** `REQUEST.md` gets a finished mockup. After review, `SPLIT_REQUEST.md` gets the pieces. Never "design and cut it" in one request; the mockup gets worse or the old pieces come back re-textured.
2. **Never ask for SVG.** Surfaces are image-model paintings; pieces are cut from them with alpha masks. Asking for "SVG + PNG" brings back flat untextured shapes.
3. **Show the user each request and each mockup before the next stage.** Picks are the user's call. Rendering spends their Codex usage: one job at a time, and no re-run on your own after a failure.
4. **Credentials:** never read, print or copy `~/.codex/auth.json` or other token files.
5. **Sandbox:** only `workspace-write` or `read-only`. Never `--dangerously-bypass-approvals-and-sandbox`.
6. **Don't call Codex for pure pixel work.** Cropping, padding and alpha extraction by a stated formula are quicker in Python (run it with `-I`). Codex is for drawing.
7. Codex's work files (`.py`, `.cjs`, `.ps1`, `.zip`, `Generated/`, `_codex_*.txt`) stay out of commits. Follow the project's own commit and art-folder rules where they exist.

## Running Codex

`scripts/run_codex_art.py` (in this skill's folder) finds `codex.exe` inside the app bundle (not on PATH; the folder changes with updates), runs `codex exec` in the project root, saves the final message, lists every file changed inside `--scope` (git-ignored ones included) and warns about anything git sees changed outside it. Run it in the background; a mockup job can take many minutes.

```
python -I ~/.claude/skills/codex-art-request/scripts/run_codex_art.py --check
python -I ~/.claude/skills/codex-art-request/scripts/run_codex_art.py --scope Art/Mockups/Inventory --request Art/Mockups/Inventory/REQUEST.md --image Art/Mockups/Inventory/Reference/current.png
```

- `--root` defaults to the current folder; `--scope` is relative to it and must be a subfolder.
- `--request` makes Codex follow that file and write only inside the scope. `--prompt` sends a free-form instruction instead. `--image` can repeat.
- Output: `<scope>/_codex_last.txt` (final message) and `_codex_log.txt`. Delete both before committing.
- Outside a git repository the outside-scope check is skipped; the script says so.

If it reports changes outside the scope, stop and tell the user. Don't revert them without asking; the working tree often holds unrelated uncommitted work.

## Stages

1. **Mockup request.** What changes and what stays, the rules the picture must show, reference files by path (save current captures to `<scope>/Reference/`), composition, design elements to borrow, a forbidden list, deliverables (`PNG`, `PROMPTS.txt`, `README.md`). For a VFX, say how the app will play it (one-shot, loop, frames, anchor), since that decides what needs drawing.
2. **Review the mockup yourself.** Open every PNG and read `README.md`. Check edge clipping, stray text, fringe, and that it isn't a re-texture of the old art. **Measure before writing the split**: real extents often break the canvas you guessed.
3. **Split request.** Exact piece table, canvas, origin, alpha formula, validation, `layout.json`, `Contact_Sheet`. Match alpha to the actual shader or blend mode: premultiplied or straight, additive or alpha-blended.
4. **Review the pieces.** Reopen the PNGs yourself: size, edge alpha, alpha range, no text inside pieces. Don't rely only on the delivered `README.md` or `validation.json`.
5. **Integrate and verify** with the project's own tools, then capture the real running app and compare with the mockup.

## Lessons from earlier jobs

- A request edited after Codex started may not be the one it used. If you change a request, say so in the next prompt.
- A near-zero before/after difference on the contact sheet means it re-textured the old pieces. For a new design, that's a failure.
- States (Default / Hover / Selected) must be the same scene with only the state changed. Ask for a confirmation mockup of missing states before cutting them.
- A VFX fixed to one spot detaches when the sprite recoils. Measure the anchor (muzzle, hand) per frame and track it.
- When erasing pixels from a sheet, keep the original and check every edited frame against it. A red "removed pixels" overlay finds mistakes quickly.
- Unity specifics (import settings, uGUI assembly, capture) are at the end of `references/workflow.md`.
