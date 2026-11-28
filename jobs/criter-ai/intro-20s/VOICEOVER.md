# CriterAI intro: voiceover prompts

For a voiced version (`criter-ai-intro-16x9-vo-v1.mp4`). Paste the "Voice:" paragraph into ElevenLabs Voice Design (or use it to pick a library voice), then paste only the script lines into the text box. Both house voices are below; the script is the same for each.

Pronunciation: written as "Krit-er A.I." (the mascot "Criter" is a pun on "critter"). Confirm with CriterAI that they say KRIT-er and not CRY-ter before generating.

## Female (warm, feminine)

```
Voice: female, late 20s, soft, warm and feminine, smooth and velvety with a slight breathy warmth. Light, natural Australian accent that stays clear for international listeners. Elegant and confident, like a premium brand campaign but friendly and reassuring, not cold. Medium-low pitch, unhurried, a gentle smile in the voice. Curious and a little searching on the three opening questions, calm and certain on "Just ask CriterAI", quietly proud on "Lawyer trained. Law driven. AI delivered." Clean studio sound, close to the mic, no reverb, no whispering, no announcer hype. Say "CriterAI" as "KRIT-er A-I". Leave a clear pause at each line break.

Which visa?

Which documents?

What's next?

Just ask Krit-er A.I.

Get an instant answer.

Then a registered migration agent checks it,

in as little as thirty minutes.

Lawyer trained.

Law driven.

A.I. delivered.

Start for free at Krit-er dot A.I.
```

## Male (deep)

```
Voice: male, 30s, deep, rich bass voice with a slight gravel. Light, natural Australian accent that stays clear for international listeners. Like a big campaign trailer but warm and trustworthy. Calm, powerful and controlled, never shouting. Deliberate pacing with weight on each line, curious on the three opening questions, real punch on "Lawyer trained. Law driven. AI delivered." Clean studio sound, close to the mic, no reverb, no whispering. Say "CriterAI" as "KRIT-er A-I". Leave a clear pause at each line break.

Which visa?

Which documents?

What's next?

Just ask Krit-er A.I.

Get an instant answer.

Then a registered migration agent checks it,

in as little as thirty minutes.

Lawyer trained.

Law driven.

A.I. delivered.

Start for free at Krit-er dot A.I.
```

## Where each line sits (start times in the film)

40 words in 20 s, about 2 words a second, so every line has room. Each line starts just after its words appear on screen.

| # | Starts | Line | On screen |
|---|---|---|---|
| 1 | 0.05 s | Which visa? | "Which visa?" |
| 2 | 0.97 s | Which documents? | "Which documents?" |
| 3 | 1.92 s | What's next? | "What's next?" |
| 4 | 3.35 s | Just ask CriterAI. | the gold check draws, the C closes |
| 5 | 5.75 s | Get an instant answer. | the answer streams in |
| 6 | 7.45 s | Then a registered migration agent checks it, | cursor goes to Verify by Expert; "checks it" should land as the rows tick (about 9.2 s) |
| 7 | 10.35 s | in as little as thirty minutes. | "Verified by a Registered Migration Agent" |
| 8 | 12.25 s | Lawyer trained. | "Lawyer trained." |
| 9 | 13.20 s | Law driven. | "Law driven." |
| 10 | 14.15 s | AI delivered. | "AI delivered." |
| 11 | 17.45 s | Start for free at criter.ai. | "Start for free" and criter.ai; must end before 19.9 s |

Every claim is on criter.ai: "instant visa guidance", a registered migration agent reviews answers through Verify by Expert (FAQ), "in as little as 30 minutes" (hero), "Lawyer Trained, Law Driven, AI Delivered" (hero), "Start for Free" (hero; free during the closed beta).

## Mixing it in (skill sound.md 4.4)
Split the take by silence, level-match every line, place each on its start time above, duck the SFX about 10-12 dB under speech (the voice at least 8 dB above everything), keep the check chimes and the logo hit between lines, then -14 LUFS and true peak under -1 dBTP. Deliver as a separate `-vo` file; the SFX-only cut stays as is.

## Voiced cut v1 (take: `audio/vo/take1-elevenlabs-v4.mp3`, ElevenLabs v4, 28 Nov 2026)
Built with `audio/vo.py`: the take split at its pauses into the 11 lines (the three questions and "Lawyer trained. Law
driven." were read together, split at their 0.18-0.2 s pauses), each line level-matched, placed just after its words
appear, SFX ducked 11 dB under speech, -14.0 LUFS, -2.3 dBTP. Voice over SFX while speaking: median 26.5 dB, 10th
percentile 9.9 dB (target 8 dB or more). Pauses between lines 0.12 s or more; the last word ends at 19.84 s.
Four lines are tightened 4-7% with a pitch-preserving tempo change because the read was longer than the on-screen
slot: "Which visa?", "Which documents?", "Then a registered migration agent checks it," and the three payoff lines.
"...checks it," ends as the rows start ticking, so the four check chimes ring out clear right after the voice.

| Line | In the film |
|---|---|
| Which visa? | 0.03 s |
| Which documents? | 1.00 s |
| What's next? | 2.09 s |
| Just ask CriterAI. | 3.30 s |
| Get an instant answer. | 5.20 s |
| Then a registered migration agent checks it, | 6.82 s |
| in as little as thirty minutes. | 9.95 s |
| Lawyer trained. | 12.00 s |
| Law driven. | 13.02 s |
| AI delivered. | 14.03 s |
| Start for free at criter.ai. | 17.42 s |

Files: `out/criter-ai-intro-16x9-vo-v1.mp4` (1080p30) and captions `out/criter-ai-intro-16x9-vo-v1.srt`. 60 fps and 4K voiced
files are the same picture re-muxed with `audio/mix_vo.wav`:
`ffmpeg -i out/criter-ai-intro-16x9-4k-v1.mp4 -i audio/mix_vo.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k out/criter-ai-intro-16x9-4k-vo-v1.mp4`
