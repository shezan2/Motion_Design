# STATE: Nick R.L. / intro film

| | |
|---|---|
| Client | Nick R.L., Associate Division Director, PropNex Realty (CEA R002622D). Prospect: spec film made to onboard him |
| Video | 20 s brand intro, 16:9 landscape (1920x1080, 30 fps), SFX only (no music, no voiceover) |
| Plan | spec / onboarding piece (no plan yet). Effort: one idea, 5 beats, one bespoke hero (ring to house to card) |
| Version | v1 delivered to Shezan, 28 Nov 2026 |
| Revision rounds used | 0 |
| Deadline | asap ("need to onboard them soon") |

## Decisions
- Copy is only Nick's own words: "days on the market" / "Sold in 1 month" (his Yishun video title), "Right advice / strategy / execution / home" and "Your trusted agent" (his thumbnail bar), "Associate Division Director", "20+ years" (PropertyGuru bio says over 20 years), "HDB · Condo · New launch" (YouTube description).
- "180 days" is the counter's way of showing his "6 months on the market". Confirm with Nick that 6 months is accurate.
- Nick only, no Rina: the brief named Nick R.L. His channels brand the team as "Nick n Rina, Property Power Couple"; ask whether v2 should include Rina.
- Palette taken from his own banner and thumbnails: deep navy + gold. Fonts: Montserrat + Cormorant Garamond (closest licensed match to his banner's sans and serif).
- PropNex logo: the official file from propnex.com, on a white plate (its wordmark is dark).
- CEA advertising details on the card (name, reg. no., phone, agency, licence no.).
- One deliberate scale cut at 16 s into the CTA (also keeps look.py's final-shot gate at 20 %).
- Sound: Clipwing real-sfx method + ElevenLabs official sound-effects skill (SFX v3). Mastered to -15.8 LUFS / -1.4 dBTP (an honest SFX-only level; forcing -14 would crush the "Sold" hit).
- Render: Skottie into a 32-bit float surface, 10-bit 4:4:4 BT.709 intermediate, dithered 8-bit master (no banding in the navy gradients).

## Retiming / changing copy
- All copy: `COPY` dict at the top of `tools/build_film.py`. All timings: the `T` table. Facts change late: one edit, then re-render.
- Rebuild: `python tools/build_film.py` -> `bash tools/render_film.sh 4` -> `python tools/sfx_mix.py` -> `bash tools/master.sh <N>`.

## Log
- 2026-11-28 v1: built from scratch, researched from his EdgeProp channel, YouTube channel, PropertyGuru (search snippets) and propnex.com.
