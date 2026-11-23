"""Sound effects for the Lottie film (no music, no voiceover).

Reads public/projects/outtakes-launch/cues.json (written by build_film.py) and
synthesises every sound from scratch, each placed on its cue frame:
camera shutters on cuts, message pops, keystrokes, taps, success chimes,
impacts, risers, whooshes, plus a quiet floodlit-pitch ambience bed so the
effects never sit on digital silence.

    python3 tools/sfx.py  ->  audio/sfx.wav
"""
import json
import os
import wave
from pathlib import Path

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import butter, resample_poly, sosfilt

ROOT = Path(__file__).resolve().parent.parent
# Both formats share one timeline; read the cues of whichever format was built last.
_PROJECT = "outtakes-launch-16x9" if os.environ.get("OT_FORMAT") == "landscape" else "outtakes-launch"
CUES = json.loads((ROOT / "public/projects" / _PROJECT / "cues.json").read_text())
SR = 48000
FPS = CUES["fps"]
DUR = CUES["total"] / FPS
N = int((DUR + 0.5) * SR)
rng = np.random.default_rng(20261120)
L = np.zeros(N)
R = np.zeros(N)


def env(n, k):
    return np.exp(-np.arange(n) / SR * k)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, fc, o=2):
    return sosfilt(butter(o, fc, btype="high", fs=SR, output="sos"), x)


def lp(x, fc, o=2):
    return sosfilt(butter(o, fc, btype="low", fs=SR, output="sos"), x)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    s = sig[: N - i] * gain
    a = min(len(s), int(0.0025 * SR))  # 2.5 ms raised-cosine attack: no instant onsets for the codec to overshoot
    s = s.copy()
    s[:a] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    L[i:i + len(s)] += s * np.cos((pan + 1) * np.pi / 4) * 1.414
    R[i:i + len(s)] += s * np.sin((pan + 1) * np.pi / 4) * 1.414


# ------------------------------------------------------------------ voices
def shutter(big=1.0):
    """Mirror slap + curtain: two damped clicks ~38 ms apart, plus a low thump."""
    n = int(0.16 * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    for d, f0, g in [(0.0, 2300, 1.0), (0.038, 3600, 0.8)]:
        i = int(d * SR)
        tm = np.arange(n - i) / SR
        out[i:] += (np.sin(2 * np.pi * f0 * tm) * np.exp(-tm * 260) * 0.6 +
                    hp(rng.standard_normal(n - i), 3000) * np.exp(-tm * 700) * 0.9) * g
    return (out + np.sin(2 * np.pi * 120 * tt) * np.exp(-tt * 55) * 0.5 * big) * 0.8


def boom(length=1.8):
    n = int(length * SR)
    tt = np.arange(n) / SR
    f = 38 + 30 * np.exp(-tt * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 2.2)
    crash = lp(rng.standard_normal(n), 6000) * env(n, 4.5) * 0.35
    air = hp(rng.standard_normal(n), 5000) * env(n, 9) * 0.2
    return np.tanh((sub * 1.4 + crash + air) * 1.2) * 0.9


def riser(length):
    n = int(length * SR)
    x = rng.standard_normal(n)
    fc = np.geomspace(300, 9000, n)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc = a[i] * acc + (1 - a[i]) * x[i]
        y[i] = acc
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 880, n)) / SR) * 0.12
    return (y * 1.6 + tone) * np.linspace(0.05, 1, n) ** 2 * 0.6


def blip(up=True):
    n = int(0.09 * SR)
    tt = np.arange(n) / SR
    f = np.geomspace(760, 1500, n) if up else np.geomspace(1300, 820, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 38) * 0.32


def tick():
    n = int(0.02 * SR)
    return hp(rng.standard_normal(n), 4000) * env(n, 500) * 0.25


def key():
    n = int(0.03 * SR)
    tt = np.arange(n) / SR
    return (hp(rng.standard_normal(n), 2500) * env(n, 380) * 0.22 +
            np.sin(2 * np.pi * 1900 * tt) * env(n, 600) * 0.05)


def tap_snd():
    n = int(0.06 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 180 * tt) * env(n, 70) * 0.5 + hp(rng.standard_normal(n), 3000) * env(n, 900) * 0.3)


def chime(soft=False):
    """Two-note success chime (perfect fifth), bell-ish partials, quick attack."""
    n = int(0.9 * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    notes = [(880, 0.0), (1318.5, 0.07)] if not soft else [(660, 0.0), (990, 0.08)]
    for f0, d in notes:
        i = int(d * SR)
        tm = tt[: n - i]
        tone = (np.sin(2 * np.pi * f0 * tm) + 0.35 * np.sin(2 * np.pi * f0 * 2.01 * tm) +
                0.12 * np.sin(2 * np.pi * f0 * 3.02 * tm))
        out[i:] += tone * np.exp(-tm * (5 if not soft else 6)) * np.minimum(1, tm / 0.004)
    return out * (0.22 if not soft else 0.16)


def pop():
    n = int(0.12 * SR)
    tt = np.arange(n) / SR
    f = np.geomspace(300, 900, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30) * 0.35


def whoosh(length=0.45):
    n = int(length * SR)
    x = bp(rng.standard_normal(n), 400, 5000)
    return x * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.35


def af():
    """Camera autofocus confirmation: two short, bright beeps."""
    n = int(0.11 * SR)
    out = np.zeros(n)
    for d, f0 in ((0.0, 2950), (0.055, 2950)):
        i = int(d * SR)
        m = int(0.035 * SR)
        tm = np.arange(m) / SR
        out[i:i + m] += np.sin(2 * np.pi * f0 * tm) * np.minimum(1, tm / 0.002) * np.exp(-tm * 40)
    return out * 0.16


VOICES = {
    "shutter": lambda: shutter(1.0), "shutter_big": lambda: shutter(1.3), "boom": lambda: boom(2.2),
    "boom_small": lambda: boom(1.2), "blip_in": lambda: blip(True), "blip_out": lambda: blip(False),
    "tick": tick, "key": key, "tap": tap_snd, "chime": lambda: chime(False), "chime_soft": lambda: chime(True),
    "pop": pop, "whoosh": lambda: whoosh(0.45), "af": af,
}

for cue in CUES["cues"]:
    kind, t, g = cue["kind"], cue["frame"] / FPS, cue["gain"]
    if kind.startswith("riser:"):
        frames = int(kind.split(":")[1])
        place(riser(frames / FPS), t, g)
    else:
        # whooshes swell to a peak: start them a little early so the peak lands on the move
        lead = 0.12 if kind == "whoosh" else 0.0
        place(VOICES[kind](), max(0.0, t - lead), g, (rng.random() - 0.5) * 0.3)

# ------------------------------------------------------------------ ambience bed (ducked under impacts)
x = rng.standard_normal((N, 2))
crowd = np.stack([bp(x[:, 0], 250, 1800), bp(x[:, 1], 250, 1800)], axis=1)
tt = np.arange(N) / SR
swell = 0.75 + 0.25 * np.sin(2 * np.pi * tt / 7.3) * np.sin(2 * np.pi * tt / 3.1 + 1)
bed = (crowd * swell[:, None] + np.stack([hp(x[:, 1], 6000), hp(x[:, 0], 6000)], axis=1) * 0.25) * 0.02
duck = np.ones(N)
for cue in CUES["cues"]:
    if cue["kind"] in ("boom", "shutter_big"):
        i = int(cue["frame"] / FPS * SR)
        n = min(int(1.2 * SR), N - i)
        duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.7 * np.exp(-np.arange(n) / SR * 3))
NO_BED = os.environ.get("OT_NO_BED") == "1"   # the voiceover mix runs without the crowd bed
if not NO_BED:
    L += bed[:, 0] * duck
    R += bed[:, 1] * duck

# ------------------------------------------------------------------ master: true-peak-aware limiter
mix = np.stack([L, R], axis=1)[: int(DUR * SR)]
mix = sosfilt(butter(2, 15500, btype="low", fs=SR, output="sos"), mix, axis=0)  # tame codec-unfriendly top end
mix *= 0.5 / np.max(np.abs(mix))
mix *= 10 ** (17.5 / 20)  # make-up gain toward the -14 LUFS social target (sparse SFX need a lot)
ceil = 0.63
tp = np.max(np.abs(resample_poly(mix, 4, 1, axis=0)), axis=1).reshape(-1, 4).max(axis=1)[: len(mix)]
e = maximum_filter1d(tp, size=int(0.004 * SR))
g = np.minimum(1.0, ceil / np.maximum(e, 1e-9))
mix *= np.minimum(uniform_filter1d(g, size=int(0.003 * SR)), g)[:, None]
fade = int(0.2 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]

out = ROOT / "audio" / ("sfx_nobed.wav" if NO_BED else "sfx.wav")
out.parent.mkdir(exist_ok=True)
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"wrote {out} ({len(mix) / SR:.2f}s, {len(CUES['cues'])} cues)")
