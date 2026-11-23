# Step 3. Turns Astra's effect sheet (pure black background, 1920 x 1080 grid) into the game texture:
# white-ish RGB with alpha = max(R, G, B), same grid, for the additive UI material.
# Optionally crops every cell to the effect canvas (when the canvas is smaller than the cell) and lifts the
# brightness of the fading tail, which the image model tends to draw too dark to see in game.
#
# usage: python -I cut_fx.py <in.png> <out.png> <frame count: 8|12|16> [--canvas x,y,w,h] [--gain 1,1,...] [--overlay guide.png check.jpg]
#   --canvas  : the effect canvas inside each cell, as printed by make_guide.py (default: the whole cell)
#   --gain    : one brightness factor per frame (default 1). Typical 12-frame tail: 1,1,1,1,1,1,1.15,1.4,1.8,2.2,2.8,3.2
#   --overlay : also writes guide + effect (additive) so the position can be checked by eye before importing
# Prints the peak alpha of every frame and the darkest value on each cell's border (must be 0: nothing may be cut).
import sys
import numpy as np
from PIL import Image

src, out, count = sys.argv[1], sys.argv[2], int(sys.argv[3])
opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
cols, rows = {8: (4, 2), 12: (4, 3), 16: (4, 4)}[count]
im = Image.open(src).convert("RGB")
assert im.size == (1920, 1080), im.size
cw, ch = 1920 // cols, 1080 // rows
cx, cy, fw, fh = [int(v) for v in opt("--canvas", f"0,0,{cw},{ch}").split(",")]
fw -= fw % 4; fh -= fh % 4  # block compression needs multiples of 4
gain = [float(v) for v in opt("--gain", ",".join(["1"] * count)).split(",")]
assert len(gain) == count

if "--overlay" in sys.argv:
    i = sys.argv.index("--overlay")
    from PIL import ImageChops
    ImageChops.add(Image.open(sys.argv[i + 1]).convert("RGB"), im).save(sys.argv[i + 2], quality=88)

a = np.asarray(im).astype(np.float32)
sheet = np.zeros((fh * rows, fw * cols, 4), np.uint8)
peaks, edges = [], []
for k in range(count):
    x0, y0 = (k % cols) * cw + cx, (k // cols) * ch + cy
    c = np.clip(a[y0:y0 + fh, x0:x0 + fw] * gain[k], 0, 255)
    al = c.max(axis=2)
    rgb = np.where(al[..., None] > 0, c / np.maximum(al[..., None], 1) * 255, 255)
    sheet[(k // cols) * fh:(k // cols + 1) * fh, (k % cols) * fw:(k % cols + 1) * fw] = np.dstack([rgb, al]).astype(np.uint8)
    peaks.append(int(al.max()))
    edges.append(int(max(al[0].max(), al[-1].max(), al[:, 0].max(), al[:, -1].max())))
Image.fromarray(sheet, "RGBA").save(out)
print(f"{out} {sheet.shape[1]}x{sheet.shape[0]} cell {fw}x{fh} cols {cols}")
print("peak alpha per frame:", peaks)
print("border alpha per frame (want 0):", edges)
