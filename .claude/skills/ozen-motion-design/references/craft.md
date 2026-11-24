# Craft numbers

Starting values, not targets. Most numbers are motionmaxxing's measurements of 53 professional films (about 4,300 moves) and HyperFrames' motion doctrine, checked against Shezan's reference reels. Frames are at 30 fps.

## Contents
1. Motion personality · 2. Durations · 3. Eases (with cubic-beziers) · 4. Stagger and overlap · 5. Overshoot · 6. Holds, breaths and living frames · 7. Type sizes · 8. Composition · 9. Camera · 10. Cursor and click · 11. Counters · 12. Frame rate and blur

## 1. Motion personality
Pick one per client from the brand sheet and keep it for the whole film (adapted from LottieFiles' archetypes).

| Personality | Typical clients | Move length | Curves | Overshoot | Cuts |
|---|---|---|---|---|---|
| Premium / calm | finance, property, clinics, luxury | long side (12-24 f) | softLand, glide, softInOut | none | few; morphs and slow pushes |
| Clean tech | SaaS, AI tools, fintech apps | median (8-14 f) | snapSettle for heroes, softLand, accelExit | one spring per film | continuous, 1-3 hard cuts |
| Playful / consumer | F&B, retail, kids, lifestyle | short (6-10 f) | snapSettle, popOver | small pops, max 1 in 8 moves | quicker, on the beat |
| Energetic / hype | events, sports, launches, gaming | very short (2-8 f) | whip, crashOut, hard steps | rare | montage, cuts every 0.3-0.7 s |

## 2. Durations
| Property | Entry median (p25-p75) | Exit median (p25-p75) |
|---|---|---|
| Move in x or y | 12 f (6-22) | 13-14 f (7-27) |
| Scale | 11 f (6-22) | 10 f (5-24) |
| Rotation | 10 f (5-25) | 10 f (5-20) |
| Opacity | 6 f (4-12) | 7 f (4-12) |
| Blur | 8 f (5-11) | 7 f (4-9) |

- All moves pooled: median 10 f (0.33 s). A film built on 20-30 f ease-outs everywhere feels slow and soft.
- By role: hooks and proofs 12-14 f, turns have the longest exits (14-16 f), CTA supporting moves halve to 6 f while the hero mark or button runs 18-30 f.
- Shezan's references: big moves median about 5 f, morphs 15-30 f. Snappy moves, generous holds.

## 3. Eases
Cubic-beziers fitted to motionmaxxing's measured curves (error under 0.3% at the sample points). Use them in Lottie keyframes, CSS, GSAP `CustomEase` or After Effects.

| Name | cubic-bezier | Frames (p25 / median / p75) | Use for |
|---|---|---|---|
| cruise | linear | 6 / 9 / 16 | drift, camera creep, counters, fades |
| glide | (0.40, 0.67, 0.76, 1.00) | 7 / 10 / 18 | everyday lands, blur-ins, pushes |
| softInOut | (0.35, 0.06, 0.65, 0.94) | 6 / 9 / 16 | colour and ground ramps, things moving on screen |
| softLand | (0.28, 1.00, 0.72, 0.93) | 6 / 12 / 21 | text rises, panels sliding in, scale-ins |
| snapSettle | (0.14, 1.00, 0.24, 0.95) | 6 / 11 / 29 | hero entries, logos, CTA elements |
| whip | (0.28, 0.67, 0.50, 1.00) | 8 / 13 / 21 | big fast moves landing |
| gentleIn | (0.58, 0.00, 0.96, 0.95) | 6 / 9 / 17 | the start of a fade-out or blur-out, pushes into a cut |
| accelExit | (0.40, 0.00, 0.67, 0.16) | 9 / 13 / 19 | exits off frame, scale-outs, pans away |
| crashOut | (0.56, 0.00, 0.71, 0.00) | 11 / 17 / 31 | exits that hit a hard cut at full speed |
| popOver | (0.29, 0.12, 0.29, 1.41) | 11 / 15 / 27 | the small late lean past the mark (peaks at 1.08) |

The Lottie toolkit's anchors map onto these: `entrance-sharp` and `crash` ≈ snapSettle, `settle-soft` ≈ softLand, `exit-accelerate` ≈ accelExit, `expressive-pop` for pops, `scroll` (0.55, 0, 0.15, 1) for UI scrolls.

Rules:
- Landing decelerates: 58% of measured landings ease out, with 60-70% of the travel done in the first 4 frames.
- Leaving accelerates: exits speed up and end at peak speed on the cut.
- One global ease for everything is the loudest AI signature. Give each role its own curve.

## 4. Stagger and overlap
- Siblings (letters, tiles, rows, avatars): onsets 1-3 f apart, slightly uneven (3, 2, 2, 2...), each move about twice as long as the gap so the tails overlap. A wave under 0.6 s reads as one gesture.
- Whole words: 2-4 f in a fast hook, 4-6 f in a headline, 8-12 f when a voice leads.
- CTA stacks slow down: about 8 f between elements.
- Keep the total stagger of a group under about 0.5 s. With 8+ items, tighten the gap or stagger only the first few.
- Similar elements share one duration and one curve.

## 5. Overshoot
- About 1 move in 11 overshoots in professional work, almost always late (peak at 65-70% of the move) and small (the button 1.055x, a badge +4%).
- Use popOver at most once per beat. The film gets one visible spring, on its payoff: snap to 0.9x, spring to 1.0 over about 0.17 s with a small wobble.
- No bounce or elastic presets.

## 6. Holds, breaths and living frames
- **Reading time:** about 0.2 s per word for 2-5 words (3 words 0.6-0.9 s, 5 words 1.0 s), 1.7-2.0 s for 6-8 words on two lines, 0.5-1.2 s for a single number, never under 0.45 s once a line is complete. UI texture text needs no reading time.
- **Shezan's pace:** the early Outtakes cut was "a bit too fast paced"; the fix was longer holds on the lines that matter, not slower moves. Keep moves snappy and give the point its time.
- **Stillness before the climax:** a 0.3-0.75 s pause between the big action and its result (the press, then the burst).
- **Designed breath:** 0.6-1.5 s, quiet, for a stated reason (just before a payoff or after a matched cut).
- **No dead frame:** any hold longer than 3 frames keeps one living thing: a linear drift of 1-3 px per frame, a 0.5-1% scale creep, light moving, a counter ticking, the caret blinking.
- **No idle wobble:** looping breathe, float or pulse animations read as "the video is waiting". If a scene has finished entering with seconds left, add story (a staged reveal, the product doing something, the camera travelling) or cut it shorter.
- **Shorten towards the end, then let the last scene linger:** for example 1.7 s, 1.5 s, 0.8 s, then the logo 1.4 s.

## 7. Type sizes
Pixel sizes for the cap height you see, by format. Small type is part of the Ozen look, but nothing that must be read goes below the floor.

| Role | 1080x1920 | 1080x1350 | 1080x1080 | 1920x1080 |
|---|---|---|---|---|
| Hero word or number (spent once) | 140-220 | 120-180 | 110-170 | 220-300 |
| Headline / statement | 72-110 | 68-100 | 64-96 | 76-120 |
| Supporting line | 40-56 | 40-52 | 36-48 | 54-76 |
| Smallest text a viewer must read | 34 | 32 | 32 | 40 |
| UI text inside a magnified product shot | at least 34 after magnification | 32 | 32 | 43 |

- One typeface family plus at most one accent face (often a serif italic). Use the client's fonts; if unlicensed or unavailable, say which match you used.
- Sentence case, regular to medium weight (400-560) for most lines, tight but not cramped tracking. Hierarchy comes from scale, not bold.
- Lines of 2-4 words in 9:16; break lines by meaning, not by width.
- Statements centred only when they are paced like speech; never a left-aligned headline block beside media.

## 8. Composition
- One hero per frame, three things at most. A second panel only if it is at least twice as large as the other or the camera moves between them.
- Colour: one ground, one ink, one accent with one meaning (action, "done", the brand). Roughly 60/30/10.
- Grounds: a plain ground works when it is the brand's own surface and something on it lives (soft shapes drifting, a glow, grain, depth). Five flat colours in 20 seconds is a deck.
- One light logic per film: one glow, beam or horizon, changing with the mood.
- Product UI is a magnified fragment readable by the camera, cropped by the frame edge or at least 55% of the frame width; not a small card on a void.
- Safe zones and per-platform margins: `formats.md`.

## 9. Camera
- Move the camera as one group, not as many separate tweens.
- Push or pull: median about 1.46x over 18 f; slow creeps are linear.
- Reveal snap: a one-frame jump to 0.56-0.77x of the old scale, then a 0.3-0.6 s tail.
- Whips: 7-8 f, peak speed early on arrival; the leaving half accelerates into the cut; blur along the direction of travel.
- Micro-drift on held frames: 1-3 px per frame or a 1.16x scale over a long hold.
- 3D UI planes: tilt 8-20 degrees, soft drop shadow, perspective from a camera layer; keep the text readable at the most tilted moment.

## 10. Cursor and click
- A custom cursor, larger than the system one, entering at 2-5x size and shrinking while it travels.
- It parks 4-8 f before acting (the viewer's eye arrives first).
- The press squashes for 2-3 f (cursor about 0.8x, the button 0.63-0.80x of its depth); the target answers one frame later; release with a small rebound or none; cut before the release when the press is the end of a beat.
- No click ripples, no circles under the cursor.

## 11. Counters
- Step the value every frame with shrinking steps, landing on a round number for a claim and an exact one for data (S$70.00).
- Units and labels stay fixed while digits change; keep the digit slots fixed so the line does not jitter.
- Counters run 7-23 f, or are tied to an on-screen cause (a slider, a progress ring).
- Only real numbers. A counter for an invented stat is two failures at once.

## 12. Frame rate and blur
- Deliver 30 fps unless the client or platform asks otherwise. Every frame stays a pure function of time, so renders are repeatable.
- Pick one blur grammar for the film: directional smear on fast moves, focus blur for entrances, or crisp steps. Mixing them reads like two editors.
- Skottie renders no motion blur: fake it with a directional or Gaussian blur on the moving layer during the move, or a stretched smear shape for 2-3 frames.
