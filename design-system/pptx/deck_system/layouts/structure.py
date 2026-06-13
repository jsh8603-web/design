"""Structure slides — cover, section_divider, closing.

These are full-bleed surface_inverse backgrounds.  NEVER reference
`primary` directly here — dark theme would collapse the background
into bg.  Always use `surface_inverse` / `surface_inverse_fg`.
"""
from __future__ import annotations
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import set_run, write_paragraph


@register("cover")
def cover_slide(slide, spec, theme, *, page_num, total):
    """Cover — left navy panel + title block on white.

    spec keys: title, subtitle, author, date, section_marker
    """
    L = theme.layout
    P = theme.palette
    T = theme.typography

    # Left full-height surface_inverse panel
    add_rect(slide, 0, 0, 3.8, L.slide_height_in, P.surface_inverse)

    # Pre-title (small caps)
    section = spec.get("section_marker") or spec.get("date", "")
    if section:
        tb = add_textbox(slide, 0.8, 1.0, 3.0, 0.3)
        write_paragraph(
            tb.text_frame, section,
            theme=theme, size=T.small_size,
            color=P.surface_inverse_fg,
        )
        tb.text_frame.paragraphs[0].runs[0].font.size = (
            tb.text_frame.paragraphs[0].runs[0].font.size  # keep small
        )

    # Title (large serif/display, on white side)
    title = spec.get("title", "")
    tb = add_textbox(slide, 4.6, 2.0, 8.0, 1.8)
    write_paragraph(
        tb.text_frame, title,
        theme=theme, size=T.cover_title_size,
        bold=True, color=P.primary, line_spacing=1.05,
    )

    # Divider rule below title
    add_hline(slide, 4.6, 3.85, 1.25, P.primary, thickness_pt=2)

    # Subtitle
    sub = spec.get("subtitle", "")
    if sub:
        tb = add_textbox(slide, 4.6, 4.1, 8.0, 1.0)
        write_paragraph(
            tb.text_frame, sub,
            theme=theme, size=T.subtitle_size,
            color=P.gray_1, line_spacing=1.4,
        )

    # Meta row (Author · Date)
    author = spec.get("author", "")
    date = spec.get("date", "")
    if author or date:
        meta = "  ·  ".join(p for p in [author, date] if p)
        tb = add_textbox(slide, 4.6, 6.2, 8.0, 0.4)
        write_paragraph(
            tb.text_frame, meta,
            theme=theme, size=T.body_size,
            color=P.gray_2,
        )


@register("section_divider")
def section_divider(slide, spec, theme, *, page_num, total):
    """Full-bleed surface_inverse with section number + title."""
    L = theme.layout
    P = theme.palette
    T = theme.typography

    # Full-bleed background
    add_rect(slide, 0, 0, L.slide_width_in, L.slide_height_in, P.surface_inverse)

    # Top hairline
    add_hline(slide, 0.8, 0.8, 1.25, P.surface_inverse_fg, thickness_pt=2)

    # Section label (small caps)
    label = spec.get("section_label") or spec.get("marker") or ""
    if label:
        tb = add_textbox(slide, 0.8, 1.25, 8.0, 0.4)
        write_paragraph(
            tb.text_frame, label,
            theme=theme, size=T.body_size,
            color=P.surface_inverse_fg,
        )

    # Large title
    title = spec.get("title", "")
    tb = add_textbox(slide, 0.8, 2.1, 11.5, 2.0)
    write_paragraph(
        tb.text_frame, title,
        theme=theme, size=80,
        bold=True, color=P.surface_inverse_fg, line_spacing=1.05,
    )

    # Subtitle
    sub = spec.get("subtitle", "")
    if sub:
        tb = add_textbox(slide, 0.8, 4.1, 11.5, 1.5)
        write_paragraph(
            tb.text_frame, sub,
            theme=theme, size=T.section_title_size,
            color=P.surface_inverse_fg, line_spacing=1.4,
        )

    # Footer
    footer = spec.get("footer", "")
    if footer:
        tb = add_textbox(slide, 0.8, L.slide_height_in - 0.5, 8.0, 0.3)
        write_paragraph(
            tb.text_frame, footer,
            theme=theme, size=T.footer_size,
            color=P.surface_inverse_fg,
        )


@register("closing")
def closing_slide(slide, spec, theme, *, page_num, total):
    """Thank-you slide.  Full-bleed surface_inverse, large closing message."""
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_rect(slide, 0, 0, L.slide_width_in, L.slide_height_in, P.surface_inverse)
    add_hline(slide, 0.8, 0.8, 1.25, P.surface_inverse_fg, thickness_pt=2)

    pretitle = spec.get("pretitle", "THANK YOU · 감 사 합 니 다")
    tb = add_textbox(slide, 0.8, 1.25, 11.0, 0.4)
    write_paragraph(
        tb.text_frame, pretitle,
        theme=theme, size=T.body_size,
        color=P.surface_inverse_fg,
    )

    title = spec.get("title", "")
    tb = add_textbox(slide, 0.8, 2.3, 11.5, 2.4)
    write_paragraph(
        tb.text_frame, title,
        theme=theme, size=T.cover_title_size + 20,
        bold=True, color=P.surface_inverse_fg, line_spacing=1.1,
    )

    sub = spec.get("subtitle", "")
    if sub:
        tb = add_textbox(slide, 0.8, 5.0, 11.0, 1.5)
        write_paragraph(
            tb.text_frame, sub,
            theme=theme, size=T.subtitle_size,
            color=P.surface_inverse_fg, line_spacing=1.5,
        )

    contact = spec.get("contact", "")
    if contact:
        tb = add_textbox(slide, 0.8, L.slide_height_in - 0.5, 10.0, 0.3)
        write_paragraph(
            tb.text_frame, contact,
            theme=theme, size=T.footer_size,
            color=P.surface_inverse_fg,
        )


@register("dark_navy_summary")
def dark_navy_summary(slide, spec, theme, *, page_num, total):
    """Bottom-line capsule — full-bleed surface_inverse with single statement.

    Used between cover and exec summary for a punchy opener.
    """
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_rect(slide, 0, 0, L.slide_width_in, L.slide_height_in, P.surface_inverse)

    label = spec.get("label", "Bottom line")
    tb = add_textbox(slide, 0.8, 2.6, 11.5, 0.6)
    write_paragraph(
        tb.text_frame, label,
        theme=theme, size=T.body_size,
        color=P.surface_inverse_fg,
    )

    body = spec.get("body") or spec.get("title", "")
    tb = add_textbox(slide, 0.8, 3.2, 11.5, 2.5)
    write_paragraph(
        tb.text_frame, body,
        theme=theme, size=T.section_title_size,
        bold=True, color=P.surface_inverse_fg, line_spacing=1.4,
    )
