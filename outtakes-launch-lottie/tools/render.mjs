// Render Lottie scenes with the same engine as the official player
// (canvaskit-wasm "full" build = Skia Skottie), offline in Node.
//
//   node tools/render.mjs still <sceneDir> <frame>[,<frame>...] <outPrefix>
//   node tools/render.mjs video <projectDir> <out.mp4> [audio.wav]
//
// Scenes are loaded exactly like the player's loadScene(): lottie.json plus
// every image/font file in the scene folder passed to MakeManagedAnimation.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const require = createRequire(import.meta.url);
const CanvasKitInit = require("canvaskit-wasm/full");
const ck = await CanvasKitInit({
  locateFile: (f) => require.resolve("canvaskit-wasm/full").replace(/canvaskit\.js$/, f),
});

const ASSET_RE = /\.(png|jpe?g|webp|gif|svg|ttf|otf|ttc)$/i;

function loadScene(dir) {
  const json = fs.readFileSync(path.join(dir, "lottie.json"), "utf8");
  const assets = {};
  for (const f of fs.readdirSync(dir)) {
    if (ASSET_RE.test(f)) assets[f] = fs.readFileSync(path.join(dir, f)).buffer.slice(0);
  }
  const anim = ck.MakeManagedAnimation(json, assets);
  if (!anim) throw new Error(`Skottie could not parse ${dir}`);
  const doc = JSON.parse(json);
  return { anim, w: doc.w, h: doc.h, frames: doc.op - doc.ip };
}

function renderFrame(scene, surface, frame) {
  const canvas = surface.getCanvas();
  canvas.clear(ck.BLACK);
  scene.anim.seekFrame(frame);
  scene.anim.render(canvas, ck.LTRBRect(0, 0, scene.w, scene.h));
  surface.flush();
}

const [mode, a, b, c] = process.argv.slice(2);

if (mode === "still") {
  const scene = loadScene(a);
  const surface = ck.MakeSurface(scene.w, scene.h);
  for (const f of b.split(",").map(Number)) {
    renderFrame(scene, surface, f);
    const png = surface.makeImageSnapshot().encodeToBytes();
    const out = `${c}_${String(f).padStart(4, "0")}.png`;
    fs.writeFileSync(out, png);
    console.log(out);
  }
} else if (mode === "video") {
  const sceneDirs = fs
    .readdirSync(a)
    .filter((d) => /^scene-\d+$/.test(d) && fs.existsSync(path.join(a, d, "lottie.json")))
    .sort((x, y) => Number(x.split("-")[1]) - Number(y.split("-")[1]))
    .map((d) => path.join(a, d));
  const first = loadScene(sceneDirs[0]);
  const { w, h } = first;
  first.anim.delete();
  const args = ["-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", `${w}x${h}`, "-r", "30", "-i", "-"];
  if (c) args.push("-i", c, "-c:a", "aac", "-b:a", "320k", "-shortest");
  args.push("-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", b);
  const ff = spawn("ffmpeg", args, { stdio: ["pipe", "inherit", "inherit"] });
  const surface = ck.MakeSurface(w, h);
  const info = { width: w, height: h, colorType: ck.ColorType.RGBA_8888, alphaType: ck.AlphaType.Unpremul, colorSpace: ck.ColorSpace.SRGB };
  let total = 0;
  for (const dir of sceneDirs) {
    const scene = loadScene(dir);
    const t0 = Date.now();
    for (let f = 0; f < scene.frames; f++) {
      renderFrame(scene, surface, f);
      const px = surface.makeImageSnapshot().readPixels(0, 0, info);
      if (!ff.stdin.write(Buffer.from(px.buffer, px.byteOffset, px.byteLength))) {
        await new Promise((r) => ff.stdin.once("drain", r));
      }
    }
    total += scene.frames;
    console.log(`${path.basename(dir)}: ${scene.frames} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    scene.anim.delete();
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  console.log(`wrote ${b} (${total} frames, ${(total / 30).toFixed(2)}s)`);
} else if (mode === "scene") {
  // one scene -> one video-only segment; film grain is added here (cheap in ffmpeg,
  // very expensive as a Skottie overlay layer)
  const scene = loadScene(a);
  const { w, h } = scene;
  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", `${w}x${h}`, "-r", "30",
    "-i", "-", "-vf", "noise=c0s=5:c0f=t+u", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", b],
    { stdio: ["pipe", "inherit", "inherit"] });
  const surface = ck.MakeSurface(w, h);
  const info = { width: w, height: h, colorType: ck.ColorType.RGBA_8888, alphaType: ck.AlphaType.Unpremul, colorSpace: ck.ColorSpace.SRGB };
  const t0 = Date.now();
  for (let f = 0; f < scene.frames; f++) {
    renderFrame(scene, surface, f);
    const px = surface.makeImageSnapshot().readPixels(0, 0, info);
    if (!ff.stdin.write(Buffer.from(px.buffer, px.byteOffset, px.byteLength))) {
      await new Promise((r) => ff.stdin.once("drain", r));
    }
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  console.log(`${path.basename(a)} -> ${b}: ${scene.frames} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
} else {
  console.error("usage: render.mjs still <sceneDir> <frames> <outPrefix> | video <projectDir> <out.mp4> [audio]");
  process.exit(1);
}
