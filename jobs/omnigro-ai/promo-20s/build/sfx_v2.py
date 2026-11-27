"""OmniGro promo, v2 sound: SFX only (no music), real recorded / CC0 library sounds placed on the film's own frames.

    python3 build/sfx_fetch.py     # once: the sound files (git-ignored, see that file for sources and licences)
    python3 build/sfx_v2.py        # -> audio/sfx_v2_mix.wav, audio/sfx_v2_track_nobed.wav, audio/sfx_v2_report.json

Method, taken from the GitHub skills chosen for this job (their scripts were not run; their documented rules are
implemented here):
- Clipwing "real-sfx" (github.com/Clipwing/skills): sounds come from real libraries, never synthesized; every role is
  brought to its peak target (hit -4, whoosh -9, riser -12, click/pop -14 dBFS) and levelled to one perceived loudness
  within the role (max +/-6 dB, peak <= -1.5 dBFS) before the cue's own gain; a fast-building sound is placed by its
  ARRIVAL (first 20 ms within 6 dB of its loudest), a building sound (riser, swell) by its PEAK or its cut; antiphase
  stereo files play from their louder channel; an SFX-only film gets one steady, dark, real ambience bed at -54 dBFS
  (median of 250 ms windows, added after the master) so it never drops to digital silence; density is checked as
  gestures per 10 s (reference reels 6.9-15.1) with no long holes.
- GFXER "sfx-library" (github.com/GFXER/sfx-library): the pick table and proven sounds per visual event (soft tone
  click for settles, bloop for badges and pills, low-passed air whoosh peaking on a transition's midpoint, riser ending
  exactly on the cut, reverse impact peaking on the cut, a layered hit of sub + body + transient + air tail for the
  big moments, a silence pocket before the biggest hit), lead frames (clicks 1-2 f early, thumps 1 f), no sparkles or
  chimes on premium work (glints get a muted air texture), SFX mono and centred, only the bed in stereo.
- ElevenLabs "sound-effects" (github.com/elevenlabs/skills) was the generation fallback for a moment no library sound
  fits; every moment found a real or CC0 sound, so nothing is generated.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import minimum_filter1d
from scipy.signal import butter, lfilter, resample_poly, sosfilt

JOB = Path(__file__).resolve().parent.parent
LIB = JOB / 'build' / 'sfx_lib'
OUT = JOB / 'audio'
FPS, SR, DUR = 30, 48000, 20.0
N = int(round(DUR * SR))
ROLE_PEAK = {'hit': -4.0, 'whoosh': -9.0, 'riser': -12.0, 'click': -14.0, 'pop': -14.0, 'texture': -20.0}
BED_DBFS = -54.0
rng = np.random.default_rng(20261127)

# ----------------------------------------------------------------------------- the film's frames (from film.html)
TYPE_FRAMES = [6, 7, 9, 10, 11, 12, 15, 16, 17, 20, 21, 23, 24, 25, 26, 27, 30, 31]
PUSH = [167.5, 170.0, 173.75]                 # rows C, B, A dropping a slot as "Your Brand" rises through them
LAND = 178                                    # the climb lands (row settles 178-180)
PILL_BADGES = [258, 264, 270, 276, 282]       # each platform pill's #1 badge snaps in
CNT0, CNT1 = 337, 360                         # +0% -> +451%
LOGO = 499                                    # coral triangle lands


def counter_ticks():
    """frames where the displayed value changes, thinned to <= 14 ticks per second (real-sfx max rate)"""
    out, last, prev = [], -9, None
    for f in range(CNT0, CNT1):
        u = min(1, max(0, (f - CNT0) / (CNT1 - CNT0)))
        v = round(451 * (1 - (1 - u) ** 3))
        if v != prev and f - last >= 2:
            out.append(f); last = f
        prev = v
    return out


# ----------------------------------------------------------------------------- audio helpers
_cache = {}


def load(name):
    """mono float at 48 kHz; an antiphase stereo file plays from its louder channel (real-sfx mono rule)"""
    if name not in _cache:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(LIB / name), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)
        pl, pr = (x[0] ** 2).mean(), (x[1] ** 2).mean(); pm = (((x[0] + x[1]) / 2) ** 2).mean()
        loss = 10 * np.log10(((pl + pr) / 2 + 1e-20) / (pm + 1e-20))
        _cache[name] = (x[0] if pl >= pr else x[1]) if loss > 3 else (x[0] + x[1]) / 2
    return _cache[name].copy()


def sos(kind, f, o=2):
    return butter(o, f, btype=kind, fs=SR, output='sos')


def kweight(x):
    b1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]; a1 = [1.0, -1.69065929318241, 0.73248077421585]
    b2 = [1.0, -2.0, 1.0]; a2 = [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)


def env20(m):
    w, h = 960, 240
    n = max(1, 1 + (len(m) - w) // h)
    e = np.array([np.sqrt(np.mean(m[i * h:i * h + w] ** 2) + 1e-20) for i in range(n)])
    return 20 * np.log10(e), h


def perceived(m):
    """short-term perceived loudness: max K-weighted RMS over 100 ms windows (dB)"""
    y = kweight(m)
    w, h = 4800, 480
    if len(y) < w:
        y = np.pad(y, (0, w - len(y)))
    return max(10 * np.log10(np.mean(y[i:i + w] ** 2) + 1e-20) for i in range(0, len(y) - w + 1, h))


def prepare(c):
    m = load(c['file'])
    if c.get('slice'):
        a, ln = c['slice']; m = m[int(a * SR):int((a + ln) * SR)]
    if c.get('pitch'):
        r = 2 ** (c['pitch'] / 12)               # resample: higher pitch, shorter sound
        up, down = 1000, int(round(1000 * r))
        m = resample_poly(m, up, down)
    if c.get('hp'):
        m = sosfilt(sos('high', c['hp']), m)
    if c.get('lp'):
        m = sosfilt(sos('low', c['lp']), m)
    fi = int(c.get('fade_in_ms', 2.5) * SR / 1000); fo = int(c.get('fade_out_ms', 12 if c.get('slice') else 4) * SR / 1000)
    m[:fi] *= np.linspace(0, 1, fi) if fi else 1
    if fo:
        m[-fo:] *= np.linspace(1, 0, fo)
    d, h = env20(m)
    ip = int(np.argmax(d))
    anchor = c.get('anchor', 'arrival')
    if anchor == 'arrival':
        off = int(np.nonzero(d >= d[ip] - 6)[0][0]) * h / SR
    elif anchor == 'peak':
        off = (ip * h + 480) / SR
    elif anchor == 'end':
        off = len(m) / SR
    else:
        off = 0.0
    aud = np.nonzero(d > d[ip] - 20)[0]
    span = ((aud[0] * h) / SR, (aud[-1] * h + 960) / SR)
    return m, off, span


# ----------------------------------------------------------------------------- the cue sheet
def cue_sheet():
    C = []
    add = lambda **k: C.append(k)
    # S1 the ask: real keystrokes on each typing burst (sliced from a CC0 keyboard recording), the send press
    strokes = keystrokes()
    for i, f in enumerate(TYPE_FRAMES):
        s = strokes[(i * 3) % len(strokes)]
        add(t=f, lead=1, role='click', gain=-3 + rng.uniform(-1.5, 1.0), label='key', **s)
    add(t=50, lead=0, role='click', gain=-9, label='cursor parks on send (hover)', file='kenney__hover-tick.mp3')
    add(t=58, lead=1, role='click', gain=-4, label='send press', file='mixkit__mouse-click-close-1113.flac', slice=[0.0, 0.09])
    # S2 the answer: the prompt lifts (swipe), the AI answer streams in (data scan texture), rows land (soft ticks)
    add(t=65, anchor='peak', role='whoosh', gain=-7, label='prompt lifts', file='mixkit__fast-swipe-zoom-2627.flac', lp=6000)
    add(t=66, anchor='start', role='texture', gain=-1, label='AI answer streams in', file='mixkit__data-scaner-2847.flac',
        slice=[0.30, 0.95], fade_in_ms=40, fade_out_ms=260, lp=9000)
    for f, fn in zip([84, 91, 98], ['kenney__hover-tick.mp3', 'mixkit__cool-interface-click-tone-2568.flac', 'kenney__glass-002.mp3']):
        add(t=f, lead=1, role='click', gain=-3, label='row lands', file=fn)
    # "Where's your brand?": a swelling sub drum + an airy hit (the question gets weight)
    add(t=119, anchor='peak', role='hit', gain=-9, label='question swell', file='mixkit__deep-cinematic-subtle-drum-impact-549.flac',
        slice=[1.30, 1.30], fade_in_ms=60, fade_out_ms=450)
    add(t=118, lead=1, role='hit', gain=-11, label='question air hit', file='mixkit__air-in-a-hit-2161.flac', hp=150)
    # S3 the lift: the line leaves, a riser builds and CUTS 2 frames before the landing (silence pocket),
    # a building whoosh peaks into the landing, rows drop a slot (small ticks), layered landing hit, #1 bloop, check
    add(t=160, anchor='peak', role='whoosh', gain=-8, label='line leaves', file='mixkit__fast-air-sweep-transition-168.flac', lp=5000)
    # silence pocket (GFXER): riser and rising whoosh both cut by f173, nothing sounds f173-f178, then the hit
    add(t=LAND - 5, anchor='end', role='riser', gain=0, label='riser into the lift', file='mixkit__short-space-stutter-intro-riser-1144.flac',
        slice=[5.62, 0.83], fade_in_ms=160, fade_out_ms=8)
    add(t=LAND - 8, anchor='peak', role='whoosh', gain=-3, label='brand rises', file='mixkit__cinematic-whoosh-fast-transition-1492.flac',
        slice=[0.35, 0.78], fade_in_ms=80, fade_out_ms=40)
    add(t=LAND, lead=1, role='hit', gain=-1, label='landing: body', file='mixkit__drum-deep-impact-563.flac', hp=70)
    add(t=LAND, lead=1, role='hit', gain=-4, label='landing: sub', file='mixkit__short-bass-hit-2299.flac', fade_out_ms=120)
    add(t=LAND, lead=1, role='hit', gain=-9, label='landing: transient', file='mixkit__air-in-a-hit-2161.flac', hp=300)
    add(t=183, lead=0, role='pop', gain=2, pitch=-2, label='#1 badge (the spring)', file='kenney__drop-004.mp3')
    add(t=189, lead=0, role='click', gain=-1, label='check mark', file='mixkit__modern-click-box-check-1120.flac')
    # S4 proof: page scrolls (deep air whoosh peaking mid-scroll), the headline resolves, each platform's #1 bloops
    # (the badge motif, rising a semitone each), the pills' hover-lift wave gets three faint ticks
    add(t=242, anchor='peak', role='whoosh', gain=0, label='scroll to proof', file='mixkit__deep-air-woosh-2604.flac', lp=4500)
    add(t=259, lead=1, role='click', gain=-6, label='headline resolves', file='kenney__hover-tick.mp3')
    for i, (f, fn) in enumerate(zip(PILL_BADGES, ['kenney__drop-004.mp3', 'kenney__drop-002.mp3', 'kenney__drop-004.mp3',
                                                  'kenney__drop-001.mp3', 'kenney__drop-004.mp3'])):
        add(t=f, lead=0, role='pop', gain=-3, pitch=i, label=f'platform #1 ({i + 1}/5)', file=fn)
    for f, fn in zip([297, 307, 317], ['kenney__glass-002.mp3', 'kenney__tick-004.mp3', 'kenney__hover-tick.mp3']):
        add(t=f, lead=0, role='click', gain=-10, label='pill lift', file=fn)
    # S5 the number: lighter scroll, a tick train that follows the count and ends on a settle click + air hit
    add(t=335, anchor='peak', role='whoosh', gain=-3, label='scroll to the number', file='mixkit__quick-air-woosh-2605.flac', lp=5000)
    ticks = counter_ticks()
    for i, f in enumerate(ticks):
        u = i / max(1, len(ticks) - 1)
        add(t=f, lead=0, role='click', gain=-8 + 3 * u, pitch=round(3 * u, 2), label='counter tick',
            file=['cc0_tick-soft.flac', 'kenney__tick-002.mp3', 'kenney__tick-001.mp3'][i % 3])
    add(t=CNT1, lead=1, role='click', gain=0, label='+451% lands', file='mixkit__cool-interface-click-tone-2568.flac')
    add(t=CNT1, lead=1, role='hit', gain=-12, label='+451% weight', file='mixkit__air-in-a-hit-2161.flac', hp=200)
    add(t=376, lead=0, role='click', gain=-8, label='trend line completes', file='kenney__glass-002.mp3')
    # S6 payoff: big scroll back to navy, the H1 lands in two lines; line 2 answers the question with the same swell
    add(t=420, anchor='peak', role='whoosh', gain=-3, label='scroll to the payoff', file='mixkit__long-sweeping-air-swoosh-167.flac', lp=4500)
    add(t=420, lead=1, role='hit', gain=-13, label='payoff line 1', file='mixkit__air-in-a-hit-2161.flac', hp=200)
    add(t=435, anchor='peak', role='hit', gain=-10, label='payoff line 2: swell', file='mixkit__deep-cinematic-subtle-drum-impact-549.flac',
        slice=[1.20, 2.10], fade_in_ms=60, fade_out_ms=300)
    add(t=434, lead=1, role='hit', gain=-12, label='payoff line 2: body', file='mixkit__drum-deep-impact-563.flac', hp=90)
    # S7 the mark: reverse impact swells and CUTS on the logo frame, a layered logo hit with a long air tail,
    # a soft swipe as the wordmark slides out, a tick on the CTA line, a light pop on the button, muted air on the sweep
    add(t=LOGO, anchor='end', role='riser', gain=2, label='letters converge (reverse)', file='mixkit__reverse-cinematic-impact-trailer-784.flac',
        slice=[8.95, 1.07], fade_in_ms=250, fade_out_ms=5, lp=8000)
    add(t=LOGO, lead=0, role='hit', gain=0, label='logo: body + air tail', file='mixkit__cinematic-impact-echo-780.flac', slice=[0.0, 2.9],
        fade_out_ms=1600)
    add(t=LOGO, lead=0, role='hit', gain=-4, label='logo: sub', file='mixkit__futuristic-bass-hit-2303.flac')
    add(t=LOGO, lead=0, role='hit', gain=-10, label='logo: transient', file='mixkit__air-in-a-hit-2161.flac', hp=300)
    add(t=528, anchor='peak', role='whoosh', gain=-9, label='wordmark slides out', file='mixkit__fast-small-sweep-transition-166.flac', lp=4000)
    add(t=553, lead=1, role='click', gain=-4, label='CTA line', file='kenney__hover-tick.mp3')
    add(t=561, lead=1, role='pop', gain=-2, label='CTA button', file='mixkit__explainer-video-pops-whoosh-light-pop-3005.flac')
    add(t=585, anchor='peak', role='whoosh', gain=-14, label='light sweep (muted air)', file='mixkit__air-woosh-1489.flac', lp=1500)
    return C


def keystrokes():
    """single key strokes cut from the CC0 keyboard recordings: onsets 60 ms apart, 110 ms long, similar loudness"""
    out = []
    for fn in ['cc0_keyboard-typing-3s.flac', 'cc0_keyboard-typing-1s.flac']:
        m = load(fn)
        h = 240; e = np.array([np.sqrt(np.mean(m[i:i + h] ** 2) + 1e-20) for i in range(0, len(m) - h, h)])
        d = 20 * np.log10(e)
        thr = np.percentile(d, 75)
        last = -999
        for i in range(1, len(d) - 1):
            if d[i] > thr and d[i] >= d[i - 1] and d[i] >= d[i + 1] and d[i] - d[max(0, i - 8):i].min() > 9 and (i - last) * h > 0.06 * SR:
                out.append({'file': fn, 'slice': [max(0, i * h / SR - 0.006), 0.11], 'loud': d[i]}); last = i
    med = np.median([o['loud'] for o in out])
    keep = [o for o in out if abs(o['loud'] - med) < 4][:12]
    for o in keep:
        o.pop('loud'); o['fade_out_ms'] = 40
    return keep


# ----------------------------------------------------------------------------- mix, master, measure
def lufs(st):
    y = kweight(st)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    ms = np.array([(y[:, i:i + blk] ** 2).mean(axis=1).sum() for i in range(0, st.shape[1] - blk + 1, hop)])
    lk = -0.691 + 10 * np.log10(ms + 1e-12)
    g1 = ms[lk > -70]
    if not len(g1):
        return -99.0
    rel = -0.691 + 10 * np.log10(g1.mean()) - 10
    return -0.691 + 10 * np.log10(ms[(lk > -70) & (lk > rel)].mean())


def true_peak(st):
    return 20 * np.log10(np.abs(resample_poly(st, 4, 1, axis=1)).max() + 1e-12)


def limiter(st, ceiling_db=-1.3, look=0.0015, rel=0.06):
    c = 10 ** (ceiling_db / 20)
    peak = np.abs(resample_poly(st, 4, 1, axis=1)).max(axis=0).reshape(-1, 4).max(axis=1)[:st.shape[1]]
    peak = np.pad(peak, (0, st.shape[1] - len(peak)), constant_values=0)
    need = np.minimum(1, c / np.maximum(peak, 1e-9))
    g = minimum_filter1d(need, size=2 * int(look * SR) + 1)
    out = np.empty_like(g); cur = 1.0; a = np.exp(-1 / (rel * SR))
    for i in range(len(g)):
        cur = g[i] if g[i] < cur else a * cur + (1 - a) * g[i]
        out[i] = cur
    return st * out, 20 * np.log10(out.min())


def compressor(st, thr_db=-24.0, ratio=3.0, att=0.004, rel=0.12):
    """feed-forward RMS bus compressor (5 ms detector): tames transient peaks so they stop setting the loudness"""
    det = np.sqrt(np.convolve((st ** 2).mean(axis=0), np.ones(240) / 240, mode='same') + 1e-20)
    lvl = 20 * np.log10(det)
    over = np.maximum(0, lvl - thr_db)
    want = -over * (1 - 1 / ratio)
    g = np.empty_like(want); cur = 0.0
    aa, ar = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    for i in range(len(want)):
        cur = aa * cur + (1 - aa) * want[i] if want[i] < cur else ar * cur + (1 - ar) * want[i]
        g[i] = cur
    return st * 10 ** (g / 20)


def win_db(x, w=0.25):
    n = int(w * SR)
    return np.array([10 * np.log10(np.mean(x[:, i:i + n] ** 2) + 1e-20) for i in range(0, x.shape[1] - n + 1, n)])


def main():
    cues = cue_sheet()
    prepared = []
    for c in cues:
        m, off, span = prepare(c)
        pk = 20 * np.log10(np.abs(m).max() + 1e-12)
        m = m * 10 ** ((ROLE_PEAK[c['role']] - pk) / 20)      # 1. role peak target
        prepared.append([c, m, off, span, perceived(m)])
    # 2. one perceived loudness per role (median, +/-6 dB, peak <= -1.5 dBFS)
    for role in ROLE_PEAK:
        group = [p for p in prepared if p[0]['role'] == role]
        if not group:
            continue
        med = float(np.median([p[4] for p in group]))
        for p in group:
            adj = float(np.clip(med - p[4], -6, 6))
            headroom = -1.5 - 20 * np.log10(np.abs(p[1]).max() + 1e-12)
            adj = min(adj, headroom)
            p[1] = p[1] * 10 ** (adj / 20); p.append(adj)
    bus = np.zeros(N)
    report, spans, placed = [], [], []
    for c, m, off, span, loud, adj in prepared:
        m = m * 10 ** (c.get('gain', 0) / 20)                 # 3. the cue's own gain
        t = (c['t'] - c.get('lead', 0)) / FPS - off
        i = int(round(t * SR))
        a, b = max(0, i), min(N, i + len(m))
        if b > a:
            bus[a:b] += m[a - i:b - i]
            at = t + off - (0.18 if c.get('anchor') == 'end' else 0.0)     # an end-anchored swell is judged just before its cut
            placed.append((c['label'], a, b, m[a - i:b - i].copy(), int(round(at * SR))))
        spans.append((t + span[0], t + span[1], c['label']))
        report.append({'label': c['label'], 'frame': c['t'], 'file': c['file'], 'slice': c.get('slice'), 'role': c['role'],
                       'anchor': c.get('anchor', 'arrival'), 'placed_at_s': round(t, 4), 'event_at_s': round(c['t'] / FPS, 4),
                       'level_adj_db': round(adj, 2), 'gain_db': round(float(c.get('gain', 0)), 2), 'pitch': c.get('pitch', 0),
                       'peak_after_db': round(20 * np.log10(np.abs(m).max() + 1e-12), 2)})
    masked = []
    for lab, a, b, sig, at in placed:
        w0, w1 = max(0, at - int(0.05 * SR)), min(N, at + int(0.15 * SR))
        mine = np.zeros(N); mine[a:b] = sig
        rest = bus[w0:w1] - mine[w0:w1]
        cue_pk = 20 * np.log10(np.abs(mine[w0:w1]).max() + 1e-12)
        rest_rms = 20 * np.log10(np.sqrt(np.mean(rest ** 2)) + 1e-12)
        if cue_pk - rest_rms < 0:
            masked.append((lab, round(at / SR, 2), round(cue_pk - rest_rms, 1)))
    # gentle fade of the SFX tails over the last 0.5 s (the bed carries on to the last frame)
    tt = np.arange(N) / SR
    bus *= np.interp(tt, [0, DUR - 0.5, DUR], [1, 1, 0.25])
    st = np.vstack([bus, bus])                                # SFX mono and centred
    # master: -14 LUFS, true peak <= -1.3; if the limiter would bite more than 4 dB, accept a lower loudness (honest)
    st = compressor(st)
    target = -14.0
    while True:
        g = 10 ** ((target - lufs(st)) / 20)
        lim, gr = limiter(st * g)
        if gr > -4.0 or target <= -15.5:
            break
        target -= 0.25                                         # a sparse film is not forced to -14 (real-sfx)
    sfx_master = lim
    # bed: one steady, dark, real room tone at -54 dBFS (median of 250 ms windows), added after the master, stereo
    bed = None
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(LIB / 'mixkit__cinematic-room-tone-3080.flac'), '-ac', '2', '-ar', str(SR),
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    bed = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)[:, int(12.0 * SR):int(12.0 * SR) + N]
    bed = bed * 10 ** ((BED_DBFS - np.median(win_db(bed))) / 20)
    bed[:, :int(0.08 * SR)] *= np.linspace(0, 1, int(0.08 * SR))
    mix = sfx_master + bed
    mix, gr2 = limiter(mix, -1.2)
    OUT.mkdir(exist_ok=True)
    wavfile.write(OUT / 'sfx_v2_mix.wav', SR, mix.T.astype(np.float32))
    wavfile.write(OUT / 'sfx_v2_track_nobed.wav', SR, sfx_master.T.astype(np.float32))
    # ---- self-critique numbers (the real-sfx definitions)
    L, TP = lufs(mix), true_peak(mix)
    L150 = lufs(sosfilt(sos('high', 150), mix, axis=-1))
    w = win_db(mix)
    floor = float(np.percentile(w, 10) - w.max())
    silent = float((w < -70).mean() * 100)
    ev = sorted(spans)
    gestures, cur = [], list(ev[0][:2])
    for s, e, _ in ev[1:]:
        if s - cur[1] < 0.25:
            cur[1] = max(cur[1], e)
        else:
            gestures.append(tuple(cur)); cur = [s, e]
    gestures.append(tuple(cur))
    pauses = [gestures[i + 1][0] - gestures[i][1] for i in range(len(gestures) - 1)]
    mono = 10 * np.log10(((mix[0] ** 2).mean() + (mix[1] ** 2).mean()) / 2 / ((((mix[0] + mix[1]) / 2) ** 2).mean() + 1e-20))
    per10 = [sum(1 for g in gestures if a <= g[0] < a + 10) for a in (0, 10)]
    stats = {'lufs': round(L, 2), 'true_peak_dbtp': round(TP, 2), 'lufs_hp150': round(L150, 2), 'loudness_target_used': round(target, 2),
             'limiter_max_gr_db': round(gr, 2), 'gestures_total': len(gestures), 'gestures_per_10s': per10,
             'pause_median_s': round(float(np.median(pauses)), 2), 'pause_p90_s': round(float(np.percentile(pauses, 90)), 2),
             'longest_hole_s': round(float(max(pauses)), 2), 'quietest_tenth_vs_loudest_db': round(floor, 1),
             'digital_silence_pct': round(silent, 1), 'mono_sum_loss_db': round(float(mono), 2), 'cues': len(cues)}
    json.dump({'stats': stats, 'cues': report}, open(OUT / 'sfx_v2_report.json', 'w'), indent=1)
    print(json.dumps(stats, indent=1))
    print('possibly masked (cue peak below the RMS of everything else around it):', masked or 'none')
    stats['possibly_masked'] = masked
    json.dump({'stats': stats, 'cues': report}, open(OUT / 'sfx_v2_report.json', 'w'), indent=1)
    print('longest holes:', sorted([(round(p, 2), round(gestures[i][1], 2)) for i, p in enumerate(pauses)], reverse=True)[:4])


if __name__ == '__main__':
    main()
