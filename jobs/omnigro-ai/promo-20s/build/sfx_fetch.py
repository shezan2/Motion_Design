"""Fetch the sound files the SFX-only mix uses (audio data only) into build/sfx_lib/ (git-ignored).

    python3 build/sfx_fetch.py

Sources, each picked for a licence that covers a client's commercial video:
- GFXER/sfx-library (github.com/GFXER/sfx-library), only its Mixkit files (Mixkit Sound Effects Free License: free for
  commercial and client projects; the files themselves may not be redistributed, which is why sfx_lib/ is not committed)
  and its CC0 files.
- soundcn (github.com/kapishdima/soundcn), only Kenney sounds marked CC0 (each file carries license and author).
"""
import base64
import re
import sys
import urllib.request
from pathlib import Path

LIB = Path(__file__).resolve().parent / 'sfx_lib'
GFXER = 'https://raw.githubusercontent.com/GFXER/sfx-library/main/skills/sfx-library/sounds/'
SOUNDCN = 'https://raw.githubusercontent.com/kapishdima/soundcn/main/registry/soundcn/sounds/'

GFXER_FILES = {
    'ticks_typing/cc0_keyboard-typing-3s.flac': 'CC0',
    'ticks_typing/cc0_keyboard-typing-1s.flac': 'CC0',
    'ticks_typing/cc0_tick-soft.flac': 'CC0',
    'ticks_typing/cc0_clock-tick.flac': 'CC0',
    'clicks/mixkit__mouse-click-close-1113.flac': 'Mixkit Free License',
    'clicks/mixkit__cool-interface-click-tone-2568.flac': 'Mixkit Free License',
    'clicks/mixkit__modern-click-box-check-1120.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__fast-swipe-zoom-2627.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__fast-air-sweep-transition-168.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__cinematic-whoosh-fast-transition-1492.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__deep-air-woosh-2604.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__quick-air-woosh-2605.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__long-sweeping-air-swoosh-167.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__fast-small-sweep-transition-166.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__air-woosh-1489.flac': 'Mixkit Free License',
    'whooshes_swells/mixkit__explainer-video-pops-whoosh-light-pop-3005.flac': 'Mixkit Free License',
    'impacts/mixkit__drum-deep-impact-563.flac': 'Mixkit Free License',
    'impacts/mixkit__short-bass-hit-2299.flac': 'Mixkit Free License',
    'impacts/mixkit__air-in-a-hit-2161.flac': 'Mixkit Free License',
    'impacts/mixkit__cinematic-impact-echo-780.flac': 'Mixkit Free License',
    'impacts/mixkit__futuristic-bass-hit-2303.flac': 'Mixkit Free License',
    'impacts/mixkit__deep-cinematic-subtle-drum-impact-549.flac': 'Mixkit Free License',
    'risers/mixkit__short-space-stutter-intro-riser-1144.flac': 'Mixkit Free License',
    'risers/mixkit__cinematic-room-tone-3080.flac': 'Mixkit Free License',
    'reverses_rewinds/mixkit__reverse-cinematic-impact-trailer-784.flac': 'Mixkit Free License',
    'glitch/mixkit__data-scaner-2847.flac': 'Mixkit Free License',
}
KENNEY = ['drop-004', 'drop-002', 'drop-001', 'hover-tick', 'glass-002', 'tick-001', 'tick-002', 'tick-004', 'click-004']


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def main():
    LIB.mkdir(exist_ok=True)
    for rel in GFXER_FILES:
        out = LIB / Path(rel).name
        if not out.exists():
            out.write_bytes(get(GFXER + rel))
        print('ok', out.name)
    for n in KENNEY:
        out = LIB / f'kenney__{n}.mp3'
        if out.exists():
            print('ok', out.name); continue
        t = get(f'{SOUNDCN}{n}/{n}.ts').decode('utf-8', 'replace')
        lic = re.search(r'license:\s*"([^"]+)"', t)
        m = re.search(r'dataUri:\s*"data:audio/[a-z0-9]+;base64,([A-Za-z0-9+/=]+)"', t)
        if not m or not lic or lic.group(1).upper() != 'CC0':
            sys.exit(f'{n}: not CC0, refusing')
        out.write_bytes(base64.b64decode(m.group(1)))
        print('ok', out.name, '(CC0, Kenney)')


if __name__ == '__main__':
    main()
