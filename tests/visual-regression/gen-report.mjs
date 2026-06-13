#!/usr/bin/env node
/**
 * gen-report.mjs — build a zero-dependency HTML gallery of visual-regression
 * heatmaps for human review (a lightweight reg-cli / BackstopJS substitute).
 *
 * Scans tests/visual-regression/diff/ for *.diff.png and writes index.html with
 * each regressed case shown large. No deps, no server — open the file or attach
 * it as the CI failure artifact.
 *
 * Run: node tests/visual-regression/gen-report.mjs [diffDir]
 * Exit: 0 always (reporting tool; the harness owns pass/fail).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const diffDir = path.resolve(process.argv[2] || path.join(__dirname, 'diff'));

export function buildReportHtml(entries, generatedAt = new Date().toISOString()) {
  const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const cards = entries.map(e => `
    <figure>
      <figcaption>${esc(e.key)}</figcaption>
      <img loading="lazy" src="${esc(e.file)}" alt="${esc(e.key)} diff">
    </figure>`).join('');
  return `<!doctype html><html lang="ko"><meta charset="utf-8">
<title>Visual Regression Report (${entries.length})</title>
<style>
  body{font:14px/1.5 system-ui,sans-serif;margin:0;background:#0f1115;color:#e7e9ee}
  header{padding:16px 24px;border-bottom:1px solid #2a2f3a;position:sticky;top:0;background:#0f1115}
  h1{font-size:16px;margin:0}
  .meta{color:#8b93a3;font-size:12px;margin-top:4px}
  .grid{display:grid;gap:24px;padding:24px}
  figure{margin:0;background:#161a22;border:1px solid #2a2f3a;border-radius:8px;overflow:hidden}
  figcaption{padding:8px 12px;font-weight:600;border-bottom:1px solid #2a2f3a;color:#ff6b6b}
  img{display:block;width:100%;height:auto;background:#fff}
  .empty{padding:48px;text-align:center;color:#5cb85c;font-size:16px}
</style>
<header><h1>Visual Regression — ${entries.length} regression(s)</h1>
<div class="meta">generated ${esc(generatedAt)} · red = changed pixels, gray = unchanged context</div></header>
${entries.length ? `<div class="grid">${cards}</div>` : `<div class="empty">✔ No regressions to report.</div>`}
</html>`;
}

export function collectEntries(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.diff.png'))
    .sort()
    .map(f => ({ key: f.replace(/\.diff\.png$/, ''), file: f })); // file relative to report location
}

function main() {
  const entries = collectEntries(diffDir);
  const html = buildReportHtml(entries);
  const out = path.join(diffDir, 'index.html');
  fs.mkdirSync(diffDir, { recursive: true });
  fs.writeFileSync(out, html);
  console.log(`report: ${entries.length} regression(s) → ${out}`);
}

// pathToFileURL handles Windows backslash paths (a bare `file://${argv[1]}` won't match).
if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
