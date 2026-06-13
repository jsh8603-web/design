/**
 * Ground-truth test for embed-fonts.mjs (embedFonts + guardFonts).
 * Verifies OOXML structure, python-pptx openability, LibreOffice render,
 * and that the repo's woff2 can be converted to ttf (fonttools) for embedding.
 *
 * guardFonts() needs no system tools — it always runs. The embed/render/convert
 * checks need a system TTF, python3, and LibreOffice; when those are absent —
 * the normal state in a locked-down corporate Windows box — they SKIP (not FAIL),
 * so a clean local run reads "passed + skipped", never red. CI (ubuntu) installs
 * the tools, so there it runs the full 13/13.
 *
 * Run: node tests/visual-regression/test-fonts.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import JSZip from 'jszip';
import PptxGenJS from 'pptxgenjs';
import { embedFonts, guardFonts } from './embed-fonts.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..', '..');
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'vr-font-'));
const TTF = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf';
const TTF_B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf';

const has = (cmd, args = ['--version']) => { try { execFileSync(cmd, args, { stdio: 'ignore' }); return true; } catch { return false; } };
const HAS_TTF = fs.existsSync(TTF) && fs.existsSync(TTF_B);
const HAS_PY = has('python3');
const HAS_SOFFICE = has('soffice');

let passed = 0, failed = 0, skipped = 0;
const ok = (n, c, d = '') => { if (c) { console.log(`  ✓ ${n}${d ? '  ' + d : ''}`); passed++; } else { console.error(`  ✗ ${n}${d ? '  ' + d : ''}`); failed++; } };
const skip = (n, why) => { console.log(`  ⊝ ${n}  (skip: ${why})`); skipped++; };

async function makePptx(file, typeface) {
  const p = new PptxGenJS(); p.layout = 'LAYOUT_16x9';
  const s = p.addSlide();
  s.addText('실적 요약 Q3', { x: 0.5, y: 0.5, w: 9, h: 1, fontSize: 32, bold: true, fontFace: typeface });
  s.addText('Revenue bridge', { x: 0.5, y: 2, w: 9, h: 0.6, fontSize: 18, fontFace: typeface });
  await p.writeFile({ fileName: file });
}

async function main() {
  console.log(`tools: TTF=${HAS_TTF}  python3=${HAS_PY}  soffice=${HAS_SOFFICE}\n`);

  // ── guard: shipped typeface passes, rogue typeface fails (no tools needed) ───
  console.log('guardFonts()');
  const good = path.join(TMP, 'good.pptx'); await makePptx(good, 'Pretendard');
  const bad = path.join(TMP, 'bad.pptx'); await makePptx(bad, 'Comic Sans MS');
  const gGood = await guardFonts(good);
  ok('shipped typeface (Pretendard) → ok', gGood.ok, `used=${gGood.used.join(',')}`);
  const gBad = await guardFonts(bad);
  ok('rogue typeface (Comic Sans MS) → offender', !gBad.ok && gBad.offenders.includes('Comic Sans MS'), `offenders=${gBad.offenders.join(',')}`);

  // ── embed: structure + openability + render (needs system TTF) ──────────────
  console.log('\nembedFonts()');
  if (!HAS_TTF) {
    skip('embed structure + python-pptx + LibreOffice (5)', 'system TTF absent');
  } else {
    const out = path.join(TMP, 'embedded.pptx');
    const res = await embedFonts(good, out, [{ typeface: 'Pretendard', regular: TTF, bold: TTF_B }]);
    ok('reports fonts embedded', res.fontsEmbedded === 2, `n=${res.fontsEmbedded}`);

    const zip = await JSZip.loadAsync(fs.readFileSync(out));
    const names = Object.keys(zip.files);
    ok('ppt/fonts/*.fntdata present', names.some(n => /ppt\/fonts\/font\d+\.fntdata/.test(n)), names.filter(n => /fonts\//.test(n)).join(','));
    const ct = await zip.file('[Content_Types].xml').async('string');
    ok('[Content_Types] declares fntdata', /Extension="fntdata"/.test(ct));
    const rels = await zip.file('ppt/_rels/presentation.xml.rels').async('string');
    ok('rels has font relationship', /relationships\/font/.test(rels));
    const pres = await zip.file('ppt/presentation.xml').async('string');
    ok('presentation.xml has embeddedFontLst', /<p:embeddedFontLst>/.test(pres));
    ok('presentation.xml has embedTrueTypeFonts', /embedTrueTypeFonts="1"/.test(pres));
    ok('embeddedFont references typeface', /<p:font typeface="Pretendard"\/>/.test(pres));

    // python-pptx must still open the package (structural validity)
    if (!HAS_PY) {
      skip('python-pptx opens embedded deck', 'python3 absent');
    } else {
      const pyOk = (() => {
        try {
          const r = execFileSync('python3', ['-c', `import pptx; p=pptx.Presentation(r"${out}"); print(len(p.slides.__iter__.__self__._sldIdLst))`], { encoding: 'utf8' });
          return r.trim().length >= 0;
        } catch (e) { console.error('    py:', (e.stderr || e.message || '').split('\n')[0]); return false; }
      })();
      ok('python-pptx opens embedded deck', pyOk);
    }

    // LibreOffice must still rasterize it (render-path validity)
    if (!HAS_SOFFICE) {
      skip('LibreOffice renders embedded deck', 'soffice absent');
    } else {
      let loOk = false;
      try {
        const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'lo-'));
        execFileSync('soffice', ['--headless', '--norestore', '--invisible', `-env:UserInstallation=file://${prof}`, '--convert-to', 'pdf', '--outdir', TMP, out], { timeout: 120000, stdio: 'ignore' });
        loOk = fs.existsSync(path.join(TMP, 'embedded.pdf'));
      } catch (e) { /* leave false */ }
      ok('LibreOffice renders embedded deck', loOk);
    }
  }

  // ── repo woff2 → ttf (fonttools) so shipped fonts are embeddable ────────────
  console.log('\nwoff2 → ttf (fonttools) for repo fonts');
  const woff2 = path.join(ROOT, 'design-system', 'fonts', 'files', 'Pretendard-Regular.woff2');
  if (!HAS_PY) {
    skip('woff2 → ttf + embed converted ttf (2)', 'python3/fonttools absent');
  } else if (!fs.existsSync(woff2)) {
    ok('repo Pretendard woff2 present', false, 'not found');
  } else {
    let convOk = false, ttfOut = path.join(TMP, 'Pretendard-Regular.ttf');
    try {
      execFileSync('python3', ['-c', `from fontTools.ttLib import TTFont; f=TTFont(r"${woff2}"); f.flavor=None; f.save(r"${ttfOut}")`], { encoding: 'utf8' });
      convOk = fs.existsSync(ttfOut) && fs.statSync(ttfOut).size > 1000;
    } catch (e) { console.error('    conv:', (e.stderr || e.message || '').split('\n')[0]); }
    ok('Pretendard woff2 → ttf', convOk, convOk ? `${(fs.statSync(ttfOut).size / 1024 | 0)}KB` : '');
    if (convOk) {
      const out2 = path.join(TMP, 'embedded-pretendard.pptx');
      const r2 = await embedFonts(good, out2, [{ typeface: 'Pretendard', regular: ttfOut }]);
      ok('embed converted Pretendard ttf', r2.fontsEmbedded === 1);
    }
  }

  fs.rmSync(TMP, { recursive: true, force: true });
  const verdict = failed === 0 ? 'PASS' : 'FAIL';
  console.log(`\n${verdict}: ${passed} passed, ${failed} failed, ${skipped} skipped`);
  process.exit(failed === 0 ? 0 : 1);
}
main().catch(e => { console.error(e); process.exit(2); });
