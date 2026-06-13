"""Combo (dual-axis) chart — PPTX renderer (mirror of mck/assets/combo.js).

Left-Y bars (absolute scale, P.surface_inverse) + right-Y line with markers
(ratio scale, P.accent). Shared X categories. The two Y axes are normalized
independently (each by its own max with 5% headroom + a "nice" ceiling) — the
FP&A default for showing a volume series and a margin/rate series on one slide.

Geometry mirrors fpna_charts.bullet / fc_tornado: @register + inches off
theme.layout + add_action_title/source/page + bottom _baseline schema. The
line is drawn by converting each data point to inches and calling add_polyline
(thin rotated rects, NOT connectors), with add_oval markers per point.
"""
from __future__ import annotations

import math

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import (
    add_rect, add_oval, add_polyline, add_hline, add_textbox,
)
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}{unit}"


def _fmt_ratio(v, unit: str = "") -> str:
    """Right-axis / line labels — one decimal place (ratio series)."""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
        return f"{v}{unit}"
    return f"{v:.1f}{unit}"


def _nice_ceil(value: float) -> float:
    """Round an axis max up to a 'nice' value so ticks land on round numbers."""
    if not (value > 0):
        return 1.0
    exp = math.floor(math.log10(value))
    base = 10 ** exp
    frac = value / base
    if frac <= 1:
        nice = 1.0
    elif frac <= 2:
        nice = 2.0
    elif frac <= 2.5:
        nice = 2.5
    elif frac <= 5:
        nice = 5.0
    else:
        nice = 10.0
    return nice * base


# ────────────────────────────────────────────────────────────────────
# COMBO — categories, bars:{label,values,unit}, line:{label,values,unit}
# dual-axis: left-Y bars (absolute) + right-Y line+markers (ratio).
# Independent scales, each normalized by its own max.
# ────────────────────────────────────────────────────────────────────
@register("combo")
def combo(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    categories = list(spec.get("categories", []))
    bars = spec.get("bars", {}) or {}
    line = spec.get("line", {}) or {}
    bar_vals = [float(v) for v in (bars.get("values") or [])]
    line_vals = [float(v) for v in (line.get("values") or [])]

    if len(categories) < 1:
        raise ValueError("[combo] need at least 1 category")
    if len(bar_vals) != len(categories) or len(line_vals) != len(categories):
        raise ValueError(
            "[combo] bars.values and line.values must match categories length"
        )

    bar_unit = bars.get("unit", "")
    line_unit = line.get("unit", "")
    bar_label = bars.get("label", "막대")
    line_label = line.get("label", "선")

    # ── Independent scales (each by own max, 5% headroom, nice ceiling) ──
    bar_max = _nice_ceil(max(bar_vals) * 1.05) if bar_vals else 1.0
    line_max = _nice_ceil(max(line_vals) * 1.05) if line_vals else 1.0

    # ── Geometry (inches) — mirror bullet/tornado, leave both axis gutters ──
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.45   # room for legend above plot
    chart_h = 3.9
    axis_w = 0.85                          # left + right tick-label gutters
    plot_left = chart_left + axis_w
    plot_w = L.content_width_in - 2 * axis_w
    plot_top = chart_top
    plot_bottom = chart_top + chart_h

    n = len(categories)
    slot = plot_w / n
    bar_w = slot * 0.46

    def x_center(i):
        return plot_left + slot * i + slot / 2

    def y_bar(v):
        return plot_bottom - (max(0.0, v) / bar_max) * chart_h

    def y_line(v):
        return plot_bottom - (max(0.0, v) / line_max) * chart_h

    TICKS = 4

    # ── 1. Gridlines + left axis ticks (bar scale) ──────────────────────
    for t in range(TICKS + 1):
        v = (bar_max / TICKS) * t
        y = y_bar(v)
        add_hline(slide, plot_left, y, plot_w, P.gray_4, thickness_pt=0.75)
        tb = add_textbox(slide, chart_left - 0.05, y - 0.12, axis_w - 0.1, 0.24)
        write_paragraph(tb.text_frame, _fmt(round(v), bar_unit), theme=theme,
                        size=T.chart_label_size, color=P.gray_2,
                        align=PP_ALIGN.RIGHT)

    # ── 2. Right axis ticks (line scale) ────────────────────────────────
    for t in range(TICKS + 1):
        v = (line_max / TICKS) * t
        y = y_line(v)
        tb = add_textbox(slide, plot_left + plot_w + 0.1, y - 0.12,
                         axis_w - 0.1, 0.24)
        write_paragraph(tb.text_frame, _fmt_ratio(v, line_unit), theme=theme,
                        size=T.chart_label_size, color=P.gray_2,
                        align=PP_ALIGN.LEFT)

    # ── 3. Bars (left scale) ────────────────────────────────────────────
    for i, v in enumerate(bar_vals):
        x = x_center(i) - bar_w / 2
        y_top = y_bar(v)
        h = max(0.02, plot_bottom - y_top)
        add_rect(slide, x, y_top, bar_w, h, P.surface_inverse)

    # ── 4. Line (right scale) — polyline + markers ──────────────────────
    pts = [(x_center(i), y_line(v)) for i, v in enumerate(line_vals)]
    add_polyline(slide, pts, P.accent, thickness_pt=2.5)
    mk = 0.11  # marker diameter (inches)
    for (cx, cy) in pts:
        add_oval(slide, cx - mk / 2, cy - mk / 2, mk, mk, P.accent)

    # line value labels (below each marker)
    for i, v in enumerate(line_vals):
        cx, cy = pts[i]
        tb = add_textbox(slide, cx - 0.6, cy + 0.1, 1.2, 0.24)
        write_paragraph(tb.text_frame, _fmt_ratio(v, line_unit), theme=theme,
                        size=T.small_size - 2, bold=True, color=P.accent,
                        align=PP_ALIGN.CENTER)

    # ── 4b. Bar value labels (above bar top / above marker, no overlap) ──
    for i, v in enumerate(bar_vals):
        y_top = y_bar(v)
        marker_y = y_line(line_vals[i])
        label_y = min(y_top, marker_y) - 0.32
        cx = x_center(i)
        tb = add_textbox(slide, cx - 0.7, max(plot_top - 0.3, label_y), 1.4, 0.26)
        write_paragraph(tb.text_frame, _fmt(v, bar_unit), theme=theme,
                        size=T.small_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.CENTER)

    # ── 5. X-axis category labels ───────────────────────────────────────
    for i, c in enumerate(categories):
        cx = x_center(i)
        tb = add_textbox(slide, cx - slot / 2, plot_bottom + 0.08, slot, 0.28)
        write_paragraph(tb.text_frame, str(c), theme=theme,
                        size=T.body_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.CENTER)

    # ── 6. Legend (top) — bar swatch + line swatch ──────────────────────
    legend_y = L.content_top_in + 0.05
    chip = 0.18
    lx = plot_left
    # bar swatch + label
    add_rect(slide, lx, legend_y, chip, chip, P.surface_inverse)
    bar_leg = f"{bar_label}{f' ({bar_unit})' if bar_unit else ''}"
    tb = add_textbox(slide, lx + chip + 0.1, legend_y - 0.04, 2.6, 0.26)
    write_paragraph(tb.text_frame, bar_leg, theme=theme,
                    size=T.small_size, bold=True, color=P.gray_1,
                    align=PP_ALIGN.LEFT)
    # advance past bar label (approx width by char count, CJK-aware)
    bar_leg_w = 0.16 * len(bar_leg) + chip + 0.5
    lx += bar_leg_w
    # line swatch (short rule + marker) + label
    add_hline(slide, lx, legend_y + chip / 2, 0.34, P.accent, thickness_pt=2.5)
    add_oval(slide, lx + 0.17 - mk / 2, legend_y + chip / 2 - mk / 2,
             mk, mk, P.accent)
    line_leg = f"{line_label}{f' ({line_unit})' if line_unit else ''}"
    tb = add_textbox(slide, lx + 0.44, legend_y - 0.04, 2.8, 0.26)
    write_paragraph(tb.text_frame, line_leg, theme=theme,
                    size=T.small_size, bold=True, color=P.gray_1,
                    align=PP_ALIGN.LEFT)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (self-contained; mirrors fpna_charts pattern) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("combo",
          _S("categories", required=True, type=list, min_length=1),
          _S("bars", required=True),
          _S("line", required=True),
          example={"title": "매출 성장과 수익성",
                   "categories": ["Q1", "Q2", "Q3", "Q4"],
                   "bars": {"label": "매출",
                            "values": [1100, 1250, 1180, 1430], "unit": "억"},
                   "line": {"label": "영업이익률",
                            "values": [11.2, 13.4, 9.8, 14.3], "unit": "%"}})
