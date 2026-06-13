"""Scatter (correlation) chart — PPTX renderer (mirror of mck/assets/scatter.js).

X–Y scatter plot for two-variable correlation (e.g. throughput × unit cost).
Points (ovals) + optional least-squares trend line. X/Y axis lines (add_hline +
thin vertical rect) with tick marks, tick labels, and axis captions.

Pattern mirrors fpna_charts.bullet / fc_tornado: @register + inches geometry off
theme.layout + add_action_title/source/page + bottom _baseline schema. Linear
regression computed in pure python (no numpy) — sum-based OLS.
"""
from __future__ import annotations

import math

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_oval, add_line, add_hline, add_rect, add_textbox
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if isinstance(v, float):
        # trim trailing noise on nice-step values
        v = round(v, 6)
        if float(v).is_integer():
            v = int(v)
    return f"{v:,}{unit}"


def _linear_regression(points):
    """Ordinary least-squares simple linear regression (pure python).

    Returns (slope, intercept) for y = slope·x + intercept.
    Degenerate input (n < 2 or zero x-variance) → slope 0 through the mean.
    """
    n = len(points)
    if n < 2:
        return 0.0, (points[0][1] if n == 1 else 0.0)
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    sxx = sum(p[0] * p[0] for p in points)
    sxy = sum(p[0] * p[1] for p in points)
    denom = n * sxx - sx * sx
    if denom == 0:
        return 0.0, sy / n
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    return slope, intercept


def _nice_scale(lo, hi, count):
    """"Nice" axis bounds + tick list for [lo,hi] targeting ~count ticks."""
    span = (hi - lo) or 1.0
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
    nice_min = math.floor(lo / step) * step
    nice_max = math.ceil(hi / step) * step
    ticks = []
    v = nice_min
    # guard against runaway loops on pathological input
    while v <= nice_max + step * 1e-6 and len(ticks) < 200:
        ticks.append(round(v, 6))
        v += step
    return nice_min, nice_max, ticks


# ────────────────────────────────────────────────────────────────────
# SCATTER — points: [{x, y, label?}], x_label, y_label, trend, x_unit, y_unit
# X–Y correlation scatter + optional least-squares trend line.
# ────────────────────────────────────────────────────────────────────
@register("scatter")
def scatter(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    raw = spec.get("points", [])
    points = [p for p in raw if p and p.get("x") is not None and p.get("y") is not None]
    if not points:
        raise ValueError("[scatter] need at least 1 point")

    x_label = spec.get("x_label", "")
    y_label = spec.get("y_label", "")
    x_unit = spec.get("x_unit", "")
    y_unit = spec.get("y_unit", "")
    tick_count = int(spec.get("ticks", 5))
    show_trend = spec.get("trend") is True

    xs = [float(p["x"]) for p in points]
    ys = [float(p["y"]) for p in points]
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)
    x_pad = ((x_hi - x_lo) or 1.0) * 0.08
    y_pad = ((y_hi - y_lo) or 1.0) * 0.08
    x_min, x_max, x_ticks = _nice_scale(x_lo - x_pad, x_hi + x_pad, tick_count)
    y_min, y_max, y_ticks = _nice_scale(y_lo - y_pad, y_hi + y_pad, tick_count)
    x_span = (x_max - x_min) or 1.0
    y_span = (y_max - y_min) or 1.0

    # ── Plot geometry (inches) — mirror bullet/tornado pattern ──
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.2
    chart_w = L.content_width_in
    chart_h = 4.5
    pad_l = 1.1   # room for y tick labels + y caption
    pad_b = 0.7   # room for x tick labels + x caption
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

    axis_thick = 1.5

    # ── Y-axis gridlines + ticks + labels ──
    for t in y_ticks:
        ty = y_for(t)
        # faint gridline across plot
        add_hline(slide, plot_left, ty, plot_w, P.gray_4, thickness_pt=0.75)
        # tick mark (short outward stub)
        add_hline(slide, plot_left - 0.06, ty, 0.06, P.gray_3, thickness_pt=1.2)
        tb = add_textbox(slide, chart_left, ty - 0.12, pad_l - 0.18, 0.24)
        write_paragraph(tb.text_frame, _fmt(t, y_unit), theme=theme,
                        size=T.small_size, color=P.gray_2, align=PP_ALIGN.RIGHT)

    # ── X-axis ticks + labels ──
    for t in x_ticks:
        tx = x_for(t)
        _vline(slide, tx, plot_bottom, 0.06, P.gray_3, thickness=0.017)
        tb = add_textbox(slide, tx - 0.6, plot_bottom + 0.1, 1.2, 0.24)
        write_paragraph(tb.text_frame, _fmt(t, x_unit), theme=theme,
                        size=T.small_size, color=P.gray_2, align=PP_ALIGN.CENTER)

    # ── Axis lines (X baseline + Y left) ──
    add_hline(slide, plot_left, plot_bottom, plot_w, P.gray_3, thickness_pt=2)
    _vline(slide, plot_left, plot_top, plot_h, P.gray_3, thickness=0.028)

    # ── Trend line (least-squares regression), clipped to y-domain ──
    if show_trend and len(points) >= 2:
        slope, intercept = _linear_regression([(float(p["x"]), float(p["y"]))
                                               for p in points])

        def y_at(x):
            return slope * x + intercept

        ax, ay = x_min, y_at(x_min)
        bx, by = x_max, y_at(x_max)

        def clip_end(px, py, qx, qy):
            x, y = px, py
            if y < y_min or y > y_max:
                target = y_min if y < y_min else y_max
                if qy != py:
                    t = (target - py) / (qy - py)
                    x = px + t * (qx - px)
                    y = target
            return x, y

        if slope != 0:
            ax, ay = clip_end(ax, ay, bx, by)
            bx, by = clip_end(bx, by, ax, ay)

        add_line(slide, x_for(ax), y_for(ay), x_for(bx), y_for(by),
                 P.accent, thickness_pt=2.5)

    # ── Data points (drawn last so they sit above grid + trend) ──
    dot = 0.14   # diameter (inches)
    for p in points:
        cx = x_for(float(p["x"]))
        cy = y_for(float(p["y"]))
        add_oval(slide, cx - dot / 2, cy - dot / 2, dot, dot, P.primary)
        lab = p.get("label")
        if lab:
            tb = add_textbox(slide, cx - 0.7, cy - 0.36, 1.4, 0.24)
            write_paragraph(tb.text_frame, str(lab), theme=theme,
                            size=T.small_size - 2, bold=True, color=P.gray_1,
                            align=PP_ALIGN.CENTER)

    # ── Axis captions ──
    if x_label:
        tb = add_textbox(slide, plot_left, chart_top + chart_h + 0.04,
                         plot_w, 0.3)
        write_paragraph(tb.text_frame, x_label, theme=theme,
                        size=T.sub_header_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.CENTER)
    if y_label:
        # vertical caption — rotated textbox centered on y-axis midpoint
        y_mid = plot_top + plot_h / 2
        cap_w = plot_h           # length runs along the axis after rotation
        cap_h = 0.3
        tb = add_textbox(slide, chart_left - cap_w / 2 + cap_h / 2 - 0.05,
                         y_mid - cap_h / 2, cap_w, cap_h)
        tb.rotation = -90
        write_paragraph(tb.text_frame, y_label, theme=theme,
                        size=T.sub_header_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.CENTER)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


def _vline(slide, x, y, length, color_hex, *, thickness=0.022):
    """Thin vertical rule via a narrow filled rect (no connector)."""
    return add_rect(slide, x - thickness / 2, y, thickness, length, color_hex)


# ── schema registration (self-contained; mirrors fpna_charts pattern) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("scatter",
          _S("points", required=True, type=list, min_length=1),
          _S("x_label", type=str),
          _S("y_label", type=str),
          _S("trend"),
          _S("x_unit", type=str),
          _S("y_unit", type=str),
          example={"title": "물량-원가 상관", "x_label": "처리물량(천건)",
                   "y_label": "건당원가(원)", "trend": True,
                   "points": [{"x": 120, "y": 840}, {"x": 240, "y": 660},
                              {"x": 360, "y": 560}, {"x": 480, "y": 505}]})
