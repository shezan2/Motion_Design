#!/usr/bin/env python3
"""SFX-only sound track for the Nick R.L. film, mixed the Clipwing real-sfx way.

  python tools/sfx_mix.py            -> audio/sfx.wav (master), audio/sfx_nobed.wav, audio/mix_report.json

Method (github.com/Clipwing/skills, real-sfx; Ozen sound.md):
- one recorded-sounding sound per cue (ElevenLabs SFX v3 takes, picked by measurement in sfx_analyze.py),
  placed by its anchor: ARRIVAL (first 60 ms within 6 dB of the loudest) for sounds that get loud fast,
  PEAK for swells/whooshes, or a measured onset time for multi-part sounds (pen check, key, mouse click);
- each sound brought to its role's peak (hit -4, whoosh -9, foley -8, click/tick -14/-16, chime -13 dBFS),
  then the cue's gain_db; 3 ms fade-in so the encoder does not overshoot;
- antiphase stereo takes play from their louder channel (mono-safe on phone speakers);
- ONE long dark steady bed under the whole film at -54 dBFS (median of 250 ms windows): never digital silence;
- master: 25 Hz high-pass, gentle 15.5 kHz low-pass, gain to about -14 LUFS, 4x-oversampled true-peak limiter.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
from scipy.signal import butter, resample_poly, sosfilt

ROOT = Path(__file__).resolve().parent.parent
TAKES = ROOT / "audio" / "library" / "takes"
SR = 48000
DUR = 20.0
FPS = 30

# real-sfx role peaks are set for films with music; with SFX only the small sounds carry the film, so they sit a
# few dB higher (ticks, clicks, whooshes) while the one big hit keeps the top of the range
ROLE_PEAK = {"hit": -3.0, "whoosh": -7.0, "foley": -6.0, "click": -11.0, "tick": -12.5, "chime": -11.0}

# kind -> layers: (take, role, anchor, extra_db, slice_from_s)
#   anchor: "arrive" | "peak" | "start" | float seconds inside the take
KINDS = {
    "tick":         [("tick_1|tick_4|tick_3", "tick", "start", 0.0, 0.0, 180)],
    "pop":          [("click_3", "click", "start", 0.0, 0.0, 220)],
    "whoosh_short": [("whoosh_short_2", "whoosh", "peak", 0.0, 0.0)],
    "whoosh_deep":  [("whoosh_deep_4", "whoosh", "peak", 0.0, 0.0)],
    "whoosh_morph": [("whoosh_deep_1", "whoosh", "peak", 0.0, 0.0), ("whoosh_deep_3", "whoosh", "peak", -5.0, 0.0)],
    "hit_sold":     [("hit_sold_4", "hit", "arrive", 0.0, 0.0), ("thud_card_2", "foley", 0.69, -9.0, 0.0)],
    "arrow":        [("arrow_2", "foley", "arrive", 0.0, 0.0)],
    "chess":        [("chess_1", "foley", "arrive", 0.0, 0.0, 150)],
    "check":        [("check_2", "foley", 0.48, 0.0, 0.0, 200)],
    "key":          [("key_4", "foley", 1.797, 0.0, 1.10)],
    "click":        [("click_2", "click", 0.09, 0.0, 0.0, 180)],
    "thud_card":    [("thud_card_2", "foley", 0.69, 0.0, 0.0)],
    "shimmer":      [("shimmer_1|shimmer_4", "chime", "start", 0.0, 0.0, 400)],
}


def load(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(TAKES / f"{name}.mp3"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)
    # mono safety: if the channels cancel, play the louder one on both sides
    l, r = x[:, 0], x[:, 1]
    if np.sum(l * r) < 0:
        keep = l if np.sum(l * l) >= np.sum(r * r) else r
        x = np.stack([keep, keep], axis=1)
    return x


def env_db(mono, hop=0.01):
    n = int(SR * hop)
    pad = len(mono) // n * n
    rms = np.sqrt((mono[:pad].reshape(-1, n) ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms)


def anchor_time(x, mode):
    if isinstance(mode, (int, float)):
        return float(mode)
    mono = x.mean(axis=1)
    if mode == "peak":
        e = env_db(mono, 0.02)
        return float(np.argmax(e) * 0.02 + 0.01)
    if mode == "arrive":
        e = env_db(mono, 0.01)
        k = 6
        win = np.convolve(e, np.ones(k) / k, mode="valid")
        return float(np.nonzero(win >= win.max() - 6)[0][0] * 0.01)
    # start: first 10 ms frame within 30 dB of the loudest
    e = env_db(mono, 0.01)
    return float(np.nonzero(e > e.max() - 30)[0][0] * 0.01)


def fade(x, fin=0.003, fout=0.03):
    n_in, n_out = int(SR * fin), int(SR * fout)
    x = x.copy()
    if len(x) > n_in:
        x[:n_in] *= np.linspace(0, 1, n_in)[:, None]
    if len(x) > n_out:
        x[-n_out:] *= np.linspace(1, 0, n_out)[:, None]
    return x


def true_peak_db(x):
    up = resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.abs(up).max() + 1e-12)


def limiter(x, ceiling_db=-1.5, attack=0.004, release=0.09):
    """Look-ahead peak limiter on a 4x-oversampled envelope (true-peak aware)."""
    ceil = 10 ** (ceiling_db / 20)
    up = np.abs(resample_poly(x, 4, 1, axis=0)).max(axis=1)
    peak = up.reshape(-1, 4).max(axis=1)[: len(x)]
    if len(peak) < len(x):
        peak = np.pad(peak, (0, len(x) - len(peak)))
    need = np.minimum(1.0, ceil / np.maximum(peak, 1e-12))
    la = int(SR * attack)
    # look-ahead: a sliding minimum so the gain reaches its target before the peak arrives
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * la + 1, mode="nearest")
    # smooth release
    a_r = np.exp(-1.0 / (SR * release))
    out = np.empty_like(g)
    cur = 1.0
    for i, v in enumerate(g):
        cur = v if v < cur else (a_r * cur + (1 - a_r) * v)
        out[i] = cur
    return x * out[:, None], float(20 * np.log10(out.min()))


def compressor(x, thresh_db=-26.0, ratio=2.0, attack=0.005, release=0.15, knee_db=6.0):
    """Gentle feed-forward bus compressor (RMS detector): lifts sound bodies relative to their transients."""
    det = np.sqrt(np.convolve((x ** 2).mean(axis=1), np.ones(int(0.01 * SR)) / int(0.01 * SR), mode="same") + 1e-12)
    lv = 20 * np.log10(det)
    over = lv - thresh_db
    gr = np.where(over <= -knee_db / 2, 0.0,
                  np.where(over >= knee_db / 2, over * (1 - 1 / ratio),
                           (1 - 1 / ratio) * (over + knee_db / 2) ** 2 / (2 * knee_db)))
    a_a, a_r = np.exp(-1 / (SR * attack)), np.exp(-1 / (SR * release))
    sm = np.empty_like(gr)
    cur = 0.0
    for i, v in enumerate(gr):
        cur = a_a * cur + (1 - a_a) * v if v > cur else a_r * cur + (1 - a_r) * v
        sm[i] = cur
    return x * (10 ** (-sm / 20))[:, None]


def main():
    cues = json.loads((ROOT / "audio" / "cues.json").read_text())["cues"]
    n = int(SR * DUR)
    bus = np.zeros((n, 2))
    rotation = {}
    report = []
    for q in cues:
        for layer_spec in KINDS[q["kind"]]:
            take, role, anchor, extra_db, slice_from = layer_spec[:5]
            hp_hz = layer_spec[5] if len(layer_spec) > 5 else None
            names = take.split("|")
            k = rotation.get((q["kind"], take), 0)
            rotation[(q["kind"], take)] = k + 1
            name = names[k % len(names)]
            x = load(name)
            a_t = anchor_time(x, anchor)
            if slice_from:
                x = x[int(slice_from * SR):]
                a_t -= slice_from
            # trim leading silence (keep 5 ms before the audible start)
            st = max(0.0, anchor_time(x, "start") - 0.005)
            x = x[int(st * SR):]
            a_t -= st
            if hp_hz:
                x = sosfilt(butter(2, hp_hz, "highpass", fs=SR, output="sos"), x, axis=0)
            x = fade(x)
            pk = np.abs(x).max() + 1e-12
            gain = 10 ** ((ROLE_PEAK[role] + q["gain_db"] + extra_db) / 20) / pk
            x = x * gain
            t0 = q["frame"] / FPS - a_t
            i0 = int(round(t0 * SR))
            j0 = max(0, -i0)
            i0 = max(0, i0)
            seg = x[j0:j0 + (n - i0)]
            bus[i0:i0 + len(seg)] += seg
            report.append({"frame": q["frame"], "kind": q["kind"], "take": name, "role": role, "anchor_s": round(a_t, 3),
                           "placed_at_s": round(t0, 3), "peak_dbfs": round(20 * np.log10(np.abs(seg).max() + 1e-12), 1)})

    # master filters
    hp = butter(2, 25, "highpass", fs=SR, output="sos")
    lp = butter(2, 15500, "lowpass", fs=SR, output="sos")
    bus = sosfilt(lp, sosfilt(hp, bus, axis=0), axis=0)

    bus = compressor(bus)
    meter = pyln.Meter(SR, block_size=0.4)
    raw_lufs = meter.integrated_loudness(bus)
    # gain toward -14 LUFS, but never more than 6 dB of limiting on the strongest hit (real-sfx: a sparse
    # film is not forced to -14; accept the honest number)
    target = -14.0
    want = target - raw_lufs
    tp = true_peak_db(bus)
    gain_db = min(want, -1.5 - tp + 6.0)
    sfx = bus * 10 ** (gain_db / 20)

    # bed: one long, dark, steady recording at -54 dBFS (median of 250 ms windows) under the whole film
    bed_file = ROOT / "audio" / "library" / "bed.mp3"
    bed_info = None
    if bed_file.exists():
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(bed_file), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        bed = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)
        if len(bed) < n:
            reps = int(np.ceil(n / len(bed))) + 1
            xf = int(0.5 * SR)
            out = bed.copy()
            for _ in range(reps):
                ramp = np.linspace(0, 1, xf)[:, None]
                out = np.concatenate([out[:-xf], out[-xf:] * (1 - ramp) + bed[:xf] * ramp, bed[xf:]])
            bed = out
        bed = bed[:n]
        bed = sosfilt(butter(2, 900, "lowpass", fs=SR, output="sos"), bed, axis=0)  # dark
        # steady: a slow auto-leveller flattens the take's level ripple (real-sfx bed rule: ripple <= 4 dB)
        hop = int(0.1 * SR)
        nb = len(bed) // hop
        lv = np.sqrt((bed[: nb * hop].mean(axis=1).reshape(-1, hop) ** 2).mean(axis=1) + 1e-12)
        g = np.clip(np.median(lv) / lv, 0.5, 2.0)
        g = np.convolve(g, np.ones(5) / 5, mode="same")
        gs = np.interp(np.arange(len(bed)), np.arange(nb) * hop + hop / 2, g)
        bed = bed * gs[:, None]
        w = int(0.25 * SR)
        rms = np.sqrt((bed[: n // w * w].mean(axis=1).reshape(-1, w) ** 2).mean(axis=1))
        med = float(np.median(20 * np.log10(rms + 1e-12)))
        bed = bed * 10 ** ((-52.0 - med) / 20)
        f_in, f_out = int(0.02 * SR), int(0.4 * SR)
        bed[:f_in] *= np.linspace(0, 1, f_in)[:, None]
        # no fade at the end: sound to the last frame (Ozen: no silent tail)
        bed_info = {"file": bed_file.name, "median_250ms_dbfs": -52.0}
    else:
        rng = np.random.default_rng(3)
        bed = sosfilt(butter(2, 600, "lowpass", fs=SR, output="sos"), rng.standard_normal((n, 2)), axis=0)
        bed *= 10 ** (-62 / 20) / (np.sqrt((bed ** 2).mean()) + 1e-12)
        bed_info = {"file": "synth room tone (fallback)", "rms_dbfs": -62.0}

    mix, gr_db = limiter(sfx + bed, ceiling_db=-1.5)
    nobed, _ = limiter(sfx, ceiling_db=-1.5)

    def write(path, x):
        pcm = np.clip(x, -1, 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                        "-c:a", "pcm_s24le", str(path)], input=pcm.tobytes(), check=True)

    write(ROOT / "audio" / "sfx.wav", mix)
    write(ROOT / "audio" / "sfx_nobed.wav", nobed)
    lufs = meter.integrated_loudness(mix)
    summary = {"cues": len(cues), "placements": len(report), "raw_lufs": round(raw_lufs, 2), "gain_db": round(gain_db, 2),
               "limiter_max_gr_db": round(gr_db, 2), "final_lufs": round(lufs, 2), "final_true_peak_dbtp": round(true_peak_db(mix), 2),
               "bed": bed_info}
    (ROOT / "audio" / "mix_report.json").write_text(json.dumps({"summary": summary, "placements": report}, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
