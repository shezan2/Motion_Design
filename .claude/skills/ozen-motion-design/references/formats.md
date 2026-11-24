# Formats and delivery

## 1. Sizes
| Ratio | Pixels | Where it goes |
|---|---|---|
| 9:16 (master) | 1080x1920 | Instagram Reels and Stories, TikTok, YouTube Shorts, WhatsApp Status |
| 4:5 | 1080x1350 | Instagram and Facebook feed, LinkedIn feed |
| 1:1 | 1080x1080 | feeds, marketplaces, some ad placements |
| 16:9 | 1920x1080 | YouTube, LinkedIn, websites, presentations, TV screens at events |

Make 9:16 first unless the brief says the main use is landscape.

## 2. Safe zones
App buttons, captions and usernames sit on top of the video. Keep every word that must be read, and every subject that matters (faces, the product, the ball), inside these boxes. They are deliberately conservative; check against a current screenshot of the app when a layout is tight.

| Format | Keep inside | Why |
|---|---|---|
| 9:16 for Instagram | x 80-940, y 260-1500 | top bar; caption, username and audio line at the bottom; like and share buttons on the right |
| 9:16 for TikTok | x 80-920, y 260-1440 | taller caption block and a wider right rail |
| 9:16 for Shorts | x 80-940, y 260-1480 | similar to Reels |
| 4:5 and 1:1 | at least 60 px from every edge | feed crops and rounded corners |
| 16:9 | 96 px from the sides, 54 px top and bottom; nothing important bottom-right on YouTube | title safe; end-screen elements and captions |

**Reels cover:** the profile grid shows a centre crop, so put the cover's title inside the centre 1080x1350 of the 9:16 frame.

## 3. Re-compose, never just crop
- Build every scene with a format switch (the Outtakes builder reads `OT_FORMAT=portrait|landscape`) and per-format positions and sizes.
- **16:9:** keep one hero per frame. Run the claim and then the proof in sequence rather than side by side ("headline left, device right" is a slide layout); spend the extra width on camera travel and wider product crops.
- **4:5 and 1:1:** fewer words per line, larger product crops, statements a size smaller than 9:16.
- **Photos and footage:** store a subject point per image (face, ball, product centre) and crop each format around it. Shezan flagged portrait crops that cut the subject on Outtakes.
- Re-check reading holds per format: a line that wraps to three lines in 1:1 needs more time.

## 4. Export settings
Master (all formats):
```bash
ffmpeg -i in.mp4 -c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -crf 16 -preset slow \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart out.mp4
```
- Constant 30 fps, yuv420p (anything else can play wrong on phones), audio 48 kHz.
- **WhatsApp preview:** video sent as media is capped at about 16 MB (check the current limit). Send a light copy for a quick look and the full file as a document or a link:
  ```bash
  ffmpeg -i out.mp4 -vf scale=720:-2 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 128k -movflags +faststart preview.mp4
  ```
- **Agencies** sometimes want a high-quality master for their own edit: ProRes 422 HQ (`-c:v prores_ks -profile:v 3`) or a CRF 10 H.264.
- **Web:** a Lottie or dotLottie file of a scene is possible from the Lottie pipeline (logo stings, hero loops); offer it as an extra, not by default.

## 5. Covers and captions
- A designed cover frame per video (the payoff line or the hero frame, title inside the centre 1080x1350), exported as a JPG at full size.
- Never let the first frame be black or empty: a feed shows it before playback starts.
- With a voiceover: an `.srt` file, plus burned-in captions when the client posts natively. Captions sit inside the safe zone, two lines at most, 40-48 px on 9:16.

## 6. Naming and the delivery package
- `<client>-<video>-<ratio>-v<N>.mp4`, for example `acme-launch-9x16-v2.mp4`. Suffixes: `-vo` (voiced), `-nomusic`, `-captions`, `-preview`.
- A delivery contains: the MP4 per format, the cover JPGs, the `.srt` if voiced, the client message (`client-workflow.md`), and the internal `NOTE.md`.
- Never overwrite a delivered file: a fix is the next version.
