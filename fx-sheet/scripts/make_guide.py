# Step 1. Builds the pose guide that goes to Codex with the request: the character frames the effect must follow,
# laid out in the same grid as the effect sheet (1920 x 1080), on dark navy, numbered.
# Each cell shows one character frame. The effect canvas is the character cell widened toward the side the
# character attacks, so a weapon that leaves the cell has room; a red line marks where the character cell begins.
#
# usage: python -I make_guide.py <frames dir> <first frame> <frame count: 8|12|16> <out.png> [--extend 0.3333] [--side left|right] [--step 1]
#   frames dir  : one PNG per frame with transparent background, named so that sorting gives play order
#                 (00.png, 01.png ... or anything). Square or not; all the same size.
#   first frame : index (in sorted order) of the frame the effect starts on: the first frame the weapon moves fast
#   --extend    : extra canvas toward --side, as a fraction of the cell width (default 1/3)
#   --side      : where the target is, i.e. where the weapon leaves the cell (default left)
#   --step      : character frames per effect frame (1 = locked 1:1 to the character sheet)
# Prints the canvas for cut_fx.py and the effect rectangle in units of the character cell.
import sys, glob
from PIL import Image, ImageDraw, ImageFont

src, first, count, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
extend, side, step = float(opt("--extend", 1 / 3)), opt("--side", "left"), int(opt("--step", 1))
files = sorted(glob.glob(src + "/*.png"))
cols, rows = {8: (4, 2), 12: (4, 3), 16: (4, 4)}[count]
cw, ch = 1920 // cols, 1080 // rows
fw0, fh0 = Image.open(files[0]).size
# the character cell keeps its aspect; the effect canvas adds `extend` of its width toward `side`
scale = min(ch / fh0, cw / (fw0 * (1 + extend)))
sw, sh = fw0 * scale, fh0 * scale
fw, fh = sw * (1 + extend), sh
ox, oy = (cw - fw) / 2, (ch - fh) / 2
try:
    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 20)
except OSError:
    font = ImageFont.load_default()
g = Image.new("RGB", (1920, 1080), (20, 28, 36))
d = ImageDraw.Draw(g)
for k in range(count):
    im = Image.open(files[first + k * step]).convert("RGBA").resize((round(sw), round(sh)), Image.LANCZOS)
    x0, y0 = (k % cols) * cw, (k // cols) * ch
    px = x0 + ox + (fw - sw if side == "left" else 0)
    g.paste(im, (round(px), round(y0 + oy)), im)
    d.rectangle((x0, y0, x0 + cw - 1, y0 + ch - 1), outline=(90, 110, 130))
    lx = round(px if side == "left" else px + sw)
    d.line((lx, y0, lx, y0 + ch - 1), fill=(160, 60, 60))
    d.text((x0 + 8, y0 + 6), str(k + 1), font=font, fill=(255, 230, 120))
g.save(out)
line = ox + fw - sw if side == "left" else ox + sw
print(f"grid {cols}x{rows} cell {cw}x{ch} canvas {fw:.0f}x{fh:.0f} at ({ox:.0f},{oy:.0f}) red line {line:.0f}px from the cell's left")
print(f"cut_fx.py --canvas {ox:.0f},{oy:.0f},{fw:.0f},{fh:.0f}")
x = -extend if side == "left" else 0.0
print(f"effect rect in character-cell units: x {x:.4f}, y 0, w {1 + extend:.4f}, h 1")
