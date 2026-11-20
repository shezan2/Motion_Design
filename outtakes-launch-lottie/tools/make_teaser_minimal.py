"""Extremely minimal 1:1 teaser: near-black, a ghost of a match shot, one small date.

    python3 tools/make_teaser_minimal.py [photo-name]          ->  out/teaser-1x1-minimal.png
    python3 tools/make_teaser_minimal.py [photo-name] --more   ->  out/teaser-1x1-mid.png (slightly less minimal)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
S = 1080
MORE = "--more" in sys.argv
args = [x for x in sys.argv[1:] if not x.startswith("--")]
name = args[0] if args else "celebrate-run"

im = Image.open(ROOT / f"brand/photos/{name}.jpg").convert("RGB")
w, h = im.size
side = min(w, h)
x0 = int(min(max(w * 0.46 - side / 2, 0), w - side))
im = im.crop((x0, 0, x0 + side, side)).resize((S, S), Image.LANCZOS)
if MORE:  # a fast-pan motion blur: the action reads, the faces don't
    a = np.asarray(im).astype(np.float32)
    shifts = range(-60, 61, 4)
    im = Image.fromarray((sum(np.roll(a, k, axis=1) for k in shifts) / len(shifts)).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(6))
else:
    im = im.filter(ImageFilter.GaussianBlur(38))

# almost black: the photo is only a faint warm presence in the middle
a = np.asarray(im).astype(np.float32) / 255
yy, xx = np.mgrid[0:S, 0:S] / S - 0.5
glow = np.clip(1 - (xx ** 2 + yy ** 2) * 4.2, 0, 1)[..., None] ** 1.6
a = 0.035 + a * (0.5 if MORE else 0.22) * (glow ** (0.6 if MORE else 1))
a += np.random.default_rng(2011).normal(0, 0.012, a.shape[:2])[..., None]
im = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8))

d = ImageDraw.Draw(im)
font = lambda f, size: ImageFont.truetype(str(ROOT / "brand/fonts" / f), size)
if MORE:
    c = S // 2
    d.rectangle([c - 30, c - 21, c + 30, c + 21], outline=(240, 235, 228), width=2)   # a lone focus point
    d.text((S / 2, S - 150), "22.11", font=font("ot-wordmark.ttf", 96), fill=(116, 242, 96), anchor="ms")
    d.text((S / 2, S - 104), "5PM SGT", font=font("ot-body-medium.ttf", 24), fill=(240, 235, 228), anchor="ms")
else:
    d.text((S / 2, S - 120), "22 . 11", font=font("ot-body-medium.ttf", 30), fill=(116, 242, 96), anchor="ms")

out = ROOT / ("out/teaser-1x1-mid.png" if MORE else "out/teaser-1x1-minimal.png")
im.save(out)
print(out)
