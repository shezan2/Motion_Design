"""OmniGro promo, v3: the ElevenLabs voiceover take cut into the SFX-only mix (voiced cut, film.html?cut=vo).

    python3 build/vo_v3.py    # needs build/sfx_lib (python3 build/sfx_fetch.py) and audio/vo/omnigro-vo-take1.mp3
    -> audio/vo_v3_mix.wav, audio/vo_v3_voice.wav, audio/vo_v3_sfx_ducked.wav, audio/vo_v3_report.json,
       out/omnigro-promo-16x9-v3-vo.srt

Follows the Ozen skill's "placing the take" (references/sound.md 4.4) plus the voice rules of the SFX skills used for v2:
1. split the take into phrases by silence (gaps of 0.15 s or more at -48 dBFS): 9 phrases = the 7 script lines, with
   the natural pauses after "Our latest pilot:" and "report:";
2. level-match every line to one speech loudness;
3. place each line by its first syllable, just after its words are on screen; no overlaps; no word under the landing
   hit (5.93 s) or the logo hit (16.63 s);
4. dip the SFX under speech (real-sfx voice-safe, about -9 dB, deeper where a line's margin is short) so the voice sits
   at least 8 dB above everything else while it speaks (GFXER: no big hit under a word); the bed stays at -54 dBFS;
5. master to -14 LUFS with a -1.5 dBTP ceiling, then limit; captions as .srt.
Fit edit: the last line "Your free AI visibility report: omni-gro A I dot com" runs 4.3 s, which does not fit between the
logo hit and the end, so only "omni-gro A I dot com" is used; the CTA line stays on screen as text.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import sosfilt

JOB = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('sfx_v2', JOB / 'build' / 'sfx_v2.py')
v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
SR, FPS, N, DUR = v2.SR, v2.FPS, v2.N, v2.DUR
TAKE = JOB / 'audio' / 'vo' / 'omnigro-vo-take1.mp3'

# end-card cues move with the voiced cut's picture (must match film.html ?cut=vo)
RETIME = {'wordmark slides out': 524, 'CTA line': 528, 'CTA button': 534, 'light sweep (muted air)': 575}
# script lines: (caption, take phrases used, first syllable at (s), tempo, gap between joined phrases (s))
LINES = [
    ("Your customers ask AI.", [0], 0.15, 1.0, 0),
    ("It names your competitors.", [1], 2.25, 1.0, 0),
    ("Where's your brand?", [2], 4.10, 1.0, 0),
    ("OmniGro puts it on top.", [3], 6.15, 1.0, 0),
    ("Our latest pilot: number one\non every major AI platform.", [4, 5], 8.25, 1.04, 0.12),
    ("Get your brand recommended by AI.", [6], 14.10, 1.0, 0),
    ("omnigroai.com", [8], 18.00, 1.0, 0),
]
KEEP_CLEAR = [(5.77, 6.06, 'landing hit'), (16.45, 16.95, 'logo hit')]


def decode(path, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-af', f'aresample={sr}:resampler=soxr', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def stretch(x, tempo):
    """formant-preserving time stretch (rubberband), pitch unchanged"""
    if abs(tempo - 1) < 1e-3:
        return x
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-af', f'rubberband=tempo={tempo}:formant=preserved:pitchq=quality', '-f', 'f32le', '-'],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).astype(np.float64)


def phrases(x):
    hop = int(0.01 * SR)
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-20) for i in range(0, len(x) - hop, hop)])
    on = 20 * np.log10(env) > -48
    segs, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            segs.append([i * hop / SR, j * hop / SR]); i = j
        else:
            i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 0.15:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [s for s in merged if s[1] - s[0] > 0.1]


def lufs_mono(x):
    return v2.lufs(np.vstack([x, x])) - 3.0103      # a mono signal measured as one channel


def build_sfx_bus():
    """the v2 cue sheet with the end card retimed, levelled exactly as v2 does, compressed (pre-master)"""
    cues = v2.cue_sheet()
    for c in cues:
        if c['label'] in RETIME:
            c['t'] = RETIME[c['label']]
    prepared = []
    for c in cues:
        m, off, span = v2.prepare(c)
        pk = 20 * np.log10(np.abs(m).max() + 1e-12)
        m = m * 10 ** ((v2.ROLE_PEAK[c['role']] - pk) / 20)
        prepared.append([c, m, off, span, v2.perceived(m)])
    for role in v2.ROLE_PEAK:
        group = [p for p in prepared if p[0]['role'] == role]
        if not group:
            continue
        med = float(np.median([p[4] for p in group]))
        for p in group:
            adj = min(float(np.clip(med - p[4], -6, 6)), -1.5 - 20 * np.log10(np.abs(p[1]).max() + 1e-12))
            p[1] = p[1] * 10 ** (adj / 20)
    bus = np.zeros(N)
    for c, m, off, span, loud in prepared:
        m = m * 10 ** (c.get('gain', 0) / 20)
        i = int(round(((c['t'] - c.get('lead', 0)) / FPS - off) * SR))
        a, b = max(0, i), min(N, i + len(m))
        if b > a:
            bus[a:b] += m[a - i:b - i]
    tt = np.arange(N) / SR
    bus *= np.interp(tt, [0, DUR - 0.5, DUR], [1, 1, 0.25])
    return v2.compressor(np.vstack([bus, bus]))


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def main():
    take = decode(TAKE)
    ph = phrases(take)
    assert len(ph) == 9, f'expected 9 phrases in the take, found {len(ph)}: {ph}'
    # ---- 1-2. cut the lines, level-match them
    lines = []
    for cap, idx, at, tempo, gap in LINES:
        parts = []
        for k in idx:
            s, e = ph[k]
            a = max(0, int((s - 0.03) * SR)); b = min(len(take), int((e + 0.08) * SR))
            seg = take[a:b].copy()
            fi, fo = int(0.008 * SR), int(0.04 * SR)
            seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
            parts.append(seg)
            if gap and k != idx[-1]:
                parts.append(np.zeros(int(gap * SR)))
        clip = stretch(np.concatenate(parts), tempo)
        clip = sosfilt(v2.sos('high', 80), clip)
        lines.append({'caption': cap, 'clip': clip, 'at': at, 'tempo': tempo, 'phrases': [ph[k] for k in idx]})
    target = float(np.median([lufs_mono(l['clip']) for l in lines]))
    for l in lines:
        l['level_db'] = round(target - lufs_mono(l['clip']), 2)
        l['clip'] *= 10 ** (l['level_db'] / 20)
    # ---- 3. place by the first syllable; check overlaps and the two hits
    voice = np.zeros(N)
    spans = []
    for l in lines:
        c = l['clip']; hop = 240
        env = 20 * np.log10(np.array([np.sqrt(np.mean(c[i:i + hop] ** 2) + 1e-20) for i in range(0, len(c) - hop, hop)]))
        loud = np.nonzero(env > env.max() - 30)[0]
        onset, end = loud[0] * hop / SR, (loud[-1] + 1) * hop / SR
        start = l['at'] - onset
        i = int(round(start * SR)); a, b = max(0, i), min(N, i + len(c))
        assert b - a == len(c), f"line does not fit inside the film: {l['caption']!r}"
        voice[a:b] += c[a - i:b - i]
        l['speech'] = (round(l['at'], 3), round(start + end, 3))
        spans.append(l['speech'])
    for (s0, e0), (s1, e1) in zip(spans, spans[1:]):
        assert s1 - e0 >= 0.18, f'lines too close: {e0} -> {s1}'
    for s, e in spans:
        for k0, k1, name in KEEP_CLEAR:
            assert e <= k0 or s >= k1, f'a word sits under the {name}'
    # ---- 4. SFX dipped under speech
    sfx = build_sfx_bus()
    tt = np.arange(N) / SR

    def duck_curve(depths):
        g = np.zeros(N)
        for (s, e), d in zip(spans, depths):
            g = np.minimum(g, np.interp(tt, [s - 0.06, s - 0.02, e + 0.05, e + 0.30], [0, -d, -d, 0], left=0, right=0))
        return 10 ** (g / 20)

    depths = [9.0] * len(spans)
    vg = 1.0
    for _ in range(6):
        sfx_d = sfx * duck_curve(depths)
        margins = []
        for (s, e) in spans:
            a, b = int(s * SR), int(e * SR)
            lv = lufs_mono(voice[a:b] * vg) if b - a > int(0.4 * SR) else 20 * np.log10(np.sqrt(np.mean((voice[a:b] * vg) ** 2)) + 1e-12)
            ls = v2.lufs(sfx_d[:, a:b]) if b - a > int(0.4 * SR) else 20 * np.log10(np.sqrt(np.mean(sfx_d[:, a:b] ** 2)) + 1e-12)
            margins.append(lv - ls)
        short = [k for k, m in enumerate(margins) if m < 9.0]
        if not short:
            break
        for k in short:                          # deepen the dip on that line first (to 15 dB), then raise the voice
            if depths[k] < 15:
                depths[k] = min(15.0, depths[k] + (9.0 - margins[k]))
            else:
                vg *= 10 ** ((9.0 - margins[k]) / 20)
    # ---- 5. master: voice-led, -14 LUFS, -1.5 dBTP; bed added after at -54 dBFS
    mix = sfx_d + np.vstack([voice * vg, voice * vg])
    target_l = -14.0
    while True:
        g = 10 ** ((target_l - v2.lufs(mix)) / 20)
        lim, gr = v2.limiter(mix * g, -1.6)
        if gr > -4.0 or target_l <= -15.5:
            break
        target_l -= 0.25
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(v2.LIB / 'mixkit__cinematic-room-tone-3080.flac'), '-ac', '2', '-ar', str(SR),
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    bed = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)[:, int(12.0 * SR):int(12.0 * SR) + N]
    bed = bed * 10 ** ((v2.BED_DBFS - np.median(v2.win_db(bed))) / 20)
    bed[:, :int(0.08 * SR)] *= np.linspace(0, 1, int(0.08 * SR))
    final, gr2 = v2.limiter(lim + bed, -1.5)
    out = JOB / 'audio'
    wavfile.write(out / 'vo_v3_mix.wav', SR, final.T.astype(np.float32))
    wavfile.write(out / 'vo_v3_voice.wav', SR, (voice * vg * g).astype(np.float32))
    wavfile.write(out / 'vo_v3_sfx_ducked.wav', SR, (sfx_d * g).T.astype(np.float32))
    # captions
    srt = []
    for k, l in enumerate(lines):
        s, e = l['speech']
        nxt = lines[k + 1]['speech'][0] if k + 1 < len(lines) else DUR
        srt.append(f"{k + 1}\n{srt_time(s)} --> {srt_time(min(e + 0.25, nxt - 0.05, DUR))}\n{l['caption']}\n")
    (JOB / 'out' / 'omnigro-promo-16x9-v3-vo.srt').write_text('\n'.join(srt), encoding='utf-8')
    # report
    rep = {'take_phrases_s': [[round(a, 3), round(b, 3)] for a, b in ph], 'line_target_lufs': round(target, 2),
           'lines': [{'caption': l['caption'].replace('\n', ' '), 'speech_s': l['speech'], 'tempo': l['tempo'], 'level_db': l['level_db'],
                      'sfx_dip_db': round(d, 1), 'voice_over_sfx_db': round(m, 1)} for l, d, m in zip(lines, depths, margins)],
           'voice_gain_db': round(20 * np.log10(vg), 2), 'master_target_lufs': target_l, 'limiter_max_gr_db': round(gr, 2),
           'lufs': round(v2.lufs(final), 2), 'true_peak_dbtp': round(v2.true_peak(final), 2),
           'lufs_hp150': round(v2.lufs(sosfilt(v2.sos('high', 150), final, axis=-1)), 2)}
    json.dump(rep, open(out / 'vo_v3_report.json', 'w'), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == '__main__':
    main()
