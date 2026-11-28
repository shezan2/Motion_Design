# Motion design films

| Client | Folder | Film | Status |
| --- | --- | --- | --- |
| [CriterAI](https://criter.ai) | [`jobs/criter-ai/intro-20s`](jobs/criter-ai/intro-20s/) | 20 s landscape brand and product intro, SFX only, 1080p30 + 1080p60 + 4K60 | v1, 28 Nov 2026 |
| [Outtakes](https://outtakes.sg) | [`outtakes-launch-lottie`](outtakes-launch-lottie/), [`outtakes-launch-video`](outtakes-launch-video/) | launch films, 9:16 and 16:9 | delivered |

## CriterAI intro (20 s, 16:9)

The noise of Australian visa options collapses into CriterAI's own check mark; a student asks a question, gets an instant answer, taps **Verify by Expert**, and every point is checked by a registered migration agent; then "Lawyer trained. Law driven. AI delivered." and the logo. Built as an HTML composition rendered frame by frame with real motion blur; sound effects from ElevenLabs Sound Effects v3 (elevenlabs/skills) and the game-sfx synth, placed by measured peak. See the job's [`README`](jobs/criter-ai/intro-20s/README.md) and [`NOTE.md`](jobs/criter-ai/intro-20s/NOTE.md).

# Outtakes launch films

Motion-design launch films for **[Outtakes](https://outtakes.sg)**, a platform that helps sports photographers get found, booked and paid. The films have one job: get photographers to sign up for free and set up a profile before the platform goes live on **20 Nov 2026, 5PM SGT**.

Both films were built in the same style (shutter clicks as the beat, sound effects only, no music) and use the same photos and brand. They are two separate projects, one per folder.

| Folder | Built with | Length | Cuts | Status |
| --- | --- | --- | --- | --- |
| [`outtakes-launch-lottie`](outtakes-launch-lottie/) | [text-to-lottie](https://github.com/diffusionstudio/lottie), Lottie animations in a React and Vite player | 64 s, 30 fps | 9:16 (primary) and 16:9 | **Current version** |
| [`outtakes-launch-video`](outtakes-launch-video/) | [Remotion](https://www.remotion.dev/), video as React code | 47 s, 30 fps | 9:16 (primary) and 16:9 | Superseded, kept for reference |

## The story, in one line

A photographer gets the shot, then spends days chasing payment over DMs. Outtakes flips that: clients find you through search, book your package, pay securely, and you get free exposure through Shot of the Week.

## Which one should I open?

- **Want the latest film?** Use the Lottie edition. Start with [`OUTTAKES.md`](outtakes-launch-lottie/OUTTAKES.md), which lists all 13 scenes.
- **Want the original build?** The Remotion edition has a 7-beat breakdown and an easy way to edit copy and dates in one file. See its [README](outtakes-launch-video/README.md).

## Other branches

The W5 Recovery Club website that used to live on `main` is saved on the [`website`](../../tree/website) branch.
