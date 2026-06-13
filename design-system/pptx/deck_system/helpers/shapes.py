"""Shape primitives — wrappers around python-pptx for cleaner call sites.

All shapes go through `_clean_shape()` to strip residual `<p:style>`
references that python-pptx leaves behind (shadows, 3D effects).
The HTML system explicitly forbids shadows/3D; this enforces parity.

Reference: likaku/experiences/layout-pitfalls.md Experience 003
"""
from __future__ import annotations
from typing import Optional

from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt, Emu

from deck_system.tokens.base import Theme, hex_to_rgb


def _clean_shape(shape) -> None:
    """Strip `<p:style>` so theme inherits don't introduce shadow/3D effects."""
    sp = shape._element
    for style_el in sp.findall(".//{http://schemas.openxmlformats.org/presentationml/2006/main}style"):
        style_el.getparent().remove(style_el)


def add_rect(slide, x: float, y: float, w: float, h: float,
             fill_hex: str, *, no_border: bool = True):
    """Add a solid-fill rectangle.

    Coordinates in inches.  Border removed by default — the HTML system
    is flat, no card outlines.
    """
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    if no_border:
        shape.line.fill.background()
    _clean_shape(shape)
    return shape


def add_oval(slide, x: float, y: float, w: float, h: float,
             fill_hex: str, *, no_border: bool = True):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    if no_border:
        shape.line.fill.background()
    _clean_shape(shape)
    return shape


def add_hline(slide, x: float, y: float, length: float,
              color_hex: str, *, thickness_pt: float = 2.0):
    """Add a horizontal rule by drawing a 1-EMU-thin filled rectangle.

    NEVER use `add_connector()` — that emits `<p:style>` which corrupts
    files on save.  This is the safe substitute.

    Reference: likaku/experiences/layout-pitfalls.md Experience 002
    """
    h_in = Pt(thickness_pt).inches
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(length), Inches(h_in)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(color_hex)
    shape.line.fill.background()
    _clean_shape(shape)
    return shape


def add_textbox(slide, x: float, y: float, w: float, h: float):
    """Add an empty text box.  Caller populates via helpers.text functions."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.text_frame.word_wrap = True
    tb.text_frame.margin_left = Emu(0)
    tb.text_frame.margin_right = Emu(0)
    tb.text_frame.margin_top = Emu(0)
    tb.text_frame.margin_bottom = Emu(0)
    return tb


def add_block_arc(slide, x: float, y: float, size: float,
                  fill_hex: str, start_angle: float, end_angle: float):
    """Native BLOCK_ARC for donut/pie segments.

    Cheaper than stacking add_rect() approximations — one shape per segment.
    `start_angle` and `end_angle` in degrees, clockwise from 3 o'clock.

    Reference: likaku/experiences/chart-limits.md
    """
    shape = slide.shapes.add_shape(
        MSO_SHAPE.BLOCK_ARC,
        Inches(x), Inches(y), Inches(size), Inches(size),
    )
    # python-pptx exposes adjust angle handles via shape.adjustments
    # Adjustment 0 = start angle, 1 = end angle (degrees, anchored at 3 o'clock)
    shape.adjustments[0] = start_angle
    shape.adjustments[1] = end_angle
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    shape.line.fill.background()
    _clean_shape(shape)
    return shape
