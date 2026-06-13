/**
 * E2E test for run-visual-regression.mjs across html / pdf / pptx modes.
 * Uses real discovery + real rasterizers; synthesizes pixels/artifacts so it is
 * fully deterministic and needs no chromium.
 *
 * PDF/PPTX sections require system tools (poppler / LibreOffice). When those are
 * absent — the normal state in a locked-down corporate environment — those
 * sections SKIP (not FAIL), so a clean run reads "passed + skipped", never red.
 *
 * Run: node tests/visual-regression/test-harness.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';
import { PDFDocument, rgb } from 'pdf-lib';
import PptxGenJS from 'pptxgenjs';
import { discoverHtmlCases } from './run-visual-regression.mjs';
import { rasterizersAvailable } from './rasterize.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARNESS = path.join(__dirname, 'run-visual-regression.mjs');
const DIFF = path.join(__dirname, 'diff');
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'vr-h-'));
// Isolated golden dir inside TMP (passed to the harness via VR_GOLDEN_DIR) so
// the self-test never touches the real committed golden/ — earlier the cleanup
// here deleted the html goldens. Real golden/ is now untouched.
const GOLDEN = path.join(TMP, 'golden');

let passed = 0, failed = 0, skipped = 0;
const ok = (n, c, d = '') => { if (c) { console.log(`  ✓ ${n}${d ? '  ' + d : ''}`); passed++; } else { console.error(`  ✗ ${n}${d ? '  ' + d : ''}`); failed++; } };
const skip = (n, why) => { console.log(`  ⊝ ${n}  (skip: ${why})`); skipped++; };

// run harness, return {code, out}
function run(args) {
  try {
    const out = execFileSync('node', [HARNESS, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], env: { ...process.env, VR_GOLDEN_DIR: GOLDEN } });
    return { code: 0, out };
  } catch (e) {
    return { code: e.status ?? 2, out: (e.stdout || '') + (e.stderr || '') };
  }
}
const solid = (file, c) => sharp({ create: { width: 320, height: 180, channels: 3, background: c } }).png().toFile(file);

async function main() {
  const avail = rasterizersAvailable();
  console.log(`rasterizers: pdftoppm=${avail.pdftoppm}  soffice=${avail.soffice}\n`);

  // ── 1. HTML discovery against the real repo ────────────────────────────────
  console.log('1. HTML discovery (real repo)');
  const cases = discoverHtmlCases();
  const mck = cases.filter(c => c.key.startsWith('mck__'));
  const aes = cases.filter(c => c.key.startsWith('aesthetics__'));
  ok('discovers mck slides', mck.length >= 30, `${mck.length}`);
  ok('discovers aesthetics layouts', aes.length >= 18, `${aes.length}`);
  ok('keys are path-namespaced', cases.every(c => /^(mck|aesthetics|deck)__/.test(c.key)), `${cases.length} total`);
  ok('every case html exists', cases.every(c => fs.existsSync(c.html)));

  // ── 2. HTML compare via --current (synthetic pixels, real case set) ─────────
  console.log('\n2. HTML compare via --current');
  fs.rmSync(path.join(GOLDEN, 'html'), { recursive: true, force: true });
  fs.mkdirSync(path.join(GOLDEN, 'html'), { recursive: true });
  const cur = path.join(TMP, 'cur'); fs.mkdirSync(cur, { recursive: true });
  for (const c of cases) {
    await solid(path.join(GOLDEN, 'html', `${c.key}.png`), { r: 200, g: 200, b: 200 });
    await solid(path.join(cur, `${c.key}.png`), { r: 200, g: 200, b: 200 });
  }
  let r = run(['--mode', 'html', '--current', cur]);
  ok('identical → exit 0', r.code === 0, `code=${r.code}`);
  ok('identical → "No visual regression"', /No visual regression/.test(r.out));
  // perturb exactly one case
  const victim = cases[Math.floor(cases.length / 2)];
  await solid(path.join(cur, `${victim.key}.png`), { r: 220, g: 20, b: 20 });
  r = run(['--mode', 'html', '--current', cur]);
  ok('one perturbed → exit 1', r.code === 1, `code=${r.code}`);
  ok('perturbed case named in output', r.out.includes(victim.key), victim.key);
  ok('diff heatmap written', fs.existsSync(path.join(DIFF, `${victim.key}.diff.png`)));

  // ── 3. PDF mode E2E (real pdftoppm) — SKIP if poppler absent ────────────────
  console.log('\n3. PDF mode (poppler)');
  const pdfDir = path.join(TMP, 'pdf');
  if (!avail.pdftoppm) {
    skip('PDF mode E2E (3) + missing-golden (5)', 'pdftoppm absent');
  } else {
    fs.rmSync(path.join(GOLDEN, 'pdf'), { recursive: true, force: true });
    fs.mkdirSync(pdfDir, { recursive: true });
    const mkPdf = async (file, pages, extra) => {
      const d = await PDFDocument.create();
      for (let p = 0; p < pages; p++) {
        const pg = d.addPage([960, 540]);
        pg.drawText(`page ${p + 1}`, { x: 60, y: 470, size: 36 });
        pg.drawRectangle({ x: 60, y: 120, width: 300, height: 180, color: rgb(0.16, 0.55, 0.29) });
        if (extra && p === 0) pg.drawRectangle({ x: 500, y: 200, width: 200, height: 140, color: rgb(0.86, 0.08, 0.08) });
      }
      fs.writeFileSync(file, await d.save());
    };
    await mkPdf(path.join(pdfDir, 'report-a.pdf'), 1, false);
    await mkPdf(path.join(pdfDir, 'report-b.pdf'), 2, false); // multi-page → __p1/__p2 goldens
    r = run(['--mode', 'pdf', '--artifacts', pdfDir, '--save']);
    ok('pdf --save → exit 0', r.code === 0, `code=${r.code}`);
    ok('multi-page golden naming (__p2)', fs.existsSync(path.join(GOLDEN, 'pdf', 'report-b__p2.png')));
    r = run(['--mode', 'pdf', '--artifacts', pdfDir]);
    ok('pdf identical → exit 0', r.code === 0, `code=${r.code}`);
    await mkPdf(path.join(pdfDir, 'report-a.pdf'), 1, true); // add red box
    r = run(['--mode', 'pdf', '--artifacts', pdfDir]);
    ok('pdf changed → exit 1', r.code === 1, `code=${r.code}`);
    ok('pdf regression names case', r.out.includes('report-a'));

    // ── 5. missing golden is not a regression (PDF mode → needs poppler) ───────
    console.log('\n5. missing golden handling');
    fs.rmSync(path.join(GOLDEN, 'pdf'), { recursive: true, force: true });
    r = run(['--mode', 'pdf', '--artifacts', pdfDir]);
    ok('missing golden → exit 0 (not regression)', r.code === 0, `code=${r.code}`);
    ok('missing golden reported', /missing golden|missing/.test(r.out));
  }

  // ── 4. PPTX mode E2E (real LibreOffice) — SKIP if soffice absent ────────────
  console.log('\n4. PPTX mode (LibreOffice)');
  if (!avail.soffice) {
    skip('PPTX mode E2E (4)', 'soffice absent');
  } else {
    fs.rmSync(path.join(GOLDEN, 'pptx'), { recursive: true, force: true });
    const pxDir = path.join(TMP, 'pptx'); fs.mkdirSync(pxDir, { recursive: true });
    const mkPptx = async (file, revised) => {
      const p = new PptxGenJS(); p.layout = 'LAYOUT_16x9';
      const s = p.addSlide();
      s.addText(revised ? 'Q3 Variance — REVISED' : 'Q3 Variance', { x: 0.5, y: 0.4, w: 9, h: 1, fontSize: 32, bold: true });
      s.addShape(p.ShapeType.rect, { x: 0.5, y: 2, w: 3, h: 2, fill: { color: '2A8C4A' } });
      // a 'revised' deck also moves/recolors a sizeable shape — an unambiguous,
      // above-threshold visual delta (text-only edits can sit under a full-frame
      // threshold; see README "threshold" note).
      if (revised) s.addShape(p.ShapeType.rect, { x: 5.5, y: 2, w: 3.5, h: 2.5, fill: { color: 'D11414' } });
      await p.writeFile({ fileName: file });
    };
    await mkPptx(path.join(pxDir, 'deck.pptx'), false);
    r = run(['--mode', 'pptx', '--artifacts', pxDir, '--save']);
    ok('pptx --save → exit 0', r.code === 0, `code=${r.code}`);
    ok('pptx golden written', fs.existsSync(path.join(GOLDEN, 'pptx', 'deck.png')));
    r = run(['--mode', 'pptx', '--artifacts', pxDir]);
    ok('pptx identical → exit 0 (LibreOffice deterministic)', r.code === 0, `code=${r.code}`);
    await mkPptx(path.join(pxDir, 'deck.pptx'), true);
    r = run(['--mode', 'pptx', '--artifacts', pxDir]);
    ok('pptx changed → exit 1', r.code === 1, `code=${r.code}`);
  }

  // cleanup synthetic goldens we created (leave repo clean)
  for (const m of ['html', 'pdf', 'pptx']) fs.rmSync(path.join(GOLDEN, m), { recursive: true, force: true });
  fs.rmSync(DIFF, { recursive: true, force: true });
  fs.rmSync(TMP, { recursive: true, force: true });

  const verdict = failed === 0 ? 'PASS' : 'FAIL';
  console.log(`\n${verdict}: ${passed} passed, ${failed} failed, ${skipped} skipped`);
  process.exit(failed === 0 ? 0 : 1);
}
main().catch(e => { console.error(e); process.exit(2); });
