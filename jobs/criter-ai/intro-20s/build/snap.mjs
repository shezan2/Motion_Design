// Stills at chosen times: node snap.mjs <outDir> <t1> <t2> ... [--scale 0.5] [--query mascot=0]
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const args = process.argv.slice(2);
let scale = 1, query = '';
const times = [];
let out = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--scale') scale = parseFloat(args[++i]);
  else if (args[i] === '--query') query = args[++i];
  else if (out === null) out = args[i];
  else times.push(parseFloat(args[i]));
}
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text()); });
page.on('pageerror', (e) => console.log('[pageerror]', e.message));
await page.goto('file://' + resolve(here, 'index.html') + (query ? '?' + query : ''));
await page.evaluate(() => window.READY);
for (const t of times) {
  await page.evaluate((tt) => window.seek(tt), t);
  const name = `t${t.toFixed(2).padStart(5, '0')}.png`;
  await page.locator('#stage').screenshot({ path: resolve(out, name) });
  console.log(name);
}
await browser.close();
