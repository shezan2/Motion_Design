# Outtakes launch film — Lottie edition (text-to-lottie)

The Outtakes launch film rebuilt as **Lottie animations**, using
[diffusionstudio/lottie](https://github.com/diffusionstudio/lottie) (text-to-lottie): its skill, its
Skia Skottie player, and its authoring rules.

- **Formats:** two cuts from one timeline, 30 fps, 56 s each:
  - portrait 1080×1920 (`public/projects/outtakes-launch`) for Reels, TikTok and Shorts
  - landscape 1920×1080 (`public/projects/outtakes-launch-16x9`) for YouTube, the website and X
- **Sound:** sound effects only, no voiceover (add your new VO on top).
- **Branding:** the new "Outtakes Dark" site.

## The film: 10 Lottie scenes

| # | Scene | Frames | What it shows |
|---|---|---|---|
| 1 | Hook — burst mode | 180 | Ten of the collective's photos fire on shutter clicks, then the shot lands. "YOU GOT / THE SHOT." |
| 2 | Problem — the DMs | 240 | One DM thread: "how much for saturday's match?" → "$150 for the full game" → "can do $30?" (lowball) → "game cancelled, no need to pay ya" (cancellation) → "just following up on the invoice :)" → Seen. "SOUND / FAMILIAR?" |
| 3 | Reveal | 135 | OUTTAKES crashes in on the hit. "MADE BY PHOTOGRAPHERS, FOR PHOTOGRAPHERS." |
| 4 | **Now clients chase you** | 165 | A client searches "football photographer", your profile is in the results, then booking requests stack up: sports club season coverage, brand shoot, final. *More clients, bigger clients, one central place where they search.* |
| 5 | **Your portfolio, organised** | 135 | Profile with sport tags, filter chips (tapped) and a portfolio grid. *Proper organised portfolio.* |
| 6 | **Booked at your rate** | 150 | The lowball DM gets struck out and thrown away. A systemised booking request (date, venue, coverage, your rate) is tapped and Booked. *Systemised booking format, fewer lowball DMs.* |
| 7 | **Invoices, done for you** | 135 | A proper invoice builds itself (billed to, items, total), then is stamped Sent. *Invoice generation for big clients.* |
| 8 | **Paid. Even if they cancel.** | 150 | Payment secured. The client cancels, and the cancellation fee is paid to you. *Secure payments.* |
| 9 | **Free exposure, built in** | 150 | Shot of the Week feature, Featured chip, nominees strip. *Free built-in exposure and marketing.* |
| 10 | CTA | 240 | "SIGN UP FREE." → "SET UP YOUR PROFILE FROM 16 NOV." → **20.11** crash → "WE GO LIVE · 5PM SGT" → button tapped → wordmark on the brand gradient. |

**Seams:** every chapter ends with the camera-shutter curtain starting to close (a cut on motion) and the next chapter opens with it finishing. This is an occlusion wipe from the skill's transition grammar.

**Feature beats:** all six use one repeated layout, as the chapterization guide recommends for lists:
- the same headline block (white line plus green line)
- one support line
- one proof object

**Camera:** every scene has one slow camera push, calmer than the objects.

**What's illustrative:**
- The DM thread.
- The sample booking, invoice and payment values ($150, Jalan Besar Stadium, Sat 22 Nov, Sports club).
- "YOUR NAME".
- The UI, which is rebuilt in Lottie from the website PDF design, not captured from the live site.

No real photographer's name is attached to any photo.

## Landscape layout

The 16:9 cut is laid out for the wide frame; it isn't the portrait one cropped.

- **Feature beats:** the headline block sits in a left column, centred vertically. The proof (search, profile, booking form, invoice, payment cards, Shot of the Week) sits in a right column at x 1000–1800. That column is almost the same size as the portrait proof area, so the same UI pieces are reused.
- **Hook, CTA and DM beats:** the hook and the CTA set their two-colour lines on one line ("YOU GOT **THE SHOT.**", "SIGN UP **FREE.**", "SOUND **FAMILIAR?**"). The DM thread is centred.
- **Timing and sound:** identical in both formats, so they share one sound-effects track.

`OT_FORMAT=landscape` switches `tools/build_film.py` and `tools/film_parts.py` to the 16:9 layout. The portrait output is unchanged by this switch; the portrait JSON was verified numerically identical.

## Edit it in the player

```bash
npm install
npm run dev        # http://localhost:3030/outtakes-launch/scene-1  (16:9: /outtakes-launch-16x9/scene-1)
```

Every scene exposes **slots** in the player's Properties panel. You can retype these without touching code:
- headlines and the background colour
- in scene 10: the profiles-open date (`16 NOV.`), the live date (`20.11`), the go-live line (`WE GO LIVE · 5PM SGT`), the button label and the end brand

`?frame=N` pins a frame.

Each `public/projects/outtakes-launch/scene-N/lottie.json` is a standard Lottie file. It works in lottie-web, iOS, Android, Flutter, and can be imported into After Effects.

## Rebuild / export the MP4

```bash
pip install fonttools brotli scipy pillow numpy
python3 tools/make_fonts.py <archivo woff2 folder> brand/fonts   # one-off: static Archivo cuts for Skottie
bash tools/export.sh                                             # portrait:  build -> SFX -> render -> out/outtakes-launch-lottie-9x16.mp4
OT_FORMAT=landscape bash tools/export.sh                         # landscape: -> out/outtakes-launch-lottie-16x9.mp4
```

- `tools/build_film.py`: authors all scenes (with `tools/film_parts.py` and `tools/lottie_kit.py`).
- `tools/sfx.py`: synthesises the sound effects from `cues.json`, which the build writes.
- `tools/render.mjs`: renders with **canvaskit-wasm "full"**, the same Skia Skottie engine as the player, offline in Node. Scenes render in parallel.
- `tools/player_shot.mjs`: screenshots pinned frames from the official player, for verification.

### Why some things are done outside the Lottie

- **Film grain** is added at encode time with ffmpeg. As a full-frame overlay-blended Lottie layer it cost about 330 ms per frame in Skottie. The skill also lists grain/dither as renderer-risky.
- **Fonts:** Skottie can't pick axes from a variable font, so `tools/make_fonts.py` cuts static instances: OT Display (Archivo Expanded ExtraBold), OT Wordmark (condensed black italic), OT Body, OT Body Medium and OT Label.

## Checks on the export (motionmaxxing `look.py`)

Both cuts give the same results below. The one exception is motion: 2.6 in landscape, 2.4 in portrait.

- **G0 render exists:** PASS. 56.00 s, audio present.
- **G2 no empty frame:** PASS. No run of more than 3 flat frames.
- **G3 end card hold:** PASS. The film ends mid-motion as the shutter closes.
- **Audio:** −15.9 LUFS, true peak −3.6 dBTP, no flags. 96 % of cuts land within ±80 ms of a sound.
- **Motion:** mean luma change 2.4, below the human band of 4.4–9.8. This is a note, not a gate. It reflects the slower pace requested and the reading holds left for the voiceover.

The official player was also checked on pinned frames: it renders the scenes identically to the Node export.
