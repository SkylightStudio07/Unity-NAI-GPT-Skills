---
name: nai-image
description: Generate illustration assets with NovelAI Diffusion V5 (NAI) — game sprites, props, backgrounds, parallax layers, UI pieces, portraits, storybook pages — including background-free (transparent) PNGs generated directly by V5, separate per-character captions, and seamless tiling. Use when the user asks for NAI / NovelAI images or art assets in a project that uses NAI prompts (e.g. an "Art Prompts" folder with "[Base Prompts].txt").
---

# NAI image assets

Scripts (run with the system Python; needs Pillow for transparent cleanup):
- `scripts/nai_gen.py`: builds and sends the request, saves the raw PNG, a cleaned `_clean.png` and the request JSON. Run `--help` for every flag.
- `scripts/make_tileable.py`: cross-fades edges so a texture wraps (`--axis x|y|xy`).

Read `references/prompting.md` before writing or editing a prompt. Read `references/environment-2_5d.md` before making layered backgrounds or props for a 2D / 2.5D game. Read `references/api.md` only to debug the API.

## Rules

1. **Token:** env `NAI_API_KEY`. On Windows the script also reads it from the User environment, because editor or agent processes often don't inherit it.
   - Never print it, echo it, read it from the clipboard or write it to a file.
   - If it is missing, ask the user to set it as a User env var. Don't ask them to paste it into the chat.
2. **The project's prompts are the source of truth.** If the project has a prompt folder (base, negative and section files), generate from those sections verbatim.
   - Don't invent style words or presets. They override the house style; this has happened before and the results came out off-style and photoreal.
   - For a new kind of asset, first add a section to the prompt files in the same vocabulary, then generate.
   - With no prompt files, write the prompt following `references/prompting.md` and agree a base style with the user first.
3. **Stay in the free tier unless the user agrees:** ≤1024×1024 px, ≤28 steps, one image per request (Opus). The script warns when a request would cost Anlas.
4. **No real-world IP:** no tags for existing franchise characters or real people in the prompt. Describe an original look instead.
5. **Show, then place:** look at the results yourself, then show the user the picks before anything is imported into a project. Keep the raw output folder out of version control.

## Workflow

1. Find the prompt source: `python -I scripts/nai_gen.py --prompts "<dir>" --list`. The default dir is `./Art Prompts`, or set env `NAI_PROMPTS_DIR`.
2. Check the assembled prompt without spending anything: `... <key> --dry-run`.
3. Generate a small batch from the project root:
   - Section key: `python -I <skill>/scripts/nai_gen.py 04:1-B --n 3 --out Tools/_nai_out`
   - Inline: `--prompt "..." --name crate --transparent [--char "B3: caption || neg"]`
   - Size comes from the section header's aspect hint (`16:9`, `2:3`, …) or from `--size WxH`.
   - Keep the seed: same seed + same JSON = the same image.
4. Look at every image (open the PNGs). Reject off-style ones and anything with mangled hands, extra limbs, merged characters or text artefacts.
5. Post-process:
   - Transparent assets: use `_clean.png` (alpha fringe removed, trimmed).
   - Repeating fills or strips: `python -I scripts/make_tileable.py in.png out.png --axis x`.
6. Copy the chosen file into the project's art folder.
   - Record the section key and seed next to it, in a commit message or a note, so it can be regenerated.
   - In engines with SRP batching, give each texture its own material.

## Prompt-file format the script reads

`[Anything] NN_Name.txt` (e.g. `[Props] 03_Stage_Objects.txt`) → keys `NN:<section>`:

```
## 1. Gates (16:9)                 <- parent header; its aspect applies to children
### 1-A. Iron gate                 <- key 03:1-A
no humans, -3::1girl, 1boy, human::, game asset, paper cutout prop, {{black background, simple background}},
ornate iron gate, ... A tall fairytale gate prop for a 2D platformer, isolated on a solid black background.
@char C3: girl, ... || mature female   <- optional, one per character
```

`[Base Prompts].txt` is appended to every prompt and `[Negative Prompts].txt` is the negative. `{{black background, simple background}}` in a section means the output will be a transparent PNG.
