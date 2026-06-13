/**
 * MCK Slide Design System — Waterfall chart renderer
 *
 * Data-driven SVG waterfall (P&L bridge / variance decomposition).
 * Theme-aware: all colors via CSS variables — switches with [data-theme].
 *
 * Usage:
 *   import { renderWaterfall } from '../assets/waterfall.js';
 *   renderWaterfall('#waterfall-container', {
 *     items: [
 *       { label: "FY25 OP",    value: 180, type: "base" },
 *       { label: "매출 증가",   value: 60,  type: "up" },
 *       { label: "물류비 증가", value: -40, type: "down" },
 *       { label: "FY26 OP",    value: 165, type: "base" },
 *     ],
 *     unit: "억원"
 *   });
 */

import { el, createSVG, resolveTarget, fmt, clear, snap } from "./chart-helpers.js";

/**
 * Render a waterfall chart into the target container.
 *
 * @param {string|Element} target  Container selector or DOM element.
 * @param {object} data
 * @param {Array<{label:string, value:number, type:'base'|'up'|'down'|'subtotal'}>} data.items
 * @param {string}  [data.unit=""]            Unit label for base bars (e.g. "억원").
 * @param {number}  [data.max_value]          Y-axis max. Auto = max(running) × 1.15.
 * @param {boolean} [data.show_connector=true] Dashed line between bars.
 * @param {boolean} [data.show_net=true]      Net-change callout (top-right).
 */
export function renderWaterfall(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const items = data.items || [];
  if (items.length < 2) {
    throw new Error("[waterfall] need at least 2 items");
  }
  const unit = data.unit || "";
  const showConnector = data.show_connector !== false;
  const showNet = data.show_net !== false;

  // ── 1. Walk items, compute running totals + bar spans ──────────────────
  // Each bar has a start (y0) and end (y1) value.  Direction sign tells us
  // up vs down for color and label sign.
  let running = 0;
  const bars = items.map((item, idx) => {
    const type = item.type;
    let start, end, signedDelta;

    if (type === "base" || type === "subtotal") {
      // base bars anchor from 0 to value (absolute reading)
      start = 0;
      end = item.value;
      running = item.value;
      signedDelta = 0; // no delta label
    } else if (type === "up") {
      signedDelta = +Math.abs(item.value);
      start = running;
      end = running + signedDelta;
      running = end;
    } else if (type === "down") {
      signedDelta = -Math.abs(item.value);
      start = running;
      end = running + signedDelta;
      running = end;
    } else {
      throw new Error(`[waterfall] unknown type at index ${idx}: ${type}`);
    }

    return {
      ...item,
      idx,
      type,
      start,
      end,
      // Bar is the rectangle between start and end
      lo: Math.min(start, end),
      hi: Math.max(start, end),
      signedDelta,
      runningAfter: running,
    };
  });

  // ── 2. Y-axis max (auto = max of all bar tops × 1.15) ──────────────────
  const maxBarTop = Math.max(...bars.map((b) => b.hi));
  const maxVal = data.max_value ?? maxBarTop * 1.15;

  // ── 3. Viewport geometry ───────────────────────────────────────────────
  const VW = 1000, VH = 500;
  const padLeft = 20, padRight = 20, padTop = 60, padBottom = 110;
  const plotW = VW - padLeft - padRight;
  const plotH = VH - padTop - padBottom;
  const baseline = padTop + plotH;
  const step = plotW / bars.length;
  const barW = Math.min(110, step * 0.62);

  const xCenter = (i) => padLeft + i * step + step / 2;
  const yFor = (v) => snap(baseline - (v / maxVal) * plotH);

  // ── 4. Build SVG ───────────────────────────────────────────────────────
  const svg = createSVG(VW, VH, "waterfall-chart");

  // 4a. Baseline rule
  svg.appendChild(
    el("line", {
      class: "baseline",
      x1: padLeft, y1: baseline,
      x2: padLeft + plotW, y2: baseline,
    })
  );

  // 4b. Connectors (drawn first so bars overlap their endpoints)
  if (showConnector) {
    for (let i = 0; i < bars.length - 1; i++) {
      const cur = bars[i];
      const next = bars[i + 1];
      // Connector sits at the running level between the two bars.
      // - If next is base/subtotal, draw from cur top to next top.
      // - Otherwise draw at the shared running value.
      const yJoin = (next.type === "base" || next.type === "subtotal")
        ? yFor(cur.runningAfter)
        : yFor(cur.runningAfter);
      const xFrom = snap(xCenter(i) + barW / 2);
      const xTo = snap(xCenter(i + 1) - barW / 2);
      svg.appendChild(
        el("line", {
          class: "connector",
          x1: xFrom, y1: yJoin,
          x2: xTo, y2: yJoin,
        })
      );
    }
  }

  // 4c. Bars + labels
  bars.forEach((b, i) => {
    const x = snap(xCenter(i) - barW / 2);
    const yTop = yFor(b.hi);
    const yBot = yFor(b.lo);
    const h = Math.max(2, yBot - yTop); // min height so zero-deltas still show

    const klass = `bar bar-${b.type}`;
    const group = el("g", { class: klass, "data-index": i });

    // rect
    group.appendChild(el("rect", {
      x: x, y: yTop,
      width: snap(barW),
      height: snap(h),
    }));

    // value label above the bar
    const valueText = b.type === "base" || b.type === "subtotal"
      ? fmt(b.value, { unit: i === 0 ? unit : "" })  // only first base shows unit
      : fmt(b.signedDelta, { signed: true });
    group.appendChild(el("text", {
      class: "bar-value",
      x: snap(xCenter(i)),
      y: snap(yTop - 8),
    }, valueText));

    // category label below baseline — supports "\n" line breaks
    const labelLines = String(b.label).split(/\n|<br\/?>/);
    const labelY0 = baseline + 22;
    const lineH = 14;
    labelLines.forEach((line, li) => {
      group.appendChild(el("text", {
        class: "bar-label",
        x: snap(xCenter(i)),
        y: snap(labelY0 + li * lineH),
      }, line.trim()));
    });

    svg.appendChild(group);
  });

  // 4d. Net-change callout (top-right of viewbox)
  if (showNet && bars.length >= 2) {
    const firstBase = bars.find((b) => b.type === "base");
    const lastBase = [...bars].reverse().find((b) => b.type === "base");
    if (firstBase && lastBase && firstBase !== lastBase) {
      const net = lastBase.value - firstBase.value;
      const pct = firstBase.value !== 0
        ? (net / firstBase.value) * 100
        : null;
      const netSign = net >= 0 ? "positive" : "negative";
      const txt = pct == null
        ? `\uc21c\ubcc0\ub3d9 ${fmt(net, { signed: true, unit })}`
        : `\uc21c\ubcc0\ub3d9 ${fmt(net, { signed: true, unit })} (${pct >= 0 ? "+" : "\u2212"}${Math.abs(pct).toFixed(1)}%)`;
      svg.appendChild(el("text", {
        class: `wf-net wf-net-${netSign}`,
        x: VW - padRight,
        y: padTop - 18,
        "text-anchor": "end",
      }, txt));
    }
  }

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side. Used by examples/test pages.
 *
 *   renderWaterfallCases(container, [{ title, data }, …]);
 */
export function renderWaterfallCases(target, cases) {
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
    renderWaterfall(slot, c.data);
  });
}
