/**
 * MCK Slide Design System — PVM Bridge chart renderer
 *
 * Price · Volume · Mix variance bridge. An extension of the waterfall:
 * the same cumulative running-total bar structure (base → factor deltas → end),
 * but each factor is *color-separated by type* so the audience reads which
 * driver moved the number, not just up vs down.
 *
 * Inherits from waterfall.js: running-total accumulation, start/end anchors,
 * lo/hi spans, xCenter/yFor coordinates, dashed connectors, net callout.
 * Differs: colors come from `item.type` (price/volume/mix), painted inline via
 * colorVar() (bullet.js / donut.js convention — self-contained, no compiled-CSS
 * class dependency). Bar *position* (above/below running) still follows the
 * delta sign exactly like the waterfall.
 *
 * Usage:
 *   import { renderPvmBridge } from '../assets/pvm-bridge.js';
 *   renderPvmBridge('#p1', {
 *     unit: "억",
 *     items: [
 *       { label: "FY25 매출", value: 1200, type: "base" },
 *       { label: "가격 효과",  value: 145,  type: "price" },
 *       { label: "물량 효과",  value: 90,   type: "volume" },
 *       { label: "믹스 효과",  value: -55,  type: "mix" },
 *       { label: "FY26 매출", value: 1380, type: "end" },
 *     ],
 *   });
 *
 * Data contract:
 *   items[].label  string  category label (below baseline; supports "\n")
 *   items[].value  number  base/end = absolute (anchored at 0);
 *                          price/volume/mix = signed delta from prior running
 *   items[].type   'base'|'end'|'price'|'volume'|'mix'
 *   unit           string  unit suffix on the first base bar + net callout
 *   max_value      number  y-axis max (auto = max bar top × 1.15)
 *   show_connector bool    dashed line between bars (default true)
 *   show_net       bool    base→end net-change callout, top-right (default true)
 */

import { el, createSVG, resolveTarget, fmt, clear, snap, colorVar } from "./chart-helpers.js";

// type → semantic color token (paint inline with colorVar)
const TYPE_COLOR = {
  base: "primary",
  end: "primary",
  price: "accent",
  volume: "positive",
  mix: "gray-2",
};

/**
 * Render a PVM bridge chart into the target container.
 *
 * @param {string|Element} target
 * @param {object} data
 * @param {Array<{label:string, value:number, type:'base'|'end'|'price'|'volume'|'mix'}>} data.items
 * @param {string}  [data.unit=""]
 * @param {number}  [data.max_value]
 * @param {boolean} [data.show_connector=true]
 * @param {boolean} [data.show_net=true]
 */
export function renderPvmBridge(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const items = data.items || [];
  if (items.length < 2) {
    throw new Error("[pvm-bridge] need at least 2 items");
  }
  const unit = data.unit || "";
  const showConnector = data.show_connector !== false;
  const showNet = data.show_net !== false;

  // ── 1. Walk items → running totals + bar spans (waterfall structure) ─────
  let running = 0;
  const bars = items.map((item, idx) => {
    const type = item.type;
    let start, end, signedDelta;

    if (type === "base" || type === "end") {
      // anchor bars: 0 → value (absolute reading)
      start = 0;
      end = item.value;
      running = item.value;
      signedDelta = 0; // no delta label, shows absolute instead
    } else if (type === "price" || type === "volume" || type === "mix") {
      // factor bars: accumulate signed delta from prior running.
      // sign of value decides whether the bar sits above (up) or below (down)
      // the running level — identical to the waterfall.
      signedDelta = item.value;
      start = running;
      end = running + signedDelta;
      running = end;
    } else {
      throw new Error(`[pvm-bridge] unknown type at index ${idx}: ${type}`);
    }

    return {
      ...item,
      idx,
      type,
      start,
      end,
      lo: Math.min(start, end),
      hi: Math.max(start, end),
      signedDelta,
      runningAfter: running,
    };
  });

  // ── 2. Y-axis max (auto = max bar top × 1.15) ───────────────────────────
  const maxBarTop = Math.max(...bars.map((b) => b.hi));
  const maxVal = data.max_value ?? maxBarTop * 1.15;

  // ── 3. Viewport geometry (mirrors waterfall) ────────────────────────────
  const VW = 1000, VH = 500;
  const padLeft = 20, padRight = 20, padTop = 60, padBottom = 110;
  const plotW = VW - padLeft - padRight;
  const plotH = VH - padTop - padBottom;
  const baseline = padTop + plotH;
  const step = plotW / bars.length;
  const barW = Math.min(110, step * 0.62);

  const xCenter = (i) => padLeft + i * step + step / 2;
  const yFor = (v) => snap(baseline - (v / maxVal) * plotH);

  // ── 4. Build SVG ────────────────────────────────────────────────────────
  const svg = createSVG(VW, VH, "pvm-bridge-chart");

  // 4a. Baseline rule
  svg.appendChild(
    el("line", {
      class: "baseline",
      x1: padLeft, y1: baseline,
      x2: padLeft + plotW, y2: baseline,
      style: `stroke:${colorVar("gray-3")};stroke-width:1.5;`,
    })
  );

  // 4b. Connectors (drawn first so bars overlap their endpoints)
  if (showConnector) {
    for (let i = 0; i < bars.length - 1; i++) {
      const cur = bars[i];
      const yJoin = yFor(cur.runningAfter);
      const xFrom = snap(xCenter(i) + barW / 2);
      const xTo = snap(xCenter(i + 1) - barW / 2);
      svg.appendChild(
        el("line", {
          class: "connector",
          x1: xFrom, y1: yJoin,
          x2: xTo, y2: yJoin,
          style: `stroke:${colorVar("gray-2")};stroke-width:1.5;stroke-dasharray:4 4;`,
        })
      );
    }
  }

  // 4c. Bars + labels
  bars.forEach((b, i) => {
    const x = snap(xCenter(i) - barW / 2);
    const yTop = yFor(b.hi);
    const yBot = yFor(b.lo);
    const h = Math.max(2, yBot - yTop); // min height so tiny deltas still show

    const fill = colorVar(TYPE_COLOR[b.type]);
    const group = el("g", { class: `pvm-bar pvm-bar-${b.type}`, "data-index": i });

    // rect — color-separated by factor type
    group.appendChild(el("rect", {
      x: x, y: yTop,
      width: snap(barW),
      height: snap(h),
      style: `fill:${fill};`,
    }));

    // value label above the bar: absolute for base/end, signed delta for factors
    const isAnchor = b.type === "base" || b.type === "end";
    const valueText = isAnchor
      ? fmt(b.value, { unit: i === 0 ? unit : "" })
      : fmt(b.signedDelta, { signed: true });
    group.appendChild(el("text", {
      class: "pvm-bar-value",
      x: snap(xCenter(i)),
      y: snap(yTop - 8),
      "text-anchor": "middle",
      style: `fill:${colorVar("gray-1")};font-weight:800;font-size:20px;`,
    }, valueText));

    // category label below baseline — supports "\n" line breaks
    const labelLines = String(b.label).split(/\n|<br\/?>/);
    const labelY0 = baseline + 24;
    const lineH = 16;
    labelLines.forEach((line, li) => {
      group.appendChild(el("text", {
        class: "pvm-bar-label",
        x: snap(xCenter(i)),
        y: snap(labelY0 + li * lineH),
        "text-anchor": "middle",
        style: `fill:${colorVar("gray-1")};font-weight:600;font-size:16px;`,
      }, line.trim()));
    });

    svg.appendChild(group);
  });

  // 4d. Net-change callout (base → end), top-right of viewbox
  if (showNet && bars.length >= 2) {
    const firstBase = bars.find((b) => b.type === "base");
    const lastEnd = [...bars].reverse().find((b) => b.type === "end")
      || [...bars].reverse().find((b) => b.type === "base");
    if (firstBase && lastEnd && firstBase !== lastEnd) {
      const net = lastEnd.value - firstBase.value;
      const pct = firstBase.value !== 0 ? (net / firstBase.value) * 100 : null;
      const netColor = net >= 0 ? "positive" : "negative";
      const txt = pct == null
        ? `순변동 ${fmt(net, { signed: true, unit })}`
        : `순변동 ${fmt(net, { signed: true, unit })} (${pct >= 0 ? "+" : "−"}${Math.abs(pct).toFixed(1)}%)`;
      svg.appendChild(el("text", {
        class: `pvm-net pvm-net-${netColor}`,
        x: VW - padRight,
        y: padTop - 18,
        "text-anchor": "end",
        style: `fill:${colorVar(netColor)};font-weight:800;font-size:22px;`,
      }, txt));
    }
  }

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 *
 *   renderPvmBridgeCases(container, [{ title, data }, …]);
 */
export function renderPvmBridgeCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "pvm-case";
    const h = document.createElement("h3");
    h.className = "pvm-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderPvmBridge(slot, c.data);
  });
}
