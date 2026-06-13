/**
 * MCK Slide Design System — Tornado (sensitivity) chart renderer
 *
 * Horizontal diverging bars for sensitivity analysis. Each driver variable
 * swings the result metric (e.g. operating income) as it moves ±. One row per
 * driver, sorted by swing magnitude (largest at top) → the funnel/"tornado".
 * FP&A use: scenario decks, valuation sensitivity, risk drivers.
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on compiled CSS bundle, mirrors bullet.js / donut.js).
 *
 * Usage:
 *   import { renderTornado } from '../assets/tornado.js';
 *   renderTornado('#tornado-container', {
 *     base: 200, unit: "억",
 *     items: [
 *       { label: "물동량 ±10%",   low: 158, high: 246 },
 *       { label: "인건비 단가 ±8%", low: 176, high: 224 },
 *       { label: "연료비 ±15%",     low: 184, high: 216 },
 *       { label: "환율 ±5%",        low: 190, high: 210 },
 *     ]
 *   });
 *
 * Data contract:
 *   base            number  base-case result value → vertical dashed reference
 *   unit            string  value suffix shown on base callout + end labels (optional)
 *   items[].label   string  driver variable name (left, right-aligned)
 *   items[].low     number  result when this driver moves to its downside
 *   items[].high    number  result when this driver moves to its upside
 *
 * Each bar spans [min(low,high) … max(low,high)] across the base line. The
 * portion below base renders in colorVar("negative"), above base in
 * colorVar("positive"); a bar straddling base splits into two rects. Rows are
 * sorted by swing = |high − low| descending.
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

export function renderTornado(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const base = Number(data.base ?? 0);
  const unit = data.unit || "";
  const items = (data.items || []).slice();
  if (items.length < 1) {
    throw new Error("[tornado] need at least 1 item");
  }

  // ── Sort by swing magnitude (largest at top) → funnel shape ───────────────
  const swing = (it) => Math.abs(Number(it.high) - Number(it.low));
  items.sort((a, b) => swing(b) - swing(a));

  // ── Shared x-scale: span every endpoint + base, padded ───────────────────
  let lo = base, hi = base;
  items.forEach((it) => {
    lo = Math.min(lo, Number(it.low), Number(it.high));
    hi = Math.max(hi, Number(it.low), Number(it.high));
  });
  const span = (hi - lo) || 1;
  const pad = span * 0.08;
  const xMin = lo - pad;
  const xMax = hi + pad;

  // ── Viewport geometry ────────────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padL = 220, padR = 70, padT = 60, padB = 30;
  const plotW = VW - padL - padR;
  const plotH = VH - padT - padB;
  const rows = items.length;
  const rowH = plotH / rows;

  const xFor = (v) => snap(padL + ((v - xMin) / (xMax - xMin)) * plotW);

  const svg = createSVG(VW, VH, "tornado-chart");

  const baseX = xFor(base);

  // ── Base-case vertical dashed reference line ──────────────────────────────
  svg.appendChild(el("line", {
    class: "tornado-base",
    x1: baseX, y1: snap(padT - 8), x2: baseX, y2: snap(padT + plotH + 4),
    style: `stroke:${colorVar("gray-2")};stroke-width:2;stroke-dasharray:6 5;`,
  }));

  // ── Base callout (top, anchored at the base line) ─────────────────────────
  svg.appendChild(el("text", {
    class: "tornado-base-label",
    x: baseX, y: snap(padT - 18),
    "text-anchor": "middle",
    style: `fill:${colorVar("gray-1")};font-weight:800;font-size:18px;`,
  }, `Base ${fmt(base, { unit })}`));

  items.forEach((it, i) => {
    const low = Number(it.low);
    const high = Number(it.high);
    const yMid = padT + i * rowH + rowH / 2;
    const barH = Math.min(46, rowH * 0.6);
    const barY = snap(yMid - barH / 2);

    const lEnd = Math.min(low, high);  // left endpoint (value-min)
    const rEnd = Math.max(low, high);  // right endpoint (value-max)
    const xL = xFor(lEnd);
    const xR = xFor(rEnd);

    // 1. Diverging bar — split at base into negative (below) / positive (above)
    if (lEnd < base) {
      const x0 = xL;
      const x1 = Math.min(baseX, xR);
      const w = Math.max(0, snap(x1 - x0));
      if (w > 0) {
        svg.appendChild(el("rect", {
          class: "tornado-bar-neg",
          x: x0, y: barY, width: w, height: snap(barH),
          style: `fill:${colorVar("negative")};`,
        }));
      }
    }
    if (rEnd > base) {
      const x0 = Math.max(baseX, xL);
      const x1 = xR;
      const w = Math.max(0, snap(x1 - x0));
      if (w > 0) {
        svg.appendChild(el("rect", {
          class: "tornado-bar-pos",
          x: x0, y: barY, width: w, height: snap(barH),
          style: `fill:${colorVar("positive")};`,
        }));
      }
    }

    // 2. Driver label (left, right-aligned)
    svg.appendChild(el("text", {
      class: "tornado-label",
      x: padL - 16, y: snap(yMid),
      "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:21px;`,
    }, String(it.label)));

    // 3. Endpoint value labels — low at its end, high at its end
    //    Place each just outside its bar end (low on the lower side).
    const loIsLeft = low <= high;
    const lowX = loIsLeft ? xL : xR;
    const highX = loIsLeft ? xR : xL;

    svg.appendChild(el("text", {
      class: "tornado-val-low",
      x: snap(lowX - 10), y: snap(yMid),
      "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:15px;`,
    }, fmt(low, { unit })));

    svg.appendChild(el("text", {
      class: "tornado-val-high",
      x: snap(highX + 10), y: snap(yMid),
      "text-anchor": "start", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:15px;`,
    }, fmt(high, { unit })));
  });

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderTornadoCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "tornado-case";
    const h = document.createElement("h3");
    h.className = "tornado-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderTornado(slot, c.data);
  });
}
