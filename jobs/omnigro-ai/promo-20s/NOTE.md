# OmniGro AI / promo-20s / v2 (SFX only)

**Change (27 Nov 2026, Shezan):** "no music just sound effects and for sound effects use the best github skills out there". The picture is identical to v1 (the video stream is copied bit for bit); the soundtrack is rebuilt as sound effects only, from real recorded and CC0 library sounds, placed on the film's own frames. File: `out/omnigro-promo-16x9-v2.mp4` (+ `-preview.mp4`). v1 (music + synthesized SFX) is kept unchanged.

## The GitHub skills used, and what each gave
| Skill | What it gave this mix |
|---|---|
| [Clipwing/skills real-sfx](https://github.com/Clipwing/skills) | the method: real recordings, never synthesis; peak targets per role (hit -4, whoosh -9, riser -12, click/pop -14 dBFS) with perceived loudness levelled inside each role and the "leveller trap" check; sounds placed by their measured arrival, peak or cut, not their file start; antiphase files played from one channel; for an SFX-only film one steady dark real bed at -54 dBFS so it never drops to digital silence; small sounds only on real picture moves in holes; the density, pause, floor, mono and masking checks; a listen list for human ears. Its own reels and blind tests set these numbers. |
| [GFXER/sfx-library](https://github.com/GFXER/sfx-library) | the pick table per visual event and lead frames (clicks 1-2 f early, thumps 1 f, whooshes peak on the transition midpoint, risers end exactly on the cut, reverse impacts peak on the cut); the layered hit (sub + body + transient + air tail); the silence pocket before the biggest hit; no sparkles or chimes on premium work (glints get muted air); SFX mono and centred, only the bed in stereo; and its library of proven sounds, from which only the Mixkit and CC0 files were used. |
| [kapishdima/soundcn](https://github.com/kapishdima/soundcn) | CC0 Kenney interface sounds (bloops, hover and glass ticks, counter ticks). Its Blizzard set is not CC0 and was not used. |
| [elevenlabs/skills sound-effects](https://github.com/elevenlabs/skills) | read as the generation fallback (SFX v3, prompt and duration control) for any moment no library sound fits; every moment found a real or CC0 sound, so nothing was generated and no credits were spent. |

Also read and set aside: Remotion's `add-sfx` (a maintainer workflow; its CC0 list is mostly meme sounds), vibe-motion/sound (Freesound MP3 previews only), procedural-sfx and owoevan sfx-skill (synthesis, which real-sfx rules out). The third-party scripts were not executed; their documented rules are implemented in `build/sfx_v2.py`, and the sounds are fetched as data by `build/sfx_fetch.py`.

## What you hear, beat by beat
- 0.2-1.0 s: real keystrokes on every typing burst (cut from a CC0 keyboard recording, 12 different strokes rotated); a hover tick as the cursor parks; a real mouse click on send.
- 2.2-3.3 s: a soft swipe as the prompt lifts, a quiet data-scan texture while the AI answer streams in, a soft tick as each row lands.
- 3.9 s: "Where's your brand?" lands on a swelling sub drum with an airy hit.
- 4.9-6.3 s: a riser and a building whoosh lift "Your Brand" and both cut at f173; five frames of near silence (the pocket); a layered landing hit at f178 (deep drum + sub + air transient); the #1 badge bloops; the check clicks.
- 7.6-10.5 s: a deep air whoosh peaks mid-scroll; the headline resolves on a tick; each platform's #1 bloops a semitone higher (three Kenney bloops alternated so it never machine-guns); faint ticks follow the pills' hover lift.
- 10.9-12.5 s: a lighter whoosh; a tick train follows the count and settles with a click and a little air on "+451%"; a glass tick as the trend line completes.
- 13.5-15.2 s: a long sweeping whoosh back to navy; line 2 of the H1 answers the question with the same swell (question and answer share a sound).
- 15.5-20 s: a reverse impact swells and cuts exactly on the logo frame; a layered logo hit (cinematic impact with an air tail + sub + transient), the biggest moment of the film; a soft swipe as the wordmark slides out; a tick on the CTA line, a light pop on the button, muted air under the light sweep. A steady dark room tone sits under everything at -54 dBFS.

## Numbers (final file and `audio/sfx_v2_report.json`)
- look.py: 20.00 s, G0 PASS, G2 PASS, G3 PASS (end hold 0.37 s, ends on the CTA sweep). Audio -14.3 LUFS integrated, -1.3 dBTP, LRA 8.4 LU, audible 99 % (first keystroke at 0.16 s), no flags.
- Mix checks: -15.3 LUFS through a 150 Hz high-pass (a phone speaker loses only ~1 LU, the hits are not sub-only); limiter at most 4.0 dB; hierarchy by momentary loudness: logo -9.1, landing -12.2, payoff -13.6 LUFS; 72 cues, none masked; pauses between gestures median 0.44 s, longest hole 1.11 s; quietest tenth 26.7 dB under the loudest 250 ms (reference reels: 21-26); 0 % digital silence; mono sum loses 0 dB.
- Against real-sfx's reference reels: 5-7 gestures per 10 s, below their 7-15, because the scrolls and builds run as long continuous gestures rather than many separate hits. Read as a description, not a fault: no hole is longer than 1.1 s.

## Listen list (the moments the numbers are least sure of: one pass on headphones, one on a phone speaker)
1. 0:00-0:01 typing: do the keystrokes sound like typing into the prompt, and sit under the picture rather than on top of it?
2. 0:05.5-0:06.4 the lift: does the 5-frame pocket before the landing read as intentional, and is the hit big without being harsh on a phone?
3. 0:08.5-0:09.5 the five #1 bloops: premium, or too playful?
4. 0:11.2-0:12.2 the counter: does the tick train feel tied to the number, or busy?
5. 0:15.6-0:17.2 reverse swell into the logo: is it the biggest moment without distortion, and is the air tail welcome under the end card?
Whole film: is the room tone noticeable? It should sit at the edge of hearing; say if it reads as a hum.

## Sound credits (no attribution required by any of these licences; kept for the record)
| File | Licence | Uses | Where |
|---|---|---|---|
| `mixkit__air-in-a-hit-2161.flac` | Mixkit Free License (via GFXER/sfx-library) | 5 | question air hit, landing: transient, +451% weight, payoff line 1, logo: transient |
| `mixkit__air-woosh-1489.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | light sweep (muted air) |
| `mixkit__cinematic-impact-echo-780.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | logo: body + air tail |
| `mixkit__cinematic-whoosh-fast-transition-1492.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | brand rises |
| `mixkit__cool-interface-click-tone-2568.flac` | Mixkit Free License (via GFXER/sfx-library) | 2 | row lands, +451% lands |
| `mixkit__data-scaner-2847.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | AI answer streams in |
| `mixkit__deep-air-woosh-2604.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | scroll to proof |
| `mixkit__deep-cinematic-subtle-drum-impact-549.flac` | Mixkit Free License (via GFXER/sfx-library) | 2 | question swell, payoff line 2: swell |
| `mixkit__drum-deep-impact-563.flac` | Mixkit Free License (via GFXER/sfx-library) | 2 | landing: body, payoff line 2: body |
| `mixkit__explainer-video-pops-whoosh-light-pop-3005.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | CTA button |
| `mixkit__fast-air-sweep-transition-168.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | line leaves |
| `mixkit__fast-small-sweep-transition-166.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | wordmark slides out |
| `mixkit__fast-swipe-zoom-2627.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | prompt lifts |
| `mixkit__futuristic-bass-hit-2303.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | logo: sub |
| `mixkit__long-sweeping-air-swoosh-167.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | scroll to the payoff |
| `mixkit__modern-click-box-check-1120.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | check mark |
| `mixkit__mouse-click-close-1113.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | send press |
| `mixkit__quick-air-woosh-2605.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | scroll to the number |
| `mixkit__reverse-cinematic-impact-trailer-784.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | letters converge (reverse) |
| `mixkit__short-bass-hit-2299.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | landing: sub |
| `mixkit__short-space-stutter-intro-riser-1144.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | riser into the lift |
| `cc0_keyboard-typing-3s.flac` | CC0 (via GFXER/sfx-library) | 18 | key |
| `cc0_tick-soft.flac` | CC0 (via GFXER/sfx-library) | 4 | counter tick |
| `kenney__drop-001.mp3` | CC0 (Kenney, via soundcn) | 1 | platform #1 (4/5) |
| `kenney__drop-002.mp3` | CC0 (Kenney, via soundcn) | 1 | platform #1 (2/5) |
| `kenney__drop-004.mp3` | CC0 (Kenney, via soundcn) | 4 | #1 badge (the spring), platform #1 (1/5), platform #1 (3/5), platform #1 (5/5) |
| `kenney__glass-002.mp3` | CC0 (Kenney, via soundcn) | 3 | row lands, pill lift, trend line completes |
| `kenney__hover-tick.mp3` | CC0 (Kenney, via soundcn) | 5 | cursor parks on send (hover), row lands, headline resolves, pill lift, CTA line |
| `kenney__tick-001.mp3` | CC0 (Kenney, via soundcn) | 3 | counter tick |
| `kenney__tick-002.mp3` | CC0 (Kenney, via soundcn) | 4 | counter tick |
| `kenney__tick-004.mp3` | CC0 (Kenney, via soundcn) | 1 | pill lift |
| `mixkit__cinematic-room-tone-3080.flac` | Mixkit Free License (via GFXER/sfx-library) | 1 | the bed, 0-20 s at -54 dBFS |

Mixkit Sound Effects Free License: free for commercial and client projects; the raw files may not be redistributed, so `build/sfx_lib/` is git-ignored and rebuilt by `build/sfx_fetch.py`.

## Client message (v2, ready to send)

> Hi [name], here's a first cut of a 20-second motion piece for OmniGro AI (16:9, for LinkedIn, YouTube and your site).
>
> The idea: a customer asks AI for a recommendation and the answer lists other brands. Then your triangle lifts their brand to #1, your pilot results back it up, and the OmniGro logo forms out of the motion. Every number and claim is taken from your site (latest pilot, June 2026), and the fonts, colours and hero art are yours.
>
> The sound is effects only, no music, so a voiceover or your own track can go on top later. Send any changes in one message, with the time in the video for each.

## Voiceover for v2 (ElevenLabs, ready to paste)

42 words (~2.7 a second), one line per beat, each heard just after its words appear, and silent through the two big hits (the landing at 0:05.9, the logo at 0:16.6). House voices: neutral accent, no whispering, no announcer hype. Put ONE "Voice:" paragraph into Voice Design (or use it to pick a library voice), and only the script lines into the text box. Test line 3 first, then three full takes.

Option A, deep male:
```
Voice: male, 30s, deep, rich bass voice with a slight gravel, like a big campaign trailer for a tech brand. Calm, confident and controlled, never shouting. Deliberate pacing with weight on each line: dry and knowing on "Where's your brand?", quiet certainty on "OmniGro puts it on top.", real warmth on "Get your brand recommended by AI." Neutral international English accent. Clean studio sound, close to the mic, no reverb, no whispering, no announcer hype. Say "OmniGro" as "OM-nee-groh". Leave a clear pause at each line break.
```

Option B, warm female:
```
Voice: female, late 20s, soft, warm and feminine, smooth and velvety with a slight breathy warmth. Elegant and confident, like a premium brand campaign but friendly, not cold. Medium-low pitch, unhurried, a gentle smile in the voice. Quietly knowing on "Where's your brand?", a touch brighter on "OmniGro puts it on top." and "Get your brand recommended by AI." Neutral international English accent. Clean studio sound, close to the mic, no reverb, no whispering, no announcer hype. Say "OmniGro" as "OM-nee-groh". Leave a clear pause at each line break.
```

Script (text box):
```
Your customers ask AI.

It names your competitors.

Where's your brand?

OmniGro puts it on top.

Our latest pilot: number one on every major AI platform.

Get your brand recommended by AI.

Your free AI visibility report: omni-gro A I dot com.
```

| Line | Starts | Sits on |
|---|---|---|
| Your customers ask AI. | 0:00.4 | the question typing |
| It names your competitors. | 0:02.4 | the competitor rows landing |
| Where's your brand? | 0:04.0 | the same words on screen; ends by 0:05.6 so the silence pocket stays clear |
| OmniGro puts it on top. | 0:06.2 | right after the #1 badge |
| Our latest pilot: number one on every major AI platform. | 0:08.2 | the "Ranked #1" headline; ends as +451% lands at 0:12.0 |
| Get your brand recommended by AI. | 0:14.2 | the H1 building; ends before the logo hit at 0:16.6 |
| Your free AI visibility report: omni-gro A I dot com. | 0:17.0 | the end card; ends by 0:19.8 |

The voice rests 0:12-0:14 so the count-up and its ticks carry +451%. To say the number too, add "And four hundred and fifty-one percent more organic clicks." after line 5 (fits only with a brisk read).
Mixing it in (v3): place each line by its first syllable on the times above; SFX dipped about 9 dB under speech (real-sfx voice-safe) and no big hit under a word (GFXER); the voice at least 8 dB above the SFX while it speaks; master -14 LUFS, -1 dBTP; deliver `omnigro-promo-16x9-v3-vo.mp4` plus an .srt.

---

# OmniGro AI / promo-20s / v1 (music + synthesized SFX, superseded by v2)

**Idea:** "Be the answer." A customer asks AI what to buy. The answer names three competitors. OmniGro's coral triangle lifts "Your Brand" up through the list to #1, then the film proves it with the real pilot, says their H1, and the coral words collapse into the coral triangle while the blue one rises in front to form the mark. It is theirs because the lifting triangle is their own logo geometry (coral rising above blue, "Gro"), on their own hero art, in their copy, colours, fonts and UI.

**Beats**
1. 0.0-2.0 s: a customer asks AI for a recommendation (their input style, with the site's rotating "ask-ai" border).
2. 2.0-5.2 s: the answer unfolds out of the prompt and lists competitors: "Where's your brand?"
3. 5.2-7.6 s: the coral triangle lifts "Your Brand" up through the list to #1 (the one spring: the #1 badge).
4. 7.6-10.8 s: the page scrolls on their wave divider into the proof: "Ranked #1 across every major AI platform" with the five platforms.
5. 10.8-13.5 s: "+451% organic clicks" counts up as the trend line climbs. The caption "From our latest pilot, June 2026" stays put across both proof beats.
6. 13.5-16.2 s: back to the navy hero: "Get your brand recommended by AI".
7. 16.2-20.0 s: the coral words converge into the mark; "OmniGro AI"; "Get your free AI visibility report"; the coral button "omnigroai.com".

**Real (from omnigroai.com, captured 27 Nov 2026):** every claim and number ("Ranked #1 across every major AI platform", ChatGPT, Gemini, Claude, Google AI Mode and Perplexity each #1, "+451% organic clicks", "From our latest pilot, June 2026"), the H1, the free-report offer, the URL, colours (#08104d, #3241e4, #ef5d50, #ecf2fe), fonts (Bricolage Grotesque, Inter), the hero art (`hero-bg.webp`), the sparkles icon, the button and pill styles, the wave divider, the caret timing and the rotating border.
**Logo:** the mark is rebuilt in vector from `logo_only.png` so it can animate (two identical triangles, blue offset down 35%). Checked against the file: 99.7% coverage agreement, every difference within 2 px of an edge on the 2048 px source, inks exact. The wordmark is the site header lockup (Bricolage ExtraBold, "AI" in coral, gap 0.3 x mark height).
**Illustrative:** the typed question ("Best skincare brand for sensitive skin?"), "Your Brand" and "Competitor A/B/C" (the placeholder names their own dashboard uses), the trend line's shape (no axis values).

**Music:** original bed synthesized for this film (`build/sound.py`): 120 BPM, A major, I-I-vi-IV / I-V-vi-IV, logo on a free-time A chord. No samples or third-party audio, so no licence limits on any platform, including paid ads. **Voice:** none (optional script below).
**SFX:** five families, synthesized and placed on the timeline's own cue frames (`audio/cues.json`): keys and clicks, ticks, whooshes on the scrolls, low hits (line, landing, logo), one pop (#1 badge), and a reverse swell into the logo.

**look.py (final file):** length 20.00 s, G0 PASS, G2 PASS (no flat frames), G3 PASS (end hold 0.37 s: the film ends on the light sweep across the CTA button, with the lockup resolved for about 0.9 s), 0 hard cuts (one continuous take), no frozen stretch over 0.6 s. Audio: -14.0 LUFS integrated, -1.2 dBTP, LRA 5.0 LU, audible 100%, no dropouts, no silent tail. Motion 2.4/255, below the human band (4.4-9.8): the holds carry constellation drift, rising motes, camera creeps, the moving trend head and the CTA sweep, and the film is deliberately one calm take.
**Checks by eye:** smallest must-read text 40 px (caption) at 1080p; everything inside title safe (pill row 117-1803 px); one hero per frame; no page chrome; no crossfades; phone-width test (390 px) keeps every headline, the number, the logo and the URL legible (the pilot caption gets small there, as landscape always does on a phone).

**Frames** (`out/omnigro-promo-16x9-v1-sheet.jpg`)
- 0.6 s: the prompt pill types the question over the navy constellation, platform chips under it.
- 1.9 s: question complete, the cursor parked on send.
- 3.1 s: the question rises to the top as the answer card unfolds beneath it; rows landing.
- 4.4 s: "Where's your brand?" over the softened card.
- 5.6 s: "Your Brand" shoots up into the card, motion-blurred, competitors dropping a slot.
- 6.9 s: "Your Brand #1" with the coral badge and check; the camera has pushed in.
- 8.1 s: the light section rises on the wave, the headline building as it arrives.
- 9.4 s / 10.6 s: "Ranked #1 across every major AI platform", five pills with #1 badges, the pilot caption.
- 11.9 s / 13.1 s: "+449%" then "+451%" "organic clicks", the trend line climbing to the corner.
- 14.4 s / 15.6 s: back on navy, "Get your brand recommended by AI" builds word by word (the cover frame).
- 16.9 s: the coral triangle has formed and the blue rises in front, a coral glow behind.
- 18.1 s / 19.4 s: the full lockup, "Get your free AI visibility report", the coral "omnigroai.com" button with its sweep.

**Still to improve (honest list)**
- The music and SFX were checked by spectrum, loudness and cue timing, not by ear. Listen once on phone speakers and once on headphones before sending; a licensed track can replace the bed in one step.
- The free report sits in the site's "Limited time offer" section. Confirm it is still running before this is posted.
- Landscape only, as asked. A 9:16 or 1:1 cut needs re-composing (pills in 3 + 2 rows, the payoff on three lines), not cropping.
- If it feels slow on a second watch, the two proof holds can each lose 6 frames and the payoff gets them.

---

## Client message (ready to send)

> Hi [name], here's a first cut of a 20-second motion piece for OmniGro AI (16:9, for LinkedIn, YouTube and your site).
>
> The idea: a customer asks AI for a recommendation and the answer lists other brands. Then your triangle lifts their brand to #1, your pilot results back it up, and the OmniGro logo forms out of the motion. Every number and claim is taken from your site (latest pilot, June 2026), and the fonts, colours and hero art are yours.
>
> Have a look and send any changes in one message, with the time in the video for each. Once you're happy we can also cut a vertical version for Reels and Shorts.

## Optional voiceover (v1 draft, superseded by the v2 voiceover above)

About 2.3 words a second, one line per beat. Paste the "Voice:" paragraph into ElevenLabs Voice Design (or use it to pick a library voice), and only the lines into the text box.

```
Voice: male, 30s, deep, rich bass voice with a slight gravel, like a big campaign trailer. Calm, confident and controlled, never shouting. Dry and knowing on "Where's your brand?", real warmth on "Get your brand recommended by AI." Clean studio sound, close to the mic, no reverb, no whispering. Say "OmniGro" as "OM-nee-groh" and "omnigroai.com" as "omni-gro A I dot com". Leave a clear pause at each line break.

Your customers ask AI what to buy.

It names your competitors. Where's your brand?

OmniGro puts it at the top.

In our latest pilot: number one on every major AI platform.

And four hundred and fifty-one percent more organic clicks.

Get your brand recommended by AI.

Get your free AI visibility report at omni-gro A I dot com.
```

For the warm female house voice, swap the first paragraph for the female prompt in `references/sound.md` and keep the last three sentences.
