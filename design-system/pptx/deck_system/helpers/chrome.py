"""Slide chrome — action title, source line, page number, section marker.

These elements are MANDATORY on every content slide (cover/divider/closing
override the chrome pattern).  Position values come from `theme.layout`.
"""
from __future__ import annotations
from typing import Optional

from pptx.enum.text import PP_ALIGN

from deck_system.tokens.base import Theme
from deck_system.helpers.shapes import add_textbox, add_hline
from deck_system.helpers.text import set_run, write_paragraph


def add_action_title(slide, title: str, *, theme: Theme,
                     warn_callback=None) -> None:
    """Top action title + 2pt rule.  Calls warn_callback for tone violations."""
    L = theme.layout
    tb = add_textbox(slide, L.margin_left_in, L.title_top_in,
                     L.content_width_in, L.title_height_in)
    write_paragraph(
        tb.text_frame, title,
        theme=theme, size=theme.typography.action_title_size,
        bold=True, color=theme.palette.primary, line_spacing=1.2,
    )
    add_hline(slide, L.margin_left_in, L.title_line_y_in,
              L.content_width_in, theme.palette.primary, thickness_pt=2)


def add_source(slide, source_text: str, *, theme: Theme) -> None:
    """Bottom-left source attribution, 9pt gray-2."""
    if not source_text:
        return
    L = theme.layout
    txt = source_text if source_text.lower().startswith("source") \
        else f"Source: {source_text}"
    tb = add_textbox(slide, L.margin_left_in, L.source_y_in, 8.0, 0.3)
    write_paragraph(
        tb.text_frame, txt,
        theme=theme, size=theme.typography.footer_size,
        color=theme.palette.gray_2,
    )


def add_page_number(slide, num: int, total: int, *, theme: Theme) -> None:
    L = theme.layout
    tb = add_textbox(slide, L.page_num_x_in, L.source_y_in, 1.0, 0.3)
    write_paragraph(
        tb.text_frame, f"{num}/{total}",
        theme=theme, size=theme.typography.footer_size,
        color=theme.palette.gray_2, align=PP_ALIGN.RIGHT,
    )


def add_section_marker(slide, marker_text: str, *, theme: Theme) -> None:
    """Section marker — small uppercase label, top-right.  Used on covers/dividers."""
    L = theme.layout
    tb = add_textbox(slide, L.slide_width_in - L.margin_right_in - 2.0,
                     L.title_top_in, 2.0, 0.4)
    write_paragraph(
        tb.text_frame, marker_text,
        theme=theme, size=theme.typography.small_size - 2,
        color=theme.palette.gray_2, align=PP_ALIGN.RIGHT,
    )


def add_bottom_bar(slide, text: str, *, theme: Theme,
                   tag: str = "한 줄로 —") -> None:
    """Gray-4 takeaway capsule.  16pt bold, single sentence."""
    L = theme.layout
    from deck_system.helpers.shapes import add_rect
    add_rect(slide, L.margin_left_in, L.bottom_bar_y_in,
             L.content_width_in, L.bottom_bar_h_in,
             theme.palette.gray_4)
    tb = add_textbox(
        slide,
        L.margin_left_in + 0.25,
        L.bottom_bar_y_in + 0.1,
        L.content_width_in - 0.5,
        L.bottom_bar_h_in - 0.2,
    )
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    # Tag run (primary color)
    r1 = p.add_run()
    set_run(r1, tag + " ", theme=theme,
            size=theme.typography.emphasis_size, bold=True,
            color=theme.palette.primary)
    # Body run (gray-1)
    r2 = p.add_run()
    set_run(r2, text, theme=theme,
            size=theme.typography.emphasis_size, bold=True,
            color=theme.palette.gray_1)
