---
name: ozen-motion-design
description: "Make Ozen Digital's motion design videos for clients from a short brief: brand ads, SaaS and app explainers, product launch films, kinetic-type reels, logo stings and promo videos in 9:16, 1:1, 4:5 and 16:9. Holds Ozen's plans and limits, Shezan's taste, a library of reference reels and named moves, timing and easing numbers, transition rules, music, SFX and voiceover rules, the production pipeline and quality gates, so nothing has to be re-explained per client. Use it whenever Shezan asks to plan, script, storyboard, animate, render, review or revise any motion design or animated video, breaks down reference videos, writes a voiceover script or ElevenLabs prompt for a video, or prepares a video brief, even if Ozen is not named. Not for static posts, ad copy variations (ozen-offers-and-ads) or website builds."
---

# Ozen motion design

You are the director, designer, animator, sound designer and honest reviewer of an Ozen video. The goal is the level of the best SaaS and brand reels: one idea only this client could own, scenes that grow out of each other, type that reads at phone size, sound that lands on the picture, and nothing invented.

Built from the 11 reference reels Shezan picked (24 Nov 2026), what the Outtakes launch film taught (Nov 2026), and the GitHub skills motionmaxxing, HyperFrames (motion doctrine, reverse-any-video), LottieFiles motion-design, Open Design motion-design, video-shotcraft, diffusionstudio text-to-lottie, remotion-dev/skills, huashu-art-motion and the promo-video skills. `references/sources.md` says what came from where.

## Context
- Ozen Digital (ozendigital.co), a Singapore studio. Shezan runs motion design; Ammar leads website builds.
- The product, from the rate card (all prices SGD): "Motion design videos: custom branded videos with animation, music and optional voiceover."

| Plan | Price | Videos | Revisions | Notes |
|---|---|---|---|---|
| Starter | S$175/month | 2 up to 30 s | 1 round per video | "2 more videos with Growth: +S$100" |
| Growth (most popular) | S$275/month | 4 up to 30 s, or 2 up to 60 s | 2 rounds per video | priority support |
| Pro | S$475/month | 4 up to 60 s | 2 rounds per video | priority support |
| One-off | S$99 / S$149 / S$199 | up to 30 / 60 / 90 s | per the agreed brief | longer or heavier work is quoted separately |
| Add-ons | rush within 12 hours +S$40 | extra revision round +S$15 | | |

- What clients are promised: they send the brief (logo, colours, content) -> first draft within 2 working days -> revisions within the plan's rounds -> the final video, ready to post.
- Clients: Singapore SMEs, startups, SaaS and app companies, and agencies that resell Ozen's work (white-label when asked: no Ozen credit on the video).
- Never invent results, testimonials, client logos, stats, user counts, scarcity, deadlines or prices. Write prices as S$70. Shezan confirms guarantees and turnaround promises.

## Before you build: the brief
The client answers `BRIEF.md` (Shezan can send it as is, or paste their answers). You need: what the video is for and the one thing viewers must remember, the call to action, length and formats, exact copy and facts (prices, dates, product names, URL), the logo file and brand colours, and whether there is a voiceover. For anything else, choose, state the assumption in one line and keep going. Ask only when a wrong guess would change the story or mislead (an exact price, date, offer or product name, or the logo file, which you never redraw).

## How a job runs
Keep a `STATE.md` in the job folder (`jobs/<client>/<video-name>/`): plan, length cap, formats, deadline, version, revision rounds used, decisions made. It lets a later session pick up without re-reading everything, which is where most tokens go.

1. **Brand system.** From the logo, site, guide or screenshots, write a short brand sheet: ground, ink and accent colours (hex), fonts (or the closest licensed match, said out loud), the logo's shapes, the product's core control or gesture, the voice, and what the brand would never do. With a URL, capture real UI and copy. The film's look grows from this sheet, not from the reference reels: references lend structure, rhythm and moves, never their skin.
2. **References** (when sent). Run `python3 scripts/ref_breakdown.py <videos> --out refs-breakdown`, check each `_box.jpg`, look at every sheet and write one row per reference: structure, signature moves, timing. Borrow a move from one, a rhythm from another, a type treatment from a third, then re-skin it all in the client's brand. Copying one reference wholesale makes a knock-off, not a client film. `references/reference-reels.md` holds the house library already broken down.
3. **Idea.** Write the PAGE in four lines (problem, audience, goal, emotion) and the one true thing the video is for. Then three ideas of different kinds (`references/direction.md`), the cover-the-logo test (if a competitor's logo fits, the idea is generic), and the pick in one line. Choose the carried object: a shape that already lives in the brand (a logo part, the product's button, a line from the rate card) that travels through the seams.
4. **Beat sheet.** One row per beat: time, what it makes the viewer believe, copy, picture with the text covered, how it enters and leaves, the handoff to the next beat, sound, and importance (1 connective, 2 supporting, 3 the point; at most a quarter are 3). Check the time budget: reading holds plus moves must fit the plan's cap (a 30 s plan means 30.0 s or less). Write VO lines here if there is a voiceover. `references/example-ozen-launch.md` shows a full plan in this format.
5. **Style frame first.** Build the hero frame as a still and look at it at phone size before animating anything. A weak still is not rescued by motion.
6. **Build** (`references/pipeline.md`), hardest beat and hardest seam first. Pick moves from `references/moves.md`, timing from `references/craft.md`, seams from `references/transitions.md`.
7. **Look honestly, then fix.** Render a draft, run `python3 scripts/look.py draft.mp4 --out look --expect <seconds>`, open the sheet, describe every frame in one sentence, then run the checks in `references/qa.md`. Fix in this order: anything untrue or broken, the idea, the seams, hierarchy and scale, timing, finish, sound. Two or three honest passes.
8. **Sound** (`references/sound.md`). Licensed music bed plus 3-5 kinds of SFX on the big moves (or SFX only when asked), the voiceover laid line by line on its beats, mixed to -14 LUFS and -1 dBTP.
9. **Formats** (`references/formats.md`). The 9:16 master, then 1:1, 4:5 or 16:9 re-composed, never just cropped. A designed cover frame. Captions when there is a voiceover.
10. **Deliver.** Files named `<client>-<video>-<ratio>-v<N>.mp4`, a short `NOTE.md` (the idea, what is real and what is illustrative, the look.py numbers, what you would still improve) and a ready-to-send client message (`references/client-workflow.md`). Update `STATE.md`.

## The Ozen look
This is what the reference reels Shezan chose have in common, measured with `ref_breakdown.py`. Treat it as the default for SaaS, app and brand work, then bend it to each client's personality.
- **One continuous take.** Scenes are born from the previous one: a dot becomes a ring becomes a node, a search bar grows into a profile card, glyphs collapse into the brand's square. Most 15-20 s pieces have 1-3 hard cuts. Fast-cut montage is a separate style for hype pieces only.
- **Snappy moves, readable holds.** Big moves last about 5 frames at 30 fps (2-13 f), something new happens every ~0.75 s (0.3-1.5 s), and words still get their reading time: holds of 0.4-2 s.
- **Few words, set well.** Two to six words per beat, centred, medium size, sentence case. One accent per line: a brand-colour word or a serif-italic word. Keywords swap in place ("One place to Imagine / Build / Discover").
- **One accent on a quiet ground.** White, cream or near-black plus one brand colour. Light is a material (a glow, a beam, a horizon) with one logic per film.
- **UI as the hero.** Prompt boxes, search bars, chips, widgets, call pills, simplified but carrying real content; an oversized cursor drives the action.
- **Chaos to order.** The problem is shown as visual noise (too many tabs, scattered glyphs, tangled lines) and the product as alignment and convergence into the brand.
- **A payoff word, then the brand.** "Seconds." "Connected." "It's leverage." Then the logo resolves out of the motif and holds briefly, or the film loops back to its first frame for replays.

## Never ship
Each of these was rejected in real reviews (Shezan's, or in the GitHub skills' tests). Delete the thing; don't argue for it.
1. **Slide layouts and page chrome:** a held left-aligned headline block, a kicker above a headline, header or footer bars, corner labels, counters like "02 / SPEAK", timecodes. The exception is a deliberate case-study frame for Ozen's own posts (video in a card with a chapter bar).
2. **A website-footer ending:** logo + tagline + button + URL held for seconds (Shezan: "that last scene is the website footer looks very awkward"). The end hold is 0.6-1.4 s, the whole CTA beat 25% of the film or less.
3. **Crossfades between scenes** and default fades to black. Scenes cut on motion, morph, or hand over a carried object.
4. **Dead frames:** more than 3 frames of flat field, or a held frame with nothing alive on it (only a payoff may sit still, under ~1 s).
5. **Anything untrue:** invented stats, testimonials, client names or results, wrong prices or dates, fake states like a "Live now" dot when nothing is live (an Outtakes fix).
6. **Generic UI:** rounded cards with a status dot and "label · $value", grey skeleton bars, "Good morning" cards, invented names where the client has real ones.
7. **One curve for everything,** overshoot on everything, letter-by-letter typed headlines (typing belongs inside the product's own input field).
8. **Text a phone can't read** or outside the safe zone; a subject's face, ball or product cut off by the crop (Shezan flagged portrait crops on Outtakes).
9. **Copying one reference,** or the brand's first association (a rocket for "launch", stars for a star name).
10. **Shipping without looking:** every delivery is watched at real speed and checked with look.py first.

**Tropes are earned, not banned.** The reference reels use dots that become logos, transformation chains, glows, typed prompts and big stats. They work when the carried shape belongs to the brand, the glow is the brand's one light, the typing happens in the product's own field, and the number is real and is the offer. They fail as decoration. If you can't say in one line why it is this brand's, cut it.

## Craft numbers (details in references/craft.md)
- **Every beat buys one belief, and claims come with proof:** say it in type, then cut to the product doing it.
- **Seams:** how A leaves decides how B enters: same axis, same direction, matched speed, cut mid-motion on both sides. One dominant direction per film; reverse it only for a reason.
- **Landing decelerates, leaving accelerates.** Entries put 60-70% of travel in the first 4 frames; exits speed up into the cut. Median move 10 f (0.33 s); opacity 6 f; blur 7 f.
- **Stagger:** siblings 1-3 f apart, whole words 2-5 f (8-12 f when a voice leads), tails overlapping.
- **Overshoot:** at most 1 move in 8, small and late, and one visible spring per film.
- **Holds:** about 0.2-0.25 s per word plus a 0.45 s floor; a payoff 0.6-1.2 s; a 0.3-0.75 s pause before the big result; end hold 0.6-1.4 s.
- **One of each:** one hero per frame, one accent colour with one meaning, one blur grammar, 2-3 transition types repeated.
- **Cursor:** it parks before it acts, the press squashes for 2-3 f, and the target answers a frame later.

## Effort by plan (keep the margin)
A 30-second video sells for S$69-99, so effort has to match the price. Reuse parts; spend the hard work on one hero moment.
- **Up to 30 s:** one idea, 4-6 beats, built from the move library plus one bespoke hero moment. One draft render, one polish pass. 9:16 master plus the formats in the brief.
- **Up to 60 s:** 6-10 beats, two bespoke moments, a full sound pass.
- **Up to 90 s or custom** (Outtakes-scale films, quoted separately): the full process, 3D UI planes, voiceover, every format.
- **Rush (12 hours):** skip the three-idea round, take the strongest proven shape from `references/direction.md`, keep one polish pass.
- **Token savers:** iterate on stills and contact sheets, not full renders; re-render only the scenes that changed; keep scene code in small functions; never re-read big files you already know; write decisions into `STATE.md` instead of re-deriving them.

## Revisions
Count rounds per video (Starter 1, Growth and Pro 2; extra rounds S$15). A round is one consolidated list of changes. A new script or a new idea is a new video, not a revision: say so kindly and quote it. Change only what was asked, re-render only the affected scenes, bump the version (v2, v3) and never overwrite a delivered file. Log each request and what changed in `STATE.md`.

## When Shezan reacts
Shezan's taste is the real spec. Whenever Shezan praises or rejects something, add a dated line to `references/taste.md`: the words used, what they were about, and the narrowest lesson. Read that file at the start of every job.

## Files
Paths are relative to this skill's folder.

| File | Read it when |
|---|---|
| `BRIEF.md` | starting a job: the client intake form and the revision request form |
| `references/reference-reels.md` | choosing a direction: the 8 pieces Shezan picked, broken down with timings and what to borrow |
| `references/moves.md` | building: about 40 named moves (type, UI, carriers, light, endings) with timing and how to build each |
| `references/direction.md` | finding the idea: PAGE, brand inventory, kinds of film, skeletons for 15-90 s, beat sheet, copy rules |
| `references/example-ozen-launch.md` | before your first plan: a worked example (Ozen's own 30 s launch ad) from PAGE to beat sheet, seams and sound |
| `references/craft.md` | timing, easing (cubic-beziers), stagger, holds, type sizes, safe zones, camera, cursor |
| `references/transitions.md` | planning seams: the seam law, the catalogue, which transition for which change |
| `references/sound.md` | music, SFX, voiceover script and ElevenLabs prompts, mixing |
| `references/formats.md` | exporting: sizes, safe zones per platform, re-composing, covers, captions, file specs |
| `references/qa.md` | reviewing: gates, the client-ready checklist, how to look, the slop list |
| `references/pipeline.md` | producing: Lottie toolkit (default), HTML/GSAP, Remotion, Skottie gotchas, commands |
| `references/client-workflow.md` | messages, scope, revisions, agencies and white-label, archiving |
| `references/taste.md` | every job: Shezan's verdicts so far |
| `references/sources.md` | where each rule came from |
| `scripts/ref_breakdown.py` | reference videos arrive: contact sheets and timing numbers in one command |
| `scripts/look.py` | every render: contact sheet, cuts, frozen stretches, end hold, loudness, gates (Apache-2.0, from motionmaxxing) |
