# Criter AI / intro-20s / v1

**Idea:** the noise of Australian visa options collapses into CriterAI's own check mark; the check opens a chat, a student gets an instant answer, taps **Verify by Expert**, and every point is checked by a registered migration agent. Then their headline, then the logo. It is this brand's film because the carried object is their logo's check and the hero moment is their own product feature, the one generic AI can't claim.

## Files (out/)
| File | What |
|---|---|
| `criter-ai-intro-16x9-v1.mp4` | **Main.** 1920x1080, 30 fps (house standard), H.264 High, BT.709, AAC 320 kbps 48 kHz, 20.00 s, 18.4 MB |
| `criter-ai-intro-16x9-60fps-v1.mp4` | Same film at 60 fps (smoother UI motion), 19.1 MB |
| `criter-ai-intro-16x9-4k-v1.mp4` | 3840x2160, 60 fps (true 4K render, not upscaled), for YouTube 4K or an agency edit, 36.6 MB |
| `criter-ai-intro-16x9-vo-v1.mp4` + `.srt` | Voiced cut (ElevenLabs v4 take, placed line by line, SFX ducked under speech), captions file. 60 fps and 4K voiced files re-mux from `audio/mix_vo.wav` (see VOICEOVER.md) |
| `criter-ai-intro-16x9-v1-preview.mp4` | 1280x720 light copy for WhatsApp, 1.4 MB |
| `criter-ai-intro-cover-v1.jpg` | Cover: the verified answer (hero frame) |
| `criter-ai-intro-cover-alt-v1.jpg` | Alternate cover: the stacked headline |

Every frame is motion-blurred for real: 8 renders per frame over a 180-degree shutter at 30 fps (4 per frame at 60 fps), averaged in ffmpeg.

## Beats
1. 0.0-3.1 Hook: "Which visa?" / "Which documents?" / "What's next?" over their own subclass marquee, three depths, getting denser. Buys: this is my confusion.
2. 3.1-4.2 Turn: everything collapses into a gold point that draws their check; light blooms to cream; the C closes. Buys: CriterAI is the answer.
3. 4.2-5.4 Ask: the mark becomes the chat field; "What do I need for my student visa?" types; send. Buys: I can just ask.
4. 5.4-7.5 Answer: the field becomes the chat card; instant answer with four items and the Verify by Expert button. Buys: it answers straight away, specifically.
5. 7.5-11.8 Verify (hero): press; "Expert review · in as little as 30 minutes"; each row ticks; "Verified by a Registered Migration Agent". Buys: a real expert checks it.
6. 11.8-16.0 Payoff: "Lawyer trained." / "Law driven." / "AI delivered.", then the three assemble into their stacked headline. Buys: built by lawyers, not a generic chatbot.
7. 16.0-20.0 Brand: the word "AI" carries into the wordmark, "Criter" slides out, the C closes and the check lands; "Start for free" + criter.ai; the button is pressed and its arrow becomes the check.

## Real (captured from criter.ai on 28 Nov 2026)
- Logo: their `criterai-lockup.png`, split into four aligned layers (ring, check, Criter, AI) that recompose to the original; drawn on with masks, never redrawn.
- Colours from their CSS (#fffef7, #1b6b6d, #071b1c to #123f41, #a6e1d1, #e8f5f1, #1a2332); logo teal and gold sampled from the PNG.
- Type: Geist (their font). Headlines in Gelasio 700, the open-licence match for their `ui-serif, Georgia` stack (New York on Apple devices).
- Copy: "Lawyer Trained, Law Driven, AI Delivered" (hero, set in sentence case), "in as little as 30 minutes" (hero), "Verify by Expert" and "registered migration agent" (their FAQ on expert verification), "Start for Free" (hero button; FAQ: free during the closed beta), criter.ai. Hook pills: their subclass marquee, the document names on their profile card and steps, and terms from their roadmap and testimonials.

## Illustrative
- The chat UI is a rebuild in their styles: their logged-in app is not public. Swapping in real app screenshots is the biggest upgrade available.
- The student's question and the four-item answer (Confirmation of Enrolment, Genuine Student requirement, evidence of funds, Overseas Student Health Cover) are general Subclass 500 requirements written for the demo; the beta covers student visas. Ask CriterAI's agents to confirm the wording before it runs as an ad.
- "Instant answer" tag and the review pill are rebuilt states of the flow their FAQ describes.
- Left out on purpose: the $500 beta credit offer and the 17 Nov countdown (the launch date has passed), testimonials, and stats.

## Sound (SFX only, no music, no voice)
- **Skills used:** [elevenlabs/skills](https://github.com/elevenlabs/skills) `sound-effects` (official, MIT): 10 designed sounds generated with Sound Effects v3 through the ElevenLabs connector, 4 variations each, 680 credits. [GhazaGG/Game-Sound-Effect-for-Claude](https://github.com/GhazaGG/Game-Sound-Effect-for-Claude) `game-sfx` (MIT): the check-chime motif, verify arpeggio, click, ticks and pop rendered from JSON patches with its click-proof synth, and its `doctor.py` measured every source (it caught two chimes that did not read as rising and a harsh tick; all fixed). [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion): every sound placed by its own measured peak or onset on cues exported from the film.
- **Palette (5 families):** UI clicks/ticks/pops; air (whooshes, riser, bloom); the check chime (the brand's sonic motif: E5 to A5, reused for the verify arpeggio A5-C#6-E6-A6 and the CTA); low warm hits (badge, payoff thuds, logo); textures (keyboard, accelerating clock under the review ring).
- **Mix:** 42 cues, room-tone floor at -65 dBFS, 9 dB dip before the logo hit, sub hits high-passed at 42 Hz and soft-clipped with a harmonic body layer so they read on phones, oversampled soft clip then true-peak limiter. -14.0 LUFS integrated, -1.8 dBTP in the AAC file. Level order: logo hit, badge, opening check, thuds, arpeggio, chimes, clicks.
- **Licences:** synth sounds are original. ElevenLabs sound effects were generated on the connected ElevenLabs account: confirm that account's plan covers commercial use of generated sound effects before CriterAI runs this as an ad.
- I can't listen; the mix was checked by measurement (doctor reports, per-event levels, look.py). **Listen once on headphones and once on a phone speaker before sending.**

Voiced cut: -14.0 LUFS, -2.3 dBTP, LRA 2.3 LU, voice 9.9 dB or more over the SFX for 90% of speech (median 26.5 dB), G0/G2/G3 PASS, end hold 1.13 s.

## look.py (main file; the 4K file also passes G0/G2 with the same audio numbers)
Length 20.00 s, G0 PASS, G2 PASS (no flat runs), G3 PASS (end hold 1.13 s; no hard cuts, one continuous take), -14.0 LUFS, -1.8 dBTP, audible 0.04-20.00 s, no dropouts, no audio flags. Mean motion 1.4/255, below the human band (6.8): a calm, premium pace on a flat cream ground; every hold has a living element (drift, creep, moving light). The 60 fps file measures the same picture with half the per-frame change, so its end hold reads 1.63 s by that metric; the 30 fps main is the gated deliverable.

## Frames (look.py sheet, one per 1.25 s)
0.6 dark forest ground, "Which *visa*?" in serif with the keyword in mint italic, subclass pills drifting at three depths · 1.9 "Which *documents*?", document pills join, denser · 3.1 everything collapsed into the gold point drawing the check · 4.4 cream ground, the field with the CriterAI mark and "Ask a visa question…" · 5.6 the field becoming the chat card, the question rising into the teal bubble · 6.9 the instant answer, four items, Verify by Expert · 8.1 camera pushed in, cursor pressing Verify by Expert · 9.4 review pill, rows ticking green · 10.6 all four verified, "Verified by a Registered Migration Agent" with the logo mark · 11.9 the card sinking back · 13.1 "Law driven." over the blurred card · 14.4 "*AI* delivered." · 15.6 the full stacked headline · 16.9 the lockup building, the C drawing · 18.1 lockup with "Start for free →" and criter.ai · 19.4 button pressed, arrow turned into the gold check.

## Still to improve
- Real app screenshots in place of the rebuilt chat card.
- Optional mascot cameo: `build/index.html?mascot=1` puts Criter the snail (thumbs up) into the end card instead of the cursor press. Left out of the main cut: it competed with the CTA.
- Only 16:9 was asked for; 9:16 and 1:1 would be re-composed, not cropped.
- If they want more energy: more camera travel in the answer beat.
