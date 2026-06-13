/**
 * MCK Slide Design System — Combo (dual-axis) chart renderer
 *
 * Combo chart: left-Y bars (absolute scale) + right-Y line with markers
 * (ratio scale). Shared X categories. The two Y axes are normalized
 * independently (each by its own max), the FP&A default for showing a
 * volume series and a margin/rate series on one slide.
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on compiled CSS bundle, mirrors bullet.js / donut.js).
 *
 * Usage:
 *   import { renderCombo } from '../assets/combo.js';
 *   renderCombo('#combo-container', {
 *     categories: ["Q1","Q2","Q3","Q4"],
 *     bars: { label: "매출",     values: [1100, 1250, 1180, 1430], unit: "억" },
 *     line: { label: "영업이익률", values: [11.2, 13.4, 9.8, 14.3],  unit: "%" }
 *   });
 *
 * Data contract:
 *   categories  string[]  shared X-axis labels (one per data point)
 *   bars.label  string    legend label for the bar series
 *   bars.values number[]  left-Y absolute values (bars)
 *   bars.unit   string    suffix on left axis ticks / bar value labels (optional)
 *   line.label  string    legend label for the line series
 *   line.values number[]  right-Y ratio values (line + markers)
 *   line.unit   string    suffix on right axis ticks / line value labels (optional)
 *
 * Left & right axes scale independently — each normalized by its own max
 * (with 5% headroom). Both axes draw their own tick labels.
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

// "Nice" axis ceiling so ticks land on round numbers.
function niceCeil(value) {
  if (!(value > 0)) return 1;
  const exp = Math.floor(Math.log10(value));
  const base = 10 ** exp;
  const frac = value / base;
  let nice;
  if (frac <= 1) nice = 1;
  else if (frac <= 2) nice = 2;
  else if (frac <= 2.5) nice = 2.5;
  else if (frac <= 5) nice = 5;
  else nice = 10;
  return nice * base;
}

export function renderCombo(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const categories = data.categories || [];
  const bars = data.bars || {};
  const line = data.line || {};
  const barVals = bars.values || [];
  const lineVals = line.values || [];
  if (categories.length < 1) {
    throw new Error("[combo] need at least 1 category");
  }
  if (barVals.length !== categories.length || lineVals.length !== categories.length) {
    throw new Error("[combo] bars.values and line.values must match categories length");
  }
  const barUnit = bars.unit || "";
  const lineUnit = line.unit || "";

  // ── Independent scales (each by its own max, 5% headroom, nice ceiling) ──
  const barMax = niceCeil(Math.max(...barVals) * 1.05);
  const lineMax = niceCeil(Math.max(...lineVals) * 1.05);

  // ── Viewport geometry ───────────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padL = 92, padR = 84, padT = 78, padB = 56;
  const plotW = VW - padL - padR;
  const plotH = VH - padT - padB;
  const plotBottom = padT + plotH;

  const svg = createSVG(VW, VH, "combo-chart");

  const yBar = (v) => snap(plotBottom - (Math.max(0, v) / barMax) * plotH);
  const yLine = (v) => snap(plotBottom - (Math.max(0, v) / lineMax) * plotH);

  const n = categories.length;
  const slot = plotW / n;
  const barW = snap(slot * 0.46);
  const xCenter = (i) => snap(padL + slot * i + slot / 2);

  const TICKS = 4;

  // ── 1. Gridlines + left axis ticks (bar scale) ──────────────────────────
  for (let t = 0; t <= TICKS; t++) {
    const v = (barMax / TICKS) * t;
    const y = yBar(v);
    svg.appendChild(el("line", {
      class: "combo-grid",
      x1: padL, y1: y, x2: padL + plotW, y2: y,
      style: `stroke:${colorVar("gray-4")};stroke-width:1;`,
    }));
    svg.appendChild(el("text", {
      class: "combo-axis-left",
      x: padL - 12, y, "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-size:15px;`,
    }, fmt(Math.round(v), { unit: barUnit })));
  }

  // ── 2. Right axis ticks (line scale) ────────────────────────────────────
  for (let t = 0; t <= TICKS; t++) {
    const v = (lineMax / TICKS) * t;
    const y = yLine(v);
    svg.appendChild(el("text", {
      class: "combo-axis-right",
      x: padL + plotW + 12, y, "text-anchor": "start", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-size:15px;`,
    }, `${snap(v, 1)}${lineUnit}`));
  }

  // ── 3. Bars (left scale) ────────────────────────────────────────────────
  // (value labels drawn last so they sit above the line/markers)
  barVals.forEach((v, i) => {
    const x = snap(xCenter(i) - barW / 2);
    const yTop = yBar(v);
    const h = Math.max(1, snap(plotBottom - yTop));
    svg.appendChild(el("rect", {
      class: "combo-bar",
      x, y: yTop, width: barW, height: h,
      style: `fill:${colorVar("primary")};`,
    }));
  });

  // ── 4. Line (right scale) — polyline + markers + value labels ───────────
  const points = lineVals.map((v, i) => `${xCenter(i)},${yLine(v)}`).join(" ");
  svg.appendChild(el("polyline", {
    class: "combo-line",
    points,
    style: `fill:none;stroke:${colorVar("accent")};stroke-width:3.5;stroke-linejoin:round;stroke-linecap:round;`,
  }));
  lineVals.forEach((v, i) => {
    const cx = xCenter(i), cy = yLine(v);
    svg.appendChild(el("circle", {
      class: "combo-marker",
      cx, cy, r: 6,
      style: `fill:${colorVar("accent")};stroke:${colorVar("gray-4")};stroke-width:2;`,
    }));
    svg.appendChild(el("text", {
      class: "combo-line-value",
      x: cx, y: snap(cy + 24),
      "text-anchor": "middle",
      style: `fill:${colorVar("accent")};font-weight:700;font-size:15px;`,
    }, `${snap(v, 1)}${lineUnit}`));
  });

  // ── 4b. Bar value labels (drawn above bars + line so nothing overlaps) ───
  barVals.forEach((v, i) => {
    const yTop = yBar(v);
    // place label above the bar top; if the line marker sits above the bar,
    // lift further so the two labels never collide.
    const markerY = yLine(lineVals[i]);
    const labelY = snap(Math.min(yTop, markerY) - 16);
    svg.appendChild(el("text", {
      class: "combo-bar-value",
      x: xCenter(i), y: labelY,
      "text-anchor": "middle",
      style: `fill:${colorVar("gray-1")};font-weight:800;font-size:16px;`,
    }, fmt(v, { unit: barUnit })));
  });

  // ── 5. X-axis category labels ───────────────────────────────────────────
  categories.forEach((c, i) => {
    svg.appendChild(el("text", {
      class: "combo-cat",
      x: xCenter(i), y: snap(plotBottom + 26),
      "text-anchor": "middle",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:18px;`,
    }, String(c)));
  });

  // ── 6. Legend (top) — bar color chip + line color chip ──────────────────
  const legendY = 34;
  let lx = padL;
  // bar swatch
  svg.appendChild(el("rect", {
    x: lx, y: legendY - 13, width: 26, height: 16,
    style: `fill:${colorVar("primary")};`,
  }));
  svg.appendChild(el("text", {
    x: lx + 34, y: legendY, "dominant-baseline": "central",
    style: `fill:${colorVar("gray-1")};font-weight:700;font-size:17px;`,
  }, `${bars.label || "막대"}${barUnit ? ` (${barUnit})` : ""}`));
  // line swatch — advance past bar label (approx width)
  const barLabelW = (String(bars.label || "막대").length) * 17 + (barUnit ? 40 : 0) + 70;
  lx += barLabelW;
  svg.appendChild(el("line", {
    x1: lx, y1: legendY - 5, x2: lx + 28, y2: legendY - 5,
    style: `stroke:${colorVar("accent")};stroke-width:3.5;`,
  }));
  svg.appendChild(el("circle", {
    cx: lx + 14, cy: legendY - 5, r: 5,
    style: `fill:${colorVar("accent")};stroke:${colorVar("gray-4")};stroke-width:2;`,
  }));
  svg.appendChild(el("text", {
    x: lx + 36, y: legendY, "dominant-baseline": "central",
    style: `fill:${colorVar("gray-1")};font-weight:700;font-size:17px;`,
  }, `${line.label || "선"}${lineUnit ? ` (${lineUnit})` : ""}`));

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderComboCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "combo-case";
    const h = document.createElement("h3");
    h.className = "combo-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderCombo(slot, c.data);
  });
}
