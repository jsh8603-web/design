/**
 * MCK Slide Design System — Cohort retention heatmap renderer
 *
 * Retention grid: one row per signup cohort, one column per elapsed period
 * (M0, M1, …), each cell = retention % shaded on a continuous color ramp.
 * FP&A / growth use: cohort retention curves, churn diagnosis, LTV inputs.
 *
 * ── Color exception (documented) ──────────────────────────────────────────
 * Every other chart in this system fills via colorVar() / CSS tokens. This
 * one is the lone exception: a continuous heatmap needs per-value shading,
 * and colorVar() only resolves fixed semantic tokens (no interpolation). So
 * cells are filled with hex computed by RGB-lerping a single-hue sequential
 * ramp (ColorBrewer "Blues"). 5 closely-spaced stops avoid lerp banding /
 * muddy midtones. Labels/headers still use colorVar() like every other chart.
 *
 * Usage:
 *   import { renderCohortHeatmap } from '../assets/cohort-heatmap.js';
 *   renderCohortHeatmap('#c1', {
 *     periods: ["M0","M1","M2","M3","M4","M5","M6"],
 *     cohorts: [
 *       { label: "25-01", values: [100, 82, 71, 65, 60, 57, 55] },
 *       { label: "25-02", values: [100, 79, 68, 61, 56, 53, null] },
 *     ],
 *   });
 *
 * Data contract:
 *   periods         string[]  column headers, left→right elapsed periods (M0…Mn)
 *   cohorts[].label string    row label (signup cohort), left, right-aligned
 *   cohorts[].values (number|null)[]  retention % per period; length == periods
 *                            null = period not yet elapsed → empty (light gray)
 *   ramp            string[]  optional hex stops (light→dark) overriding default
 *   domain          [min,max] optional value range for color mapping (def [0,100])
 */

import { el, createSVG, resolveTarget, clear, snap, colorVar } from "./chart-helpers.js";

// Single-hue sequential "Blues" ramp, light → dark. 5 stops keeps lerp tight
// so the continuous fill doesn't band or go muddy across the 0–100% range.
const DEFAULT_RAMP = ["#EFF6FB", "#C6DCEC", "#8CB8DA", "#4A90C2", "#2A6D9C"];

// ── hex color helpers (heatmap-local, see exception note above) ──────────────
function hexToRgb(hex) {
  const h = hex.replace("#", "");
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  };
}

function rgbToHex({ r, g, b }) {
  const c = (n) => Math.round(Math.max(0, Math.min(255, n))).toString(16).padStart(2, "0");
  return `#${c(r)}${c(g)}${c(b)}`;
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

/**
 * Map t∈[0,1] onto a multi-stop hex ramp via per-channel RGB lerp.
 * t is clamped; ramp must have ≥2 stops.
 */
function rampColor(ramp, t) {
  const x = Math.max(0, Math.min(1, t));
  const segs = ramp.length - 1;
  const pos = x * segs;
  const i = Math.min(segs - 1, Math.floor(pos));
  const f = pos - i;
  const a = hexToRgb(ramp[i]);
  const b = hexToRgb(ramp[i + 1]);
  return rgbToHex({
    r: lerp(a.r, b.r, f),
    g: lerp(a.g, b.g, f),
    b: lerp(a.b, b.b, f),
  });
}

/**
 * Relative luminance (sRGB, 0–255 in) → 0..1. Used to flip cell text to white
 * on dark fills, dark on light fills, so the % is always legible.
 */
function luminance(hex) {
  const { r, g, b } = hexToRgb(hex);
  return (0.2126 * r + 0.7152 * g + 0.1152 * b) / 255;
}

export function renderCohortHeatmap(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const periods = data.periods || [];
  const cohorts = data.cohorts || [];
  if (periods.length < 1 || cohorts.length < 1) {
    throw new Error("[cohort-heatmap] need ≥1 period and ≥1 cohort");
  }
  const ramp = Array.isArray(data.ramp) && data.ramp.length >= 2 ? data.ramp : DEFAULT_RAMP;
  const [dMin, dMax] = data.domain || [0, 100];
  const span = dMax - dMin || 1;

  // ── Viewport geometry ──────────────────────────────────────────────────────
  // The slide's chart-wrap (left:76.8 top:150 in the demo) gives the SVG about
  // a 1126×565 box before the section clips. Author the viewBox to ~that aspect
  // (1000×500) so the rendered grid fills the wrap top-to-bottom instead of
  // piling into the upper half. The grid is then sized to consume the full
  // padded height (gridH = VH − padT − padB), so there's no dead space below —
  // cells get as tall as the box allows (here ≈86 design-units, ~97px rendered).
  const VW = 1000, VH = 500;
  const padL = 120, padR = 24, padT = 52, padB = 16;
  const cols = periods.length;
  const rows = cohorts.length;
  const gridW = VW - padL - padR;
  const gridH = VH - padT - padB;
  const cellW = gridW / cols;
  const cellH = gridH / rows; // rows fill the box exactly → no bottom dead space
  const gap = 3; // hairline gutter between cells

  const svg = createSVG(VW, VH, "cohort-heatmap");

  // 1. Column headers (period labels, centered above each column)
  periods.forEach((p, c) => {
    svg.appendChild(el("text", {
      class: "cohort-col-head",
      x: snap(padL + c * cellW + cellW / 2),
      y: snap(padT - 18),
      "text-anchor": "middle", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-2")};font-weight:700;font-size:20px;`,
    }, String(p)));
  });

  // "코호트" corner label above the row-label column
  svg.appendChild(el("text", {
    class: "cohort-corner",
    x: snap(padL - 16), y: snap(padT - 18),
    "text-anchor": "end", "dominant-baseline": "central",
    style: `fill:${colorVar("gray-3")};font-weight:700;font-size:15px;`,
  }, "코호트"));

  cohorts.forEach((co, r) => {
    const yTop = padT + r * cellH;
    const yMid = yTop + cellH / 2;

    // 2. Row label (cohort name, left, right-aligned)
    svg.appendChild(el("text", {
      class: "cohort-row-label",
      x: snap(padL - 16), y: snap(yMid),
      "text-anchor": "end", "dominant-baseline": "central",
      style: `fill:${colorVar("gray-1")};font-weight:700;font-size:20px;`,
    }, String(co.label)));

    const values = co.values || [];
    periods.forEach((_p, c) => {
      const v = values[c];
      const x = snap(padL + c * cellW + gap / 2);
      const y = snap(yTop + gap / 2);
      const w = snap(cellW - gap);
      const h = snap(cellH - gap);

      // null = not-yet-elapsed → empty light-gray placeholder, no text
      if (v == null || Number.isNaN(v)) {
        svg.appendChild(el("rect", {
          class: "cohort-cell cohort-cell-empty",
          x, y, width: w, height: h, rx: 3,
          style: `fill:${colorVar("gray-4")};`,
        }));
        return;
      }

      // 3. Continuous fill: map value→[0,1]→ramp hex (documented exception)
      const t = (v - dMin) / span;
      const fill = rampColor(ramp, t);
      svg.appendChild(el("rect", {
        class: "cohort-cell",
        x, y, width: w, height: h, rx: 3,
        style: `fill:${fill};`,
      }));

      // 4. Cell value text, luminance-flipped for contrast on its own fill.
      // Threshold 0.62 (not 0.5) because the Blues ramp's mid stops are fairly
      // light — at 0.5 the lower-retention cells (≈50–60%) get white text on
      // pale blue and wash out. Bumping it keeps those cells on dark text.
      const textHex = luminance(fill) < 0.62 ? "#FFFFFF" : "#1A2332";
      svg.appendChild(el("text", {
        class: "cohort-cell-value",
        x: snap(padL + c * cellW + cellW / 2),
        y: snap(yMid),
        "text-anchor": "middle", "dominant-baseline": "central",
        style: `fill:${textHex};font-weight:700;font-size:19px;`,
      }, `${Math.round(v)}%`));
    });
  });

  container.appendChild(svg);
  return svg;
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderCohortHeatmapCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "cohort-case";
    const h = document.createElement("h3");
    h.className = "cohort-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderCohortHeatmap(slot, c.data);
  });
}
