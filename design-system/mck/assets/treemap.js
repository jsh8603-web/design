/**
 * MCK Slide Design System — Treemap renderer (1-level, squarified)
 *
 * Area-proportional rectangle packing: each item's cell area ∝ its value, so
 * a single glance reads composition / share-of-total. FP&A use: cost structure
 * (영업비용 구성), revenue mix, segment contribution, headcount allocation.
 *
 * Layout = squarified treemap (Bruls/Huizing/van Wijk). Greedy row-packing that
 * keeps each cell's aspect ratio as close to 1 as possible — squarish cells read
 * far better than the thin slivers a naive slice-and-dice produces.
 *
 * Theme-aware: cell fills via colorVar() palette cycling (inline fill — self-
 * contained, mirrors bullet.js / donut.js). Cell text auto-switches white/dark
 * by the resolved fill's luminance (getComputedStyle on a probe), so labels stay
 * legible on every theme.
 *
 * Usage:
 *   import { renderTreemap } from '../assets/treemap.js';
 *   renderTreemap('#t1', {
 *     unit: "억",
 *     items: [
 *       { label: "인건비",   value: 420 },
 *       { label: "물류비",   value: 310 },
 *       { label: "마케팅비", value: 180 },
 *     ],
 *   });
 *
 * Data contract:
 *   items[].label  string  cell label
 *   items[].value  number  positive magnitude → cell area (non-positive dropped)
 *   items[].color  string  optional explicit color token / hex (overrides cycle)
 *   unit           string  value suffix on each cell (optional)
 *   show_pct       bool    show share-of-total % under value (default true)
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

// Palette ring per spec — adjacent cells visibly differ.
const TREEMAP_PALETTE = ["primary", "accent", "gray-2", "positive", "gray-3", "negative"];

/**
 * Squarified treemap layout.
 * @param {number[]} values   item values (same order as items), all > 0
 * @param {object}   rect     { x, y, w, h } available area
 * @returns {{x,y,w,h}[]}     one rect per value, same order
 */
function squarify(values, rect) {
  const total = values.reduce((a, b) => a + b, 0);
  const area = rect.w * rect.h;
  // Scale values → area units so packed rects tile `rect` exactly.
  const scaled = values.map((v) => (v / total) * area);
  const out = new Array(values.length);
  const free = { ...rect };
  let i = 0;

  const worst = (row, side, sumRow) => {
    // Aspect-ratio cost of laying `row` along a strip of length `side`.
    const s2 = sumRow * sumRow;
    const side2 = side * side;
    let rmax = -Infinity, rmin = Infinity;
    for (const a of row) {
      if (a > rmax) rmax = a;
      if (a < rmin) rmin = a;
    }
    return Math.max((side2 * rmax) / s2, s2 / (side2 * rmin));
  };

  while (i < scaled.length) {
    const shorter = Math.min(free.w, free.h);
    const row = [scaled[i]];
    let sumRow = scaled[i];
    let j = i + 1;
    // Grow the row while aspect ratios keep improving.
    while (j < scaled.length) {
      const next = sumRow + scaled[j];
      if (worst(row, shorter, sumRow) <= worst([...row, scaled[j]], shorter, next)) break;
      row.push(scaled[j]);
      sumRow = next;
      j++;
    }
    // Lay the finalized row across the shorter side of the free rect.
    const rowThick = sumRow / shorter; // depth of the strip
    let pos = 0;
    const horizontal = free.w >= free.h; // strip runs along the shorter side
    for (let k = i; k < j; k++) {
      const cellLen = (scaled[k] / sumRow) * shorter;
      if (horizontal) {
        out[k] = { x: free.x, y: free.y + pos, w: rowThick, h: cellLen };
      } else {
        out[k] = { x: free.x + pos, y: free.y, w: cellLen, h: rowThick };
      }
      pos += cellLen;
    }
    // Shrink the free rect by the consumed strip.
    if (horizontal) {
      free.x += rowThick;
      free.w -= rowThick;
    } else {
      free.y += rowThick;
      free.h -= rowThick;
    }
    i = j;
  }
  return out;
}

// Resolve a colorVar() reference (var(--x) or hex) to a concrete hex via a
// detached probe, so we can pick legible white/dark text per cell.
function resolveHex(colorRef) {
  const probe = document.createElement("span");
  probe.style.color = colorRef;
  probe.style.display = "none";
  document.body.appendChild(probe);
  const rgb = getComputedStyle(probe).color; // "rgb(r, g, b)"
  document.body.removeChild(probe);
  const m = rgb.match(/(\d+(?:\.\d+)?)/g);
  if (!m) return { r: 0, g: 0, b: 0 };
  return { r: +m[0], g: +m[1], b: +m[2] };
}

// Relative luminance (WCAG) → decide white vs dark ink on the fill.
function textOnFill(colorRef) {
  const { r, g, b } = resolveHex(colorRef);
  const lin = (c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  const L = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  return L > 0.45 ? "#1A1A1A" : "#FFFFFF";
}

export function renderTreemap(target, data) {
  const container = resolveTarget(target);
  clear(container);

  // Normalize: positive values only, preserve declared order (no sort — keeps
  // the caller's narrative order; squarify handles aspect regardless of order).
  const items = (data.items || []).filter((it) => Number(it.value) > 0);
  if (items.length < 1) throw new Error("[treemap] need at least 1 item with value > 0");

  const unit = data.unit || "";
  const showPct = data.show_pct !== false;
  const total = items.reduce((a, it) => a + Number(it.value), 0);

  // ── Viewport geometry (matches bullet.js authoring units) ──────────────────
  const VW = 1000, VH = 500;
  const pad = 4; // inner padding so the white 2px borders read at the edges too
  const rect = { x: pad, y: pad, w: VW - pad * 2, h: VH - pad * 2 };

  const svg = createSVG(VW, VH, "treemap-chart");

  const cells = squarify(items.map((it) => Number(it.value)), rect);
  const GAP = 2; // half of the 2px white seam (each cell insets by GAP)

  items.forEach((it, i) => {
    const c = cells[i];
    // Inset each cell so adjacent fills leave a 2*GAP white seam between them.
    const x = snap(c.x + GAP), y = snap(c.y + GAP);
    const w = snap(Math.max(0, c.w - GAP * 2)), h = snap(Math.max(0, c.h - GAP * 2));
    const fill = colorVar(it.color || TREEMAP_PALETTE[i % TREEMAP_PALETTE.length], i);
    const ink = textOnFill(fill);
    const pct = total > 0 ? (Number(it.value) / total) * 100 : 0;

    const g = el("g", { class: "treemap-cell" });
    g.appendChild(el("rect", {
      x, y, width: w, height: h,
      rx: 2, ry: 2,
      style: `fill:${fill};stroke:#FFFFFF;stroke-width:2;`,
    }));

    // ── Text fitting: only draw what the cell can hold without overflow ───────
    const cx = snap(x + w / 2);
    const cy = snap(y + h / 2);
    const labelSize = Math.min(26, Math.max(13, Math.round(Math.min(w, h) * 0.18)));
    const valueSize = Math.round(labelSize * 0.82);

    // Approx CJK glyph width ≈ 1.0em; Latin/number ≈ 0.6em. Estimate the widest
    // line and require it (plus a margin) to fit inside the cell before drawing.
    const labelText = String(it.label);
    const valueText = fmt(Number(it.value), { unit }) + (showPct ? `  ${pct.toFixed(0)}%` : "");
    const estW = (s, size) => {
      let units = 0;
      for (const ch of s) units += /[\x00-\x7F]/.test(ch) ? 0.58 : 1.02;
      return units * size;
    };

    const fitsLabel = estW(labelText, labelSize) <= w - 10 && labelSize + 6 <= h;
    const showValue =
      estW(valueText, valueSize) <= w - 10 &&
      labelSize + valueSize + 14 <= h; // need room for both lines

    if (fitsLabel && showValue) {
      g.appendChild(el("text", {
        class: "treemap-label",
        x: cx, y: snap(cy - valueSize * 0.55),
        "text-anchor": "middle", "dominant-baseline": "central",
        style: `fill:${ink};font-weight:700;font-size:${labelSize}px;`,
      }, labelText));
      g.appendChild(el("text", {
        class: "treemap-value",
        x: cx, y: snap(cy + labelSize * 0.6),
        "text-anchor": "middle", "dominant-baseline": "central",
        style: `fill:${ink};font-weight:800;font-size:${valueSize}px;opacity:0.92;`,
      }, valueText));
    } else if (fitsLabel) {
      // Tight cell → label only, vertically centered.
      g.appendChild(el("text", {
        class: "treemap-label",
        x: cx, y: cy,
        "text-anchor": "middle", "dominant-baseline": "central",
        style: `fill:${ink};font-weight:700;font-size:${labelSize}px;`,
      }, labelText));
    }
    // else: cell too small for even the label → leave it as a colored tile.

    svg.appendChild(g);
  });

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderTreemapCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "treemap-case";
    const h = document.createElement("h3");
    h.className = "treemap-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderTreemap(slot, c.data);
  });
}
