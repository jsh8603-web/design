/**
 * MCK Slide Design System — KPI dashboard renderer
 *
 * Data-driven KPI tile grid with auto-layout and ▲▼ direction markers.
 * Pure DOM (no SVG) — uses CSS grid for layout, theme-aware via variables.
 *
 * Usage:
 *   import { renderKPIDashboard } from "../assets/kpi-dashboard.js";
 *   renderKPIDashboard("#kpi-target", {
 *     kpis: [
 *       { label: "매출",        value: "1,260억", yoy: 18.3, detail: "FY25 1,065억" },
 *       { label: "활성 고객",   value: "2,400만", yoy: 12.1 },
 *       { label: "GMV",         value: "5,800억", yoy: 22.0 },
 *       { label: "영업이익률",  value: "13.1%",   yoy: -1.9, yoy_label: "YoY (%p)" },
 *     ],
 *     layout: "auto",
 *   });
 */

import { resolveTarget, clear, pctFmt, yoyState } from "./chart-helpers.js";

/**
 * Render a KPI dashboard.
 *
 * @param {string|Element} target
 * @param {object} data
 * @param {Array<{label:string,value:string|number,yoy?:number,yoy_label?:string,detail?:string,value_suffix?:string}>} data.kpis
 * @param {"auto"|"1x3"|"1x4"|"1x5"|"2x2"|"2x3"|"2x4"|"3x2"} [data.layout="auto"]
 * @param {number} [data.neutral_threshold=0]  Dead-band; |yoy| ≤ threshold reads as neutral
 */
export function renderKPIDashboard(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const kpis = data.kpis || [];
  if (kpis.length === 0) {
    throw new Error("[kpi] need at least one KPI");
  }
  const neutralThreshold = data.neutral_threshold ?? 0;

  // ── Auto-layout decision ───────────────────────────────────────────────
  const n = kpis.length;
  let layout = data.layout || "auto";
  if (layout === "auto") {
    if (n === 3) layout = "1x3";
    else if (n === 4) layout = "2x2";
    else if (n === 5) layout = "1x5";
    else if (n === 6) layout = "2x3";
    else if (n === 8) layout = "2x4";
    else layout = `1x${n}`; // fallback: single row
  }

  // ── Build grid ─────────────────────────────────────────────────────────
  const grid = document.createElement("div");
  grid.className = `kpi-grid layout-${layout}`;

  kpis.forEach((kpi) => {
    const tile = document.createElement("div");
    tile.className = "kpi-tile";

    // Head row: label + YoY chip
    const head = document.createElement("div");
    head.className = "kpi-tile__head";

    const lbl = document.createElement("div");
    lbl.className = "kpi-tile__label";
    lbl.textContent = kpi.label || "";
    head.appendChild(lbl);

    if (kpi.yoy != null) {
      const yoy = document.createElement("div");
      const state = yoyState(kpi.yoy, neutralThreshold);
      yoy.className = `kpi-tile__yoy ${state}`;
      const marker = state === "positive" ? "▲" : state === "negative" ? "▼" : "●";
      const yoyUnit = kpi.yoy_label && /%p/i.test(kpi.yoy_label) ? "%p" : "%";
      yoy.textContent = `${marker} ${pctFmt(kpi.yoy, { unit: yoyUnit })}`;
      head.appendChild(yoy);
    }

    tile.appendChild(head);

    // Value + detail
    const valueWrap = document.createElement("div");
    const value = document.createElement("div");
    value.className = "kpi-tile__value";
    value.textContent = String(kpi.value ?? "—");
    if (kpi.value_suffix) {
      const sfx = document.createElement("span");
      sfx.className = "kpi-tile__value-suffix";
      sfx.textContent = kpi.value_suffix;
      value.appendChild(sfx);
    }
    valueWrap.appendChild(value);

    if (kpi.detail) {
      const det = document.createElement("div");
      det.className = "kpi-tile__detail";
      det.textContent = kpi.detail;
      valueWrap.appendChild(det);
    }
    tile.appendChild(valueWrap);

    grid.appendChild(tile);
  });

  container.appendChild(grid);
  return grid;
}

/**
 * Convenience: render multiple KPI cases stacked. Used by examples pages.
 */
export function renderKPIDashboardCases(target, cases) {
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
    renderKPIDashboard(slot, c.data);
  });
}
