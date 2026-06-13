"""Narrative layouts — two_stat, three_stat, three_trends, five_key_areas, venn.

Reference: likaku (two_stat, three_stat, venn),
           seulee26 (three_trends, five_key_areas).
"""
from __future__ import annotations
from math import cos, sin, pi

from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from deck_system.builder.registry import register
from deck_system.helpers.shapes import (
    add_rect, add_oval, add_textbox, add_hline, _clean_shape,
)
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)
from deck_system.tokens.base import hex_to_rgb


def _render_stat_row(slide, theme, spec, n_stats):
    """Shared layout for two_stat / three_stat.

    spec.stats: [{number, unit?, label, sub?}]
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    stats = spec.get("stats", [])[:n_stats]
    body_top = L.content_top_in + 0.5
    body_h = 3.5
    gap = 0.4
    tile_w = (L.content_width_in - gap * (n_stats - 1)) / n_stats

    for i, st in enumerate(stats):
        x = L.margin_left_in + i * (tile_w + gap)
        # Big number
        tb = add_textbox(slide, x, body_top, tile_w, 1.8)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r1 = p.add_run()
        set_run(r1, str(st.get("number", "")), theme=theme,
                size=96, bold=True, color=P.primary)
        if st.get("unit"):
            r2 = p.add_run()
            set_run(r2, str(st["unit"]), theme=theme,
                    size=36, color=P.gray_2)
        # Label
        tb = add_textbox(slide, x, body_top + 2.0, tile_w, 0.5)
        write_paragraph(tb.text_frame, str(st.get("label", "")), theme=theme,
                         size=T.sub_header_size, bold=True, color=P.gray_1)
        # Sub
        if st.get("sub"):
            tb = add_textbox(slide, x, body_top + 2.55, tile_w, 0.8)
            write_paragraph(tb.text_frame, str(st["sub"]), theme=theme,
                             size=T.body_size - 1, color=P.gray_2,
                             line_spacing=1.45)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)


@register("two_stat")
def two_stat(slide, spec, theme, *, page_num, total):
    _render_stat_row(slide, theme, spec, 2)
    add_page_number(slide, page_num, total, theme=theme)


@register("three_stat")
def three_stat(slide, spec, theme, *, page_num, total):
    _render_stat_row(slide, theme, spec, 3)
    add_page_number(slide, page_num, total, theme=theme)


@register("three_trends")
def three_trends(slide, spec, theme, *, page_num, total):
    """Three columns: numbered trend + headline + bullets.

    spec:
        trends: [{num?, headline, bullets: [str,...]}, ...] (3 expected)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    trends = spec.get("trends", [])[:3]
    body_top = L.content_top_in + 0.2
    gap = 0.4
    col_w = (L.content_width_in - gap * 2) / 3

    for i, t in enumerate(trends):
        x = L.margin_left_in + i * (col_w + gap)
        # Number badge
        num_str = str(t.get("num", f"{i + 1:02d}"))
        tb = add_textbox(slide, x, body_top, 1.0, 0.7)
        write_paragraph(tb.text_frame, num_str, theme=theme,
                         size=48, bold=True, color=P.accent)
        # Headline
        tb = add_textbox(slide, x, body_top + 0.9, col_w, 1.0)
        write_paragraph(tb.text_frame, str(t.get("headline", "")), theme=theme,
                         size=T.sub_header_size, bold=True, color=P.gray_1,
                         line_spacing=1.3)
        # Bullets
        for j, b in enumerate(t.get("bullets", [])):
            tb = add_textbox(slide, x, body_top + 2.1 + j * 0.5, col_w, 0.45)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, "• ", theme=theme, size=T.body_size - 1, color=P.accent)
            r2 = p.add_run()
            set_run(r2, b, theme=theme, size=T.body_size - 1,
                    color=P.gray_1)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("five_key_areas")
def five_key_areas(slide, spec, theme, *, page_num, total):
    """5 numbered area tiles in a row + descriptions.

    spec:
        areas: [{num?, label, desc}, ...] (5 expected)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    areas = spec.get("areas", [])[:5]
    n = max(len(areas), 1)
    body_top = L.content_top_in + 0.3
    gap = 0.2
    col_w = (L.content_width_in - gap * (n - 1)) / n

    for i, a in enumerate(areas):
        x = L.margin_left_in + i * (col_w + gap)
        # Number badge (surface_inverse)
        badge_size = 0.7
        add_oval(slide, x + col_w / 2 - badge_size / 2, body_top,
                  badge_size, badge_size, P.surface_inverse)
        tb = add_textbox(slide, x, body_top, col_w, badge_size)
        write_paragraph(tb.text_frame, str(a.get("num", f"{i + 1:02d}")),
                         theme=theme, size=T.sub_header_size, bold=True,
                         color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)
        # Label
        tb = add_textbox(slide, x, body_top + badge_size + 0.15, col_w, 0.6)
        write_paragraph(tb.text_frame, str(a.get("label", "")), theme=theme,
                         size=T.body_size + 1, bold=True, color=P.gray_1,
                         align=PP_ALIGN.CENTER, line_spacing=1.25)
        # Desc
        if a.get("desc"):
            tb = add_textbox(slide, x, body_top + badge_size + 0.85, col_w, 2.5)
            write_paragraph(tb.text_frame, str(a["desc"]), theme=theme,
                             size=T.body_size - 1, color=P.gray_2,
                             align=PP_ALIGN.CENTER, line_spacing=1.45)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("venn")
def venn(slide, spec, theme, *, page_num, total):
    """2 or 3 overlapping circles.  Center label = intersection.

    spec:
        circles: [{label}, {label}, ({label})]  — 2 or 3
        intersection: str (center label)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    circles = spec.get("circles", [])
    n = min(len(circles), 3)
    body_top = L.content_top_in + 0.4

    # 3-circle layout: triangle.  2-circle: side-by-side overlap.
    diam = 3.6
    if n == 2:
        cx = L.margin_left_in + L.content_width_in / 2
        cy = body_top + diam / 2 + 0.3
        offset = diam * 0.35
        positions = [(cx - offset, cy), (cx + offset, cy)]
        colors = [P.surface_inverse, P.accent]
    else:
        cx = L.margin_left_in + L.content_width_in / 2
        cy = body_top + diam / 2 + 0.5
        positions = [
            (cx, cy - diam * 0.3),
            (cx - diam * 0.3, cy + diam * 0.18),
            (cx + diam * 0.3, cy + diam * 0.18),
        ]
        colors = [P.surface_inverse, P.accent, P.gray_2]

    # Draw circles with line outlines (no fill for visible overlap)
    for i in range(n):
        x, y = positions[i]
        shape = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(x - diam / 2), Inches(y - diam / 2),
            Inches(diam), Inches(diam),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = hex_to_rgb(colors[i])
        # Transparency would be ideal but python-pptx doesn't expose alpha cleanly
        shape.line.color.rgb = hex_to_rgb(colors[i])
        shape.line.width = Inches(0.04)
        _clean_shape(shape)

    # Circle labels — outside the circle (top for 1, bottom-left/right for 2,3)
    for i in range(n):
        x, y = positions[i]
        label = circles[i].get("label", "") if i < len(circles) else ""
        if n == 2:
            tx, ty = x - 1.5, y - diam / 2 - 0.5
            align = PP_ALIGN.CENTER
        elif i == 0:
            tx, ty = x - 1.5, y - diam / 2 - 0.5
            align = PP_ALIGN.CENTER
        elif i == 1:
            tx, ty = x - 2.0, y + diam / 2 + 0.2
            align = PP_ALIGN.LEFT
        else:
            tx, ty = x + 0.0, y + diam / 2 + 0.2
            align = PP_ALIGN.LEFT
        tb = add_textbox(slide, tx, ty, 3.0, 0.4)
        write_paragraph(tb.text_frame, label, theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=colors[i], align=align)

    # Intersection (center)
    if spec.get("intersection"):
        ix = positions[0][0] if n == 2 else cx
        iy = positions[0][1] if n == 2 else cy
        tb = add_textbox(slide, ix - 1.5, iy - 0.25, 3.0, 0.5)
        write_paragraph(tb.text_frame, spec["intersection"], theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=P.white, align=PP_ALIGN.CENTER)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
