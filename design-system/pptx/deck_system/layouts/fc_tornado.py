"""Tornado (sensitivity) chart — PPTX renderer (mirror of mck/assets/tornado.js).

Horizontal diverging bars for sensitivity analysis. One row per driver, sorted
by swing magnitude (largest at top) → the funnel/"tornado". Each bar spans
[min(low,high) … max(low,high)] across a vertical base reference line; the
portion below base = P.negative, above base = P.positive (split into two rects).

Pattern mirrors fpna_charts.bullet: @register + inches geometry off theme.layout
+ add_action_title/source/page + bottom _baseline schema registration.
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}{unit}"


# ────────────────────────────────────────────────────────────────────
# TORNADO — items: [{label, low, high}], base, unit
# diverging sensitivity bars; sorted by swing |high-low| desc.
# ────────────────────────────────────────────────────────────────────
@register("tornado")
def tornado(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = list(spec.get("items", []))
    if not items:
        raise ValueError("[tornado] need at least 1 item")
    unit = spec.get("unit", "")
    base = float(spec.get("base", 0))

    # Sort by swing magnitude (largest at top) → funnel shape
    def _swing(it):
        return abs(float(it.get("high", 0)) - float(it.get("low", 0)))
    items.sort(key=_swing, reverse=True)

    # Shared x-scale: span every endpoint + base, padded
    lo = base
    hi = base
    for it in items:
        lo = min(lo, float(it.get("low", 0)), float(it.get("high", 0)))
        hi = max(hi, float(it.get("low", 0)), float(it.get("high", 0)))
    span = (hi - lo) or 1.0
    pad = span * 0.08
    x_min = lo - pad
    x_max = hi + pad

    # Geometry (inches) — mirror bullet pattern
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.2
    chart_w = L.content_width_in
    chart_h = 4.3
    label_w = 2.2
    value_w = 0.7  # breathing room for end labels on the right
    plot_left = chart_left + label_w
    plot_w = chart_w - label_w - value_w
    rows = len(items)
    row_h = chart_h / rows

    def x_for(v):
        return plot_left + ((v - x_min) / (x_max - x_min)) * plot_w

    base_x = x_for(base)

    # Base-case vertical reference line — dashed approximation via stacked
    # short rects (dash 0.08in, gap 0.06in). Thin vertical rect = line.
    line_thick = 0.022
    line_top = chart_top - 0.1
    line_bottom = chart_top + chart_h + 0.05
    dash_h, gap_h = 0.08, 0.06
    yy = line_top
    while yy < line_bottom:
        seg = min(dash_h, line_bottom - yy)
        add_rect(slide, base_x - line_thick / 2, yy, line_thick, seg, P.gray_2)
        yy += dash_h + gap_h

    # Base callout (top, anchored over the base line)
    callout_w = 1.6
    tb = add_textbox_safe(slide, base_x - callout_w / 2, line_top - 0.34,
                          callout_w, 0.3)
    write_paragraph(tb.text_frame, f"Base {_fmt(base, unit)}", theme=theme,
                    size=T.small_size, bold=True, color=P.gray_1,
                    align=PP_ALIGN.CENTER)

    for i, it in enumerate(items):
        low = float(it.get("low", 0))
        high = float(it.get("high", 0))
        y_mid = chart_top + i * row_h + row_h / 2
        bar_h = min(0.46, row_h * 0.6)
        bar_y = y_mid - bar_h / 2

        l_end = min(low, high)   # left endpoint (value-min)
        r_end = max(low, high)   # right endpoint (value-max)
        x_l = x_for(l_end)
        x_r = x_for(r_end)

        # Diverging bar — split at base: negative (below) / positive (above)
        if l_end < base:
            x0 = x_l
            x1 = min(base_x, x_r)
            w = x1 - x0
            if w > 0.001:
                add_rect(slide, x0, bar_y, w, bar_h, P.negative)
        if r_end > base:
            x0 = max(base_x, x_l)
            x1 = x_r
            w = x1 - x0
            if w > 0.001:
                add_rect(slide, x0, bar_y, w, bar_h, P.positive)

        # Driver label (left, right-aligned)
        tb = add_textbox_safe(slide, chart_left, y_mid - 0.18,
                              label_w - 0.15, 0.36)
        write_paragraph(tb.text_frame, str(it.get("label", "")), theme=theme,
                        size=T.body_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.RIGHT)

        # Endpoint value labels — low at its end, high at its end
        lo_is_left = low <= high
        low_x = x_l if lo_is_left else x_r
        high_x = x_r if lo_is_left else x_l

        # low label — outside the lower end
        lab_w = 0.7
        tb = add_textbox_safe(slide, low_x - lab_w - 0.1, y_mid - 0.13,
                              lab_w, 0.26)
        write_paragraph(tb.text_frame, _fmt(low, unit), theme=theme,
                        size=T.small_size - 2, bold=True, color=P.gray_1,
                        align=PP_ALIGN.RIGHT)
        # high label — outside the upper end
        tb = add_textbox_safe(slide, high_x + 0.1, y_mid - 0.13, lab_w, 0.26)
        write_paragraph(tb.text_frame, _fmt(high, unit), theme=theme,
                        size=T.small_size - 2, bold=True, color=P.gray_1,
                        align=PP_ALIGN.LEFT)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


def add_textbox_safe(slide, x, y, w, h):
    """Wrap add_textbox, clamping x ≥ 0 so off-slide labels don't error."""
    from deck_system.helpers.shapes import add_textbox
    return add_textbox(slide, max(0.0, x), y, w, h)


# ── schema registration (self-contained; mirrors fpna_charts pattern) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("tornado",
          _S("items", required=True, type=list, min_length=1),
          _S("base"),
          _S("unit", type=str),
          example={"title": "민감도 분석", "base": 200, "unit": "억",
                   "items": [
                       {"label": "물동량 ±10%", "low": 158, "high": 246},
                       {"label": "인건비 ±8%", "low": 176, "high": 224}]})
