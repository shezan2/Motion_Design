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
