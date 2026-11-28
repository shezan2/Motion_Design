"""Measure every SFX take (the real-sfx way: read sound as numbers and pictures, never guess).

  python tools/sfx_analyze.py audio/library/takes  -> audio/library/takes.json + takes_sheet.png
Per take: audible start, arrival (first 60 ms window within 6 dB of the loudest), peak, audible length,
spectral centroid, integrated loudness, peak dBFS, how many separate onsets (double hits are bad).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
from PIL import Image, ImageDraw
from scipy.signal import stft

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)


def env_db(mono, win=0.01):
    n = int(SR * win)
    pad = len(mono) // n * n
    frames = mono[:pad].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms + 1e-12)


def analyze(path):
    x = load(path)
    mono = x.mean(axis=1)
    peak = float(np.abs(x).max() + 1e-12)
    e = env_db(mono)            # 10 ms frames
    top = e.max()
    above = np.nonzero(e > top - 30)[0]
    start = above[0] * 0.01 if above.size else 0.0
    end = above[-1] * 0.01 + 0.01 if above.size else len(mono) / SR
    # arrival: first 60 ms window (6 frames) whose mean is within 6 dB of the loudest 60 ms window
    k = 6
    win = np.convolve(e, np.ones(k) / k, mode="valid")
    best = win.max()
    arrival = float(np.nonzero(win >= best - 6)[0][0] * 0.01)
    peak_t = float(np.argmax(np.abs(mono)) / SR)
    # onsets: rises of > 12 dB within 30 ms
    rises = []
    for i in range(3, len(e)):
        if e[i] > top - 24 and e[i] - e[i - 3] > 12 and (not rises or i - rises[-1] > 8):
            rises.append(i)
    seg = mono[int(start * SR):int(end * SR)] if end > start else mono
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) if len(seg) > 64 else np.zeros(2)
    freqs = np.fft.rfftfreq(len(seg), 1 / SR) if len(seg) > 64 else np.zeros(2)
    centroid = float((spec * freqs).sum() / (spec.sum() + 1e-12))
    try:
        lufs = float(pyln.Meter(SR, block_size=0.1).integrated_loudness(x))
    except Exception:
        lufs = float("nan")
    return {"file": path.name, "dur": round(len(mono) / SR, 3), "start": round(start, 3), "arrival": round(arrival, 3),
            "peak_t": round(peak_t, 3), "audible": round(end - start, 3), "peak_db": round(20 * np.log10(peak), 1),
            "centroid": round(centroid), "lufs": round(lufs, 1), "onsets": len(rises),
            "onset_t": [round(i * 0.01, 2) for i in rises[:6]]}, x


def strip(x, w=520, h=120):
    mono = x.mean(axis=1)
    f, t, Z = stft(mono, SR, nperseg=1024, noverlap=768)
    S = 20 * np.log10(np.abs(Z) + 1e-9)
    S = np.clip((S - S.max() + 80) / 80, 0, 1)
    fmax_bin = np.searchsorted(f, 16000)
    S = S[:fmax_bin][::-1]
    img = Image.fromarray((S * 255).astype(np.uint8)).resize((w, h)).convert("RGB")
    d = ImageDraw.Draw(img)
    n = len(mono)
    step = max(1, n // w)
    for px in range(w):
        seg = mono[px * step:(px + 1) * step]
        if seg.size:
            a = float(np.abs(seg).max())
            d.line([(px, h / 2 - a * h / 2), (px, h / 2 + a * h / 2)], fill=(80, 200, 255))
    return img


def main():
    folder = Path(sys.argv[1])
    rows, imgs = [], []
    for p in sorted(folder.glob("*.mp3")):
        info, x = analyze(p)
        rows.append(info)
        imgs.append((info, strip(x)))
    (folder.parent / "takes.json").write_text(json.dumps(rows, indent=1))
    W, Hh = 520, 120
    cols = 4
    sheet = Image.new("RGB", (cols * W, ((len(imgs) + cols - 1) // cols) * (Hh + 30)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (info, img) in enumerate(imgs):
        x0, y0 = (i % cols) * W, (i // cols) * (Hh + 30)
        sheet.paste(img, (x0, y0 + 26))
        d.text((x0 + 4, y0 + 2), f"{info['file'][:-4]}  dur {info['dur']}s  arr {info['arrival']}  onsets {info['onsets']}  c {info['centroid']}Hz  {info['lufs']}LUFS",
               fill=(255, 220, 0))
    sheet.save(folder.parent / "takes_sheet.png")
    for r in rows:
        print(f"{r['file']:<20} dur {r['dur']:>5} start {r['start']:>5} arr {r['arrival']:>5} peak {r['peak_t']:>5} aud {r['audible']:>5} "
              f"pk {r['peak_db']:>6} c {r['centroid']:>6} lufs {r['lufs']:>6} onsets {r['onsets']} {r['onset_t']}")


if __name__ == "__main__":
    main()
