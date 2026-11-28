// OmniGro promo renderer: headless Chromium (Playwright) + ffmpeg.
//
//   node build/render.cjs still 0,60,180 out/stills        # PNG stills of chosen frames (no motion blur)
//   node build/render.cjs frames out/frames [from] [to]     # PNG sequence with 4-sub-frame shutter blur
//   node build/render.cjs cues audio/cues.json              # write the SFX cue list from the timeline
//
// Every frame is a pure function of time (FILM.render(t)), so any frame or range can be re-rendered alone.
// Workers: JOBS=3 (default). Sub-frames: SUB=4 (180-degree shutter), SUB=1 for a fast draft. CUT=vo renders the voiced cut (v3).
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const JOB = path.resolve(__dirname, '..');
const W = 1920, H = 1080, FPS = 30, TOTAL = 600;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.css': 'text/css' };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(JOB, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(JOB) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

async function openPage(browser, port) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('pageerror:', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.goto(`http://127.0.0.1:${port}/build/film.html${process.env.CUT ? '?cut=' + process.env.CUT : ''}`, { waitUntil: 'load' });
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); FILM.init(); });
  return page;
}

async function shot(page, t) {
  await page.evaluate(tt => FILM.render(tt), t);
  return page.screenshot({ type: 'png', clip: { x: 0, y: 0, width: W, height: H }, animations: 'disabled' });
}

async function main() {
  const [mode, a1, a2, a3] = process.argv.slice(2);
  const srv = await serve(); const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-lcd-text', '--force-color-profile=srgb'] });
  try {
    if (mode === 'still') {
      const frames = a1.split(',').map(Number); const out = path.resolve(a2); fs.mkdirSync(out, { recursive: true });
      const page = await openPage(browser, port);
      for (const f of frames) { fs.writeFileSync(path.join(out, `f${String(f).padStart(3, '0')}.png`), await shot(page, f)); }
      console.log(`stills -> ${out}`);
    } else if (mode === 'eval') {
      const page = await openPage(browser, port);
      console.log(JSON.stringify(await page.evaluate(a1), null, 1));
    } else if (mode === 'cues') {
      const page = await openPage(browser, port);
      const cues = await page.evaluate(() => FILM.cues);
      fs.mkdirSync(path.dirname(path.resolve(a1)), { recursive: true });
      fs.writeFileSync(path.resolve(a1), JSON.stringify({ fps: FPS, total: TOTAL, cues }, null, 1));
      console.log(`${cues.length} cues -> ${a1}`);
    } else if (mode === 'frames') {
      const out = path.resolve(a1); fs.mkdirSync(out, { recursive: true });
      const from = a2 ? +a2 : 0, to = a3 ? +a3 : TOTAL;
      const SUB = +(process.env.SUB || 4), JOBS = +(process.env.JOBS || 3);
      // sub-frame offsets: centres of SUB equal bins across half a frame (180-degree shutter)
      const offs = Array.from({ length: SUB }, (_, k) => SUB === 1 ? 0 : -0.25 + (k + 0.5) * 0.5 / SUB);
      const n = to - from, per = Math.ceil(n / JOBS);
      const t0 = Date.now();
      await Promise.all(Array.from({ length: JOBS }, async (_, w) => {
        const a = from + w * per, b = Math.min(to, a + per); if (a >= b) return;
        const page = await openPage(browser, port);
        const vf = SUB > 1 ? `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})'` : 'null';
        const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS * SUB), '-i', '-',
          '-vf', vf, '-fps_mode', 'passthrough', '-start_number', String(a), path.join(out, 'f%04d.png')], { stdio: ['pipe', 'inherit', 'inherit'] });
        const done = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c))));
        for (let f = a; f < b; f++) {
          for (const o of offs) { const buf = await shot(page, f + o); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
          if (w === 0 && (f - a) % 20 === 0) console.log(`frame ${f}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
        }
        ff.stdin.end(); await done; await page.close();
      }));
      console.log(`frames ${from}-${to - 1} -> ${out} in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    } else {
      console.log('modes: still | frames | cues');
    }
  } finally { await browser.close(); srv.close(); }
}
main().catch(e => { console.error(e); process.exit(1); });
