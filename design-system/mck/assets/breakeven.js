/**
 * MCK Slide Design System — Breakeven / CVP (cost-volume-profit) chart renderer
 *
 * Classic break-even chart. X-axis = volume (0 → max). Three lines:
 *   1. Revenue line   = unit_price × Q          (from origin, slopes up)
 *   2. Total-cost line = fixed_cost + unit_var_cost × Q (intercept = fixed cost)
 *   3. Fixed-cost line (optional) = fixed_cost  (horizontal, dashed)
 * Their intersection is the break-even point (BEP): Q* = fixed_cost / (unit_price − unit_var_cost).
 * A marker + "BEP Q*=…" label sit at the crossing. Optional light shading for
 * the loss region (left of BEP) and profit region (right of BEP).
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on compiled CSS bundle, mirrors scatter.js / combo.js).
 *
 * Usage:
 *   import { renderBreakeven } from '../assets/breakeven.js';
 *   renderBreakeven('#be-container', {
 *     fixed_cost: 4000,     // 만원
 *     unit_price: 50,       // 개당 만원
 *     unit_var_cost: 30,    // 개당 만원
 *     max_volume: 400,      // 개
 *     unit: "만원", vol_unit: "개"
 *   });
 *
 * Data contract:
 *   fixed_cost     number  fixed cost (Y-intercept of the total-cost line)
 *   unit_price     number  selling price per unit (slope of the revenue line)
 *   unit_var_cost  number  variable cost per unit (slope component of total cost)
 *   max_volume     number  right edge of the X domain (volume)
 *   unit           string  money-axis unit suffix (Y ticks, optional)
 *   vol_unit       string  volume-axis unit suffix (X ticks, optional)
 *   show_fixed     bool    draw the dashed fixed-cost horizontal (default true)
 *   show_regions   bool    shade loss/profit regions (default true)
 *   ticks          number  approx. tick count per axis (default 5)
 *
 * Revenue = colorVar("positive"), total cost = colorVar("negative"),
 * fixed-cost line = colorVar("gray-3") dashed, BEP marker = colorVar("primary").
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

/**
 * Break-even point in volume + the revenue/cost level at that point.
 * Q* = fixed_cost / (unit_price − unit_var_cost).
 * Returns { q, value, feasible }. Infeasible (margin ≤ 0) → feasible:false.
 */
export function breakevenPoint(fixed_cost, unit_price, unit_var_cost) {
  const margin = unit_price - unit_var_cost; // contribution margin per unit
  if (!(margin > 0)) return { q: Infinity, value: Infinity, feasible: false };
  const q = fixed_cost / margin;
  const value = unit_price * q; // revenue (== total cost) at break-even
  return { q, value, feasible: true };
}

/** "Nice" axis bounds + step for a [0,max] range targeting ~count ticks. */
function niceScale(max, count) {
  const span = max || 1;
  const rawStep = span / Math.max(1, count);
  const mag = 10 ** Math.floor(Math.log10(rawStep));
  const norm = rawStep / mag;
  let step;
  if (norm < 1.5) step = 1;
  else if (norm < 3) step = 2;
  else if (norm < 7) step = 5;
  else step = 10;
  step *= mag;
  const niceMax = Math.ceil(max / step) * step;
  const ticks = [];
  for (let v = 0; v <= niceMax + step * 1e-6; v += step) {
    ticks.push(snap(v, 6));
  }
  return { min: 0, max: niceMax, ticks };
}

export function renderBreakeven(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const fixedCost = Number(data.fixed_cost) || 0;
  const unitPrice = Number(data.unit_price) || 0;
  const unitVarCost = Number(data.unit_var_cost) || 0;
  const maxVolume = Number(data.max_volume) || 0;
  if (!(maxVolume > 0)) throw new Error("[breakeven] max_volume must be > 0");
  const unit = data.unit || "";
  const volUnit = data.vol_unit || "";
  const tickCount = data.ticks || 5;
  const showFixed = data.show_fixed !== false;
  const showRegions = data.show_regions !== false;

  const bep = breakevenPoint(fixedCost, unitPrice, unitVarCost);

  // ── Domains. X = [0, max_volume]. Y = [0, max revenue or total cost at max] ──
  const revAtMax = unitPrice * maxVolume;
  const costAtMax = fixedCost + unitVarCost * maxVolume;
  const yTop = Math.max(revAtMax, costAtMax, fixedCost);
  const xScale = niceScale(maxVolume, tickCount);
  const yScale = niceScale(yTop, tickCount);

  // ── Viewport geometry ──────────────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padL = 120, padR = 60, padT = 56, padB = 78;
  const plotW = VW - padL - padR;
  const plotH = VH - padT - padB;

  const xFor = (v) => snap(padL + (v / xScale.max) * plotW);
  const yFor = (v) => snap(padT + plotH - (v / yScale.max) * plotH);

  const svg = createSVG(VW, VH, "breakeven-chart");

  const axisColor = colorVar("gray-3");
  const x0 = padL;
  const y0 = padT + plotH; // baseline (x-axis) y

  // ── Region shading (loss left of BEP, profit right of BEP) ──────────────────
  // Drawn first so everything else sits on top. Only when BEP falls in-domain.
  if (showRegions && bep.feasible && bep.q < xScale.max) {
    const xBep = xFor(bep.q);
    // Loss region: between cost line and revenue line, left of BEP (cost > rev).
    // Polygon: origin(rev) → BEP → fixed-cost intercept.
    svg.appendChild(el("polygon", {
      class: "breakeven-loss",
      points: [
        `${xFor(0)},${yFor(0)}`,
        `${xBep},${yFor(bep.value)}`,
        `${xFor(0)},${yFor(fixedCost)}`,
      ].join(" "),
      style: `fill:${colorVar("negative")};opacity:0.10;`,
    }));
    // Profit region: between revenue and cost line, right of BEP (rev > cost).
    svg.appendChild(el("polygon", {
      class: "breakeven-profit",
      points: [
        `${xBep},${yFor(bep.value)}`,
        `${xFor(xScale.max)},${yFor(unitPrice * xScale.max)}`,
        `${xFor(xScale.max)},${yFor(fixedCost + unitVarCost * xScale.max)}`,
      ].join(" "),
      style: `fill:${colorVar("positive")};opacity:0.12;`,
    }));
  }

  // ── Y-axis ticks + gridlines + labels ──────────────────────────────────────
  yScale.ticks.forEach((t) => {
    const ty = yFor(t);
    svg.appendChild(el("line", {
      class: "breakeven-grid",
      x1: x0, y1: ty, x2: snap(padL + plotW), y2: ty,
      style: `stroke:${colorVar("gray-4")};stroke-width:1;`,
    }));
    svg.appendChild(el("line", {
      class: "breakeven-tick",
      x1: snap(x0 - 6), y1: ty, x2: x0, y2: ty,
      style: `stroke:${axisColor};stroke-width:1.5;`,
    }));
    svg.appendChild(el("text", {
      class: "breakeven-tick-label",
      x: snap(x0 - 12), y: ty,
      "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-size:15px;`,
    }, fmt(Math.round(t), { unit })));
  });

  // ── X-axis ticks + labels ───────────────────────────────────────────────────
  xScale.ticks.forEach((t) => {
    const tx = xFor(t);
    svg.appendChild(el("line", {
      class: "breakeven-tick",
      x1: tx, y1: y0, x2: tx, y2: snap(y0 + 6),
      style: `stroke:${axisColor};stroke-width:1.5;`,
    }));
    svg.appendChild(el("text", {
      class: "breakeven-tick-label",
      x: tx, y: snap(y0 + 24),
      "text-anchor": "middle", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-size:15px;`,
    }, fmt(Math.round(t), { unit: volUnit })));
  });

  // ── Axis lines ──────────────────────────────────────────────────────────────
  svg.appendChild(el("line", {
    class: "breakeven-axis-y",
    x1: x0, y1: padT, x2: x0, y2: y0,
    style: `stroke:${axisColor};stroke-width:2;`,
  }));
  svg.appendChild(el("line", {
    class: "breakeven-axis-x",
    x1: x0, y1: y0, x2: snap(padL + plotW), y2: y0,
    style: `stroke:${axisColor};stroke-width:2;`,
  }));

  // ── Fixed-cost horizontal (optional, dashed) ────────────────────────────────
  if (showFixed) {
    const fy = yFor(fixedCost);
    svg.appendChild(el("line", {
      class: "breakeven-fixed",
      x1: x0, y1: fy, x2: snap(padL + plotW), y2: fy,
      style: `stroke:${colorVar("gray-3")};stroke-width:2;stroke-dasharray:7 6;`,
    }));
  }

  // ── Total-cost line: fixed_cost → fixed_cost + unit_var_cost·max ────────────
  svg.appendChild(el("line", {
    class: "breakeven-cost",
    x1: xFor(0), y1: yFor(fixedCost),
    x2: xFor(xScale.max), y2: yFor(fixedCost + unitVarCost * xScale.max),
    style: `stroke:${colorVar("negative")};stroke-width:3.5;stroke-linecap:round;`,
  }));

  // ── Revenue line: 0 → unit_price·max (from origin) ──────────────────────────
  svg.appendChild(el("line", {
    class: "breakeven-revenue",
    x1: xFor(0), y1: yFor(0),
    x2: xFor(xScale.max), y2: yFor(unitPrice * xScale.max),
    style: `stroke:${colorVar("positive")};stroke-width:3.5;stroke-linecap:round;`,
  }));

  // ── BEP marker + label ──────────────────────────────────────────────────────
  if (bep.feasible && bep.q <= xScale.max) {
    const bx = xFor(bep.q);
    const by = yFor(bep.value);
    // drop-line down to the X axis so the volume reads off the axis
    svg.appendChild(el("line", {
      class: "breakeven-bep-drop",
      x1: bx, y1: by, x2: bx, y2: y0,
      style: `stroke:${colorVar("primary")};stroke-width:1.5;stroke-dasharray:4 5;opacity:0.7;`,
    }));
    svg.appendChild(el("circle", {
      class: "breakeven-bep",
      cx: bx, cy: by, r: 9,
      style: `fill:${colorVar("primary")};stroke:${colorVar("gray-4")};stroke-width:2.5;`,
    }));
    // "BEP Q*=…" label, lifted above-left of the marker so it clears the lines
    svg.appendChild(el("text", {
      class: "breakeven-bep-label",
      x: snap(bx + 14), y: snap(by - 18),
      "text-anchor": "start",
      style: `fill:${colorVar("primary")};font-weight:800;font-size:17px;`,
    }, `BEP Q*=${fmt(Math.round(bep.q), { unit: volUnit })}`));
  }

  // ── Axis captions ───────────────────────────────────────────────────────────
  svg.appendChild(el("text", {
    class: "breakeven-x-label",
    x: snap(padL + plotW / 2), y: snap(VH - 14),
    "text-anchor": "middle",
    style: `fill:${colorVar("gray-1")};font-weight:700;font-size:18px;`,
  }, `물량 (${volUnit || "수량"})`));
  const yMid = snap(padT + plotH / 2);
  svg.appendChild(el("text", {
    class: "breakeven-y-label",
    x: 30, y: yMid,
    "text-anchor": "middle",
    transform: `rotate(-90 30 ${yMid})`,
    style: `fill:${colorVar("gray-1")};font-weight:700;font-size:18px;`,
  }, `금액 (${unit || ""})`));

  // ── Legend (top) — revenue / total cost / fixed cost swatches ───────────────
  const legendY = 30;
  let lx = padL;
  const chip = (color, label, dashed) => {
    if (dashed) {
      svg.appendChild(el("line", {
        x1: lx, y1: legendY - 5, x2: lx + 26, y2: legendY - 5,
        style: `stroke:${color};stroke-width:3;stroke-dasharray:6 5;`,
      }));
    } else {
      svg.appendChild(el("line", {
        x1: lx, y1: legendY - 5, x2: lx + 26, y2: legendY - 5,
        style: `stroke:${color};stroke-width:4;stroke-linecap:round;`,
      }));
    }
    svg.appendChild(el("text", {
      x: lx + 34, y: legendY, "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:16px;`,
    }, label));
    lx += 34 + label.length * 16 + 28;
  };
  chip(colorVar("positive"), "매출선", false);
  chip(colorVar("negative"), "총비용선", false);
  if (showFixed) chip(colorVar("gray-3"), "고정비", true);

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderBreakevenCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "breakeven-case";
    const h = document.createElement("h3");
    h.className = "breakeven-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderBreakeven(slot, c.data);
  });
}
