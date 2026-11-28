// Write the film's sound cues (single source of truth: film.js) to a JSON file: node export_cues.mjs <out.json>
import { createRequire } from 'node:module';
import { writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto('file://' + resolve(here, 'index.html'));
await page.evaluate(() => window.READY);
const data = await page.evaluate(() => ({ dur: window.DUR, cues: window.CUES, dips: window.DIPS }));
writeFileSync(process.argv[2], JSON.stringify(data, null, 1));
console.log(`wrote ${data.cues.length} cues to ${process.argv[2]}`);
await browser.close();
