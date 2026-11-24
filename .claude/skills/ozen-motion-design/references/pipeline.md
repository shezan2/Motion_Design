# Production pipeline

## Contents
1. Choosing the engine · 2. The Lottie toolkit (default) · 3. Starting a new client film · 4. Commands · 5. Skottie gotchas · 6. HTML/GSAP and Remotion · 7. Saving tokens and time

## 1. Choosing the engine
| Engine | Use it when | Strengths | Limits |
|---|---|---|---|
| **Lottie + Skottie** (default) | most client jobs: type, UI, shapes, photos, 3D planes | deterministic, light, fast parallel renders, reusable Python parts, the scene JSON is also a web deliverable | no shaders, no threshold or metaball filter, no depth sorting, no real motion blur |
| **HTML + GSAP** (motionmaxxing runtime or HyperFrames) | the hero needs real 3D (three.js), shaders, backdrop blur, CSS filters or live web capture | richest look, any web technique | needs headless Chrome rendering; slower; more code per scene |
| **Remotion** (React) | many variants from data: 20 localised ads, a price list per branch, weekly templated videos | data-driven templates, batch rendering | React project overhead; licence terms for companies (check `remotion-dev/skills`, remotion-license) |

When a client needs both, build the film in Lottie and render one hero shot in HTML/GSAP, then join them with ffmpeg on a carried-object seam.

## 2. The Lottie toolkit (default)
It lives in the repo `shezan2/w5-recovery-club-website`, folder `outtakes-launch-lottie/` (built from `diffusionstudio/lottie`, text-to-lottie; its own skill is in `outtakes-launch-lottie/skills/text-to-lottie/`). Everything renders with the same engine as the official player: canvaskit-wasm "full", which is Skia Skottie.

| File (in `tools/`) | What it does |
|---|---|
| `lottie_kit.py` | the authoring kit: `Comp` (layers bottom to top, `build()` writes Lottie order), shape, image, native text, null, camera layers, track mattes, gradients, trim paths, text slots, keyframes eased by named anchors (`entrance-sharp`, `settle-soft`, `travel-balanced`, `exit-accelerate`, `expressive-pop`, `crash`, `scroll`) |
| `film_parts.py` | format-aware parts: `OT_FORMAT=portrait|landscape`, palette (`COL`), backgrounds, glows, grain, vignette, curtains, flashes, line rises, photos with focus points, chips, taps, icons, CTA buttons, `drift` |
| `parts4.py` | the premium parts: `Plane` (3D UI planes with boxes, text, keyed text, images, icons), `button` with press physics, `cursor` with presses, `film_strip`, focus `brackets`, `statement` (centred blur-in lines), Gaussian blur and drop shadow effects (`gblur`, `drop_shadow`, `with_fx`), `ground`, `soft_vignette` |
| `build_film.py` | the film: one function per scene, writes `public/projects/<project>/scene-N/lottie.json` and the SFX cue list |
| `render.mjs` | offline Skottie renderer: `still`, `scene` (one scene to a segment, grain added in ffmpeg) and `video` modes |
| `export.sh` | build -> SFX -> render all scenes in parallel -> concat with audio |
| `sfx.py` | synthesised SFX placed on the cue frames, mixed to -14 LUFS |
| `vo_mix.py`, `vo_mux.sh` | voiceover lines placed on beats, ducking, loudness, mux |
| `make_fonts.py` | cuts static font instances (Skottie can't pick variable-font axes) |
| `make_assets_v4.py` | bakes photos and textures (crops around subject points, duotones, foil glyphs) |
| `player_shot.mjs` | screenshots pinned frames from the official player (`?frame=N`) as a cross-check |

## 3. Starting a new client film
1. Copy `outtakes-launch-lottie/tools/` into a new project folder next to it (for example `acme-launch/tools/`), plus `package.json`, `public/` structure and `scripts/copy-canvaskit.mjs`; run `npm install` there (or reuse the existing `node_modules` by building inside `outtakes-launch-lottie/` under a new project name).
2. Fonts: put the client's font files in a fonts folder, run `make_fonts.py` for static instances, register them in the `Fonts` table.
3. Palette: set the brand sheet's colours in a `C` dictionary (as `parts4.C` does) and `fp.COL.update(C)`.
4. Assets: logo as SVG converted to shapes, or a large PNG; photos baked with subject points (`make_assets_v4.py` is the pattern).
5. Write `build_<client>.py`: one small function per beat, using the parts. Keep the beat sheet's frames as constants at the top so retiming is one edit.
6. Write the cue list as you place events (presses, cuts, hits); `sfx.py` reads it.
7. Render stills of the hero frame first, then the hardest seam, then the rest.

## 4. Commands
```bash
python3 tools/build_film.py                                   # write every scene's lottie.json
node tools/render.mjs still public/projects/<project>/scene-3 0,45,90 /tmp/s3   # stills of one scene
bash tools/export.sh                                          # full portrait film -> out/*-9x16.mp4
OT_FORMAT=landscape bash tools/export.sh                      # landscape -> out/*-16x9.mp4
JOBS=4 bash tools/export.sh                                   # parallel scene renders (default 4)
python3 tools/sfx.py                                          # SFX only
bash tools/vo_mux.sh                                          # voiced versions of both formats
python3 <skill>/scripts/look.py out/<file>.mp4 --out look --expect <s> --expect-audio
```
- **Partial re-render:** after changing one scene, render only it into `out/segments-<format>/scene-N.mp4` with `node tools/render.mjs scene <sceneDir> <out.mp4>`, then re-run only the concat and mux lines of `export.sh`.
- **Cross-check in the official player:** run the Vite dev server and open `/<project>/<scene>?frame=N`, or use `player_shot.mjs`.

## 5. Skottie gotchas (each cost real time on Outtakes)
- Keyframe easing: both `o` and `i` sit on the starting keyframe.
- Track mattes: the matte layer has `td: 1` and sits directly above its target, which has `tt: 1`.
- Fill-colour alpha is ignored: use layer opacity or a matte.
- Opacity does not inherit through parenting: fade every child, or put them in a precomp or matte.
- 3D: a camera layer (`ty: 13`, `pe` = zoom, position `[cx, cy, -zoom]`, anchor `[cx, cy, 0]`) and `ddd: 1` layers. There is no depth sorting: layers draw in layer order, so order them back to front yourself.
- Children of a 3D null need their own in and out points; a parent being out of range does not hide them.
- Gaussian Blur (`ty: 29`) and Drop Shadow (`ty: 25`) render and animate, also on 3D layers.
- Variable fonts don't switch axes: cut static instances, one family name each.
- Images are deduplicated by the kit's `_asset()`; give `Comp.image()` an anchor when it will scale.
- Verify anything unusual (blend modes, gradients on strokes, text animators) with a `render.mjs still` before building a scene around it.
- Grain is added per segment in ffmpeg (`noise=c0s=5:c0f=t+u`), not in Lottie.

## 6. HTML/GSAP and Remotion
- **motionmaxxing** (github.com/Tejashmakwana/motionmaxxing): a seek-safe GSAP runtime, a three.js hero object, iOS UI builders, a brand capture script (`brand.mjs <url>` saves colours, fonts, logo, screenshots), a renderer with shutter blur, and `lint.mjs` for page chrome. Clone it when a film needs these; its `look.py` is bundled here.
- **HyperFrames** (github.com/heygen-com/hyperframes): HTML compositions rendered to video, with a seam verifier that enforces the seam law and a `reverse-any-video` workflow that rebuilds a reference frame by frame. Install with `npx skills add heygen-com/hyperframes`. Use only for references the client has the right to use.
- **Remotion** (remotion-dev/skills): `npx create-video@latest`, one set of scenes with a layout context for portrait and landscape, `npx remotion render`. Best for batch variants.

## 7. Saving tokens and time
- Work from `STATE.md` and the beat sheet; don't re-read big files you already know.
- Iterate on stills and contact sheets; render the full film only at milestones.
- Re-render only the scenes that changed; keep scenes independent so this works.
- Keep scene functions small and parameterised by the beat-sheet constants; retiming should be a one-line edit.
- Reuse parts across clients; when you write a new helper twice, move it into the parts file.
- Run `ref_breakdown.py` once per batch of references instead of opening frames one by one.
- Batch renders in parallel (`JOBS`), and run long renders in the background while writing the sound plan.
