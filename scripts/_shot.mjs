// Quick single-slide screenshot for visual QA of new chart renderers.
// Usage: node scripts/_shot.mjs <html-path> <out-png>
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const [htmlArg, outArg] = process.argv.slice(2);
if (!htmlArg || !outArg) {
  console.error('usage: node scripts/_shot.mjs <html> <out.png>');
  process.exit(1);
}
const url = pathToFileURL(resolve(htmlArg)).href;
const browser = await chromium.launch({
  args: ['--allow-file-access-from-files', '--disable-web-security'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
const errors = [];
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', (e) => errors.push(String(e)));
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForTimeout(600);
const stage = await page.$('.deck-stage section');
await (stage ?? page).screenshot({ path: resolve(outArg) });
await browser.close();
if (errors.length) { console.error('PAGE ERRORS:\n' + errors.join('\n')); process.exit(2); }
console.log('OK ' + outArg);
