/**
 * MCK Slide Design System — Variance table renderer
 *
 * Data-driven budget-vs-actual table with cost_nature inversion (FP&A standard).
 * Pure HTML table — no SVG. Theme-aware via CSS variables.
 *
 * Usage:
 *   import { renderVarianceTable } from "../assets/variance-table.js";
 *   renderVarianceTable("#var-target", {
 *     items: [
 *       { label: "매출",        budget: 1200, actual: 1260 },
 *       { label: "매출원가",    budget:  720, actual:  770, cost_nature: true },
 *       { label: "영업이익",    budget:  180, actual:  165 },
 *       { label: "영업이익률",  budget: 15.0, actual: 13.1, unit: "%" },
 *     ],
 *     columns: ["label","budget","actual","variance_abs","variance_pct"],
 *     highlight_row_index: 2,
 *   });
 */

import { resolveTarget, clear, fmt, pctFmt } from "./chart-helpers.js";

const COL_DEFS = {
  label:        { th: "항목",     cls: "label" },
  budget:       { th: "예산",     cls: "num" },
  actual:       { th: "실적",     cls: "num" },
  variance_abs: { th: "차이",     cls: "num" },
  variance_pct: { th: "차이 %",   cls: "num" },
};

/**
 * Render a variance table.
 *
 * @param {string|Element} target
 * @param {object} data
 * @param {Array<{label:string, budget:number, actual:number, unit?:string, cost_nature?:boolean}>} data.items
 * @param {Array<string>} [data.columns=["label","budget","actual","variance_abs","variance_pct"]]
 * @param {string} [data.unit_default=""]      Unit for budget / actual / abs columns when item.unit is unset
 * @param {number} [data.neutral_threshold_pct=0]  Dead-band: |variance_pct| ≤ threshold reads as neutral
 * @param {number} [data.highlight_row_index]  Row to highlight with gray-4 background
 */
export function renderVarianceTable(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const items = data.items || [];
  if (items.length === 0) {
    throw new Error("[variance] need at least one item");
  }
  const columns = data.columns || ["label", "budget", "actual", "variance_abs", "variance_pct"];
  const unitDefault = data.unit_default ?? "";
  const neutral = data.neutral_threshold_pct ?? 0;
  const highlightIdx = data.highlight_row_index;

  // ── Compute derived columns + state per row ────────────────────────────
  const rows = items.map((it, idx) => {
    const budget = it.budget;
    const actual = it.actual;
    const unit = it.unit ?? unitDefault;
    const isCost = !!it.cost_nature;
    const abs = actual - budget;
    const pct = budget === 0 ? null : (abs / budget) * 100;

    // State: for cost-nature items, flip the sign — increasing cost is bad.
    let state = "neutral";
    if (pct != null) {
      const effective = isCost ? -pct : pct;
      if (effective > neutral) state = "positive";
      else if (effective < -neutral) state = "negative";
    }

    return { ...it, idx, unit, abs, pct, state };
  });

  // ── Build table ────────────────────────────────────────────────────────
  const table = document.createElement("table");
  table.className = "variance-table";

  // <thead>
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((col) => {
    const th = document.createElement("th");
    const def = COL_DEFS[col] || { th: col, cls: "" };
    th.textContent = def.th;
    if (def.cls === "num") th.classList.add("num");
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  // <tbody>
  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    if (highlightIdx === row.idx) tr.classList.add("highlight");

    columns.forEach((col) => {
      const td = document.createElement("td");
      const def = COL_DEFS[col] || { cls: "" };
      if (def.cls === "label") td.classList.add("label");
      if (def.cls === "num")   td.classList.add("num");

      let content = "";
      switch (col) {
        case "label":
          content = row.label;
          break;
        case "budget":
          content = formatVal(row.budget, row.unit);
          break;
        case "actual":
          content = formatVal(row.actual, row.unit);
          break;
        case "variance_abs":
          content = fmt(row.abs, { signed: true, unit: row.unit });
          if (row.state !== "neutral") {
            td.classList.add(row.state === "positive" ? "var-positive" : "var-negative");
          } else {
            td.classList.add("var-neutral");
          }
          break;
        case "variance_pct":
          content = row.pct == null ? "—" : pctFmt(row.pct);
          if (row.state !== "neutral") {
            td.classList.add(row.state === "positive" ? "var-positive" : "var-negative");
          } else {
            td.classList.add("var-neutral");
          }
          break;
        default:
          content = String(row[col] ?? "");
      }
      td.textContent = content;
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.appendChild(table);
  return table;
}

function formatVal(v, unit) {
  if (v == null || Number.isNaN(v)) return "—";
  // For percentage rows we want one decimal; for currency we want no decimals.
  const decimals = unit === "%" || unit === "%p" ? 1 : 0;
  const abs = Math.abs(v);
  const num = decimals === 0
    ? Math.round(abs).toLocaleString("en-US")
    : abs.toFixed(decimals);
  const sign = v < 0 ? "\u2212" : "";
  return `${sign}${num}${unit || ""}`;
}

/**
 * Convenience: render multiple variance cases stacked.
 */
export function renderVarianceTableCases(target, cases) {
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
    renderVarianceTable(slot, c.data);
  });
}
