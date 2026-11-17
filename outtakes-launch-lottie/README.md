# Outtakes launch film: Lottie edition

The current Outtakes launch film, built as **Lottie animations** and previewed in a React and Vite player. It has **13 scenes** and runs **64 s at 30 fps**, in two cuts from one timeline:

| Cut | Size | Use | Folder |
| --- | --- | --- | --- |
| Portrait (primary) | 1080×1920 | Reels, TikTok, Shorts | `public/projects/outtakes-launch` |
| Landscape | 1920×1080 | YouTube, website, X | `public/projects/outtakes-launch-16x9` |

Sound is effects only (no music, no voiceover). The interface in the film is rebuilt to match the live Outtakes website.

## Read this first

[`OUTTAKES.md`](OUTTAKES.md) is the full guide: a scene-by-scene table, the site animations that were ported, type, transitions and pricing format.

## Run it

```bash
npm install
npm run dev        # opens the player; scenes live-update as files change
npm run build      # type-check and production build
```

## What is where

| Path | What it holds |
| --- | --- |
| `public/projects/` | The films. Each scene is `<project>/<scene>/lottie.json` |
| `brand/` | Outtakes fonts and the supplied photos |
| `src/` | The player app |
| `tools/` | Python scripts that build and export the film |
| `skills/text-to-lottie/` | The authoring rules used to generate the animations |

## Credits

Built on the open-source [text-to-lottie](https://github.com/diffusionstudio/lottie) framework by Diffusion Studio. Its original README is kept as [`TEXT-TO-LOTTIE.md`](TEXT-TO-LOTTIE.md) and its licence in [`LICENSE`](LICENSE).
