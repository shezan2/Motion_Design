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
VO = ROOT / "brand/vo/vo-v6.mp3"   # latest take for the 60 s cut (vo-v5.mp3 was the previous one)

# (start, end) of each line in the take (from silence detection), and where it lands in the film (s)
LINES = [
    ((0.00, 0.91), 3.15, "You got the shot."),
    ((1.29, 3.05), 5.60, "Then came the DMs."),
    ((3.33, 4.17), 10.25, "Sound familiar?"),
    ((4.48, 6.16), 11.25, "This is Outtakes."),
    ((6.43, 9.11), 13.08, "Made by photographers, for photographers."),
    ((9.33, 11.22), 15.95, "Set up once. Get booked."),
    ((11.42, 13.42), 23.60, "Your portfolio, organised."),
    ((13.63, 15.40), 25.80, "Now clients find you."),
    ((15.67, 18.75), 31.55, "Booked at your rate. No lowball DMs."),
    ((18.95, 21.03), 37.00, "Paid. Even if they cancel."),
    ((21.29, 23.17), 39.55, "Invoices, done for you."),
    ((23.41, 25.04), 42.55, "Your shot. Featured."),
    ((25.32, 25.76), 47.35, "Call."),
    ((26.00, 26.33), 48.65, "Book."),
    ((26.55, 26.97), 49.65, "Pay."),
    ((27.14, 27.71), 50.65, "Shoot."),
    ((27.91, 28.92), 51.75, "Get in the frame."),
    ((29.15, 32.65), 52.90, "Set up your profile free, from the twenty-fourth of November."),
    ((32.88, 34.37), 57.45, "outtakes dot S G."),
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

# duck the effects ~17 dB while the voice talks (fast attack, slow release)
active = uniform_filter1d((np.abs(vo) > 0.01).astype(float), int(0.12 * SR))
active = np.clip(active * 4, 0, 1)
env = np.zeros(N)
att, rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.30 * SR))
e = 0.0
for k in range(0, N, 48):  # control rate 1 kHz
    t = active[k]
    e = t + (e - t) * (att ** 48 if t > e else rel ** 48)
    env[k:k + 48] = e
duck = 1 - env * (1 - 10 ** (-17 / 20))
mix = sfx * duck[:, None] + vo[:, None] * 1.0

out = ROOT / "audio/mix_vo_raw.wav"
with wave.open(str(out), "wb") as w:
    w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
    w.writeframes((np.clip(mix / max(1.0, np.max(np.abs(mix)) / 0.98), -1, 1) * 32767).astype(np.int16).tobytes())
print(out, f"{N / SR:.2f}s")
