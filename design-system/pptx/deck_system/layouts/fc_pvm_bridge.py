"""PVM Bridge — Price · Volume · Mix variance bridge (PPTX renderer).

An extension of the waterfall: identical cumulative running-total bar structure
(base → factor deltas → end), but each factor is *color-separated by type* so the
audience reads which driver moved the number, not just up vs down.

Mirrors mck/assets/pvm-bridge.js (design intent) and reuses data_special.waterfall
geometry: running totals, start/end anchors, lo/hi spans, x_center/y_for, dashed
connectors, net callout. Differs only in fill color, which comes from item.type.

items: [{label, value, type ∈ base/price/volume/mix/end}]
    base/end   = absolute value anchored at 0
    price/volume/mix = signed delta from prior running total
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)


# type → semantic palette token (mirrors JS TYPE_COLOR; "primary"→surface_inverse)
def _type_fill(t, P):
    return {
        "base": P.surface_inverse,
        "end": P.surface_inverse,
        "price": P.accent,
        "volume": P.positive,
        "mix": P.gray_2,
    }[t]


@register("pvm_bridge")
def pvm_bridge(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = spec.get("items", [])
    if len(items) < 2:
        raise ValueError("[pvm_bridge] need at least 2 items")
    unit = spec.get("unit", "")

    # Walk items + compute running totals (waterfall structure)
    running = 0.0
    bars = []
    for i, item in enumerate(items):
        t = item["type"]
        val = float(item["value"])
        if t in ("base", "end"):
            start, end, delta = 0.0, val, 0.0
            running = val
        elif t in ("price", "volume", "mix"):
            delta = val
            start = running
            end = running + delta
            running = end
        else:
            raise ValueError(f"[pvm_bridge] unknown type at index {i}: {t}")
        bars.append({
            **item, "_start": start, "_end": end,
            "_lo": min(start, end), "_hi": max(start, end),
            "_delta": delta, "_running": running,
        })

    max_val = float(spec.get("max_value") or max(b["_hi"] for b in bars) * 1.15)

    # Geometry (inches) — mirrors waterfall
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

    # Connectors (dashed approximation via short segments; drawn first)
    if spec.get("show_connector", True) is not False:
        for i in range(n - 1):
            yj = y_for(bars[i]["_running"])
            x_from = x_center(i) + bar_w / 2
            x_to = x_center(i + 1) - bar_w / 2
            _dashed_hline(slide, x_from, yj, x_to, P.gray_2)

    # Bars
    for i, b in enumerate(bars):
        bx = x_center(i) - bar_w / 2
        y_top = y_for(b["_hi"])
        y_bot = y_for(b["_lo"])
        h = max(0.04, y_bot - y_top)
        t = b["type"]
        fill = _type_fill(t, P)
        add_rect(slide, bx, y_top, bar_w, h, fill)

        # Value label above bar — absolute for anchors, signed delta for factors
        if t in ("base", "end"):
            val_txt = _fmt(b["value"], unit=unit if i == 0 else "")
        else:
            val_txt = _fmt(b["_delta"], signed=True)
        tb = add_textbox(slide, bx - 0.2, y_top - 0.32, bar_w + 0.4, 0.28)
        write_paragraph(tb.text_frame, val_txt, theme=theme,
                        size=T.body_size - 1, bold=True,
                        color=P.gray_1, align=PP_ALIGN.CENTER)

        # Category label below baseline
        tb = add_textbox(slide, bx - 0.3, baseline_y + 0.12, bar_w + 0.6, 0.7)
        write_paragraph(tb.text_frame, b["label"], theme=theme,
                        size=T.small_size, color=P.gray_2,
                        align=PP_ALIGN.CENTER, line_spacing=1.2)

    # Net change callout (base → end), top-right
    if spec.get("show_net", True):
        firstbase = next((b for b in bars if b["type"] == "base"), None)
        lastend = next((b for b in reversed(bars) if b["type"] == "end"), None) \
            or next((b for b in reversed(bars) if b["type"] == "base"), None)
        if firstbase is not None and lastend is not None and firstbase is not lastend:
            net = lastend["value"] - firstbase["value"]
            base_val = firstbase["value"]
            pct = (net / base_val * 100) if base_val else 0
            sign = "+" if net >= 0 else "−"
            color = P.positive if net >= 0 else P.negative
            txt = f"순변동 {sign}{abs(net):,.0f}{unit} ({sign}{abs(pct):.1f}%)"
            tb = add_textbox(slide, chart_left + chart_w - 3.0,
                             chart_top - 0.05, 3.0, 0.3)
            write_paragraph(tb.text_frame, txt, theme=theme,
                            size=T.body_size - 2, bold=True,
                            color=color, align=PP_ALIGN.RIGHT)

    # Right takeaway panel (optional, mirrors waterfall)
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
        for j, bl in enumerate(takeaway.get("bullets", [])):
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


def _dashed_hline(slide, x_from, x_to, y, color, *, dash=0.08, gap=0.06):
    """Approximate a dashed horizontal connector via short add_hline segments."""
    span = x_to - x_from
    if span <= 0:
        return
    x = x_from
    while x < x_to:
        seg = min(dash, x_to - x)
        add_hline(slide, x, y, seg, color, thickness_pt=0.5)
        x += dash + gap


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
    return f"{sign}{abs_v:,}{unit}"


# ── schema registration (self-contained, like fpna_charts.bullet) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("pvm_bridge",
          _S("items", required=True, type=list, min_length=2),
          _S("unit", type=str),
          example={"title": "FY26 매출 분해", "unit": "억", "items": [
              {"label": "FY25 매출", "value": 1200, "type": "base"},
              {"label": "가격 효과", "value": 145, "type": "price"},
              {"label": "물량 효과", "value": 90, "type": "volume"},
              {"label": "믹스 효과", "value": -55, "type": "mix"},
              {"label": "FY26 매출", "value": 1380, "type": "end"}]})
