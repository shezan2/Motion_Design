# Sound: music, SFX and voiceover

## Contents
1. Defaults · 2. Music · 3. SFX · 4. Voiceover (script, ElevenLabs prompts, placing the take) · 5. Mixing targets · 6. Lessons from Outtakes

## 1. Defaults
- Client videos get a licensed music bed plus SFX: the rate card promises "animation, music and optional voiceover".
- SFX only when the brief asks (the Outtakes film was SFX only by request).
- Voiceover only when ordered, with a script approved before generating.
- Silence is a tool: pull the sound down for 0.2-0.3 s before the biggest hit so the ear finds the peak.

## 2. Music
- **Tempo by personality:** calm 70-90 BPM, clean tech 100-120, playful 110-128, hype 128-150. At 30 fps one beat lasts 1800 / BPM frames (120 BPM = 15 f, 100 BPM = 18 f).
- **Cut to it:** big moves and seams on beats and downbeats, details on the off-beats. Camera-level hits on the beat at most three times per film; the rest move only elements.
- **Arc:** quiet hook, a build into the turn, full energy under the proof, a drop just before the payoff, a final hit or button under the logo. The music fades over the last second or ends on that hit; never a silent tail.
- **Under a voice:** duck the music 9-12 dB while the voice speaks (fast attack, about 0.3 s release), back up in gaps longer than 0.4 s.
- **Licence:** the track's licence must cover the client's commercial use on every platform they post to, including paid ads if they run them. Record the source, track name and licence in `NOTE.md`. For generated music, check that the plan in use allows commercial use. If unsure, ask Shezan before delivering.
- **Instagram business accounts** can generally use only Meta's Sound Collection in the app, so music baked into the video must be properly licensed. Offer a no-music version if the client wants to add an in-app sound themselves.

## 3. SFX
Choose 3-5 kinds per film and reuse them: one click, one whoosh, one hit, one tick family, one pop or riser. Fifteen different sounds sound like a library demo.

| Picture event | Sound | Placement | Level against the voice peak |
|---|---|---|---|
| Press or click (squash 2-3 f) | short dry click | on the press frame | -6 to -10 dB |
| Hard cut at full speed | soft thud or tick, 0.15 s tail | on the cut frame | -8 to -12 dB |
| Whip or smear | airy whoosh, 0.3-0.5 s | starts 3-4 f before peak speed | -10 to -14 dB |
| Counter rolling | one soft riser, or a tick every 3rd-4th value | across the roll, ending on the last frame | -16 to -20 dB |
| Typing | quiet keyboard texture, or one tick per word | across the typing | -16 to -22 dB |
| Logo or name slam | low hit with a 0.6-1.0 s tail | on the first big frame | -6 to -10 dB |
| One-frame state change (pop, toggle) | tiny pop | on that frame | -12 to -16 dB |
| Cascade of chips or rows | sparse uneven ticks on 2-3 of the items | on the strongest items | -14 to -18 dB |
| Wipe | filtered sweep | across the wipe | -12 to -16 dB |
| Focus lock (brackets) | autofocus double beep | on the lock | -14 to -18 dB |
| Lingering mark | nothing, or a soft shimmer | tail only | -18 dB or lower |

- Put each sound's transient exactly on its event frame (trim leading silence; pre-roll soft attacks by 1-2 frames).
- Synthesised SFX work well and need no licence: the Outtakes `tools/sfx.py` builds shutters, pops, keystrokes, taps, chimes, impacts, risers, whooshes and autofocus beeps from scratch, placed from a cue list the scene builder writes.
- Give every placed sound a 2-3 ms fade-in and low-pass the master gently (around 15.5 kHz). Instant onsets after silence made the AAC file overshoot the true-peak limit on Outtakes; this fixed it.
- Never leave digital silence under a voice or between hits: lay an inaudible room-tone floor (around -65 dBFS of low-passed noise). look.py flags dropouts otherwise.

## 4. Voiceover

### 4.1 When
Explainers and ads that need more than about six on-screen words per beat usually want a voice. Kinetic-type reels and stings usually don't.

### 4.2 Script rules
- 2.5-3 words per second, one short line per beat, written to the picture, then cut by half. Read it aloud against the timeline.
- The on-screen words finish 0-2 frames before they are heard.
- Spell things the way they should be said: "outtakes dot S G", "seventy dollars", "the twenty-fourth of November", brand names phonetically ("OUT-tayks").
- One line per paragraph with a blank line between, so the take has clean pauses to split on.
- Shezan's voice choices so far: no Singaporean accent; two house voices, a warm feminine female voice or a deep male voice; no whispering (it came out too quiet) and no announcer hype.

### 4.3 ElevenLabs prompts
Put the "Voice:" paragraph into Voice Design (or use it to pick a library voice); paste only the script lines into the text box. Fill the brackets.

```
Voice: female, late 20s, soft, warm and feminine, smooth and velvety with a slight breathy warmth. Elegant and confident, like a premium brand campaign but friendly, not cold. Medium-low pitch, unhurried, a gentle smile in the voice. [Tone notes, e.g. quietly knowing on the problem line, a touch brighter on the short punchy lines.] Clean studio sound, close to the mic, no reverb, no whispering, no announcer hype. Say "[Brand]" as "[PHO-net-ic]". Leave a clear pause at each line break.

[line 1]

[line 2]
```

```
Voice: male, 30s, deep, rich bass voice with a slight gravel, like a sports documentary or a big campaign trailer. Calm, powerful and controlled, never shouting. Deliberate pacing with weight on each line, [dry and knowing on "...", real punch on "..."]. Clean studio sound, close to the mic, no reverb, no whispering. Say "[Brand]" as "[PHO-net-ic]". Leave a clear pause at each line break.

[line 1]

[line 2]
```

Swap the reference style to suit the client (a calm clinic, a playful café), but keep the technical lines: close mic, no reverb, no whispering, pauses at breaks.

### 4.4 Placing the take
1. Split the take into lines by silence (gaps of 0.2 s or more), refining very short gaps by energy.
2. Level-match every line to the same speech loudness, so a soft line doesn't vanish.
3. Place each line on its beat, starting 0-2 frames after its words appear. Check that no two lines overlap.
4. Duck the SFX about 17 dB and the music 9-12 dB under speech. The voice should sit at least 8 dB above everything else while it speaks.
5. Mix, then normalise in two passes to -14 LUFS with a -1.5 dBTP ceiling, then limit. Mux as AAC at 256-320 kbps.

The Outtakes tools do exactly this: `tools/vo_mix.py` (the LINES table holds each line's span in the take and its place in the film) and `tools/vo_mux.sh` (both formats, loudness, mux).

### 4.5 Client recordings and captions
- Ask for WAV, a quiet room, the phone close to the mouth. Denoise lightly; then the same steps.
- With a voiceover, deliver an `.srt` caption file, and burned-in captions when the client posts natively (many people watch muted). Keep captions out of the safe-zone overlays (`formats.md`).

## 5. Mixing targets
| Layer | Target |
|---|---|
| Whole mix | -14 LUFS integrated, true peak -1 dBTP or lower, 48 kHz |
| Voice | the loudest sustained layer |
| Music under voice | ducked 9-12 dB; full in gaps and with no voice |
| SFX | per the table above; only the single strongest hit may pass the voice peak |
| Silence | 0.2-0.3 s of reduced sound before the strongest hit, on purpose |
| Coverage | sound to the last frame, no silent tail, no digital-silence dropouts |

Check the final file with `look.py --expect-audio` and quote its LUFS and true-peak numbers. Scrub the render once at every hit frame and every word onset: sync errors hide in continuous playback.

## 6. Lessons from Outtakes
- Whispered lines came out too quiet: level-match each line.
- "Remove the noise in the background": the crowd ambience under the voice was cut, and a near-silent room tone kept the mix from dropping to digital silence.
- A take with short pauses needed finer splitting; leave clear pauses in the script.
- One line had only a 4.6 dB margin over the effects until the duck was deepened to -17 dB.
