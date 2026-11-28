#!/usr/bin/env python3
"""Voiced cut of the CriterAI intro: the ElevenLabs take placed line by line on the picture, over the SFX mix.

    python3 vo.py <cues.json> <out.wav> <out.srt>

Follows the Ozen skill (sound.md 4.4): split the take into lines (by its pauses), level-match every line, place each
on its beat just after its words appear, no overlaps, duck the SFX under speech (the voice sits 8 dB or more above
everything while it speaks), then -14 LUFS with a true-peak ceiling. The SFX bus is rebuilt from the same cues as
mix.py, so the sound effects are identical to the SFX-only cut.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
import pyloudnorm as pyln

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mix', HERE / 'mix.py')
mix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mix)
SR = mix.SR

TAKE = HERE / 'vo' / 'take1-elevenlabs-v4.mp3'
# (text, take start s, take end s, film start s, tempo) - take spans found by silence (gaps >= 0.2 s, refined to the
# 0.18-0.2 s pauses inside the two runs the voice read together); film starts from VOICEOVER.md. Tempo > 1 tightens a
# line by a few percent (pitch kept) where the read is longer than its on-screen slot.
LINES = [
    ('Which visa?', 0.00, 0.86, 0.03, 1.05),
    ('Which documents?', 1.06, 2.07, 1.00, 1.07),
    ("What's next?", 2.27, 3.00, 2.09, 1.00),
    ('Just ask CriterAI.', 3.35, 5.08, 3.30, 1.00),
    ('Get an instant answer.', 5.40, 6.81, 5.20, 1.00),
    ('Then a registered migration agent checks it,', 7.08, 9.56, 6.82, 1.05),
    ('in as little as thirty minutes.', 9.80, 11.47, 9.95, 1.00),
    ('Lawyer trained.', 11.84, 12.75, 12.00, 1.06),
    ('Law driven.', 12.93, 13.84, 13.02, 1.06),
    ('AI delivered.', 14.10, 15.24, 14.03, 1.04),
    ('Start for free at criter.ai.', 15.60, 17.99, 17.42, 1.00),
]
LINE_LUFS = -18.0      # every line level-matched to this (speech loudness)
DUCK_DB = 11.0         # SFX under speech
DUCK_LOOK = 0.06       # duck lands just before the voice
DUCK_RELEASE = 0.28


def decode(path, start, end, tempo=1.0):
    af = f'atrim=start={start}:end={end},asetpts=N/SR/TB'
    if abs(tempo - 1.0) > 1e-3:
        af += f',atempo={tempo}'
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-af', af, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def build_sfx_bus(meta, n):
    bus = np.zeros((n + int(2 * SR), 2))
    for c in meta['cues']:
        sid, t, db, at = c['s'], float(c['t']), float(c.get('db', 0)), c.get('at', 'peak')
        x = mix.build(sid, c.get('dur'))
        off = mix.peak_t(x) if at == 'peak' else mix.onset_t(x)
        x = mix.fades(x, 0.0025, 0.012) * 10 ** (db / 20)
        x = mix.pan(x, mix.pan_for(sid, t))
        i0 = int(round((t - off) * SR))
        if i0 < 0:
            x = mix.fades(x[-i0:], 0.004, 0.0); i0 = 0
        bus[i0:i0 + len(x)] += x[:len(bus) - i0]
    bus = bus[:n]
    tt = np.arange(n) / SR
    for d in meta.get('dips', []):
        t0, t1, ddb = float(d['t0']), float(d['t1']), float(d['db'])
        w = np.clip((tt - t0) / 0.06, 0, 1) * np.clip((t1 - tt) / 0.02, 0, 1)
        bus *= (10 ** (ddb * w / 20))[:, None]
    return bus


def build_voice(n):
    meter = pyln.Meter(SR)
    v = np.zeros(n)
    placed = []
    for text, a, b, t, tempo in LINES:
        x = decode(TAKE, max(0.0, a - 0.02), b + 0.06, tempo)
        x = mix.butter(x, 'highpass', 75, 2)
        x = mix.fades(np.stack([x, x], 1), 0.005, 0.03)[:, 0]
        x *= 10 ** ((LINE_LUFS - meter.integrated_loudness(np.pad(x, (0, max(0, int(0.45 * SR) - len(x)))))) / 20)
        i0 = int(round(t * SR))
        v[i0:i0 + len(x)] += x[:n - i0]
        placed.append((text, t, t + len(x) / SR))
    for (_, _, e1), (txt, s2, _) in zip(placed, placed[1:]):
        assert s2 >= e1 - 0.02, f'lines overlap before "{txt}" ({e1:.2f} > {s2:.2f})'
    return v, placed


def duck_curve(v, n):
    env = np.abs(v)
    k = int(0.02 * SR)
    env = np.sqrt(np.convolve(env ** 2, np.ones(k) / k, mode='same'))
    act = (20 * np.log10(env + 1e-9) > -42).astype(float)
    look = int(DUCK_LOOK * SR)
    act = np.maximum(act, np.concatenate([act[look:], np.zeros(look)]))  # start ducking a little early
    a_rel = np.exp(-1.0 / (DUCK_RELEASE * SR)); a_att = np.exp(-1.0 / (0.012 * SR))
    g = np.empty(n); prev = 0.0
    for i in range(n):
        x = act[i]
        prev = a_att * prev + (1 - a_att) * x if x > prev else a_rel * prev + (1 - a_rel) * x
        g[i] = prev
    return 10 ** (-DUCK_DB * g / 20), g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cues'); ap.add_argument('out'); ap.add_argument('srt')
    a = ap.parse_args()
    meta = json.loads(Path(a.cues).read_text())
    n = int(round(float(meta['dur']) * SR))
    sfx = build_sfx_bus(meta, n)
    voice, placed = build_voice(n)
    duck, active = duck_curve(voice, n)
    rng = np.random.default_rng(3)
    floor = mix.butter(rng.standard_normal((n, 2)), 'lowpass', 900, 2)
    floor *= 10 ** (-65 / 20) / np.sqrt(np.mean(floor ** 2))
    pre = sfx * duck[:, None] + np.stack([voice, voice], 1) + floor
    y = mix.master(pre)
    y[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))[:, None]
    # voice margin over the (ducked) SFX while speaking, in 100 ms windows
    g = 10 ** ((mix.kweight_lufs(y) - mix.kweight_lufs(mix.butter(mix.butter(pre, 'lowpass', 15500, 2), 'highpass', 28, 2))) / 20)
    k = int(0.1 * SR)
    def rms_db(z):
        return 20 * np.log10(np.sqrt(np.convolve(z ** 2, np.ones(k) / k, mode='same')) + 1e-9)
    vdb, sdb = rms_db(voice * g), rms_db(sfx.mean(1) * duck * g)
    speaking = active > 0.9
    margin = (vdb - sdb)[speaking]
    pcm = (np.clip(y, -1, 1) * 8388607).astype(np.int32).astype('<i4').tobytes()
    with wave.open(a.out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
        w.writeframes(b''.join(pcm[i:i + 3] for i in range(0, len(pcm), 4)))
    def ts(s):
        ms = int(round(s * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'
    with open(a.srt, 'w') as f:
        for i, (text, s, e) in enumerate(placed, 1):
            nxt = placed[i][1] - 0.02 if i < len(placed) else float(meta['dur'])
            f.write(f'{i}\n{ts(s)} --> {ts(min(e + 0.25, nxt))}\n{text}\n\n')
    print(f'wrote {a.out}: integrated {mix.kweight_lufs(y):.2f} LUFS, true peak {mix.true_peak_db(y):.2f} dBTP')
    print(f'voice over SFX while speaking: median {np.median(margin):.1f} dB, 10th percentile {np.percentile(margin, 10):.1f} dB')
    for text, s, e in placed:
        print(f'  {s:6.2f}-{e:6.2f}s  {text}')


if __name__ == '__main__':
    main()
