# CriterAI intro film (20 s, 16:9)

A 20-second landscape brand and product film for [CriterAI](https://criter.ai), made with the Ozen motion design skill. Sound effects only.

- Watch: `out/criter-ai-intro-16x9-v1.mp4` (1080p30, main), `out/criter-ai-intro-16x9-60fps-v1.mp4`, `out/criter-ai-intro-16x9-4k-v1.mp4`
- Plan and decisions: [`STATE.md`](STATE.md). Delivery note (real vs illustrative, sound, look.py numbers): [`NOTE.md`](NOTE.md). Client message: [`CLIENT-MESSAGE.md`](CLIENT-MESSAGE.md)

## How it is built
One HTML composition (`build/index.html` + `build/film.js`) where every style is a pure function of time in `seek(t)`. Playwright renders it frame by frame and ffmpeg averages sub-frames into real motion blur.

```bash
cd build
node snap.mjs /tmp/stills 3.2 9.6 17.5                       # stills at chosen times (add --scale 2 for 4K)
node render.mjs --out ../out/master_1080p30.mp4 --fps 30 --sub 8 --scale 1 --crf 14   # main picture (~6 min)
node render.mjs --out ../out/master_1080p60.mp4 --fps 60 --sub 4 --scale 1 --crf 14
node render.mjs --out ../out/master_2160p60.mp4 --fps 60 --sub 4 --scale 2 --crf 16   # 4K
node export_cues.mjs ../audio/cues.json                      # sound cues come from film.js (one source of truth)
cd ../audio && python3 mix.py cues.json mix_final.wav        # SFX mix: -14 LUFS, true peak under -1.5 dBTP
cd .. && ffmpeg -i out/master_1080p30.mp4 -i audio/mix_final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -movflags +faststart out/criter-ai-intro-16x9-v1.mp4
```
Needs Node with Playwright and Chromium, ffmpeg, Python 3 with numpy, scipy and pyloudnorm.

## Where things live
| Path | What |
|---|---|
| `build/film.js` | timing table `T`, every beat as a function, camera, cursor, sound cues `CUES` |
| `build/index.html` | the stage, styles and brand tokens |
| `build/assets/` | logo split into four aligned layers (from their PNG), mark, mascot, grain |
| `build/fonts/` | Geist (their UI font) and Gelasio (match for their serif headline stack), both OFL |
| `audio/sfx/eleven/` | ElevenLabs Sound Effects v3 sources (10 prompts x 4 variations) |
| `audio/sfx/patches/`, `audio/sfx/synth/` | game-sfx synth patches and their renders (check chime motif, arpeggio, click, ticks, pop) |
| `audio/mix.py` | places each sound by its own peak or onset on the film's cues, masters to -14 LUFS |
| `brand/` | captured logo, mascots, site hero frame and copy |
