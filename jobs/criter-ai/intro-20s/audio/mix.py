#!/usr/bin/env python3
"""SFX-only soundtrack for the CriterAI intro, built from the film's own cue list.

    python3 mix.py <cues.json> <out.wav> [--stems DIR]

Sources
  sfx/eleven/*.mp3  designed sounds from ElevenLabs Sound Effects v3 (the elevenlabs/skills `sound-effects` approach)
  sfx/synth/*.wav   tuned UI sounds rendered from sfx/patches/*.json with GhazaGG/Game-Sound-Effect-for-Claude (game-sfx)
Rules (Ozen skill sound.md, product-launch-motion): every sound is placed by its own measured peak or onset on a cue
exported from film.js, 2-3 ms fades on every placement, a room-tone floor so there is never digital silence, a dip
before the biggest hit, gentle 15.5 kHz low-pass on the master, then -14 LUFS integrated with a true-peak ceiling.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
from scipy import signal

SR = 48000
HERE = Path(__file__).resolve().parent
EL = HERE / 'sfx' / 'eleven'
SY = HERE / 'sfx' / 'synth'
TARGET_LUFS = -14.0
CEILING_DBTP = -2.0


# ------------------------------------------------------------------ io and basic dsp
@lru_cache(maxsize=None)
def _decode(path: str) -> np.ndarray:
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def load(path: Path, start: float = 0.0, length: float | None = None) -> np.ndarray:
    x = _decode(str(path))[int(start * SR):]
    return (x[:int(length * SR)] if length else x).copy()


def mono(x):
    return x.mean(axis=1)


def fades(x, fin=0.003, fout=0.012):
    x = x.copy()
    n, m = min(len(x), int(fin * SR)), min(len(x), int(fout * SR))
    if n > 0:
        x[:n] *= np.linspace(0, 1, n)[:, None]
    if m > 0:
        x[-m:] *= np.linspace(1, 0, m)[:, None] ** 2
    return x


def butter(x, kind, fc, order=4):
    sos = signal.butter(order, fc, btype=kind, fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def env_db(x, win=0.010):
    m = mono(x) ** 2
    k = max(1, int(win * SR))
    e = np.sqrt(np.convolve(m, np.ones(k) / k, mode='same') + 1e-12)
    return 20 * np.log10(e)


def trim_lead(x, rel_db=-42.0, pre=0.002):
    e = env_db(x, 0.004)
    idx = np.argmax(e > e.max() + rel_db)
    return x[max(0, idx - int(pre * SR)):]


def trim_tail(x, rel_db=-60.0, fout=0.04):
    e = env_db(x, 0.02)
    above = np.where(e > e.max() + rel_db)[0]
    end = int(above[-1]) if len(above) else len(x)
    return fades(x[:end + 1], 0.0, fout)


def peak_t(x):
    """time of the loudest 10 ms (the sound's own peak)"""
    return float(np.argmax(env_db(x, 0.010))) / SR


def onset_t(x, rel_db=-24.0):
    e = env_db(x, 0.003)
    return float(np.argmax(e > e.max() + rel_db)) / SR


def norm_peak(x, db=0.0):
    p = np.abs(x).max()
    return x * (10 ** (db / 20) / p) if p > 0 else x


def resample_semitones(x, semis):
    """pitch by playback rate (shorter when higher), like a sampler"""
    ratio = 2 ** (-semis / 12)
    up, down = int(round(ratio * 1000)), 1000
    g = np.gcd(up, down)
    return signal.resample_poly(x, up // g, down // g, axis=0)


def body(x, drive=5.0, lo=110, hi=1200, mix=0.55):
    """parallel saturation band: harmonics of a sub hit so it survives laptop and phone speakers"""
    y = np.tanh(drive * x / (np.abs(x).max() + 1e-9))
    y = butter(butter(y, 'highpass', lo, 2), 'lowpass', hi, 2)
    y *= np.abs(x).max() / (np.abs(y).max() + 1e-9)
    return x + mix * y


def tame_hit(x, hp=42, clip=1.8):
    """sub-heavy hits: high-pass the rumble nobody's speakers play, then soft-clip the first transient a little,
    so the master limiter does not have to crush the film's biggest moments"""
    x = butter(x, 'highpass', hp, 4)
    pk = np.abs(x).max()
    return np.tanh(clip * x / pk) * pk / np.tanh(clip)


def pan(x, p):
    """constant-power pan, p in [-1, 1]"""
    a = (p + 1) * np.pi / 4
    return np.stack([x[:, 0] * np.cos(a) * np.sqrt(2), x[:, 1] * np.sin(a) * np.sqrt(2)], axis=1)


def st(x):
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


# ------------------------------------------------------------------ the sound palette (5 families)
def densest(x, length):
    e = mono(x) ** 2
    k = int(length * SR)
    c = np.convolve(e, np.ones(k), mode='valid')
    i = int(np.argmax(c))
    return x[i:i + k]


def slice_ticks(path, n=3):
    x = load(path)
    e = env_db(x, 0.002)
    peaks, _ = signal.find_peaks(e, height=e.max() - 14, distance=int(0.06 * SR))
    peaks = sorted(peaks, key=lambda p: -e[p])[:n]
    return [fades(x[max(0, p - int(0.004 * SR)): p + int(0.045 * SR)], 0.001, 0.02) for p in sorted(peaks)]


def build_clock(dur):
    ticks = slice_ticks(EL / 'clock_4.mp3', 3)
    gaps = np.array([0.15, 0.125, 0.105, 0.09, 0.077, 0.066, 0.057, 0.05])
    gaps *= (dur - 0.03) / gaps.sum()
    out = np.zeros((int((dur + 0.2) * SR), 2))
    t = 0.0
    for k, g in enumerate(gaps):
        tk = resample_semitones(ticks[k % len(ticks)], 0.35 * k)
        tk = norm_peak(tk, -6 + 0.5 * k)
        i = int(t * SR)
        out[i:i + len(tk)] += tk[:len(out) - i]
        t += g
    return out


def build(sid, dur=None):
    """returns (stereo clip, anchor_offset_seconds_for_'peak', onset_offset) at a reference level (peak 0 dBFS = loudest hit)"""
    if sid == 'air':
        x = load(EL / 'air_2.mp3', 0.12, 3.3)
        x = butter(butter(x, 'highpass', 45, 2), 'lowpass', 7000, 2)
        x = fades(norm_peak(x, -20), 0.03, 0.7)
    elif sid == 'tick':
        x = norm_peak(st(load(SY / 'tick.wav')), -11)
    elif sid == 'tick_small':
        x = norm_peak(st(load(SY / 'tick_small.wav')), -17)
    elif sid == 'pop':
        x = norm_peak(st(load(SY / 'pop_soft.wav')), -12)
    elif sid == 'click':
        x = norm_peak(st(load(SY / 'ui_click.wav')), -7)
    elif sid == 'whoosh':
        x = norm_peak(trim_tail(trim_lead(load(EL / 'whoosh_3.mp3'))), -12)
    elif sid == 'whoosh_b':
        x = norm_peak(trim_tail(trim_lead(load(EL / 'whoosh_1.mp3'))), -12)
    elif sid == 'swish':
        x = resample_semitones(trim_tail(trim_lead(load(EL / 'whoosh_1.mp3'))), 5)
        x = norm_peak(butter(x, 'highpass', 220, 2), -14)
    elif sid == 'send':
        x = resample_semitones(trim_tail(trim_lead(load(EL / 'whoosh_4.mp3'))), 3)
        x = norm_peak(butter(x, 'highpass', 180, 2), -12)
    elif sid == 'morph':
        x = resample_semitones(trim_tail(trim_lead(load(EL / 'whoosh_3.mp3'))), 7)
        x = norm_peak(butter(x, 'highpass', 400, 2), -17)
    elif sid == 'recede':
        x = resample_semitones(trim_tail(trim_lead(load(EL / 'whoosh_2.mp3'))), -4)
        x = norm_peak(butter(x, 'lowpass', 3200, 2), -12)
    elif sid == 'push':
        x = trim_tail(trim_lead(load(EL / 'whoosh_2.mp3')))
        x = norm_peak(butter(x, 'lowpass', 2400, 2), -15)
    elif sid == 'riser':
        x = trim_lead(load(EL / 'riser_2.mp3'))
        x = butter(x, 'lowpass', 9000, 2)
        x = fades(norm_peak(x, -10), 0.02, 0.006)
    elif sid == 'pen':
        x = norm_peak(trim_tail(trim_lead(load(EL / 'pen_2.mp3'))), -11)
    elif sid == 'bloom':
        x = load(EL / 'bloom_3.mp3', 0.2, 2.6)
        x = fades(norm_peak(butter(x, 'lowpass', 9000, 2), -13), 0.01, 1.0)
    elif sid == 'typing':
        x = densest(load(EL / 'typing_3.mp3'), dur or 0.6)
        x = fades(norm_peak(butter(x, 'highpass', 250, 2), -19), 0.006, 0.05)
    elif sid == 'clock':
        x = norm_peak(build_clock(dur or 0.7), -17)
    elif sid.startswith('check_'):
        x = norm_peak(st(load(SY / f'{sid}.wav')), -16)
    elif sid == 'chime':
        x = norm_peak(st(load(SY / 'check_chime.wav')), -8)
    elif sid == 'logo_chime':
        x = norm_peak(st(load(SY / 'check_logo.wav')), -7)
    elif sid == 'small_chime':
        x = norm_peak(st(load(SY / 'check_small.wav')), -18)
    elif sid == 'badge':
        h = norm_peak(body(tame_hit(trim_tail(trim_lead(load(EL / 'lowhit_2.mp3'))), clip=3.4)), -6)
        s = norm_peak(trim_lead(load(EL / 'shimmer_2.mp3')), -17)
        x = np.zeros((max(len(h), len(s)), 2)); x[:len(h)] += h; x[:len(s)] += s
    elif sid == 'thud':
        h = tame_hit(trim_lead(load(EL / 'lowhit_4.mp3'))[:int(0.75 * SR)])
        x = fades(norm_peak(body(h, drive=4, mix=0.45), -9), 0.002, 0.4)
    elif sid == 'logo_hit':
        x = norm_peak(body(tame_hit(trim_tail(trim_lead(load(EL / 'lowhit_3.mp3'))), clip=4.0), drive=5, mix=0.6), -1)
    elif sid == 'shimmer':
        x = norm_peak(trim_tail(trim_lead(load(EL / 'shimmer_2.mp3'))), -17)
    elif sid == 'shimmer_end':
        x = norm_peak(trim_lead(load(EL / 'shimmer_4.mp3')), -15)
        x = fades(x, 0.004, 0.25)
    else:
        raise KeyError(sid)
    return st(x)


# where each sound sits left-right, following the picture (subtle)
PAN = {'click@5.27': 0.28, 'send': 0.12, 'click@8.10': -0.18, 'click@18.72': 0.06, 'pop@3.88': -0.25}


def pan_for(sid, t):
    for k, v in PAN.items():
        name, _, at = k.partition('@')
        if name == sid and (not at or abs(float(at) - t) < 0.05):
            return v
    return 0.0


# ------------------------------------------------------------------ mastering
def kweight_lufs(x):
    return pyln.Meter(SR).integrated_loudness(x)


def true_peak_db(x, os=4):
    y = signal.resample_poly(x, os, 1, axis=0)
    return 20 * np.log10(np.abs(y).max() + 1e-12)


def limiter(x, ceiling_db, look=0.0015, release=0.09, os=4):
    """look-ahead peak limiter on a 4x oversampled detector, so inter-sample peaks stay under the ceiling"""
    c = 10 ** (ceiling_db / 20)
    det = np.abs(signal.resample_poly(x, os, 1, axis=0)).max(axis=1)
    det = det.reshape(-1, os).max(axis=1) if len(det) % os == 0 else np.pad(det, (0, os - len(det) % os)).reshape(-1, os).max(axis=1)
    det = det[:len(x)]
    need = np.minimum(1.0, c / np.maximum(det, 1e-12))
    la = max(1, int(look * SR))
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * la + 1, mode='nearest')  # running min, centred = look-ahead
    g = np.minimum(g, need)
    # release smoothing (attack instant, thanks to the look-ahead minimum)
    a = np.exp(-1.0 / (release * SR))
    out = np.empty_like(g)
    prev = 1.0
    for i, v in enumerate(g):
        prev = v if v < prev else a * prev + (1 - a) * v
        out[i] = prev
    return x * out[:, None]


def soft_clip(x, ceiling_db, knee_db=6.0, os=4):
    """4x-oversampled soft clipper: leaves everything below (ceiling - knee) untouched and bends only the peak
    samples towards the ceiling, so hits keep their body instead of being pulled down by a limiter's release"""
    c = 10 ** (ceiling_db / 20); t = c * 10 ** (-knee_db / 20)
    y = signal.resample_poly(x, os, 1, axis=0)
    a = np.abs(y)
    over = a > t
    y[over] = np.sign(y[over]) * (t + (c - t) * np.tanh((a[over] - t) / (c - t)))
    return signal.resample_poly(y, 1, os, axis=0)


def master(mix):
    mix = butter(mix, 'lowpass', 15500, 2)
    mix = butter(mix, 'highpass', 28, 2)
    gain = 10 ** ((TARGET_LUFS - kweight_lufs(mix)) / 20)
    for _ in range(10):  # the limiter takes some loudness back: iterate until the limited output sits on target
        y = limiter(soft_clip(mix * gain, CEILING_DBTP + 0.3), CEILING_DBTP - 0.3)
        err = TARGET_LUFS - kweight_lufs(y)
        if abs(err) < 0.05:
            break
        gain *= 10 ** (err / 20)
    return y


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cues')
    ap.add_argument('out')
    ap.add_argument('--stems', default=None)
    a = ap.parse_args()
    meta = json.loads(Path(a.cues).read_text())
    dur = float(meta['dur'])
    n = int(round(dur * SR))
    mix = np.zeros((n + int(2 * SR), 2))
    log = []
    for c in meta['cues']:
        sid, t, db, at = c['s'], float(c['t']), float(c.get('db', 0)), c.get('at', 'peak')
        x = build(sid, c.get('dur'))
        off = peak_t(x) if at == 'peak' else onset_t(x)
        start = t - off
        x = fades(x, 0.0025, 0.012) * 10 ** (db / 20)
        x = pan(x, pan_for(sid, t))
        i0 = int(round(start * SR))
        if i0 < 0:
            x = fades(x[-i0:], 0.004, 0.0); i0 = 0
        mix[i0:i0 + len(x)] += x[:len(mix) - i0]
        log.append((t, sid, at, start, len(x) / SR, db))
    mix = mix[:n]
    # dips: the ear finds the peak after a moment of less
    tt = np.arange(n) / SR
    for d in meta.get('dips', []):
        t0, t1, ddb = float(d['t0']), float(d['t1']), float(d['db'])
        w = np.clip((tt - t0) / 0.06, 0, 1) * np.clip((t1 - tt) / 0.02, 0, 1)
        mix *= (10 ** (ddb * w / 20))[:, None]
    # room-tone floor (about -65 dBFS) so there is never digital silence
    rng = np.random.default_rng(3)
    floor = butter(rng.standard_normal((n, 2)), 'lowpass', 900, 2)
    floor *= 10 ** (-65 / 20) / np.sqrt(np.mean(floor ** 2))
    pre = mix + floor
    y = master(pre)
    y[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))[:, None]
    import wave
    pcm = np.clip(y, -1, 1)
    pcm = (pcm * 8388607).astype(np.int32)
    with wave.open(a.out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
        b = pcm.astype('<i4').tobytes()
        w.writeframes(b''.join(b[i:i + 3] for i in range(0, len(b), 4)))
    print(f'wrote {a.out}  {dur:.2f} s  integrated {kweight_lufs(y):.2f} LUFS  true peak {true_peak_db(y):.2f} dBTP  ({len(log)} cues)')
    for t, sid, at, start, ln, db in log:
        print(f'  {t:6.2f}s {sid:12s} {at:5s} starts {start:6.3f}s  len {ln:4.2f}s  {db:+.0f} dB')


if __name__ == '__main__':
    main()
