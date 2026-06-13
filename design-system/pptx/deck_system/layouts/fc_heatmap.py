"""Generic diverging heatmap — PPTX renderer (mirror of mck/assets/heatmap.js).

Row × column grid; each cell = a value shaded on a *diverging* color ramp.
Built for variance / margin maps where sign matters: negative = red, zero =
near-white pivot, positive = green. center=0 anchors both flanks so a −8% and
a +8% cell read symmetrically intense on opposite hues. FP&A use: dept × month
cost-variance maps, margin drift, YoY heatmaps.

Generalizes fc_cohort_heatmap (single-hue sequential Blues). The structural
pattern — cell grid, RGB-lerp fill, luminance-flipped text — is reused; the key
difference is the *two-sided* ramp anchored at a center value.

── Color exception (documented) ──────────────────────────────────────────
Every other chart fills via theme.palette tokens. Heatmaps are the lone
exception: continuous per-value shading needs interpolation, and palette tokens
only resolve fixed semantic colors. So cells get hex computed by RGB-lerping a
diverging ramp (ColorBrewer "RdYlGn"-style), split at center: |value| drives
intensity into the red (neg) or green (pos) flank, both passing through a
near-white pivot. Labels / headers still use palette tokens like every chart.
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.enum.text import MSO_ANCHOR

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


# Diverging RdYlGn-style ramps, each running from a near-white pivot outward to
# the strong flank color. Authored center→extreme so intensity = |value| maps
# linearly onto the flank. 4 stops/flank keeps the lerp tight (no banding).
NEG_RAMP = ["#FBE9E4", "#F5C9A8", "#E67E55", "#C0392B"]  # pivot → strong red
POS_RAMP = ["#EAF4EE", "#A8D5BA", "#5FA777", "#2A8C4A"]  # pivot → strong green
# Sequential fallback (diverging=False) — single-hue Blues, light → dark.
SEQ_RAMP = ["#EFF6FB", "#C6DCEC", "#8CB8DA", "#4A90C2", "#2A6D9C"]
EMPTY_HEX = "#E8ECF0"   # null cell — pale gray placeholder


def _hex_to_rgb_tuple(hex_str: str):
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rgb_to_hex(r: float, g: float, b: float) -> str:
    def c(n):
        return f"{max(0, min(255, round(n))):02X}"
    return f"#{c(r)}{c(g)}{c(b)}"


def _ramp_color(ramp, t: float) -> str:
    """Map t∈[0,1] onto a multi-stop hex ramp via per-channel RGB lerp."""
    x = max(0.0, min(1.0, t))
    segs = len(ramp) - 1
    pos = x * segs
    i = min(segs - 1, int(pos))
    f = pos - i
    a = _hex_to_rgb_tuple(ramp[i])
    b = _hex_to_rgb_tuple(ramp[i + 1])
    return _rgb_to_hex(
        a[0] + (b[0] - a[0]) * f,
        a[1] + (b[1] - a[1]) * f,
        a[2] + (b[2] - a[2]) * f,
    )


def _diverging_color(v, center, extent, neg_ramp, pos_ramp) -> str:
    """Pick neg/pos flank by sign of (v−center), then map |v−center|/extent →
    [0,1] → that flank's ramp. center maps to whichever flank's pale pivot, so
    the two flanks join seamlessly at the near-white center."""
    d = v - center
    t = min(1.0, abs(d) / (extent or 1.0))
    return _ramp_color(neg_ramp, t) if d < 0 else _ramp_color(pos_ramp, t)


def _luminance(hex_str: str) -> float:
    """Relative luminance (sRGB, 0–255 in) → 0..1. Flips cell text white/dark."""
    r, g, b = _hex_to_rgb_tuple(hex_str)
    return (0.2126 * r + 0.7152 * g + 0.1152 * b) / 255.0


def _cell_text(v: float, unit: str, signed: bool) -> str:
    """Signed for diverging maps (+/−), fixed 1 decimal + unit suffix."""
    a = f"{abs(v):.1f}"
    if signed:
        sign = "+" if v > 0 else ("−" if v < 0 else "")
    else:
        sign = "−" if v < 0 else ""
    return f"{sign}{a}{unit}"


# ────────────────────────────────────────────────────────────────────
# HEATMAP — rows: [...], cols: [...], values: [[v,...],...] (values[r][c])
# Diverging two-flank ramp anchored at `center`; sign → flank, |Δ| → intensity.
# ────────────────────────────────────────────────────────────────────
@register("heatmap")
def heatmap(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    rows = spec.get("rows", [])
    cols = spec.get("cols", [])
    values = spec.get("values", [])
    if not rows or not cols:
        raise ValueError("[heatmap] need ≥1 row and ≥1 col")

    unit = spec.get("unit", "")
    diverging = spec.get("diverging", True) is not False
    center = float(spec.get("center", 0))
    neg_ramp = spec.get("negRamp")
    if not (isinstance(neg_ramp, list) and len(neg_ramp) >= 2):
        neg_ramp = NEG_RAMP
    pos_ramp = spec.get("posRamp")
    if not (isinstance(pos_ramp, list) and len(pos_ramp) >= 2):
        pos_ramp = POS_RAMP

    # Flatten present values to derive the color domain.
    flat = [float(v) for row in values for v in (row or [])
            if v is not None]

    # Diverging: symmetric extent = max|v−center| so both flanks scale equally.
    # Sequential: plain [min,max].
    extent, seq_min, seq_span = 1.0, 0.0, 1.0
    dom = spec.get("domain")
    if diverging:
        if dom:
            extent = max(abs(float(dom[0]) - center), abs(float(dom[1]) - center))
        elif flat:
            extent = max(abs(v - center) for v in flat)
        extent = extent or 1.0
    else:
        if not dom:
            dom = [min(flat), max(flat)] if flat else [0, 1]
        seq_min = float(dom[0])
        seq_span = (float(dom[1]) - float(dom[0])) or 1.0

    n_cols = len(cols)
    n_rows = len(rows)

    # ── Geometry (inches off theme.layout) ──────────────────────────
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.2
    chart_w = L.content_width_in
    chart_h = 4.5

    label_w = 1.3          # row-label column (left)
    header_h = 0.35        # column-header band (top)
    plot_left = chart_left + label_w
    plot_top = chart_top + header_h
    plot_w = chart_w - label_w
    plot_h = chart_h - header_h
    cell_w = plot_w / n_cols
    cell_h = plot_h / n_rows
    gap = 0.03             # hairline gutter between cells

    # Corner label above the row-label column
    tb = add_textbox(slide, chart_left, chart_top, label_w - 0.12, header_h)
    write_paragraph(tb.text_frame, "", theme=theme,
                    size=T.small_size - 1, bold=True, color=P.gray_3,
                    align=PP_ALIGN.RIGHT)

    # Column headers (centered above each column)
    for c, col in enumerate(cols):
        cx = plot_left + c * cell_w
        tb = add_textbox(slide, cx, chart_top, cell_w, header_h)
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        write_paragraph(tb.text_frame, str(col), theme=theme,
                        size=T.small_size, bold=True, color=P.gray_2,
                        align=PP_ALIGN.CENTER)

    for r, label in enumerate(rows):
        y_top = plot_top + r * cell_h

        # Row label (left, right-aligned, vertically centered)
        tb = add_textbox(slide, chart_left, y_top, label_w - 0.12, cell_h)
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        write_paragraph(tb.text_frame, str(label), theme=theme,
                        size=T.small_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.RIGHT)

        row_vals = values[r] if r < len(values) else []
        row_vals = row_vals or []
        for c in range(n_cols):
            v = row_vals[c] if c < len(row_vals) else None
            x = plot_left + c * cell_w + gap / 2
            y = y_top + gap / 2
            w = cell_w - gap
            h = cell_h - gap

            # null → empty pale-gray placeholder, no text
            if v is None:
                add_rect(slide, x, y, w, h, EMPTY_HEX)
                continue

            v = float(v)
            # Continuous fill (documented exception): diverging two-flank or
            # sequential single-hue.
            if diverging:
                fill = _diverging_color(v, center, extent, neg_ramp, pos_ramp)
            else:
                fill = _ramp_color(SEQ_RAMP, (v - seq_min) / seq_span)
            add_rect(slide, x, y, w, h, fill)

            # Cell value text, luminance-flipped for contrast on its own fill.
            # Threshold 0.62 (not 0.5) because the diverging mid stops are
            # fairly light — at 0.5 pale cells wash out white-on-pale.
            text_hex = P.white if _luminance(fill) < 0.62 else P.gray_1
            tb = add_textbox(slide, x, y, w, h)
            tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
            write_paragraph(tb.text_frame, _cell_text(v, unit, diverging),
                            theme=theme, size=T.small_size, bold=True,
                            color=text_hex, align=PP_ALIGN.CENTER)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (self-contained; avoids editing validation.py) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("heatmap",
          _S("rows", required=True, type=list),
          _S("cols", required=True, type=list),
          _S("values", required=True, type=list),
          _S("unit", type=str),
          example={"title": "부서별 월간 비용 변동률",
                   "rows": ["물류", "영업", "마케팅"],
                   "cols": ["1월", "2월", "3월"],
                   "unit": "%", "diverging": True, "center": 0,
                   "values": [[2.1, -3.4, 5.2],
                              [-5.5, 3.1, -2.0],
                              [8.2, -6.1, 1.4]]})
