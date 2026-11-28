# OmniGro AI / promo-20s / STATE

| Field | Value |
|---|---|
| Client | OmniGro AI (omnigroai.com), Singapore. GEO / AEO / AI SEO agency |
| Video | 20 s brand promo, 16:9 1920x1080, 30 fps (600 frames) |
| Plan | spec / onboarding piece (bill as one-off up to 30 s if needed) |
| Version | **v3 delivered 28 Nov 2026** (voiced: ElevenLabs take + SFX): `out/omnigro-promo-16x9-v3-vo.mp4` + `.srt`; v2 (SFX only) and v1 (music) kept |
| Revision rounds used | 0 |
| Engine | HTML + deterministic JS timeline, rendered frame by frame in headless Chromium (Playwright), 4-subframe shutter blur, ffmpeg encode. Chosen over Lottie for the site's real CSS look: variable Bricolage Grotesque, glass, glows, conic borders |
| Sound | v2: sound effects only (real recorded Mixkit + CC0 library sounds, no music), built with the Clipwing real-sfx and GFXER sfx-library methods; v1 had a synthesized music bed |

## Brand sheet (from the live site, 27 Nov 2026)
- **Ground:** navy `#08104d` with their hero art (`hero-bg.webp`: a blue constellation with faint triangle marks) under a navy gradient. Light sections `#ecf2fe` with white cards (border `#e8edf8`, radius 20, soft navy shadows).
- **Ink:** navy `#08104d` on light, white on navy. Body grey-navy.
- **Accents:** blue `#3241e4` = AI and product (buttons, sparkle icon, "AI Search"); coral `#ef5d50` = the result and the action ("Recommended by AI", "#1", "+451%", "your brand", the CTA button).
- **Type:** Bricolage Grotesque (H1 800, -0.02em, leading 1.05; H2 700, -0.02em) + Inter (body). Both open-licensed Google Fonts, used as-is (variable files in `brand/fonts/`).
- **Logo:** `logo_only.png` = two identical triangles, coral on top and blue in front, offset down by 35% of the height (an upward arrow: "Gro"). Inks are exactly `#ef5d50` and `#3241e4`. Site lockup = mark + "OmniGro AI" in Bricolage 800, "AI" in coral. (`logo.png`, a slab-serif lockup, is only used as their og:image; the film uses the site header lockup.)
- **Core control:** the input ("Your website / yourbrand.com / Submit") with the Lucide sparkles icon in an indigo circle; platform chips ChatGPT, Claude, Perplexity, Gemini.
- **Success moment:** "#1" badges per platform; "AI Visibility Score 90%, from 0%"; "+451% organic clicks".
- **Signature motion on the site:** the rotating conic "ask-ai" border (coral → blue → navy, 6 s a turn), caret blink (1.25 s), fade-up reveals (0.6-0.8 s, 20-24 px), card lift on hover, the S-wave divider under the hero.
- **Voice:** direct and confident ("4 Steps to Rule AI Search", "Old SEO is fading. GEO is the future.").
- **Never:** invented stats, emoji-heavy or robot clichés, third-party AI logos (the site itself uses names and emoji only).

## PAGE
- **Problem:** customers now ask ChatGPT, Gemini, Claude and Perplexity what to buy, and the answer names other brands ("When AI doesn't know your brand, customers can't find you").
- **Audience:** founders and marketers of consumer brands; LinkedIn, YouTube, website.
- **Goal:** get the free AI visibility report at omnigroai.com.
- **Emotion:** a jolt ("we're not in the answer"), then confidence ("they've done it, #1 everywhere").
- **The one true thing:** OmniGro AI gets your brand recommended by AI, with a real pilot to prove it.

## Three ideas
1. **Be the answer** (UI documentary of one question): a customer asks AI for a recommendation; the answer lists competitors; OmniGro's coral triangle lifts "Your Brand" to #1; proof from the pilot; the triangle becomes the logo.
2. **The 10 blue links fade** (chaos to order): a page of search links dissolves into the constellation, which converges into the triangle mark. Their "Old SEO is fading" line.
3. **The rising triangle** (transformation chain): the coral triangle travels as caret, rank arrow, chart peak, then rises above the blue to form the mark.

**Pick: 1, carrying 3's triangle.** The question-and-answer is exactly what OmniGro sells, and the coral triangle that lifts your brand is their own logo part, so the idea fails the cover-the-logo test for anyone else. The film is a continuous downward scroll through their site's world: navy (the question) → light (the proof) → navy (the promise and the mark), joined by their own wave divider.

**Carried object:** coral = your brand winning. The coral triangle lifts the row, coral "#1" badges multiply, the coral words "recommended by AI" collapse into the coral triangle, and the blue triangle rises in front to complete the mark.
**The current:** up (rank up, growth, scrolling down the page). Content always leaves upward and arrives from below.

## Beat sheet (30 fps; 120 BPM, bars every 60 f)
| # | Frames | Role | Imp. | Buys: the viewer... | Copy | Picture (text covered) | In → out | Handoff | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0-60 | hook | 2 | sees a customer asking AI what to buy | typed: "Best skincare brand for sensitive skin?" (illustrative) | a glass prompt pill with the site's rotating coral/blue border over the navy constellation; platform chips under it; a cursor presses send | present at f0 → press f58 | the pill rises and becomes the question bubble | key ticks, click |
| 2 | 60-158 | problem | 2 | sees AI recommend other brands | "Top picks for sensitive skin" / Competitor A, B, C; then "Where's your brand?" | an answer card unfolds from the pill, three rows land; the card defocuses behind the line | container morph → line holds | the card stays | whoosh, 3 ticks, soft low note |
| 3 | 154-232 | turn | **3** | believes OmniGro puts their brand on top | "Your Brand" #1 | the coral triangle lifts a "Your Brand" row up through the list; competitors drop a slot; the #1 badge springs (the film's one spring) | rise f160-180 → hold 1.7 s | the page scrolls up | riser, 0.25 s dip, hit, pop |
| 4 | 228-324 | proof | 2 | sees it is real: #1 on every major AI platform | "Ranked #1 across every major AI platform"; pills ChatGPT, Gemini, Claude, Google AI Mode, Perplexity; caption "From our latest pilot, June 2026" | the light section rises on their wave; five white pills pop in with coral #1 badges | scroll → word build → hold 2 s | caption stays put | whoosh, groove in, ticks |
| 5 | 322-408 | proof | 2 | sees the business result | "+451%" / "organic clicks" | a giant coral number counts up as a blue trend line climbs | scroll → count lands f360 → hold | the page scrolls up | whoosh, tick on land |
| 6 | 408-482 | payoff | 2 | hears the promise in the brand's own words | "Get your brand / recommended by AI" | the navy hero returns on the wave; their H1, white and coral | scroll → word build → hold 1.3 s | the coral words | whoosh, chord |
| 7 | 482-600 | brand + CTA | 2 | knows who and where | "OmniGro AI" / "Get your free AI visibility report" / "omnigroai.com" | coral letters converge into the coral triangle, the blue triangle rises in front: the logo; wordmark wipes in; CTA under it | converge → lockup → hold 1.33 s | end | whoosh, logo hit + shimmer |

Checks: 600 frames = 20.0 s. One importance-3 beat of seven. CTA beat 3.9 s (19.5%), end hold 1.33 s. No hard cuts: one continuous take. Transition types: container morph, scroll on the wave divider, convergence.

## Handoffs
| Seam | A's last frame | B's first frame | Carrier | Cut |
|---|---|---|---|---|
| 1 → 2 | pill centred, send button squashed | pill rising (glide), card growing from its bottom edge | the prompt pill | none |
| 2 → 3 | line held, card soft | line accelerating up and out; card sharpening; row entering from the bottom edge | the card | none |
| 3 → 4 | navy section accelerating up | light section rising at the same speed behind the wave | the scroll | none |
| 4 → 5 | headline and pills leaving up | stat block arriving from below at the same speed | the fixed caption | none |
| 5 → 6 | light section leaving up | navy section rising on the wave | the scroll | none |
| 6 → 7 | coral words accelerating into one point | the coral triangle growing from that point | coral | none |

## Real or illustrative
- **Real (from omnigroai.com):** every claim and number (#1 on ChatGPT, Gemini, Claude, Google AI Mode, Perplexity; +451% organic clicks; "From our latest pilot, June 2026"), the H1, the offer, the URL, colours, fonts, logo, hero art, UI styles and motion.
- **Illustrative:** the typed question, "Competitor A/B/C" and "Your Brand" (the site's own placeholder names from its dashboard), the trend line shape (no axis values).

## Decisions
- 27 Nov: landscape only, as asked. The 9:16 can be re-composed later (pills stack, line breaks change).
- 27 Nov: no third-party AI logos; platform names as text, like the site's step-1 chips.
- 27 Nov: music is an original synthesized bed (no licence question). A licensed track can replace it on request.

## v1 build log (27 Nov)
- Style frames first, then a fast draft (no motion blur) through `look.py`; fixed: S4/S5 not centred, rows pushed in the wrong order during the climb, "+45 1%" digit gaps (now Bricolage tabular figures), the answer card appearing above the prompt (it now hangs off the pill and unfolds with it), an empty mid-scroll frame between S4 and S5 (scroll cut from 1000 to 760 px, the number fades in while it scrolls).
- Holds were too still (look.py: two frozen 1.5 s stretches). Added rising data motes and faster drift on the navy hero art, camera creeps on S4 and S5, the trend head keeps travelling through its hold, one hover-lift wave across the pills (the site's card hover), a living wave edge.
- G3 failed twice (end hold 2.3 s, then 2.03 s): small CTA text never registers on look.py's 96x54 area-averaged frame. Fix: the URL became the site's coral button with one light sweep across it (the wordmark shine was dropped so there is still only one sweep). G3 now passes.
- Mark rebuilt in vector for the animation, verified against `logo_only.png` (99.7% coverage agreement, edges only).
- Sound: first mix had the sub 13 dB above the musical body (thin on phones); rebalanced (harmonic bass, warmer louder pad, knock on the kick, body on the hits). Final -14.0 LUFS, -1.2 dBTP.
- Grain: temporal strength 2 (strength 4 made a 121 MB file); kills the faint banding on the lavender ground. Master 14.8 MB.

## Files
| File | What |
|---|---|
| `out/omnigro-promo-16x9-v1.mp4` | master, 1920x1080, 30 fps, H.264 CRF 16, AAC 320k 48 kHz, -14 LUFS |
| `out/omnigro-promo-16x9-v1-preview.mp4` | 720p WhatsApp preview (1.7 MB) |
| `out/omnigro-promo-16x9-v1-cover.jpg` | cover frame (the payoff, f470) |
| `out/omnigro-promo-16x9-v1-sheet.jpg` | look.py contact sheet |
| `NOTE.md` | internal note, client message, optional VO script |
| `build/film.html` | the whole film: stage, styles, timeline (`T`), `FILM.render(t)`; open `build/film.html?play` through a local server to preview |
| `build/render.cjs` | stills, sub-frame PNG sequence, cue export (Playwright + ffmpeg) |
| `build/sound.py` | music + SFX + master from `audio/cues.json` |

## How to rebuild (from this folder)
```bash
node build/render.cjs still 0,180,470,590 /tmp/stills            # check frames
node build/render.cjs cues audio/cues.json                          # SFX cue list from the timeline
SUB=4 JOBS=3 node build/render.cjs frames /tmp/frames              # 600 frames, 180-degree shutter blur (~4 min)
SUB=4 node build/render.cjs frames /tmp/frames 545 600              # re-render only a range after an edit
python3 build/sound.py                                              # audio/mix.wav
ffmpeg -framerate 30 -i /tmp/frames/f%04d.png -i audio/mix.wav -map 0:v -map 1:a -vf "noise=c0s=2:c0f=t" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -crf 16 -preset slow -c:a aac -b:a 320k -ar 48000 \
  -movflags +faststart -shortest out/omnigro-promo-16x9-v2.mp4
python3 <skill>/scripts/look.py out/omnigro-promo-16x9-v2.mp4 --out look --expect 20 --expect-audio
```
Copy and numbers live in `build/film.html` (`QUERY`, the headline spans) so a change is one edit plus a partial re-render. Never overwrite v1: the next delivery is v2.

## v2 (27 Nov): SFX only
- Shezan: "no music just sound effects and for sound effects use the best github skills out there". Not a client revision round (internal, before sending).
- Taste lesson (for the skill's `references/taste.md`): 2026-11-27, OmniGro promo: asked for no music and SFX built with the best GitHub SFX skills. Lesson: offer an SFX-only cut by default for SaaS promos, built from real library sounds, not synthesis.
- Researched and read: Clipwing real-sfx, GFXER sfx-library, soundcn (Kenney CC0), ElevenLabs sound-effects, Remotion add-sfx, vibe-motion/sound, procedural-sfx, owoevan sfx-skill. Used: real-sfx (method, levels, anchoring, bed, checks), GFXER (pick table, lead frames, layering, pocket, licence-safe Mixkit/CC0 sounds), soundcn (Kenney CC0 UI sounds). Their scripts were not run (the session's safety check blocks running fetched third-party code); their rules live in `build/sfx_v2.py`.
- Rounds of the mix: (1) loudness fell to -16.6 because peaks set the level; (2) the send click hit the leveller trap and the payoff out-shouted the logo: fixed with a bus compressor, gains, -14.3 LUFS; (3) long tails merged everything: added a 5-frame silence pocket before the landing, shorter question swell and logo tail; (4) two holes at bed level: hover tick on the cursor park and a tick on the trend line completing (real picture moves); five same-source bloops alternated; masked push ticks removed.
- Rebuild: `python3 build/sfx_fetch.py` then `python3 build/sfx_v2.py`, then `ffmpeg -i out/omnigro-promo-16x9-v1.mp4 -i audio/sfx_v2_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest out/omnigro-promo-16x9-v2.mp4`.

## v3 (28 Nov): voiced
- Shezan generated the ElevenLabs take from the v2 voiceover prompt (`audio/vo/omnigro-vo-take1.mp3`). Placed by `build/vo_v3.py`; the voiced picture is `film.html?cut=vo` (render with `CUT=vo`), which differs from v2 only in frames 246-284 (pilot caption earlier) and 510-599 (end card a second earlier).
- Fit edit: last line trimmed to the URL (the full line does not fit after the logo hit in 20 s). Line 5 at 1.04x.
- Rebuild: `python3 build/vo_v3.py`; frames: copy the v2 frames and `CUT=vo SUB=4 node build/render.cjs frames <dir> 246 285` and `... 510 600`; encode like v1 with `audio/vo_v3_mix.wav`.
