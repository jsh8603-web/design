"""V2.2 additions — 8 secondary layouts ported from likaku.

These fill gaps identified in audit/v2_drift_report.md §2.2 Medium tier:
- horizontal_bar    (#39) — category ranking w/ long labels
- metric_cards      (#10) — 3-4 light KPI cards (lighter than kpi_dashboard)
- stacked_area      (#70) — cumulative trends
- bubble            (#53) — 2-var + size scatter
- dashboard_kpi     (#57) — KPIs row + chart + takeaways
- dashboard_table   (#58) — table + chart + factoid cards
- numbered_list_panel (#69) — numbered recs + highlight panel
- gauge_pair        (variant) — paired gauges

All use surface_inverse for full-bleed; CJK routing via set_run().
"""
from __future__ import annotations
from typing import List, Optional

from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from deck_system.builder.registry import register
from deck_system.helpers.shapes import (
    add_rect, add_oval, add_textbox, add_hline, _clean_shape,
)
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)
from deck_system.tokens.base import hex_to_rgb


# ════════════════════════════════════════════════════════════════════
# HORIZONTAL_BAR (#39)
# ════════════════════════════════════════════════════════════════════

@register("horizontal_bar")
def horizontal_bar(slide, spec, theme, *, page_num, total):
    """Horizontal bar chart — best when category labels are long.

    spec:
        items: [{label, value, color?}, ...]  (sorted DESC by default)
        unit: "억" or "%"
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = sorted(spec.get("items", []), key=lambda x: -x.get("value", 0))[:10]
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    label_w = L.content_width_in * 0.30
    bar_w_max = L.content_width_in - label_w - 1.0  # leave room for value label
    row_h = body_h / max(len(items), 1)

    max_val = max((i.get("value", 0) for i in items), default=1) or 1
    unit = spec.get("unit", "")

    for i, item in enumerate(items):
        y = body_top + i * row_h + 0.05
        # Label
        tb = add_textbox(slide, L.margin_left_in, y + 0.05,
                          label_w - 0.15, row_h - 0.15)
        write_paragraph(tb.text_frame, item.get("label", ""), theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1,
                         align=PP_ALIGN.RIGHT)
        # Bar
        v = item.get("value", 0)
        bw = (v / max_val) * bar_w_max
        bar_color = item.get("color")
        if bar_color and not bar_color.startswith("#"):
            bar_color = getattr(P, bar_color.replace("-", "_"), P.surface_inverse)
        if not bar_color:
            bar_color = P.surface_inverse if i == 0 else P.accent if i == 1 else P.gray_2
        add_rect(slide, L.margin_left_in + label_w, y + 0.1,
                  max(bw, 0.05), row_h - 0.25, bar_color)
        # Value label at end of bar
        tb = add_textbox(slide, L.margin_left_in + label_w + bw + 0.1,
                          y + 0.05, 1.5, row_h - 0.15)
        write_paragraph(tb.text_frame, f"{v:,}{unit}", theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# METRIC_CARDS (#10) — 3-4 lighter KPI cards (compared to kpi_dashboard)
# ════════════════════════════════════════════════════════════════════

@register("metric_cards")
def metric_cards(slide, spec, theme, *, page_num, total):
    """3-4 lighter KPI cards w/ label + value + optional sub.

    Less dense than kpi_dashboard — uses ~60% slide height to leave
    room for narrative below.

    spec:
        cards: [{label, value, sub?, color?}, ...] (3-4)
        narrative: "..."  (optional text below cards)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    cards = spec.get("cards", [])[:4]
    n = max(len(cards), 1)
    body_top = L.content_top_in + 0.3
    card_h = 1.8
    gap = 0.2
    card_w = (L.content_width_in - gap * (n - 1)) / n

    for i, c in enumerate(cards):
        x = L.margin_left_in + i * (card_w + gap)
        col = c.get("color")
        if col and not col.startswith("#"):
            col = getattr(P, col.replace("-", "_"), P.surface_inverse)
        accent = col or (P.surface_inverse if i == 0 else P.accent if i == 1 else P.gray_2)
        # Left accent stripe
        add_rect(slide, x, body_top, 0.08, card_h, accent)
        # Card background
        add_rect(slide, x + 0.08, body_top, card_w - 0.08, card_h, P.gray_4)
        # Label
        tb = add_textbox(slide, x + 0.25, body_top + 0.2, card_w - 0.4, 0.35)
        write_paragraph(tb.text_frame, c.get("label", ""), theme=theme,
                         size=T.small_size, bold=True, color=P.gray_2)
        # Value
        tb = add_textbox(slide, x + 0.25, body_top + 0.55, card_w - 0.4, 0.9)
        write_paragraph(tb.text_frame, str(c.get("value", "")), theme=theme,
                         size=T.section_title_size, bold=True, color=accent)
        # Sub
        if c.get("sub"):
            tb = add_textbox(slide, x + 0.25, body_top + 1.4,
                              card_w - 0.4, 0.35)
            write_paragraph(tb.text_frame, c["sub"], theme=theme,
                             size=T.small_size - 1, color=P.gray_2)

    # Narrative panel
    if spec.get("narrative"):
        n_top = body_top + card_h + 0.4
        n_h = L.bottom_bar_y_in - n_top - 0.3
        tb = add_textbox(slide, L.margin_left_in, n_top,
                          L.content_width_in, n_h)
        write_paragraph(tb.text_frame, spec["narrative"], theme=theme,
                         size=T.body_size, color=P.gray_1, line_spacing=1.55)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# STACKED_AREA (#70) — Cumulative trends over time
# ════════════════════════════════════════════════════════════════════

@register("stacked_area")
def stacked_area(slide, spec, theme, *, page_num, total):
    """Stacked area chart.

    spec:
        categories: ["Q1","Q2",...]
        series: [{label, values, color?}, ...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    cats = spec.get("categories", [])
    series_data = spec.get("series", [])
    cd = CategoryChartData()
    cd.categories = [str(c) for c in cats]
    for sd in series_data:
        cd.add_series(sd["label"], [float(v) for v in sd["values"]])

    x_in = L.margin_left_in
    y_in = L.content_top_in + 0.3
    w_in = L.content_width_in
    h_in = L.bottom_bar_y_in - y_in - 0.4

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.AREA_STACKED, Inches(x_in), Inches(y_in),
        Inches(w_in), Inches(h_in), cd,
    ).chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(T.chart_label_size)
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

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# BUBBLE (#53) — x-y-size scatter (BCG variant)
# ════════════════════════════════════════════════════════════════════

@register("bubble")
def bubble(slide, spec, theme, *, page_num, total):
    """Bubble chart — manually drawn (python-pptx bubble support is fragile).

    spec:
        points: [{label, x, y, size, color?}, ...]
        x_label: "..."   y_label: "..."
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    points = spec.get("points", [])
    body_top = L.content_top_in + 0.5
    body_h = L.bottom_bar_y_in - body_top - 0.8
    grid_x = L.margin_left_in + 0.5
    grid_w = L.content_width_in - 0.5

    # Bounding box
    add_hline(slide, grid_x, body_top + body_h,
               grid_w, P.gray_3, thickness_pt=0.75)
    add_rect(slide, grid_x - 0.005, body_top, 0.01, body_h, P.gray_3)

    # Find x/y ranges
    if points:
        xs = [p.get("x", 0) for p in points]
        ys = [p.get("y", 0) for p in points]
        x_min, x_max = min(xs), max(xs) or 1
        y_min, y_max = min(ys), max(ys) or 1
        x_range = (x_max - x_min) or 1
        y_range = (y_max - y_min) or 1
        max_size = max((p.get("size", 1) for p in points), default=1) or 1

        for p in points:
            px = grid_x + ((p.get("x", 0) - x_min) / x_range) * (grid_w - 0.5)
            py = body_top + body_h - ((p.get("y", 0) - y_min) / y_range) * (body_h - 0.5)
            bsize = 0.3 + (p.get("size", 1) / max_size) * 1.2
            col = p.get("color")
            if col and not col.startswith("#"):
                col = getattr(P, col.replace("-", "_"), P.surface_inverse)
            if not col:
                col = P.surface_inverse
            add_oval(slide, px - bsize / 2, py - bsize / 2, bsize, bsize, col)
            if p.get("label"):
                tb = add_textbox(slide, px + bsize / 2 + 0.05,
                                  py - 0.15, 2.5, 0.3)
                write_paragraph(tb.text_frame, p["label"], theme=theme,
                                 size=T.small_size, bold=True, color=P.gray_1)

    # Axis labels
    tb = add_textbox(slide, grid_x + grid_w / 2 - 1.0,
                      body_top + body_h + 0.1, 2.0, 0.3)
    write_paragraph(tb.text_frame, spec.get("x_label", ""), theme=theme,
                     size=T.small_size - 1, bold=True, color=P.gray_2,
                     align=PP_ALIGN.CENTER)
    tb = add_textbox(slide, L.margin_left_in - 0.1,
                      body_top + body_h / 2 - 0.2, 0.5, 0.4)
    write_paragraph(tb.text_frame, spec.get("y_label", ""), theme=theme,
                     size=T.small_size - 1, bold=True, color=P.gray_2)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# DASHBOARD_KPI (#57) — KPIs row + chart + takeaways
# ════════════════════════════════════════════════════════════════════

@register("dashboard_kpi")
def dashboard_kpi(slide, spec, theme, *, page_num, total):
    """Composite dashboard: KPI row on top, chart-area placeholder middle, takeaway row bottom.

    spec:
        kpis: [{label, value, yoy?}, ...]  (max 4)
        chart_caption: "..."  (placeholder describing the chart)
        takeaways: ["...", "..."]  (max 3)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.2
    # Row 1: KPI strip (1.2" tall)
    kpis = spec.get("kpis", [])[:4]
    n = max(len(kpis), 1)
    kpi_w = (L.content_width_in - 0.15 * (n - 1)) / n
    for i, k in enumerate(kpis):
        x = L.margin_left_in + i * (kpi_w + 0.15)
        add_rect(slide, x, body_top, kpi_w, 1.1, P.gray_4)
        tb = add_textbox(slide, x + 0.2, body_top + 0.1, kpi_w - 0.4, 0.3)
        write_paragraph(tb.text_frame, k.get("label", ""), theme=theme,
                         size=T.small_size, bold=True, color=P.gray_2)
        tb = add_textbox(slide, x + 0.2, body_top + 0.4, kpi_w - 0.4, 0.5)
        write_paragraph(tb.text_frame, str(k.get("value", "")), theme=theme,
                         size=T.sub_header_size + 4, bold=True, color=P.gray_1)
        if k.get("yoy") is not None:
            yoy = float(k["yoy"])
            mark = "▲" if yoy > 0 else "▼" if yoy < 0 else "●"
            col = P.positive if yoy > 0 else P.negative if yoy < 0 else P.gray_2
            tb = add_textbox(slide, x + kpi_w - 1.0, body_top + 0.1,
                              0.9, 0.3)
            write_paragraph(tb.text_frame, f"{mark} {abs(yoy):.1f}%", theme=theme,
                             size=T.small_size, bold=True, color=col,
                             align=PP_ALIGN.RIGHT)

    # Row 2: chart area placeholder (~2.5" tall)
    chart_top = body_top + 1.3
    chart_h = 2.5
    add_rect(slide, L.margin_left_in, chart_top,
              L.content_width_in, chart_h, P.gray_4)
    tb = add_textbox(slide, L.margin_left_in + 0.3, chart_top + 0.2,
                      L.content_width_in - 0.6, 0.4)
    write_paragraph(tb.text_frame, spec.get("chart_caption", "[차트 영역]"),
                     theme=theme, size=T.body_size, color=P.gray_2)

    # Row 3: takeaway bullets
    takeaway_top = chart_top + chart_h + 0.3
    for i, t in enumerate(spec.get("takeaways", [])[:3]):
        y = takeaway_top + i * 0.45
        tb = add_textbox(slide, L.margin_left_in, y,
                          L.content_width_in, 0.4)
        p = tb.text_frame.paragraphs[0]
        r1 = p.add_run()
        set_run(r1, f"  {i+1}.  ", theme=theme,
                size=T.body_size, bold=True, color=P.accent)
        r2 = p.add_run()
        set_run(r2, t, theme=theme, size=T.body_size, color=P.gray_1)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# DASHBOARD_TABLE (#58) — Table + chart placeholder + factoid cards
# ════════════════════════════════════════════════════════════════════

@register("dashboard_table")
def dashboard_table(slide, spec, theme, *, page_num, total):
    """Composite: table left, chart placeholder right, factoid row bottom.

    spec:
        headers: [...]   rows: [[...], ...]
        chart_caption: "..."
        factoids: [{label, value}, ...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.2
    # Top zone (60%): table left + chart right
    top_h = 3.4
    table_w = L.content_width_in * 0.55
    chart_x = L.margin_left_in + table_w + 0.25
    chart_w = L.content_width_in - table_w - 0.25

    # Table
    headers = spec.get("headers", [])
    rows = spec.get("rows", [])
    n_cols = max(len(headers), 1)
    col_w = table_w / n_cols
    header_h = 0.4
    row_h = min(0.45, (top_h - header_h) / max(len(rows), 1))

    add_rect(slide, L.margin_left_in, body_top, table_w, header_h, P.surface_inverse)
    for j, h in enumerate(headers):
        tb = add_textbox(slide, L.margin_left_in + j * col_w + 0.12,
                          body_top + 0.08, col_w - 0.24, header_h - 0.16)
        write_paragraph(tb.text_frame, str(h), theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.surface_inverse_fg)
    for i, row in enumerate(rows[:8]):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, L.margin_left_in, y, table_w, row_h, P.gray_4)
        for j, cell in enumerate(row):
            tb = add_textbox(slide, L.margin_left_in + j * col_w + 0.12,
                              y + 0.08, col_w - 0.24, row_h - 0.16)
            write_paragraph(tb.text_frame, str(cell), theme=theme,
                             size=T.body_size - 1, color=P.gray_1)

    # Chart placeholder
    add_rect(slide, chart_x, body_top, chart_w, top_h, P.gray_4)
    tb = add_textbox(slide, chart_x + 0.2, body_top + 0.2,
                      chart_w - 0.4, 0.4)
    write_paragraph(tb.text_frame, spec.get("chart_caption", "[차트 영역]"),
                     theme=theme, size=T.body_size, color=P.gray_2)

    # Factoid row
    fact_top = body_top + top_h + 0.3
    factoids = spec.get("factoids", [])[:4]
    nf = max(len(factoids), 1)
    fact_w = (L.content_width_in - 0.15 * (nf - 1)) / nf
    for i, f in enumerate(factoids):
        x = L.margin_left_in + i * (fact_w + 0.15)
        add_rect(slide, x, fact_top, fact_w, 0.9, P.surface_inverse)
        tb = add_textbox(slide, x + 0.15, fact_top + 0.1, fact_w - 0.3, 0.35)
        write_paragraph(tb.text_frame, str(f.get("value", "")),
                         theme=theme, size=T.sub_header_size, bold=True,
                         color=P.surface_inverse_fg)
        tb = add_textbox(slide, x + 0.15, fact_top + 0.5, fact_w - 0.3, 0.35)
        write_paragraph(tb.text_frame, str(f.get("label", "")),
                         theme=theme, size=T.small_size, color=P.surface_inverse_fg)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# NUMBERED_LIST_PANEL (#69) — Numbered recs + highlight panel right
# ════════════════════════════════════════════════════════════════════

@register("numbered_list_panel")
def numbered_list_panel(slide, spec, theme, *, page_num, total):
    """Numbered list (left, ~65%) + highlight panel (right, ~35%).

    spec:
        items: ["...", "...", ...]  (max 7)
        panel: {label, headline, supporting: [str,...]}
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    list_w = L.content_width_in * 0.62
    panel_x = L.margin_left_in + list_w + 0.3
    panel_w = L.content_width_in - list_w - 0.3

    items = spec.get("items", [])[:7]
    n = max(len(items), 1)
    row_h = min(0.65, body_h / n)

    for i, it in enumerate(items):
        y = body_top + i * row_h
        # Number badge
        add_oval(slide, L.margin_left_in, y + 0.05, 0.45, 0.45, P.accent)
        tb = add_textbox(slide, L.margin_left_in, y + 0.08, 0.45, 0.4)
        write_paragraph(tb.text_frame, str(i + 1), theme=theme,
                         size=T.body_size, bold=True, color=P.white,
                         align=PP_ALIGN.CENTER)
        # Item text
        tb = add_textbox(slide, L.margin_left_in + 0.6, y + 0.05,
                          list_w - 0.7, row_h - 0.1)
        write_paragraph(tb.text_frame, it, theme=theme,
                         size=T.body_size, color=P.gray_1, line_spacing=1.45)

    # Highlight panel
    panel = spec.get("panel", {})
    add_rect(slide, panel_x, body_top, panel_w, body_h, P.surface_inverse)
    tb = add_textbox(slide, panel_x + 0.2, body_top + 0.2, panel_w - 0.4, 0.35)
    write_paragraph(tb.text_frame, panel.get("label", "Key insight"),
                     theme=theme, size=T.small_size - 1, bold=True,
                     color=P.surface_inverse_fg)
    if panel.get("headline"):
        tb = add_textbox(slide, panel_x + 0.2, body_top + 0.6,
                          panel_w - 0.4, 1.0)
        write_paragraph(tb.text_frame, panel["headline"], theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=P.surface_inverse_fg, line_spacing=1.3)
    for j, s in enumerate(panel.get("supporting", [])[:4]):
        tb = add_textbox(slide, panel_x + 0.2, body_top + 1.8 + j * 0.5,
                          panel_w - 0.4, 0.45)
        p = tb.text_frame.paragraphs[0]
        r1 = p.add_run()
        set_run(r1, "• ", theme=theme, size=T.body_size - 1,
                color=P.surface_inverse_fg)
        r2 = p.add_run()
        set_run(r2, s, theme=theme, size=T.body_size - 1,
                color=P.surface_inverse_fg)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# GAUGE_PAIR — Two paired gauges (KPI vs target side-by-side)
# ════════════════════════════════════════════════════════════════════

@register("gauge_pair")
def gauge_pair(slide, spec, theme, *, page_num, total):
    """Two gauges side-by-side.  Each shows a single value 0-100.

    spec:
        gauges: [{label, value, sub?}, {label, value, sub?}]
        source, bottom_bar
    """
    from deck_system.helpers.shapes import add_block_arc

    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    gauges = spec.get("gauges", [])[:2]
    body_top = L.content_top_in + 0.5
    gauge_size = 3.0
    gap = 1.0
    total_w = gauge_size * 2 + gap
    start_x = L.margin_left_in + (L.content_width_in - total_w) / 2

    for i, g in enumerate(gauges):
        gx = start_x + i * (gauge_size + gap)
        value = max(0, min(100, float(g.get("value", 0))))
        col = P.positive if value >= 70 else P.negative if value < 40 else "#F4C57A"
        add_block_arc(slide, gx, body_top, gauge_size, P.gray_4, 180, 0)
        end = (180 - (value / 100) * 180) % 360
        add_block_arc(slide, gx, body_top, gauge_size, col, 180, end)

        # Center number
        tb = add_textbox(slide, gx, body_top + gauge_size * 0.45,
                          gauge_size, 0.7)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r1 = p.add_run()
        set_run(r1, f"{value:.0f}", theme=theme, size=60, bold=True, color=col)
        r2 = p.add_run()
        set_run(r2, "%", theme=theme, size=24, color=P.gray_2)

        # Label below
        tb = add_textbox(slide, gx, body_top + gauge_size * 0.45 + 0.85,
                          gauge_size, 0.5)
        write_paragraph(tb.text_frame, g.get("label", ""), theme=theme,
                         size=T.sub_header_size, bold=True, color=P.gray_1,
                         align=PP_ALIGN.CENTER)
        if g.get("sub"):
            tb = add_textbox(slide, gx, body_top + gauge_size * 0.45 + 1.4,
                              gauge_size, 0.4)
            write_paragraph(tb.text_frame, g["sub"], theme=theme,
                             size=T.small_size, color=P.gray_2,
                             align=PP_ALIGN.CENTER)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
