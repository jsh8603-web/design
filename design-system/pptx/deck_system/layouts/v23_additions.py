"""V2.3-A additions — 8 FP&A-relevant layouts from likaku catalog.

Tier 1 (weekly):
  scorecard          (#12 data_table) — KPI evaluation w/ scoring
  checklist          (#61 data_table) — task completion tracker
  temple             (#18 matrix)     — roof-pillar-foundation framework
  pie                (#64 data)       — simple part-of-whole (≠ donut)
  appendix_title     (structure)      — appendix marker

Tier 2 (monthly):
  three_images       (#42 image)      — 3-image + caption row
  two_col_image_grid (#68 image)      — 2×2 image+text grid
  metric_comparison  (#62 narrative)  — before/after delta cards

All use surface_inverse for full-bleed; CJK routing via set_run().
Image layouts use image_placeholder (engine does not embed images).
"""
from __future__ import annotations
from typing import List, Optional

from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from deck_system.builder.registry import register
from deck_system.helpers.shapes import (
    add_rect, add_oval, add_textbox, add_hline, _clean_shape, add_block_arc,
)
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)
from deck_system.helpers.image_placeholder import add_image_placeholder
from deck_system.tokens.base import hex_to_rgb


# ════════════════════════════════════════════════════════════════════
# SCORECARD (#12) — KPI evaluation w/ scoring (5-point or RAG)
# ════════════════════════════════════════════════════════════════════

@register("scorecard")
def scorecard(slide, spec, theme, *, page_num, total):
    """Multi-dimension scoring table.

    spec:
        items: [{label, score: 1..5 OR 'red'|'amber'|'green', note?}, ...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = spec.get("items", [])[:10]
    body_top = L.content_top_in + 0.3
    body_w = L.content_width_in
    header_h = 0.45
    row_h = 0.5

    cols = [("항목", 0.45), ("점수", 0.25), ("비고", 0.30)]
    add_rect(slide, L.margin_left_in, body_top, body_w, header_h, P.surface_inverse)
    cursor = L.margin_left_in
    col_xs = []
    for name, ratio in cols:
        w = body_w * ratio
        col_xs.append((cursor, w))
        tb = add_textbox(slide, cursor + 0.14, body_top + 0.08,
                          w - 0.28, header_h - 0.16)
        write_paragraph(tb.text_frame, name, theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.surface_inverse_fg)
        cursor += w

    for i, it in enumerate(items):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, L.margin_left_in, y, body_w, row_h, P.gray_4)
        x, w = col_xs[0]
        tb = add_textbox(slide, x + 0.14, y + 0.1, w - 0.28, row_h - 0.2)
        write_paragraph(tb.text_frame, it.get("label", ""), theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1)
        # Score column — dots for 1-5 OR colored chip for RAG
        x, w = col_xs[1]
        score = it.get("score", 0)
        if isinstance(score, str):
            col = {"green":"positive","amber":"#F4C57A","red":"negative",
                    "g":"positive","a":"#F4C57A","r":"negative"}.get(score.lower(), "gray_2")
            col_hex = getattr(P, col, col) if not col.startswith("#") else col
            add_oval(slide, x + w/2 - 0.13, y + row_h/2 - 0.13, 0.26, 0.26, col_hex)
        else:
            # 5-dot bar
            n = max(0, min(5, int(score)))
            dot_w = 0.22; gap = 0.06
            total_w = 5 * dot_w + 4 * gap
            sx = x + w/2 - total_w/2
            for d in range(5):
                fill = P.surface_inverse if d < n else P.gray_4
                add_oval(slide, sx + d * (dot_w + gap), y + row_h/2 - dot_w/2,
                          dot_w, dot_w, fill)
        x, w = col_xs[2]
        tb = add_textbox(slide, x + 0.14, y + 0.1, w - 0.28, row_h - 0.2)
        write_paragraph(tb.text_frame, it.get("note", ""), theme=theme,
                         size=T.body_size - 1, color=P.gray_2)
        add_hline(slide, L.margin_left_in, y + row_h - 0.01,
                   body_w, P.gray_4, thickness_pt=0.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# CHECKLIST (#61) — task completion w/ ✓/✗
# ════════════════════════════════════════════════════════════════════

@register("checklist")
def checklist(slide, spec, theme, *, page_num, total):
    """Task checklist w/ status markers.

    spec:
        rows: [{label, done: bool, note?}, ...] (max 7)
        progress_label: "..." (optional headline)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    rows = spec.get("rows", [])[:7]
    body_top = L.content_top_in + 0.4
    if spec.get("progress_label"):
        tb = add_textbox(slide, L.margin_left_in, body_top,
                          L.content_width_in, 0.4)
        write_paragraph(tb.text_frame, spec["progress_label"], theme=theme,
                         size=T.sub_header_size, bold=True, color=P.primary)
        body_top += 0.55

    body_h = L.bottom_bar_y_in - body_top - 0.3
    row_h = min(0.65, body_h / max(len(rows), 1))

    for i, row in enumerate(rows):
        y = body_top + i * row_h
        done = bool(row.get("done", False))
        # Status icon
        icon_color = P.positive if done else P.gray_3
        add_oval(slide, L.margin_left_in, y + 0.1, 0.4, 0.4, icon_color)
        tb = add_textbox(slide, L.margin_left_in, y + 0.13, 0.4, 0.35)
        write_paragraph(tb.text_frame, "✓" if done else "·", theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=P.white, align=PP_ALIGN.CENTER)
        # Label
        tb = add_textbox(slide, L.margin_left_in + 0.55, y + 0.05,
                          L.content_width_in * 0.55, row_h - 0.1)
        write_paragraph(tb.text_frame, row.get("label", ""), theme=theme,
                         size=T.body_size,
                         bold=done, color=P.gray_1 if done else P.gray_2)
        # Note
        if row.get("note"):
            tb = add_textbox(slide,
                              L.margin_left_in + L.content_width_in * 0.62,
                              y + 0.05,
                              L.content_width_in * 0.38, row_h - 0.1)
            write_paragraph(tb.text_frame, row["note"], theme=theme,
                             size=T.small_size, color=P.gray_2)
        add_hline(slide, L.margin_left_in, y + row_h - 0.01,
                   L.content_width_in, P.gray_4, thickness_pt=0.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# TEMPLE (#18) — Roof + pillars + foundation
# ════════════════════════════════════════════════════════════════════

@register("temple")
def temple(slide, spec, theme, *, page_num, total):
    """Strategic framework w/ roof (vision) + pillars + foundation.

    spec:
        roof: "..." (vision/goal at top)
        pillars: [{label, bullets?}, ...] (3-5)
        foundation: "..." (enablers/principles at bottom)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3

    roof_h = 0.7
    foundation_h = 0.7
    pillar_h = body_h - roof_h - foundation_h - 0.3

    # Roof
    add_rect(slide, L.margin_left_in, body_top,
              L.content_width_in, roof_h, P.surface_inverse)
    tb = add_textbox(slide, L.margin_left_in + 0.2, body_top + 0.18,
                      L.content_width_in - 0.4, roof_h - 0.3)
    write_paragraph(tb.text_frame, spec.get("roof", ""), theme=theme,
                     size=T.sub_header_size, bold=True,
                     color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)
    # Pillars
    pillars = spec.get("pillars", [])[:5]
    n = max(len(pillars), 1)
    pillar_top = body_top + roof_h + 0.15
    gap = 0.2
    pillar_w = (L.content_width_in - gap * (n - 1)) / n
    for i, p in enumerate(pillars):
        x = L.margin_left_in + i * (pillar_w + gap)
        add_rect(slide, x, pillar_top, pillar_w, pillar_h, P.gray_4)
        # Pillar header band
        add_rect(slide, x, pillar_top, pillar_w, 0.45, P.accent)
        tb = add_textbox(slide, x + 0.15, pillar_top + 0.08,
                          pillar_w - 0.3, 0.3)
        write_paragraph(tb.text_frame, p.get("label", ""), theme=theme,
                         size=T.body_size, bold=True, color=P.white,
                         align=PP_ALIGN.CENTER)
        for j, b in enumerate(p.get("bullets", [])[:5]):
            tb = add_textbox(slide, x + 0.15,
                              pillar_top + 0.6 + j * 0.4,
                              pillar_w - 0.3, 0.35)
            para = tb.text_frame.paragraphs[0]
            r1 = para.add_run()
            set_run(r1, "• ", theme=theme,
                    size=T.body_size - 1, color=P.accent)
            r2 = para.add_run()
            set_run(r2, b, theme=theme,
                    size=T.body_size - 1, color=P.gray_1)

    # Foundation
    fnd_top = pillar_top + pillar_h + 0.15
    add_rect(slide, L.margin_left_in, fnd_top,
              L.content_width_in, foundation_h, P.gray_4)
    tb = add_textbox(slide, L.margin_left_in + 0.2, fnd_top + 0.15,
                      L.content_width_in - 0.4, foundation_h - 0.3)
    write_paragraph(tb.text_frame, spec.get("foundation", ""), theme=theme,
                     size=T.body_size, bold=True, color=P.gray_1,
                     align=PP_ALIGN.CENTER)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# PIE (#64) — Simple part-of-whole (≠ donut, no center hole)
# ════════════════════════════════════════════════════════════════════

@register("pie")
def pie(slide, spec, theme, *, page_num, total):
    """Simple pie chart.

    spec:
        segments: [{label, value, color?}, ...] (≤6)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    segs = [s for s in spec.get("segments", []) if s.get("value", 0) > 0][:6]
    total_v = sum(s["value"] for s in segs) or 1

    body_top = L.content_top_in + 0.3
    size = 4.0
    pie_x = L.margin_left_in + 0.5
    pie_y = body_top + 0.3

    palette_order = ["surface_inverse", "accent", "gray_2",
                      "gray_3", "positive", "negative"]
    # Pie segments — BLOCK_ARC w/ inner radius = 0 not exposed; use filled wedges via BLOCK_ARC
    cur = 0
    legend_x = pie_x + size + 0.6
    legend_w = L.content_width_in - size - 1.0
    for i, s in enumerate(segs):
        sweep = (s["value"] / total_v) * 360
        # BLOCK_ARC at 3 o'clock = 0°, start angle in degrees clockwise
        start_deg = (cur - 90) % 360
        end_deg = (cur + sweep - 90) % 360
        col_name = s.get("color")
        if col_name and not col_name.startswith("#"):
            col = getattr(P, col_name.replace("-", "_"), None) or P.surface_inverse
        elif col_name:
            col = col_name
        else:
            col = getattr(P, palette_order[i % len(palette_order)])
        add_block_arc(slide, pie_x, pie_y, size, col, start_deg, end_deg)
        # Legend row
        ly = body_top + 0.4 + i * 0.55
        add_rect(slide, legend_x, ly + 0.05, 0.25, 0.25, col)
        pct = (s["value"] / total_v) * 100
        tb = add_textbox(slide, legend_x + 0.4, ly, legend_w - 0.5, 0.3)
        para = tb.text_frame.paragraphs[0]
        r1 = para.add_run()
        set_run(r1, s.get("label", ""), theme=theme,
                size=T.body_size, bold=True, color=P.gray_1)
        r2 = para.add_run()
        set_run(r2, f"   {pct:.0f}%", theme=theme,
                size=T.body_size, color=P.gray_2)
        cur += sweep

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# APPENDIX_TITLE — back-matter separator (variant of section_divider)
# ════════════════════════════════════════════════════════════════════

@register("appendix_title")
def appendix_title(slide, spec, theme, *, page_num, total):
    """Appendix marker.  Full-bleed surface_inverse + 'APPENDIX' label.

    spec:
        title: "..."   subtitle?: "..."   note?: "..."
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_rect(slide, 0, 0, L.slide_width_in, L.slide_height_in,
              P.surface_inverse)

    tb = add_textbox(slide, 0.8, 1.5,
                      L.content_width_in, 0.5)
    write_paragraph(tb.text_frame, spec.get("label", "APPENDIX"),
                     theme=theme, size=T.body_size, bold=True,
                     color=P.surface_inverse_fg)
    tb = add_textbox(slide, 0.8, 2.5,
                      L.content_width_in, 1.5)
    write_paragraph(tb.text_frame, spec.get("title", "부록"),
                     theme=theme, size=T.cover_title_size, bold=True,
                     color=P.surface_inverse_fg)
    if spec.get("subtitle"):
        tb = add_textbox(slide, 0.8, 4.2,
                          L.content_width_in, 0.6)
        write_paragraph(tb.text_frame, spec["subtitle"], theme=theme,
                         size=T.section_title_size,
                         color=P.surface_inverse_fg)
    if spec.get("note"):
        tb = add_textbox(slide, 0.8, L.slide_height_in - 1.0,
                          L.content_width_in, 0.5)
        write_paragraph(tb.text_frame, spec["note"], theme=theme,
                         size=T.body_size, color=P.surface_inverse_fg)


# ════════════════════════════════════════════════════════════════════
# THREE_IMAGES (#42) — 3-image row + captions
# ════════════════════════════════════════════════════════════════════

@register("three_images")
def three_images(slide, spec, theme, *, page_num, total):
    """3 image placeholders side-by-side + captions.

    spec:
        images: [{label, caption?}, ...] (3)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    images = spec.get("images", [])[:3]
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    img_h = body_h * 0.65
    gap = 0.25
    n = 3
    img_w = (L.content_width_in - gap * (n - 1)) / n

    for i in range(n):
        x = L.margin_left_in + i * (img_w + gap)
        img = images[i] if i < len(images) else {"label": f"이미지 {i+1}"}
        add_image_placeholder(slide,
                               left=x, top=body_top,
                               width=img_w, height=img_h,
                               label=img.get("label", f"이미지 {i+1}"),
                               theme=theme)
        if img.get("caption"):
            tb = add_textbox(slide, x, body_top + img_h + 0.15,
                              img_w, body_h - img_h - 0.15)
            write_paragraph(tb.text_frame, img["caption"], theme=theme,
                             size=T.body_size - 1, color=P.gray_1,
                             align=PP_ALIGN.CENTER, line_spacing=1.4)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# TWO_COL_IMAGE_GRID (#68) — 2×2 image+text grid
# ════════════════════════════════════════════════════════════════════

@register("two_col_image_grid")
def two_col_image_grid(slide, spec, theme, *, page_num, total):
    """2×2 image+text grid.

    spec:
        items: [{image_label, headline, desc?}, ...] (4)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = spec.get("items", [])[:4]
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    gap = 0.2
    cell_w = (L.content_width_in - gap) / 2
    cell_h = (body_h - gap) / 2
    img_w = cell_w * 0.45

    for i, it in enumerate(items):
        r, c = divmod(i, 2)
        x = L.margin_left_in + c * (cell_w + gap)
        y = body_top + r * (cell_h + gap)
        add_image_placeholder(slide,
                               left=x, top=y, width=img_w, height=cell_h,
                               label=it.get("image_label", "이미지"),
                               theme=theme)
        # Text right of image
        tx = x + img_w + 0.2
        tw = cell_w - img_w - 0.2
        tb = add_textbox(slide, tx, y + 0.15, tw, 0.5)
        write_paragraph(tb.text_frame, it.get("headline", ""), theme=theme,
                         size=T.sub_header_size, bold=True, color=P.gray_1,
                         line_spacing=1.25)
        if it.get("desc"):
            tb = add_textbox(slide, tx, y + 0.75, tw, cell_h - 0.85)
            write_paragraph(tb.text_frame, it["desc"], theme=theme,
                             size=T.body_size, color=P.gray_2,
                             line_spacing=1.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ════════════════════════════════════════════════════════════════════
# METRIC_COMPARISON (#62) — before/after delta cards
# ════════════════════════════════════════════════════════════════════

@register("metric_comparison")
def metric_comparison(slide, spec, theme, *, page_num, total):
    """Before/after metric cards w/ delta badges.

    spec:
        metrics: [{label, before, after, unit?, cost_nature?: bool}, ...]
                 (≤5)
        period_before: "Q3"   period_after: "Q4"
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    metrics = spec.get("metrics", [])[:5]
    n = max(len(metrics), 1)
    body_top = L.content_top_in + 0.4
    gap = 0.2
    card_w = (L.content_width_in - gap * (n - 1)) / n
    card_h = 3.5
    label_band_h = 0.4

    p_before = spec.get("period_before", "Before")
    p_after = spec.get("period_after", "After")

    for i, m in enumerate(metrics):
        x = L.margin_left_in + i * (card_w + gap)
        # Label band on top
        add_rect(slide, x, body_top, card_w, label_band_h, P.surface_inverse)
        tb = add_textbox(slide, x + 0.15, body_top + 0.08,
                          card_w - 0.3, label_band_h - 0.16)
        write_paragraph(tb.text_frame, m.get("label", ""), theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.surface_inverse_fg,
                         align=PP_ALIGN.CENTER)
        body_y = body_top + label_band_h + 0.2
        # Compute delta
        try:
            before = float(m["before"]); after = float(m["after"])
            delta = after - before
            pct = (delta / before * 100) if before else 0
            is_cost = m.get("cost_nature", False)
            up_good = not is_cost
            good = (delta >= 0) == up_good
            col = P.positive if good else P.negative
            mark = "▲" if delta > 0 else "▼" if delta < 0 else "●"
            sign = "+" if delta > 0 else ""
            unit = m.get("unit", "")
        except Exception:
            delta = pct = 0; col = P.gray_2; mark = "●"; sign = ""; unit = ""

        # Before
        tb = add_textbox(slide, x + 0.15, body_y, card_w - 0.3, 0.3)
        write_paragraph(tb.text_frame, p_before, theme=theme,
                         size=T.small_size, color=P.gray_2,
                         align=PP_ALIGN.CENTER)
        tb = add_textbox(slide, x + 0.15, body_y + 0.3, card_w - 0.3, 0.6)
        write_paragraph(tb.text_frame,
                         f"{m.get('before','')}{m.get('unit','')}",
                         theme=theme,
                         size=T.section_title_size, bold=True,
                         color=P.gray_2, align=PP_ALIGN.CENTER)
        # Arrow
        tb = add_textbox(slide, x + 0.15, body_y + 1.0, card_w - 0.3, 0.4)
        write_paragraph(tb.text_frame, "→", theme=theme,
                         size=T.sub_header_size, bold=True, color=P.gray_3,
                         align=PP_ALIGN.CENTER)
        # After
        tb = add_textbox(slide, x + 0.15, body_y + 1.4, card_w - 0.3, 0.3)
        write_paragraph(tb.text_frame, p_after, theme=theme,
                         size=T.small_size, color=P.primary,
                         align=PP_ALIGN.CENTER)
        tb = add_textbox(slide, x + 0.15, body_y + 1.7, card_w - 0.3, 0.6)
        write_paragraph(tb.text_frame,
                         f"{m.get('after','')}{m.get('unit','')}",
                         theme=theme,
                         size=T.section_title_size, bold=True,
                         color=P.gray_1, align=PP_ALIGN.CENTER)
        # Delta badge
        tb = add_textbox(slide, x + 0.15, body_y + 2.4, card_w - 0.3, 0.3)
        write_paragraph(tb.text_frame,
                         f"{mark} {sign}{pct:.1f}%",
                         theme=theme,
                         size=T.body_size, bold=True, color=col,
                         align=PP_ALIGN.CENTER)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
