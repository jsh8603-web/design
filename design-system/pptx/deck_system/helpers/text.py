"""Text helpers — runs, paragraphs, East Asian font enforcement.

Korean rendering critical-path: every run that contains CJK characters
MUST have its `<a:ea>` element set to a Korean-capable font, otherwise
PowerPoint will fall back to Gulim/SimSun.  `set_ea_font()` does this,
and `set_run()` calls it by default.

Reference: likaku/experiences/cjk-issues.md
"""
from __future__ import annotations
from typing import Optional

from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt

from deck_system.tokens.base import Theme, hex_to_rgb


def set_ea_font(run, typeface: str) -> None:
    """Set the East Asian font on a run.

    python-pptx doesn't expose this directly — patch the XML.
    Without it, Korean/CJK characters render in the OS default
    (Gulim, SimSun, etc), breaking visual parity with the HTML system.

    Reference: likaku/experiences/cjk-issues.md Experience 001
    """
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {"typeface": typeface})
        rPr.append(ea)
    else:
        ea.set("typeface", typeface)


def set_run(
    run,
    text: str,
    *,
    theme: Theme,
    size: Optional[int] = None,
    bold: bool = False,
    color: Optional[str] = None,
    family: Optional[str] = None,
    ea_font: bool = True,
) -> None:
    """Set a run's text + formatting in one call.

    `size` is points (int).  `color` is a hex string from the theme palette.
    `ea_font=True` (default) installs the EA font for CJK safety.
    """
    run.text = text
    font = run.font
    if family is not None:
        font.name = family
    else:
        font.name = theme.typography.family_en
    if size is not None:
        font.size = Pt(size)
    if bold:
        font.bold = True
    if color is not None:
        font.color.rgb = hex_to_rgb(color)
    if ea_font:
        set_ea_font(run, theme.typography.family_ea)


def write_paragraph(
    tf,
    text: str,
    *,
    theme: Theme,
    size: int,
    bold: bool = False,
    color: Optional[str] = None,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    line_spacing: Optional[float] = None,
) -> None:
    """Replace the first paragraph of a text frame with one run.

    For multi-line text use add_paragraph() repeatedly with this signature.
    Korean default line-spacing is 1.4 (HTML system uses lh-normal=1.45).
    """
    p = tf.paragraphs[0] if tf.paragraphs else tf.add_paragraph()
    p.alignment = align
    if line_spacing is not None:
        p.line_spacing = line_spacing
    # Clear any existing runs
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    run = p.add_run()
    set_run(run, text, theme=theme, size=size, bold=bold, color=color)
