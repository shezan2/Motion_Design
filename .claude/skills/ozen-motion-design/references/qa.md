# Review: gates, the client-ready checklist and how to look

## Contents
1. Gates · 2. How to look · 3. Client-ready checklist · 4. AI tells and their fixes · 5. Fix order · 6. NOTE.md

## 1. Gates
Computed gates come from `scripts/look.py`; quote its numbers, never estimate them. A fail gets fixed, not explained away.

```bash
python3 scripts/look.py draft.mp4 --out look --expect 30                  # while iterating
python3 scripts/look.py final.mp4 --out look-final --expect 30 --expect-audio   # before delivery
```

| Gate | Pass | Checked by |
|---|---|---|
| G0 render exists | decodes, not blank, moves, length matches the plan, audio present and not silent | look.py |
| G1 proof readable | text that must be read meets the size floor in `craft.md`; product UI magnified, not a small card on a void | your eyes on `look/sheet.jpg` and stills |
| G2 no empty frame | no run of more than 3 flat frames | look.py |
| G3 short ending | end hold 0.6-1.4 s; the last shot 25% of the film or less | look.py |
| G4 one hero per frame | two panels only if one is at least twice the other or the camera moves between them | your eyes |
| G5 no page chrome | no corner labels, counters, timecodes, header or footer bars, kicker above headline, left headline block with media beside it | your eyes on the outer 12% of every frame |
| Audio | about -14 LUFS, true peak -1 dBTP or lower, no silent tail, no dropouts | look.py audio block |

look.py also prints the film's mean motion. Human-made films sit around 6.8 (IQR 4.4-9.8); treat it as a question (too busy to breathe? too still to exist?), not a gate.

## 2. How to look
1. Open `look/sheet.jpg` and write one sentence per frame: what is on screen, what the hero is, whether it would pass as a slide. Writing it down stops you from approving what you expected to see.
2. Open `look/mid.jpg` and `look/strips.jpg` (frames just before and across each cut): broken transitions hide there.
3. **Thumbnail test:** would any frame work as the cover? If none would, the hero moment is missing.
4. **Cover-the-logo test:** hide the logo; could a competitor run this film?
5. **Phone test:** watch at real speed at phone size, once with sound and once muted. A still at phone width: `ffmpeg -ss 4.2 -i final.mp4 -frames:v 1 -vf scale=390:-2 phone.png`.
6. **Reading test:** read every line aloud while it plays. If you can't finish before it leaves, add hold time or cut words.
7. **Fresh-eyes pass:** before delivering, watch as the client would, start to finish, without stopping.

## 3. Client-ready checklist
**Facts**
- [ ] Every price, date, name, URL and handle matches the brief character by character; prices written S$70.
- [ ] Nothing invented: no stats, testimonials, client logos, user counts, scarcity or fake states ("Live now" only if it is live).
- [ ] Spelling and grammar checked on every frame, including small UI text.

**Brand**
- [ ] The client's logo file is used, never redrawn; clear space respected.
- [ ] Colours match the hex values; fonts are theirs or a stated match.
- [ ] The voice of the copy sounds like them.

**Picture**
- [ ] Every must-read word is above the size floor and inside the safe zone, in every format.
- [ ] No subject cut by a crop in any format.
- [ ] One hero per frame; one accent with one meaning.
- [ ] No crossfades between scenes; seams cut mid-motion; 2-3 transition types.
- [ ] No dead frames; holds match the reading time; the payoff gets its time.
- [ ] The length is within the plan's cap (a 30 s plan means 30.0 s or less).
- [ ] The ending is short (0.6-1.4 s hold) and not a website footer.

**Sound**
- [ ] About -14 LUFS, true peak -1 dBTP or lower, nothing clipped.
- [ ] The voice sits at least 8 dB above the bed while it speaks; every word is clear.
- [ ] Hits land on their frames; no silent tail; no digital-silence dropouts.
- [ ] The music licence covers the client's use, and is recorded in `NOTE.md`.

**Files**
- [ ] Every ordered format, named `<client>-<video>-<ratio>-v<N>.mp4`.
- [ ] Cover JPGs; `.srt` when voiced; a WhatsApp-size preview if sending by WhatsApp.
- [ ] `STATE.md` updated: version, rounds used, what changed.

## 4. AI tells and their fixes
| Tell | Fix |
|---|---|
| Every element fades in | entrances move: offset, scale or blur clearing; opacity only as a helper |
| One ease on everything | per-role curves (`craft.md` section 3) |
| Everything bounces | at most 1 move in 8 leans late; one spring per film |
| Scenes crossfade | cut on motion, morph, or carry an object |
| Headline typed with a caret | blur-in word build; typing only inside a product field |
| A big number centred over a small label, invented | only real numbers, inside the UI or tied to a cause |
| A small rounded card on an empty ground | magnify the UI; build the ground (light, depth, texture) |
| The same glow under every scene | one light logic that changes with the mood |
| Labels and counters in the corners | delete them |
| Each beat animated the same way | importance budget: connective, supporting, the point |
| The logo fades in at the end over a footer of links | the logo resolves from the motif; hold 0.6-1.4 s |
| Text re-centres every time a word lands | fixed slots planned from the final line |
| Long static holds | one living thing on every hold; story instead of filler |
| Copy full of "unlock", "elevate", "seamless" | the client's own words, then cut half |

## 5. Fix order
1. Anything untrue or broken (wrong facts, crashes, black frames, text off screen).
2. The idea (does every beat buy something; is it this brand's film?).
3. The seams (handoffs, carried objects, direction).
4. Hierarchy and scale (one hero, readable type).
5. Timing (holds, rhythm, the pause before the climax).
6. Surface and finish (light, texture, shadows).
7. Sound polish.

Two or three honest passes, then deliver. Polish on a broken idea is wasted.

## 6. NOTE.md
Keep it short; it is for Shezan, not the client.
```
# <client> / <video> / v<N>
Idea: <one line> - why it is this brand's
Beats: <one line each: what it buys>
Real: <captured UI, client photos, copy from the brief>
Illustrative: <rebuilt UI, generated surfaces, placeholder data and why>
Music: <track, source, licence>   Voice: <voice, settings>
look.py: length <s>, G0 <pass>, G2 <pass/fail + times>, G3 end hold <s>, final shot <%>, <LUFS> LUFS, <dBTP> dBTP
Frames: <one sentence per sheet frame>
Still to improve: <honest list>
```
