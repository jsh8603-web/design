"""TREEMAP — 1-level squarified treemap PPTX renderer.

Mirror of mck/assets/treemap.js. Area-proportional rectangle packing: each
item's cell area ∝ its value, so a single glance reads composition / share.
FP&A use: cost structure (영업비용 구성), revenue mix, segment contribution.

Layout = squarified treemap (Bruls/Huizing/van Wijk) — greedy row-packing that
keeps cell aspect ratios near 1. Cell fills cycle the palette ring; text ink
auto-switches white/dark by the fill's WCAG luminance. White seams between
cells come from insetting each cell by GAP (no borders — add_rect is flat).
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number
from deck_system.tokens.base import hex_to_rgb


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}{unit}"


# ────────────────────────────────────────────────────────────────────
# Squarified layout — port of treemap.js squarify().
# values: list[float] (all > 0), rect: dict {x, y, w, h} in inches.
# Returns one {x, y, w, h} per value, same order, tiling `rect` exactly.
# ────────────────────────────────────────────────────────────────────
def _squarify(values, rect):
    total = sum(values)
    area = rect["w"] * rect["h"]
    scaled = [(v / total) * area for v in values]
    out = [None] * len(values)
    free = dict(rect)
    i = 0

    def worst(row, side, sum_row):
        s2 = sum_row * sum_row
        side2 = side * side
        rmax = max(row)
        rmin = min(row)
        return max((side2 * rmax) / s2, s2 / (side2 * rmin))

    while i < len(scaled):
        shorter = min(free["w"], free["h"])
        row = [scaled[i]]
        sum_row = scaled[i]
        j = i + 1
        # Grow the row while aspect ratios keep improving.
        while j < len(scaled):
            next_sum = sum_row + scaled[j]
            if worst(row, shorter, sum_row) <= worst(row + [scaled[j]], shorter, next_sum):
                break
            row.append(scaled[j])
            sum_row = next_sum
            j += 1
        # Lay the finalized row across the shorter side of the free rect.
        row_thick = sum_row / shorter if shorter > 0 else 0
        pos = 0.0
        horizontal = free["w"] >= free["h"]
        for k in range(i, j):
            cell_len = (scaled[k] / sum_row) * shorter if sum_row > 0 else 0
            if horizontal:
                out[k] = {"x": free["x"], "y": free["y"] + pos,
                          "w": row_thick, "h": cell_len}
            else:
                out[k] = {"x": free["x"] + pos, "y": free["y"],
                          "w": cell_len, "h": row_thick}
            pos += cell_len
        # Shrink the free rect by the consumed strip.
        if horizontal:
            free["x"] += row_thick
            free["w"] -= row_thick
        else:
            free["y"] += row_thick
            free["h"] -= row_thick
        i = j
    return out


def _text_on_fill(fill_hex: str) -> str:
    """WCAG relative luminance → white vs dark ink, mirror of treemap.js."""
    rgb = hex_to_rgb(fill_hex)
    r, g, b = rgb[0], rgb[1], rgb[2]

    def lin(c):
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    lum = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return "#1A1A1A" if lum > 0.45 else "#FFFFFF"


def _est_w_em(s: str, size_pt: float) -> float:
    """Estimate rendered text width in inches: CJK ≈ 1.02em, Latin ≈ 0.58em."""
    units = 0.0
    for ch in s:
        units += 0.58 if ord(ch) < 128 else 1.02
    return units * (size_pt / 72.0)


@register("treemap")
def treemap(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    raw_items = spec.get("items", [])
    if not raw_items:
        raise ValueError("[treemap] need at least 1 item")
    g_unit = spec.get("unit", "")

    # Positive values only; preserve declared (narrative) order.
    items = [it for it in raw_items if float(it.get("value", 0)) > 0]
    if not items:
        raise ValueError("[treemap] need at least 1 item with value > 0")
    grand_total = sum(float(it["value"]) for it in items)

    # ── Plot geometry (inches) ──────────────────────────────────────
    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.2
    chart_w = L.content_width_in
    chart_h = 4.55
    GAP = 0.025  # half-seam inset per cell → ~0.05in white gap between cells

    rect = {"x": chart_left, "y": chart_top, "w": chart_w, "h": chart_h}
    cells = _squarify([float(it["value"]) for it in items], rect)

    palette_ring = [P.primary, P.accent, P.gray_2, P.positive, P.gray_3, P.negative]

    for i, it in enumerate(items):
        c = cells[i]
        x = c["x"] + GAP
        y = c["y"] + GAP
        w = max(0.0, c["w"] - GAP * 2)
        h = max(0.0, c["h"] - GAP * 2)
        if w <= 0 or h <= 0:
            continue

        fill = it.get("color") or palette_ring[i % len(palette_ring)]
        ink = _text_on_fill(fill)
        pct = (float(it["value"]) / grand_total) * 100 if grand_total > 0 else 0

        add_rect(slide, x, y, w, h, fill)

        # ── Text fitting: only draw what the cell holds without overflow ──
        # Sizes scale with the smaller cell dimension (in inches → pt).
        smaller_pt = min(w, h) * 72.0
        label_size = min(20, max(11, round(smaller_pt * 0.20)))
        value_size = max(9, round(label_size * 0.82))

        label_text = str(it.get("label", ""))
        value_text = _fmt(float(it["value"]), g_unit) + f"  {pct:.0f}%"

        pad_in = 0.12  # horizontal text padding inside the cell
        label_h_in = label_size / 72.0 * 1.4
        value_h_in = value_size / 72.0 * 1.4

        fits_label = (_est_w_em(label_text, label_size) <= w - pad_in
                      and label_h_in + 0.04 <= h)
        show_value = (_est_w_em(value_text, value_size) <= w - pad_in
                      and label_h_in + value_h_in + 0.06 <= h)

        cx = x + w / 2.0
        cy = y + h / 2.0

        if fits_label and show_value:
            # Two stacked lines, centered on the cell.
            lt = add_textbox(slide, x + 0.04, cy - label_h_in - 0.02,
                             w - 0.08, label_h_in)
            write_paragraph(lt.text_frame, label_text, theme=theme,
                            size=label_size, bold=True, color=ink,
                            align=PP_ALIGN.CENTER)
            vt = add_textbox(slide, x + 0.04, cy + 0.01, w - 0.08, value_h_in)
            write_paragraph(vt.text_frame, value_text, theme=theme,
                            size=value_size, bold=True, color=ink,
                            align=PP_ALIGN.CENTER)
        elif fits_label:
            # Tight cell → label only, vertically centered.
            lt = add_textbox(slide, x + 0.04, cy - label_h_in / 2.0,
                             w - 0.08, label_h_in)
            write_paragraph(lt.text_frame, label_text, theme=theme,
                            size=label_size, bold=True, color=ink,
                            align=PP_ALIGN.CENTER)
        # else: cell too small for even the label → colored tile only.

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (self-contained, mirrors fpna_charts.py) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("treemap",
          _S("items", required=True, type=list, min_length=1),
          _S("unit", type=str),
          example={"title": "영업비용 구성", "unit": "억", "items": [
              {"label": "인건비", "value": 420},
              {"label": "물류비", "value": 310},
              {"label": "마케팅비", "value": 180}]})
