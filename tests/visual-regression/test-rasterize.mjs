/**
 * Ground-truth test for output-layer regression (Layer B = PDF, Layer C = PPTX).
 * Generates artifacts with the REAL engines (pdf-lib, pptxgenjs), rasterizes via
 * system poppler/LibreOffice, and diffs with the proven diff.mjs.
 *
 * Establishes: (1) identical artifact → ~0 ratio, (2) determinism of the
 * rasterizer (same input twice → 0), (3) a real change → detected.
 *
 * Run: node tests/visual-regression/test-rasterize.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { PDFDocument, rgb } from 'pdf-lib';
import PptxGenJS from 'pptxgenjs';
import { diffImages } from './diff.mjs';
import { rasterizersAvailable, pdfToPngs, pptxToPngs } from './rasterize.mjs';

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'vr-gt-'));

let passed = 0, failed = 0, skipped = 0;
const ok = (n, c, d = '') => { if (c) { console.log(`  ✓ ${n}${d ? '  ' + d : ''}`); passed++; } else { console.error(`  ✗ ${n}${d ? '  ' + d : ''}`); failed++; } };
const skip = (n, why) => { console.log(`  ⊝ ${n}  (skip: ${why})`); skipped++; };

// ── build two PDFs that differ by one rectangle ───────────────────────────────
async function makePdf(file, withExtraBox) {
  const doc = await PDFDocument.create();
  const page = doc.addPage([960, 540]);
  page.drawText('FP&A Report', { x: 60, y: 470, size: 36 });
  page.drawRectangle({ x: 60, y: 120, width: 320, height: 200, color: rgb(0.16, 0.55, 0.29) });
  page.drawText('Revenue bridge', { x: 60, y: 90, size: 18 });
  if (withExtraBox) page.drawRectangle({ x: 480, y: 200, width: 180, height: 120, color: rgb(0.86, 0.08, 0.08) });
  fs.writeFileSync(file, await doc.save());
}

// ── build two PPTX via pptxgenjs (the repo's real PPTX engine) ─────────────────
async function makePptx(file, altText) {
  const p = new PptxGenJS();
  p.layout = 'LAYOUT_16x9';
  const s = p.addSlide();
  s.addText(altText ? 'Q3 Variance — REVISED' : 'Q3 Variance', { x: 0.5, y: 0.4, w: 9, h: 1, fontSize: 32, bold: true });
  s.addShape(p.ShapeType.rect, { x: 0.5, y: 2, w: 3, h: 2, fill: { color: '2A8C4A' } });
  s.addText('실적 vs 목표', { x: 0.5, y: 4.2, w: 4, h: 0.5, fontSize: 16 });
  await p.writeFile({ fileName: file });
}

async function main() {
  const avail = rasterizersAvailable();
  console.log(`rasterizers: pdftoppm=${avail.pdftoppm}  soffice=${avail.soffice}\n`);

  // ===== Layer B: PDF =====
  console.log('Layer B — PDF rasterization regression');
  if (!avail.pdftoppm) {
    skip('PDF layer', 'pdftoppm absent');
  } else {
    const pdfA = path.join(TMP, 'a.pdf'), pdfB = path.join(TMP, 'b.pdf');
    await makePdf(pdfA, false);
    await makePdf(pdfB, true); // adds red box
    const pa = await pdfToPngs(pdfA, path.join(TMP, 'pa'));
    const pa2 = await pdfToPngs(pdfA, path.join(TMP, 'pa2')); // same input again
    const pb = await pdfToPngs(pdfB, path.join(TMP, 'pb'));
    ok('PDF renders 1 page', pa.length === 1, `pages=${pa.length}`);
    const det = await diffImages(pa[0], pa2[0], { heatmap: false });
    ok('rasterizer deterministic (same PDF twice → 0)', det.ratio === 0, `ratio=${det.ratio}`);
    const self = await diffImages(pa[0], pa[0], { heatmap: false });
    ok('identical page → 0', self.ratio === 0, `ratio=${self.ratio}`);
    const chg = await diffImages(pa[0], pb[0], { heatmap: true });
    ok('added red box → detected', chg.ratio > 0.01, `ratio=${chg.ratio.toFixed(4)}`);
    fs.mkdirSync(path.join(__dirname, '_selftest-out'), { recursive: true });
    fs.writeFileSync(path.join(__dirname, '_selftest-out', 'pdf-diff.png'), chg.diffPng);
  }

  // ===== Layer C: PPTX =====
  console.log('\nLayer C — PPTX rasterization regression (LibreOffice)');
  if (!avail.soffice) {
    skip('PPTX layer', 'soffice absent');
  } else {
    const pxA = path.join(TMP, 'a.pptx'), pxB = path.join(TMP, 'b.pptx');
    await makePptx(pxA, false);
    await makePptx(pxB, true); // title text changed
    const ra = await pptxToPngs(pxA, path.join(TMP, 'ra'));
    const ra2 = await pptxToPngs(pxA, path.join(TMP, 'ra2'));
    const rb = await pptxToPngs(pxB, path.join(TMP, 'rb'));
    ok('PPTX renders >=1 page', ra.length >= 1, `pages=${ra.length}`);
    const det = await diffImages(ra[0], ra2[0], { heatmap: false });
    // LibreOffice determinism is the key risk — assert it holds on identical input
    ok('LibreOffice deterministic (same PPTX twice → ~0)', det.ratio < 0.001, `ratio=${det.ratio.toFixed(5)}`);
    const chg = await diffImages(ra[0], rb[0], { heatmap: true });
    ok('changed title text → detected', chg.ratio > 0.001, `ratio=${chg.ratio.toFixed(4)}`);
    fs.writeFileSync(path.join(__dirname, '_selftest-out', 'pptx-diff.png'), chg.diffPng);
  }

  fs.rmSync(TMP, { recursive: true, force: true });
  console.log(`\n${failed === 0 ? 'PASS' : 'FAIL'}: ${passed} passed, ${failed} failed, ${skipped} skipped`);
  process.exit(failed === 0 ? 0 : 1);
}
main().catch(e => { console.error(e); process.exit(2); });
