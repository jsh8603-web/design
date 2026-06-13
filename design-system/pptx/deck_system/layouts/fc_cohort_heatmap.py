"""Cohort retention heatmap — PPTX renderer (mirror of mck/assets/cohort-heatmap.js).

Retention grid: one row per signup cohort, one column per elapsed period
(M0, M1, …), each cell = retention % shaded on a continuous color ramp.

── Color exception (documented) ──────────────────────────────────────────
Every other chart fills via theme.palette tokens. This one is the lone
exception: a continuous heatmap needs per-value shading. Cells are filled
with hex computed by RGB-lerping a single-hue sequential ramp (ColorBrewer
"Blues"), 5 closely-spaced stops to avoid lerp banding / muddy midtones.
Row labels / column headers still use palette tokens like every other chart.
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.enum.text import MSO_ANCHOR

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


# Single-hue sequential "Blues" ramp, light → dark. 5 stops keeps lerp tight
# so the continuous fill doesn't band or go muddy across the 0–100% range.
DEFAULT_RAMP = ["#EFF6FB", "#C6DCEC", "#8CB8DA", "#4A90C2", "#2A6D9C"]
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


def _luminance(hex_str: str) -> float:
    """Relative luminance (sRGB, 0–255 in) → 0..1. Flips cell text white/dark."""
    r, g, b = _hex_to_rgb_tuple(hex_str)
    return (0.2126 * r + 0.7152 * g + 0.1152 * b) / 255.0


# ────────────────────────────────────────────────────────────────────
# COHORT_HEATMAP — periods: [...], cohorts: [{label, values: [...]}]
# rows = cohorts, cols = elapsed periods, cell = retention % (continuous fill)
# ────────────────────────────────────────────────────────────────────
@register("cohort_heatmap")
def cohort_heatmap(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    periods = spec.get("periods", [])
    cohorts = spec.get("cohorts", [])
    if not periods or not cohorts:
        raise ValueError("[cohort_heatmap] need ≥1 period and ≥1 cohort")

    ramp = spec.get("ramp")
    if not (isinstance(ramp, list) and len(ramp) >= 2):
        ramp = DEFAULT_RAMP
    domain = spec.get("domain") or [0, 100]
    d_min, d_max = float(domain[0]), float(domain[1])
    span = (d_max - d_min) or 1.0

    cols = len(periods)
    rows = len(cohorts)

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
    cell_w = plot_w / cols
    cell_h = plot_h / rows
    gap = 0.03             # hairline gutter between cells

    # Corner label above the row-label column
    tb = add_textbox(slide, chart_left, chart_top, label_w - 0.12, header_h)
    write_paragraph(tb.text_frame, "코호트", theme=theme,
                    size=T.small_size - 1, bold=True, color=P.gray_3,
                    align=PP_ALIGN.RIGHT)

    # Column headers (period labels, centered above each column)
    for c, pd in enumerate(periods):
        cx = plot_left + c * cell_w
        tb = add_textbox(slide, cx, chart_top, cell_w, header_h)
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        write_paragraph(tb.text_frame, str(pd), theme=theme,
                        size=T.small_size, bold=True, color=P.gray_2,
                        align=PP_ALIGN.CENTER)

    for r, co in enumerate(cohorts):
        y_top = plot_top + r * cell_h

        # Row label (cohort name, left, right-aligned, vertically centered)
        tb = add_textbox(slide, chart_left, y_top, label_w - 0.12, cell_h)
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        write_paragraph(tb.text_frame, str(co.get("label", "")), theme=theme,
                        size=T.small_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.RIGHT)

        values = co.get("values", []) or []
        for c in range(cols):
            v = values[c] if c < len(values) else None
            x = plot_left + c * cell_w + gap / 2
            y = y_top + gap / 2
            w = cell_w - gap
            h = cell_h - gap

            # null = not-yet-elapsed → empty pale-gray placeholder, no text
            if v is None:
                add_rect(slide, x, y, w, h, EMPTY_HEX)
                continue

            # Continuous fill: map value→[0,1]→ramp hex (documented exception)
            t = (float(v) - d_min) / span
            fill = _ramp_color(ramp, t)
            add_rect(slide, x, y, w, h, fill)

            # Cell value text, luminance-flipped for contrast on its own fill.
            # Threshold 0.62 (not 0.5) because the Blues ramp's mid stops are
            # fairly light — at 0.5 lower-retention cells wash out as white on
            # pale blue. Bumping it keeps those on dark text.
            text_hex = P.white if _luminance(fill) < 0.62 else P.gray_1
            tb = add_textbox(slide, x, y, w, h)
            tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
            write_paragraph(tb.text_frame, f"{round(float(v))}%", theme=theme,
                            size=T.small_size, bold=True, color=text_hex,
                            align=PP_ALIGN.CENTER)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (self-contained; avoids editing validation.py) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("cohort_heatmap",
          _S("cohorts", required=True, type=list, min_length=1),
          _S("periods", required=True, type=list),
          example={"title": "코호트 잔존율",
                   "periods": ["M0", "M1", "M2", "M3"],
                   "cohorts": [
                       {"label": "25-01", "values": [100, 82, 71, 65]},
                       {"label": "25-02", "values": [100, 79, 68, None]}]})
