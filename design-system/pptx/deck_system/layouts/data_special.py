"""Special data layouts: waterfall, donut, kpi_dashboard.

All accept HTML JSON spec verbatim.
"""
from __future__ import annotations
from typing import Optional

from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from deck_system.builder.registry import register
from deck_system.helpers.shapes import (
    add_rect, add_textbox, add_hline, add_block_arc,
)
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)


# ────────────────────────────────────────────────────────────────────
# WATERFALL — items: [{label, value, type ∈ base/up/down/subtotal}]
# ────────────────────────────────────────────────────────────────────

@register("waterfall")
def waterfall(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = spec.get("items", [])
    if len(items) < 2:
        raise ValueError("[waterfall] need at least 2 items")
    unit = spec.get("unit", "")

    # Walk items + compute running totals
    running = 0.0
    bars = []
    for item in items:
        t = item["type"]
        val = float(item["value"])
        if t in ("base", "subtotal"):
            start, end, delta = 0.0, val, 0.0
            running = val
        elif t == "up":
            delta = abs(val); start = running; end = running + delta
            running = end
        elif t == "down":
            delta = -abs(val); start = running; end = running + delta
            running = end
        else:
            raise ValueError(f"[waterfall] unknown type: {t}")
        bars.append({
            **item, "_start": start, "_end": end,
            "_lo": min(start, end), "_hi": max(start, end),
            "_delta": delta, "_running": running,
        })

    max_val = float(spec.get("max_value") or max(b["_hi"] for b in bars) * 1.15)

    # Geometry (inches)
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.2
    chart_w = L.content_width_in - 3.6  # room for right takeaway
    chart_h = 3.8
    baseline_y = chart_top + chart_h

    n = len(bars)
    step = chart_w / n
    bar_w = min(1.1, step * 0.62)

    def x_center(i): return chart_left + i * step + step / 2
    def y_for(v): return baseline_y - (v / max_val) * chart_h

    # Baseline rule
    add_hline(slide, chart_left, baseline_y, chart_w, P.gray_3, thickness_pt=0.75)

    # Connectors (drawn first so bars overlap endpoints)
    if spec.get("show_connector", True) is not False:
        for i in range(n - 1):
            yj = y_for(bars[i]["_running"])
            x_from = x_center(i) + bar_w / 2
            x_to = x_center(i + 1) - bar_w / 2
            add_hline(slide, x_from, yj, x_to - x_from, P.gray_3, thickness_pt=0.5)

    # Bars
    for i, b in enumerate(bars):
        bx = x_center(i) - bar_w / 2
        y_top = y_for(b["_hi"])
        y_bot = y_for(b["_lo"])
        h = max(0.04, y_bot - y_top)
        t = b["type"]
        if t in ("base", "subtotal"):
            fill = P.surface_inverse
            label_color = P.gray_1
        elif t == "up":
            fill = P.positive
            label_color = P.positive
        else:
            fill = P.negative
            label_color = P.negative
        add_rect(slide, bx, y_top, bar_w, h, fill)

        # Value label above bar
        if t in ("base", "subtotal"):
            val_txt = _fmt(b["value"], unit=unit if i == 0 else "")
        else:
            val_txt = _fmt(b["_delta"], signed=True)
        tb = add_textbox(slide, bx - 0.2, y_top - 0.32, bar_w + 0.4, 0.28)
        write_paragraph(tb.text_frame, val_txt, theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=label_color, align=PP_ALIGN.CENTER)

        # Category label below baseline
        tb = add_textbox(slide, bx - 0.3, baseline_y + 0.12,
                          bar_w + 0.6, 0.7)
        write_paragraph(tb.text_frame, b["label"], theme=theme,
                         size=T.small_size, color=P.gray_2,
                         align=PP_ALIGN.CENTER, line_spacing=1.2)

    # Net change callout (top-right)
    if spec.get("show_net", True) and any(b["type"] == "base" for b in bars):
        firsts = [b for b in bars if b["type"] == "base"]
        if len(firsts) >= 2:
            net = firsts[-1]["value"] - firsts[0]["value"]
            base_val = firsts[0]["value"]
            pct = (net / base_val * 100) if base_val else 0
            sign = "+" if net >= 0 else "−"
            color = P.positive if net >= 0 else P.negative
            txt = f"순변동 {sign}{abs(net):,.0f}{unit} ({sign}{abs(pct):.1f}%)"
            tb = add_textbox(slide, chart_left + chart_w - 3.0,
                              chart_top - 0.05, 3.0, 0.3)
            write_paragraph(tb.text_frame, txt, theme=theme,
                             size=T.body_size - 2, bold=True,
                             color=color, align=PP_ALIGN.RIGHT)

    # Right takeaway panel
    takeaway = spec.get("takeaway")
    if takeaway:
        panel_x = chart_left + chart_w + 0.3
        panel_w = L.content_width_in - chart_w - 0.3
        add_rect(slide, panel_x, chart_top, panel_w, chart_h, P.gray_4)
        tb = add_textbox(slide, panel_x + 0.2, chart_top + 0.2, panel_w - 0.4, 0.3)
        write_paragraph(tb.text_frame, takeaway.get("label", "시사점"),
                         theme=theme, size=T.small_size - 1, bold=True,
                         color=P.primary)
        if takeaway.get("headline"):
            tb = add_textbox(slide, panel_x + 0.2, chart_top + 0.55,
                              panel_w - 0.4, 0.6)
            write_paragraph(tb.text_frame, takeaway["headline"],
                             theme=theme, size=T.body_size + 4, bold=True,
                             color=P.gray_1, line_spacing=1.3)
        bullets = takeaway.get("bullets", [])
        for j, bl in enumerate(bullets):
            tb = add_textbox(slide, panel_x + 0.2,
                              chart_top + 1.25 + j * 0.55,
                              panel_w - 0.4, 0.5)
            write_paragraph(tb.text_frame, "• " + bl, theme=theme,
                             size=T.body_size - 1, color=P.gray_1,
                             line_spacing=1.4)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


def _fmt(v, *, unit: str = "", signed: bool = False) -> str:
    sign = ""
    if signed:
        if v > 0: sign = "+"
        elif v < 0: sign = "−"
    elif v < 0:
        sign = "−"
    abs_v = abs(v)
    if isinstance(abs_v, float) and abs_v.is_integer():
        abs_v = int(abs_v)
    body = f"{abs_v:,}"
    return f"{sign}{body}{unit}"


# ────────────────────────────────────────────────────────────────────
# DONUT — segments: [{label, value, color?}]
# ────────────────────────────────────────────────────────────────────

_DEFAULT_PALETTE_ORDER = ["primary", "accent", "gray_2", "gray_3", "positive", "negative"]


def _color_for(name: Optional[str], theme, fallback_idx: int) -> str:
    """Semantic name → hex.  'primary' → surface_inverse (dark-mode safe)."""
    P = theme.palette
    if not name:
        name = _DEFAULT_PALETTE_ORDER[fallback_idx % len(_DEFAULT_PALETTE_ORDER)]
    if name.startswith("#"):
        return name
    if name == "primary":
        return P.surface_inverse
    key = name.replace("-", "_")
    return getattr(P, key, P.gray_2)


@register("donut")
def donut(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    segs = [s for s in spec.get("segments", []) if s.get("value", 0) > 0]
    if not segs:
        raise ValueError("[donut] need at least one positive segment")
    max_segments = spec.get("max_segments", 6)
    show_pct = spec.get("show_percent", True)
    show_val = spec.get("show_value", True)
    callout_pos = spec.get("callout_position", "right")

    # Auto-merge tail past max_segments
    segs = sorted(segs, key=lambda s: -s["value"])
    if len(segs) > max_segments:
        head = segs[:max_segments - 1]
        tail = segs[max_segments - 1:]
        merged = {
            "label": "기타",
            "value": sum(s["value"] for s in tail),
            "color": "gray_3",
            "_merged": True,
        }
        segs = head + [merged]

    s_total = sum(s["value"] for s in segs)
    for i, s in enumerate(segs):
        s["_pct"] = s["value"] / s_total
        s["_color"] = _color_for(s.get("color"), theme, i)

    # Geometry
    donut_size = 4.0     # square
    callout_x = L.margin_left_in + donut_size + 1.0 if callout_pos == "right" \
        else L.margin_left_in
    donut_x = L.margin_left_in if callout_pos == "right" else L.content_width_in - donut_size + L.margin_left_in
    donut_y = L.content_top_in + 0.3
    cx = donut_x + donut_size / 2

    # BLOCK_ARC takes adjustments in degrees, measured from 3 o'clock clockwise.
    # We want our slices to start at 12 o'clock (top) so subtract 90.
    cursor = 0.0
    for i, s in enumerate(segs):
        sweep = s["_pct"] * 360
        start_deg = (cursor * 360 - 90) % 360
        end_deg = (start_deg + sweep) % 360
        add_block_arc(slide, donut_x, donut_y, donut_size,
                       s["_color"], start_deg, end_deg)
        cursor += s["_pct"]

    # Center labels — mask center w/ white box (overpaint)
    inner = donut_size * 0.58
    add_rect(slide,
              donut_x + (donut_size - inner) / 2,
              donut_y + (donut_size - inner) / 2,
              inner, inner, P.white)  # Will be overridden by theme bg in dark mode

    cv = spec.get("center_value")
    cl = spec.get("center_label")
    if cv:
        tb = add_textbox(slide, donut_x, donut_y + donut_size / 2 - 0.45,
                          donut_size, 0.6)
        write_paragraph(tb.text_frame, cv, theme=theme,
                         size=T.action_title_size + 16, bold=True,
                         color=P.primary, align=PP_ALIGN.CENTER)
    if cl:
        tb = add_textbox(slide, donut_x, donut_y + donut_size / 2 + 0.2,
                          donut_size, 0.3)
        write_paragraph(tb.text_frame, cl, theme=theme,
                         size=T.body_size - 2, color=P.gray_2,
                         align=PP_ALIGN.CENTER)

    # Callouts (no leader lines — color swatches sufficient, per HTML v2.2.1)
    n_rows = len(segs)
    row_h = min(0.7, 4.0 / max(n_rows, 1))
    rows_total_h = row_h * n_rows
    rows_y0 = donut_y + (donut_size - rows_total_h) / 2 + row_h / 2

    for i, s in enumerate(segs):
        row_y = rows_y0 + i * row_h - row_h / 2
        # Swatch
        add_rect(slide, callout_x, row_y + 0.05, 0.2, 0.2, s["_color"])
        # Label
        tb = add_textbox(slide, callout_x + 0.35, row_y, 4.5, 0.35)
        write_paragraph(tb.text_frame, s["label"], theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1)
        # Sub
        subparts = []
        if show_val:
            subparts.append(f"{int(s['value']):,}")
        if show_pct:
            pct = s["_pct"] * 100
            subparts.append(f"{pct:.0f}%" if pct >= 10 else f"{pct:.1f}%")
        if subparts:
            tb = add_textbox(slide, callout_x + 0.35, row_y + 0.32,
                              4.5, 0.3)
            write_paragraph(tb.text_frame, " · ".join(subparts), theme=theme,
                             size=T.small_size, color=P.gray_2)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ────────────────────────────────────────────────────────────────────
# KPI DASHBOARD — kpis: [{label, value, yoy, yoy_label, detail, value_suffix}]
# ────────────────────────────────────────────────────────────────────

@register("kpi_dashboard")
def kpi_dashboard(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    kpis = spec.get("kpis", [])
    if not kpis:
        raise ValueError("[kpi_dashboard] need at least one KPI")
    neutral = float(spec.get("neutral_threshold", 0.0))

    n = len(kpis)
    layout_mode = spec.get("layout", "auto")
    if layout_mode == "auto":
        layout_mode = {3: "1x3", 4: "2x2", 5: "1x5",
                       6: "2x3", 8: "2x4"}.get(n, f"1x{n}")
    rows, cols = (int(x) for x in layout_mode.split("x"))

    grid_x = L.margin_left_in
    grid_y = L.content_top_in + 0.2
    grid_w = L.content_width_in
    grid_h = L.bottom_bar_y_in - grid_y - 0.2
    gap = 0.15
    tile_w = (grid_w - gap * (cols - 1)) / cols
    tile_h = (grid_h - gap * (rows - 1)) / rows

    for i, kpi in enumerate(kpis):
        r = i // cols
        c = i % cols
        x = grid_x + c * (tile_w + gap)
        y = grid_y + r * (tile_h + gap)
        add_rect(slide, x, y, tile_w, tile_h, P.gray_4)

        # Label
        tb = add_textbox(slide, x + 0.25, y + 0.2, tile_w - 0.5, 0.35)
        write_paragraph(tb.text_frame, kpi["label"], theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.gray_2)

        # YoY chip (top-right)
        yoy = kpi.get("yoy")
        if yoy is not None:
            yoy_label = kpi.get("yoy_label", "")
            unit = "%p" if "%p" in yoy_label else "%"
            if yoy > neutral:
                state_color, marker = P.positive, "▲"
            elif yoy < -neutral:
                state_color, marker = P.negative, "▼"
            else:
                state_color, marker = P.gray_2, "●"
            sign = "+" if yoy > 0 else ("−" if yoy < 0 else "")
            txt = f"{marker} {sign}{abs(yoy):.1f}{unit}"
            tb = add_textbox(slide, x + tile_w - 2.2, y + 0.2,
                              2.0, 0.35)
            write_paragraph(tb.text_frame, txt, theme=theme,
                             size=T.body_size, bold=True,
                             color=state_color, align=PP_ALIGN.RIGHT)

        # Value + suffix
        value = str(kpi.get("value", "—"))
        suffix = kpi.get("value_suffix", "")
        tb = add_textbox(slide, x + 0.25, y + tile_h - 1.2, tile_w - 0.5, 0.8)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r0 = p.add_run()
        set_run(r0, value, theme=theme, size=T.cover_title_size - 8,
                bold=True, color=P.gray_1)
        if suffix:
            r1 = p.add_run()
            set_run(r1, " " + suffix, theme=theme, size=T.subtitle_size,
                    color=P.gray_2)

        # Detail
        detail = kpi.get("detail", "")
        if detail:
            tb = add_textbox(slide, x + 0.25, y + tile_h - 0.45,
                              tile_w - 0.5, 0.35)
            write_paragraph(tb.text_frame, detail, theme=theme,
                             size=T.small_size, color=P.gray_2)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)



# ────────────────────────────────────────────────────────────────────
# PARETO — bars + cumulative line (80/20 analysis)
# ────────────────────────────────────────────────────────────────────

@register("pareto")
def pareto(slide, spec, theme, *, page_num, total):
    """Pareto chart: descending bars + cumulative % line.

    spec:
        items: [{label, value}, ...]
        threshold_pct: 80 (default, draws horizontal reference line)
        source, bottom_bar
    """
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
    from pptx.util import Inches, Pt
    from deck_system.tokens.base import hex_to_rgb

    L = theme.layout
    P = theme.palette
    T = theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = sorted(spec.get("items", []), key=lambda x: -x["value"])
    threshold = spec.get("threshold_pct", 80)
    total_val = sum(i["value"] for i in items) or 1
    cum_pct = []
    running = 0
    for it in items:
        running += it["value"]
        cum_pct.append(running / total_val * 100)

    cd = CategoryChartData()
    cd.categories = [i["label"] for i in items]
    cd.add_series("Value", [i["value"] for i in items])
    cd.add_series("Cumulative %", cum_pct)

    x_in = L.margin_left_in
    y_in = L.content_top_in + 0.3
    w_in = L.content_width_in
    h_in = L.bottom_bar_y_in - y_in - 0.4

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x_in), Inches(y_in),
        Inches(w_in), Inches(h_in), cd,
    ).chart
    chart.has_legend = False
    chart.plots[0].gap_width = 60

    # Series 0: bars
    s0 = chart.series[0]
    s0.format.fill.solid()
    s0.format.fill.fore_color.rgb = hex_to_rgb(P.surface_inverse)
    s0.format.line.fill.background()
    s0.data_labels.show_value = True
    s0.data_labels.font.size = Pt(T.chart_label_size)
    s0.data_labels.font.color.rgb = hex_to_rgb(P.gray_1)
    s0.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END

    # Series 1: should be a line on a secondary axis (python-pptx can't add
    # secondary axis from CategoryChartData mid-stream; we approximate
    # by leaving as bars + adding a textbox callout summarizing 80/20)
    s1 = chart.series[1]
    s1.format.fill.solid()
    s1.format.fill.fore_color.rgb = hex_to_rgb(P.accent)
    s1.format.line.fill.background()

    # Threshold callout (above chart, right side)
    # Find the index where cumulative crosses threshold
    crossing = next((i for i, v in enumerate(cum_pct) if v >= threshold), None)
    if crossing is not None:
        from deck_system.helpers.shapes import add_textbox
        tb = add_textbox(slide, x_in + w_in - 3.5, y_in - 0.05, 3.5, 0.3)
        write_paragraph(tb.text_frame,
                        f"상위 {crossing + 1}개 항목이 누적 {threshold}% 도달",
                        theme=theme, size=T.body_size - 1, bold=True,
                        color=P.accent)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ────────────────────────────────────────────────────────────────────
# GAUGE — single-KPI dial/semicircle
# ────────────────────────────────────────────────────────────────────

@register("gauge")
def gauge(slide, spec, theme, *, page_num, total):
    """Single-KPI gauge.  Semicircle 180° with filled wedge for current value.

    spec:
        value: 0..100 (percent)
        label: str (large center label below the gauge)
        sub: str (caption below label)
        threshold_good: 70 (above = positive color)
        threshold_warn: 40 (below = negative)
        source, bottom_bar
    """
    from deck_system.helpers.shapes import add_block_arc
    L = theme.layout
    P = theme.palette
    T = theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    value = max(0, min(100, float(spec.get("value", 0))))
    good = spec.get("threshold_good", 70)
    warn = spec.get("threshold_warn", 40)
    if value >= good:
        fill_color = P.positive
        state_word = "정상"
    elif value < warn:
        fill_color = P.negative
        state_word = "위험"
    else:
        fill_color = "#F4C57A"
        state_word = "주의"

    # Gauge geometry: semicircle in the upper half
    gauge_size = 5.0
    gx = L.margin_left_in + (L.content_width_in - gauge_size) / 2
    gy = L.content_top_in + 0.3

    # Background arc (gray, full 180° from 9 o'clock to 3 o'clock = 180→0)
    # In pptx, 180° = 9 o'clock, 0°/360° = 3 o'clock
    add_block_arc(slide, gx, gy, gauge_size, P.gray_4, 180, 0)
    # Fill arc — sweep from 180° clockwise by (value/100 * 180)°
    end = 180 - (value / 100) * 180  # going clockwise toward 0
    if end < 0:
        end += 360
    add_block_arc(slide, gx, gy, gauge_size, fill_color, 180, end)

    # Center value (large)
    cv_y = gy + gauge_size * 0.45
    from deck_system.helpers.shapes import add_textbox
    tb = add_textbox(slide, gx, cv_y, gauge_size, 0.9)
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r1 = p.add_run()
    set_run(r1, f"{value:.0f}", theme=theme, size=84, bold=True, color=fill_color)
    r2 = p.add_run()
    set_run(r2, "%", theme=theme, size=36, color=P.gray_2)

    # Label below
    if spec.get("label"):
        tb = add_textbox(slide, gx, cv_y + 1.0, gauge_size, 0.5)
        write_paragraph(tb.text_frame, spec["label"], theme=theme,
                        size=T.sub_header_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.CENTER)
    # State chip
    tb = add_textbox(slide, gx, cv_y + 1.6, gauge_size, 0.4)
    write_paragraph(tb.text_frame, state_word, theme=theme,
                    size=T.body_size, bold=True, color=fill_color,
                    align=PP_ALIGN.CENTER)
    # Sub
    if spec.get("sub"):
        tb = add_textbox(slide, gx, cv_y + 2.05, gauge_size, 0.4)
        write_paragraph(tb.text_frame, spec["sub"], theme=theme,
                        size=T.body_size - 1, color=P.gray_2,
                        align=PP_ALIGN.CENTER)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
