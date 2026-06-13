/**
 * Rasterizers for output-layer visual regression (Layer B = PDF, Layer C = PPTX).
 *
 * Uses SYSTEM tools, never bundled, never cloud:
 *   - PDF  → PNG : poppler `pdftoppm`
 *   - PPTX → PDF : LibreOffice `soffice --headless` (then reuse PDF path)
 *
 * Both detect availability and throw a typed ENOTOOL error so the harness can
 * SKIP (not fail) when a tool is absent in a locked-down environment.
 */
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const exec = promisify(execFile);

function which(bin) {
  for (const dir of (process.env.PATH || '').split(path.delimiter)) {
    const p = path.join(dir, bin);
    try { fs.accessSync(p, fs.constants.X_OK); return p; } catch { /* next */ }
  }
  return null;
}

export function rasterizersAvailable() {
  return { pdftoppm: !!which('pdftoppm'), soffice: !!(which('soffice') || which('libreoffice')) };
}

function notool(name) {
  const e = new Error(`${name} not found on PATH — skipping this layer`);
  e.code = 'ENOTOOL';
  return e;
}

/**
 * Rasterize a PDF to one PNG per page (deterministic: fixed DPI, no AA jitter source).
 * @returns {Promise<string[]>} sorted PNG paths
 */
export async function pdfToPngs(pdfPath, outDir, { dpi = 150 } = {}) {
  if (!which('pdftoppm')) throw notool('pdftoppm');
  fs.mkdirSync(outDir, { recursive: true });
  const prefix = path.join(outDir, 'page');
  // -png deterministic raster; -r fixes DPI so page N always same pixel grid
  await exec('pdftoppm', ['-png', '-r', String(dpi), pdfPath, prefix]);
  return fs.readdirSync(outDir)
    .filter(f => /^page-?\d+\.png$/.test(f))
    .sort((a, b) => parseInt(a.match(/\d+/)[0]) - parseInt(b.match(/\d+/)[0]))
    .map(f => path.join(outDir, f));
}

/**
 * Convert a PPTX to PDF via headless LibreOffice, returning the PDF path.
 * Uses an isolated profile dir so concurrent/CI runs don't collide.
 */
export async function pptxToPdf(pptxPath, outDir) {
  const bin = which('soffice') || which('libreoffice');
  if (!bin) throw notool('soffice');
  fs.mkdirSync(outDir, { recursive: true });
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'lo-'));
  try {
    await exec(bin, [
      '--headless', '--norestore', '--invisible',
      `-env:UserInstallation=file://${profile}`,
      '--convert-to', 'pdf', '--outdir', outDir, pptxPath,
    ], { timeout: 120000 });
  } finally {
    fs.rmSync(profile, { recursive: true, force: true });
  }
  const pdf = path.join(outDir, path.basename(pptxPath).replace(/\.pptx$/i, '.pdf'));
  if (!fs.existsSync(pdf)) throw new Error(`LibreOffice did not produce ${pdf}`);
  return pdf;
}

/** PPTX → PNG[] (compose: pptx→pdf→png). */
export async function pptxToPngs(pptxPath, outDir, opts = {}) {
  const pdf = await pptxToPdf(pptxPath, outDir);
  return pdfToPngs(pdf, outDir, opts);
}
