# Nick R.L. intro film

A 20-second landscape (16:9) motion design film for **Nick R.L.**, Associate Division Director at PropNex Realty (CEA Reg. No. R002622D). It has sound effects only: no music and no voiceover. Ozen Digital made it as a spec piece to onboard him as a client.

**Watch:** [`delivery/nickrl-intro-16x9-v1.mp4`](delivery/nickrl-intro-16x9-v1.mp4). There's also a WhatsApp-size preview and a cover image in the same folder.

## The film in one line

A listing sits for 180 days. Then, with Nick, it's **sold in 1 month**. The gold ring becomes his four promises: **Right advice, Right strategy, Right execution, Right home**. The house then opens into his name card, ending on WhatsApp 9859 9857.

| Time | Beat | On screen |
| --- | --- | --- |
| 0.0-2.8 s | Hook | A day counter rolls to 180 inside a ring with six month marks: "days on the market" |
| 2.8-6.0 s | Turn | A gold arc covers a sixth of the ring: "Sold in 1 month." Blk 123 Yishun · 4-room HDB |
| 6.0-11.6 s | Promise | The gold ring becomes his icons: target, knight, check, house. "Right advice / strategy / execution / home." |
| 11.6-16.0 s | Reveal | The house outline turns into his name card: photo, name, "Your trusted agent", title, PropNex, specialities |
| 16.0-20.0 s | Call to action | A scale cut moves in, the gold "WhatsApp 9859 9857" button appears and the cursor presses it. CEA details sit on the card |

All copy and facts come from Nick's public channels. [`PLAN.md`](PLAN.md) has the brand sheet, beat sheet, seams and sources. [`NOTE.md`](NOTE.md) is the internal review note, with what is real, the QA numbers and what still needs confirming.

## How it's built

- **Picture:** Lottie scenes written in Python with the Outtakes toolkit (`tools/lottie_kit.py` plus `tools/nk.py`), using the [text-to-lottie](https://github.com/diffusionstudio/lottie) approach. They're rendered offline with Skia Skottie (`canvaskit-wasm`) into a **32-bit float surface**, so the navy gradients never band. The intermediate is 10-bit 4:4:4 BT.709, dithered down to the 8-bit master.
- **Sound** comes from two GitHub skills plus a mixer:
  - [Clipwing **real-sfx**](https://github.com/Clipwing/skills/tree/main/skills/real-sfx) sets the method: one recorded-sounding sound per cue, placed by its arrival or peak on the exact frame, role levels, a near-silent bed, a mono check, and a comparison against nine reference SFX reels (`refstyle.py`).
  - The [ElevenLabs **sound-effects** skill](https://github.com/elevenlabs/skills/tree/main/sound-effects) (official, model `eleven_text_to_sound_v3`) supplied the sounds. Each cue got four takes, and one was picked by measurement (`tools/sfx_analyze.py`).
  - The mixer is `tools/sfx_mix.py`.
- **Method:** the Ozen motion design skill, with QA by its `look.py` (gates G0, G2 and G3).

## Rebuild

```bash
npm install                               # canvaskit-wasm (Skottie)
pip install numpy pillow scipy fonttools brotli svgelements soundfile pyloudnorm
python tools/build_film.py                # Lottie scene + SFX cue list (copy and timings at the top)
bash tools/render_film.sh 4               # 16-bit render in 4 parallel ranges -> out/film-video10.mp4
python tools/sfx_mix.py                   # SFX track -> audio/sfx.wav
bash tools/master.sh 2                    # master + WhatsApp preview -> out/nickrl-intro-16x9-v2.mp4
node tools/render.mjs still public/projects/nickrl-intro-16x9/scene-1 0,97,250,470 out/stills/s   # stills
```

Copy lives in the `COPY` dict and timing in the `T` table, both at the top of `tools/build_film.py`, so a change is one edit followed by a re-render.

## Credits and licences

- Fonts: Montserrat and Cormorant Garamond (SIL OFL, through @fontsource).
- Icons: Tabler Icons (MIT).
- PropNex logo: the official file from propnex.com, used only as the agency credit.
- Nick's photo: cut out from his own YouTube channel banner (BiRefNet matte plus a SAM boundary).
- Sounds: generated with ElevenLabs SFX v3 under the account's plan.
