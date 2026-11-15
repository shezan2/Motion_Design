// Screenshot pinned frames from the OFFICIAL text-to-lottie player (?frame=N).
//   node tools/player_shot.mjs <project> <scene> <f1,f2,...> <outPrefix> [port]
import { createRequire } from "node:module";
const req = createRequire(import.meta.url);
// the container ships a preinstalled Playwright (with its own Chromium)
const { chromium } = req(process.env.PLAYWRIGHT_PATH ?? "playwright");
const [project, scene, frames, out, port = "3030"] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1100 }, deviceScaleFactor: 1 });
for (const f of frames.split(",")) {
  await page.goto(`http://localhost:${port}/${project}/${scene}?frame=${f}`, { waitUntil: "networkidle" });
  await page.waitForSelector("#main-canvas");
  await page.waitForTimeout(1500);
  const canvas = await page.$("#main-canvas");
  await canvas.screenshot({ path: `${out}_${String(f).padStart(4, "0")}.png` });
  console.log(`${out}_${f}`);
}
await browser.close();
