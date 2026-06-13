"""Shape primitives — wrappers around python-pptx for cleaner call sites.

All shapes go through `_clean_shape()` to strip residual `<p:style>`
references that python-pptx leaves behind (shadows, 3D effects).
The HTML system explicitly forbids shadows/3D; this enforces parity.

Reference: likaku/experiences/layout-pitfalls.md Experience 003
"""
from __future__ import annotations
import math
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


def add_line(slide, x1: float, y1: float, x2: float, y2: float,
             color_hex: str, *, thickness_pt: float = 2.0):
    """Add an arbitrary-angle line between two points (inches).

    Implemented as a thin, rotated filled RECTANGLE — NEVER `add_connector()`
    (which emits `<p:style>` and corrupts files on save; see add_hline).
    The rect is centered on the segment midpoint and rotated by the segment
    angle, so diagonals (scatter trend, line/combo polylines, BEP lines) work
    without connectors. For dashed lines, callers emit short segments.
    """
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length <= 0:
        return None
    angle = math.degrees(math.atan2(dy, dx))
    h_in = Pt(thickness_pt).inches
    cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(cx - length / 2.0), Inches(cy - h_in / 2.0),
        Inches(length), Inches(h_in),
    )
    shape.rotation = angle
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(color_hex)
    shape.line.fill.background()
    _clean_shape(shape)
    return shape


def add_polyline(slide, points, color_hex: str, *, thickness_pt: float = 2.0):
    """Draw a connected polyline through `points` [(x,y), ...] (inches) as a
    chain of add_line() segments. Used for line_chart / combo / overlapping."""
    out = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        seg = add_line(slide, x1, y1, x2, y2, color_hex, thickness_pt=thickness_pt)
        if seg is not None:
            out.append(seg)
    return out
