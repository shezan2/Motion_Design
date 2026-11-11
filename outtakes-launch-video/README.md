# Outtakes — launch film (Remotion)

A 39-second launch film for outtakes.sg aimed at Outtakes' own photographers. It has one job: get them to sign up (free) and set up a profile before the platform goes live on **20 Nov, 5PM SGT**.

Two compositions share one timeline:

| id | size | use |
|---|---|---|
| `Outtakes-16x9` | 1920×1080 | master: website, YouTube, X |
| `Outtakes-9x16` | 1080×1920 | Reels, TikTok, Shorts |

## The idea

**The shutter is the beat.** Every cut is a camera shutter firing, and the percussion is built from shutter clicks, kicks and impacts. No music, just beats, as briefed. The film opens in burst mode on the collective's own photos, so the first thing a photographer sees is the work of people they know.

## Beats

| # | frames (30 fps) | beat | what it shows the viewer | handoff |
|---|---|---|---|---|
| 1 | 0–165 | **Hook — burst** | 17 shutter clicks speeding up, then the shot lands. "YOU GOT THE SHOT." | the hero photo stays on screen |
| 2 | 165–352 | **Turn — the chase** | That photo shrinks into a sent image in a DM, then invoice follow-ups pile up: "just following up :)", "hello?", "hellooo??", then "Seen". "CHASING PAYMENTS." flips to "BOOKINGS." | riser, then silence and the shutter closes |
| 3 | 352–465 | **Reveal** | OUTTAKES crashes in on the hit. "MADE BY PHOTOGRAPHERS, FOR PHOTOGRAPHERS." | the wordmark docks into the site's nav pill |
| 4 | 465–742 | **Proof — get found** | Site hero: "GET FOUND BY THOSE WHO ACTUALLY NEED YOU." A client types "football photographer", your card appears in the results, gets clicked and opens your profile (portfolio, styles), then CONTACT is pressed | the camera pushes into your card |
| 5 | 742–810 | **Payoff — the call** | "NEW CLIENT — found you on OUTTAKES", phone buzzing | shutter |
| 6 | 810–930 | **Community** | "CAMARADERIE / OVER / RIVALRY.", one word per cut, then Shot of the Week with this week's nominees | shutter |
| 7 | 930–1170 | **CTA** | "SIGN UP FREE." → "SET UP YOUR PROFILE FROM 16 NOV." → **20.11** crashes in → "WE GO LIVE · 5PM SGT" → a cursor presses "SIGN UP FREE · OUTTAKES.SG" → wordmark + url, and the shutter closes | end |

## What is real vs illustrative

- **Real:**
  - All 16 photos (supplied by Outtakes).
  - Colours, fonts and wordmark style from the Figma design system: lime `#D8EE48`, olive, forest, `#0D0D0F`, Archivo extended and condensed italic, Geist.
  - Copy from the Figma file: "Get found by those who actually need you", "Camaraderie over rivalry", "Shot of the week", "Nominees this week", "Find a photographer".
  - The booking flow ("Call the photographer and agree on the shoot").
  - "Made by photographers for photographers", "Sign up free", the dates and the URL, from the brief.
- **Illustrative:**
  - The DM thread.
  - The search results labels ("Football · Matchday" etc.).
  - The "YOUR NAME" profile.
  - The incoming-call card.
  - The UI is rebuilt in code from the Figma components, not screen captures of the live site.
- **Deliberately not claimed:** the film never says the platform handles payments, never invents numbers, and never pairs a real photographer's name with a photo.

## Edit copy and dates

Every date, time and URL lives in `src/timeline.json` → `copy`:

```json
"profilesOpen": "16 NOV", "liveDate": "20.11", "liveTime": "5PM SGT", "url": "OUTTAKES.SG"
```

All timings in that file are absolute frames. Change a beat there and both the picture and the beat track follow it.

## Commands

```bash
npm i
npm run dev                       # Remotion Studio preview
python3 scripts/beat.py           # regenerate public/beat.wav from the timeline (needs numpy + scipy)
npx remotion render Outtakes-16x9 out/outtakes-launch-16x9.mp4 --crf=19
npx remotion render Outtakes-9x16 out/outtakes-launch-9x16.mp4 --crf=19
node scripts/stills.mjs 130,375,700   # review stills for both formats
```

On a machine without a Chrome download, set `REMOTION_CHROME=/path/to/chrome-headless-shell`.

## Sound

`scripts/beat.py` synthesizes everything from scratch: 120 BPM, 808-style kick and bass, clap, hats, a two-stage mechanical shutter click, booms, risers, UI blips and the phone buzz. Each hit is placed on a timeline frame. The master is about −15 LUFS integrated, with peaks around −1 dBFS. There is room for a voiceover later. The chase and call beats are the natural places for it.

## Checks run on the render

- Decodes, 39.0 s, 30 fps, AAC stereo audio present.
- No empty frames, except two deliberate black beats: the curtain before the crash (frames 352–359) and the opening frames 0–2.
- No end-card hold: the end frame keeps contracting until the shutter closes.
- Longest near-static stretch is about 1.3 s, during the client typing, with the caret and camera drift alive.

## Licence note

Remotion is free for individuals and companies of up to 3 people. Larger companies need a Remotion company licence.
