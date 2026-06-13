"""Image placeholder helper — V2.3-A.

Policy: this engine does NOT embed images.  Users insert in PowerPoint.
This helper draws a clear "image goes here" rectangle so the layout
is correct and the user can drop their asset onto it.
"""
from __future__ import annotations
from pptx.enum.text import PP_ALIGN

from deck_system.helpers.shapes import add_rect, add_textbox
from deck_system.helpers.text import write_paragraph, set_run


def add_image_placeholder(slide, *, left, top, width, height,
                          label: str, theme, sub: str = "이미지 영역") -> None:
    """Draw a placeholder rectangle for user-supplied imagery.

    - gray-3 fill (visible but unobtrusive)
    - centered label + small "이미지 영역" hint
    - never references palette.primary (surface_inverse for dark-safe)
    """
    P, T = theme.palette, theme.typography
    add_rect(slide, left, top, width, height, P.gray_3)
    tb = add_textbox(slide, left, top + height / 2 - 0.35,
                      width, 0.4)
    write_paragraph(tb.text_frame, label or "이미지", theme=theme,
                     size=T.sub_header_size, bold=True,
                     color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)
    tb = add_textbox(slide, left, top + height / 2 + 0.1, width, 0.3)
    write_paragraph(tb.text_frame, sub, theme=theme,
                     size=T.small_size - 1, color=P.surface_inverse_fg,
                     align=PP_ALIGN.CENTER)
