"""V2.1 layouts ported from likaku — 9 high-impact FP&A layouts.

This module hosts layouts that didn't fit a single category cleanly OR
that I batched together for the V2.1 round.  Each function uses the
same calling convention as other layouts.

Layouts:
- table_insight (#71) — table left + insight panel right (McK opener)
- meet_the_team (#32) — team profile grid
- case_study (#33) — SAR sections + result box
- action_items (#34) — task list w/ owner / due / status
- timeline (#28) — simple horizontal milestones (≠ gantt)
- side_by_side (#19) — 2-option visual comparison
- four_column (#27) — McK 4-column overview (overflow rules enforced)
- stakeholder_map (#59) — influence × interest 2×2
- decision_tree (#60) — MECE diagnostic tree
"""
from __future__ import annotations
from typing import List, Optional

from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
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
from deck_system.qa.experiences import (
    MAX_FOUR_COL_DESC_CHARS, MAX_TIMELINE_LAST_LABEL_CHARS,
)


# ════════════════════════════════════════════════════════════════════
# TABLE INSIGHT (#71) — McKinsey signature opener
# Left: structured data table.  Right: gray-bg insight panel w/ chevron arrow.
# ════════════════════════════════════════════════════════════════════

@register("table_insight")
def table_insight(slide, spec, theme, *, page_num, total):
    """Opening analytical slide — table + insight panel.

    spec:
        headers: ["지표", "Q3", "Q4", "YoY"]
        rows: [["매출","1,065억","1,260억","+18.3%"], …]
        insights: ["북미 매출 가속화", "GMV가 매출 견인", …]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2

    # Left 60% = table, right 38% = insight panel, 2% gap
    table_w = L.content_width_in * 0.58
    panel_x = L.margin_left_in + table_w + 0.3
    panel_w = L.content_width_in - table_w - 0.3

    # ── Table ─────────────────────────────────────────────────────
    headers = spec.get("headers", [])
    rows = spec.get("rows", [])
    n_cols = max(len(headers), 1)
    col_w = table_w / n_cols
    header_h = 0.45
    row_h = min(0.5, (body_h - header_h) / max(len(rows), 1))

    add_rect(slide, L.margin_left_in, body_top, table_w, header_h, P.surface_inverse)
    for j, h in enumerate(headers):
        tb = add_textbox(slide, L.margin_left_in + j * col_w + 0.14,
                          body_top + 0.08, col_w - 0.28, header_h - 0.16)
        write_paragraph(tb.text_frame, h, theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.surface_inverse_fg,
                         align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)

    for i, row in enumerate(rows):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, L.margin_left_in, y, table_w, row_h, P.gray_4)
        for j, cell in enumerate(row):
            tb = add_textbox(slide, L.margin_left_in + j * col_w + 0.14,
                              y + 0.1, col_w - 0.28, row_h - 0.2)
            write_paragraph(tb.text_frame, str(cell), theme=theme,
                             size=T.body_size, bold=(j == 0),
                             color=P.gray_1,
                             align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
        add_hline(slide, L.margin_left_in, y + row_h - 0.01,
                   table_w, P.gray_4, thickness_pt=0.5)

    # ── Insight panel ─────────────────────────────────────────────
    add_rect(slide, panel_x, body_top, panel_w, body_h, P.gray_4)
    # Chevron arrow on left edge pointing into panel
    arrow_w = 0.2
    add_oval(slide, panel_x - arrow_w / 2, body_top + 0.4,
              arrow_w, arrow_w, P.accent)
    tb = add_textbox(slide, panel_x + 0.25, body_top + 0.3,
                      panel_w - 0.5, 0.4)
    write_paragraph(tb.text_frame, spec.get("insight_title", "Insight · 시사점"),
                     theme=theme, size=T.small_size - 1, bold=True,
                     color=P.primary)
    for i, ins in enumerate(spec.get("insights", [])):
        tb = add_textbox(slide, panel_x + 0.25,
                          body_top + 0.85 + i * 0.7,
                          panel_w - 0.5, 0.6)
        p = tb.text_frame.paragraphs[0]
        r1 = p.add_run()
        set_run(r1, "• ", theme=theme, size=T.body_size, color=P.accent)
        r2 = p.add_run()
        set_run(r2, ins, theme=theme, size=T.body_size,
                color=P.gray_1)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# MEET THE TEAM (#32)
# ════════════════════════════════════════════════════════════════════

@register("meet_the_team")
def meet_the_team(slide, spec, theme, *, page_num, total):
    """Team member profile grid.

    spec:
        members: [{name, role, responsibility?}, …] (max 8)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    members = spec.get("members", [])[:8]
    n = max(len(members), 1)
    # Layout: 4 cols × up to 2 rows
    cols = min(n, 4)
    rows = (n + cols - 1) // cols

    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    gap = 0.25
    tile_w = (L.content_width_in - gap * (cols - 1)) / cols
    tile_h = (body_h - gap * (rows - 1)) / rows

    for i, m in enumerate(members):
        r, c = divmod(i, cols)
        x = L.margin_left_in + c * (tile_w + gap)
        y = body_top + r * (tile_h + gap)
        add_rect(slide, x, y, tile_w, tile_h, P.gray_4)
        # Avatar circle (placeholder — surface_inverse oval w/ initial)
        av_size = 0.9
        add_oval(slide, x + tile_w / 2 - av_size / 2, y + 0.2,
                  av_size, av_size, P.surface_inverse)
        initial = (m.get("name", "?") or "?")[0]
        tb = add_textbox(slide, x, y + 0.4, tile_w, 0.5)
        write_paragraph(tb.text_frame, initial, theme=theme,
                         size=T.cover_title_size - 8, bold=True,
                         color=P.surface_inverse_fg,
                         align=PP_ALIGN.CENTER)
        # Name
        tb = add_textbox(slide, x + 0.15, y + 1.25,
                          tile_w - 0.3, 0.4)
        write_paragraph(tb.text_frame, m.get("name", ""), theme=theme,
                         size=T.body_size + 1, bold=True, color=P.gray_1,
                         align=PP_ALIGN.CENTER)
        # Role
        tb = add_textbox(slide, x + 0.15, y + 1.65,
                          tile_w - 0.3, 0.35)
        write_paragraph(tb.text_frame, m.get("role", ""), theme=theme,
                         size=T.body_size - 1, color=P.accent,
                         align=PP_ALIGN.CENTER)
        # Responsibility
        if m.get("responsibility"):
            tb = add_textbox(slide, x + 0.15, y + 2.05,
                              tile_w - 0.3, tile_h - 2.15)
            write_paragraph(tb.text_frame, m["responsibility"], theme=theme,
                             size=T.small_size, color=P.gray_2,
                             align=PP_ALIGN.CENTER, line_spacing=1.4)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# CASE STUDY (#33) — SAR (Situation/Approach/Result) sections + result box
# ════════════════════════════════════════════════════════════════════

@register("case_study")
def case_study(slide, spec, theme, *, page_num, total):
    """Case study slide w/ SAR sections + optional result callout.

    spec:
        sections: [{label, content}, …] (3-4 expected)
        result_box: {headline, supporting: [str,…]} (optional)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    sections = spec.get("sections", [])[:4]
    has_box = bool(spec.get("result_box"))

    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2
    if has_box:
        sec_w = L.content_width_in * 0.62
        box_x = L.margin_left_in + sec_w + 0.3
        box_w = L.content_width_in - sec_w - 0.3
    else:
        sec_w = L.content_width_in
        box_x = box_w = 0

    n = max(len(sections), 1)
    sec_h = body_h / n

    for i, sec in enumerate(sections):
        y = body_top + i * sec_h
        # Label (small caps, accent color)
        tb = add_textbox(slide, L.margin_left_in, y + 0.05, sec_w, 0.35)
        write_paragraph(tb.text_frame, sec.get("label", "").upper(), theme=theme,
                         size=T.small_size - 1, bold=True,
                         color=P.accent)
        # Content
        tb = add_textbox(slide, L.margin_left_in, y + 0.4,
                          sec_w, sec_h - 0.5)
        write_paragraph(tb.text_frame, sec.get("content", ""), theme=theme,
                         size=T.body_size, color=P.gray_1,
                         line_spacing=1.55)

    # Result box
    if has_box:
        rb = spec["result_box"]
        add_rect(slide, box_x, body_top, box_w, body_h, P.surface_inverse)
        tb = add_textbox(slide, box_x + 0.2, body_top + 0.2,
                          box_w - 0.4, 0.4)
        write_paragraph(tb.text_frame, "결과 · Result", theme=theme,
                         size=T.small_size - 1, bold=True,
                         color=P.surface_inverse_fg)
        tb = add_textbox(slide, box_x + 0.2, body_top + 0.6,
                          box_w - 0.4, 1.0)
        write_paragraph(tb.text_frame, rb.get("headline", ""), theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=P.surface_inverse_fg, line_spacing=1.3)
        for j, s in enumerate(rb.get("supporting", [])[:4]):
            tb = add_textbox(slide, box_x + 0.2, body_top + 1.8 + j * 0.5,
                              box_w - 0.4, 0.45)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, "• ", theme=theme, size=T.body_size - 1,
                    color=P.surface_inverse_fg)
            r2 = p.add_run()
            set_run(r2, s, theme=theme, size=T.body_size - 1,
                    color=P.surface_inverse_fg)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# ACTION ITEMS (#34)
# ════════════════════════════════════════════════════════════════════

@register("action_items")
def action_items(slide, spec, theme, *, page_num, total):
    """Action items table w/ owner / due / status.

    spec:
        actions: [{id?, title, owner?, due?, status?: 'in_progress'|'done'|'blocked'}, …]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    actions = spec.get("actions", [])
    body_top = L.content_top_in + 0.2
    body_w = L.content_width_in
    header_h = 0.45
    row_h = 0.6

    # Columns: ID 8%, Title 42%, Owner 15%, Due 15%, Status 20%
    cols = [
        ("ID", 0.08),
        ("Action", 0.42),
        ("Owner", 0.15),
        ("Due", 0.15),
        ("Status", 0.20),
    ]
    add_rect(slide, L.margin_left_in, body_top, body_w, header_h, P.surface_inverse)
    cursor = L.margin_left_in
    col_xs = []
    for name, w_ratio in cols:
        w = body_w * w_ratio
        col_xs.append((cursor, w))
        tb = add_textbox(slide, cursor + 0.14, body_top + 0.08,
                          w - 0.28, header_h - 0.16)
        write_paragraph(tb.text_frame, name, theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.surface_inverse_fg)
        cursor += w

    _STATUS_COLORS = {"done": "positive", "in_progress": "accent",
                       "blocked": "negative"}
    _STATUS_LABELS = {"done": "✓ 완료", "in_progress": "▷ 진행",
                       "blocked": "× 차단"}

    for i, a in enumerate(actions):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, L.margin_left_in, y, body_w, row_h, P.gray_4)
        # ID
        x, w = col_xs[0]
        tb = add_textbox(slide, x + 0.14, y + 0.15, w - 0.28, row_h - 0.3)
        write_paragraph(tb.text_frame, str(a.get("id", f"A{i+1}")),
                         theme=theme, size=T.body_size, bold=True,
                         color=P.accent)
        # Title
        x, w = col_xs[1]
        tb = add_textbox(slide, x + 0.14, y + 0.15, w - 0.28, row_h - 0.3)
        write_paragraph(tb.text_frame, a.get("title", ""), theme=theme,
                         size=T.body_size, color=P.gray_1)
        # Owner
        x, w = col_xs[2]
        tb = add_textbox(slide, x + 0.14, y + 0.15, w - 0.28, row_h - 0.3)
        write_paragraph(tb.text_frame, a.get("owner", ""), theme=theme,
                         size=T.body_size - 1, color=P.gray_2)
        # Due
        x, w = col_xs[3]
        tb = add_textbox(slide, x + 0.14, y + 0.15, w - 0.28, row_h - 0.3)
        write_paragraph(tb.text_frame, a.get("due", ""), theme=theme,
                         size=T.body_size - 1, color=P.gray_2)
        # Status
        x, w = col_xs[4]
        status = a.get("status", "in_progress")
        col_name = _STATUS_COLORS.get(status, "gray_2")
        col_hex = getattr(P, col_name, P.gray_2)
        tb = add_textbox(slide, x + 0.14, y + 0.15, w - 0.28, row_h - 0.3)
        write_paragraph(tb.text_frame, _STATUS_LABELS.get(status, status),
                         theme=theme, size=T.body_size - 1, bold=True,
                         color=col_hex)
        add_hline(slide, L.margin_left_in, y + row_h - 0.01,
                   body_w, P.gray_4, thickness_pt=0.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# TIMELINE (#28) — Simple horizontal milestone bar (≠ gantt)
# ════════════════════════════════════════════════════════════════════

@register("timeline")
def timeline(slide, spec, theme, *, page_num, total):
    """Horizontal milestone bar.  See experiences/overflow.md Exp 6:
    last milestone label should be ≤6 chars to avoid right-edge overflow.

    spec:
        milestones: [{date, label}, …]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    milestones = spec.get("milestones", [])
    n = max(len(milestones), 1)
    bar_y = L.content_top_in + 2.5
    bar_left = L.margin_left_in + 0.5
    bar_right = L.margin_left_in + L.content_width_in - 0.5
    bar_w = bar_right - bar_left

    # Main horizontal line
    add_hline(slide, bar_left, bar_y, bar_w, P.gray_3, thickness_pt=1.5)

    # Milestones
    for i, m in enumerate(milestones):
        x = bar_left + (bar_w * i / max(n - 1, 1)) if n > 1 else bar_left + bar_w / 2
        is_last = i == n - 1
        dot_size = 0.22
        add_oval(slide, x - dot_size / 2, bar_y - dot_size / 2 + 0.01,
                  dot_size, dot_size,
                  P.accent if not is_last else P.surface_inverse)
        # Date above
        tb = add_textbox(slide, x - 0.75, bar_y - 0.6, 1.5, 0.3)
        write_paragraph(tb.text_frame, m.get("date", ""), theme=theme,
                         size=T.small_size - 1, bold=True, color=P.accent,
                         align=PP_ALIGN.CENTER)
        # Label below
        label_text = m.get("label", "")
        # last label sanity per experiences/overflow.md Exp 6
        if is_last and len(label_text) > MAX_TIMELINE_LAST_LABEL_CHARS:
            label_text = label_text[:MAX_TIMELINE_LAST_LABEL_CHARS]
        tb = add_textbox(slide, x - 1.0, bar_y + 0.3, 2.0, 1.0)
        write_paragraph(tb.text_frame, label_text, theme=theme,
                         size=T.body_size, bold=(is_last), color=P.gray_1,
                         align=PP_ALIGN.CENTER, line_spacing=1.3)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# SIDE BY SIDE (#19) — Two options w/ bullets + KPIs each
# ════════════════════════════════════════════════════════════════════

@register("side_by_side")
def side_by_side(slide, spec, theme, *, page_num, total):
    """Two-option comparison.

    spec:
        options: [{label, bullets: [str,…], kpis?: {key: value, …}}, {…}]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    options = spec.get("options", [])[:2]
    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2
    gap = 0.4
    col_w = (L.content_width_in - gap) / 2

    for i, opt in enumerate(options):
        x = L.margin_left_in + i * (col_w + gap)
        # Header strip
        head_color = P.surface_inverse if i == 0 else P.accent
        add_rect(slide, x, body_top, col_w, 0.55, head_color)
        tb = add_textbox(slide, x + 0.2, body_top + 0.13,
                          col_w - 0.4, 0.35)
        write_paragraph(tb.text_frame, opt.get("label", f"Option {i+1}"),
                         theme=theme, size=T.sub_header_size, bold=True,
                         color=P.surface_inverse_fg if i == 0 else P.white)
        # Bullets
        bullets_top = body_top + 0.75
        for j, b in enumerate(opt.get("bullets", [])):
            tb = add_textbox(slide, x, bullets_top + j * 0.5, col_w, 0.45)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, "• ", theme=theme, size=T.body_size,
                    color=head_color)
            r2 = p.add_run()
            set_run(r2, b, theme=theme, size=T.body_size,
                    color=P.gray_1)
        # KPIs at bottom
        kpis = opt.get("kpis", {})
        if kpis:
            kpi_box_y = body_top + body_h - 1.6
            add_rect(slide, x, kpi_box_y, col_w, 1.4, P.gray_4)
            n_kpis = min(len(kpis), 3)
            kpi_w = (col_w - 0.4) / max(n_kpis, 1)
            for j, (k, v) in enumerate(list(kpis.items())[:3]):
                kx = x + 0.2 + j * kpi_w
                tb = add_textbox(slide, kx, kpi_box_y + 0.15, kpi_w, 0.35)
                write_paragraph(tb.text_frame, k, theme=theme,
                                 size=T.small_size - 1, color=P.gray_2,
                                 align=PP_ALIGN.LEFT)
                tb = add_textbox(slide, kx, kpi_box_y + 0.55, kpi_w, 0.7)
                write_paragraph(tb.text_frame, str(v), theme=theme,
                                 size=T.sub_header_size, bold=True,
                                 color=P.gray_1, align=PP_ALIGN.LEFT)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# FOUR COLUMN (#27) — McK 4-column overview
# Enforces overflow.md Exp 2 (desc ≤120) and Exp 5 (3-tuple items)
# ════════════════════════════════════════════════════════════════════

@register("four_column")
def four_column(slide, spec, theme, *, page_num, total):
    """4-column overview.  Items can be tuples (num, title, desc) OR dicts.

    spec:
        items: [["1","북미","desc"], …]  OR  [{num,title,desc}, …]   (≤4)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = spec.get("items", [])[:4]
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    gap = 0.25
    col_w = (L.content_width_in - gap * 3) / 4

    for i, it in enumerate(items):
        # Normalize tuple/list → dict
        if isinstance(it, (list, tuple)):
            num = it[0] if len(it) > 0 else f"{i+1:02d}"
            title = it[1] if len(it) > 1 else ""
            desc = it[2] if len(it) > 2 else ""
        else:
            num = it.get("num", f"{i+1:02d}")
            title = it.get("title", "")
            desc = it.get("desc", "")
        # Enforce desc length (experiences/overflow.md Exp 2)
        if len(desc) > MAX_FOUR_COL_DESC_CHARS:
            desc = desc[:MAX_FOUR_COL_DESC_CHARS - 1] + "…"

        x = L.margin_left_in + i * (col_w + gap)
        # Number circle on top
        circle_size = 0.7
        add_oval(slide, x + col_w / 2 - circle_size / 2, body_top,
                  circle_size, circle_size, P.surface_inverse)
        tb = add_textbox(slide, x, body_top + 0.15, col_w, 0.4)
        write_paragraph(tb.text_frame, str(num), theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)
        # Title
        tb = add_textbox(slide, x + 0.1, body_top + circle_size + 0.15,
                          col_w - 0.2, 0.6)
        write_paragraph(tb.text_frame, title, theme=theme,
                         size=T.sub_header_size, bold=True, color=P.gray_1,
                         align=PP_ALIGN.CENTER, line_spacing=1.2)
        # Underline accent
        add_hline(slide,
                   x + col_w / 2 - 0.3,
                   body_top + circle_size + 0.95,
                   0.6, P.accent, thickness_pt=2)
        # Desc
        tb = add_textbox(slide, x + 0.1,
                          body_top + circle_size + 1.15,
                          col_w - 0.2,
                          body_h - circle_size - 1.2)
        write_paragraph(tb.text_frame, desc, theme=theme,
                         size=T.body_size, color=P.gray_2,
                         align=PP_ALIGN.CENTER, line_spacing=1.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# STAKEHOLDER MAP (#59) — Influence × Interest 2×2
# ════════════════════════════════════════════════════════════════════

@register("stakeholder_map")
def stakeholder_map(slide, spec, theme, *, page_num, total):
    """Stakeholder mapping w/ influence × interest grid.

    spec:
        stakeholders: [{label, influence: 1..3, interest: 1..3,
                         action?}] — placed as dots in quadrants
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.4
    body_h = L.bottom_bar_y_in - body_top - 0.6
    grid_x = L.margin_left_in + 1.0
    grid_w = L.content_width_in - 1.0 - 3.5   # room for action panel on right
    grid_h = body_h
    cw = grid_w / 2
    ch = grid_h / 2

    # Quadrant labels in light tones
    QUAD_LABELS = [
        ("키 플레이어\n(높은 영향·관심)", P.negative),         # top-right
        ("적극 관리\n(높은 영향·낮은 관심)", P.accent),         # top-left
        ("정보 제공\n(낮은 영향·높은 관심)", P.positive),        # bottom-right
        ("모니터링만\n(낮은 영향·낮은 관심)", P.gray_2),         # bottom-left
    ]
    # Draw 4 quadrants (light bg)
    for r in range(2):
        for c in range(2):
            qx = grid_x + c * cw
            qy = body_top + r * ch
            # Subtle tint
            # We use surface_inverse with alpha would be ideal; pptx has no alpha
            # for fill, so use gray_4 with quadrant label
            add_rect(slide, qx, qy, cw, ch, P.gray_4)
    # Grid lines
    add_hline(slide, grid_x, body_top + ch, grid_w, P.gray_3, thickness_pt=0.75)
    add_rect(slide, grid_x + cw - 0.005, body_top, 0.01, grid_h, P.gray_3)

    # Quadrant headers
    quad_positions = [
        (grid_x + cw, body_top),               # top-right
        (grid_x, body_top),                    # top-left
        (grid_x + cw, body_top + ch),          # bottom-right
        (grid_x, body_top + ch),               # bottom-left
    ]
    for (qx, qy), (label, color) in zip(quad_positions, QUAD_LABELS):
        tb = add_textbox(slide, qx + 0.15, qy + 0.1,
                          cw - 0.3, 0.55)
        write_paragraph(tb.text_frame, label.split("\n")[0], theme=theme,
                         size=T.small_size, bold=True, color=color,
                         line_spacing=1.2)

    # Axis labels
    tb = add_textbox(slide, grid_x - 0.7, body_top + grid_h / 2 - 0.2,
                      0.6, 0.4)
    write_paragraph(tb.text_frame, "영향력 →", theme=theme,
                     size=T.small_size - 1, bold=True, color=P.gray_2)
    tb = add_textbox(slide, grid_x + grid_w / 2 - 0.6,
                      body_top + grid_h + 0.05, 1.5, 0.3)
    write_paragraph(tb.text_frame, "관심도 →", theme=theme,
                     size=T.small_size - 1, bold=True, color=P.gray_2,
                     align=PP_ALIGN.CENTER)

    # Stakeholders as dots
    stakeholders = spec.get("stakeholders", [])
    for sh in stakeholders:
        inf = max(1, min(3, int(sh.get("influence", 2))))
        ints = max(1, min(3, int(sh.get("interest", 2))))
        # influence: 1=bottom, 3=top   interest: 1=left, 3=right
        sx = grid_x + (ints / 3) * grid_w - 0.15
        sy = body_top + (1 - inf / 3) * grid_h + 0.05
        add_oval(slide, sx, sy, 0.3, 0.3, P.surface_inverse)
        if sh.get("label"):
            tb = add_textbox(slide, sx + 0.35, sy + 0.02,
                              2.5, 0.3)
            write_paragraph(tb.text_frame, sh["label"], theme=theme,
                             size=T.small_size, bold=True, color=P.gray_1)

    # Action panel on right
    panel_x = grid_x + grid_w + 0.3
    panel_w = L.margin_left_in + L.content_width_in - panel_x
    add_rect(slide, panel_x, body_top, panel_w, body_h, P.surface_inverse)
    tb = add_textbox(slide, panel_x + 0.2, body_top + 0.2,
                      panel_w - 0.4, 0.4)
    write_paragraph(tb.text_frame, "관리 전략", theme=theme,
                     size=T.small_size - 1, bold=True,
                     color=P.surface_inverse_fg)
    for i, sh in enumerate(stakeholders[:6]):
        if sh.get("action"):
            tb = add_textbox(slide, panel_x + 0.2,
                              body_top + 0.7 + i * 0.5,
                              panel_w - 0.4, 0.45)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, f"{sh.get('label', '?')[:6]}: ",
                    theme=theme, size=T.small_size, bold=True,
                    color=P.surface_inverse_fg)
            r2 = p.add_run()
            set_run(r2, sh["action"], theme=theme, size=T.small_size,
                    color=P.surface_inverse_fg)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# DECISION TREE (#60) — MECE diagnostic w/ branches
# ════════════════════════════════════════════════════════════════════

@register("decision_tree")
def decision_tree(slide, spec, theme, *, page_num, total):
    """Decision tree w/ root → branches.  Simple 2-3 branch flat layout.

    spec:
        root: "..." (root question)
        branches: [{condition, outcome?, sub?: [{...}, ...]}, …]
        right_panel: "..." (optional recommendation)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2

    has_panel = bool(spec.get("right_panel"))
    if has_panel:
        tree_w = L.content_width_in * 0.65
        panel_x = L.margin_left_in + tree_w + 0.3
        panel_w = L.content_width_in - tree_w - 0.3
    else:
        tree_w = L.content_width_in
        panel_x = panel_w = 0

    # Root node — top of tree
    root_w = 3.2
    root_h = 0.8
    root_x = L.margin_left_in + (tree_w - root_w) / 2
    root_y = body_top + 0.2
    add_rect(slide, root_x, root_y, root_w, root_h, P.surface_inverse)
    tb = add_textbox(slide, root_x + 0.15, root_y + 0.18,
                      root_w - 0.3, root_h - 0.3)
    write_paragraph(tb.text_frame, spec.get("root", ""), theme=theme,
                     size=T.body_size, bold=True,
                     color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)

    # Branches — laid out evenly below root
    branches = spec.get("branches", [])[:3]
    n = max(len(branches), 1)
    br_top = root_y + root_h + 1.0
    br_w = min(2.8, (tree_w - 0.6) / n)
    spacing = tree_w / n

    # Connector trunk (vertical from root bottom)
    trunk_x = root_x + root_w / 2
    trunk_top = root_y + root_h
    trunk_y2 = br_top - 0.4
    add_rect(slide, trunk_x - 0.005, trunk_top, 0.01, trunk_y2 - trunk_top, P.gray_3)
    # Horizontal trunk if >1 branch
    if n > 1:
        first_x = L.margin_left_in + 0 * spacing + spacing / 2
        last_x = L.margin_left_in + (n - 1) * spacing + spacing / 2
        add_hline(slide, first_x, trunk_y2, last_x - first_x,
                   P.gray_3, thickness_pt=0.5)

    for i, br in enumerate(branches):
        bx_center = L.margin_left_in + i * spacing + spacing / 2
        bx = bx_center - br_w / 2
        # Connector down to branch
        add_rect(slide, bx_center - 0.005, trunk_y2,
                  0.01, br_top - trunk_y2, P.gray_3)
        # Condition label (small accent text above branch)
        tb = add_textbox(slide, bx, br_top - 0.3, br_w, 0.25)
        write_paragraph(tb.text_frame, br.get("condition", ""),
                         theme=theme, size=T.small_size - 1, bold=True,
                         color=P.accent, align=PP_ALIGN.CENTER)
        # Branch box
        add_rect(slide, bx, br_top, br_w, 0.7, P.gray_4)
        tb = add_textbox(slide, bx + 0.15, br_top + 0.15,
                          br_w - 0.3, 0.5)
        write_paragraph(tb.text_frame, br.get("outcome", br.get("condition", "")),
                         theme=theme, size=T.body_size - 1, bold=True,
                         color=P.gray_1, align=PP_ALIGN.CENTER, line_spacing=1.2)
        # Sub-leaves
        subs = br.get("sub", []) or br.get("subtree", [])
        for j, sub in enumerate(subs[:3]):
            sub_y = br_top + 1.0 + j * 0.5
            tb = add_textbox(slide, bx, sub_y, br_w, 0.4)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, "• ", theme=theme, size=T.body_size - 1,
                    color=P.accent)
            r2 = p.add_run()
            sub_text = sub if isinstance(sub, str) else sub.get("label", "")
            set_run(r2, sub_text, theme=theme, size=T.body_size - 1,
                    color=P.gray_1)

    # Right panel
    if has_panel:
        add_rect(slide, panel_x, body_top, panel_w, body_h, P.surface_inverse)
        tb = add_textbox(slide, panel_x + 0.2, body_top + 0.2,
                          panel_w - 0.4, 0.4)
        write_paragraph(tb.text_frame, "권고 · Recommendation",
                         theme=theme, size=T.small_size - 1, bold=True,
                         color=P.surface_inverse_fg)
        tb = add_textbox(slide, panel_x + 0.2, body_top + 0.7,
                          panel_w - 0.4, body_h - 0.9)
        write_paragraph(tb.text_frame, spec["right_panel"], theme=theme,
                         size=T.body_size, color=P.surface_inverse_fg,
                         line_spacing=1.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
