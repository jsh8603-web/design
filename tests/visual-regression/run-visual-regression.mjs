#!/usr/bin/env node
/**
 * Visual Regression — deterministic golden-image comparison across the whole pipeline.
 *
 * Modes (every path funnels through a "producer" → PNG pages → diff vs golden):
 *   --mode html  (default)  render slide HTML via src/editor/screenshot.js  [Layer A]
 *   --mode pdf              rasterize *.pdf via poppler  pdftoppm            [Layer B]
 *   --mode pptx             rasterize *.pptx via LibreOffice → pdf → png     [Layer C]
 *
 * Engine: tests/visual-regression/diff.mjs (sharp). Rasterizers: tests/.../rasterize.mjs
 * (system tools, detect+skip). Zero new npm deps. No network / OAuth / Vision.
 *
 * Common flags:
 *   --save                 write goldens instead of comparing
 *   --threshold <r>        max changed-pixel ratio before regression (default 0.005)
 *   --current <dir>        (html) skip render; read <dir>/<key>.png  (CI/offline)
 *   --artifacts <dir>      (pdf|pptx) dir of artifacts to rasterize
 *
 * Exit: 0 = no regression, 1 = regression, 2 = environment error.
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { diffImages } from './diff.mjs';
import { rasterizersAvailable, pdfToPngs, pptxToPngs } from './rasterize.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..', '..');
const GOLDEN_DIR = path.join(__dirname, 'golden');
const DIFF_DIR = path.join(__dirname, 'diff');
const DEFAULT_THRESHOLD = 0.005;

const C = { red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m', cyan: '\x1b[36m', bold: '\x1b[1m', dim: '\x1b[2m', reset: '\x1b[0m' };

// CSS injected before every navigation so transient animation/transition frames
// can never make a render non-deterministic (determinism rule #2).
const FREEZE_CSS = '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}';

function parseArgs() {
  const a = process.argv.slice(2);
  const o = { mode: 'html', save: false, threshold: DEFAULT_THRESHOLD, current: null, artifacts: null };
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--mode' && a[i + 1]) o.mode = a[++i];
    else if (a[i] === '--save') o.save = true;
    else if (a[i] === '--threshold' && a[i + 1]) o.threshold = parseFloat(a[++i]);
    else if (a[i] === '--current' && a[i + 1]) o.current = path.resolve(a[++i]);
    else if (a[i] === '--artifacts' && a[i + 1]) o.artifacts = path.resolve(a[++i]);
  }
  return o;
}

const goldenSub = (mode) => path.join(GOLDEN_DIR, mode);

// ── HTML case discovery (Layer A) ─────────────────────────────────────────────
export function discoverHtmlCases() {
  const cases = [];
  const add = (key, html) => cases.push({ key, html });

  const mckDir = path.join(ROOT, 'design-system', 'mck', 'slides');
  if (fs.existsSync(mckDir)) {
    for (const f of fs.readdirSync(mckDir).filter(x => /\.html$/.test(x) && x !== 'index.html').sort()) {
      add(`mck__${f.replace(/\.html$/, '')}`, path.join(mckDir, f));
    }
  }
  const aesDir = path.join(ROOT, 'design-system', 'aesthetics');
  if (fs.existsSync(aesDir)) {
    for (const sub of fs.readdirSync(aesDir).sort()) {
      const subDir = path.join(aesDir, sub);
      if (!fs.statSync(subDir).isDirectory()) continue;
      for (const f of fs.readdirSync(subDir).filter(x => /\.html$/.test(x) && x !== 'index.html').sort()) {
        add(`aesthetics__${sub}__${f.replace(/\.html$/, '')}`, path.join(subDir, f));
      }
    }
  }
  const decksDir = path.join(ROOT, 'slides');
  if (fs.existsSync(decksDir)) {
    for (const slug of fs.readdirSync(decksDir).sort()) {
      const d = path.join(decksDir, slug);
      if (!fs.statSync(d).isDirectory()) continue;
      for (const f of fs.readdirSync(d).filter(x => /^slide-\d+[^]*\.html$/.test(x)).sort()) {
        add(`deck__${slug}__${f.replace(/\.html$/, '')}`, path.join(d, f));
      }
    }
  }
  return cases;
}

// ── Artifact discovery (Layers B/C) ───────────────────────────────────────────
export function discoverArtifactCases(dir, ext) {
  if (!dir || !fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.toLowerCase().endsWith(ext))
    .sort()
    .map(f => ({ key: f.slice(0, -ext.length), file: path.join(dir, f) }));
}

// ── Producers: case → PNG page paths ──────────────────────────────────────────
async function produceHtml(c, outDir, ctx) {
  if (ctx.currentDir) {
    const src = path.join(ctx.currentDir, `${c.key}.png`);
    if (!fs.existsSync(src)) throw new Error(`current image missing: ${src}`);
    const dst = path.join(outDir, `${c.key}.png`);
    fs.copyFileSync(src, dst);
    return [dst];
  }
  const out = path.join(outDir, `${c.key}.png`);
  await ctx.captureSlideScreenshot(ctx.page, path.basename(c.html), out, path.dirname(c.html));
  return [out];
}
async function producePdf(c, outDir) { return pdfToPngs(c.file, path.join(outDir, c.key)); }
async function producePptx(c, outDir) { return pptxToPngs(c.file, path.join(outDir, c.key)); }

function goldenName(key, pageIdx, pageCount) {
  return pageCount <= 1 ? `${key}.png` : `${key}__p${pageIdx + 1}.png`;
}

async function main() {
  const opts = parseArgs();
  if (!['html', 'pdf', 'pptx'].includes(opts.mode)) {
    console.error(`${C.red}--mode must be html|pdf|pptx${C.reset}`); process.exit(2);
  }

  let cases, produce, ctx = {};
  if (opts.mode === 'html') {
    cases = discoverHtmlCases();
    produce = produceHtml;
  } else {
    const avail = rasterizersAvailable();
    const need = opts.mode === 'pdf' ? avail.pdftoppm : (avail.pdftoppm && avail.soffice);
    if (!need) {
      console.error(`${C.yellow}Rasterizer unavailable for --mode ${opts.mode} (pdftoppm=${avail.pdftoppm}, soffice=${avail.soffice}) — skipping.${C.reset}`);
      process.exit(2);
    }
    const dir = opts.artifacts || path.join(__dirname, 'fixtures', opts.mode);
    cases = discoverArtifactCases(dir, '.' + opts.mode);
    produce = opts.mode === 'pdf' ? producePdf : producePptx;
    if (cases.length === 0) console.error(`${C.yellow}No *.${opts.mode} found in ${dir}${C.reset}`);
  }

  if (cases.length === 0) { console.error(`${C.red}No cases for --mode ${opts.mode}${C.reset}`); process.exit(2); }

  let browser = null;
  if (opts.mode === 'html' && !opts.current) {
    try {
      const mod = await import(pathToFileURL(path.join(ROOT, 'src', 'editor', 'screenshot.js')).href);
      const b = await mod.createScreenshotBrowser();
      browser = b.browser;
      const { page } = await mod.createScreenshotPage(browser);
      await page.addInitScript((css) => {
        const inject = () => { const s = document.createElement('style'); s.textContent = css; document.documentElement.appendChild(s); };
        if (document.documentElement) inject(); else document.addEventListener('DOMContentLoaded', inject);
      }, FREEZE_CSS);
      ctx = { page, captureSlideScreenshot: mod.captureSlideScreenshot };
    } catch (err) {
      console.error(`${C.red}Cannot launch Chromium.${C.reset} ${C.dim}${err.message}${C.reset}`);
      console.error(`  Fix: ${C.cyan}npx playwright install chromium${C.reset}  or use ${C.cyan}--current <dir>${C.reset}`);
      process.exit(2);
    }
  } else if (opts.current) {
    ctx = { currentDir: opts.current };
    console.log(`${C.dim}html: using pre-rendered candidates from ${opts.current}${C.reset}`);
  }

  const gdir = goldenSub(opts.mode);
  fs.mkdirSync(gdir, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'vr-'));

  console.log(`${C.bold}Visual Regression [${opts.mode}]${C.reset}  (${cases.length} cases, threshold ${(opts.threshold * 100).toFixed(2)}%)`);
  console.log('━'.repeat(54));

  let regressions = 0, saved = 0, missing = 0, comparedPages = 0;
  for (const c of cases) {
    let pages;
    try { pages = await produce(c, tmp, ctx); }
    catch (err) {
      if (err.code === 'ENOTOOL') { console.log(`${C.yellow}⊝${C.reset}  ${c.key}: ${err.message}`); continue; }
      console.log(`${C.yellow}⚠${C.reset}  ${c.key}: produce failed — ${err.message}`); regressions++; continue;
    }
    if (!pages.length) { console.log(`${C.yellow}⚠${C.reset}  ${c.key}: 0 pages`); regressions++; continue; }

    let worst = 0, caseRegressed = false, missAny = false;
    for (let i = 0; i < pages.length; i++) {
      const gName = goldenName(c.key, i, pages.length);
      const gPath = path.join(gdir, gName);
      if (opts.save) { fs.copyFileSync(pages[i], gPath); continue; }
      if (!fs.existsSync(gPath)) { missAny = true; continue; }
      const r = await diffImages(gPath, pages[i], { heatmap: true });
      comparedPages++;
      if (r.ratio > worst) worst = r.ratio;
      if (r.ratio > opts.threshold) {
        fs.mkdirSync(DIFF_DIR, { recursive: true });
        fs.writeFileSync(path.join(DIFF_DIR, `${gName.replace(/\.png$/, '')}.diff.png`), r.diffPng);
        caseRegressed = true;
      }
    }

    if (opts.save) { console.log(`${C.green}✔${C.reset}  ${c.key}: ${pages.length} golden(s)`); saved += pages.length; }
    else if (missAny) { console.log(`${C.yellow}?${C.reset}  ${c.key}: golden missing ${C.dim}(run --save)${C.reset}`); missing++; }
    else if (caseRegressed) { console.log(`${C.red}✗  ${c.key}: REGRESSION ${(worst * 100).toFixed(3)}% → diff/${C.reset}`); regressions++; }
    else { console.log(`${C.green}✔${C.reset}  ${c.key}: ${(worst * 100).toFixed(3)}% (${pages.length}p)`); }
  }

  if (browser) await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });

  console.log('━'.repeat(54));
  if (opts.save) { console.log(`${C.green}${C.bold}${saved} golden(s) saved → ${path.relative(ROOT, gdir)}${C.reset}`); process.exit(0); }
  console.log(`${C.dim}compared ${comparedPages} page(s)${C.reset}`);
  if (missing > 0) console.log(`${C.yellow}${missing} case(s) missing golden${C.reset}`);
  if (regressions > 0) { console.log(`${C.red}${C.bold}REGRESSION: ${regressions} case(s)${C.reset}`); process.exit(1); }
  console.log(`${C.green}${C.bold}No visual regression${C.reset}`);
  process.exit(0);
}

// Run only when invoked directly (allows importing discovery in tests).
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(e => { console.error(e); process.exit(2); });
}
