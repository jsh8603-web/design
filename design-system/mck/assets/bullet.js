/**
 * MCK Slide Design System — Bullet chart renderer
 *
 * Horizontal bullet graphs (Stephen Few) — actual vs target vs qualitative bands.
 * One row per KPI. FP&A use: KPI scorecards, board packs, dashboard panels.
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on compiled CSS bundle, mirrors donut.js / kpi-dashboard.js).
 *
 * Usage:
 *   import { renderBullet } from '../assets/bullet.js';
 *   renderBullet('#bullet-container', {
 *     items: [
 *       { label: "매출",   measure: 1430, target: 1200, ranges: [800, 1100, 1500] },
 *       { label: "영업이익", measure: 168,  target: 200,  ranges: [120, 180, 240] },
 *     ],
 *     unit: "억원"
 *   });
 *
 * Data contract:
 *   items[].label    string  KPI name (left, right-aligned)
 *   items[].measure  number  actual value → solid inner bar
 *   items[].target   number  goal → vertical tick marker        (optional)
 *   items[].ranges   number[] ascending band thresholds          (optional)
 *                            e.g. [poor, satisfactory, good] → 3 grey bands
 *   items[].unit     string  per-row unit suffix (overrides global unit) (optional)
 *   unit             string  default unit suffix on each row's value (optional)
 *   shared_scale     bool    one x-scale across all rows (default false —
 *                            KPIs usually differ in unit/scale, so per-row)
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

export function renderBullet(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const items = data.items || [];
  if (items.length < 1) {
    throw new Error("[bullet] need at least 1 item");
  }
  const unit = data.unit || "";
  const sharedScale = data.shared_scale === true;

  // ── Shared x-scale (max over every band/measure/target across rows) ──────
  const rowCeil = (it) =>
    Math.max(it.target ?? 0, it.measure ?? 0, ...((it.ranges) || [0]));
  const globalMax = Math.max(...items.map(rowCeil)) * 1.05;

  // ── Viewport geometry ────────────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padL = 220, padR = 112, padT = 34, padB = 26;
  const plotW = VW - padL - padR;
  const plotH = VH - padT - padB;
  const rows = items.length;
  const rowH = plotH / rows;

  const svg = createSVG(VW, VH, "bullet-chart");

  items.forEach((it, i) => {
    const rowMax = sharedScale ? globalMax : rowCeil(it) * 1.05;
    const xFor = (v) => snap(padL + (Math.max(0, v) / rowMax) * plotW);
    const yMid = padT + i * rowH + rowH / 2;
    const bandH = Math.min(48, rowH * 0.66);
    const bandY = snap(yMid - bandH / 2);
    const measureH = snap(bandH * 0.34);
    const measureY = snap(yMid - measureH / 2);

    // 1. Qualitative bands — low range darker, high range lighter (Few convention)
    const ranges = (it.ranges || []).slice().sort((a, b) => a - b);
    let prev = 0;
    ranges.forEach((r, ri) => {
      const x0 = xFor(prev), x1 = xFor(r);
      const w = Math.max(0, snap(x1 - x0));
      if (w > 0) {
        svg.appendChild(el("rect", {
          class: "bullet-band",
          x: x0, y: bandY, width: w, height: snap(bandH),
          style: `fill:${colorVar(ri === 0 ? "gray-3" : "gray-4")};`,
        }));
      }
      prev = r;
    });

    // 2. Measure bar (solid, centered, dark)
    const mw = Math.max(2, xFor(it.measure) - xFor(0));
    svg.appendChild(el("rect", {
      class: "bullet-measure",
      x: xFor(0), y: measureY, width: snap(mw), height: measureH,
      style: `fill:${colorVar("primary")};`,
    }));

    // 3. Target tick (vertical marker)
    if (it.target != null) {
      const tx = xFor(it.target);
      svg.appendChild(el("line", {
        class: "bullet-target",
        x1: tx, y1: snap(bandY - 4), x2: tx, y2: snap(bandY + bandH + 4),
        style: `stroke:${colorVar("accent")};stroke-width:3.5;`,
      }));
    }

    // 4. KPI label (left, right-aligned)
    svg.appendChild(el("text", {
      class: "bullet-label",
      x: padL - 16, y: snap(yMid),
      "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:22px;`,
    }, String(it.label)));

    // 5. Value + delta-vs-target (right of plot)
    const delta = it.target != null ? it.measure - it.target : null;
    svg.appendChild(el("text", {
      class: "bullet-value",
      x: VW - padR + 14, y: snap(delta != null ? yMid - 8 : yMid),
      "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:800;font-size:21px;`,
    }, fmt(it.measure, { unit: it.unit ?? unit })));
    if (delta != null) {
      const dColor = delta >= 0 ? "positive" : "negative";
      const arrow = delta >= 0 ? "▲ " : "▼ ";
      svg.appendChild(el("text", {
        class: "bullet-delta",
        x: VW - padR + 14, y: snap(yMid + 13),
        "dominant-baseline": "central",
        style: `fill:${colorVar(dColor)};font-weight:700;font-size:14px;`,
      }, arrow + fmt(Math.abs(delta), { unit: "" })));
    }
  });

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderBulletCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "bullet-case";
    const h = document.createElement("h3");
    h.className = "bullet-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderBullet(slot, c.data);
  });
}
