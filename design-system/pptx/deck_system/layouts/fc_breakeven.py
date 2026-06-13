"""Breakeven / CVP (cost-volume-profit) chart — PPTX renderer
(mirror of mck/assets/breakeven.js).

Classic break-even chart. X-axis = volume (0 → max). Three lines:
  1. Revenue line    = unit_price × Q              (from origin, slopes up, positive)
  2. Total-cost line = fixed_cost + unit_var_cost × Q (intercept = fixed cost, negative)
  3. Fixed-cost line = fixed_cost                   (horizontal, dashed, gray_3)
Their intersection is the break-even point: Q* = fixed_cost / (unit_price − unit_var_cost).
A marker (oval, primary) + "BEP Q*=N" label + drop-line sit at the crossing.

Pattern mirrors fc_scatter / fpna_charts.bullet: @register + inches geometry off
theme.layout + add_action_title/source/page + bottom _baseline schema. Diagonals
via add_line (rotated rect, NOT connector). Axis rules via add_hline + thin _vline.
"""
from __future__ import annotations

import math

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import (
    add_oval, add_line, add_hline, add_rect, add_textbox,
)
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float):
        v = round(v, 6)
        if float(v).is_integer():
            v = int(v)
    return f"{v:,}{unit}"


def _nice_scale(max_v, count):
    """"Nice" axis bounds + tick list for [0, max] targeting ~count ticks."""
    span = max_v or 1.0
    raw_step = span / max(1, count)
    mag = 10 ** math.floor(math.log10(raw_step)) if raw_step > 0 else 1.0
    norm = raw_step / mag
    if norm < 1.5:
        step = 1
    elif norm < 3:
        step = 2
    elif norm < 7:
        step = 5
    else:
        step = 10
    step *= mag
    nice_max = math.ceil(max_v / step) * step if max_v > 0 else step
    ticks = []
    v = 0.0
    while v <= nice_max + step * 1e-6 and len(ticks) < 200:
        ticks.append(round(v, 6))
        v += step
    return 0.0, nice_max, ticks


def breakeven_point(fixed_cost, unit_price, unit_var_cost):
    """Q* = fixed_cost / (unit_price − unit_var_cost).

    Returns (q, value, feasible). Infeasible (margin ≤ 0) → feasible False.
    """
    margin = unit_price - unit_var_cost  # contribution margin per unit
    if not (margin > 0):
        return float("inf"), float("inf"), False
    q = fixed_cost / margin
    value = unit_price * q  # revenue (== total cost) at break-even
    return q, value, True


def _vline(slide, x, y, length, color_hex, *, thickness=0.022):
    """Thin vertical rule via a narrow filled rect (no connector)."""
    return add_rect(slide, x - thickness / 2, y, thickness, length, color_hex)


def _dashed_line(slide, x1, y1, x2, y2, color_hex, *, thickness_pt=1.5,
                 dash=0.07, gap=0.05):
    """Dashed line — emit short add_line segments along the path."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length <= 0:
        return
    ux, uy = dx / length, dy / length
    pos = 0.0
    while pos < length:
        seg = min(dash, length - pos)
        sx, sy = x1 + ux * pos, y1 + uy * pos
        ex, ey = x1 + ux * (pos + seg), y1 + uy * (pos + seg)
        add_line(slide, sx, sy, ex, ey, color_hex, thickness_pt=thickness_pt)
        pos += dash + gap


# ────────────────────────────────────────────────────────────────────
# BREAKEVEN — fixed_cost, unit_price, unit_var_cost, max_volume, unit, vol_unit
# CVP chart: revenue / total-cost / fixed-cost lines + BEP marker.
# ────────────────────────────────────────────────────────────────────
@register("breakeven")
def breakeven(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    fixed_cost = float(spec.get("fixed_cost", 0) or 0)
    unit_price = float(spec.get("unit_price", 0) or 0)
    unit_var_cost = float(spec.get("unit_var_cost", 0) or 0)
    max_volume = float(spec.get("max_volume", 0) or 0)
    if not (max_volume > 0):
        raise ValueError("[breakeven] max_volume must be > 0")
    unit = spec.get("unit", "")
    vol_unit = spec.get("vol_unit", "")
    tick_count = int(spec.get("ticks", 5))
    show_fixed = spec.get("show_fixed") is not False

    q_bep, v_bep, feasible = breakeven_point(fixed_cost, unit_price, unit_var_cost)

    # ── Domains. X = [0, max_volume]. Y = [0, max(rev, cost) over domain] ──
    rev_at_max = unit_price * max_volume
    cost_at_max = fixed_cost + unit_var_cost * max_volume
    y_top = max(rev_at_max, cost_at_max, fixed_cost)
    x_min, x_max, x_ticks = _nice_scale(max_volume, tick_count)
    y_min, y_max, y_ticks = _nice_scale(y_top, tick_count)
    x_span = (x_max - x_min) or 1.0
    y_span = (y_max - y_min) or 1.0

    # ── Plot geometry (inches) — mirror fc_scatter ──
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.35   # extra room for the legend strip
    chart_w = L.content_width_in
    chart_h = 4.3
    pad_l = 1.1   # y tick labels + y caption
    pad_b = 0.7   # x tick labels + x caption
    pad_r = 0.35
    pad_t = 0.1
    plot_left = chart_left + pad_l
    plot_top = chart_top + pad_t
    plot_w = chart_w - pad_l - pad_r
    plot_h = chart_h - pad_t - pad_b
    plot_bottom = plot_top + plot_h   # x-axis baseline y

    def x_for(v):
        return plot_left + ((v - x_min) / x_span) * plot_w

    def y_for(v):
        return plot_bottom - ((v - y_min) / y_span) * plot_h

    # ── Y-axis gridlines + ticks + labels ──
    for t in y_ticks:
        ty = y_for(t)
        add_hline(slide, plot_left, ty, plot_w, P.gray_4, thickness_pt=0.75)
        add_hline(slide, plot_left - 0.06, ty, 0.06, P.gray_3, thickness_pt=1.2)
        tb = add_textbox(slide, chart_left, ty - 0.12, pad_l - 0.18, 0.24)
        write_paragraph(tb.text_frame, _fmt(t, unit), theme=theme,
                        size=T.small_size, color=P.gray_2, align=PP_ALIGN.RIGHT)

    # ── X-axis ticks + labels ──
    for t in x_ticks:
        tx = x_for(t)
        _vline(slide, tx, plot_bottom, 0.06, P.gray_3, thickness=0.017)
        tb = add_textbox(slide, tx - 0.6, plot_bottom + 0.1, 1.2, 0.24)
        write_paragraph(tb.text_frame, _fmt(t, vol_unit), theme=theme,
                        size=T.small_size, color=P.gray_2, align=PP_ALIGN.CENTER)

    # ── Axis lines (X baseline + Y left) ──
    add_hline(slide, plot_left, plot_bottom, plot_w, P.gray_3, thickness_pt=2)
    _vline(slide, plot_left, plot_top, plot_h, P.gray_3, thickness=0.028)

    # ── Fixed-cost horizontal (dashed, gray_3) ──
    if show_fixed and fixed_cost <= y_max:
        fy = y_for(fixed_cost)
        _dashed_line(slide, plot_left, fy, plot_left + plot_w, fy, P.gray_3,
                     thickness_pt=1.6)

    # ── Total-cost line: fixed_cost → fixed_cost + unit_var_cost·x_max ──
    add_line(slide, x_for(x_min), y_for(fixed_cost),
             x_for(x_max), y_for(fixed_cost + unit_var_cost * x_max),
             P.negative, thickness_pt=3.0)

    # ── Revenue line: 0 → unit_price·x_max (from origin) ──
    add_line(slide, x_for(x_min), y_for(0),
             x_for(x_max), y_for(unit_price * x_max),
             P.positive, thickness_pt=3.0)

    # ── BEP marker + drop-line + label ──
    if feasible and q_bep <= x_max:
        bx = x_for(q_bep)
        by = y_for(v_bep)
        # drop-line down to the X axis so the volume reads off the axis
        _dashed_line(slide, bx, by, bx, plot_bottom, P.primary,
                     thickness_pt=1.4, dash=0.05, gap=0.05)
        dot = 0.18
        add_oval(slide, bx - dot / 2, by - dot / 2, dot, dot, P.primary)
        tb = add_textbox(slide, bx + 0.12, by - 0.42, 2.6, 0.3)
        write_paragraph(tb.text_frame,
                        f"BEP Q*={_fmt(round(q_bep), vol_unit)}", theme=theme,
                        size=T.small_size, bold=True, color=P.primary,
                        align=PP_ALIGN.LEFT)

    # ── Axis captions ──
    tb = add_textbox(slide, plot_left, chart_top + chart_h + 0.04, plot_w, 0.3)
    write_paragraph(tb.text_frame, f"물량 ({vol_unit or '수량'})", theme=theme,
                    size=T.sub_header_size, bold=True, color=P.gray_1,
                    align=PP_ALIGN.CENTER)
    y_mid = plot_top + plot_h / 2
    cap_w = plot_h
    cap_h = 0.3
    tb = add_textbox(slide, chart_left - cap_w / 2 + cap_h / 2 - 0.05,
                     y_mid - cap_h / 2, cap_w, cap_h)
    tb.rotation = -90
    write_paragraph(tb.text_frame, f"금액 ({unit})", theme=theme,
                    size=T.sub_header_size, bold=True, color=P.gray_1,
                    align=PP_ALIGN.CENTER)

    # ── Legend strip (top of plot) — revenue / total cost / fixed cost ──
    leg_y = chart_top - 0.3
    lx = plot_left
    swatch_w = 0.32
    gap = 0.14

    def chip(color, label, dashed):
        nonlocal lx
        cy = leg_y + 0.12
        if dashed:
            _dashed_line(slide, lx, cy, lx + swatch_w, cy, color,
                         thickness_pt=2.0, dash=0.06, gap=0.05)
        else:
            add_line(slide, lx, cy, lx + swatch_w, cy, color, thickness_pt=3.0)
        tb = add_textbox(slide, lx + swatch_w + 0.06, leg_y, 1.3, 0.26)
        write_paragraph(tb.text_frame, label, theme=theme,
                        size=T.small_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.LEFT)
        lx += swatch_w + 0.06 + len(label) * 0.16 + gap

    chip(P.positive, "매출선", False)
    chip(P.negative, "총비용선", False)
    if show_fixed:
        chip(P.gray_3, "고정비", True)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (self-contained; mirrors fpna_charts pattern) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("breakeven",
          _S("fixed_cost", required=True),
          _S("unit_price", required=True),
          _S("unit_var_cost", required=True),
          _S("max_volume", required=True),
          _S("unit", type=str),
          _S("vol_unit", type=str),
          _S("show_fixed"),
          _S("ticks"),
          example={"title": "손익분기 분석", "fixed_cost": 4000,
                   "unit_price": 50, "unit_var_cost": 30, "max_volume": 400,
                   "unit": "만원", "vol_unit": "개"})
