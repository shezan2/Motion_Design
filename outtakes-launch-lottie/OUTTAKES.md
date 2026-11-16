# Outtakes launch film — Lottie edition (text-to-lottie)

The Outtakes launch film, built as **Lottie animations** with
[diffusionstudio/lottie](https://github.com/diffusionstudio/lottie) (text-to-lottie). The project uses its skill, its Skia
Skottie player and its authoring rules.

- **Formats:** two cuts from one timeline, 30 fps, **64 s** each:
  - portrait 1080×1920 (`public/projects/outtakes-launch`), the primary cut for Reels, TikTok and Shorts
  - landscape 1920×1080 (`public/projects/outtakes-launch-16x9`) for YouTube, the website and X
- **Sound:** sound effects only, no voiceover (add your new VO on top).
- **Interface:** rebuilt to match the **live website** (outtakes.ozendigital.co, November 2026). This covers the hero, the
  sideline section, the photographer profile page, packages and availability, the four booking steps, "Get in the frame"
  and the footer. The site's signature animations are ported too (see below).

## The film: 13 Lottie scenes

| # | Scene | Frames | What it shows |
|---|---|---|---|
| 1 | Hook — burst mode | 140 | Ten of the collective's photos fire on shutter clicks, then the shot lands. "YOU GOT / THE SHOT." |
| 2 | Problem — the DMs | 195 | One DM thread: "how much for saturday's match?" → "$70 for the full game" → "can do $30?" (lowball) → "game cancelled, no need to pay ya" (cancellation) → "just following up on the invoice :)" → Seen. "SOUND / FAMILIAR?" |
| 3 | **Hero (site)** | 135 | OUTTAKES crashes in over the motion-blurred hero photo. Then "STORIES TOLD THROUGH FRAMES", the Sign In / Menu bar, "Made by photographers, for photographers." and the green "Find a Photographer" button. The page then scrolls into the next section. |
| 4 | **Every sideline shot starts with a search (site)** | 135 | The cream-to-green glow section. Tilted 3D photo cards fly in and orbit while the headline loads letter by letter. |
| 5 | **Now clients chase you** | 150 | A client searches "football photographer" and your profile is in the results. Booking requests then stack up: season coverage, a brand shoot, a final. *More clients, bigger clients, one central place where they search.* |
| 6 | **Your portfolio, organised (site profile page)** | 150 | The photographer page: hero, avatar, YOUR NAME, tagline, Specialises in / Packages from S$70 / Covers, and the Featured grid. *Proper organised portfolio.* |
| 7 | **Booked at your rate (site packages + availability)** | 165 | The lowball DM is struck out and thrown away. The AVAILABILITY calendar for November 2026 appears; 21 Nov is tapped. Then the PACKAGES panel: Full match, S$70, "Book" is tapped → "Booked · Sat 21 Nov". *Systemised booking, fewer lowball DMs.* |
| 8 | **How a booking goes (site steps, 3D)** | 135 | The four green step cards in a 3D carousel, using the site's copy: ONE Call the photographer and agree on the shoot, TWO Book their package and date on Outtakes, THREE Pay once they accept, FOUR Get shot, then get your photos. |
| 9 | **Invoices, done for you** | 120 | A proper invoice builds itself (billed to, items, S$70.00 total), then is stamped Sent. *Invoice generation for big clients.* |
| 10 | **Paid. Even if they cancel.** | 135 | Payment secured (S$70.00). The client cancels, and the cancellation fee is paid to you. *Secure payments.* |
| 11 | **Free exposure, built in** | 135 | Shot of the Week feature, the Featured chip and the nominees strip. *Free built-in exposure and marketing.* |
| 12 | Dates | 165 | "SIGN UP / FREE." → "SET UP YOUR / PROFILE FROM / 16 NOV." → **20.11** crash → "WE GO LIVE · 5PM SGT". |
| 13 | **Get in the frame (site, 3D) + footer** | 165 | A 3D corridor of photo walls glides past. Over it: "GET IN / THE FRAME", the site's two audience lines and buttons ("Join as Photographer" gets tapped). Then the site footer: cream page, "Sign up free at outtakes.sg · Live 20.11 · 5PM SGT", and the giant green OUTTAKES. |

### Site animations ported to Lottie

- **Hero wordmark crash:** a giant italic OUTTAKES slams in over the panning, motion-blurred hero plate.
- **Smooth page scroll as a transition:** the hero scrolls up and the sideline section's glow and headline scroll in with
  it, as on the site. The carry from chapter 3 into chapter 4 is frame-exact: the last frame of 3 is pixel-identical to the
  first frame of 4.
- **Letter-by-letter headline load:** "EVERY SIDELINE SHOT STARTS WITH A SEARCH" arrives as faint ghost letters, then
  lights up one character at a time. It uses a native Lottie text animator (range selector on opacity).
- **Floating 3D photo cards:** tilted cards fly in from depth and slowly orbit. This uses a real Lottie 3D camera and 3D
  image layers.
- **3D step carousel:** the green ONE–FOUR cards rotate through, the active card bright and the neighbours turned away and
  darker.
- **"Get in the frame" photo corridor:** walls of photo panels in 3D perspective, moving toward the viewer.
- **Site buttons, calendar and packages:** the green and white rounded buttons with arrows, availability dots and package
  rows, all in the site's colours and type.

**Type:** statements use the site's condensed italic display face (OT Wordmark). Small titles use Archivo Expanded (OT
Display).

**Seams:** most chapters end with the camera-shutter curtain closing mid-motion, and the next opens with it finishing. That
is an occlusion wipe from the skill's transition grammar. The exception is hero → sideline, which is a continuous page scroll
like the site's.

**Feature beats:** all use one repeated layout: the same headline block (white line plus green line), one support line and
one proof object.

**Prices:** UI elements use the site's currency format: **S$70** and **S$70.00**. The casual DM in chapter 2 stays
"$70 for the full game".

**What's illustrative:**
- The DM thread.
- The sample booking, invoice and payment values (S$70, Jalan Besar Stadium, Sat 21 Nov, Sports club).
- "YOUR NAME" and its tagline.

No real photographer's name is attached to any photo.

## Landscape layout

The 16:9 cut is laid out for the wide frame; it isn't the portrait one cropped.

- **Hero:** the wordmark sits top-left, the tagline under it, the nav bar top-right, and the positioning line and button
  bottom-right, as on the desktop site.
- **Feature beats:** the headline block sits in a left column. The proof (search, profile page, calendar and packages,
  carousel, invoice, payment cards, Shot of the Week) sits in a right column at x 1000–1800.
- **Hook, problem and sign-up statements:** set on one line ("YOU GOT **THE SHOT.**", "SOUND **FAMILIAR?**",
  "SIGN UP **FREE.**").
- **Footer:** the giant wordmark is cropped by the bottom edge, as on the site.
- **Timing and sound:** identical in both formats, so they share one sound-effects track.

`OT_FORMAT=landscape` switches `tools/build_film.py` and `tools/film_parts.py` to the 16:9 layout.

## Edit it in the player

```bash
npm install
npm run dev        # http://localhost:3030/outtakes-launch/scene-1  (16:9: /outtakes-launch-16x9/scene-1)
```

Every scene exposes **slots** in the player's Properties panel. You can retype these without touching code:
- each scene's headline lines and background colour
- `brand` and `tagline` (hero)
- `sideline1` and `sideline2`
- `profileName`
- `sotw`
- in scene 12: `profilesOpen` (`16 NOV.`), `liveDate` (`20.11`) and `liveLine` (`WE GO LIVE · 5PM SGT`)
- `endBrand` (footer wordmark)

`?frame=N` pins a frame.

Each `public/projects/outtakes-launch/scene-N/lottie.json` is a standard Lottie file. It works in lottie-web, iOS, Android
and Flutter, and can be imported into After Effects.

## Rebuild / export the MP4

```bash
pip install fonttools brotli scipy pillow numpy
python3 tools/make_fonts.py <archivo woff2 folder> brand/fonts   # one-off: static Archivo cuts for Skottie
bash tools/export.sh                                             # portrait:  build -> SFX -> render -> out/outtakes-launch-lottie-9x16.mp4
OT_FORMAT=landscape bash tools/export.sh                         # landscape: -> out/outtakes-launch-lottie-16x9.mp4
```

- `tools/build_film.py`: authors all scenes (with `tools/film_parts.py` and `tools/lottie_kit.py`). It also bakes the 4:5
  panel crops for the corridor (`brand/photos/panel-*.jpg`, git-ignored, rebuilt on demand).
- `tools/sfx.py`: synthesises the sound effects from `cues.json`, which the build writes.
- `tools/render.mjs`: renders with **canvaskit-wasm "full"**, the same Skia Skottie engine as the player, offline in Node.
  Scenes render in parallel.
- `tools/player_shot.mjs`: screenshots pinned frames from the official player, for verification.

### Why some things are done the way they are

- **3D:** scenes 4, 8 and 13 use a Lottie camera layer (`ty: 13`) and 3D layers (`ddd: 1`). Skottie draws 3D layers in
  layer order, not by depth, so far layers are authored first. Corridor panels are cropped up front because a 3D image
  layer draws its whole image.
- **Film grain** is added at encode time with ffmpeg. As a full-frame overlay-blended Lottie layer it cost about 330 ms per
  frame in Skottie. The skill also lists grain/dither as renderer-risky.
- **Fonts:** Skottie can't pick axes from a variable font, so `tools/make_fonts.py` cuts static instances: OT Display
  (Archivo Expanded ExtraBold), OT Wordmark (condensed black italic), OT Body, OT Body Medium and OT Label.

## Checks on the export (motionmaxxing `look.py`)

Run with `--expect 64.17 --expect-audio` (first v3 portrait export):

- **G0 render exists:** PASS. 64.17 s, audio present.
- **G2 no empty frame:** PASS. No run of more than 3 flat frames.
- **G3 end card hold:** PASS. The film ends mid-motion as the shutter closes over the footer.
- **Audio:** −16.3 LUFS, true peak −3.3 dBTP, no flags. 93 % of cuts land within ±80 ms of a sound.
- **Motion:** mean luma change 3.4, up from 2.4 in v2 but still below the human band of 4.4–9.8. This is a note, not a
  gate. It reflects the slower pace you asked for and the reading holds left for the voiceover.

The official player renders the 3D scenes (4, 8, 13) and the letter-by-letter load the same as the Node export, checked
on pinned frames.
