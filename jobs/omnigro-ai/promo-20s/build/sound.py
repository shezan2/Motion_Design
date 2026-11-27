"""OmniGro promo: original music bed + SFX, mixed and mastered (no samples, no licence needed).

    python3 build/sound.py      reads audio/cues.json (written by render.cjs from the film timeline)
                                writes audio/music.wav, audio/sfx.wav, audio/mix.wav (48 kHz, -14 LUFS, <= -1 dBTP)

Music: 120 BPM in A major. The beat grid is offset by -2 frames so the click (f58), "Where's your brand?"
(f118) and the climb's landing (f178) sit exactly on the downbeats of bars 2, 3 and 4.
I - I - vi - IV | I - V - vi - IV | (V) I : quiet pulse under the question, a riser and a 0.25 s dip into the
landing, a soft four-on-the-floor groove under the proof, the groove drops out for the payoff, and the
logo lands on a free-time A chord with a long tail.
SFX (5 families): clicks/ticks (keys, press, rows, counter), whooshes (scrolls), low hits (line, landing,
logo), a pop (#1 badge), a reverse swell (letters converging).
"""
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly

JOB = Path(__file__).resolve().parent.parent
CUES = json.loads((JOB / 'audio/cues.json').read_text())
FPS = CUES['fps']
SR = 48000
DUR = CUES['total'] / FPS               # 20.0 s exactly
N = int(round(DUR * SR))
rng = np.random.default_rng(20261127)
BEAT = 0.5                              # 120 BPM
GRID0 = -2 / FPS                        # beat 0 of bar 1 sits 2 frames before t=0


def beat_t(bar, beat=0.0):              # bar is 1-based
    return GRID0 + ((bar - 1) * 4 + beat) * BEAT


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def sos(kind, f, o=2):
    return butter(o, f, btype=kind, fs=SR, output='sos')


def lp(x, f, o=2): return sosfilt(sos('low', f, o), x)
def hp(x, f, o=2): return sosfilt(sos('high', f, o), x)
def bp(x, lo, hi, o=2): return sosfilt(sos('band', [lo, hi], o), x)


def stereo():
    return np.zeros((2, N))


def place(bus, sig, t, gain=1.0, pan=0.0):
    """add a mono or stereo signal at time t (s); constant-power pan for mono"""
    i = int(round(t * SR))
    if sig.ndim == 1:
        sig = np.vstack([sig * np.cos((pan + 1) * np.pi / 4) * 1.4142, sig * np.sin((pan + 1) * np.pi / 4) * 1.4142])
    a, b = max(0, i), min(N, i + sig.shape[1])
    if b <= a:
        return
    bus[:, a:b] += sig[:, a - i:b - i] * gain


def fade_in(x, ms=2.5):
    n = max(1, int(ms * SR / 1000)); x = x.copy(); x[..., :n] *= np.linspace(0, 1, n); return x


def env_exp(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


def make_ir(rt=1.7, pre=0.022, damp=5200, seed=3):
    r = np.random.default_rng(seed)
    n = int(rt * SR); t = np.arange(n) / SR
    decay = np.exp(-6.91 * t / rt)
    ir = np.zeros((2, n + int(pre * SR)))
    for c in range(2):
        noise = r.standard_normal(n) * decay
        noise = lp(noise, damp) + 0.25 * lp(noise, 1800)
        ir[c, int(pre * SR):] = noise
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    return ir


IR = make_ir()


def reverb(bus, wet):
    out = np.zeros_like(bus)
    mono = bus.mean(axis=0)
    for c in range(2):
        out[c] = fftconvolve(mono, IR[c])[:N]
    return out * wet


# ======================================================================= music
CH = {   # pad voicing (midi), bass root (midi), arp tones (midi)
    'A':    ([57, 61, 64, 71, 76], 33, [69, 73, 76, 83]),
    'F#m':  ([54, 57, 61, 64, 69], 30, [66, 69, 73, 76]),
    'D':    ([50, 57, 61, 64, 66], 38, [62, 66, 69, 73, 76]),
    'E':    ([52, 56, 59, 61, 68], 40, [64, 68, 71, 73]),
    'Esus': ([52, 57, 59, 64, 69], 40, [64, 69, 71, 76]),
}
# (start time, end time, chord)
LOGO_T = next(f for f, k, g in CUES['cues'] if k == 'logo') / FPS
PROG = [
    (0.0, beat_t(3), 'A'),
    (beat_t(3), beat_t(4), 'F#m'),
    (beat_t(4), beat_t(5), 'D'),
    (beat_t(5), beat_t(6), 'A'),
    (beat_t(6), beat_t(7), 'E'),
    (beat_t(7), beat_t(8), 'F#m'),
    (beat_t(8), beat_t(9) + .3, 'D'),
    (beat_t(9) + .3, LOGO_T, 'Esus'),
    (LOGO_T, DUR, 'A'),
]


def chord_at(t):
    for a, b, c in PROG:
        if a <= t < b:
            return c
    return 'A'


def saw_soft(f, n, harm=9, detune=0.0, phase=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, harm + 1):
        if f * k > 9000:
            break
        out += np.sin(2 * np.pi * f * (1 + detune) * k * t + phase * k) / k ** 1.5
    return out


def pad_bus():
    bus = stereo()
    for a, b, c in PROG:
        notes = CH[c][0]
        t0, t1 = a, b
        n = int((t1 - t0 + 1.2) * SR)
        att, rel = (0.35 if a > 0 else 0.6), 0.9
        e = np.minimum(1, np.arange(n) / SR / att)
        tail = np.clip((t1 - t0 + rel - np.arange(n) / SR) / rel, 0, 1)
        e = e * np.minimum(1, tail) ** 1.5
        for side, dt in ((0, -0.0024), (1, 0.0024)):
            sig = np.zeros(n)
            for m in notes:
                f = mtof(m)
                sig += saw_soft(f, n, detune=dt, phase=rng.uniform(0, 6.28)) * 0.5 + saw_soft(f, n, detune=-dt * .6, phase=rng.uniform(0, 6.28)) * 0.5
            sig = hp(lp(sig, 1500 if c != 'A' or a < 1 else 1800, 2), 110, 2)
            place_side = np.zeros((2, n)); place_side[side] = sig * e
            place(bus, place_side, t0, 0.085)
    # slow filter-like breathing: brighter in the proof, darker under the question
    t = np.arange(N) / SR
    shape = np.interp(t, [0, 3.9, 4.6, 5.9, 6.4, 13.9, 14.6, 16.6, 20], [.75, .8, .55, .6, 1, 1, .8, 1, .9])
    return bus * shape


def arp_bus():
    bus = stereo()
    step = BEAT / 2
    k = 0
    tt = 0.0
    while True:
        t = GRID0 + k * step
        k += 1
        if t >= DUR:
            break
        if t < 0:
            continue
        # sections: soft in bars 1-2, sparse in bar 3, full in the proof, quiet pulse in the payoff, gone after the logo
        if t < beat_t(3):
            g = 0.55
        elif t < beat_t(4):
            g = 0.35 if (k % 2 == 0) else 0.0
            if t > beat_t(3, 3.0):
                g = 0.0
        elif t < beat_t(8):
            g = 0.9
        elif t < LOGO_T - .5:
            g = 0.4
        else:
            g = 0.0
        if g <= 0:
            continue
        tones = CH[chord_at(t + .01)][2]
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        m = tones[pat[(k - 1) % 8] % len(tones)]
        f = mtof(m)
        n = int(0.42 * SR)
        x = np.arange(n) / SR
        sig = (np.sin(2 * np.pi * f * x) + 0.28 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x / .05) + 0.1 * np.sin(2 * np.pi * 3 * f * x) * np.exp(-x / .03))
        sig *= np.exp(-x / 0.16) * np.minimum(1, x / 0.003)
        sig = lp(sig, 5200)
        vel = 0.75 + 0.25 * ((k % 4) == 1)
        place(bus, sig, t, 0.09 * g * vel, pan=(-.35 if k % 2 else .35))
    return bus


def bass_bus():
    bus = stereo()
    for a, b, c in PROG:
        root = mtof(CH[c][1])
        if a >= beat_t(4) and a < beat_t(8):          # groove: pulse on every beat
            hits = np.arange(a, b - 1e-6, BEAT)
            for h in hits:
                n = int(0.46 * SR); x = np.arange(n) / SR
                sig = .55 * np.sin(2 * np.pi * root * x) + .5 * np.sin(2 * np.pi * 2 * root * x) + .28 * np.sin(2 * np.pi * 3 * root * x) + .12 * np.sin(2 * np.pi * 4 * root * x)
                sig *= np.minimum(1, x / 0.008) * np.exp(-x / 0.3)
                place(bus, np.tanh(sig * 1.3), h, 0.085)
        else:                                          # held notes elsewhere
            n = int((b - a + .4) * SR); x = np.arange(n) / SR
            sig = .55 * np.sin(2 * np.pi * root * x) + .45 * np.sin(2 * np.pi * 2 * root * x) + .2 * np.sin(2 * np.pi * 3 * root * x)
            e = np.minimum(1, x / 0.25) * np.clip((b - a + .35 - x) / .35, 0, 1)
            g = 0.055 if a < beat_t(4) else 0.065
            if a >= LOGO_T:
                e *= np.exp(-x / 2.6)
                g = 0.085
            place(bus, sig * e, a, g)
    return hp(lp(bus, 420, 2), 32, 2)


def kick(n=None):
    n = int(0.42 * SR); x = np.arange(n) / SR
    f = 46 + 120 * np.exp(-x / 0.028)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.2) * .75
    knock = np.sin(2 * np.pi * 118 * x) * np.exp(-x / 0.035) * .45
    click = hp(rng.standard_normal(n), 2500) * np.exp(-x / 0.004) * 0.25
    return np.tanh((body + knock + click) * 1.3)


def clap():
    n = int(0.35 * SR); x = np.arange(n) / SR
    s = np.zeros(n)
    for d in (0, .009, .019):
        i = int(d * SR); s[i:] += rng.standard_normal(n - i) * np.exp(-(x[:n - i]) / (.011 if d < .019 else .09))
    return bp(s, 900, 3600) * 0.9


def hat(open_=False):
    n = int((0.16 if open_ else 0.05) * SR); x = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7500) * np.exp(-x / (0.05 if open_ else 0.012))


def drums_bus():
    bus = stereo(); kicks = []
    for bar in range(4, 8):
        for b in range(4):
            t = beat_t(bar, b)
            if bar == 4 and b == 0:
                continue                                # the landing hit owns this downbeat
            place(bus, kick(), t, 0.42); kicks.append(t)
            if b in (1, 3) and bar >= 5:
                place(bus, clap(), t, 0.16, pan=.05)
    # shaker 8ths from bar 2, hats 16ths in the proof
    for k in range(0, 160):
        t = GRID0 + k * BEAT / 4
        if t < 0 or t >= DUR:
            continue
        if beat_t(2) <= t < beat_t(3, 3) and k % 2 == 1:
            place(bus, bp(hat(), 4500, 11000), t, 0.05 + 0.02 * (k % 4 == 3), pan=.25)
        if beat_t(5) <= t < beat_t(8):
            g = 0.045 if k % 4 == 2 else 0.022
            place(bus, hat(k % 8 == 6), t, g, pan=-.2 if k % 2 else .2)
    return bus, kicks


def riser(t_end, length=1.05):
    n = int(length * SR); x = np.arange(n) / SR; u = x / length
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # sweep a band-pass upward in 12 slices
    sl = 12
    for i in range(sl):
        a, b = i * n // sl, (i + 1) * n // sl
        fc = 400 * (16 ** (i / sl))
        seg = bp(noise, fc * .7, min(fc * 1.6, 15000))[a:b]
        out[a:b] = seg
    tone = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (u * 1.6)) / SR) * 0.25
    sig = (out * 0.8 + tone) * (u ** 2.2)
    return sig, t_end - length


# ======================================================================= SFX
def sfx_key():
    n = int(0.035 * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 1800, 6500) * np.exp(-x / 0.0045) + np.sin(2 * np.pi * 180 * x) * np.exp(-x / 0.01) * 0.3
    return fade_in(s, 0.6)


def sfx_click():
    n = int(0.09 * SR); x = np.arange(n) / SR
    s = np.zeros(n)
    for d, g in ((0, 1), (0.032, .55)):
        i = int(d * SR)
        s[i:] += (bp(rng.standard_normal(n - i), 2200, 7000) * np.exp(-x[:n - i] / 0.003) + np.sin(2 * np.pi * 1450 * x[:n - i]) * np.exp(-x[:n - i] / 0.006) * .4) * g
    return fade_in(s, 0.4)


def sfx_tick(f=2100):
    n = int(0.12 * SR); x = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * x) * np.exp(-x / 0.022) + 0.5 * np.sin(2 * np.pi * f * 1.5 * x) * np.exp(-x / 0.012) + bp(rng.standard_normal(n), 3000, 9000) * np.exp(-x / 0.002) * .3
    return fade_in(s, 0.8)


def sfx_whoosh(length=0.55, peak=0.62, lo=250, hi=3600):
    n = int(length * SR); x = np.arange(n) / SR; u = x / length
    noise = rng.standard_normal(n)
    out = np.zeros(n); sl = 16
    for i in range(sl):
        a, b = i * n // sl, (i + 1) * n // sl
        k = (i + .5) / sl
        fc = lo * (hi / lo) ** (np.sin(np.pi * min(1, k / peak) / 2) if k < peak else 1 - .6 * (k - peak) / (1 - peak))
        out[a:b] = bp(noise, fc * .55, min(fc * 1.8, 16000))[a:b]
    e = np.where(u < peak, (u / peak) ** 2.4, np.exp(-(u - peak) / (1 - peak) * 3.2))
    return fade_in(out * e, 3)


def sfx_thud():
    n = int(0.5 * SR); x = np.arange(n) / SR
    f = 70 + 40 * np.exp(-x / 0.04)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.16) + lp(rng.standard_normal(n), 900) * np.exp(-x / 0.03) * .3
    return fade_in(np.tanh(s * 1.2), 2)


def sfx_hit():
    n = int(2.2 * SR); x = np.arange(n) / SR
    f = 34 + 52 * np.exp(-x / 0.09)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.75)
    punch = np.sin(2 * np.pi * 95 * x) * np.exp(-x / 0.05) * .5 + np.sin(2 * np.pi * 165 * x) * np.exp(-x / 0.07) * .35 + bp(rng.standard_normal(n), 180, 900) * np.exp(-x / 0.09) * .5
    crash = lp(rng.standard_normal(n), 7000) * np.exp(-x / 0.35) * .28
    air = hp(rng.standard_normal(n), 6000) * np.exp(-x / 0.6) * .12
    return fade_in(np.tanh((sub * 1.3 + punch + crash + air) * 1.1), 1.5)


def sfx_pop():
    n = int(0.16 * SR); x = np.arange(n) / SR
    f = 520 + 900 * (1 - np.exp(-x / 0.018))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.045) + np.sin(2 * np.pi * 2600 * x) * np.exp(-x / 0.01) * .2
    return fade_in(s, 1)


def sfx_suck(length=0.5):
    n = int(length * SR); x = np.arange(n) / SR; u = x / length
    noise = bp(rng.standard_normal(n), 900, 9000)
    tone = np.sin(2 * np.pi * np.cumsum(300 + 600 * u ** 2) / SR) * .3
    return (noise * .7 + tone) * u ** 3


def sfx_logo():
    n = int(3.6 * SR); x = np.arange(n) / SR
    f = 38 + 44 * np.exp(-x / 0.1)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.9) * .75
    body = lp(rng.standard_normal(n), 2500) * np.exp(-x / 0.12) * .35 + np.sin(2 * np.pi * 146.8 * x) * np.exp(-x / 0.3) * .35 + bp(rng.standard_normal(n), 200, 1200) * np.exp(-x / 0.16) * .4
    shimmer = np.zeros(n)
    for m, g, tau in ((81, .22, 1.6), (88, .16, 1.3), (93, .1, 1.0), (100, .06, .8)):     # A5 E6 A6 E7 bell partials
        fr = mtof(m)
        shimmer += (np.sin(2 * np.pi * fr * x) + .3 * np.sin(2 * np.pi * fr * 2.76 * x) * np.exp(-x / .2)) * np.exp(-x / tau) * g
    shimmer *= np.minimum(1, x / 0.004)
    return fade_in(np.tanh((sub * 1.25 + body) * 1.1) + shimmer, 1.5)


def build_sfx():
    bus = stereo()
    for f, kind, g in CUES['cues']:
        t = f / FPS
        if kind == 'key':
            place(bus, sfx_key(), t, 0.10 * g, pan=rng.uniform(-.15, .15))
        elif kind == 'click':
            place(bus, sfx_click(), t, 0.42 * g, pan=.3)
        elif kind == 'tick':
            place(bus, sfx_tick(2100 + rng.uniform(-150, 150)), t, 0.12 * g, pan=rng.uniform(-.25, .25))
        elif kind == 'count':
            place(bus, sfx_tick(3100), t, 0.05 * g)
        elif kind == 'whoosh':
            w = sfx_whoosh(); place(bus, w, t - 0.62 * len(w) / SR + 0.12, 0.30 * g)
        elif kind == 'thud':
            place(bus, sfx_thud(), t, 0.34 * g)
        elif kind == 'hit':
            place(bus, sfx_hit(), t, 0.62 * g)
        elif kind == 'pop':
            place(bus, sfx_pop(), t, 0.22 * g, pan=.2)
        elif kind == 'suck':
            s = sfx_suck(); logo = next(ff for ff, k, gg in CUES['cues'] if k == 'logo') / FPS
            place(bus, s, logo - len(s) / SR, 0.36 * g)
        elif kind == 'logo':
            place(bus, sfx_logo(), t, 0.62 * g)
    return bus


# ======================================================================= loudness (ITU-R BS.1770-4)
def k_weight(x):
    # pre-filter (high shelf) + RLB high-pass, biquads designed for 48 kHz
    b1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]; a1 = [1.0, -1.69065929318241, 0.73248077421585]
    b2 = [1.0, -2.0, 1.0]; a2 = [1.0, -1.99004745483398, 0.99007225036621]
    from scipy.signal import lfilter
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)


def lufs(st):
    y = k_weight(st)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    ms = []
    for i in range(0, st.shape[1] - blk + 1, hop):
        ms.append((y[:, i:i + blk] ** 2).mean(axis=1).sum())
    ms = np.array(ms)
    lk = -0.691 + 10 * np.log10(ms + 1e-12)
    g1 = ms[lk > -70]
    rel = -0.691 + 10 * np.log10(g1.mean()) - 10
    g2 = ms[(lk > -70) & (lk > rel)]
    return -0.691 + 10 * np.log10(g2.mean())


def true_peak(st):
    up = resample_poly(st, 4, 1, axis=1)
    return 20 * np.log10(np.abs(up).max() + 1e-12)


def limiter(st, ceiling_db=-1.3, look=0.0015, rel=0.08):
    c = 10 ** (ceiling_db / 20)
    peak = np.abs(resample_poly(st, 4, 1, axis=1)).max(axis=0)[::4][:st.shape[1]]
    need = np.minimum(1, c / np.maximum(peak, 1e-9))
    la = int(look * SR)
    # look-ahead: minimum over the window, then smooth release
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * la + 1)
    out = np.empty_like(g); cur = 1.0; a = np.exp(-1 / (rel * SR))
    for i in range(len(g)):
        cur = g[i] if g[i] < cur else a * cur + (1 - a) * g[i]
        out[i] = cur
    return st * out


def main():
    music = pad_bus() + arp_bus() + bass_bus()
    drums, kicks = drums_bus()
    # sidechain pad, arp and bass to the kick
    t = np.arange(N) / SR
    sc = np.ones(N)
    for k in kicks:
        i = int(k * SR); m = min(N, i + int(0.4 * SR))
        sc[i:m] = np.minimum(sc[i:m], 1 - 0.5 * np.exp(-(t[i:m] - k) / 0.11))
    music = music * sc
    r_t, r_t0 = None, None
    rs, r0 = riser(beat_t(4) - 0.10)
    place(music, rs, r0, 0.10)
    music = music + drums
    music = music + reverb(music, 0.22)
    # the dip: pull the bed down for 0.25 s before the landing so the ear finds the peak
    land = beat_t(4)
    dip = np.interp(t, [land - .32, land - .25, land - .01, land], [1, .12, .12, 1])
    music *= dip
    # fade the very end gently but never to digital silence
    music *= np.interp(t, [0, DUR - 1.1, DUR], [1, 1, .35])

    sfx = build_sfx()
    sfx = sfx + reverb(sfx, 0.12)

    mix = music * 1.0 + sfx * 1.0
    # room-tone floor (inaudible) so nothing ever drops to digital silence
    floor = lp(rng.standard_normal((2, N)), 1200) * 10 ** (-66 / 20)
    mix = mix + floor
    mix = lp(mix, 16000, 2)
    # master: normalise to -14 LUFS, limit to -1.3 dBTP, re-check
    for _ in range(3):
        g = 10 ** ((-14.0 - lufs(mix)) / 20)
        mix = limiter(mix * g)
    L, TP = lufs(mix), true_peak(mix)
    out = JOB / 'audio'
    wavfile.write(out / 'music.wav', SR, (music / max(1e-9, np.abs(music).max()) * .8).T.astype(np.float32))
    wavfile.write(out / 'sfx.wav', SR, (sfx / max(1e-9, np.abs(sfx).max()) * .8).T.astype(np.float32))
    wavfile.write(out / 'mix.wav', SR, mix.T.astype(np.float32))
    print(f'mix.wav  {DUR:.2f} s  {L:.2f} LUFS  true peak {TP:.2f} dBTP')


if __name__ == '__main__':
    main()
