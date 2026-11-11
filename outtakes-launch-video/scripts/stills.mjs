// Render review stills for both formats: node scripts/stills.mjs 130,200,...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";

const frames = (process.argv[2] ?? "130").split(",").map(Number);
const ids = (process.argv[3] ?? "Outtakes-16x9,Outtakes-9x16").split(",");
const scale = Number(process.argv[4] ?? 0.5);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const browserExecutable = process.env.REMOTION_CHROME ?? null;
for (const id of ids) {
  const comp = await selectComposition({ serveUrl, id, inputProps: { withAudio: false }, browserExecutable });
  for (const frame of frames) {
    const output = `out/stills/${id === "Outtakes-16x9" ? "l" : "p"}_${String(frame).padStart(4, "0")}.jpg`;
    await renderStill({ composition: comp, serveUrl, output, frame, scale, inputProps: { withAudio: false }, browserExecutable, imageFormat: "jpeg", jpegQuality: 85 });
    console.log(output);
  }
}
