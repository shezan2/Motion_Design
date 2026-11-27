# OmniGro AI / promo-20s / STATE

| Field | Value |
|---|---|
| Client | OmniGro AI (omnigroai.com), Singapore. GEO / AEO / AI SEO agency |
| Video | 20 s brand promo, 16:9 1920x1080, 30 fps (600 frames) |
| Plan | spec / onboarding piece (bill as one-off up to 30 s if needed) |
| Version | v1 (first draft) |
| Revision rounds used | 0 |
| Engine | HTML + deterministic JS timeline, rendered frame by frame in headless Chromium (Playwright), 4-subframe shutter blur, ffmpeg encode. Chosen over Lottie for the site's real CSS look: variable Bricolage Grotesque, glass, glows, conic borders |
| Sound | original synthesized music bed (120 BPM) + 5 kinds of SFX, no voiceover |

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
