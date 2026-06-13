"""Summary / narrative layouts.

Includes:
- executive_summary: bottom-line capsule (surface_inverse) + 3 supporting bullets
- key_takeaway: detail-left + takeaway-cards-right
- big_number: hero number + 3 supporting bullets
- two_column_text: 2 columns of bullets (limit 1 per deck per HTML guidance)
- agenda / toc: section list
"""
from __future__ import annotations
from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)


@register("executive_summary")
def executive_summary(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    # Bottom-line capsule on surface_inverse
    cap_top = L.content_top_in + 0.1
    cap_h = 1.4
    add_rect(slide, L.margin_left_in, cap_top, L.content_width_in, cap_h,
              P.surface_inverse)
    # Label "Bottom line"
    label = spec.get("headline_label", "Bottom line")
    tb = add_textbox(slide, L.margin_left_in + 0.3, cap_top + 0.25, 1.6, 0.4)
    write_paragraph(tb.text_frame, label, theme=theme,
                     size=T.small_size - 1, bold=True,
                     color=P.surface_inverse_fg)
    # Headline body
    head = spec.get("headline") or spec.get("bottom_line", "")
    tb = add_textbox(slide, L.margin_left_in + 2.0, cap_top + 0.18,
                      L.content_width_in - 2.3, cap_h - 0.36)
    write_paragraph(tb.text_frame, head, theme=theme,
                     size=T.sub_header_size + 4, bold=True,
                     color=P.surface_inverse_fg, line_spacing=1.35)

    # Supporting bullets — 3 columns
    items = spec.get("items", []) or spec.get("bullets", [])
    items = items[:3]
    col_top = cap_top + cap_h + 0.4
    col_h = L.bottom_bar_y_in - col_top - 0.2
    n = max(len(items), 1)
    col_gap = 0.3
    col_w = (L.content_width_in - col_gap * (n - 1)) / n

    for i, it in enumerate(items):
        x = L.margin_left_in + i * (col_w + col_gap)
        # Index marker
        idx_str = it.get("num", f"{i + 1:02d}") + " · " + it.get("kicker", "")
        tb = add_textbox(slide, x, col_top, col_w, 0.4)
        write_paragraph(tb.text_frame, idx_str, theme=theme,
                         size=T.small_size - 1, bold=True,
                         color=P.accent)
        # Title
        if it.get("title"):
            tb = add_textbox(slide, x, col_top + 0.4, col_w, 0.6)
            write_paragraph(tb.text_frame, it["title"], theme=theme,
                             size=T.sub_header_size, bold=True,
                             color=P.gray_1, line_spacing=1.25)
        # Description
        if it.get("desc"):
            tb = add_textbox(slide, x, col_top + 1.1, col_w, col_h - 1.1)
            write_paragraph(tb.text_frame, it["desc"], theme=theme,
                             size=T.body_size - 1, color=P.gray_2,
                             line_spacing=1.45)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("key_takeaway")
def key_takeaway(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    # Two columns: detail (left, 60%) + takeaway cards (right, 40%)
    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2
    left_w = L.content_width_in * 0.58
    right_x = L.margin_left_in + left_w + 0.4
    right_w = L.content_width_in - left_w - 0.4

    # Left detail blocks
    details = spec.get("details", [])
    sec_h = body_h / max(len(details), 1) if details else 0
    for i, d in enumerate(details):
        y = body_top + i * sec_h
        tb = add_textbox(slide, L.margin_left_in, y, left_w, 0.4)
        write_paragraph(tb.text_frame, d.get("label", ""), theme=theme,
                         size=T.small_size - 1, bold=True,
                         color=P.primary)
        tb = add_textbox(slide, L.margin_left_in, y + 0.45,
                          left_w, sec_h - 0.5)
        write_paragraph(tb.text_frame, d.get("body", ""), theme=theme,
                         size=T.body_size, color=P.gray_1,
                         line_spacing=1.55)

    # Right takeaway cards
    cards = spec.get("takeaways", [])
    card_gap = 0.15
    card_h = (body_h - card_gap * (len(cards) - 1)) / max(len(cards), 1) \
        if cards else 0
    for i, c in enumerate(cards):
        y = body_top + i * (card_h + card_gap)
        is_primary = i < 2  # first 2 cards in surface_inverse
        fill = P.surface_inverse if is_primary else P.gray_4
        fg = P.surface_inverse_fg if is_primary else P.gray_1
        sub_fg = P.surface_inverse_fg if is_primary else P.gray_2
        add_rect(slide, right_x, y, right_w, card_h, fill)
        # Number
        tb = add_textbox(slide, right_x + 0.25, y + 0.15, 0.8, 0.6)
        write_paragraph(tb.text_frame, c.get("num", f"{i + 1:02d}"),
                         theme=theme, size=T.section_title_size,
                         bold=True, color=fg if is_primary else P.gray_3)
        # Title
        tb = add_textbox(slide, right_x + 0.95, y + 0.2,
                          right_w - 1.1, 0.5)
        write_paragraph(tb.text_frame, c.get("title", ""), theme=theme,
                         size=T.sub_header_size, bold=True, color=fg,
                         line_spacing=1.2)
        # Sub
        if c.get("sub"):
            tb = add_textbox(slide, right_x + 0.95, y + 0.65,
                              right_w - 1.1, card_h - 0.7)
            write_paragraph(tb.text_frame, c["sub"], theme=theme,
                             size=T.small_size, color=sub_fg,
                             line_spacing=1.4)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("big_number")
def big_number(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    # Left hero number
    hero_x = L.margin_left_in
    hero_y = L.content_top_in + 0.4
    hero_w = L.content_width_in * 0.4

    number = str(spec.get("number", ""))
    unit = spec.get("unit", "")
    tb = add_textbox(slide, hero_x, hero_y, hero_w, 2.4)
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r0 = p.add_run()
    set_run(r0, number, theme=theme, size=160, bold=True, color=P.primary)
    if unit:
        r1 = p.add_run()
        set_run(r1, unit, theme=theme, size=64, color=P.primary)

    # Description below
    desc = spec.get("description", "")
    if desc:
        tb = add_textbox(slide, hero_x, hero_y + 2.5, hero_w, 1.0)
        write_paragraph(tb.text_frame, desc, theme=theme,
                         size=T.body_size, color=P.gray_2,
                         line_spacing=1.4)

    # Right supporting bullets (max 3-4)
    items = spec.get("detail_items", []) or spec.get("items", [])
    items = items[:4]
    right_x = hero_x + hero_w + 0.5
    right_w = L.content_width_in - hero_w - 0.5
    n = len(items)
    item_h = 1.2
    block_total = item_h * n + 0.15 * (n - 1)
    block_y = hero_y + (3.0 - block_total) / 2

    for i, it in enumerate(items):
        y = block_y + i * (item_h + 0.15)
        accent_color = it.get("color", P.primary if i == 0
                                else (P.accent if i == 1 else P.negative))
        if not accent_color.startswith("#"):
            accent_color = getattr(P, accent_color, P.primary)
        # Left accent bar
        add_rect(slide, right_x, y, 0.04, item_h, accent_color)
        # Number
        tb = add_textbox(slide, right_x + 0.2, y, right_w - 0.2, 0.5)
        write_paragraph(tb.text_frame, str(it.get("value", "")),
                         theme=theme, size=T.section_title_size + 4,
                         bold=True, color=accent_color)
        # Body
        if it.get("desc"):
            tb = add_textbox(slide, right_x + 0.2, y + 0.55,
                              right_w - 0.2, item_h - 0.55)
            write_paragraph(tb.text_frame, it["desc"], theme=theme,
                             size=T.body_size - 1, color=P.gray_1,
                             line_spacing=1.4)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("two_column_text")
def two_column_text(slide, spec, theme, *, page_num, total):
    """Two-column bulleted list.  HTML system caps these at 1 per deck."""
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2
    gap = 0.5
    col_w = (L.content_width_in - gap) / 2

    cols = spec.get("columns", [])[:2]
    for i, col in enumerate(cols):
        x = L.margin_left_in + i * (col_w + gap)
        if col.get("title"):
            tb = add_textbox(slide, x, body_top, col_w, 0.5)
            write_paragraph(tb.text_frame, col["title"], theme=theme,
                             size=T.sub_header_size, bold=True,
                             color=P.primary)
        bullets = col.get("bullets", [])
        b_y0 = body_top + (0.6 if col.get("title") else 0)
        for j, bl in enumerate(bullets):
            tb = add_textbox(slide, x, b_y0 + j * 0.6,
                              col_w, 0.55)
            write_paragraph(tb.text_frame, "• " + bl, theme=theme,
                             size=T.body_size, color=P.gray_1,
                             line_spacing=1.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("toc")
@register("agenda")
def toc(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", "목차"), theme=theme)

    items = spec.get("items", [])
    body_top = L.content_top_in + 0.3
    row_h = (L.bottom_bar_y_in - body_top - 0.3) / max(len(items), 1)
    for i, it in enumerate(items):
        y = body_top + i * row_h
        # Number — large serif
        num_str = it.get("num") if isinstance(it, dict) else None
        if num_str is None:
            num_str = f"{i + 1:02d}"
        if isinstance(it, dict):
            title = it.get("title", "")
            desc = it.get("desc", "")
        elif isinstance(it, (list, tuple)):
            num_str = it[0] if len(it) > 0 else f"{i + 1:02d}"
            title = it[1] if len(it) > 1 else ""
            desc = it[2] if len(it) > 2 else ""
        else:
            title, desc = str(it), ""
        tb = add_textbox(slide, L.margin_left_in, y, 0.8, row_h)
        write_paragraph(tb.text_frame, str(num_str), theme=theme,
                         size=T.cover_title_size, bold=True,
                         color=P.primary)
        tb = add_textbox(slide, L.margin_left_in + 1.0, y + 0.05,
                          3.0, 0.5)
        write_paragraph(tb.text_frame, title, theme=theme,
                         size=T.section_title_size - 4, bold=True,
                         color=P.gray_1)
        if desc:
            tb = add_textbox(slide,
                              L.margin_left_in + 4.0,
                              y + 0.15, L.content_width_in - 4.0,
                              row_h - 0.2)
            write_paragraph(tb.text_frame, desc, theme=theme,
                             size=T.body_size, color=P.gray_2,
                             line_spacing=1.4)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
