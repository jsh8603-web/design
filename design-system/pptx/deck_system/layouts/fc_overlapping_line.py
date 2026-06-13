"""Overlapping line (seasonality / YoY) chart — PPTX renderer
(mirror of mck/assets/overlapping-line.js).

Fixed X-axis of months (1–12) with one line per year, all overlaid on a single
shared Y scale so the eye reads the recurring seasonal shape and the
year-over-year level shift in one pass. Older year → newer year reads faint →
bold (gray_3 → gray_2 → primary) so the most recent year pops; older lines are
drawn first so the emphasized recent line sits on top.

Geometry mirrors fc_combo: @register + inches off theme.layout +
add_action_title/source/page + bottom _baseline schema. Each year line is drawn
by converting its data points to inches and calling add_polyline (thin rotated
rects, NOT connectors); markers via add_oval; Y ticks via add_hline gridlines.
"""
from __future__ import annotations

import math

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import (
    add_oval, add_polyline, add_hline, add_textbox,
)
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}{unit}"


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


def _ramp_color(P, idx: int, total: int) -> str:
    """Default recency ramp: last = primary (boldest), then gray_2, then gray_3."""
    if idx == total - 1:
        return P.primary
    if idx == total - 2:
        return P.gray_2
    return P.gray_3


# ────────────────────────────────────────────────────────────────────
# OVERLAPPING_LINE — months:[...], series:[{year, values[]}], unit
# seasonality / YoY: fixed month X-axis, one line per year, shared Y scale,
# faint older → bold recent (gray_3 → gray_2 → primary).
# ────────────────────────────────────────────────────────────────────
@register("overlapping_line")
def overlapping_line(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    months = list(spec.get("months", []))
    series = spec.get("series", []) or []
    unit = spec.get("unit", "")

    if len(months) < 1:
        raise ValueError("[overlapping_line] need at least 1 month")
    if len(series) < 1:
        raise ValueError("[overlapping_line] need at least 1 year series")
    for s in series:
        vals = s.get("values") or []
        if len(vals) != len(months):
            raise ValueError(
                f"[overlapping_line] series \"{s.get('year', '')}\" values must "
                f"match months length ({len(months)})"
            )

    # ── Shared Y-scale across every year (one common axis) ──────────────
    all_vals = [float(v) for s in series for v in (s.get("values") or [])]
    y_max = _nice_ceil(max(all_vals) * 1.05) if all_vals else 1.0

    # ── Geometry (inches) — mirror fc_combo, single left axis gutter ────
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.45    # room for legend above plot
    chart_h = 3.9
    axis_w = 0.85                          # left tick-label gutter
    end_label_w = 0.7                      # right gutter for end-of-line year labels
    plot_left = chart_left + axis_w
    plot_w = L.content_width_in - axis_w - end_label_w
    plot_top = chart_top
    plot_bottom = chart_top + chart_h

    n = len(months)

    def x_for(i):
        if n == 1:
            return plot_left + plot_w / 2
        return plot_left + (plot_w / (n - 1)) * i

    def y_for(v):
        return plot_bottom - (max(0.0, v) / y_max) * chart_h

    TICKS = 4

    # ── 1. Gridlines + Y-axis ticks (shared scale) ──────────────────────
    for t in range(TICKS + 1):
        v = (y_max / TICKS) * t
        y = y_for(v)
        add_hline(slide, plot_left, y, plot_w, P.gray_4, thickness_pt=0.75)
        tb = add_textbox(slide, chart_left - 0.05, y - 0.12, axis_w - 0.1, 0.24)
        write_paragraph(tb.text_frame, _fmt(round(v), unit), theme=theme,
                        size=T.chart_label_size, color=P.gray_2,
                        align=PP_ALIGN.RIGHT)

    # ── 2. Year lines (faint older → bold recent) + markers + end label ─
    # Draw older years first so the emphasized recent line sits on top.
    n_series = len(series)
    for si, s in enumerate(series):
        color = s.get("color") or _ramp_color(P, si, n_series)
        is_recent = si == n_series - 1
        sw = 4.0 if is_recent else 2.5
        vals = [float(v) for v in (s.get("values") or [])]
        pts = [(x_for(i), y_for(v)) for i, v in enumerate(vals)]
        add_polyline(slide, pts, color, thickness_pt=sw)
        mk = 0.14 if is_recent else 0.10
        for (cx, cy) in pts:
            add_oval(slide, cx - mk / 2, cy - mk / 2, mk, mk, color)
        # end-of-line year label (right edge) — reinforces recency ramp
        last_x, last_y = pts[-1]
        tb = add_textbox(slide, last_x + 0.1, last_y - 0.13, end_label_w - 0.05, 0.26)
        write_paragraph(tb.text_frame, str(s.get("year", "")), theme=theme,
                        size=T.small_size, bold=True, color=color,
                        align=PP_ALIGN.LEFT)

    # ── 3. X-axis month labels ──────────────────────────────────────────
    for i, m in enumerate(months):
        cx = x_for(i)
        tb = add_textbox(slide, cx - 0.5, plot_bottom + 0.08, 1.0, 0.28)
        write_paragraph(tb.text_frame, f"{m}월", theme=theme,
                        size=T.body_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.CENTER)

    # ── 4. Legend (top) — one chip per year, faint → bold ───────────────
    legend_y = L.content_top_in + 0.05
    chip = 0.18
    lx = plot_left
    for si, s in enumerate(series):
        color = s.get("color") or _ramp_color(P, si, n_series)
        is_recent = si == n_series - 1
        add_hline(slide, lx, legend_y + chip / 2, 0.34, color,
                  thickness_pt=4.0 if is_recent else 2.5)
        mk = 0.14 if is_recent else 0.10
        add_oval(slide, lx + 0.17 - mk / 2, legend_y + chip / 2 - mk / 2,
                 mk, mk, color)
        label = f"{s.get('year', '')}년"
        tb = add_textbox(slide, lx + 0.44, legend_y - 0.04, 1.6, 0.26)
        write_paragraph(tb.text_frame, label, theme=theme,
                        size=T.small_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.LEFT)
        # advance: swatch (0.44) + label width (CJK-aware) + gap
        lx += 0.44 + 0.16 * len(label) + 0.4

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (self-contained; mirrors fpna_charts/fc_combo) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("overlapping_line",
          _S("months", required=True, type=list, min_length=1),
          _S("series", required=True, type=list, min_length=1),
          _S("unit", type=str),
          example={"title": "월별 계절성 (전년 대비)",
                   "months": ["1", "2", "3", "4", "5", "6",
                              "7", "8", "9", "10", "11", "12"],
                   "unit": "억",
                   "series": [
                       {"year": "2023",
                        "values": [80, 75, 90, 95, 88, 92,
                                   98, 110, 105, 120, 140, 165]},
                       {"year": "2024",
                        "values": [88, 82, 98, 103, 96, 101,
                                   108, 121, 116, 132, 154, 182]},
                       {"year": "2025",
                        "values": [95, 90, 107, 112, 105, 110,
                                   118, 132, 127, 144, 168, 198]}]})
