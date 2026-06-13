"""Bar/column/line chart layouts — historic+forecast, simple growth,
line, stacked column, grouped column.  All use native python-pptx charts
so they're editable in PowerPoint (not stacked rectangles).

Reference: seulee26 (column_historic_forecast, column_simple_growth),
           likaku (line_chart, stacked_column, grouped_column).
"""
from __future__ import annotations
from typing import Optional

from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import set_run, write_paragraph, set_ea_font
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)
from deck_system.tokens.base import hex_to_rgb


def _chart_geom(layout):
    """Standard 1-chart-fills-content area.  Returns (x, y, w, h) in inches."""
    L = layout
    x = L.margin_left_in
    y = L.content_top_in + 0.2
    w = L.content_width_in
    h = L.bottom_bar_y_in - y - 0.3
    return x, y, w, h


def _style_chart_axes(chart, theme):
    """Apply theme colors + Pretendard EA to all chart text + thin axis lines."""
    P = theme.palette
    T = theme.typography
    for axis in (chart.category_axis, chart.value_axis):
        try:
            axis.tick_labels.font.size = Pt(T.chart_label_size)
            axis.tick_labels.font.color.rgb = hex_to_rgb(P.gray_2)
            axis.tick_labels.font.name = T.family_en
            # EA font for any Korean axis labels
            tl = axis.tick_labels
            for txAttr in ("_txPr", "_txBody"):
                pass  # python-pptx 0.6.x doesn't expose tick-label runs cleanly
        except Exception:
            pass


@register("column_historic_forecast")
def column_historic_forecast(slide, spec, theme, *, page_num, total):
    """Historic vs forecast columns.  Past = primary, future = lighter accent.

    spec:
        title, categories: [yr,…], values: [v,…],
        forecast_from_index: int,  unit: "",
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    cats = spec.get("categories", [])
    vals = [float(v) for v in spec.get("values", [])]
    fi = int(spec.get("forecast_from_index", len(vals)))

    cd = CategoryChartData()
    cd.categories = [str(c) for c in cats]
    cd.add_series("Historic", [v if i < fi else None for i, v in enumerate(vals)])
    cd.add_series("Forecast", [v if i >= fi else None for i, v in enumerate(vals)])

    x, y, w, h = _chart_geom(L)
    gf = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd,
    )
    chart = gf.chart
    chart.has_legend = False
    plot = chart.plots[0]
    plot.gap_width = 60

    # Historic bars = primary, forecast = accent (lighter via fill alpha not avail in pptx)
    series = chart.series
    for s, col in zip(series, (P.surface_inverse, P.accent)):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = hex_to_rgb(col)
        s.format.line.fill.background()
        # Value labels on top
        s.data_labels.show_value = True
        s.data_labels.font.size = Pt(T.chart_label_size)
        s.data_labels.font.color.rgb = hex_to_rgb(P.gray_1)
        s.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END

    _style_chart_axes(chart, theme)

    # Manual legend (color swatch + label, since native legend chrome is fiddly)
    legend_y = y - 0.05
    add_rect(slide, x, legend_y - 0.05, 0.18, 0.18, P.surface_inverse)
    tb = add_textbox(slide, x + 0.25, legend_y - 0.08, 1.5, 0.25)
    write_paragraph(tb.text_frame, "Historic", theme=theme,
                    size=T.chart_label_size, color=P.gray_2)
    add_rect(slide, x + 1.6, legend_y - 0.05, 0.18, 0.18, P.accent)
    tb = add_textbox(slide, x + 1.85, legend_y - 0.08, 1.5, 0.25)
    write_paragraph(tb.text_frame, "Forecast", theme=theme,
                    size=T.chart_label_size, color=P.gray_2)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("column_simple_growth")
def column_simple_growth(slide, spec, theme, *, page_num, total):
    """Single-series growth columns with delta arrows.

    spec: categories, values, unit, source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    cats = spec.get("categories", [])
    vals = [float(v) for v in spec.get("values", [])]

    cd = CategoryChartData()
    cd.categories = [str(c) for c in cats]
    cd.add_series("Value", vals)

    x, y, w, h = _chart_geom(L)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd,
    ).chart
    chart.has_legend = False
    chart.plots[0].gap_width = 80
    s = chart.series[0]
    s.format.fill.solid()
    s.format.fill.fore_color.rgb = hex_to_rgb(P.surface_inverse)
    s.format.line.fill.background()
    s.data_labels.show_value = True
    s.data_labels.font.size = Pt(T.chart_label_size + 1)
    s.data_labels.font.color.rgb = hex_to_rgb(P.gray_1)
    s.data_labels.font.bold = True
    s.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    _style_chart_axes(chart, theme)

    # CAGR callout (if 2+ values)
    if len(vals) >= 2 and vals[0] > 0:
        cagr = ((vals[-1] / vals[0]) ** (1 / (len(vals) - 1)) - 1) * 100
        sign = "+" if cagr >= 0 else "\u2212"
        color = P.positive if cagr >= 0 else P.negative
        tb = add_textbox(slide, x + w - 2.4, y - 0.05, 2.4, 0.3)
        write_paragraph(tb.text_frame,
                        f"CAGR {sign}{abs(cagr):.1f}%", theme=theme,
                        size=T.body_size, bold=True, color=color,
                        align=PP_ALIGN.RIGHT)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("line_chart")
def line_chart(slide, spec, theme, *, page_num, total):
    """Multi-series line chart.

    spec: categories, series: [{label, values, color?}], source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    cats = spec.get("categories", [])
    series_data = spec.get("series", [])

    cd = CategoryChartData()
    cd.categories = [str(c) for c in cats]
    for sd in series_data:
        cd.add_series(sd["label"], [float(v) for v in sd["values"]])

    x, y, w, h = _chart_geom(L)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), cd,
    ).chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(T.chart_label_size)
    chart.legend.font.color.rgb = hex_to_rgb(P.gray_2)

    palette_order = [P.surface_inverse, P.accent, P.gray_2, P.positive, P.negative]
    for i, (s, sd) in enumerate(zip(chart.series, series_data)):
        col = sd.get("color")
        if col and not col.startswith("#"):
            col = getattr(P, col.replace("-", "_"), None)
        if not col:
            col = palette_order[i % len(palette_order)]
        s.format.line.color.rgb = hex_to_rgb(col)
        s.format.line.width = Pt(2.25)
        # Marker
        try:
            s.marker.style = 8  # circle
            s.marker.size = 6
            s.marker.format.fill.solid()
            s.marker.format.fill.fore_color.rgb = hex_to_rgb(col)
            s.marker.format.line.fill.background()
        except Exception:
            pass
    _style_chart_axes(chart, theme)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("stacked_column")
def stacked_column(slide, spec, theme, *, page_num, total):
    """Stacked-column chart for part-of-whole over time.

    spec: categories, series: [{label, values, color?}], source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    cats = spec.get("categories", [])
    series_data = spec.get("series", [])

    cd = CategoryChartData()
    cd.categories = [str(c) for c in cats]
    for sd in series_data:
        cd.add_series(sd["label"], [float(v) for v in sd["values"]])

    x, y, w, h = _chart_geom(L)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_STACKED, Inches(x), Inches(y), Inches(w), Inches(h), cd,
    ).chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(T.chart_label_size)
    chart.plots[0].gap_width = 70

    palette_order = [P.surface_inverse, P.accent, P.gray_2, P.gray_3, P.positive]
    for i, (s, sd) in enumerate(zip(chart.series, series_data)):
        col = sd.get("color")
        if col and not col.startswith("#"):
            col = getattr(P, col.replace("-", "_"), None)
        if not col:
            col = palette_order[i % len(palette_order)]
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = hex_to_rgb(col)
        s.format.line.fill.background()
    _style_chart_axes(chart, theme)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("grouped_column")
def grouped_column(slide, spec, theme, *, page_num, total):
    """Grouped/clustered column chart — multiple series side by side.

    spec: categories, series: [{label, values, color?}], source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    cats = spec.get("categories", [])
    series_data = spec.get("series", [])

    cd = CategoryChartData()
    cd.categories = [str(c) for c in cats]
    for sd in series_data:
        cd.add_series(sd["label"], [float(v) for v in sd["values"]])

    x, y, w, h = _chart_geom(L)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd,
    ).chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(T.chart_label_size)
    chart.plots[0].gap_width = 80

    palette_order = [P.surface_inverse, P.accent, P.gray_2, P.positive, P.negative]
    for i, (s, sd) in enumerate(zip(chart.series, series_data)):
        col = sd.get("color")
        if col and not col.startswith("#"):
            col = getattr(P, col.replace("-", "_"), None)
        if not col:
            col = palette_order[i % len(palette_order)]
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = hex_to_rgb(col)
        s.format.line.fill.background()
    _style_chart_axes(chart, theme)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
