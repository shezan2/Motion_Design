# OmniGro AI / promo-20s / v1

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

## Optional voiceover (for a later voiced version)

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
