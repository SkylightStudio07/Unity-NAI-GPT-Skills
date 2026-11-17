# Mockup → split → integrate

Give Codex (Astra) a request, get a **finished screen mockup**, then have the same picture cut into **game pieces** and assemble them in the engine.

```
1. Gather current captures and references
2. Mockup request (REQUEST.md)        → Codex: finished mockup PNG
3. Review and pick                     (back to 2 until it is right)
4. Split request (SPLIT_REQUEST.md)   → Codex: piece PNGs + layout.json + Contact_Sheet
5. Check the pieces
6. Copy into the project and set import settings
7. Assemble in code, using layout.json coordinates as is
8. Capture the running app and compare → user test → commit
```

## Folder

```
<ArtFolder>/<Screen>Mockup/
  REQUEST.md            mockup request
  Reference/            current captures and design references
  <Name>_Mockup.png     the picked mockup (the master)
  PROMPTS.txt           generation prompts Codex actually used
  SPLIT_REQUEST.md      split request
  Extracted/            pieces (PNG + layout.json + Contact_Sheet.jpg + README.md)
```

When replacing a design, put the new pieces in a new folder (`.../V3/`) instead of overwriting, so the old version is easy to bring back.

## 1–3. Mockup request

Include:

- **What changes and what stays.** E.g. "normal dialogue box as is, only the choice moment is new."
- **Reference pictures** by path: mockups whose design language to borrow, and current captures.
- **Composition**: background, characters, dim overlay, positions, matching how the app behaves now.
- **Design elements to borrow**, concretely (e.g. pale blue-grey geometric planes, thin drafting lines, small registration crosses, cut ink corners, hard offset shadow, short teal bars, small number + wide-spaced English subtitle + bold title).
- **Forbidden list**: e.g. neon glow, gold, grunge, dense circuit patterns, SVG, shape assembly, asset sheets.
- **States as the same scene**: Default / Hover / Selected share layout, dimness and panel shape; only the state differs.
- **Deliverables**: full-screen PNG at the target resolution (e.g. 1920×1080), `PROMPTS.txt`, `README.md`.

Review:

- Panels have inner structure, not "empty white rectangle + noise".
- Dimness and panel detail don't drift between images.
- White fringe around characters, overlapping text.
- Codex worked from the current request, not an earlier version.

## 4. Split request

### Core rules (write them into the request)

1. **Surfaces are image-model paintings.** Keep the mockup's paper/ink texture, planes and patterns. Regenerating the master at higher resolution (or a piece alone) with the same prompt and cutting from that works well.
2. **No SVG.** Only 1–2 px lines, tiny crosses and short bars may be drawn flat.
3. **No text, numbers, arrow glyphs, characters, card art or backgrounds inside pieces.** Values that change are written by the app.
4. **2× PNG** (1 screen px = 2 PNG px), transparent background, **0° rotation** (the app rotates).
5. Outer edges use **binary alpha** (0/255). Only patterns and gradient overlays get soft alpha; mark them `soft` in the table.
6. Panel, shadow, pattern, overlay and border come **separately**, so they can animate separately.
7. Only pieces that must stretch are **9-slice**: visible motifs in fixed corners only, the middle repeatable texture. Everything else is fixed size.
8. When swapping existing pieces, keep **file names, sizes and alpha** identical. For a new design, say new ones are fine.
9. States missing from the mockup: have Codex draw a confirmation mockup of the same scene first, then cut from it.

### Piece table

| File | Content | Alpha |
|---|---|---|
| `Panel.png` | white paper panel: cut corners, inner geometric planes, drafting lines, crosses | binary |
| `Emblem_Compass.png` | large pale compass, **already clipped to the panel outline** | soft |
| `Strip_Mask.png` | **shape only** (white) of the photo strip; the app masks real art into it | binary |

Overlays that sit on a panel are easiest on **the panel's canvas size and position** (one offset stacks them).

### `layout.json`

- Reference resolution (e.g. 1920×1080), top-left origin, `[x,y,w,h]` in screen px.
- Per piece: `file`, `png_size_px`, `screen_rect`, `alpha`, `nine_slice_px`, shadow opacity.
- **`text_slots`**: per text spot `[x,y,w,h]`, alignment, size (px), weight, colour (hex), letter spacing (px).
- Pieces that follow a resizable panel (tails etc.): offsets from the panel corner.
- Art windows / masks: polygon vertices in PNG px and screen px.

### Deliverables

`Extracted/`: PNGs + `layout.json` + `Contact_Sheet.jpg` (each piece alone, a reassembly from layout coordinates next to the master, 9-slices shown stretched) + `README.md` (no SVG used, prompts, validation).

## 5. Checking the pieces

- `README.md` mentioning "geometric redraw" or SVG → ask again.
- Compare the reassembly with the master. Almost no difference from the old pieces means re-texturing (a failure for a new design).
- No text inside pieces.
- Open the PNGs yourself: size, alpha range, edge alpha.

## 6–8. Engine integration (Unity, uGUI)

- Edit through the project's editor automation (e.g. `unity command eval_file`) rather than adding one-off editor scripts, if the project allows.
- Import: Sprite / Single / **PPU 200** for 2× PNGs on a 100-reference canvas / FullRect / Bilinear / no compression / no mipmaps / NPOT None. 9-slice borders go in `spriteBorder` in PNG px (L, B, R, T).
- Position: anchor top-centre, pivot top-left, `anchoredPosition = (x - width/2, -y)` keeps it centred on wide screens.
- TMP `characterSpacing` is in 1/100 em: `spacing_px / font_size × 100`.
- Art windows: put the art under a `Mask` (showMaskGraphic off) and the overlay piece above it.
- A `Button` added in code applies its default colour tint first (disabled = translucent grey). Switch to SpriteSwap and call `canvasRenderer.SetColor(Color.white)`.
- Particles under uGUI need a UI particle component, and the renderer's `maxParticleSize` raised, or big particles clamp away.
- Verify: in play mode trigger the effect from an editor script, capture with `ScreenCapture`, compare with the master. For frame-accurate capture set `Time.captureFramerate` and restore it to 0.
- Never stop the user's play session; check play state and scene dirty state before switching scenes. A script retried while play mode starts can run twice: exit early if its marker object already exists.
