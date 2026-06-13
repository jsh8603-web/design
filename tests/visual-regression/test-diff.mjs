/**
 * Self-test for diff.mjs — proves the engine is correct and deterministic
 * using the REAL golden renders in _review/ plus controlled perturbations
 * synthesized with sharp. No chromium / no network required.
 *
 * Run: node tests/visual-regression/test-diff.mjs
 * Exit 0 = all assertions pass, 1 = failure.
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { diffImages } from './diff.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..', '..');
const G = (f) => path.join(ROOT, '_review', f);

let passed = 0, failed = 0;
function assert(name, cond, detail = '') {
  if (cond) { console.log(`  ✓ ${name}${detail ? '  ' + detail : ''}`); passed++; }
  else { console.error(`  ✗ ${name}${detail ? '  ' + detail : ''}`); failed++; }
}

async function main() {
  const bullet = G('1-bullet.png');
  const pvm = G('3-pvm.png');

  // 1. Identical image → ~0 changed pixels
  {
    const r = await diffImages(bullet, bullet, { heatmap: false });
    assert('identical image → ratio == 0', r.ratio === 0, `ratio=${r.ratio}`);
  }

  // 2. Re-encoded (lossless PNG round-trip) → still 0 (deterministic)
  {
    const reenc = await sharp(bullet).png().toBuffer();
    const r = await diffImages(bullet, reenc, { heatmap: false });
    assert('lossless re-encode → ratio == 0', r.ratio === 0, `ratio=${r.ratio}`);
  }

  // 3. Sub-tolerance brightness shift (+8/255) → absorbed, stays 0
  {
    const shifted = await sharp(bullet).linear(1, 8).png().toBuffer(); // out = in*1 + 8
    const r = await diffImages(bullet, shifted, { colorTolerance: 24, heatmap: false });
    assert('+8/255 brightness (< tol 24) → ratio == 0', r.ratio === 0, `ratio=${r.ratio}`);
  }

  // 4. Above-tolerance shift on a NEUTRAL field → detected everywhere.
  //    (Mid-gray avoids the white-background clamping confound: on the real
  //     slides most pixels are already 255 and don't move under +brightness.)
  {
    const gray = await sharp({ create: { width: 1280, height: 720, channels: 3, background: { r: 128, g: 128, b: 128 } } }).png().toBuffer();
    const grayShift = await sharp({ create: { width: 1280, height: 720, channels: 3, background: { r: 188, g: 188, b: 188 } } }).png().toBuffer(); // +60
    const r = await diffImages(gray, grayShift, { colorTolerance: 24, heatmap: false });
    assert('+60 on neutral field (> tol 24) → ratio == 1.0', r.ratio === 1, `ratio=${r.ratio.toFixed(3)}`);
  }

  // 5. Localized regression: paint an opaque red box over ~1/16 of the slide.
  //    Expect changed ratio to be in a sane band around that area fraction.
  {
    const meta = await sharp(bullet).metadata();
    const bw = Math.round(meta.width / 4), bh = Math.round(meta.height / 4); // quarter x quarter = 1/16
    const box = await sharp({
      create: { width: bw, height: bh, channels: 3, background: { r: 220, g: 20, b: 20 } },
    }).png().toBuffer();
    const broken = await sharp(bullet)
      .composite([{ input: box, top: 0, left: 0 }])
      .png().toBuffer();
    const r = await diffImages(bullet, broken, { heatmap: true });
    const areaFrac = (bw * bh) / (meta.width * meta.height); // ~0.0625
    assert('localized box → detected', r.ratio > 0.02, `ratio=${r.ratio.toFixed(4)} (box area≈${areaFrac.toFixed(4)})`);
    assert('localized box → not full-frame', r.ratio < 0.20, `ratio=${r.ratio.toFixed(4)}`);
    assert('heatmap PNG produced', Buffer.isBuffer(r.diffPng) && r.diffPng.length > 0, `${r.diffPng?.length} bytes`);
    const hm = await sharp(r.diffPng).metadata();
    assert('heatmap dims == compare size', hm.width === r.width && hm.height === r.height, `${hm.width}x${hm.height}`);
    // save artifact for eyeballing
    const outDir = path.join(__dirname, '_selftest-out');
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, 'box-diff.png'), r.diffPng);
  }

  // 6. Entirely different chart → high ratio
  {
    const r = await diffImages(bullet, pvm, { heatmap: false });
    assert('different chart (bullet vs pvm) → ratio high', r.ratio > 0.10, `ratio=${r.ratio.toFixed(3)}`);
  }

  // 7. Determinism: same inputs twice → identical ratio
  {
    const r1 = await diffImages(bullet, pvm, { heatmap: false });
    const r2 = await diffImages(bullet, pvm, { heatmap: false });
    assert('deterministic across runs', r1.changedPixels === r2.changedPixels, `${r1.changedPixels}==${r2.changedPixels}`);
  }

  console.log(`\n${failed === 0 ? 'PASS' : 'FAIL'}: ${passed} passed, ${failed} failed`);
  process.exit(failed === 0 ? 0 : 1);
}

main().catch((e) => { console.error(e); process.exit(2); });
