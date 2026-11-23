# Outtakes launch film — Lottie edition (text-to-lottie)

The Outtakes launch film, built as **Lottie animations** with
[diffusionstudio/lottie](https://github.com/diffusionstudio/lottie) (text-to-lottie). It uses that project's skill, its
Skia Skottie player and its authoring rules.

- **Formats:** two cuts from one timeline, 30 fps, **60 s** each (59.6 s):
  - portrait 1080×1920 (`public/projects/outtakes-launch`), the primary cut for Reels, TikTok and Shorts
  - landscape 1920×1080 (`public/projects/outtakes-launch-16x9`) for YouTube, the website and X
- **Sound:** sound effects only, no voiceover.
- **Interface (v4):** rebuilt for the **redesigned website** (November 2026), as shown in the six screen recordings. The
  redesign includes:
  - light editorial pages (cool grey #E5E9EC) with black condensed-italic statements
  - the neon green #4BFF2C
  - the film-strip dividers
  - duotone "Browse by sport" cards
  - the new photographer profile page
  - the photographer Studio, with its orange accents
  - the holographic "How a booking goes" cards
  - the light "Get in the frame" corridor

## How it is directed

v3 was a feature tour: a headline above a card, repeated six times. v4 follows **one case from start to finish**: you get
the shot, you set up your Studio, a client finds you and books you at your rate, you get paid (even when someone cancels),
and the shot you took is featured. The craft decisions come from the motionmaxxing references, which distil about 50
designer-made launch films (`references/ui-demo.md`, `transitions.md` and `judgment.md`). The opening montage borrows the
graphic match cut from Nike's "You Can't Stop Us" (Wieden+Kennedy):

- **One carried object.** The hook ends on the celebration shot. The same photo is your profile's hero image, your card in
  the search results, and finally Shot of the Week.
- **Claim, then proof.** Each feature states its claim big, then a 3D interface surface rises over it with the proof. The
  profile chapter does it the other way round: proof first, then the claim.
- **Real UI, magnified.** Every interface is built as 3D planes, using a Lottie camera and 3D layers. They have perspective
  tilt on entry and soft drop shadows. Copy is sized to read on a phone.
- **A custom cursor with press physics.** The black arrow with a white edge enters oversized, travels on eased paths and
  squashes on each press. The button it presses squashes a frame later.
- **Motivated seams.** Transitions use shutter flashes, the site's own film strip as a wipe, a fly-through into the
  profile page, whips that cut at peak speed, and the site's glow carries into a dark end card that echoes the opening's focus lock.

## The film: 12 Lottie scenes

| # | Scene | Frames | What it shows |
|---|---|---|---|
| 1 | Hook — the photographer's eye | 150 | A focus point hops subject to subject (ball, ball, ball, … a face), locking green with an autofocus beep before each shutter. The shots speed up and land on the celebration. "YOU GOT / THE SHOT." |
| 2 | Problem — the DMs | 180 | The DM thread: lowball, cancellation, invoice chasing, Seen. "SOUND / FAMILIAR?" |
| 3 | Hero (new site) | 150 | OUTTAKES crashes in over the motion-blurred hero. Then "STORIES TOLD THROUGH FRAMES", the Sign In / Menu bar, the Shot of the Week credit, "A platform where photographers and athletes can meet in one searchable place." and "Find a Photographer". The site's film strip, full of the collective's frames, wipes up to the light pages. |
| 4 | Set up your Studio | 140 | "SET UP ONCE. / GET BOOKED." The Studio's "Set up your profile" card rises. All eight steps tick in turn as the orange progress bar fills. The button becomes "Preview profile"; it is clicked and the camera flies through. *Organised portfolio.* |
| 5 | Your profile page | 150 | The redesigned profile page: breadcrumbs, avatar, YOUR NAME, the shot, thumbnails, then Reviews, Packages from S$70, Next free date, Covers, Experience, and See packages. Then "YOUR PORTFOLIO, / ORGANISED." |
| 6 | Now clients find you | 180 | "Browse by sport" duotone cards whip in and stop on Football. A client picks it; the film strip of featured photographers rises; the results scroll and stop on your card, and the client hearts it. *Bigger pool of clients searching one place.* |
| 7 | Booked at your rate | 165 | "BOOK YOUR NAME". Full match, S$70, and the November availability calendar. The client taps the 28th, then Book. "Booked · Sat 28 Nov". *Systemised booking, no lowball DMs.* |
| 8 | Paid, even if they cancel | 165 | In the Studio, the photos are delivered and Earnings this month counts S$0.00 → S$70.00. An invoice is sent automatically. A second client cancels, and the cancellation fee is paid to you. *Secure payments, invoices.* |
| 9 | Your shot, featured | 135 | "PHOTOS OF THE WEEK" with the shot from the hook, your card, and the Shot of the Week chip. *Free built-in exposure.* |
| 10 | How a booking goes | 135 | The holographic green step cards (foil lettering) in a 3D carousel, using the site's copy. |
| 11 | Get in the frame | 150 | The light corridor of photo walls, "Live now · Sign up free", "GET IN / THE FRAME", and the two site buttons. "Join as Photographer" is clicked; the site's glow sweeps light, then green, then dark. |
| 12 | End card | 96 | The OUTTAKES wordmark starts out of focus. The hook's focus brackets lock onto it in green (beep), it snaps sharp, and the shutter fires. Then "STORIES TOLD THROUGH FRAMES" and "Sign up free at outtakes.sg", and the shutter closes. The film opens on black, lives in the light pages, and closes on black. |

**Prices:** UI uses the site's format (S$70). The DM keeps "$70 for the full game".

**What's illustrative (not real data):**
- the DM thread
- "Your name", its tagline, reviews, stats and next free date
- the bookings (Sports club, Brand shoot, the dates)
- the earnings figure
- the invoice number
- the other names in the results strip, which are the demo profiles from the site

## Edit it in the player

```bash
npm install
npm run dev        # http://localhost:3030/outtakes-launch/scene-1  (16:9: /outtakes-launch-16x9/scene-1)
```

Every scene exposes **slots** in the player's Properties panel, so you can retype these without touching code:
- statements and the background colour
- the wordmark and tagline
- the profile name and the step title
- "Get in the frame"
- the end card's wordmark and tagline

`?frame=N` pins a frame. Each `scene-N/lottie.json` is a standard Lottie file.

## Rebuild / export

```bash
pip install fonttools brotli scipy pillow numpy
python3 tools/make_fonts.py <archivo woff2 folder> brand/fonts   # one-off: static Archivo cuts for Skottie
python3 tools/make_assets_v4.py <full-resolution originals>      # one-off: bakes brand/photos/v4-* (committed)
bash tools/export.sh                                             # portrait  -> out/outtakes-launch-lottie-9x16.mp4
OT_FORMAT=landscape bash tools/export.sh                         # landscape -> out/outtakes-launch-lottie-16x9.mp4
```

- `tools/build_film.py`: authors the scenes. It uses `tools/parts4.py` (the v4 design system: palette, 3D planes,
  cursor, film strip, focus brackets), `tools/film_parts.py` and `tools/lottie_kit.py`.
- `tools/make_assets_v4.py`: bakes the image assets. These are hook crops from the 2560 px originals, with each subject
  placed for the focus point, plus the blurred hero plate, the duotone sport cards, the foil step lettering and the round
  avatar.
- `tools/sfx.py`: synthesises the sound effects (shutters, autofocus beeps, taps, chimes, whooshes) from `cues.json`.
- `tools/render.mjs`: renders with canvaskit-wasm (Skia Skottie, the player's engine). Film grain is added by ffmpeg.

### Why some things are done the way they are

- **3D interfaces:** each interface is a 3D null with 3D children (shapes, native text, images), viewed by a Lottie
  camera. Skottie draws 3D layers in layer order, so each plane is authored back to front. Drop shadows and Gaussian blur
  are native Skottie effects.
- **Foil lettering and duotones are baked**, because Lottie text can't take a gradient fill and Skottie has no duotone
  effect.

## Checks on the export (motionmaxxing `look.py`)

Run on both final exports with `--expect 59.57 --expect-audio`:

| Gate | Portrait 9:16 | Landscape 16:9 |
|---|---|---|
| G0 render exists | PASS (59.57 s, audio present) | PASS |
| G2 no empty frame | PASS | PASS |
| G3 end card hold | PASS (ends mid-motion as the shutter closes) | PASS |
| Loudness | −15.8 LUFS, true peak −3.0 dBTP, no flags | −15.8 LUFS, true peak −3.2 dBTP, no flags |
| Cut sync | 68 % of cuts within ±80 ms of a sound | 61 % |
| Motion (a note, not a gate) | mean luma change 3.7 | 3.3 |

Motion sits below the human band of 4.4–9.8. That reflects the light pages and the slower pace you asked for; the holds
drift so nothing sits frozen.

The official player renders the hook's focus point, the 3D Studio card with its shadow and the foil step cards the same
as the Node export, checked on pinned frames.
