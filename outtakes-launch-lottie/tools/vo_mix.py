"""Lay the ElevenLabs voiceover onto the film: one take, cut into its 17 lines,
each placed on its beat, with the sound effects ducked under the voice.

    OT_NO_BED=1 python3 tools/sfx.py && python3 tools/vo_mix.py   ->  audio/mix_vo.wav  (then mux with tools/vo_mux.sh)
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
VO = ROOT / "brand/vo/vo-v4.mp3"   # second take (new voice)

# (start, end) of each line in the take (from silence detection), and where it lands in the film (s)
LINES = [
    ((0.00, 0.96), 3.00, "You got the shot."),
    ((1.37, 2.84), 5.50, "Then came the DMs."),
    ((3.12, 4.28), 10.10, "Sound familiar?"),
    ((4.67, 5.98), 11.85, "This is Outtakes."),
    ((6.14, 8.54), 13.35, "Made by photographers, for photographers."),
    ((8.81, 11.06), 16.50, "Every sideline shot starts with a search."),
    ((11.34, 12.91), 21.00, "Now the clients come to you."),
    ((13.26, 15.27), 26.00, "Your work, all on one page."),
    ((15.57, 18.70), 31.00, "They pick a date, they book your package. At your rate."),
    ((19.06, 21.16), 36.50, "Call. Book. Pay. Shoot."),
    ((21.46, 23.46), 41.00, "Invoices? Done for you."),
    ((23.81, 26.01), 45.00, "And if they cancel, you still get paid."),
    ((26.39, 29.64), 49.50, "Shot of the Week puts your best frame in front of everyone."),
    ((29.97, 32.36), 53.50, "Sign up free. Profiles are open now."),
    ((32.71, 35.36), 56.40, "We go live the twentieth of November, five PM."),
    ((35.69, 36.59), 59.30, "Get in the frame."),
    ((36.88, 38.43), 62.30, "outtakes dot S G."),
]
PRE, POST = 0.04, 0.10


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
