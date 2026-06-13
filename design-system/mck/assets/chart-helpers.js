/**
 * MCK Slide Design System — Chart helpers
 *
 * Shared utilities for data-driven chart components in assets/*.js.
 * SVG-first, theme-aware (uses CSS variables, never hardcoded colors).
 *
 * ─── 5 patterns every chart component follows (extracted from waterfall.js) ──
 *
 * 1. Single function entry: `render<Component>(target, data)`. The only
 *    export. JSDoc above with `@param` per data field. Data is one JSON
 *    object with one required collection (items/segments/kpis/…) plus
 *    optional formatting flags.
 *
 * 2. Theming via CSS variables, never hardcoded colors. SVG fills/strokes
 *    are set in colors_and_type.css under `.<component>-chart …`. JS never
 *    writes `fill="#..."`. Elements that would collapse against `--bg` in
 *    dark mode use `--surface-inverse` (already defined per theme).
 *
 * 3. viewBox + width:100% — author in design units (e.g. 1000×500); the SVG
 *    scales to its container while preserving aspect via `createSVG()`.
 *
 * 4. Forgiving inputs, deterministic outputs. Normalize input (sign coercion,
 *    color-name resolution, item-count caps). Auto-derive everything that
 *    isn't explicitly passed (max_value, layout, colors).
 *
 * 5. Side-by-side `render<Component>Cases(target, cases[])` convenience for
 *    the verification page in `examples/`. Each component ships with a
 *    cases page that proves it survives 3–5 inputs.
 *
 * Plus a slide-level pattern (PART A-2): every data-driven slide guards its
 * mount with `data-rendered` so re-entry / deck-stage switching can't
 * double-render. See `safeRender()` below — call it from `<script type=module>`.
 *
 * Pattern: each chart component (waterfall.js, donut.js, kpi-dashboard.js,
 * variance-table.js) imports from here, then exports a single
 * `render*(target, data)` function.
 */

export const SVG_NS = "http://www.w3.org/2000/svg";

/**
 * Resolve a target argument to a DOM element.
 * Accepts a CSS selector string OR an Element directly.
 * Throws if not found, so callers fail loudly.
 */
export function resolveTarget(target) {
  if (target instanceof Element) return target;
  if (typeof target === "string") {
    const el = document.querySelector(target);
    if (!el) throw new Error(`[mck-chart] target not found: ${target}`);
    return el;
  }
  throw new Error("[mck-chart] target must be a selector string or Element");
}

/**
 * Create an SVG element with attributes and (optionally) text content.
 * Children may be passed as a flat array; nested elements use `el()` calls.
 *
 *   el("rect", { x: 0, y: 0, width: 10, height: 20, class: "bar" })
 *   el("text", { x: 50, y: 60 }, "Hello")
 *   el("g", { class: "bar" }, [el("rect", …), el("text", …, "label")])
 */
export function el(tag, attrs = {}, children = null) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null) continue;
    // `class` is a reserved word in some contexts; support both class and className
    const attr = k === "className" ? "class" : k;
    node.setAttribute(attr, String(v));
  }
  if (children == null) return node;
  if (typeof children === "string" || typeof children === "number") {
    node.textContent = String(children);
  } else if (Array.isArray(children)) {
    for (const child of children) if (child) node.appendChild(child);
  } else {
    node.appendChild(children);
  }
  return node;
}

/**
 * Build a root SVG element sized via viewBox + width 100% so it scales
 * to its container while preserving the design aspect ratio.
 */
export function createSVG(viewWidth, viewHeight, className = "") {
  return el("svg", {
    xmlns: SVG_NS,
    viewBox: `0 0 ${viewWidth} ${viewHeight}`,
    width: "100%",
    height: "auto",
    preserveAspectRatio: "xMidYMid meet",
    class: className,
    role: "img",
  });
}

/**
 * Format a number with thousand separators.
 * Optional sign forcing and unit suffix.
 *
 *   fmt(1260)              -> "1,260"
 *   fmt(1260, { unit: "억" })       -> "1,260억"
 *   fmt(60,  { signed: true })       -> "+60"
 *   fmt(-40, { signed: true })       -> "−40"     (uses U+2212 minus)
 *   fmt(60,  { signed: true, unit: "억" }) -> "+60억"
 */
export function fmt(value, { signed = false, unit = "" } = {}) {
  const abs = Math.abs(value);
  const numStr = abs.toLocaleString("en-US");
  let sign = "";
  if (signed) {
    if (value > 0) sign = "+";
    else if (value < 0) sign = "\u2212"; // proper minus glyph
  } else if (value < 0) {
    sign = "\u2212";
  }
  return `${sign}${numStr}${unit}`;
}

/**
 * Clear all children of a node — used before re-rendering.
 */
export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

/**
 * Snap a number to N decimal places — useful for pixel coordinates.
 */
export function snap(value, decimals = 2) {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
}

/**
 * Slide-level mount guard. Use inside `<script type="module">` to render a
 * data-driven chart safely against re-entry, deck-stage re-mount, etc.
 *
 *   import { safeRender } from "../assets/chart-helpers.js";
 *   import { renderKPIDashboard } from "../assets/kpi-dashboard.js";
 *
 *   safeRender("#kpi-target", renderKPIDashboard, { kpis: [...] });
 *
 * Behavior:
 *  - skip if target not in DOM (e.g. slide not yet mounted)
 *  - skip if `target.dataset.rendered === 'true'` (already rendered)
 *  - on success, sets `data-rendered="true"` and `data-render-ts="<ms>"`
 *  - also listens once for `slide:activated` so late-mounting deck shells
 *    pick up the render on first activation.
 */
export function safeRender(selector, renderFn, ...args) {
  const tryOnce = () => {
    let node;
    try {
      node = typeof selector === "string"
        ? document.querySelector(selector)
        : selector;
    } catch {
      return false;
    }
    if (!node) return false;
    if (node.dataset && node.dataset.rendered === "true") return true;
    renderFn(node, ...args);
    if (node.dataset) {
      node.dataset.rendered = "true";
      node.dataset.renderTs = String(Date.now());
    }
    return true;
  };

  // 1. Immediate attempt
  if (!tryOnce()) {
    // 2. Wait for slide activation if deck-stage gates rendering
    document.addEventListener("slide:activated", tryOnce, { once: false });
    // 3. Fallback: poll briefly in case DOM is just slow
    let tries = 0;
    const handle = setInterval(() => {
      tries++;
      if (tryOnce() || tries > 40) clearInterval(handle); // ~4s max
    }, 100);
  }
}

/**
 * Resolve a semantic color name to a CSS `var(--…)` reference.
 *
 *   colorVar("primary")    -> "var(--primary)"
 *   colorVar("accent")     -> "var(--accent)"
 *   colorVar("gray-2")     -> "var(--gray-2)"
 *   colorVar("#FF0000")    -> "#FF0000"      (passes hex through)
 *   colorVar(undefined, 2) -> default palette ring at index 2
 *
 * Default palette (cycled for auto-assignment):
 *   primary → accent → gray-2 → gray-3 → positive → negative
 */
const DEFAULT_PALETTE = [
  "primary", "accent", "gray-2", "gray-3", "positive", "negative",
];

export function colorVar(name, fallbackIdx = 0) {
  if (typeof name === "string" && name.startsWith("#")) return name;
  if (typeof name === "string" && name.startsWith("var(")) return name;
  const token = name || DEFAULT_PALETTE[fallbackIdx % DEFAULT_PALETTE.length];
  // "primary" is dark-mode-unsafe (collapses into --bg). For chart fills the
  // semantic "primary surface" is `--surface-inverse`, which is identical to
  // --primary in light themes but visible in dark mode.
  if (token === "primary") return "var(--surface-inverse)";
  return `var(--${token})`;
}

/**
 * Polar → cartesian for SVG arc math.
 * Angle in DEGREES, measured clockwise from 12 o'clock (top).
 */
export function polarToCart(cx, cy, r, angleDeg) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

/**
 * Build an SVG arc path string for a ring (donut) segment.
 * startAngle / endAngle in degrees from 12 o'clock, clockwise.
 *
 *   arcPath(50, 50, 40, 30, 0, 90)  // outer 40, inner 30, 0°→90° quadrant
 */
export function arcPath(cx, cy, rOuter, rInner, startAngle, endAngle) {
  const startOuter = polarToCart(cx, cy, rOuter, endAngle);
  const endOuter = polarToCart(cx, cy, rOuter, startAngle);
  const startInner = polarToCart(cx, cy, rInner, endAngle);
  const endInner = polarToCart(cx, cy, rInner, startAngle);
  const largeArc = Math.abs(endAngle - startAngle) > 180 ? 1 : 0;

  // Special-case full circle (avoids degenerate path):
  if (Math.abs(endAngle - startAngle) >= 359.999) {
    // Two half-arcs to form a complete ring
    const midOuter = polarToCart(cx, cy, rOuter, startAngle + 180);
    const midInner = polarToCart(cx, cy, rInner, startAngle + 180);
    return [
      `M ${endOuter.x} ${endOuter.y}`,
      `A ${rOuter} ${rOuter} 0 0 1 ${midOuter.x} ${midOuter.y}`,
      `A ${rOuter} ${rOuter} 0 0 1 ${endOuter.x} ${endOuter.y}`,
      `M ${endInner.x} ${endInner.y}`,
      `A ${rInner} ${rInner} 0 0 0 ${midInner.x} ${midInner.y}`,
      `A ${rInner} ${rInner} 0 0 0 ${endInner.x} ${endInner.y}`,
      "Z",
    ].join(" ");
  }

  return [
    `M ${endOuter.x} ${endOuter.y}`,
    `A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${startOuter.x} ${startOuter.y}`,
    `L ${startInner.x} ${startInner.y}`,
    `A ${rInner} ${rInner} 0 ${largeArc} 0 ${endInner.x} ${endInner.y}`,
    "Z",
  ].join(" ");
}

/**
 * Format a signed percent for display: `+18.3%`, `−1.9%`, `0.0%`.
 *
 *   pctFmt(18.3)              -> "+18.3%"
 *   pctFmt(-1.9)              -> "−1.9%"
 *   pctFmt(1.2, { unit: "%p" }) -> "+1.2%p"
 */
export function pctFmt(value, { unit = "%", decimals = 1, signed = true } = {}) {
  if (value == null || Number.isNaN(value)) return "—";
  const abs = Math.abs(value).toFixed(decimals);
  let sign = "";
  if (signed) {
    if (value > 0) sign = "+";
    else if (value < 0) sign = "\u2212";
  } else if (value < 0) {
    sign = "\u2212";
  }
  return `${sign}${abs}${unit}`;
}

/**
 * Decide whether a YoY value should read as positive / negative / neutral
 * given an optional dead-band (default 0).
 *
 *   yoyState(18.3, 1.0)  -> "positive"
 *   yoyState(-1.9, 1.0)  -> "negative"
 *   yoyState(0.3, 1.0)   -> "neutral"
 */
export function yoyState(value, neutralThreshold = 0) {
  if (value == null || Number.isNaN(value)) return "neutral";
  if (value > neutralThreshold) return "positive";
  if (value < -neutralThreshold) return "negative";
  return "neutral";
}
