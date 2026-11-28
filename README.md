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

## OmniGro AI promo (Nov 2026)

A 20-second landscape (16:9) motion piece for **[OmniGro AI](https://www.omnigroai.com)**, a GEO agency that gets brands recommended by ChatGPT, Gemini, Claude and Perplexity. A customer asks AI what to buy, the answer names competitors, and OmniGro's coral triangle lifts "Your Brand" to #1, followed by the real pilot results and the logo forming out of the motion. Built as HTML with a deterministic timeline, rendered frame by frame in headless Chromium with shutter motion blur, with a sound-effects-only soundtrack.

| Folder | Built with | Length | Cuts | Status |
| --- | --- | --- | --- | --- |
| [`jobs/omnigro-ai/promo-20s`](jobs/omnigro-ai/promo-20s/) | HTML + JS timeline, Playwright, ffmpeg; SFX from Mixkit + CC0 libraries | 20 s, 30 fps | 16:9 | v3 delivered (voiced), v2 (SFX only) |

Start with [`STATE.md`](jobs/omnigro-ai/promo-20s/STATE.md) (brand sheet, idea, beat sheet, rebuild commands) and [`NOTE.md`](jobs/omnigro-ai/promo-20s/NOTE.md) (what is real, QA numbers, client message). The voiced cut is [`out/omnigro-promo-16x9-v3-vo.mp4`](jobs/omnigro-ai/promo-20s/out/omnigro-promo-16x9-v3-vo.mp4) (ElevenLabs voiceover over the SFX, captions in the `.srt` beside it). [`out/omnigro-promo-16x9-v2.mp4`](jobs/omnigro-ai/promo-20s/out/omnigro-promo-16x9-v2.mp4) is sound effects only, built with the [real-sfx](https://github.com/Clipwing/skills) and [sfx-library](https://github.com/GFXER/sfx-library) skills' methods from Mixkit and CC0 sounds. v1 (with a synthesized music bed) is kept next to it.

## Other branches

The W5 Recovery Club website that used to live on `main` is saved on the [`website`](../../tree/website) branch.
