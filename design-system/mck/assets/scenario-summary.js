/**
 * MCK Slide Design System — Scenario Summary renderer
 *
 * Executive scenario comparison (Downside / Base / Upside) of key P&L results.
 * One group per KPI metric; within each group, 3 scenario bars side-by-side
 * with the value labelled above each bar. Scenario color is fixed across all
 * groups so the eye reads "red = Downside, navy = Base, green = Upside".
 *
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on the compiled CSS bundle, mirrors bullet.js / donut.js).
 *
 * KEY DESIGN DECISION — per-KPI independent scale.
 *   Metrics mix units & magnitudes (매출 ~1500억 vs 영업이익률 ~16.7%). A single
 *   shared y-scale would crush the small metric to a sliver. So each KPI group
 *   gets its own local scale: bar height is relative to the max of *that group's*
 *   3 scenario values only. Cross-group magnitude is intentionally NOT comparable
 *   — values are printed above each bar for the absolute read.
 *
 * Usage:
 *   import { renderScenarioSummary } from '../assets/scenario-summary.js';
 *   renderScenarioSummary('#sc1', {
 *     scenarios: ["Downside", "Base", "Upside"],
 *     metrics: [
 *       { label: "매출",     values: [1100, 1300, 1500], unit: "억" },
 *       { label: "영업이익",  values: [120, 180, 250],    unit: "억" },
 *       { label: "영업이익률", values: [10.9, 13.8, 16.7], unit: "%" }
 *     ]
 *   });
 *
 * Data contract:
 *   scenarios     string[]  scenario names, order = bar order within each group.
 *                           Color is keyed by name (Downside/Base/Upside) when
 *                           recognised, else falls back to position. (required)
 *   metrics[].label  string   KPI name → group label under the bars (required)
 *   metrics[].values number[] one value per scenario, same order as `scenarios`
 *                             (required, length must match scenarios)
 *   metrics[].unit   string   per-metric unit suffix on the value labels (optional)
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

// Fixed scenario → semantic color. Name-keyed (case-insensitive) so order in
// the `scenarios` array doesn't change the color mapping. Unknown names fall
// back to a positional ring so the chart still renders.
const SCENARIO_COLOR = {
  downside: "negative",
  base: "primary",
  upside: "positive",
};
const FALLBACK_RING = ["negative", "primary", "positive"];

function scenarioColorToken(name, idx) {
  const key = String(name).trim().toLowerCase();
  return SCENARIO_COLOR[key] || FALLBACK_RING[idx % FALLBACK_RING.length];
}

export function renderScenarioSummary(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const scenarios = data.scenarios || [];
  const metrics = data.metrics || [];
  if (scenarios.length < 1) throw new Error("[scenario-summary] need at least 1 scenario");
  if (metrics.length < 1) throw new Error("[scenario-summary] need at least 1 metric");

  // ── Viewport geometry ────────────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padL = 24, padR = 24, padT = 76, padB = 56;
  const plotW = VW - padL - padR;
  const plotH = VH - padT - padB;
  const groups = metrics.length;
  const groupW = plotW / groups;

  // Within a group: leave side gutters, split remaining width across N bars.
  const nBars = scenarios.length;
  const groupGutter = groupW * 0.16;        // empty space each side of a group
  const innerW = groupW - groupGutter * 2;
  const barGap = innerW * 0.08;             // gap between bars in a group
  const barW = (innerW - barGap * (nBars - 1)) / nBars;
  const baseY = padT + plotH;               // bars sit on this baseline

  const svg = createSVG(VW, VH, "scenario-summary-chart");

  // ── Legend (top) — scenario color chips ───────────────────────────────────
  // Centered cluster of [chip + name] pairs.
  const chip = 16, chipGap = 9, itemGap = 32, fontSz = 17;
  // Rough width estimate: chip + gap + ~ (chars * 0.62 * font) per item.
  const itemWidths = scenarios.map((s) => chip + chipGap + String(s).length * fontSz * 0.62);
  const legendW = itemWidths.reduce((a, w) => a + w, 0) + itemGap * (nBars - 1);
  let lx = snap((VW - legendW) / 2);
  const ly = 30;
  scenarios.forEach((s, i) => {
    const token = scenarioColorToken(s, i);
    svg.appendChild(el("rect", {
      class: "scenario-legend-chip",
      x: lx, y: snap(ly - chip / 2), width: chip, height: chip, rx: 3,
      style: `fill:${colorVar(token)};`,
    }));
    svg.appendChild(el("text", {
      class: "scenario-legend-label",
      x: snap(lx + chip + chipGap), y: snap(ly),
      "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:${fontSz}px;`,
    }, String(s)));
    lx = snap(lx + itemWidths[i] + itemGap);
  });

  // ── Groups (one per metric, independent scale) ─────────────────────────────
  metrics.forEach((m, gi) => {
    const values = m.values || [];
    // Per-KPI independent scale: max of THIS group's values only, +headroom for
    // the value label that sits above the tallest bar. Guard against all-zero /
    // negatives so the bars never invert.
    const groupMax = Math.max(0, ...values.map((v) => Math.abs(v))) * 1.18 || 1;
    const gx0 = padL + gi * groupW + groupGutter;

    values.forEach((vRaw, bi) => {
      const v = Number(vRaw) || 0;
      const token = scenarioColorToken(scenarios[bi], bi);
      const bx = snap(gx0 + bi * (barW + barGap));
      const h = Math.max(2, snap((Math.abs(v) / groupMax) * plotH));
      const by = snap(baseY - h);

      // Bar
      svg.appendChild(el("rect", {
        class: "scenario-bar",
        x: bx, y: by, width: snap(barW), height: h, rx: 2,
        style: `fill:${colorVar(token)};`,
      }));

      // Value above bar
      svg.appendChild(el("text", {
        class: "scenario-value",
        x: snap(bx + barW / 2), y: snap(by - 9),
        "text-anchor": "middle", "dominant-baseline": "alphabetic",
        style: `fill:${colorVar("gray-1")};font-weight:800;font-size:18px;`,
      }, fmt(v, { unit: m.unit || "" })));
    });

    // KPI group label (bottom, centered under the group)
    svg.appendChild(el("text", {
      class: "scenario-group-label",
      x: snap(gx0 + innerW / 2), y: snap(baseY + 30),
      "text-anchor": "middle", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:20px;`,
    }, String(m.label)));
  });

  // Baseline rule
  svg.appendChild(el("line", {
    class: "scenario-baseline",
    x1: padL, y1: snap(baseY), x2: VW - padR, y2: snap(baseY),
    style: `stroke:${colorVar("gray-3")};stroke-width:1.5;`,
  }));

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderScenarioSummaryCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "scenario-summary-case";
    const h = document.createElement("h3");
    h.className = "scenario-summary-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderScenarioSummary(slot, c.data);
  });
}
