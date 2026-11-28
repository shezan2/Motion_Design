// Render the film to MP4: Playwright frames -> ffmpeg, with real motion blur from sub-frames.
//   node render.mjs --out ../out/draft.mp4 [--fps 60] [--sub 4] [--scale 1] [--workers 3] [--crf 16] [--from 0] [--to 20] [--query mascot=1]
// Each output frame averages `sub` renders spread over a 180-degree shutter (ffmpeg tmix), so fast moves smear like a camera.
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, rmSync, existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const opt = { out: '../out/draft.mp4', fps: 60, sub: 4, scale: 1, workers: 3, crf: 16, from: 0, to: null, query: '', preset: 'slow', shutter: 0.5 };
const a = process.argv.slice(2);
for (let i = 0; i < a.length; i += 2) {
  const k = a[i].replace(/^--/, '');
  opt[k] = ['out', 'query', 'preset'].includes(k) ? a[i + 1] : parseFloat(a[i + 1]);
}
const out = resolve(here, opt.out);
mkdirSync(dirname(out), { recursive: true });
const tmp = out + '.parts';
rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });

const url = 'file://' + resolve(here, 'index.html') + (opt.query ? '?' + opt.query : '');
const W = Math.round(1920 * opt.scale), H = Math.round(1080 * opt.scale);

// probe duration and cues
const probeB = await chromium.launch();
const probeP = await probeB.newPage({ viewport: { width: 1920, height: 1080 } });
await probeP.goto(url);
await probeP.evaluate(() => window.READY);
const { DUR, CUES, DIPS } = await probeP.evaluate(() => ({ DUR: window.DUR, CUES: window.CUES, DIPS: window.DIPS }));
await probeB.close();
const to = opt.to ?? DUR;
writeFileSync(out.replace(/\.mp4$/, '.cues.json'), JSON.stringify({ dur: DUR, fps: opt.fps, cues: CUES, dips: DIPS }, null, 1));

const f0 = Math.round(opt.from * opt.fps), f1 = Math.round(to * opt.fps); // [f0, f1)
const total = f1 - f0;
const per = Math.ceil(total / opt.workers);
const chunks = [];
for (let w = 0; w < opt.workers; w++) {
  const s = f0 + w * per, e = Math.min(f1, s + per);
  if (s < e) chunks.push({ w, s, e, file: join(tmp, `c${String(w).padStart(2, '0')}.mp4`) });
}

const S = Math.max(1, Math.round(opt.sub));
const vf = [
  ...(S > 1 ? [`tmix=frames=${S}:weights='${Array(S).fill(1).join(' ')}'`, `select='eq(mod(n\\,${S})\\,${S - 1})'`, `setpts=N/(${opt.fps}*TB)`] : []),
  'scale=out_color_matrix=bt709:out_range=tv', 'format=yuv420p',
].join(',');

async function renderChunk(c) {
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: opt.scale });
  await page.goto(url);
  await page.evaluate(() => window.READY);
  const cdp = await page.context().newCDPSession(page);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(opt.fps * S), '-i', '-', '-vf', vf, '-r', String(opt.fps),
    '-c:v', 'libx264', '-preset', opt.preset, '-crf', String(opt.crf), '-pix_fmt', 'yuv420p',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', c.file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', (code) => (code === 0 ? res() : rej(new Error('ffmpeg ' + code)))));
  const t0 = Date.now();
  for (let f = c.s; f < c.e; f++) {
    for (let j = 0; j < S; j++) {
      const off = S > 1 ? ((j + 0.5) / S - 0.5) * (opt.shutter / opt.fps) : 0;
      const t = Math.min(Math.max(f / opt.fps + off, 0), DUR - 1e-4);
      await page.evaluate((tt) => window.seek(tt), t);
      // raw CDP capture ignores deviceScaleFactor here, so supersampled (4K) renders go through page.screenshot
      const buf = opt.scale === 1
        ? Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true, captureBeyondViewport: false })).data, 'base64')
        : await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    if ((f - c.s) % 60 === 0) process.stdout.write(`[w${c.w}] ${f - c.s}/${c.e - c.s} frames, ${((Date.now() - t0) / 1000).toFixed(0)} s\n`);
  }
  ff.stdin.end();
  await done;
  await browser.close();
}

const t0 = Date.now();
await Promise.all(chunks.map(renderChunk));
const list = join(tmp, 'list.txt');
writeFileSync(list, chunks.map((c) => `file '${c.file}'`).join('\n'));
await new Promise((res, rej) => {
  const p = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', '-movflags', '+faststart', out], { stdio: 'inherit' });
  p.on('close', (code) => (code === 0 ? res() : rej(new Error('concat ' + code))));
});
rmSync(tmp, { recursive: true, force: true });
const probe = require('node:child_process').execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', out]).toString().trim();
console.log(`wrote ${out} (${total} frames @ ${opt.fps} fps, ${S} sub-frames, encoded ${probe.replace(',', 'x')}, asked ${W}x${H}) in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
process.exit(0);
