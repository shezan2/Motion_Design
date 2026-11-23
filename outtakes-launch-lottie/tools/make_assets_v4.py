"""Bake the v4 image assets (run once; the outputs are committed under brand/photos/v4-*).

    python3 tools/make_assets_v4.py <folder with the full-resolution originals>

Skottie draws image layers whole, so anything that needs a precise crop, a duotone, a holographic fill or an
alpha mask is prepared here instead of inside the Lottie:

* hook shots: each photo cropped (portrait and landscape) so its subject (the ball, or a face) lands on a chosen
  point; baked at 1.1x so the Lottie can push in about the subject without ever going below native resolution.
  Subject points go to brand/photos/v4-meta.json for the focus-point animation.
* hero plate: the celebration shot with a horizontal motion blur and a warm grade (the site's blurred hero).
* sport cards: duotone crops in the site's "Browse by sport" colours.
* step glyphs: ONE..FOUR and 1..4 in the condensed italic, filled with an iridescent foil texture.
* avatar: a round face crop with alpha.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "brand" / "photos"
FONTS = ROOT / "brand" / "fonts"

# original file names (uploads) -> photo names, matched by content
ORIGINALS = {
    "basketball": "f5ac2705-image.jpg", "celebrate-fists": "db8a4834-image.jpg", "celebrate-run": "6a0578c8-image.jpg",
    "floodlight-profile": "0d15526c-image.jpg", "heart-hands": "a0b34a75-image.jpg", "kids-duel": "6600cfab-image.jpg",
    "motion-blur": "0839677e-image.jpg", "number-10": "1749d568-image.jpg", "point-orange": "8737c27f-image.jpg",
    "portrait-flare": "8cdd1c9e-image.jpg", "sepak-takraw": "dc4ed9a1-image.jpg", "smile-orange": "7cf5d9eb-image.jpg",
    "stretch-ball": "ddeb5fdc-image.jpg", "tackle-night": "33b15149-image.jpg", "team-backs": "71169636-image.jpg",
    "team-talk": "e7f9645b-image.jpg",
}

# subject point (original px) and its size, for the hook's focus point
SUBJECTS = {
    "tackle-night": ((1690, 1456), 192, "ball"), "kids-duel": ((384, 455), 104, "ball"),
    "sepak-takraw": ((1028, 517), 72, "ball"), "stretch-ball": ((1898, 1294), 205, "ball"),
    "basketball": ((469, 425), 120, "ball"), "motion-blur": ((277, 1507), 240, "ball"),
    "point-orange": ((1316, 411), 195, "face"), "portrait-flare": ((1140, 1000), 520, "face"),
    "celebrate-run": ((1139, 416), 135, "face"),
}
# where each subject should land (fraction of frame) and extra zoom, per format: a zig-zag for the eye to follow
HOOK = {
    "portrait": [("tackle-night", (0.60, 0.64), 1.40), ("kids-duel", (0.36, 0.50), 1.05),
                 ("sepak-takraw", (0.58, 0.36), 1.25), ("stretch-ball", (0.40, 0.60), 1.25),
                 ("basketball", (0.52, 0.33), 1.00), ("motion-blur", (0.34, 0.70), 1.50),
                 ("point-orange", (0.58, 0.40), 1.10), ("portrait-flare", (0.50, 0.40), 1.00),
                 ("celebrate-run", (0.50, 0.36), 1.00)],
    "landscape": [("tackle-night", (0.62, 0.68), 1.10), ("kids-duel", (0.36, 0.52), 1.30),
                  ("sepak-takraw", (0.56, 0.36), 1.40), ("stretch-ball", (0.40, 0.62), 1.20),
                  ("basketball", (0.54, 0.36), 1.00), ("motion-blur", (0.30, 0.70), 1.15),
                  ("point-orange", (0.58, 0.40), 1.25), ("portrait-flare", (0.52, 0.42), 1.00),
                  ("celebrate-run", (0.50, 0.40), 1.05)],
}
FRAMES = {"portrait": (1080, 1920), "landscape": (1920, 1080)}
BAKE = 1.1  # baked resolution over frame size, so a push-in stays at or above native


def load(folder: Path, name: str) -> Image.Image:
    return Image.open(folder / ORIGINALS[name]).convert("RGB")


def framed(im: Image.Image, subj, want, zoom, fw, fh):
    """Crop/scale so `subj` lands as near `want` (px) as coverage allows. Returns (image fw x fh, subject px, scale)."""
    w, h = im.size
    s = max(fw / w, fh / h) * zoom
    left = min(0.0, max(fw - w * s, want[0] - subj[0] * s))
    top = min(0.0, max(fh - h * s, want[1] - subj[1] * s))
    big = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    out = big.crop((round(-left), round(-top), round(-left) + fw, round(-top) + fh))
    return out, (subj[0] * s + left, subj[1] * s + top), s


def bake_hook(folder: Path, meta: dict):
    for fmt, shots in HOOK.items():
        fw, fh = FRAMES[fmt]
        meta[fmt] = []
        for name, (wx, wy), zoom in shots:
            (bx, by), size, kind = SUBJECTS[name]
            im = load(folder, name)
            out, (sx, sy), s = framed(im, (bx, by), (wx * fw * BAKE, wy * fh * BAKE), zoom,
                                      round(fw * BAKE), round(fh * BAKE))
            out = grade(out, warm=0.02)
            fn = f"v4-hook-{fmt[0]}-{name}.jpg"
            out.save(OUT / fn, quality=90)
            meta[fmt].append({"name": name, "file": fn, "w": out.width, "h": out.height, "kind": kind,
                              "subject": [round(sx / BAKE, 1), round(sy / BAKE, 1)],
                              "subject_size": round(size * s / BAKE, 1)})
            print(f"{fn}: subject at {meta[fmt][-1]['subject']} size {meta[fmt][-1]['subject_size']}")


def grade(im: Image.Image, warm=0.0, lift=0.0, contrast=1.0) -> Image.Image:
    a = np.asarray(im).astype(np.float32) / 255
    a = (a - 0.5) * contrast + 0.5 + lift
    a[..., 0] += warm
    a[..., 2] -= warm
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def motion_blur_x(im: Image.Image, length: int) -> Image.Image:
    a = np.asarray(im).astype(np.float32)
    k = np.ones(length) / length
    pad = length // 2
    p = np.pad(a, ((0, 0), (pad, pad), (0, 0)), mode="edge")
    c = np.cumsum(p, axis=1)
    c = np.concatenate([np.zeros_like(c[:, :1]), c], axis=1)
    out = (c[:, length:] - c[:, :-length])[:, : a.shape[1]] / length
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def bake_hero(folder: Path):
    im = load(folder, "celebrate-run")
    for fmt, (fw, fh) in FRAMES.items():
        out, _, _ = framed(im, (1139, 600), (fw * 0.5, fh * 0.5), 1.0 if fmt == "landscape" else 1.0, fw, fh)
        out = motion_blur_x(out, int(fw * 0.09))
        out = out.filter(ImageFilter.GaussianBlur(3))
        a = np.asarray(out).astype(np.float32) / 255
        # warm, slightly lifted shadows, like the site's blurred runners
        a = a ** 0.92
        a[..., 0] = np.clip(a[..., 0] * 1.10 + 0.04, 0, 1)
        a[..., 1] = np.clip(a[..., 1] * 0.93 + 0.01, 0, 1)
        a[..., 2] = np.clip(a[..., 2] * 0.82, 0, 1)
        out = Image.fromarray((a * 255).astype(np.uint8))
        out.save(OUT / f"v4-hero-{fmt[0]}.jpg", quality=90)
        print(f"v4-hero-{fmt[0]}.jpg")


SPORTS = [  # label, photo, focus (fraction), shadow colour, highlight colour
    ("BASKETBALL", "basketball", (0.55, 0.40), "#6b1702", "#ffb07a"),
    ("SEPAK TAKRAW", "sepak-takraw", (0.47, 0.42), "#063b4a", "#7fe3ee"),
    ("FUTSAL", "point-orange", (0.50, 0.38), "#5a0718", "#ff9fb3"),
    ("FOOTBALL", "tackle-night", (0.58, 0.55), "#0a4a17", "#9dff8a"),
]


def duotone(im: Image.Image, dark: str, light: str) -> Image.Image:
    g = np.asarray(im.convert("L")).astype(np.float32) / 255
    g = np.clip((g - 0.08) / 0.84, 0, 1) ** 0.9
    d = np.array([int(dark[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
    l = np.array([int(light[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
    rgb = d[None, None] * (1 - g[..., None]) + l[None, None] * g[..., None]
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))


def bake_sports(folder: Path):
    cw, ch = 480, 672
    for label, name, (fx, fy), dark, light in SPORTS:
        im = load(folder, name)
        w, h = im.size
        out, _, _ = framed(im, (fx * w, fy * h), (cw / 2, ch / 2), 1.0, cw, ch)
        out = duotone(out, dark, light)
        fn = f"v4-sport-{name}.jpg"
        out.save(OUT / fn, quality=90)
        print(fn)


def foil_texture(w: int, h: int, seed: int) -> np.ndarray:
    """Iridescent oil-slick foil: hue driven by smooth noise and a diagonal sweep, with a pearly sheen."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = xx / w, yy / h
    field = 0.9 * u + 0.6 * v
    for k in range(4):
        fx, fy, ph = rng.uniform(0.6, 2.2), rng.uniform(0.6, 2.2), rng.uniform(0, 6.3)
        field += 0.22 / (k + 1) * np.sin(2 * np.pi * (fx * u + fy * v) + ph) * np.cos(2 * np.pi * fy * u - ph)
    hue = (field * 0.85) % 1.0
    # hue -> rgb with a palette that leans green/yellow/magenta/cyan like the site's foil cards
    stops = np.array([[0.30, 1.00, 0.18], [0.96, 0.95, 0.20], [1.00, 0.52, 0.18], [0.95, 0.25, 0.70],
                      [0.45, 0.35, 1.00], [0.10, 0.90, 0.95], [0.30, 1.00, 0.18]], np.float32)
    t = hue * (len(stops) - 1)
    i = np.floor(t).astype(int)
    f = (t - i)[..., None]
    rgb = stops[i] * (1 - f) + stops[np.minimum(i + 1, len(stops) - 1)] * f
    sheen = 0.5 + 0.5 * np.sin(2 * np.pi * (2.3 * u - 1.1 * v) + 1.0)
    rgb = rgb * (0.82 + 0.18 * sheen[..., None]) + 0.12 * sheen[..., None] ** 6
    return np.clip(rgb, 0, 1)


def bake_glyphs():
    font_path = FONTS / "ot-wordmark.ttf"
    jobs = [(t, 260, f"v4-holo-word-{t.lower()}.png") for t in ("ONE", "TWO", "THREE", "FOUR")]
    jobs += [(n, 900, f"v4-holo-num-{n}.png") for n in ("1", "2", "3", "4")]
    meta = {}
    for k, (text, size, fn) in enumerate(jobs):
        font = ImageFont.truetype(str(font_path), size)
        l, t, r, b = font.getbbox(text)
        pad = int(size * 0.06)
        w, h = r - l + 2 * pad, b - t + 2 * pad
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).text((pad - l, pad - t), text, font=font, fill=255)
        tex = foil_texture(w, h, seed=11 + k)
        rgba = np.dstack([tex * 255, np.asarray(mask, np.float32)]).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(OUT / fn)
        meta[fn] = {"w": w, "h": h, "baseline_from_top": pad - t + font.getmetrics()[0] - (font.getmetrics()[0])}
        print(fn, w, h)
    return meta


def bake_avatar(folder: Path):
    im = load(folder, "portrait-flare")
    cx, cy, r = 1140, 960, 470
    c = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((320, 320), Image.LANCZOS)
    mask = Image.new("L", (1280, 1280), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 1279, 1279), fill=255)
    mask = mask.resize((320, 320), Image.LANCZOS)
    c.putalpha(mask)
    c.save(OUT / "v4-avatar.png")
    print("v4-avatar.png")


def main():
    folder = Path(sys.argv[1])
    meta = {}
    bake_hook(folder, meta)
    bake_hero(folder)
    bake_sports(folder)
    meta["glyphs"] = bake_glyphs()
    bake_avatar(folder)
    (OUT / "v4-meta.json").write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
