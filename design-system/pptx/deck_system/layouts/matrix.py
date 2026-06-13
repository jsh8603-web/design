"""Matrix layouts — swot, bcg_matrix, prioritization_matrix, risk_matrix.

All share a 2×2 (or 3×3) grid skeleton with axis labels + quadrant content.
Reference: likaku (swot, risk_matrix),
           seulee26 (bcg, prioritization).
"""
from __future__ import annotations
from typing import Optional

from pptx.enum.text import PP_ALIGN
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


def _grid_geom(layout):
    L = layout
    x = L.margin_left_in + 1.0  # leave space for Y-axis label
    y = L.content_top_in + 0.3
    w = L.content_width_in - 1.0
    h = L.bottom_bar_y_in - y - 0.6  # leave space for X-axis label
    return x, y, w, h


def _draw_axes(slide, theme, gx, gy, gw, gh, x_label, y_label):
    L, P, T = theme.layout, theme.palette, theme.typography
    # Y-axis label (vertical, on the left)
    tb = add_textbox(slide, L.margin_left_in - 0.2, gy + gh / 2 - 0.2,
                      1.0, 0.4)
    write_paragraph(tb.text_frame, y_label, theme=theme,
                     size=T.small_size, bold=True, color=P.gray_2)
    # X-axis label (below grid, centered)
    tb = add_textbox(slide, gx, gy + gh + 0.15, gw, 0.3)
    write_paragraph(tb.text_frame, x_label, theme=theme,
                     size=T.small_size, bold=True, color=P.gray_2,
                     align=PP_ALIGN.CENTER)


def _render_2x2_grid(slide, theme, x, y, w, h, quadrants, axis_labels=None):
    """Render a 2x2 grid with 4 quadrant cells.

    quadrants: [TL, TR, BL, BR]  — each {label, color?, headline?, bullets?}
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    cw = w / 2
    ch = h / 2
    positions = [(x, y), (x + cw, y), (x, y + ch), (x + cw, y + ch)]
    default_colors = [P.surface_inverse, P.accent, P.gray_2, P.gray_3]
    for i, (q, (qx, qy)) in enumerate(zip(quadrants, positions)):
        col = q.get("color")
        if col and not col.startswith("#"):
            col = getattr(P, col.replace("-", "_"), None)
        if not col:
            col = default_colors[i]
        add_rect(slide, qx, qy, cw, ch, col)
        # Label (small, top-left of cell)
        if q.get("label"):
            tb = add_textbox(slide, qx + 0.2, qy + 0.15, cw - 0.4, 0.4)
            write_paragraph(tb.text_frame, q["label"], theme=theme,
                             size=T.small_size, bold=True,
                             color=P.surface_inverse_fg
                                   if col in (P.surface_inverse, P.accent, P.gray_2)
                                   else P.gray_1)
        # Headline (medium, below label)
        if q.get("headline"):
            tb = add_textbox(slide, qx + 0.2, qy + 0.55, cw - 0.4, 0.7)
            write_paragraph(tb.text_frame, q["headline"], theme=theme,
                             size=T.sub_header_size, bold=True,
                             color=P.white, line_spacing=1.25)
        # Bullets
        y_cursor = qy + 0.55 + (0.7 if q.get("headline") else 0)
        for j, b in enumerate(q.get("bullets", [])[:4]):
            tb = add_textbox(slide, qx + 0.2, y_cursor + j * 0.4,
                              cw - 0.4, 0.4)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, "• ", theme=theme, size=T.body_size - 1,
                    color=P.white)
            r2 = p.add_run()
            set_run(r2, b, theme=theme, size=T.body_size - 1,
                    color=P.white)


@register("swot")
def swot(slide, spec, theme, *, page_num, total):
    """SWOT 2×2.  Strengths/Weaknesses/Opportunities/Threats.

    spec:
        strengths, weaknesses, opportunities, threats: each [str,...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    gx, gy, gw, gh = _grid_geom(L)
    quads = [
        {"label": "S · Strength", "color": P.positive,
         "bullets": spec.get("strengths", [])},
        {"label": "W · Weakness", "color": P.negative,
         "bullets": spec.get("weaknesses", [])},
        {"label": "O · Opportunity", "color": P.accent,
         "bullets": spec.get("opportunities", [])},
        {"label": "T · Threat", "color": P.surface_inverse,
         "bullets": spec.get("threats", [])},
    ]
    _render_2x2_grid(slide, theme, gx, gy, gw, gh, quads)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("bcg_matrix")
def bcg_matrix(slide, spec, theme, *, page_num, total):
    """BCG growth-share matrix.  Stars / Question marks / Cash cows / Dogs.

    spec:
        stars, question_marks, cash_cows, dogs: each [str,...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    gx, gy, gw, gh = _grid_geom(L)
    quads = [
        {"label": "★ Stars", "color": P.accent,
         "headline": spec.get("stars_headline", ""),
         "bullets": spec.get("stars", [])},
        {"label": "? Question Marks", "color": P.gray_2,
         "headline": spec.get("qm_headline", ""),
         "bullets": spec.get("question_marks", [])},
        {"label": "$ Cash Cows", "color": P.surface_inverse,
         "headline": spec.get("cc_headline", ""),
         "bullets": spec.get("cash_cows", [])},
        {"label": "× Dogs", "color": P.gray_3,
         "headline": spec.get("dogs_headline", ""),
         "bullets": spec.get("dogs", [])},
    ]
    _render_2x2_grid(slide, theme, gx, gy, gw, gh, quads)
    _draw_axes(slide, theme, gx, gy, gw, gh,
                spec.get("x_label", "← 시장 점유율 (Market Share)"),
                spec.get("y_label", "시장 성장률 ↑"))

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("prioritization_matrix")
def prioritization_matrix(slide, spec, theme, *, page_num, total):
    """Impact × Effort 2×2.  Quick wins / Major projects / Fill-ins / Hard slogs.

    spec:
        quick_wins, major_projects, fill_ins, hard_slogs: each [str,...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    gx, gy, gw, gh = _grid_geom(L)
    quads = [
        {"label": "Major Projects", "color": P.accent,
         "bullets": spec.get("major_projects", [])},
        {"label": "★ Quick Wins", "color": P.positive,
         "bullets": spec.get("quick_wins", [])},
        {"label": "Hard Slogs", "color": P.gray_3,
         "bullets": spec.get("hard_slogs", [])},
        {"label": "Fill-ins", "color": P.gray_2,
         "bullets": spec.get("fill_ins", [])},
    ]
    _render_2x2_grid(slide, theme, gx, gy, gw, gh, quads)
    _draw_axes(slide, theme, gx, gy, gw, gh,
                spec.get("x_label", "← 실행 난이도 (Effort)"),
                spec.get("y_label", "임팩트 (Impact) ↑"))

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("risk_matrix")
def risk_matrix(slide, spec, theme, *, page_num, total):
    """Likelihood × Impact 3×3 heat map with risk dots.

    spec:
        risks: [{label, likelihood: 1..3, impact: 1..3}, ...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    gx, gy, gw, gh = _grid_geom(L)
    cw = gw / 3
    ch = gh / 3
    # Heat colors per cell — light red top-right, light green bottom-left
    # Cells (row, col) with (0,0) top-left; risk = (3-row)*impact*col
    cells = [[None] * 3 for _ in range(3)]
    for r in range(3):  # row 0=top (highest likelihood)
        for c in range(3):  # col 0=left (lowest impact)
            score = (3 - r) + c  # 1..5
            if score >= 4:
                cells[r][c] = P.negative
            elif score == 3:
                cells[r][c] = P.gray_2
            else:
                cells[r][c] = P.positive

    for r in range(3):
        for c in range(3):
            add_rect(slide, gx + c * cw, gy + r * ch, cw, ch, cells[r][c])
            # Faint cell separator
    # Grid hairlines
    for i in range(1, 3):
        add_hline(slide, gx, gy + i * ch, gw, P.white, thickness_pt=0.5)
        # Vertical line via thin rect
        add_rect(slide, gx + i * cw - 0.005, gy, 0.01, gh, P.white)

    # Risk dots
    for risk in spec.get("risks", []):
        lk = max(1, min(3, int(risk.get("likelihood", 2))))
        im = max(1, min(3, int(risk.get("impact", 2))))
        # likelihood=3 → row 0 (top), likelihood=1 → row 2 (bottom)
        row = 3 - lk
        col = im - 1
        dx = gx + col * cw + cw / 2 - 0.15
        dy = gy + row * ch + ch / 2 - 0.15
        add_oval(slide, dx, dy, 0.3, 0.3, P.surface_inverse)
        if risk.get("label"):
            tb = add_textbox(slide, dx + 0.35, dy + 0.02, 2.0, 0.25)
            write_paragraph(tb.text_frame, risk["label"], theme=theme,
                             size=T.small_size - 1, bold=True,
                             color=P.surface_inverse_fg)

    _draw_axes(slide, theme, gx, gy, gw, gh,
                spec.get("x_label", "임팩트 (Impact) →"),
                spec.get("y_label", "발생 가능성 ↑"))

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
