"""Compare/contrast layouts — comparison_table, pros_cons, before_after.

Reference: likaku/seulee26 comparison_slides.py.
"""
from __future__ import annotations
from typing import List

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)


@register("comparison_table")
def comparison_table(slide, spec, theme, *, page_num, total):
    """Side-by-side feature/option comparison.

    spec:
        options: ["A", "B", ...] (column headers, 2-5 supported)
        criteria: [{label, values: [str,...] per option}, ...]
        highlight_option: int (optional, 0-based; column gets accent header)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    options = spec.get("options", [])
    criteria = spec.get("criteria", [])
    highlight = spec.get("highlight_option")

    body_left = L.margin_left_in
    body_top = L.content_top_in + 0.2
    body_width = L.content_width_in
    header_h = 0.55
    row_h = 0.5

    label_w = body_width * 0.28
    n_opt = max(len(options), 1)
    opt_w = (body_width - label_w) / n_opt

    # Header: blank label cell + option headers
    add_rect(slide, body_left, body_top, body_width, header_h, P.surface_inverse)
    for j, opt in enumerate(options):
        x = body_left + label_w + j * opt_w
        # Highlight column header
        if highlight == j:
            add_rect(slide, x, body_top, opt_w, header_h, P.accent)
        tb = add_textbox(slide, x + 0.15, body_top + 0.12, opt_w - 0.3, header_h - 0.2)
        write_paragraph(tb.text_frame, str(opt), theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=P.surface_inverse_fg,
                         align=PP_ALIGN.CENTER)

    # Rows
    for i, c in enumerate(criteria):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, body_left, y, body_width, row_h, P.gray_4)
        # Label
        tb = add_textbox(slide, body_left + 0.15, y + 0.1, label_w - 0.3, row_h - 0.15)
        write_paragraph(tb.text_frame, c.get("label", ""), theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1)
        # Values
        for j, val in enumerate(c.get("values", [])):
            x = body_left + label_w + j * opt_w
            tb = add_textbox(slide, x + 0.15, y + 0.1, opt_w - 0.3, row_h - 0.15)
            write_paragraph(tb.text_frame, str(val), theme=theme,
                             size=T.body_size, color=P.gray_1,
                             align=PP_ALIGN.CENTER)
        add_hline(slide, body_left, y + row_h - 0.01,
                   body_width, P.gray_4, thickness_pt=0.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("pros_cons")
def pros_cons(slide, spec, theme, *, page_num, total):
    """Pros/cons two-column layout with ✓/✗ markers.

    spec:
        pros_title (default "장점"), pros: ["..."],
        cons_title (default "단점"), cons: ["..."],
        conclusion (optional), source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2
    gap = 0.4
    col_w = (L.content_width_in - gap) / 2

    pros_title = spec.get("pros_title", "장점")
    cons_title = spec.get("cons_title", "단점")

    for i, (title, items, color, marker) in enumerate([
        (pros_title, spec.get("pros", []), P.positive, "✓"),
        (cons_title, spec.get("cons", []), P.negative, "✗"),
    ]):
        x = L.margin_left_in + i * (col_w + gap)
        # Header strip
        add_rect(slide, x, body_top, col_w, 0.5, color)
        tb = add_textbox(slide, x + 0.25, body_top + 0.1, col_w - 0.5, 0.3)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r1 = p.add_run()
        set_run(r1, f"{marker}  ", theme=theme,
                size=T.sub_header_size, bold=True, color=P.white)
        r2 = p.add_run()
        set_run(r2, title, theme=theme,
                size=T.sub_header_size, bold=True, color=P.white)

        # Bullets
        for j, item in enumerate(items):
            y = body_top + 0.7 + j * 0.55
            tb = add_textbox(slide, x + 0.15, y, col_w - 0.3, 0.5)
            p = tb.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r1 = p.add_run()
            set_run(r1, f"{marker} ", theme=theme,
                    size=T.body_size, bold=True, color=color)
            r2 = p.add_run()
            set_run(r2, item, theme=theme,
                    size=T.body_size, color=P.gray_1)

    if spec.get("conclusion"):
        add_bottom_bar(slide, spec["conclusion"], theme=theme,
                       tag=spec.get("bottom_tag", "결론 —"))
    elif spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("before_after")
def before_after(slide, spec, theme, *, page_num, total):
    """Before/after two-column layout with arrow divider.

    spec:
        before_title (default "이전"), before: ["..."],
        after_title (default "이후"), after: ["..."],
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2
    arrow_w = 0.7
    col_w = (L.content_width_in - arrow_w) / 2

    before_title = spec.get("before_title", "이전")
    after_title = spec.get("after_title", "이후")

    # Before block (gray_4 bg)
    x0 = L.margin_left_in
    add_rect(slide, x0, body_top, col_w, body_h, P.gray_4)
    tb = add_textbox(slide, x0 + 0.25, body_top + 0.25, col_w - 0.5, 0.45)
    write_paragraph(tb.text_frame, before_title, theme=theme,
                     size=T.sub_header_size, bold=True, color=P.gray_2)
    for j, item in enumerate(spec.get("before", [])):
        y = body_top + 0.85 + j * 0.55
        tb = add_textbox(slide, x0 + 0.25, y, col_w - 0.5, 0.5)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r1 = p.add_run()
        set_run(r1, "• ", theme=theme, size=T.body_size, color=P.gray_3)
        r2 = p.add_run()
        set_run(r2, item, theme=theme, size=T.body_size, color=P.gray_2)

    # Arrow (black circle with → glyph)
    arrow_x = x0 + col_w
    arrow_size = 0.5
    arrow_cy = body_top + body_h / 2
    add_rect(slide, arrow_x + 0.1, arrow_cy - arrow_size / 2,
              arrow_w - 0.2, arrow_size, P.surface_inverse)
    tb = add_textbox(slide, arrow_x, arrow_cy - 0.2, arrow_w, 0.4)
    write_paragraph(tb.text_frame, "→", theme=theme,
                     size=T.sub_header_size + 4, bold=True,
                     color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)

    # After block (surface_inverse bg)
    x1 = arrow_x + arrow_w
    add_rect(slide, x1, body_top, col_w, body_h, P.surface_inverse)
    tb = add_textbox(slide, x1 + 0.25, body_top + 0.25, col_w - 0.5, 0.45)
    write_paragraph(tb.text_frame, after_title, theme=theme,
                     size=T.sub_header_size, bold=True,
                     color=P.surface_inverse_fg)
    for j, item in enumerate(spec.get("after", [])):
        y = body_top + 0.85 + j * 0.55
        tb = add_textbox(slide, x1 + 0.25, y, col_w - 0.5, 0.5)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r1 = p.add_run()
        set_run(r1, "• ", theme=theme, size=T.body_size,
                color=P.surface_inverse_fg)
        r2 = p.add_run()
        set_run(r2, item, theme=theme, size=T.body_size,
                color=P.surface_inverse_fg)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
