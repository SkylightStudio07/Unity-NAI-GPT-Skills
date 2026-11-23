# Builds the 1920x540 video frames from recordings in Temp/PlayRec/<tag>/ into Temp/PlayRec/_frames/.
#   two tags      : side by side, the same moment of each (before | after)
#   one tag       : left = full frame, right = the --zoom region enlarged
#   --part attack|idle|both (default attack)   --loops N (default 2)   --labels "left|right"
#   --zoom x,y,w,h in the 960x540 recording (default 300,80,600,337)
# Also writes Temp/PlayRec/<first tag>_sheet.jpg: 16 stills of the attack, for a quick look without the video.
# usage: python -I compose.py <tag> [<tag2>] [--part attack] [--zoom 300,80,600,337] [--labels "이전|이후"]
import sys, os, glob, shutil
from PIL import Image, ImageDraw, ImageFont

args = [a for a in sys.argv[1:]]
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
flags = {"--part", "--zoom", "--labels", "--loops"}
tags = []
i = 0
while i < len(args):
    if args[i] in flags: i += 2; continue
    tags.append(args[i]); i += 1
part, loops = opt("--part", "attack"), int(opt("--loops", "2"))
zx, zy, zw, zh = [int(v) for v in opt("--zoom", "300,80,600,337").split(",")]
labels = opt("--labels", "").split("|") if "--labels" in args else []
W = "Temp/PlayRec/"
out = W + "_frames/"
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 22)  # Korean-capable on Windows
except OSError:
    font = ImageFont.load_default()


def frames(tag):
    parts = ["idle", "attack"] if part == "both" else [part]
    fs = []
    for p in parts:
        fs += sorted(glob.glob(f"{W}{tag}/{p}_*.jpg"))
    if not fs: sys.exit(f"no {part} frames in {W}{tag}")
    return fs


a = frames(tags[0]); b = frames(tags[1]) if len(tags) > 1 else None
n = 0
for _ in range(loops):
    for k in range(len(a)):
        st = Image.new("RGB", (1920, 540))
        fa = Image.open(a[k]); st.paste(fa, (0, 0))
        if b: st.paste(Image.open(b[min(k, len(b) - 1)]), (960, 0))
        else: st.paste(fa.crop((zx, zy, zx + zw, zy + zh)).resize((960, 540), Image.LANCZOS), (960, 0))
        d = ImageDraw.Draw(st)
        for x, t in zip((16, 976), labels):
            if t: d.rectangle((x - 6, 496, x + 22 * len(t) + 10, 530), fill=(0, 0, 0)); d.text((x, 499), t, font=font, fill=(255, 255, 255))
        st.save(f"{out}f_{n:04d}.jpg", quality=90); n += 1

att = sorted(glob.glob(f"{W}{tags[0]}/attack_*.jpg"))
if att:
    sheet = Image.new("RGB", (480 * 4, 270 * 4))
    for j, p in enumerate(att[10:10 + 64:4][:16]):
        sheet.paste(Image.open(p).resize((480, 270)), ((j % 4) * 480, (j // 4) * 270))
    sheet.save(f"{W}{tags[0]}_sheet.jpg", quality=85)
print("frames", n)
