# Move library

Named moves, mostly from the reference reels Shezan picked, with timing and build notes. Frames are at 30 fps. Pick 4-8 moves per film, give one of them the hero moment, and make every move belong to the client's brand. Build notes assume the Lottie toolkit (`pipeline.md`); HTML/GSAP and Remotion equivalents are standard (CSS `filter: blur()`, `clip-path`, `interpolate()`).

Seen in: CB calbby.mg, DV divyansh.fx, OA OpenAI concept, AW Apple Widgets, YM youmotion, BB BLACKBOX.AI, AV Ava AI, ZP Zapier, OT our Outtakes film.

## Contents
A. Type (1-13) · B. Product UI (14-26) · C. Carriers and shapes (27-35) · D. Light, depth and camera (36-44) · E. Endings (45-50) · F. Build notes that apply to many moves

## A. Type

1. **Blur-in word build** (CB, DV, OT). Words resolve from 8-12 px blur while rising 0.03-0.05 of the frame height. Words 3-5 f apart (8-12 f when a voice leads). Blur 7 f `glide`, rise 12 f `softLand`, opacity only as a 4-6 f helper. The default type entrance of the Ozen look. Lottie: Gaussian Blur effect on each word layer (`parts4.gblur`, `with_fx`).
2. **Keyword swap in a fixed slot** (OA "One place to Imagine / Build / Discover", ZP, AV). The fixed part never moves; only the keyword changes, sliding vertically inside a matte or swapping through a short blur. 0.6-1.0 s per keyword, the last one gets the full stop and a longer hold. Measure the longest keyword first and set the slot so nothing re-centres. Lottie: track matte (matte layer `td: 1`, keyword `tt: 1`).
3. **Hard phrase replacement** (AV "Sales reps" -> "Training"). The whole line swaps in one frame on a beat; reads as rhythm and state. Pair with a light streak or SFX tick.
4. **Fragment completes itself** (AW "End" -> "Endless creativity"). The first word lands alone in its final position, the rest grows out of it. Plan final positions first so the survivor never jumps.
5. **One word at a time** (DV "The / brands / the / market."). Each word alone and centred, 6-9 f each, the last word held. For a punchline of up to five words, not for information.
6. **Accent word** (DV serif italic, OA blue, ZP orange). One word per line arrives in the brand colour or a serif italic. The colour lands with the word, never after it. Rate card example: "Motion design *videos*".
7. **Brace framing** (AV "{ is expensive }"). Braces or brackets start wide and close onto the phrase over 10-14 f `softLand`, then shrink with it. Good for a single cost or pain line.
8. **Hand-drawn ellipse** (DV "It's leverage."). A stroke circles the payoff word in 12-18 f, passing its start point slightly, with a soft glow. Lottie: trim paths on a slightly irregular ellipse path.
9. **Scramble decode** (DV logo). Letters cycle through random glyphs and settle left to right, one glyph change every 2 f, 10-20 f total. For tech brands and logo reveals. Lottie: keyed text documents (`Plane.keyed_text`), one key every 2 f.
10. **Letter boxes** (OA "OpenAI"). Each letter appears inside its own box, the boxes vanish, the tracking opens a little and settles. A precise, technical name reveal.
11. **Typed prompt** (OA, ZP, CB search bar). Only inside the product's own input field. Bursts of 3-4 characters per frame with irregular pauses, a caret blinking every 0.5 s, the cursor parks on send, press, cut before the release. Typing a headline letter by letter outside a field is a tell.
12. **Chip cascade** (DV benefit pills). Benefits arrive as pills from alternating sides with a short motion smear, alternating filled (brand colour) and outlined, 12-20 f apart because each must be read, on staggered rows. They leave together by defocusing. Max six chips.
13. **Persistent tiny caption** (BB "where the future gets built"). One small line stays fixed while footage changes under it every 4-8 f. Anchors a montage.

## B. Product UI

14. **Search bar hook** (CB). An empty search bar materialises (blur clearing, scale 0.92 -> 1), shows "search...", then the brand or problem types in. Works for any business people look up.
15. **Container morph** (CB search bar -> profile card, YM pill -> band). A bar, pill or button inflates into the next card: size and corner radius tween over 12-18 f, its content lands 4-6 f after the container settles. The best seam for UI films.
16. **Prompt -> press -> burst** (OA). The prompt types, the camera pushes 1.5-2x into the send button, the press squashes for 2-3 f, then the results burst out radially from behind the button (1-2 f stagger, rotation spread, `snapSettle`), and the camera pulls back to show the whole spray.
17. **Workflow tree** (ZP). Steps appear line by line with indent guides, 8-12 f per line, the active step in the brand colour. Then the tree collapses into the next container (chips, a single result).
18. **Chained chips** (ZP Gmail - Slack - Sheets). App names or logos in pills, linked by connectors that draw in 6 f each (trim paths). Use real integrations only.
19. **Cylinder list** (ZP app names). Names roll on a 3D drum: scale and opacity follow the cosine of each item's angle, blur grows towards the edges, 0.25-0.4 s per item. Says "works with everything" without a logo wall. Lottie: bake per-item position, scale and opacity every 2 f in Python.
20. **Count-up inside UI** (AW activity rings, OT earnings S$0 -> S$70). Values step every frame with shrinking steps and land on the real number; units and labels stay fixed. A soft tick every third or fourth value, or one riser for the whole roll.
21. **Resize morph** (AW widget sizes). A card grows small -> medium -> large and shows more each time: the feature demo is the resize.
22. **Call pill** (AV "9:21" -> "Talking to AVA"). A pill expands from a time into an active call with an icon. For voice, call and booking products.
23. **Error -> fix** (OA). The ground flashes the error colour for 3-6 f, the wrong line gets a cross, "Fixing..." appears, the corrected line ticks green, the colour returns. Shows a product solving something in two seconds.
24. **3D card fan or tilt** (CB, AW, OT). Cards rotate 8-20 degrees in 3D with soft shadows while the camera dollies; one card comes forward. Lottie: camera layer plus 3D planes (`parts4.Plane`), drop shadow effect.
25. **Cursor drives the action** (CB, ZP, OT). An oversized custom cursor enters at 2-5x and shrinks while travelling, parks 4-8 f before acting, squashes 2-3 f on the press, and the target answers one frame later. No click ripples. Lottie: `parts4.cursor(keys, presses)`.
26. **Case-study frame** (AV). For Ozen's own portfolio posts only: the client film plays inside a rounded card, with a chapter bar under it (Hook / Problem / Solution / Demo / CTA) and a moving playhead. Shows the thinking, not just the result.

## C. Carriers and shapes

27. **Dot carrier** (YM, DV, OA). One dot travels through the film: ring -> node -> star -> pill -> logo. Morph through shapes with the same number of vertices so the change reads as one object.
28. **Comet line** (YM "Connected"). A dot drags a gradient-tailed line that draws the next container. Lottie: trim paths with the start lagging the end by 20-30%, a gradient stroke for the tail.
29. **Signal fibres** (OA). One line splits into a fan of curves that reach the problem's UI chips, then everything converges back into points. Visualises "too many inputs".
30. **Glyph chaos -> brand square -> logo part** (ZP). Dozens of characters drift as noise, then accelerate into one point that becomes a square in the brand colour, which stretches into a piece of the logo. The strongest carrier logic in the library: the problem literally becomes the brand.
31. **Strings with physics** (YM pill on a string). A label hangs on a string with a weighted dot; it swings and the string lags behind. Bake a damped spring per frame in Python and write it as keyframes.
32. **Icon nodes with callouts** (DV honeycomb). Icons in hexagons or circles pop in one by one, each with a hairline callout and a small label. For listing pains or features as a system.
33. **Ring counter** (DV "8 -> 13 Is a second"). A number counts inside a progress ring as it draws, then the ring collapses to a dot that carries on.
34. **Organic growth** (OA branch). A branch or vine grows (trim paths, tapered width) and connects scattered labels; leaves or particles fall after. Chaos to order, warm version.
35. **Blobs -> logo** (YM, AW). Soft colour blobs drift and merge behind a line of text, then sharpen into the logo. Lottie has no threshold filter, so fake metaballs with 3-4 heavily blurred circles (60-120 px) and bring the logo in by animating its blur from about 60 px to 0 as the blobs shrink into it.

## D. Light, depth and camera

36. **Bloom flash** (YM). A white radial bloom grows from a point to fill the frame in 6-10 f, flipping a dark film to light: the effect becomes the next ground. Lottie: radial gradient circle scaling up, or a white circle with a large blur.
37. **Ring fly-through** (OA "connected."). The camera pushes through a glowing ring into the next world. Spend it once, on the turn from problem to product.
38. **Light streak** (AV). An anamorphic streak (a thin bright ellipse, screen or add blend) slides across a word as it swaps. Check blend modes in a Skottie still before relying on them.
39. **Horizon glow** (AV, CB). A soft glow in the brand colour rising from the bottom edge: the film's one light. It may drift slowly; it never pulses on a loop.
40. **Ambient colour blobs** (AW). Blurred blobs in colours taken from the UI on screen drift slowly behind it, so each feature carries its own mood.
41. **Focus pull with brackets** (DV viewfinder, OT hook). The subject sharpens from 20-55 px blur to 0 while the background softens, and corner brackets lock on with an autofocus double beep. The natural hook for anything visual (photography, products, property).
42. **Push into the detail** (OA send button, AW). The camera pushes 1.3-2x into the button or number that matters over 10-22 f `glide`, then moves on.
43. **Whip with motion blur** (DV, CB logo). A 7-8 f whip with directional blur on the moving layer; the content changes during the blur, so the cut hides inside the move.
44. **Depth-of-field field** (OA labels). Floating labels at three depths, big and blurred near, sharp in the middle, tiny far away, with slow parallax. Makes a flat list feel like space.

## E. Endings

45. **Logo resolves from the motif** (ZP square -> underscore, YM blobs -> M, AV slashes -> mark). The carrier becomes the logo over 18-30 f, then holds 0.6-1.4 s with one living thing (a slow scale creep, a sweep of light). The default Ozen ending.
46. **Payoff word, then brand** (OA "Seconds.", DV "Aren't louder."). One word or a short line holds 0.6-1.0 s before the logo.
47. **Loop seam** (CB, DV, OA). The last 0.3 s leads into frame 1 with the same composition and direction of motion, so a replay looks continuous.
48. **Small logo after the storm** (BB). After a fast montage, a small logo on black with a short hold.
49. **Press and cut** (motionmaxxing C8). The CTA button is pressed and the film cuts on the squash, before the release.
50. **Brand-colour flood** (ZP orange). The last line sits on a full-bleed field of the brand colour, then the logo.

## F. Build notes that apply to many moves
- **Blur** is the most useful single tool: entrances, exits, focus pulls, whips and fake metaballs. Skottie renders the Gaussian Blur effect (animatable) and Drop Shadow, also on 3D layers.
- **Mattes** handle slots, wipes and reveals: the matte layer sits directly above its target (`td: 1`), the target carries `tt: 1`.
- **Trim paths** handle every line draw, ring, ellipse and connector; a gradient stroke gives the comet tail.
- **Physics and drums** are baked: compute positions per frame in Python and write keyframes every 1-2 frames.
- **Counters and scrambles** are keyed text documents, one key per value.
- **3D** uses a camera layer and 3D planes. Skottie does no depth sorting, so add layers back to front yourself, and give children of a 3D null their own in and out points.
- **Opacity does not inherit through parenting** and fill-colour alpha is ignored: fade each layer, or use a matte.
