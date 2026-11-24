"""8-second mysterious launch teaser (Ozen Flow for Outtakes): a photographer's viewfinder hunting in the dark.

    python3 tools/make_teaser_8s.py            -> out/outtakes-teaser-8s-9x16.mp4
    python3 tools/make_teaser_8s.py square     -> out/outtakes-teaser-8s-1x1.mp4

Picture (30 fps, 240 frames), one treatment over everything (dark, desaturated, green-tinted shadows, grain):
  0-12    black; a lone focus point blinks
  12-134  glimpses of match shots, cuts accelerating 14 f -> 2 f, each one smeared, pushing in, the focus
          brackets snapping onto the subject; a tiny caption stays put underneath ("persistent caption")
  134-156 stutter: 1-frame photo / black / green
  156-176 silence and black (the breath before the payoff)
  176-178 OUTTAKES, two frames, subliminal
  186-240 30.11 pulls into focus, the brackets lock green, a shutter fires; 5PM SGT; held 1.2 s
Sound is synthesised here (shutters, sub pulses, riser, autofocus beeps, impacts) and cut to the same frames.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SQUARE = len(sys.argv) > 1 and sys.argv[1] == "square"
W, H = (1080, 1080) if SQUARE else (1080, 1920)
FPS, N = 30, 240
GREEN, CREAM = (116, 242, 96), (240, 235, 228)
rng = np.random.default_rng(3011)
font = lambda f, s: ImageFont.truetype(str(ROOT / "brand/fonts" / f), s)
META = json.loads((ROOT / "brand/photos/v4-meta.json").read_text())["portrait"]


# ------------------------------------------------------------------ the treatment
def blur_line(a, L, axis):
    if L < 2:
        return a
    c = np.cumsum(np.pad(a, [(L, L) if i == axis else (0, 0) for i in range(3)], mode="edge"), axis=axis)
    sl = lambda s, e: tuple(slice(s, e) if i == axis else slice(None) for i in range(3))
    n = a.shape[axis]
    return (c[sl(L + L // 2, L + L // 2 + n)] - c[sl(L // 2, L // 2 + n)]) / L


def grade(a):
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 0.35                       # mostly drained of colour
    a = np.clip((a - 0.06) * 1.25, 0, 1) ** 1.35 * 0.72
    a[..., 1] *= 1.06                                # green-tinted shadows
    a[..., 0] *= 0.94
    return a


shots = []
for k, sh in enumerate(META):
    im = Image.open(ROOT / "brand/photos" / sh["file"]).convert("RGB")
    iw, ih = im.size
    sx, sy = sh["subject"]
    pad = 1.18
    if SQUARE:
        side = int(iw / pad * 0.98)
        x0 = int(np.clip(sx - side / 2, 0, iw - side))
        y0 = int(np.clip(sy - side / 2, 0, ih - side))
        im = im.crop((x0, y0, x0 + side, y0 + side))
        sx, sy = sx - x0, sy - y0
        iw = ih = side
    bw, bh = int(W * pad), int(H * pad)
    k_ = max(bw / iw, bh / ih)
    im = im.resize((int(iw * k_), int(ih * k_)), Image.BILINEAR)
    sx, sy = sx * k_, sy * k_
    x0 = int(np.clip(sx - bw / 2, 0, im.width - bw))
    y0 = int(np.clip(sy - bh / 2, 0, im.height - bh))
    im = im.crop((x0, y0, x0 + bw, y0 + bh))
    a = np.asarray(im).astype(np.float32) / 255
    axis = 1 if k % 3 else 0
    a = grade(blur_line(a, 46 + 10 * (k % 4), axis))
    shots.append((a, (sx - x0, sy - y0), sh["subject_size"] * k_))

yy, xx = np.mgrid[0:H, 0:W]
vig = np.clip(1 - (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2.2, 0.15, 1)[..., None].astype(np.float32)


def frame_photo(i, t):
    """Shot i at progress t (0..1): a slow push toward the subject."""
    a, (sx, sy), _ = shots[i % len(shots)]
    bh, bw = a.shape[:2]
    z = 1 + 0.07 * t
    cw, ch = bw / 1.18 / z * 1.0, bh / 1.18 / z
    cx = np.clip(sx, cw / 2, bw - cw / 2)
    cy = np.clip(sy, ch / 2, bh - ch / 2)
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))
    im = Image.fromarray((a * 255).astype(np.uint8)).crop(box).resize((W, H), Image.BILINEAR)
    sub = ((sx - box[0]) * W / (box[2] - box[0]), (sy - box[1]) * H / (box[3] - box[1]))
    return np.asarray(im).astype(np.float32) / 255 * vig, sub


def brackets(d, cx, cy, size, colour, w=4):
    L = size * 0.28
    for sx_ in (-1, 1):
        for sy_ in (-1, 1):
            x, y = cx + sx_ * size / 2, cy + sy_ * size / 2
            d.line([(x, y), (x - sx_ * L, y)], fill=colour, width=w)
            d.line([(x, y), (x, y - sy_ * L)], fill=colour, width=w)


# ------------------------------------------------------------------ the schedule
durs = [14, 12, 11, 10, 9, 8, 7, 6, 5, 5, 4, 4, 3, 3, 2, 2, 2, 2]
gaps = [3, 2, 2, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
plan, f = [], 12
for k, (d_, g) in enumerate(zip(durs, gaps)):
    plan.append((f, f + d_, k))
    f += d_ + g
STUTTER0, STUTTER1, FLASH_WM, DATE0 = f, f + 22, 176, 179
LOCK, SHOT, SUB = 192, 194, 198
cues = []  # (frame, kind, gain)

cap_font = font("ot-label.ttf", 24)
CAPTION = "SOMETHING'S ABOUT TO STEP INTO FRAME"
cap_y = H - (190 if SQUARE else 540)
wm_font = font("ot-wordmark.ttf", 230 if not SQUARE else 200)
date_font = font("ot-wordmark.ttf", 300 if not SQUARE else 260)
sub_font = font("ot-body-medium.ttf", 34)

date_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(date_layer)
DATE_Y = H / 2 + (30 if not SQUARE else 10)
dd.text((W / 2, DATE_Y), "30.11", font=date_font, fill=(*GREEN, 255), anchor="mm")
db = dd.textbbox((W / 2, DATE_Y), "30.11", font=date_font, anchor="mm")


def ease(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3


ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                       str(ROOT / "out/_teaser_video.mp4")], stdin=subprocess.PIPE)
for fr in range(N):
    img = np.zeros((H, W, 3), np.float32) + 0.012
    marks = []    # (cx, cy, size, colour)
    caption = 10 <= fr < STUTTER1
    cur = next((p for p in plan if p[0] <= fr < p[1]), None)
    if cur:
        s0, s1, k = cur
        img, sub = frame_photo(k * 5 % len(shots), (fr - s0) / (s1 - s0))
        size = max(140, min(320, shots[k * 5 % len(shots)][2] * 1.2))
        snap = fr - s0
        marks.append((sub[0], sub[1], size * (1.6 if snap == 0 else 1.15 if snap == 1 else 1.0),
                      GREEN if snap >= 3 and (s1 - s0) > 5 else CREAM))
        if fr == s0:
            fl_ = 0.4 if (s1 - s0) > 4 else 0.16   # the shutter's flash on the cut, lighter as the cuts get fast
            img = img * (1 - fl_) + fl_
            cues.append((fr, "shutter", 0.35 + 0.5 * k / len(plan)))
            if k % 2 == 0:
                cues.append((fr, "thump", 0.5 + 0.4 * k / len(plan)))
        if snap == 3 and (s1 - s0) > 5:
            cues.append((fr, "af", 0.35))
    elif STUTTER0 <= fr < STUTTER1:
        m = (fr - STUTTER0) % 3
        if m == 0:
            img, _ = frame_photo(int(rng.integers(len(shots))), 0.5)
            cues.append((fr, "shutter", 0.7))
        elif m == 2:
            img[:] = np.array(GREEN) / 255 * 0.55
    elif fr < 12 or (STUTTER1 <= fr < FLASH_WM):
        if fr >= STUTTER1:   # the breath: a faint ghost of the last shot drifting, never a dead frame
            ghost, _ = frame_photo(plan[-1][2] * 5 % len(shots), (fr - STUTTER1) / (FLASH_WM - STUTTER1))
            img = img + ghost * 0.16
        marks.append((W / 2, H / 2, 70, CREAM if (fr // 8) % 2 == 0 else (110, 108, 104)))
        if fr in (STUTTER1 + 6, STUTTER1 + 14):
            cues.append((fr, "af_soft", 0.3))
    pil = Image.fromarray((np.clip(img + rng.normal(0, 0.03, img.shape[:2])[..., None], 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    if FLASH_WM <= fr < FLASH_WM + 2:
        d.rectangle([0, 0, W, H], fill=(8, 8, 9))
        d.text((W / 2, H / 2), "OUTTAKES", font=wm_font, fill=CREAM, anchor="mm")
    if fr >= DATE0:
        t = (fr - DATE0) / (LOCK - DATE0)
        r = 44 * (1 - ease(t))
        z = 1.08 - 0.08 * ease(t) + 0.025 * max(0, fr - LOCK) / (N - LOCK)
        lay = date_layer.filter(ImageFilter.GaussianBlur(r)) if r > 0.5 else date_layer
        if abs(z - 1) > 0.002:
            lay = lay.resize((int(W * z), int(H * z)), Image.BILINEAR)
            ox, oy = (lay.width - W) // 2, (lay.height - H) // 2
            lay = lay.crop((ox, oy, ox + W, oy + H))
        pil.paste(lay, (0, 0), lay)
        bw_, bh_ = (db[2] - db[0]) + 120, (db[3] - db[1]) + 120
        sc = 1.5 - 0.5 * ease((fr - DATE0) / (LOCK - 1 - DATE0))
        col = GREEN if fr >= LOCK else CREAM
        L = min(bw_, bh_) * 0.22
        cx, cy = W / 2, (db[1] + db[3]) / 2
        for sx_ in (-1, 1):
            for sy_ in (-1, 1):
                x, y = cx + sx_ * bw_ * sc / 2, cy + sy_ * bh_ * sc / 2
                d.line([(x, y), (x - sx_ * L, y)], fill=col, width=6)
                d.line([(x, y), (x, y - sy_ * L)], fill=col, width=6)
        if fr >= SUB:
            a_ = min(1, (fr - SUB) / 6)
            d.text((W / 2, db[3] + 110), "5PM SGT", font=sub_font, fill=tuple(int(v * a_) for v in CREAM), anchor="mm")
    for cx, cy, size, colr in marks:
        brackets(d, cx, cy, size, colr)
    if caption:
        d.text((W / 2, cap_y), CAPTION, font=cap_font, fill=(200, 196, 190), anchor="mm")
    if fr == SHOT:
        pil = Image.blend(pil, Image.new("RGB", (W, H), (255, 255, 255)), 0.35)
    ff.stdin.write(pil.tobytes())
ff.stdin.close()
ff.wait()
cues += [(STUTTER1, "cut_silence", 1), (FLASH_WM - 6, "suck", 0.7), (FLASH_WM, "impact", 1.0), (DATE0, "whoosh", 0.4),
         (LOCK, "af", 0.6), (SHOT, "shutter_big", 1.0), (SHOT, "impact_soft", 0.6)]

# ------------------------------------------------------------------ sound
SR = 48000
T = N / FPS
n = int(T * SR)
L = np.zeros(n)
R = np.zeros(n)
t_all = np.arange(n) / SR


def env(m, k):
    return np.exp(-np.arange(m) / SR * k)


def place(sig, t, g=1.0, pan=0.0):
    i = int(t * SR)
    s = sig[: max(0, n - i)] * g
    a = min(len(s), 120)
    s = s.copy()
    s[:a] *= np.linspace(0, 1, a)
    L[i:i + len(s)] += s * (1 - pan) ** 0.5
    R[i:i + len(s)] += s * (1 + pan) ** 0.5


def noise(m):
    return rng.standard_normal(m)


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(0, len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def shutter(big=1.0):
    m = int(0.09 * SR)
    s = noise(m) * env(m, 70)
    s2 = np.zeros(m)
    j = int(0.035 * SR)
    s2[j:] = noise(m - j) * env(m - j, 90) * 0.8
    click = np.diff(s + s2, prepend=0) * 0.6 + (s + s2) * 0.25
    return click * big


def thump(f0=52):
    m = int(0.35 * SR)
    tt = np.arange(m) / SR
    return np.sin(2 * np.pi * (f0 + 60 * np.exp(-tt * 40)) * tt) * env(m, 9)


def af(soft=False):
    m = int(0.05 * SR)
    tt = np.arange(m) / SR
    b = np.sin(2 * np.pi * 2350 * tt) * env(m, 30) * (0.5 if soft else 1)
    out = np.zeros(int(0.13 * SR))
    out[:m] += b
    out[int(0.07 * SR):int(0.07 * SR) + m] += b
    return out


def impact(m_s=1.6, f0=40):
    m = int(m_s * SR)
    tt = np.arange(m) / SR
    body = np.sin(2 * np.pi * (f0 + 90 * np.exp(-tt * 18)) * tt) * env(m, 2.6)
    crack = noise(m) * env(m, 30) * 0.5
    return body + crack


SPEC = {"shutter": lambda: shutter(), "shutter_big": lambda: shutter(1.6), "thump": lambda: thump(),
        "af": lambda: af(), "af_soft": lambda: af(True), "impact": lambda: impact(), "impact_soft": lambda: impact(1.2, 55) * 0.6}
for fr, kind, g in cues:
    if kind in SPEC:
        place(SPEC[kind](), fr / FPS, g, pan=float(rng.uniform(-0.3, 0.3)) if kind == "shutter" else 0.0)
# drone + riser under the montage, cut dead at the silence
cut = STUTTER1 / FPS
drone = (np.sin(2 * np.pi * 41 * t_all) + 0.4 * np.sin(2 * np.pi * 82.3 * t_all)) * np.clip(t_all / 2.5, 0, 1) * 0.25
rise = lowpass(noise(n), 2500) * np.clip((t_all - 1.5) / (cut - 1.5), 0, 1) ** 2 * 0.9
bed = (drone + rise) * (t_all < cut)
# a reversed swell into the subliminal wordmark
sw0, sw1 = (FLASH_WM - 18) / FPS, FLASH_WM / FPS
swell = lowpass(noise(n), 1800) * np.clip((t_all - sw0) / (sw1 - sw0), 0, 1) ** 3 * ((t_all >= sw0) & (t_all < sw1)) * 0.8
tail = (np.sin(2 * np.pi * 41 * t_all) * 0.18) * np.clip((t_all - DATE0 / FPS) / 0.6, 0, 1) * np.clip((T - t_all) / 0.6, 0, 1)
L += bed + swell + tail
R += bed + swell + tail
mix = np.stack([L, R], axis=1)
mix /= np.max(np.abs(mix)) / 0.9
wav = ROOT / "audio/_teaser.wav"
with wave.open(str(wav), "wb") as w:
    w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

out = ROOT / f"out/outtakes-teaser-8s-{'1x1' if SQUARE else '9x16'}.mp4"
COMP = "acompressor=threshold=-22dB:ratio=4:attack=4:release=140:makeup=2,"
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", COMP + "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                    "-f", "null", "-"], capture_output=True, text=True).stderr
mj = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
ln = COMP + (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
      f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true,"
      "lowpass=f=15500,aresample=192000,alimiter=limit=0.70:attack=1:release=60:level=disabled,aresample=48000")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "out/_teaser_video.mp4"), "-i", str(wav),
                "-af", ln,
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest",
                "-movflags", "+faststart", str(out)], check=True)
print(out)
