"""1:1 'coming soon' Instagram teaser: a motion-blurred match shot, no logo, just the date.

    python3 tools/make_teaser.py [photo-name]   ->  out/teaser-1x1.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
S = 1080
GREEN, CREAM = (116, 242, 96), (240, 235, 228)
name = sys.argv[1] if len(sys.argv) > 1 else "celebrate-run"
font = lambda f, s: ImageFont.truetype(str(ROOT / "brand/fonts" / f), s)

# square cover crop around the subject
im = Image.open(ROOT / f"brand/photos/{name}.jpg").convert("RGB")
w, h = im.size
side = min(w, h)
x0 = int(min(max(w * 0.46 - side / 2, 0), w - side))
im = im.crop((x0, 0, x0 + side, side)).resize((S, S), Image.LANCZOS)

# horizontal motion blur (a fast pan): average of shifted copies, then a soft gaussian
a = np.asarray(im).astype(np.float32)
acc = np.zeros_like(a)
shifts = range(-70, 71, 5)
for d in shifts:
    acc += np.roll(a, d, axis=1)
a = acc / len(shifts)
im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))

# grade: darker, cooler shadows, vignette, grain
a = np.asarray(im).astype(np.float32) / 255
a = a ** 1.25 * 0.78
yy, xx = np.mgrid[0:S, 0:S] / S - 0.5
vig = np.clip(1 - (xx ** 2 + yy ** 2) * 1.9, 0.25, 1)[..., None]
a = a * vig
a += np.random.default_rng(2011).normal(0, 0.025, a.shape[:2])[..., None]
im = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8))

d = ImageDraw.Draw(im)
# viewfinder brackets + focus point + REC dot
m, L, t = 64, 70, 4
for cx, cy, sx, sy in ((m, m, 1, 1), (S - m, m, -1, 1), (m, S - m, 1, -1), (S - m, S - m, -1, -1)):
    d.line([(cx, cy), (cx + sx * L, cy)], fill=CREAM, width=t)
    d.line([(cx, cy), (cx, cy + sy * L)], fill=CREAM, width=t)
c = S // 2
d.rectangle([c - 34, c - 24, c + 34, c + 24], outline=(*CREAM, ), width=2)
d.ellipse([m + 24, m + 26, m + 42, m + 44], fill=(235, 64, 52))
d.text((m + 54, m + 22), "REC", font=font("ot-body-medium.ttf", 26), fill=CREAM)
d.text((S - m - 24, m + 22), "1/2000  f2.8", font=font("ot-body.ttf", 26), fill=CREAM, anchor="ra")

# the only real information: the date
big = font("ot-wordmark.ttf", 230)
d.text((m + 20, S - m - 120), "22.11", font=big, fill=GREEN, anchor="ls")
d.text((m + 26, S - m - 62), "5PM SGT  ·  SOMETHING'S ABOUT TO STEP INTO FRAME", font=font("ot-label.ttf", 28), fill=CREAM, anchor="ls")

out = ROOT / "out/teaser-1x1.png"
im.save(out)
print(out)
