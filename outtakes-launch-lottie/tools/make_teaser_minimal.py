"""Extremely minimal 1:1 teaser: near-black, a ghost of a match shot, one small date.

    python3 tools/make_teaser_minimal.py [photo-name]  ->  out/teaser-1x1-minimal.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
S = 1080
name = sys.argv[1] if len(sys.argv) > 1 else "celebrate-run"

im = Image.open(ROOT / f"brand/photos/{name}.jpg").convert("RGB")
w, h = im.size
side = min(w, h)
x0 = int(min(max(w * 0.46 - side / 2, 0), w - side))
im = im.crop((x0, 0, x0 + side, side)).resize((S, S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(38))

# almost black: the photo is only a faint warm presence in the middle
a = np.asarray(im).astype(np.float32) / 255
yy, xx = np.mgrid[0:S, 0:S] / S - 0.5
glow = np.clip(1 - (xx ** 2 + yy ** 2) * 4.2, 0, 1)[..., None] ** 1.6
a = 0.035 + a * 0.22 * glow
a += np.random.default_rng(2011).normal(0, 0.012, a.shape[:2])[..., None]
im = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8))

d = ImageDraw.Draw(im)
f = ImageFont.truetype(str(ROOT / "brand/fonts/ot-body-medium.ttf"), 30)
d.text((S / 2, S - 120), "20 . 11", font=f, fill=(116, 242, 96), anchor="ms")

out = ROOT / "out/teaser-1x1-minimal.png"
im.save(out)
print(out)
