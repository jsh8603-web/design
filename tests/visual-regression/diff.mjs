/**
 * Deterministic pixel-diff engine for visual regression.
 *
 * Zero new dependencies — uses `sharp` (already in package.json).
 * No network, no OAuth, no Vision model. Replaces the archived Gemini-Vision
 * Phase-4 rung with a fully reproducible image comparison.
 *
 * Strategy:
 *  - Normalize both images to a canonical RGB raster (default 1280x720).
 *  - Per pixel, take the max absolute per-channel delta.
 *  - A pixel "changed" if that delta exceeds `colorTolerance` (absorbs
 *    anti-aliasing / font-hinting noise that differs run-to-run).
 *  - Return changed-pixel ratio + an optional diff heatmap PNG buffer.
 */

import sharp from 'sharp';

export const DEFAULT_COMPARE_SIZE = { width: 1280, height: 720 };

/**
 * @param {string|Buffer} a              golden image (path or buffer)
 * @param {string|Buffer} b              candidate image (path or buffer)
 * @param {object} [opts]
 * @param {number} [opts.colorTolerance=24]  per-channel delta (0-255) below which a pixel is "same"
 * @param {{width:number,height:number}} [opts.size]  canonical compare size
 * @param {boolean} [opts.heatmap=true]  also produce a diff heatmap PNG buffer
 * @returns {Promise<{changedPixels:number,totalPixels:number,ratio:number,width:number,height:number,diffPng:Buffer|null}>}
 */
export async function diffImages(a, b, opts = {}) {
  const colorTolerance = opts.colorTolerance ?? 24;
  const size = opts.size ?? DEFAULT_COMPARE_SIZE;
  const wantHeatmap = opts.heatmap !== false;

  const toRaw = (src) =>
    sharp(src)
      .resize(size.width, size.height, { fit: 'fill', kernel: 'cubic' })
      .removeAlpha()
      .raw()
      .toBuffer();

  const [rawA, rawB] = await Promise.all([toRaw(a), toRaw(b)]);

  const totalPixels = size.width * size.height;
  const channels = 3;
  if (rawA.length !== rawB.length) {
    throw new Error(`raw length mismatch: ${rawA.length} vs ${rawB.length}`);
  }

  let changedPixels = 0;
  const heat = wantHeatmap ? Buffer.alloc(totalPixels * channels) : null;

  for (let p = 0; p < totalPixels; p++) {
    const i = p * channels;
    const dr = Math.abs(rawA[i] - rawB[i]);
    const dg = Math.abs(rawA[i + 1] - rawB[i + 1]);
    const db = Math.abs(rawA[i + 2] - rawB[i + 2]);
    const delta = dr > dg ? (dr > db ? dr : db) : (dg > db ? dg : db);
    const changed = delta > colorTolerance;
    if (changed) changedPixels++;
    if (heat) {
      if (changed) {
        heat[i] = 255; heat[i + 1] = 0; heat[i + 2] = 0; // mark red
      } else {
        // dimmed grayscale of golden so context is visible
        const g = (rawA[i] * 0.3 + rawA[i + 1] * 0.59 + rawA[i + 2] * 0.11) * 0.35 + 160;
        const v = g > 255 ? 255 : g | 0;
        heat[i] = v; heat[i + 1] = v; heat[i + 2] = v;
      }
    }
  }

  let diffPng = null;
  if (heat) {
    diffPng = await sharp(heat, { raw: { width: size.width, height: size.height, channels } })
      .png()
      .toBuffer();
  }

  return {
    changedPixels,
    totalPixels,
    ratio: changedPixels / totalPixels,
    width: size.width,
    height: size.height,
    diffPng,
  };
}
