"""Synthesize the film's sound-effects track (no music, no drum groove) from src/timeline.json.

No samples, no music library: every sound (kick, clap, hats, 808, camera
shutter, impacts, risers, UI blips, phone buzz) is generated here, and every
hit is placed on a frame from the timeline, so picture and sound cannot drift.

    python3 scripts/beat.py            -> public/beat.wav
"""
import json
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent.parent
T = json.loads((ROOT / "src" / "timeline.json").read_text())
SR = 48000
FPS = T["fps"]
BEAT_F = FPS * 60 / T["bpm"]  # 15 frames
DUR = T["total"] / FPS + 0.6
N = int(DUR * SR)
rng = np.random.default_rng(20251120)

L = np.zeros(N)
R = np.zeros(N)


def t_of(f):
    return f / FPS


def env_exp(n, k):
    return np.exp(-np.arange(n) / SR * k)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, btype="high", fs=SR, output="sos"), x)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, btype="low", fs=SR, output="sos"), x)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0:
        return
    s = sig[: max(0, N - i)] * gain
    lg = np.cos((pan + 1) * np.pi / 4)
    rg = np.sin((pan + 1) * np.pi / 4)
    L[i : i + len(s)] += s * lg * 1.414
    R[i : i + len(s)] += s * rg * 1.414


# ------------------------------------------------------------------ voices
def kick(punch=1.0):
    n = int(0.5 * SR)
    tt = np.arange(n) / SR
    freq = 48 + 120 * np.exp(-tt * 28) * punch
    phase = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * env_exp(n, 6.5)
    click = hp(rng.standard_normal(n), 2500) * env_exp(n, 400) * 0.35
    return np.tanh((body + click) * 1.6) * 0.9


def clap():
    n = int(0.35 * SR)
    noise = bp(rng.standard_normal(n), 900, 3200)
    e = np.zeros(n)
    for k, d in enumerate([0.0, 0.009, 0.019]):
        i = int(d * SR)
        e[i:] += env_exp(n - i, 180) * (0.8 if k < 2 else 1.0)
    e += env_exp(n, 14) * 0.35
    return noise * e * 0.75


def hat(open_=False):
    n = int((0.3 if open_ else 0.06) * SR)
    x = hp(rng.standard_normal(n), 7500, 4)
    return x * env_exp(n, 11 if open_ else 70) * 0.35


def bass(freq, length=0.45):
    n = int(length * SR)
    tt = np.arange(n) / SR
    f = freq * (1 + 0.8 * np.exp(-tt * 40))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 3.2)
    s[-int(0.02 * SR) :] *= np.linspace(1, 0, int(0.02 * SR))
    return np.tanh(s * 2.2) * 0.55


def shutter(big=1.0):
    """Mirror slap + curtain: two damped clicks ~38 ms apart, plus a low thump."""
    n = int(0.16 * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    for d, f0, g in [(0.0, 2300, 1.0), (0.038, 3600, 0.8)]:
        i = int(d * SR)
        m = n - i
        tm = np.arange(m) / SR
        ring = np.sin(2 * np.pi * f0 * tm) * np.exp(-tm * 260)
        burst = hp(rng.standard_normal(m), 3000) * np.exp(-tm * 700)
        out[i:] += (ring * 0.6 + burst * 0.9) * g
    thump = np.sin(2 * np.pi * 120 * tt) * np.exp(-tt * 55) * 0.5 * big
    return (out + thump) * 0.8


def boom(length=1.8):
    n = int(length * SR)
    tt = np.arange(n) / SR
    f = 38 + 30 * np.exp(-tt * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 2.2)
    crash = lp(rng.standard_normal(n), 6000) * env_exp(n, 4.5) * 0.35
    air = hp(rng.standard_normal(n), 5000) * env_exp(n, 9) * 0.2
    return np.tanh((sub * 1.4 + crash + air) * 1.2) * 0.9


def riser(length):
    n = int(length * SR)
    x = rng.standard_normal(n)
    # time-varying one-pole lowpass: cutoff sweeps 300 Hz -> 9 kHz
    fc = np.geomspace(300, 9000, n)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc = a[i] * acc + (1 - a[i]) * x[i]
        y[i] = acc
    tt = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 880, n)) / SR) * 0.12
    return (y * 1.6 + tone) * np.linspace(0.05, 1, n) ** 2 * 0.6


def blip():
    n = int(0.09 * SR)
    tt = np.arange(n) / SR
    f = np.geomspace(760, 1500, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 38) * 0.32


def tick():
    n = int(0.02 * SR)
    return hp(rng.standard_normal(n), 4000) * env_exp(n, 500) * 0.25


def buzz(length):
    n = int(length * SR)
    tt = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 155 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 32 * tt))
    s = lp(s, 900)
    edge = int(0.01 * SR)
    s[:edge] *= np.linspace(0, 1, edge)
    s[-edge:] *= np.linspace(1, 0, edge)
    return s * 0.18


def whoosh(length):
    n = int(length * SR)
    x = bp(rng.standard_normal(n), 400, 5000)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * e * 0.35


# ------------------------------------------------------------------ arrangement
def beats(f0, f1):
    """Global 16th-note grid positions (in frames) between f0 and f1."""
    out = []
    k = int(np.ceil(f0 / (BEAT_F / 4)))
    while k * BEAT_F / 4 < f1:
        out.append(k)
        k += 1
    return out


BASS_NOTES = [41.2, 41.2, 49.0, 36.7]  # E1 E1 G1 D1, one per bar


def groove(f0, f1, kind="full", gain=1.0):
    return  # SFX-only mix: no drum groove
    for k in beats(f0, f1):
        f = k * BEAT_F / 4
        t = t_of(f)
        step = k % 16  # 16 steps per bar
        bar = k // 16
        vel = 0.85 + 0.15 * rng.random()
        if kind == "full":
            if step % 4 == 0:
                place(kick(), t, 0.95 * gain)
                place(bass(BASS_NOTES[bar % 4]), t, 0.8 * gain)
            if step in (4, 12):
                place(clap(), t, 0.8 * gain, 0.05)
            if step % 2 == 0:
                place(hat(), t, (0.5 if step % 4 else 0.3) * vel * gain, 0.3)
            elif step in (3, 11, 15):
                place(hat(), t, 0.25 * vel * gain, 0.3)
            if step in (6, 14):
                place(hat(True), t, 0.3 * gain, -0.25)
        elif kind == "half":
            if step in (0, 7, 10):
                place(kick(0.8), t, 0.85 * gain)
            if step in (0,):
                place(bass(BASS_NOTES[(bar + 2) % 4], 0.9), t, 0.7 * gain)
            if step == 8:
                place(clap(), t, 0.8 * gain, 0.05)
            if step % 4 == 2:
                place(hat(), t, 0.35 * vel * gain, 0.3)
        elif kind == "light":
            if step % 4 == 0:
                place(kick(0.9), t, 0.8 * gain)
            if step % 2 == 0:
                place(hat(), t, 0.3 * vel * gain, 0.3)
            if step in (4, 12):
                place(clap(), t, 0.5 * gain, 0.05)
        elif kind == "air":  # breakdown under the phone call
            if step % 2 == 0:
                place(hat(), t, 0.3 * vel * gain, 0.3)
            if step in (4, 12):
                place(clap(), t, 0.55 * gain, 0.05)


h, c, r, u, k_, m, cta = T["hook"], T["chase"], T["reveal"], T["ui"], T["call"], T["community"], T["cta"]

# 1 hook: burst of shutters accelerating over a growing riser, then the land
place(riser(t_of(h["land"] - 30)), t_of(30), 0.45)
for i, f in enumerate(h["burst"]):
    place(shutter(0.6 + 0.4 * i / len(h["burst"])), t_of(f), 0.7 + 0.3 * i / len(h["burst"]), (rng.random() - 0.5) * 0.4)
place(shutter(1.2), t_of(h["land"]), 1.0)
place(boom(1.2), t_of(h["land"]), 0.55)
groove(h["land"], h["to"], "light")
for f in h["words"]:
    place(tick(), t_of(f), 0.5, 0.2)

# 2 chase: half-time, message blips, stabs on the words, riser into silence
groove(c["from"], c["to"] - 22, "half")
place(whoosh(0.5), t_of(c["shrink"][0]), 0.6)
for f in c["bubbles"]:
    place(blip(), t_of(f), 0.9, 0.15)
for f in c["words"]:
    place(shutter(0.7), t_of(f), 0.6)
place(whoosh(0.35), t_of(c["swap"] - 3), 0.7)
place(riser(t_of(c["to"] - 3 - 322)), t_of(322), 0.7)
place(shutter(1.0), t_of(c["to"]), 0.9)  # curtain closes; then silence

# 3 reveal: the hit
place(boom(2.2), t_of(r["crash"]), 1.0)
place(shutter(1.3), t_of(r["crash"]), 1.0)
groove(r["crash"] + BEAT_F * 2, k_["from"], "full")
for f in r["words"]:
    place(tick(), t_of(f), 0.35, -0.2)

# 4 UI: keystrokes, enter, card press, push into flash, contact press
t0 = u["typeStart"]
gaps = [0, 2, 2, 1, 2, 3, 1, 2, 2, 4, 2, 1, 2, 2, 1, 3, 2, 1, 2, 2, 1]
for g in gaps:
    t0 += g
    place(tick(), t_of(t0), 0.45, 0.25)
place(blip(), t_of(u["enter"]), 0.6)
place(shutter(0.5), t_of(u["cardPress"]), 0.6)
place(whoosh(t_of(u["push"][1] - u["push"][0])), t_of(u["push"][0]), 0.8)
place(shutter(0.9), t_of(u["profile"]), 0.8)
place(shutter(0.5), t_of(u["contactPress"]), 0.6)

# 5 call: breakdown, the phone buzzes in its ring pattern
place(shutter(1.0), t_of(k_["from"]), 0.9)
groove(k_["from"], k_["to"], "air")
f = k_["from"] + 8
while f < k_["to"]:
    place(buzz(t_of(16)), t_of(f), 1.0)
    f += 24

# 6 community + 7 CTA
place(boom(1.2), t_of(m["from"]), 0.6)
groove(m["from"], cta["riser"][0], "full")
for f in m["cuts"] + [m["sotw"], cta["from"]]:
    place(shutter(1.0), t_of(f), 0.85, (rng.random() - 0.5) * 0.3)
# snare roll + riser into silence, then the date hit
roll = []
f = cta["riser"][0]
step = 7.5
while f < cta["riser"][1] - 1:
    roll.append(f)
    f += step
    step = max(1.875, step * 0.82)
for i, f in enumerate(roll):
    place(shutter(0.4), t_of(f), 0.2 + 0.4 * i / len(roll))  # burst-mode build
place(riser(t_of(cta["riser"][1] - cta["riser"][0])), t_of(cta["riser"][0]), 0.6)
place(boom(2.0), t_of(cta["crash"]), 1.0)
place(shutter(1.3), t_of(cta["crash"]), 1.0)
groove(cta["crash"] + BEAT_F, cta["final"], "full")
place(blip(), t_of(cta["pill"]), 0.6)
place(shutter(0.6), t_of(cta["press"]), 0.7)
# end: one last shutter, a quiet sub tail, the curtain closing
place(shutter(1.1), t_of(cta["final"]), 0.9)
place(boom(1.6), t_of(cta["final"]), 0.45)
place(shutter(0.8), t_of(cta["to"] - 3), 0.8)

# ambience bed: distant crowd / floodlit-pitch air under everything, so the
# SFX never sit on digital silence. Ducked under impacts.
def ambience():
    x = rng.standard_normal((N, 2))
    crowd = np.stack([bp(x[:, 0], 250, 1800, 2), bp(x[:, 1], 250, 1800, 2)], axis=1)
    tt = np.arange(N) / SR
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * tt / 7.3) * np.sin(2 * np.pi * tt / 3.1 + 1)
    air = np.stack([hp(x[:, 1], 6000), hp(x[:, 0], 6000)], axis=1) * 0.25
    return (crowd * swell[:, None] + air) * 0.022

bed = ambience()
duck = np.ones(N)
for f in [h["land"], r["crash"], m["from"], cta["crash"], cta["final"]]:
    i = int(t_of(f) * SR); n = int(1.2 * SR)
    duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.7 * np.exp(-np.arange(min(n, N - i)) / SR * 3))
# silence before the two hits stays (designed breath), but not digital: keep 15 %
for f0, f1 in [(c["to"] - 2, r["crash"]), (cta["riser"][1] - 2, cta["crash"])]:
    duck[int(t_of(f0) * SR):int(t_of(f1) * SR)] = 0.15
L += bed[:, 0] * duck
R += bed[:, 1] * duck

# ------------------------------------------------------------------ master
mix = np.stack([L, R], axis=1)
mix = mix[: int(T["total"] / FPS * SR) + int(0.3 * SR)]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)  # soft limiter (SFX only: peak-normalised, no loudness push)
peak = np.max(np.abs(mix))
mix *= 0.50 / peak
# fast look-ahead peak limiter, then +6 dB make-up: shutter clicks are spiky,
# so this lifts loudness toward the -14 LUFS social target without overshoot.
from scipy.ndimage import maximum_filter1d, uniform_filter1d
gain_db = 6.5
mix *= 10 ** (gain_db / 20)
ceil = 0.5
env = maximum_filter1d(np.max(np.abs(mix), axis=1), size=int(0.004 * SR))
g = np.minimum(1.0, ceil / np.maximum(env, 1e-9))
g = uniform_filter1d(np.minimum.accumulate(g[::-1])[::-1] if False else g, size=int(0.003 * SR))
g = np.minimum(g, ceil / np.maximum(env, 1e-9))
mix *= g[:, None]
fade = int(0.25 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]

out = ROOT / "public" / "beat.wav"
pcm = (mix * 32767).astype(np.int16)
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {out} {len(mix) / SR:.2f}s rms={20 * np.log10(np.sqrt(np.mean(mix ** 2))):.1f} dBFS")


# ------------------------------------------------------------------ voiceover mix
# Places each VO segment from timeline.json on its film cue, ducks the SFX
# under the voice, and writes public/mix.wav (beat.wav stays the SFX stem).
import subprocess

vo_cfg = T.get("vo")
if vo_cfg:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(ROOT / "public" / vo_cfg["file"]), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    take = np.frombuffer(raw, np.float32).astype(float)
    n_out = len(mix)
    vo = np.zeros(n_out)
    edge = int(0.012 * SR)
    for a, b, at, _ in vo_cfg["segments"]:
        seg = take[int(a * SR):int(b * SR)].copy()
        seg[:edge] *= np.linspace(0, 1, edge)
        seg[-edge:] *= np.linspace(1, 0, edge)
        i = int(at * SR)
        m = min(len(seg), n_out - i)
        vo[i:i + m] += seg[:m]
    vo *= 0.9 / max(np.max(np.abs(vo)), 1e-9)
    # duck: SFX down ~7 dB while the voice speaks, smooth attack/release
    from scipy.ndimage import uniform_filter1d as _uf
    act = (_uf(np.abs(vo), size=int(0.05 * SR)) > 0.01).astype(float)
    act = _uf(np.maximum.accumulate(act[::-1])[::-1] * 0 + act, size=int(0.25 * SR))
    duck_g = 1 - 0.55 * np.clip(act * 1.5, 0, 1)
    out_mix = mix * duck_g[:, None] * 0.85 + vo[:, None] * 0.62
    out_mix *= 10 ** (7.0 / 20)  # make-up gain toward -14 LUFS
    ceil2 = 0.63  # -4 dBFS, true-peak aware (4x oversampled detection)
    from scipy.signal import resample_poly
    tp = np.max(np.abs(resample_poly(out_mix, 4, 1, axis=0)), axis=1).reshape(-1, 4).max(axis=1)[: len(out_mix)]
    env2 = maximum_filter1d(tp, size=int(0.004 * SR))
    g2 = np.minimum(1.0, ceil2 / np.maximum(env2, 1e-9))
    out_mix *= np.minimum(_uf(g2, size=int(0.003 * SR)), g2)[:, None]
    pcm2 = (np.clip(out_mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(ROOT / "public" / "mix.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm2.tobytes())
    print("wrote public/mix.wav with", len(vo_cfg["segments"]), "VO segments")
