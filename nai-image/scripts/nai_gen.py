#!/usr/bin/env python3
"""NovelAI Diffusion V5 image generator for game / art assets (any project).

Prompts come from one of:
  1. A prompt folder (default "./Art Prompts" if it exists, or --prompts DIR / env NAI_PROMPTS_DIR):
       "[...] NN_*.txt"         one prompt per "## N." / "### N-A." section  -> key "NN:N-A"
       "[Base Prompts].txt"     appended to every prompt (style / artists / quality)
       "[Negative Prompts].txt" the negative prompt
  2. An inline prompt: --prompt "..." (base / negative files above are still applied unless --no-base)

Inside a section (or with --char), one character per line keeps two people from blending into one face
(V4+ char_captions):
  @char C3: <caption for one character> || <that character's negative>
The grid position (A-E left->right, 1-5 top->bottom, like the NAI UI) is optional.

Transparent background (V5 alpha PNG): automatic when the prompt contains "{{black background, simple background}}"
or "on a solid black background" (rewritten to a real transparent background), or forced with --transparent.

Size: an aspect hint in the section header (16:9, 21:9, 3:2, 1:1, 2:3, 9:16, 9:21; default 1:1) or --size WxH.
Anything above 1024x1024 px or 28 steps costs Anlas even on Opus.

Token: env NAI_API_KEY; on Windows also read from the User environment (registry) if the process didn't inherit it.
It is only ever sent in the Authorization header - never printed or written to disk.

  python -I nai_gen.py --list
  python -I nai_gen.py 04:1-B 05:2 --n 2 [--seed 123] [--size 832x1216]
  python -I nai_gen.py --prompt "no humans, game asset, wooden crate, ..." --name crate --transparent --n 3
  python -I nai_gen.py 07:3 --dry-run            # print the assembled request, no API call

Output (default ./_nai_out, keep it out of version control):
  <out>/<name>/<name>_<seed>.png         raw image
  <out>/<name>/<name>_<seed>_clean.png   alpha fringe removed + trimmed (transparent only)
  <out>/<name>/<name>_<seed>.json        exact request body (no token) - reproducible with the same seed
"""
import argparse, glob, io, json, os, random, re, sys, time, urllib.error, urllib.request, zipfile

URL = "https://image.novelai.net/ai/generate-image"
UA = "nai-asset-tool/1.0"            # urllib's default UA is rejected by Cloudflare (error 1010)
FREE_PIXELS = 1024 * 1024            # Opus free-generation limit (also steps <= 28, 1 image per request)
FREE_STEPS = 28

ASPECTS = {"21:9": (1472, 704), "16:9": (1344, 768), "3:2": (1216, 832), "1:1": (1024, 1024),
           "2:3": (832, 1216), "9:16": (768, 1344), "9:21": (704, 1472)}
CHAR = re.compile(r"^@char\s*(?:([A-Ea-e])([1-5]))?\s*:\s*(.*)$")
HEADER = re.compile(r"^(#{2,3})\s+(\d+(?:-[A-Za-z0-9]+)?)\.\s*(.*)$")
BLACK_TAG = re.compile(r"\{*\s*black background\s*,\s*simple background\s*\}*\s*,?\s*")
BLACK_PHRASE = re.compile(r"(?:isolated\s+)?(?:cleanly\s+)?on a solid black background(?: for easy alpha extraction)?")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip().rstrip(",")


def join(*parts):
    return ", ".join(p.strip().strip(",") for p in parts if p and p.strip())


def aspect_of(title):
    for key in sorted(ASPECTS, key=len, reverse=True):
        if re.search(rf"(?<!\d){re.escape(key)}(?!\d)", title):
            return ASPECTS[key]
    return None


def parse_char(text, pos_letter=None, pos_row=None):
    caption, _, neg = text.partition("||")
    pos = None
    if pos_letter:
        pos = {"x": 0.1 + 0.2 * "abcde".index(pos_letter.lower()), "y": 0.1 + 0.2 * (int(pos_row) - 1)}
    return {"caption": caption.strip().rstrip(","), "neg": neg.strip().rstrip(","), "pos": pos}


def load_sections(prompt_dir):
    """{ '04:1-A': {title, prompt, chars, size, file} } from every '[..] NN_*.txt' in the prompt folder."""
    sections = {}
    if not prompt_dir or not os.path.isdir(prompt_dir):
        return sections
    for path in sorted(glob.glob(os.path.join(glob.escape(prompt_dir), "*.txt"))):
        m = re.search(r"\]\s*(\d\d)_", os.path.basename(path))
        if not m:
            continue
        num, cur, parent_size = m.group(1), None, None
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                h = HEADER.match(line)
                if h:
                    size = aspect_of(h.group(3))
                    if h.group(1) == "##":
                        parent_size = size
                    cur = {"title": h.group(3), "lines": [], "chars": [], "size": size or parent_size or ASPECTS["1:1"],
                           "file": os.path.basename(path)}
                    sections[f"{num}:{h.group(2)}"] = cur
                elif cur is not None and CHAR.match(line):
                    c = CHAR.match(line)
                    cur["chars"].append(parse_char(c.group(3), c.group(1), c.group(2)))
                elif cur is not None and line and not line.startswith(("#", "---", "//")):
                    cur["lines"].append(line)
    out = {}
    for key, s in sections.items():
        if s["lines"]:  # parents of sub-sections carry no prompt
            s["prompt"] = " ".join(s["lines"])
            out[key] = s
    return out


def build(section, size, seed, base, neg, args):
    prompt = section["prompt"]
    transparent = bool(BLACK_TAG.search(prompt)) or args.transparent
    if transparent:
        prompt = BLACK_TAG.sub("", prompt)
        prompt = BLACK_PHRASE.sub("on a transparent background", prompt)
    # the tag must sit before the base (quality) tags to take
    prompt = join(prompt, "2.0::transparent background::" if transparent else "", base)
    w, h = size
    if w % 64 or h % 64:
        raise SystemExit(f"size {w}x{h}: both sides must be multiples of 64")
    if w * h > FREE_PIXELS or args.steps > FREE_STEPS:
        print(f"  ! {w}x{h}, {args.steps} steps is beyond the Opus free tier (costs Anlas)")
    params = {
        "params_version": 3,
        "width": w, "height": h,
        "scale": args.scale,
        "sampler": "k_euler_ancestral",
        "steps": args.steps,
        "n_samples": 1,
        "seed": seed,
        "noise_schedule": "karras",
        "negative_prompt": neg,
        "v4_prompt": {"caption": {"base_caption": prompt, "char_captions": []}, "use_coords": False, "use_order": True},
        "v4_negative_prompt": {"caption": {"base_caption": neg, "char_captions": []}, "legacy_uc": False},
    }
    chars = section.get("chars") or []
    if chars:
        centre = lambda c: c["pos"] or {"x": 0.5, "y": 0.5}
        params["v4_prompt"]["caption"]["char_captions"] = [{"char_caption": c["caption"], "centers": [centre(c)]} for c in chars]
        params["v4_negative_prompt"]["caption"]["char_captions"] = [{"char_caption": c["neg"], "centers": [centre(c)]} for c in chars]
        params["v4_prompt"]["use_coords"] = any(c["pos"] for c in chars)
        params["characterPrompts"] = [{"prompt": c["caption"], "uc": c["neg"], "center": centre(c), "enabled": True} for c in chars]
    if transparent:
        # V5 web-client behaviour: the tag alone or these flags alone are not enough - send both.
        params["straight_alpha"] = True
        params["tag_hint_transparent_background"] = True
    body = {"input": prompt, "model": args.model, "action": "generate", "parameters": params}
    return body, transparent


def token():
    t = os.environ.get("NAI_API_KEY")
    if not t and os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                t = winreg.QueryValueEx(k, "NAI_API_KEY")[0]
        except OSError:
            t = None
    if not t:
        raise SystemExit("NAI_API_KEY is not set (env var, or the Windows User environment). Ask the user to set it; "
                         "never ask them to paste the token into the chat.")
    return t


def request(body, tok):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "User-Agent": UA,
    })
    for attempt in range(5):
        try:
            data = urllib.request.urlopen(req, timeout=240).read()
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                return z.read(z.namelist()[0])
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:500]
            if e.code == 429 and attempt < 4:   # one generation at a time per account
                print("  429 busy, retrying...", flush=True)
                time.sleep(5 * (attempt + 1))
                continue
            hint = {401: " (token invalid/expired)", 402: " (needs Opus or Anlas for this size/steps)",
                    403: " (Cloudflare: check User-Agent)"}.get(e.code, "")
            raise SystemExit(f"HTTP {e.code}{hint}: {msg}")


def clean(png_bytes, alpha_floor, pad):
    """Kill faint alpha noise, zero RGB under full transparency (no coloured fringe when filtered), trim to content."""
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    r, g, b, a = im.split()
    a = a.point(lambda v: 0 if v < alpha_floor else v)
    mask = a.point(lambda v: 255 if v > 0 else 0)
    black = Image.new("L", im.size, 0)
    r, g, b = (Image.composite(c, black, mask) for c in (r, g, b))
    im = Image.merge("RGBA", (r, g, b, a))
    box = a.getbbox()
    if box:
        x0, y0, x1, y1 = box
        im = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
    hist = a.histogram()
    return im, hist[0] / sum(hist)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # prompt titles may be non-ASCII; cp949 consoles choke
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("keys", nargs="*", help="section keys like 04:1-B 05:2")
    ap.add_argument("--prompts", default=os.environ.get("NAI_PROMPTS_DIR") or "Art Prompts", help="prompt folder")
    ap.add_argument("--list", action="store_true", help="list section keys in the prompt folder")
    ap.add_argument("--prompt", help="inline prompt instead of section keys")
    ap.add_argument("--char", action="append", default=[], metavar="'[C3:] caption || negative'",
                    help="character caption for the inline prompt (repeatable)")
    ap.add_argument("--name", default="inline", help="output name for --prompt")
    ap.add_argument("--base", help="base prompt file (default: '[Base Prompts].txt' in the prompt folder)")
    ap.add_argument("--negative", help="negative prompt file (default: '[Negative Prompts].txt' in the prompt folder)")
    ap.add_argument("--negative-text", help="negative prompt text (overrides the file)")
    ap.add_argument("--no-base", action="store_true", help="don't append the base prompt")
    ap.add_argument("--transparent", action="store_true", help="force a transparent background")
    ap.add_argument("--n", type=int, default=1, help="images per prompt (one request each)")
    ap.add_argument("--seed", type=int, help="first seed (then +1 per image)")
    ap.add_argument("--size", help="WxH, multiples of 64, e.g. 832x1216")
    ap.add_argument("--steps", type=int, default=23)
    ap.add_argument("--scale", type=float, default=5.0, help="prompt guidance")
    ap.add_argument("--model", default="nai-diffusion-5-full")
    ap.add_argument("--out", default=os.environ.get("NAI_OUT_DIR") or "_nai_out")
    ap.add_argument("--alpha-floor", type=int, default=24)
    ap.add_argument("--pad", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="print the request body, don't call the API")
    args = ap.parse_args()

    sections = load_sections(args.prompts)
    if args.list or (not args.keys and not args.prompt):
        if not sections:
            print(f"no '[..] NN_*.txt' prompt files in '{args.prompts}' (use --prompts DIR or --prompt)")
        for k, s in sections.items():
            print(f"{k:8} {s['size'][0]}x{s['size'][1]:<5} {s['title']}  [{s['file']}]")
        return

    def opt_file(explicit, default_name):
        path = explicit or os.path.join(args.prompts, default_name)
        if explicit and not os.path.isfile(path):
            raise SystemExit(f"not found: {path}")
        return read(path) if os.path.isfile(path) else ""

    base = "" if args.no_base else opt_file(args.base, "[Base Prompts].txt")
    neg = args.negative_text if args.negative_text is not None else opt_file(args.negative, "[Negative Prompts].txt")

    jobs = []
    if args.prompt:
        chars = []
        for c in args.char:
            m = re.match(r"^\s*([A-Ea-e])([1-5])\s*:\s*(.*)$", c)
            chars.append(parse_char(m.group(3), m.group(1), m.group(2)) if m else parse_char(c))
        jobs.append((args.name, {"prompt": args.prompt, "chars": chars, "size": ASPECTS["1:1"]}))
    for key in args.keys:
        if key not in sections:
            raise SystemExit(f"unknown key {key} (see --list)")
        jobs.append((key.replace(":", "_"), sections[key]))

    tok = None if args.dry_run else token()
    for name, section in jobs:
        size = tuple(int(v) for v in args.size.lower().split("x")) if args.size else section["size"]
        os.makedirs(os.path.join(args.out, name), exist_ok=True)
        for i in range(args.n):
            seed = (args.seed + i) if args.seed is not None else random.randint(1, 2**32 - 1)
            body, transparent = build(section, size, seed, base, neg, args)
            if args.dry_run:
                print(json.dumps(body, ensure_ascii=False, indent=1))
                continue
            print(f"{name} seed={seed} {size[0]}x{size[1]} ...", flush=True)
            png = request(body, tok)
            stem = os.path.join(args.out, name, f"{name}_{seed}")
            with open(stem + ".png", "wb") as f:
                f.write(png)
            with open(stem + ".json", "w", encoding="utf-8") as f:
                json.dump(body, f, ensure_ascii=False, indent=1)
            if transparent:
                im, clear = clean(png, args.alpha_floor, args.pad)
                im.save(stem + "_clean.png")
                print(f"  -> {stem}_clean.png {im.size} transparent={clear:.0%}")
            else:
                print(f"  -> {stem}.png")


if __name__ == "__main__":
    main()
