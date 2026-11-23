"""Lay the ElevenLabs voiceover onto the film: one take, cut into its lines, each placed on its beat (the step
words land as their cards arrive), with the sound effects ducked under the voice.

    bash tools/vo_mux.sh     # per format: effects without the crowd bed -> this mix -> loudness -> *-vo.mp4
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
VO = ROOT / "brand/vo/vo-v5.mp3"   # v4 film (60 s cut)

# (start, end) of each line in the take (from silence detection), and where it lands in the film (s)
LINES = [
    ((0.00, 0.83), 3.15, "You got the shot."),
    ((1.29, 2.45), 5.60, "Then came the DMs."),
    ((2.87, 3.47), 10.35, "Sound familiar?"),
    ((4.08, 5.36), 11.30, "This is Outtakes."),
    ((5.73, 8.03), 12.80, "Made by photographers, for photographers."),
    ((8.46, 10.10), 15.85, "Set up once. Get booked."),
    ((10.52, 12.22), 23.85, "Your portfolio, organised."),
    ((12.66, 14.14), 25.85, "Now clients find you."),
    ((14.75, 17.35), 31.60, "Booked at your rate. No lowball DMs."),
    ((17.87, 19.47), 37.00, "Paid. Even if they cancel."),
    ((20.01, 21.46), 39.55, "Invoices, done for you."),
    ((21.96, 23.44), 42.55, "Your shot. Featured."),
    ((23.89, 24.30), 47.35, "Call."),
    ((24.56, 24.86), 48.65, "Book."),
    ((25.17, 25.50), 49.65, "Pay."),
    ((25.62, 26.06), 50.65, "Shoot."),
    ((26.55, 27.25), 51.75, "Get in the frame."),
    ((27.74, 30.54), 52.90, "Set up your profile free, from the twenty-fourth of November."),
    ((31.05, 32.21), 57.45, "outtakes dot S G."),
]
PRE, POST = 0.04, 0.08


def load(path, ch):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).astype(np.float64)


take = load(VO, 1)[:, 0]
sfx = load(ROOT / "audio/sfx_nobed.wav", 2)   # OT_NO_BED=1 python3 tools/sfx.py
N = len(sfx)
vo = np.zeros(N)

# each line: cut with short fades, level-matched to the same speech RMS
target = 10 ** (-20 / 20)
for (a, b), at, text in LINES:
    i0, i1 = int(max(0, a - PRE) * SR), int(min(len(take) / SR, b + POST) * SR)
    seg = take[i0:i1].copy()
    f = int(0.012 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    loud = seg[np.abs(seg) > 0.02]
    seg *= min(4.0, target / max(np.sqrt(np.mean(loud ** 2)), 1e-6))
    j = int((at - PRE) * SR)
    assert j + len(seg) <= N, text
    assert not np.any(vo[j:j + len(seg)]), f"overlap at {text}"
    vo[j:j + len(seg)] += seg

# duck the effects ~13 dB while the voice talks (fast attack, slow release)
active = uniform_filter1d((np.abs(vo) > 0.01).astype(float), int(0.12 * SR))
active = np.clip(active * 4, 0, 1)
env = np.zeros(N)
att, rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.30 * SR))
e = 0.0
for k in range(0, N, 48):  # control rate 1 kHz
    t = active[k]
    e = t + (e - t) * (att ** 48 if t > e else rel ** 48)
    env[k:k + 48] = e
duck = 1 - env * (1 - 10 ** (-13 / 20))
mix = sfx * duck[:, None] + vo[:, None] * 1.0

out = ROOT / "audio/mix_vo_raw.wav"
with wave.open(str(out), "wb") as w:
    w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
    w.writeframes((np.clip(mix / max(1.0, np.max(np.abs(mix)) / 0.98), -1, 1) * 32767).astype(np.int16).tobytes())
print(out, f"{N / SR:.2f}s")
