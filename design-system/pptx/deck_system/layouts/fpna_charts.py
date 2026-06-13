"""FP&A handoff charts — PPTX renderers (mirror of mck/assets/*.js).

One @register per chart. Colors via theme.palette tokens (never hardcoded hex).
Diagonals via helpers.shapes.add_line/add_polyline (rotated rect, NOT connector).

Pilot: bullet. The remaining 11 are appended by parallel workers following this
exact pattern (geometry in inches off theme.layout, add_action_title/source/page).
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_line, add_polyline
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}{unit}"


# ────────────────────────────────────────────────────────────────────
# BULLET — items: [{label, measure, target?, ranges?, unit?}]
# actual-vs-target-vs-qualitative-bands. Per-row scale (KPIs differ in unit).
# ────────────────────────────────────────────────────────────────────
@register("bullet")
def bullet(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = spec.get("items", [])
    if not items:
        raise ValueError("[bullet] need at least 1 item")
    g_unit = spec.get("unit", "")

    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.2
    chart_w = L.content_width_in
    chart_h = 4.3
    label_w, value_w = 2.2, 1.3
    plot_left = chart_left + label_w
    plot_w = chart_w - label_w - value_w
    rows = len(items)
    row_h = chart_h / rows

    for i, it in enumerate(items):
        unit = it.get("unit", g_unit)
        measure = float(it.get("measure", 0))
        target = it.get("target")
        ranges = sorted(float(r) for r in (it.get("ranges") or []))
        candidates = [measure] + ([float(target)] if target is not None else []) + ranges
        row_max = (max(candidates) * 1.05) or 1.0
        y_mid = chart_top + i * row_h + row_h / 2
        band_h = min(0.46, row_h * 0.66)
        band_y = y_mid - band_h / 2
        meas_h = band_h * 0.34
        meas_y = y_mid - meas_h / 2

        def x_for(v, _rm=row_max):
            return plot_left + (max(0.0, v) / _rm) * plot_w

        prev = 0.0
        for ri, r in enumerate(ranges):
            x0, x1 = x_for(prev), x_for(r)
            if x1 - x0 > 0.001:
                add_rect(slide, x0, band_y, x1 - x0, band_h,
                         P.gray_3 if ri == 0 else P.gray_4)
            prev = r

        mw = max(0.03, x_for(measure) - plot_left)
        add_rect(slide, plot_left, meas_y, mw, meas_h, P.surface_inverse)

        if target is not None:
            tx = x_for(float(target))
            add_rect(slide, tx - 0.02, band_y - 0.05, 0.04, band_h + 0.1, P.accent)

        tb = add_textbox(slide, chart_left, y_mid - 0.18, label_w - 0.15, 0.36)
        write_paragraph(tb.text_frame, str(it.get("label", "")), theme=theme,
                        size=T.body_size, bold=True, color=P.gray_1, align=PP_ALIGN.RIGHT)

        tb = add_textbox(slide, plot_left + plot_w + 0.1, y_mid - 0.22, value_w - 0.1, 0.3)
        write_paragraph(tb.text_frame, _fmt(measure, unit), theme=theme,
                        size=T.body_size, bold=True, color=P.gray_1, align=PP_ALIGN.LEFT)
        if target is not None:
            delta = measure - float(target)
            dcolor = P.positive if delta >= 0 else P.negative
            arrow = "▲ " if delta >= 0 else "▼ "
            tb = add_textbox(slide, plot_left + plot_w + 0.1, y_mid + 0.06, value_w - 0.1, 0.25)
            write_paragraph(tb.text_frame, arrow + _fmt(abs(delta)), theme=theme,
                            size=T.small_size - 2, bold=True, color=dcolor, align=PP_ALIGN.LEFT)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (kept here so each chart is self-contained; avoids
#    editing validation.py and lets parallel workers add charts conflict-free) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("bullet",
          _S("items", required=True, type=list, min_length=1),
          _S("unit", type=str),
          example={"title": "FY26 KPI", "items": [
              {"label": "매출", "measure": 1430, "target": 1200,
               "ranges": [800, 1100, 1500], "unit": "억"}]})
