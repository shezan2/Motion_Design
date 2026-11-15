import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
const require = createRequire(import.meta.url);
const CanvasKitInit = require("canvaskit-wasm/full");
const ck = await CanvasKitInit({ locateFile: (f) => require.resolve("canvaskit-wasm/full").replace(/canvaskit\.js$/, f) });
const [dir, mutate] = process.argv.slice(2);
let doc = JSON.parse(fs.readFileSync(path.join(dir, "lottie.json"), "utf8"));
if (mutate) doc.layers = doc.layers.filter((l) => !new RegExp(mutate).test(l.nm));
const assets = {};
for (const f of fs.readdirSync(dir)) if (/\.(jpe?g|png|ttf)$/.test(f)) assets[f] = fs.readFileSync(path.join(dir, f)).buffer.slice(0);
const anim = ck.MakeManagedAnimation(JSON.stringify(doc), assets);
const surf = ck.MakeSurface(doc.w, doc.h);
const info = { width: doc.w, height: doc.h, colorType: ck.ColorType.RGBA_8888, alphaType: ck.AlphaType.Unpremul, colorSpace: ck.ColorSpace.SRGB };
let tr = 0, tp = 0;
const frames = [20, 60, 100, 140];
for (const f of frames) {
  const t0 = performance.now();
  const c = surf.getCanvas(); c.clear(ck.BLACK); anim.seekFrame(f); anim.render(c, ck.LTRBRect(0, 0, doc.w, doc.h)); surf.flush();
  const t1 = performance.now();
  surf.makeImageSnapshot().readPixels(0, 0, info);
  const t2 = performance.now();
  tr += t1 - t0; tp += t2 - t1;
}
console.log(`${path.basename(dir)} ${mutate ? "without /" + mutate + "/" : "full"}: render ${(tr / frames.length).toFixed(0)} ms/frame, readPixels ${(tp / frames.length).toFixed(0)} ms/frame`);
