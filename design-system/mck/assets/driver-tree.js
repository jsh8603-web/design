/**
 * MCK Slide Design System — Driver Tree (수익성 분해 트리) renderer
 *
 * Horizontal hierarchy tree (left → right) for value-driver decomposition:
 * DuPont (ROIC = margin × turnover), 매출 = 물량 × 단가, KPI breakdowns.
 * Root node (left) → child nodes → grandchildren. Each node is a rounded box
 * (label + bold value). Parent→child links are right-angle elbows. Operator
 * glyphs (×, +, −) sit between sibling child groups. Depth 2–3.
 * Theme-aware: all colors via colorVar() (inline fill — self-contained, no
 * dependency on compiled CSS bundle, mirrors bullet.js / tornado.js).
 *
 * Usage:
 *   import { renderDriverTree } from '../assets/driver-tree.js';
 *   renderDriverTree('#tree-container', {
 *     root: { label: "ROIC", value: "14.0%" },
 *     children: [
 *       { label: "영업이익률", value: "8.0%", op: "×",
 *         children: [ { label: "매출", value: "1,430억" }, { label: "영업이익", value: "114억" } ] },
 *       { label: "자산회전율", value: "1.75x", op: "",
 *         children: [ { label: "매출", value: "1,430억" }, { label: "투하자본", value: "817억" } ] },
 *     ],
 *   });
 *
 * Data contract:
 *   root             object  { label, value } — leftmost root node (highlighted)
 *   root.label       string  node name (top line)
 *   root.value       string  node value (bold, bottom line) — pre-formatted
 *   children         object[] level-1 nodes (vertically stacked, right of root)
 *   children[].op    string  operator glyph drawn in the gutter between this
 *                            child and its sibling (×, +, −, ÷). May be carried
 *                            by either operand of a gap — the example puts × on
 *                            the first child ("영업이익률"). Empty/omitted → none.
 *   children[].children object[] level-2 nodes (grandchildren, right of child).
 *                            Omit → 2-level tree.
 *   <node>.label/.value follow the same shape at every depth.
 *
 * Layout is auto-derived from the leaf count: each leaf (deepest node) gets an
 * equal vertical slot; a parent centers on the vertical span of its children.
 */

import { el, createSVG, resolveTarget, clear, snap, colorVar } from "./chart-helpers.js";

// ── Node box geometry (design units) ────────────────────────────────────────
const NODE_W = 188;
const NODE_H = 64;
const NODE_RX = 10;
const COL_GAP = 96;   // horizontal gap between a node's right edge and its child's left edge
const ROW_GAP = 22;   // minimum vertical gap between leaf boxes

/**
 * Recursively assign vertical centers. Returns the assigned center y of `node`.
 * Leaves consume a slot of height `slotH`; parents center on their children.
 * `cursor` is a mutable { y } tracking the next free leaf slot top.
 */
function layout(node, depth, cursor, slotH) {
  const kids = node.children || [];
  if (kids.length === 0) {
    node._cy = cursor.y + slotH / 2;
    node._depth = depth;
    cursor.y += slotH;
    return node._cy;
  }
  const childCenters = kids.map((k) => layout(k, depth + 1, cursor, slotH));
  node._cy = (childCenters[0] + childCenters[childCenters.length - 1]) / 2;
  node._depth = depth;
  return node._cy;
}

/** Count leaf (deepest) nodes under a subtree — drives the vertical slot count. */
function countLeaves(node) {
  const kids = node.children || [];
  if (kids.length === 0) return 1;
  return kids.reduce((s, k) => s + countLeaves(k), 0);
}

/** Max depth reached below+including this node (root = 0). */
function maxDepth(node, depth = 0) {
  const kids = node.children || [];
  if (kids.length === 0) return depth;
  return Math.max(...kids.map((k) => maxDepth(k, depth + 1)));
}

export function renderDriverTree(target, data) {
  const container = resolveTarget(target);
  clear(container);

  const root = data.root;
  if (!root) throw new Error("[driver-tree] need a root node");
  // Attach children to the root for uniform recursion.
  const tree = { ...root, children: data.children || [] };

  const VW = 1000, VH = 500;
  const padT = 30, padB = 30;
  const plotH = VH - padT - padB;

  const leaves = countLeaves(tree);
  const depth = maxDepth(tree);                 // 0,1,2…
  const slotH = plotH / Math.max(1, leaves);

  // ── Horizontal columns: one x per depth, evenly spread across the canvas ──
  // Total width consumed = depth columns of NODE_W + COL_GAP gaps. Center it.
  const cols = depth + 1;
  const totalW = cols * NODE_W + depth * COL_GAP;
  const padL = Math.max(20, (VW - totalW) / 2);
  const xForDepth = (d) => snap(padL + d * (NODE_W + COL_GAP));

  // ── Assign vertical centers ──────────────────────────────────────────────
  const cursor = { y: padT };
  layout(tree, 0, cursor, slotH);

  const svg = createSVG(VW, VH, "driver-tree-chart");

  // ── Pass 1: connectors (drawn under the boxes) ───────────────────────────
  drawConnectors(svg, tree, xForDepth);

  // ── Pass 2: operator glyphs between sibling groups ───────────────────────
  drawOperators(svg, tree, xForDepth);

  // ── Pass 3: node boxes (root highlighted) ────────────────────────────────
  drawNodes(svg, tree, xForDepth, true);

  container.appendChild(svg);
  return svg;
}

/** Node box (rounded rect + label + bold value), recursing into children. */
function drawNodes(svg, node, xForDepth, isRoot) {
  const x = xForDepth(node._depth);
  const y = snap(node._cy - NODE_H / 2);

  const fill = isRoot ? colorVar("primary") : colorVar("gray-4");
  const stroke = isRoot ? colorVar("primary") : colorVar("gray-3");
  const labelColor = isRoot ? "#FFFFFF" : colorVar("gray-2");
  const valueColor = isRoot ? "#FFFFFF" : colorVar("gray-1");

  const g = el("g", { class: "driver-node" + (isRoot ? " driver-node-root" : "") });
  g.appendChild(el("rect", {
    x, y, width: NODE_W, height: NODE_H, rx: NODE_RX, ry: NODE_RX,
    style: `fill:${fill};stroke:${stroke};stroke-width:1.5;`,
  }));

  // Label (top line) — clipped within the box width via centered anchor.
  g.appendChild(el("text", {
    class: "driver-node-label",
    x: snap(x + NODE_W / 2), y: snap(node._cy - 11),
    "text-anchor": "middle", "dominant-baseline": "central",
    style: `fill:${labelColor};font-weight:600;font-size:16px;`,
  }, String(node.label ?? "")));

  // Value (bottom line) — bold, the hero number.
  g.appendChild(el("text", {
    class: "driver-node-value",
    x: snap(x + NODE_W / 2), y: snap(node._cy + 13),
    "text-anchor": "middle", "dominant-baseline": "central",
    style: `fill:${valueColor};font-weight:800;font-size:21px;`,
  }, String(node.value ?? "")));

  svg.appendChild(g);

  (node.children || []).forEach((k) => drawNodes(svg, k, xForDepth, false));
}

/** Right-angle elbow from each parent's right edge to each child's left edge. */
function drawConnectors(svg, node, xForDepth) {
  const kids = node.children || [];
  if (kids.length === 0) return;

  const parentRight = snap(xForDepth(node._depth) + NODE_W);
  const childLeft = snap(xForDepth(node._depth + 1));
  const midX = snap((parentRight + childLeft) / 2);
  const parentY = snap(node._cy);

  kids.forEach((k) => {
    const childY = snap(k._cy);
    // Elbow: parent edge → horizontal to midX → vertical to childY → into child.
    const d = `M ${parentRight} ${parentY} L ${midX} ${parentY} L ${midX} ${childY} L ${childLeft} ${childY}`;
    svg.appendChild(el("path", {
      class: "driver-link",
      d,
      style: `fill:none;stroke:${colorVar("gray-3")};stroke-width:2;`,
    }));
    drawConnectors(svg, k, xForDepth);
  });
}

function drawOperators(svg, node, xForDepth) {
  const kids = node.children || [];
  // Operator glyph sits in the gutter between parent and children, at the
  // vertical midpoint between consecutive sibling boxes that carry an op.
  const opX = kids.length
    ? snap((xForDepth(node._depth) + NODE_W + xForDepth(node._depth + 1)) / 2)
    : 0;

  kids.forEach((k, i) => {
    // Operator for the gap between sibling i-1 and i. The sample contract puts
    // the glyph on the *first* operand ("영업이익률" carries the ×), so accept an
    // op from either side of the gap — later sibling wins, earlier as fallback.
    const gapOp = i > 0 ? (k.op || kids[i - 1].op) : "";
    if (gapOp) {
      const prev = kids[i - 1];
      const midY = snap((prev._cy + k._cy) / 2);
      // Small backing disc keeps the glyph legible over crossing links.
      svg.appendChild(el("circle", {
        class: "driver-op-bg",
        cx: opX, cy: midY, r: 16,
        style: `fill:var(--bg);stroke:${colorVar("accent")};stroke-width:1.5;`,
      }));
      svg.appendChild(el("text", {
        class: "driver-op",
        x: opX, y: midY,
        "text-anchor": "middle", "dominant-baseline": "central",
        style: `fill:${colorVar("accent")};font-weight:800;font-size:22px;`,
      }, String(gapOp)));
    }
    drawOperators(svg, k, xForDepth);
  });
}

/**
 * Convenience: render multiple cases side-by-side for the verification page.
 */
export function renderDriverTreeCases(target, cases) {
  const container = resolveTarget(target);
  clear(container);
  cases.forEach((c) => {
    const wrap = document.createElement("div");
    wrap.className = "driver-tree-case";
    const h = document.createElement("h3");
    h.className = "driver-tree-case-title";
    h.textContent = c.title || "";
    wrap.appendChild(h);
    const slot = document.createElement("div");
    wrap.appendChild(slot);
    container.appendChild(wrap);
    renderDriverTree(slot, c.data);
  });
}
