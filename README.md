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

A 20-second landscape (16:9) motion piece for **[OmniGro AI](https://www.omnigroai.com)**, a GEO agency that gets brands recommended by ChatGPT, Gemini, Claude and Perplexity. A customer asks AI what to buy, the answer names competitors, and OmniGro's coral triangle lifts "Your Brand" to #1, followed by the real pilot results and the logo forming out of the motion. Built as HTML with a deterministic timeline, rendered frame by frame in headless Chromium with shutter motion blur, plus an original synthesized music bed and SFX.

| Folder | Built with | Length | Cuts | Status |
| --- | --- | --- | --- | --- |
| [`jobs/omnigro-ai/promo-20s`](jobs/omnigro-ai/promo-20s/) | HTML + JS timeline, Playwright, ffmpeg, numpy audio | 20 s, 30 fps | 16:9 | v1 delivered |

Start with [`STATE.md`](jobs/omnigro-ai/promo-20s/STATE.md) (brand sheet, idea, beat sheet, rebuild commands) and [`NOTE.md`](jobs/omnigro-ai/promo-20s/NOTE.md) (what is real, QA numbers, client message). The video is [`out/omnigro-promo-16x9-v1.mp4`](jobs/omnigro-ai/promo-20s/out/omnigro-promo-16x9-v1.mp4).

## Other branches

The W5 Recovery Club website that used to live on `main` is saved on the [`website`](../../tree/website) branch.
