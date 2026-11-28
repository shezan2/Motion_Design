# Nick R.L. / intro / v1

**Idea:** his own Yishun result told with one shape. A grey ring of 180 days becomes a gold arc a sixth as long, "Sold in 1 month". That ring becomes his four promises (Right advice, strategy, execution, home), and the house opens into his name card. It belongs to Nick: his case, his tagline, his icons, his face and number.

**Beats:**
1. Hook (0-2.8 s): a listing that sat for months. Counter to 180, "days on the market", six month marks.
2. Turn (2.8-6 s): the difference. Gold arc of one month, "Sold in 1 month.", Blk 123 Yishun · 4-room HDB. The one big hit, and the light turns warm.
3. Promise (6-11.6 s): how, in his words. Target and arrow thunk, knight and chess clack, check and pen tick, house and key in the lock.
4. Reveal (11.6-16 s): who. The house outline becomes his card, and he rises into the doorway light. Name, "Your trusted agent", title, PropNex, chips.
5. CTA (16-20 s): what to do. Scale cut, gold "WhatsApp 9859 9857" pill, the cursor presses it, CEA details on the card.

**Real** (all from his public channels, read 28 Nov 2026):
- Copy: "days on the market" and "Sold in 1 month" for Blk 123 Yishun, 4-room (his YouTube title: "From 6 Months on the Market to SOLD in Just 1 Month @ Blk 123 Yishun | 4Rm"); "Right Advice / Strategy / Execution / Home" and "Your Trusted Agent" (his thumbnail bar); "Associate Division Director" and PropNex (banner, PropertyGuru); "20+ years" (PropertyGuru: "over 20 years"); "HDB · Condo · New launch" (YouTube description).
- Phone 9859 9857; CEA R002622D; agency licence L3008022J (PropertyGuru snippet).
- Photo cut out from his YouTube banner. PropNex logo is the official file from propnex.com.

**Illustrative / converted:**
- "180 days" is the counter's version of his "6 months". The six month marks keep it honest, but confirm the exact period with Nick.
- The icons are Tabler line icons (MIT), matching the pictograms on his thumbnails, not his own files.
- Colours and fonts are matched from his banner and thumbnails (navy, gold, Montserrat, Cormorant Garamond). He has no formal brand guide that I could find.

**Music:** none (brief: SFX only).
**SFX:**
- Clipwing real-sfx method plus the official ElevenLabs sound-effects skill (`eleven_text_to_sound_v3`). 11 sound kinds with 4 takes each, picked by measurement, plus a 22 s room-tone bed at -52 dBFS.
- 36 cues: ticks, whooshes, one hit, object foley (arrow, chess, pen, key), click, shimmer. Real-sfx texture layer in the long hold.
- Licence: generated under the account's ElevenLabs plan (commercial use depends on that plan; check before Nick runs paid ads).

**look.py** (final master, `out/look-final`):
- Length 20.00 s. G0 PASS, G2 PASS, G3 PASS (end hold 1.20 s, final shot 4.0 s = 20 %).
- One cut at 16.00 s (scale cut), landing on a sound onset.
- Audio: -15.8 LUFS integrated, LRA 10.3 LU, true peak -1.4 dBFS, no flags.
- Motion 0.4/255: below the human band. The film is dark and calm, with small elements.

**real-sfx reference** (`refstyle.py`, nine finished SFX reels): 10 of 12 measures inside the range.
- Inside: gestures per 10 s 10.5, longest gap 2.1 s, level spread 11.6 dB, low-end share 76 %, digital silence 0 %, loudness -15.8 LUFS (references -15.9 to -14.3).
- High: median gap 0.90 s (it breathes a little more than the references).
- Low: floor (the bed sits at real-sfx's human-tested level).

**Frames** (look sheet):
- 0.6 s and 1.9 s: the counter rolling to 179 in the notched grey ring.
- 3.1 s: gold "Sold" lands in the ring. 4.4 s: "Sold in 1 month." with the case line.
- 5.6 s: the gold ring in flight.
- 6.9 s, 8.1 s, 9.4 s, 10.6 s: target "Right advice.", knight "Right strategy.", check "Right execution.", house "Right home.".
- 11.9 s: card outline completing.
- 13.1 s to 15.6 s: the card builds and holds (Nick, name, tagline, title, chips, PropNex badge, legal line).
- 16.9 s: scale cut with the WhatsApp pill (cover frame).
- 18.1 s and 19.4 s: the cursor parks past the number and presses.

**Phone test:** at 844 px wide every card line is readable, fine print included.

**Still to improve (honest):**
- The ring's flight into the target (about 5.6 s) reads for a frame or two like a loading spinner. A short trail would fix it.
- The card's reading hold (13.2-16.0 s) only creeps. A slow parallax between Nick and the card would add life.
- Loudness is 1.8 dB under the Ozen -14 LUFS target (inside the SFX-reel range). Forcing -14 needs about 8 dB of limiting on the "Sold" hit.
- A higher-resolution original headshot and his real logo file would replace the banner cut-out at onboarding.
- No 9:16 or 1:1 cut yet (the brief asked for landscape only). The builder is ready for a portrait re-compose.
