# 2.5D layered environments

Lessons from a 2.5D puzzle platformer whose stage art was all made with V5, and from a deckbuilder's base-camp rooms.

## Split a scene into layers, one prompt each

A single 16:9 painting can't put a character *behind* a table and *in front of* a wall. Generate the room as separate pieces and stack them in Unity:

| Layer | What | How |
|---|---|---|
| Back | walls, windows, ceiling, far machinery; the floor plane | opaque 16:9 background |
| Mid props | furniture characters stand beside or behind: bunk beds, workbench, map table, locker | **transparent** props, one per prompt, placed in Unity |
| Front | things that overlap the bottom edge and the characters' legs: crates, a railing, a sofa back, cables | **transparent** strip or props, drawn last |

Keep the back layer **sparse in the bottom 40%**, so characters and mid props have floor to stand on. Ask for it in words, for example: "an empty open concrete floor fills the lower part of the image".

## Prompt patterns that worked

- **Backgrounds:** `wide shot, scenery, horizontal composition, eye-level perspective`, then a sentence about depth: "darker toward the edges, warm light only near the centre".
- **Front view for 2.5D:** to keep a room square to the camera, use `{{straight-on front view of the room, one-point perspective, back wall parallel to the picture plane}}` and suppress `-3::dutch angle, fisheye, wide-angle distortion, top-down view, isometric::`.
- **Props cut flat from the side:** `no humans, -3::1girl, 1boy, human::, game asset, prop, {{black background, simple background}}, {{flat front view}}`, with `-3::isometric, three-quarter view, top-down view, perspective::`. End the paragraph with "isolated on a solid black background". The script turns this into a real alpha PNG.
- **Solid objects** (a table, a locker, a stove) come out cleaner with `single object, centered, isolated`.
- **One prop per request.** Two props in one prompt merge or clip each other.
- **Ground line:** for a prop that stands on the floor, write "standing on an invisible flat ground line, bottom edge straight". Unity can then put its pivot at the bottom.
- **Light must match.** Name the same light in every layer of a room, e.g. "lit from a warm work lamp on the right, cold blue moonlight from the window on the left". Mismatched light is what makes stacked layers look pasted on.
