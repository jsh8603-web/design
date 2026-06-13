/**
 * MCK Slide Design System — Scatter (correlation) chart renderer
 *
 * X–Y scatter plot for two-variable correlation (e.g. throughput × unit cost).
 * Points (circles) + optional least-squares trend line. X/Y axis lines with
 * tick marks, tick labels, and axis labels. Optional per-point labels.
 * FP&A use: cost-driver correlation, scale-economics, sensitivity scatter.
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on compiled CSS bundle, mirrors bullet.js / tornado.js).
 *
 * Usage:
 *   import { renderScatter } from '../assets/scatter.js';
 *   renderScatter('#scatter-container', {
 *     points: [
 *       { x: 120, y: 840 }, { x: 185, y: 720 }, { x: 240, y: 660 },
 *       { x: 310, y: 590 }, { x: 360, y: 560 }, { x: 420, y: 520 },
 *       { x: 480, y: 505 },
 *     ],
 *     x_label: "처리물량 (천 건)", y_label: "건당 원가 (원)", trend: true
 *   });
 *
 * Data contract:
 *   points[].x      number  x-coordinate (independent variable)
 *   points[].y      number  y-coordinate (dependent variable)
 *   points[].label  string  per-point annotation (optional)
 *   x_label         string  x-axis caption (optional)
 *   y_label         string  y-axis caption (optional)
 *   trend           bool    draw least-squares regression line (default false)
 *   x_unit          string  unit suffix on x tick labels (optional)
 *   y_unit          string  unit suffix on y tick labels (optional)
 *   ticks           number  approx. tick count per axis (default 5)
 *
 * Points render in colorVar("primary"); the trend line in colorVar("accent")
 * dashed; axes/ticks in colorVar("gray-3"). The plot domain is auto-derived
 * from the data range with a small pad so points never sit on the axis.
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

/**
 * Ordinary least-squares simple linear regression.
 * Returns { slope, intercept } for y = slope·x + intercept.
 * Degenerate input (n < 2 or zero x-variance) → slope 0 through the mean.
 */
export function linearRegression(points) {
  const n = points.length;
  if (n < 2) return { slope: 0, intercept: n === 1 ? points[0].y : 0 };
  let sx = 0, sy = 0, sxx = 0, sxy = 0;
  for (const p of points) {
    sx += p.x; sy += p.y; sxx += p.x * p.x; sxy += p.x * p.y;
  }
  const denom = n * sxx - sx * sx;
  if (denom === 0) return { slope: 0, intercept: sy / n };
  const slope = (n * sxy - sx * sy) / denom;
  const intercept = (sy - slope * sx) / n;
  return { slope, intercept };
}

/** "Nice" axis bounds + step for a [min,max] range targeting ~count ticks. */
function niceScale(min, max, count) {
  const span = (max - min) || 1;
  const rawStep = span / Math.max(1, count);
  const mag = 10 ** Math.floor(Math.log10(rawStep));
  const norm = rawStep / mag;
  let step;
  if (norm < 1.5) step = 1;
  else if (norm < 3) step = 2;
  else if (norm < 7) step = 5;
  else step = 10;
  step *= mag;
  const niceMin = Math.floor(min / step) * step;
  const niceMax = Math.ceil(max / step) * step;
  const ticks = [];
  for (let v = niceMin; v <= niceMax + step * 1e-6; v += step) {
    ticks.push(snap(v, 6));
  }
  return { min: niceMin, max: niceMax, ticks };
}

export function renderScatter(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const points = (data.points || []).filter((p) => p && p.x != null && p.y != null);
  if (points.length < 1) {
    throw new Error("[scatter] need at least 1 point");
  }
  const xLabel = data.x_label || "";
  const yLabel = data.y_label || "";
  const xUnit = data.x_unit || "";
  const yUnit = data.y_unit || "";
  const tickCount = data.ticks || 5;
  const showTrend = data.trend === true;

  // ── Data range → nice axis domains (small pad so points clear the axes) ────
  const xs = points.map((p) => Number(p.x));
  const ys = points.map((p) => Number(p.y));
  const xLo = Math.min(...xs), xHi = Math.max(...xs);
  const yLo = Math.min(...ys), yHi = Math.max(...ys);
  const xPad = ((xHi - xLo) || 1) * 0.08;
  const yPad = ((yHi - yLo) || 1) * 0.08;
  const xScale = niceScale(xLo - xPad, xHi + xPad, tickCount);
  const yScale = niceScale(yLo - yPad, yHi + yPad, tickCount);

  // ── Viewport geometry ──────────────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padL = 110, padR = 48, padT = 30, padB = 78;
  const plotW = VW - padL - padR;
  const plotH = VH - padT - padB;

  const xFor = (v) =>
    snap(padL + ((v - xScale.min) / (xScale.max - xScale.min)) * plotW);
  const yFor = (v) =>
    snap(padT + plotH - ((v - yScale.min) / (yScale.max - yScale.min)) * plotH);

  const svg = createSVG(VW, VH, "scatter-chart");

  const axisColor = colorVar("gray-3");
  const x0 = padL;
  const y0 = padT + plotH; // baseline (x-axis) y

  // ── Y-axis ticks + gridlines + labels ──────────────────────────────────────
  yScale.ticks.forEach((t) => {
    const ty = yFor(t);
    // faint gridline across the plot
    svg.appendChild(el("line", {
      class: "scatter-grid",
      x1: x0, y1: ty, x2: snap(padL + plotW), y2: ty,
      style: `stroke:${colorVar("gray-4")};stroke-width:1;`,
    }));
    // tick mark
    svg.appendChild(el("line", {
      class: "scatter-tick",
      x1: snap(x0 - 6), y1: ty, x2: x0, y2: ty,
      style: `stroke:${axisColor};stroke-width:1.5;`,
    }));
    // tick label
    svg.appendChild(el("text", {
      class: "scatter-tick-label",
      x: snap(x0 - 12), y: ty,
      "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-size:15px;`,
    }, fmt(t, { unit: yUnit })));
  });

  // ── X-axis ticks + labels ───────────────────────────────────────────────────
  xScale.ticks.forEach((t) => {
    const tx = xFor(t);
    svg.appendChild(el("line", {
      class: "scatter-tick",
      x1: tx, y1: y0, x2: tx, y2: snap(y0 + 6),
      style: `stroke:${axisColor};stroke-width:1.5;`,
    }));
    svg.appendChild(el("text", {
      class: "scatter-tick-label",
      x: tx, y: snap(y0 + 24),
      "text-anchor": "middle", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-size:15px;`,
    }, fmt(t, { unit: xUnit })));
  });

  // ── Axis lines ──────────────────────────────────────────────────────────────
  svg.appendChild(el("line", {
    class: "scatter-axis-y",
    x1: x0, y1: padT, x2: x0, y2: y0,
    style: `stroke:${axisColor};stroke-width:2;`,
  }));
  svg.appendChild(el("line", {
    class: "scatter-axis-x",
    x1: x0, y1: y0, x2: snap(padL + plotW), y2: y0,
    style: `stroke:${axisColor};stroke-width:2;`,
  }));

  // ── Trend line (least-squares regression), clipped to plot domain ──────────
  if (showTrend && points.length >= 2) {
    const { slope, intercept } = linearRegression(
      points.map((p) => ({ x: Number(p.x), y: Number(p.y) }))
    );
    const yAt = (x) => slope * x + intercept;
    // Clip the fitted line to the visible y-domain so it never escapes the plot.
    let ax = xScale.min, ay = yAt(xScale.min);
    let bx = xScale.max, by = yAt(xScale.max);
    const clipEnd = (px, py, qx, qy) => {
      // clip segment endpoint (px,py) toward (qx,qy) into [yScale.min, yScale.max]
      let x = px, y = py;
      if (y < yScale.min || y > yScale.max) {
        const target = y < yScale.min ? yScale.min : yScale.max;
        const t = (target - py) / (qy - py);
        x = px + t * (qx - px);
        y = target;
      }
      return { x, y };
    };
    if (slope !== 0) {
      const A = clipEnd(ax, ay, bx, by);
      const B = clipEnd(bx, by, ax, ay);
      ax = A.x; ay = A.y; bx = B.x; by = B.y;
    }
    svg.appendChild(el("line", {
      class: "scatter-trend",
      x1: xFor(ax), y1: yFor(ay), x2: xFor(bx), y2: yFor(by),
      style: `stroke:${colorVar("accent")};stroke-width:3;stroke-dasharray:9 6;stroke-linecap:round;`,
    }));
  }

  // ── Data points (drawn last so they sit above grid + trend) ────────────────
  points.forEach((p) => {
    const cx = xFor(Number(p.x));
    const cy = yFor(Number(p.y));
    svg.appendChild(el("circle", {
      class: "scatter-point",
      cx, cy, r: 9,
      style: `fill:${colorVar("primary")};`,
    }));
    if (p.label != null && p.label !== "") {
      svg.appendChild(el("text", {
        class: "scatter-point-label",
        x: cx, y: snap(cy - 16),
        "text-anchor": "middle",
        style: `fill:${colorVar("gray-1")};font-weight:700;font-size:14px;`,
      }, String(p.label)));
    }
  });

  // ── Axis captions ───────────────────────────────────────────────────────────
  if (xLabel) {
    svg.appendChild(el("text", {
      class: "scatter-x-label",
      x: snap(padL + plotW / 2), y: snap(VH - 14),
      "text-anchor": "middle",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:18px;`,
    }, xLabel));
  }
  if (yLabel) {
    const yMid = snap(padT + plotH / 2);
    svg.appendChild(el("text", {
      class: "scatter-y-label",
      x: 28, y: yMid,
      "text-anchor": "middle",
      transform: `rotate(-90 28 ${yMid})`,
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:18px;`,
    }, yLabel));
  }

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderScatterCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "scatter-case";
    const h = document.createElement("h3");
    h.className = "scatter-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderScatter(slot, c.data);
  });
}
