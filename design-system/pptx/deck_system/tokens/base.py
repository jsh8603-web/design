"""Token dataclasses — synchronized with HTML deck system v2.2.

Each Theme bundles a Palette (colors), Typography (font stacks + sizes),
and Layout (slide grid + margin tokens).  All values match HTML's
`colors_and_type.css` exactly so HTML and .pptx outputs are visually 1:1.
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional

from pptx.dml.color import RGBColor


def hex_to_rgb(hex_str: str) -> RGBColor:
    """'#1A2332' or '1A2332' → RGBColor."""
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


@dataclass(frozen=True)
class Palette:
    """Color tokens — hex strings, NOT RGBColor.  Convert at draw time.

    The hex strings allow easy diffing against HTML's CSS variables;
    the helpers convert to python-pptx RGBColor only when applying.
    """
    primary: str
    accent: str
    positive: str
    negative: str
    gray_1: str
    gray_2: str
    gray_3: str
    gray_4: str
    white: str
    black: str

    # Semantic tokens — dark-mode safety.  In light themes these mirror
    # primary/white; in dark theme they diverge so full-bleed slides
    # stay visible (primary collapses into bg in dark mode).
    surface_inverse: str          # cover, section_divider, dark_navy_summary, closing
    surface_inverse_fg: str       # text on surface_inverse


@dataclass(frozen=True)
class Typography:
    family_kr: str = "Pretendard"
    family_en: str = "Pretendard"
    family_ea: str = "Pretendard"   # East Asian font — CRITICAL for Korean rendering

    # ── Type scale (pt) ────────────────────────────────────────────────
    # v0.3.3 Tier classification rule v2 — semantics × density decides tier
    #
    # Core principle: content semantics is the primary tier decider.
    # "I want it to look smaller" is NOT a valid reason to downgrade.
    # Card/column density is the secondary decider (4-col card body can
    # drop one tier vs 3-col).  Use weight + color + layout for hierarchy,
    # not just size.
    #
    # Tier mapping:
    #   action         22pt  — slide-level conclusion title
    #   sub_header     18pt  — card heading, section title
    #   body           17pt  — primary body, paragraphs (slide default)
    #   body_compact   16pt  — card body in 3+ column dense grids
    #   small          15pt  — captions, short meta values, card sub-labels
    #   chart_label    10pt  — mono labels, chart axes, category tags
    #   footer          9pt  — source attribution, page number ONLY
    #
    # FORBIDDEN:
    #   - body content rendered at chart_label or footer tier
    #   - any slide body content under 12pt (footer reserved for source/page only)
    #   - size demotion as hierarchy retreat — use weight/color instead
    cover_title_size: int = 44
    section_title_size: int = 28
    subtitle_size: int = 24
    action_title_size: int = 22
    sub_header_size: int = 18
    emphasis_size: int = 16
    body_size: int = 17               # primary body (was 14, +3)
    body_compact_size: int = 16       # NEW v0.3.3 — dense card body, 3+ col
    small_size: int = 15              # captions, meta (was 12, +3)
    footer_size: int = 9              # source + page number ONLY
    chart_label_size: int = 10        # mono labels, axes only


@dataclass(frozen=True)
class Layout:
    # 16:9 slide — 1280×720 px design grid; python-pptx wants inches
    slide_width_in: float = 13.333
    slide_height_in: float = 7.5

    margin_left_in: float = 0.8
    margin_right_in: float = 0.8
    content_width_in: float = 11.733   # slide_width − 2×margin

    title_top_in: float = 0.15
    title_height_in: float = 0.9
    title_line_y_in: float = 1.05      # 2pt black rule under action title
    content_top_in: float = 1.3
    source_y_in: float = 7.05
    page_num_x_in: float = 12.2
    bottom_bar_y_in: float = 6.2
    bottom_bar_h_in: float = 0.65


@dataclass(frozen=True)
class Theme:
    palette: Palette
    typography: Typography = field(default_factory=Typography)
    layout: Layout = field(default_factory=Layout)
    copyright_text: str = ""

    def variant(self, **kwargs) -> "Theme":
        """Build a derived theme — e.g. company-branded subclass."""
        return replace(self, **kwargs)
