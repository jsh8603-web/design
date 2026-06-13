"""Driver tree (수익성 분해 트리) — PPTX renderer (mirror of mck/assets/driver-tree.js).

Horizontal value-driver decomposition (left → right): root → children →
grandchildren (DuPont ROIC = margin × turnover, 매출 = 물량 × 단가, KPI breakdown).
Each node is a box (label + bold value, 2 lines). Parent→child links are
right-angle elbows (horizontal add_hline + thin vertical add_rect). Operator
glyphs (×, +, −, ÷) sit on a small add_oval disc between sibling groups.

Pattern mirrors fpna_charts.bullet / fc_tornado: @register + inches geometry off
theme.layout + add_action_title/source/page + bottom _baseline registration.
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_oval, add_hline, add_textbox
from deck_system.helpers.text import set_run
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


# ── Node box geometry (inches) ──────────────────────────────────────────────
NODE_W = 2.05
NODE_H = 0.78
LINK_THICK = 0.022   # vertical elbow segment thickness (inches)
OP_R = 0.17          # operator disc radius (inches)


def _leaves(node) -> int:
    kids = node.get("children") or []
    if not kids:
        return 1
    return sum(_leaves(k) for k in kids)


def _max_depth(node, depth: int = 0) -> int:
    kids = node.get("children") or []
    if not kids:
        return depth
    return max(_max_depth(k, depth + 1) for k in kids)


def _layout(node, depth: int, cursor: dict, slot_h: float) -> float:
    """Assign a vertical center (_cy) and _depth to every node.

    Leaves consume one slot; parents center on the span of their children.
    `cursor['y']` tracks the next free leaf-slot top. Returns node._cy.
    """
    node["_depth"] = depth
    kids = node.get("children") or []
    if not kids:
        node["_cy"] = cursor["y"] + slot_h / 2.0
        cursor["y"] += slot_h
        return node["_cy"]
    centers = [_layout(k, depth + 1, cursor, slot_h) for k in kids]
    node["_cy"] = (centers[0] + centers[-1]) / 2.0
    return node["_cy"]


# ────────────────────────────────────────────────────────────────────
# DRIVER_TREE — root: {label, value}, children: [{label, value, op?, children?}]
# horizontal hierarchy; elbow links; operator discs between siblings.
# ────────────────────────────────────────────────────────────────────
@register("driver_tree")
def driver_tree(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    root = spec.get("root")
    if not root:
        raise ValueError("[driver_tree] need a root node")
    children = spec.get("children") or []

    # Uniform recursion: attach children onto a copy of root.
    tree = {**root, "children": children}

    # ── Plot box (inches) ────────────────────────────────────────────
    plot_left = L.margin_left_in
    plot_top = L.content_top_in + 0.15
    plot_w = L.content_width_in
    plot_h = 4.6

    leaves = max(1, _leaves(tree))
    depth = _max_depth(tree)             # 0, 1, 2…
    slot_h = plot_h / leaves

    # ── Horizontal columns: one x per depth, spread across the plot ──
    cols = depth + 1
    if cols > 1:
        # remaining horizontal space after the boxes → distribute as gaps
        gap = max(0.6, (plot_w - cols * NODE_W) / depth)
    else:
        gap = 0.0
    used_w = cols * NODE_W + depth * gap
    pad_l = plot_left + max(0.0, (plot_w - used_w) / 2.0)

    def x_for_depth(d: int) -> float:
        return pad_l + d * (NODE_W + gap)

    # ── Assign vertical centers ──────────────────────────────────────
    cursor = {"y": plot_top}
    _layout(tree, 0, cursor, slot_h)

    # Pass 1: connectors (under boxes)
    _draw_connectors(slide, tree, x_for_depth, P)
    # Pass 2: operator discs
    _draw_operators(slide, tree, x_for_depth, theme)
    # Pass 3: node boxes
    _draw_nodes(slide, tree, x_for_depth, theme, is_root=True)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


def _draw_nodes(slide, node, x_for_depth, theme, *, is_root: bool):
    P, T = theme.palette, theme.typography
    x = x_for_depth(node["_depth"])
    y = node["_cy"] - NODE_H / 2.0

    if is_root:
        fill = P.surface_inverse
        label_color = P.surface_inverse_fg
        value_color = P.surface_inverse_fg
    else:
        fill = P.gray_4
        label_color = P.gray_2
        value_color = P.gray_1

    add_rect(slide, x, y, NODE_W, NODE_H, fill)

    # Label + value stacked, vertically centered inside the box.
    tb = add_textbox(slide, x + 0.06, y, NODE_W - 0.12, NODE_H)
    tf = tb.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = True

    p_label = tf.paragraphs[0]
    p_label.alignment = PP_ALIGN.CENTER
    r = p_label.add_run()
    set_run(r, str(node.get("label", "")), theme=theme,
            size=T.small_size - 1, bold=False, color=label_color)

    p_val = tf.add_paragraph()
    p_val.alignment = PP_ALIGN.CENTER
    r = p_val.add_run()
    set_run(r, str(node.get("value", "")), theme=theme,
            size=T.sub_header_size, bold=True, color=value_color)

    for k in (node.get("children") or []):
        _draw_nodes(slide, k, x_for_depth, theme, is_root=False)


def _draw_connectors(slide, node, x_for_depth, P):
    kids = node.get("children") or []
    if not kids:
        return
    parent_right = x_for_depth(node["_depth"]) + NODE_W
    child_left = x_for_depth(node["_depth"] + 1)
    mid_x = (parent_right + child_left) / 2.0
    parent_y = node["_cy"]

    line_pt = 2.0
    for k in kids:
        child_y = k["_cy"]
        # Horizontal: parent edge → mid_x at parent_y
        add_hline(slide, parent_right, parent_y, mid_x - parent_right,
                  P.gray_3, thickness_pt=line_pt)
        # Vertical elbow: mid_x from parent_y to child_y (thin rect)
        top = min(parent_y, child_y)
        height = abs(child_y - parent_y)
        if height > 0.001:
            add_rect(slide, mid_x - LINK_THICK / 2.0, top, LINK_THICK, height,
                     P.gray_3)
        # Horizontal: mid_x → child edge at child_y
        add_hline(slide, mid_x, child_y, child_left - mid_x,
                  P.gray_3, thickness_pt=line_pt)
        _draw_connectors(slide, k, x_for_depth, P)


def _draw_operators(slide, node, x_for_depth, theme):
    P, T = theme.palette, theme.typography
    kids = node.get("children") or []
    if kids:
        op_x = (x_for_depth(node["_depth"]) + NODE_W
                + x_for_depth(node["_depth"] + 1)) / 2.0
        for i, k in enumerate(kids):
            if i == 0:
                _draw_operators(slide, k, x_for_depth, theme)
                continue
            # Op carried by either operand of the gap; later sibling wins.
            gap_op = k.get("op") or kids[i - 1].get("op") or ""
            if gap_op:
                prev = kids[i - 1]
                mid_y = (prev["_cy"] + k["_cy"]) / 2.0
                add_oval(slide, op_x - OP_R, mid_y - OP_R,
                         OP_R * 2, OP_R * 2, P.accent)
                tb = add_textbox(slide, op_x - OP_R, mid_y - OP_R,
                                 OP_R * 2, OP_R * 2)
                tf = tb.text_frame
                tf.vertical_anchor = MSO_ANCHOR.MIDDLE
                pp = tf.paragraphs[0]
                pp.alignment = PP_ALIGN.CENTER
                r = pp.add_run()
                set_run(r, str(gap_op), theme=theme,
                        size=T.sub_header_size, bold=True, color=P.white)
            _draw_operators(slide, k, x_for_depth, theme)


# ── schema registration (self-contained; mirrors fpna_charts pattern) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("driver_tree",
          _S("root", required=True),
          _S("children", required=True, type=list),
          example={"title": "ROIC 분해",
                   "root": {"label": "ROIC", "value": "14.0%"},
                   "children": [
                       {"label": "영업이익률", "value": "8.0%", "op": "×",
                        "children": [
                            {"label": "매출", "value": "1,430억"},
                            {"label": "영업이익", "value": "114억"}]},
                       {"label": "자산회전율", "value": "1.75x", "op": "",
                        "children": [
                            {"label": "매출", "value": "1,430억"},
                            {"label": "투하자본", "value": "817억"}]}]})
