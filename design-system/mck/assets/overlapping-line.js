/**
 * MCK Slide Design System — Overlapping Line (seasonality / YoY) chart renderer
 *
 * Seasonality comparison: a fixed X-axis of months (1–12) with one line per
 * year, all overlaid on the same axis so the eye reads the recurring shape
 * (e.g. a 11–12월 성수기 bump) and the year-over-year level shift in one pass.
 * Older year → newer year reads faint → bold so the most recent year pops.
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on compiled CSS bundle, mirrors bullet.js / combo.js).
 *
 * Usage:
 *   import { renderOverlappingLine } from '../assets/overlapping-line.js';
 *   renderOverlappingLine('#o1', {
 *     months: ["1","2","3","4","5","6","7","8","9","10","11","12"],
 *     unit: "억",
 *     series: [
 *       { year: "2023", values: [80, 75, 90, ...] },
 *       { year: "2024", values: [88, 82, 98, ...] },
 *       { year: "2025", values: [95, 90, 107, ...] },
 *     ],
 *   });
 *
 * Data contract:
 *   months    string[]  fixed X-axis labels (one per period, usually 1..12)
 *   unit      string    suffix on Y-axis ticks (optional)
 *   series[].year    string   legend label for the year line
 *   series[].values  number[] one value per month (must match months length)
 *
 * Color ramp (faint → bold, recent year emphasized): the LAST series in the
 * array always gets "primary"; the second-to-last "gray-2"; the rest "gray-3".
 * Pass an explicit series[].color to override.
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

// Default ramp by recency: last = primary (boldest), then gray-2, then gray-3.
function rampColor(idx, total) {
  if (idx === total - 1) return "primary"; // most recent — emphasized
  if (idx === total - 2) return "gray-2";
  return "gray-3"; // older years — faintest
}

export function renderOverlappingLine(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const months = data.months || [];
  const series = data.series || [];
  if (months.length < 1) {
    throw new Error("[overlapping-line] need at least 1 month");
  }
  if (series.length < 1) {
    throw new Error("[overlapping-line] need at least 1 year series");
  }
  series.forEach((s) => {
    if ((s.values || []).length !== months.length) {
      throw new Error(
        `[overlapping-line] series "${s.year}" values must match months length (${months.length})`
      );
    }
  });
  const unit = data.unit || "";

  // ── Shared Y-scale across every year (one common axis) ───────────────────
  const allVals = series.flatMap((s) => s.values);
  const yMax = niceCeil(Math.max(...allVals) * 1.05);

  // ── Viewport geometry ────────────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padL = 84, padR = 78, padT = 70, padB = 52;
  const plotW = VW - padL - padR;
  const plotH = VH - padT - padB;
  const plotBottom = padT + plotH;

  const svg = createSVG(VW, VH, "overlapping-line-chart");

  const n = months.length;
  // Lines span the full plot width, one x per month, end-to-end.
  const xFor = (i) => snap(padL + (n === 1 ? plotW / 2 : (plotW / (n - 1)) * i));
  const yFor = (v) => snap(plotBottom - (Math.max(0, v) / yMax) * plotH);

  const TICKS = 4;

  // ── 1. Gridlines + Y-axis ticks (shared scale) ───────────────────────────
  for (let t = 0; t <= TICKS; t++) {
    const v = (yMax / TICKS) * t;
    const y = yFor(v);
    svg.appendChild(el("line", {
      class: "ol-grid",
      x1: padL, y1: y, x2: padL + plotW, y2: y,
      style: `stroke:${colorVar("gray-4")};stroke-width:1;`,
    }));
    svg.appendChild(el("text", {
      class: "ol-axis-y",
      x: padL - 12, y, "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-size:15px;`,
    }, fmt(Math.round(v), { unit })));
  }

  // ── 2. Year lines (faint older → bold recent) + markers ──────────────────
  // Draw older years first so the emphasized recent line sits on top.
  series.forEach((s, si) => {
    const stroke = colorVar(s.color || rampColor(si, series.length));
    const isRecent = si === series.length - 1;
    const sw = isRecent ? 4 : 2.5;
    const points = s.values.map((v, i) => `${xFor(i)},${yFor(v)}`).join(" ");
    svg.appendChild(el("polyline", {
      class: `ol-line${isRecent ? " ol-line-recent" : ""}`,
      points,
      style: `fill:none;stroke:${stroke};stroke-width:${sw};stroke-linejoin:round;stroke-linecap:round;`,
    }));
    // markers
    const mr = isRecent ? 5.5 : 4;
    s.values.forEach((v, i) => {
      svg.appendChild(el("circle", {
        class: "ol-marker",
        cx: xFor(i), cy: yFor(v), r: mr,
        style: `fill:${stroke};stroke:${colorVar("bg")};stroke-width:1.5;`,
      }));
    });
    // end-of-line year label (right edge) — reinforces recency ramp
    const lastX = xFor(n - 1), lastY = yFor(s.values[n - 1]);
    svg.appendChild(el("text", {
      class: "ol-end-label",
      x: snap(lastX + 8), y: lastY, "dominant-baseline": "central",
      style: `fill:${stroke};font-weight:${isRecent ? 800 : 700};font-size:14px;`,
    }, s.year));
  });

  // ── 3. X-axis month labels ───────────────────────────────────────────────
  months.forEach((m, i) => {
    svg.appendChild(el("text", {
      class: "ol-axis-x",
      x: xFor(i), y: snap(plotBottom + 26),
      "text-anchor": "middle",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:16px;`,
    }, `${m}월`));
  });

  // ── 4. Legend (top) — one chip per year, faint → bold ────────────────────
  const legendY = 34;
  let lx = padL;
  series.forEach((s, si) => {
    const stroke = colorVar(s.color || rampColor(si, series.length));
    const isRecent = si === series.length - 1;
    svg.appendChild(el("line", {
      class: "ol-legend-line",
      x1: lx, y1: legendY - 5, x2: lx + 28, y2: legendY - 5,
      style: `stroke:${stroke};stroke-width:${isRecent ? 4 : 2.5};`,
    }));
    svg.appendChild(el("circle", {
      cx: lx + 14, cy: legendY - 5, r: isRecent ? 5 : 4,
      style: `fill:${stroke};stroke:${colorVar("bg")};stroke-width:1.5;`,
    }));
    const label = `${s.year}년`;
    svg.appendChild(el("text", {
      class: "ol-legend-label",
      x: lx + 36, y: legendY, "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:${isRecent ? 800 : 700};font-size:16px;`,
    }, label));
    // advance: swatch (36) + label width (≈ label.length * 15) + gap (28)
    lx += 36 + label.length * 15 + 28;
  });

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderOverlappingLineCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "ol-case";
    const h = document.createElement("h3");
    h.className = "ol-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderOverlappingLine(slot, c.data);
  });
}
