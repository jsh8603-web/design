/**
 * MCK Slide Design System — Generic diverging heatmap renderer
 *
 * Row × column grid; each cell = a value shaded on a *diverging* color ramp.
 * Built for variance / margin maps where sign matters: negative = red,
 * zero = white/light-gray, positive = green. center=0 anchors both flanks,
 * so a −8% and a +8% cell read symmetrically intense on opposite hues.
 * FP&A use: dept × month cost-variance maps, margin drift, YoY heatmaps.
 *
 * Generalizes cohort-heatmap.js (single-hue sequential Blues). The structural
 * pattern — cell grid, RGB-lerp fill, luminance-flipped text — is reused; the
 * key difference is the *two-sided* ramp anchored at a center value.
 *
 * ── Color exception (documented) ──────────────────────────────────────────
 * Every other chart fills via colorVar() / CSS tokens. Heatmaps are the lone
 * exception: continuous per-value shading needs interpolation, and colorVar()
 * only resolves fixed semantic tokens. So cells get hex computed by RGB-lerping
 * a diverging ramp (ColorBrewer "RdYlGn"-style). The ramp is split at center:
 * |value| drives intensity into the red (neg) or green (pos) flank, both
 * passing through a near-white pivot at center. Labels/headers still use
 * colorVar() like every other chart.
 *
 * Usage:
 *   import { renderHeatmap } from '../assets/heatmap.js';
 *   renderHeatmap('#h1', {
 *     rows: ["물류","영업","마케팅","개발","지원"],
 *     cols: ["1월","2월","3월","4월","5월","6월"],
 *     unit: "%",
 *     values: [[2.1,-3.4,5.2,...], ...],  // values[r][c]
 *     diverging: true, center: 0,
 *   });
 *
 * Data contract:
 *   rows      string[]            row labels (left, right-aligned)
 *   cols      string[]            column headers (top, centered)
 *   values    (number|null)[][]   values[r][c]; null → empty light-gray cell
 *   unit      string              suffix on cell text (e.g. "%")
 *   diverging boolean             true (default) → two-sided ramp anchored at
 *                                 center; false → sequential single-hue Blues
 *   center    number             diverging pivot value (default 0)
 *   domain    [min,max]          optional value range; default = symmetric
 *                                ±max(|v−center|) for diverging, [min,max] else
 *   negRamp   string[]           optional override, center→strong-negative
 *   posRamp   string[]           optional override, center→strong-positive
 */

import { el, createSVG, resolveTarget, clear, snap, colorVar } from "./chart-helpers.js";

// Diverging RdYlGn-style ramps, each running from a near-white pivot outward to
// the strong flank color. Authored center→extreme so intensity = |value| maps
// linearly onto the flank. 3 stops/flank keeps the lerp tight (no banding).
const NEG_RAMP = ["#FBE9E4", "#F5C9A8", "#E67E55", "#C0392B"]; // pivot → strong red
const POS_RAMP = ["#EAF4EE", "#A8D5BA", "#5FA777", "#2A8C4A"]; // pivot → strong green
// Sequential fallback (diverging:false) — single-hue Blues, light → dark.
const SEQ_RAMP = ["#EFF6FB", "#C6DCEC", "#8CB8DA", "#4A90C2", "#2A6D9C"];

// ── hex color helpers (heatmap-local, see exception note above) ──────────────
function hexToRgb(hex) {
  const h = hex.replace("#", "");
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  };
}

function rgbToHex({ r, g, b }) {
  const c = (n) => Math.round(Math.max(0, Math.min(255, n))).toString(16).padStart(2, "0");
  return `#${c(r)}${c(g)}${c(b)}`;
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

/**
 * Map t∈[0,1] onto a multi-stop hex ramp via per-channel RGB lerp.
 * t is clamped; ramp must have ≥2 stops.
 */
function rampColor(ramp, t) {
  const x = Math.max(0, Math.min(1, t));
  const segs = ramp.length - 1;
  const pos = x * segs;
  const i = Math.min(segs - 1, Math.floor(pos));
  const f = pos - i;
  const a = hexToRgb(ramp[i]);
  const b = hexToRgb(ramp[i + 1]);
  return rgbToHex({
    r: lerp(a.r, b.r, f),
    g: lerp(a.g, b.g, f),
    b: lerp(a.b, b.b, f),
  });
}

/**
 * Diverging fill: pick the negative or positive flank by sign of (v−center),
 * then map |v−center| / extent → [0,1] → that flank's ramp. center maps to the
 * near-white pivot of whichever flank (both pivots are pale → seamless join).
 */
function divergingColor(v, center, extent, negRamp, posRamp) {
  const d = v - center;
  const t = Math.min(1, Math.abs(d) / (extent || 1));
  return d < 0 ? rampColor(negRamp, t) : rampColor(posRamp, t);
}

/**
 * Relative luminance (sRGB, 0–255 in) → 0..1. Used to flip cell text to white
 * on dark fills, dark on light fills, so the value is always legible.
 */
function luminance(hex) {
  const { r, g, b } = hexToRgb(hex);
  return (0.2126 * r + 0.7152 * g + 0.1152 * b) / 255;
}

/** Format a cell value: signed for diverging maps, fixed 1 decimal + unit. */
function cellText(v, unit, signed) {
  const abs = Math.abs(v).toFixed(1);
  let sign = "";
  if (signed) sign = v > 0 ? "+" : v < 0 ? "−" : "";
  else if (v < 0) sign = "−";
  return `${sign}${abs}${unit}`;
}

export function renderHeatmap(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const rows = data.rows || [];
  const cols = data.cols || [];
  const values = data.values || [];
  if (rows.length < 1 || cols.length < 1) {
    throw new Error("[heatmap] need ≥1 row and ≥1 col");
  }
  const unit = data.unit || "";
  const diverging = data.diverging !== false; // default true
  const center = data.center ?? 0;
  const negRamp = Array.isArray(data.negRamp) && data.negRamp.length >= 2 ? data.negRamp : NEG_RAMP;
  const posRamp = Array.isArray(data.posRamp) && data.posRamp.length >= 2 ? data.posRamp : POS_RAMP;

  // Flatten present values to derive the color domain.
  const flat = values.flat().filter((v) => v != null && !Number.isNaN(v));

  // Diverging: symmetric extent = max |v − center| so both flanks scale equally
  // (a −8 and +8 cell read with matching intensity). Sequential: plain [min,max].
  let extent = 1, seqMin = 0, seqSpan = 1;
  if (diverging) {
    const dom = data.domain;
    extent = dom ? Math.max(Math.abs(dom[0] - center), Math.abs(dom[1] - center))
                 : (flat.length ? Math.max(...flat.map((v) => Math.abs(v - center))) : 1);
    extent = extent || 1;
  } else {
    const dom = data.domain || (flat.length ? [Math.min(...flat), Math.max(...flat)] : [0, 1]);
    seqMin = dom[0];
    seqSpan = (dom[1] - dom[0]) || 1;
  }

  // ── Viewport geometry ──────────────────────────────────────────────────────
  // Mirror cohort-heatmap: chart-wrap (~1126×565) → author viewBox 1000×500 so
  // the grid fills the wrap top-to-bottom. Grid consumes full padded height
  // (gridH = VH − padT − padB) → cells stretch, no dead space below.
  const VW = 1000, VH = 500;
  const padL = 120, padR = 24, padT = 52, padB = 16;
  const nCols = cols.length;
  const nRows = rows.length;
  const gridW = VW - padL - padR;
  const gridH = VH - padT - padB;
  const cellW = gridW / nCols;
  const cellH = gridH / nRows;
  const gap = 3; // hairline gutter between cells

  const svg = createSVG(VW, VH, "heatmap");

  // 1. Column headers (centered above each column)
  cols.forEach((p, c) => {
    svg.appendChild(el("text", {
      class: "heatmap-col-head",
      x: snap(padL + c * cellW + cellW / 2),
      y: snap(padT - 18),
      "text-anchor": "middle", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-weight:700;font-size:20px;`,
    }, String(p)));
  });

  // Corner label above the row-label column
  svg.appendChild(el("text", {
    class: "heatmap-corner",
    x: snap(padL - 16), y: snap(padT - 18),
    "text-anchor": "end", "dominant-baseline": "central",
    style: `fill:${colorVar("gray-3")};font-weight:700;font-size:15px;`,
  }, "부서"));

  rows.forEach((label, r) => {
    const yTop = padT + r * cellH;
    const yMid = yTop + cellH / 2;

    // 2. Row label (left, right-aligned)
    svg.appendChild(el("text", {
      class: "heatmap-row-label",
      x: snap(padL - 16), y: snap(yMid),
      "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:20px;`,
    }, String(label)));

    const rowVals = values[r] || [];
    cols.forEach((_p, c) => {
      const v = rowVals[c];
      const x = snap(padL + c * cellW + gap / 2);
      const y = snap(yTop + gap / 2);
      const w = snap(cellW - gap);
      const h = snap(cellH - gap);

      // null → empty light-gray placeholder, no text
      if (v == null || Number.isNaN(v)) {
        svg.appendChild(el("rect", {
          class: "heatmap-cell heatmap-cell-empty",
          x, y, width: w, height: h, rx: 3,
          style: `fill:${colorVar("gray-4")};`,
        }));
        return;
      }

      // 3. Continuous fill: diverging (sign→flank, |Δ|→intensity) or sequential.
      const fill = diverging
        ? divergingColor(v, center, extent, negRamp, posRamp)
        : rampColor(SEQ_RAMP, (v - seqMin) / seqSpan);
      svg.appendChild(el("rect", {
        class: "heatmap-cell",
        x, y, width: w, height: h, rx: 3,
        style: `fill:${fill};`,
      }));

      // 4. Cell value text, luminance-flipped for contrast on its own fill.
      // Threshold 0.62 mirrors cohort-heatmap: the diverging mid stops are
      // fairly light, so 0.5 would put white text on pale fills and wash out.
      const textHex = luminance(fill) < 0.62 ? "#FFFFFF" : "#1A2332";
      svg.appendChild(el("text", {
        class: "heatmap-cell-value",
        x: snap(padL + c * cellW + cellW / 2),
        y: snap(yMid),
        "text-anchor": "middle", "dominant-baseline": "central",
        style: `fill:${textHex};font-weight:700;font-size:18px;`,
      }, cellText(v, unit, diverging)));
    });
  });

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderHeatmapCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "heatmap-case";
    const h = document.createElement("h3");
    h.className = "heatmap-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderHeatmap(slot, c.data);
  });
}
