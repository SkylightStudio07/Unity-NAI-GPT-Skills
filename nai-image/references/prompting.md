# NAI V5 prompt writing

## Order (front = stronger)

1. Subject / count: `1girl, solo` · `1boy` · `no humans` (props, scenery). Keep humans out of props with `-3::1girl, 1boy, human::`.
2. Asset spec and framing tags: `game asset, paper cutout prop, full body, standing, facing left, from side, 3/4 profile`.
3. Fixed appearance tags: hair, outfit parts, items held.
4. One or two English sentences for what tags can't express: composition, left/right, where an object sits, material, mood, light direction.
5. Base prompt: artists, style, quality. This comes from the project's base file; don't rewrite it.
6. `Text:` line, only when you want lettering (see below).

V5 reads Danbooru tags and plain English together, and both survive long prompts (about 1,400 tokens). Tags pin down *what* is in the image; sentences pin down *how it is arranged*.

## Weights

| Form | Effect |
|---|---|
| `{tag}` / `{{tag}}` / `{{{tag}}}` | ×1.05 / ×1.10 / ×1.16 |
| `[tag]` / `[[tag]]` | ÷1.05 / ÷1.10 |
| `1.4::tag a, tag b::` | exact weight for a group; **always close with `::`** or the weight leaks into everything after it |
| `0.5::artist:name::` | mix in an artist lightly |
| `-1::multiple views::`, `-3::eyeshadow::` | negative weight *inside* the positive prompt: suppress a concept |

Overdoing it (`3.0::` and up, or 5+ braces) overbakes the image: outlines break and colours burn. The usual fix for a strong artist habit (eye shape, makeup, mouth) is a pair: `2.0::wanted look::` up front plus `-3::the habit::`.

In the negative prompt, `{bad hands}` excludes harder and `[signature]` excludes more weakly.

## Several characters

Give each person their own caption (V4+ `char_captions`). Without it, two characters merge into one face or swap outfits. In a prompt file:

```
@char B3: girl, young princess, silver hair, black cloak, ... || mature female, large horns
@char D3: boy, prince, blindfold, white coat, ... || girl
```

The grid is A–E for left→right and 1–5 for top→bottom, the same as the NAI UI, and it's optional. Put scene, composition and style in the main prompt; put appearance only in `@char` lines. Copy appearance lines word for word from the character's reference prompt file, so every image draws the same person.

## Transparent background (sprites, props, UI pieces)

Write the prompt with `{{black background, simple background}}` (or "on a solid black background"). The generator turns this into a true alpha request: it adds `2.0::transparent background::` before the base tags and sends `straight_alpha` + `tag_hint_transparent_background`. Neither the tag alone nor the flags alone is enough. The `_clean.png` output has faint alpha noise removed, RGB under α=0 set to black (so no coloured fringe after filtering) and is trimmed to the content.

Shapes that need to read as one solid piece, such as a plank, a frame or a gear, come out cleaner with `simple background, isolated, single object, centered`.

## Lettering

- **Best:** include `english text` in the tags, then make the **last** line `Text:` followed by the string. Nothing may come after it, because everything after `Text:` gets drawn as letters.
- **Alternative:** describe it in a sentence: `...with the text "R&C Company" stencilled on the hull`. If the spelling comes out wrong, add the `Text:` line as well.
- Only short English text renders reliably. Draw Korean or Japanese UI text in the engine, not in the image.

## Sizes (multiples of 64)

| Aspect | Size | Use |
|---|---|---|
| 21:9 | 1472×704 | wide parallax strips |
| 16:9 | 1344×768 | backgrounds, story pages |
| 3:2 | 1216×832 | wide props |
| 1:1 | 1024×1024 | props, icons |
| 2:3 / 9:16 | 832×1216 / 768×1344 | full-body characters, tall props |

On Opus a generation is free while it stays at ≤1024×1024 pixels (all of the above are ≤1,048,576 px), ≤28 steps and 1 image per request. Anything bigger costs Anlas, so ask the user before doing that.

## Style discipline (the lesson that cost a day)

When a project has prompt files, **use them verbatim**. Adding your own style words up front ("watercolor", "soft lighting", "colored pencil") overrides the project's base style, and the results look off-style or photoreal. For a new kind of asset, first add a section to the prompt files in the *same vocabulary* as the existing ones, then generate it, then show the user the results before anything goes into the game.
