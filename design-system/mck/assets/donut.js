/**
 * MCK Slide Design System — Donut chart renderer
 *
 * Data-driven SVG donut chart with leader-line callouts.
 * Theme-aware: all colors via CSS variables — switches with [data-theme].
 *
 * Usage:
 *   import { renderDonut } from "../assets/donut.js";
 *   renderDonut("#donut-target", {
 *     segments: [
 *       { label: "북미", value: 720, color: "primary" },
 *       { label: "유럽", value: 280, color: "accent" },
 *       { label: "아시아", value: 180 },         // color auto-assigned
 *       { label: "기타", value: 80 },
 *     ],
 *     center_value: "1,260억",
 *     center_label: "FY26 매출",
 *   });
 */

import {
  el, createSVG, resolveTarget, clear, snap, colorVar, arcPath, polarToCart,
} from "./chart-helpers.js";

/**
 * Render a donut chart with leader-line callouts into the target container.
 *
 * @param {string|Element} target
 * @param {object} data
 * @param {Array<{label:string, value:number, color?:string}>} data.segments
 * @param {string}  [data.center_value]        Large center label (e.g. "1,260억")
 * @param {string}  [data.center_label]        Small center label (e.g. "FY26 매출")
 * @param {boolean} [data.show_percent=true]   Show "(38%)" beside each callout
 * @param {boolean} [data.show_value=true]     Show absolute value beside callout
 * @param {"right"|"left"} [data.callout_position="right"]
 * @param {number}  [data.max_segments=6]      Top-(N-1) shown, rest merged into "기타"
 */
export function renderDonut(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const segmentsIn = (data.segments || []).filter((s) => s && s.value > 0);
  if (segmentsIn.length === 0) {
    throw new Error("[donut] need at least one segment with value > 0");
  }
  const maxSeg = data.max_segments ?? 6;
  const showPct = data.show_percent !== false;
  const showVal = data.show_value !== false;
  const calloutSide = data.callout_position === "left" ? "left" : "right";

  // ── 1. Auto-merge tail into "기타" if more than max_segments ─────────────
  let segs = [...segmentsIn].sort((a, b) => b.value - a.value);
  if (segs.length > maxSeg) {
    const head = segs.slice(0, maxSeg - 1);
    const tail = segs.slice(maxSeg - 1);
    const tailSum = tail.reduce((acc, s) => acc + s.value, 0);
    segs = [
      ...head,
      { label: "기타", value: tailSum, color: "gray-3", _merged: true },
    ];
  }

  const total = segs.reduce((acc, s) => acc + s.value, 0);

  // ── 2. Annotate each segment with angles + resolved color ──────────────
  let cursor = 0;
  const arcs = segs.map((s, i) => {
    const pct = s.value / total;
    const startAngle = cursor * 360;
    cursor += pct;
    const endAngle = cursor * 360;
    return {
      ...s,
      idx: i,
      pct,
      startAngle,
      endAngle,
      midAngle: (startAngle + endAngle) / 2,
      colorRef: colorVar(s.color, i),
    };
  });

  // ── 3. Geometry ────────────────────────────────────────────────────────
  // Aspect ~2.94:1 (1000×340) keeps the SVG short enough that at 1126px wide
  // it renders ~383px tall, fitting under any standard slide bottom-bar.
  const VW = 1000, VH = 340;
  const padTop = 14, padBottom = 14;

  // Donut sits on one side; callouts on the other.
  const ringSide = calloutSide === "right" ? "left" : "right";
  const donutCx = ringSide === "left" ? 190 : VW - 190;
  const donutCy = VH / 2;
  const rOuter = 140;
  const rInner = 94;

  // ── 4. SVG root + segments ─────────────────────────────────────────────
  const svg = createSVG(VW, VH, "donut-chart");

  // Track ring background (light gray) — visible if a single 100% segment is drawn
  svg.appendChild(el("circle", {
    class: "donut-track",
    cx: donutCx, cy: donutCy, r: (rOuter + rInner) / 2,
    fill: "none", "stroke-width": rOuter - rInner,
  }));

  // Arcs
  arcs.forEach((a) => {
    const d = arcPath(donutCx, donutCy, rOuter, rInner, a.startAngle, a.endAngle);
    const seg = el("path", {
      class: `donut-segment ${a._merged ? "is-merged" : ""}`,
      d,
      "data-index": a.idx,
      style: `fill: ${a.colorRef};`,
    });
    svg.appendChild(seg);
  });

  // ── 5. Center label ────────────────────────────────────────────────────
  if (data.center_value) {
    svg.appendChild(el("text", {
      class: "donut-center-value",
      x: donutCx, y: donutCy - 4,
      "text-anchor": "middle",
      "dominant-baseline": "alphabetic",
    }, data.center_value));
  }
  if (data.center_label) {
    svg.appendChild(el("text", {
      class: "donut-center-label",
      x: donutCx, y: donutCy + 26,
      "text-anchor": "middle",
    }, data.center_label));
  }

  // ── 6. Callouts: leader lines + label rows on the opposite side ────────
  // Lay rows out vertically; if N ≤ 5, even spacing in the donut height;
  // if more, compress toward center proportional to share of total.
  const calloutX0 = calloutSide === "right" ? donutCx + rOuter + 40 : donutCx - rOuter - 40;
  const calloutAnchor = calloutSide === "right" ? "start" : "end";
  const rowCount = arcs.length;
  const rowH = Math.min(48, (VH - padTop - padBottom) / Math.max(rowCount, 1));
  const rowsTotalH = rowH * rowCount;
  const rowsStartY = (VH - rowsTotalH) / 2 + rowH / 2;

  arcs.forEach((a, i) => {
    const rowY = rowsStartY + i * rowH;

    // Leader lines removed in v2.2.1 — color-coded swatches are sufficient
    // to bind callouts to segments.  Re-introduce by uncommenting below.
    // const fromPt = polarToCart(donutCx, donutCy, rOuter + 6, a.midAngle);
    // const elbowX = calloutSide === "right" ? (donutCx + rOuter + 24) : (donutCx - rOuter - 24);
    // svg.appendChild(el("path", { class: "donut-leader", d: ..., fill: "none" }));

    // Swatch
    const swatchX = calloutSide === "right" ? calloutX0 : calloutX0 - 14;
    svg.appendChild(el("rect", {
      class: "donut-swatch",
      x: swatchX, y: rowY - 7, width: 14, height: 14,
      style: `fill: ${a.colorRef};`,
    }));

    // Label group
    const labelX = calloutSide === "right" ? calloutX0 + 22 : calloutX0 - 22;
    const pctStr = `${(a.pct * 100).toFixed(a.pct < 0.1 ? 1 : 0)}%`;
    svg.appendChild(el("text", {
      class: "donut-callout-label",
      x: labelX, y: rowY - 2,
      "text-anchor": calloutAnchor,
    }, a.label));
    const subParts = [];
    if (showVal) subParts.push(a.value.toLocaleString("en-US"));
    if (showPct) subParts.push(pctStr);
    if (subParts.length) {
      svg.appendChild(el("text", {
        class: "donut-callout-sub",
        x: labelX, y: rowY + 14,
        "text-anchor": calloutAnchor,
      }, subParts.join(" · ")));
    }
  });

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple donut cases stacked. Used by examples pages.
 */
export function renderDonutCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "wf-case";
    const h = document.createElement("h3");
    h.className = "wf-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    slot.className = "wf-case-slot";
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderDonut(slot, c.data);
  });
}
