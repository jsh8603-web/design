"""Process layouts — phases_chevron, vertical_steps, value_chain, funnel,
pyramid, gantt_timeline, waves_timeline, cycle.

Reference: likaku (phases_chevron, vertical_steps, value_chain, pyramid, cycle),
           seulee26 (funnel, gantt_timeline, waves_timeline).
"""
from __future__ import annotations
from math import cos, sin, pi

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


@register("phases_chevron")
def phases_chevron(slide, spec, theme, *, page_num, total):
    """Horizontal chevron-step process (3-5 steps).

    spec:
        steps: [{label, headline?, desc?}, ...] (max 5)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    steps = spec.get("steps", [])[:5]
    n = max(len(steps), 1)
    chev_y = L.content_top_in + 0.3
    chev_h = 0.8
    overlap = 0.25  # how much each chevron tail overlaps the next
    total_w = L.content_width_in + overlap * (n - 1)
    step_w = total_w / n

    for i, st in enumerate(steps):
        x = L.margin_left_in + i * (step_w - overlap)
        # Use CHEVRON shape (pentagon arrow)
        shape = slide.shapes.add_shape(
            MSO_SHAPE.CHEVRON, Inches(x), Inches(chev_y),
            Inches(step_w), Inches(chev_h),
        )
        color = P.surface_inverse if i == 0 else (
            P.accent if i == 1 else P.gray_2 if i < 4 else P.gray_3
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = hex_to_rgb(color)
        shape.line.fill.background()
        _clean_shape(shape)
        # Label inside the chevron
        tb = add_textbox(slide, x + 0.3, chev_y + 0.2,
                          step_w - 0.7, chev_h - 0.4)
        label_text = st.get("label", f"Step {i + 1}")
        # Strip newlines (chevron labels must be single-line per likaku guidance)
        label_text = label_text.replace("\n", " ").replace("<br>", " ")
        write_paragraph(tb.text_frame, label_text, theme=theme,
                         size=T.body_size, bold=True,
                         color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)

    # Detail rows below chevrons
    detail_top = chev_y + chev_h + 0.3
    col_w = (L.content_width_in - 0.2 * (n - 1)) / n
    for i, st in enumerate(steps):
        x = L.margin_left_in + i * (col_w + 0.2)
        if st.get("headline"):
            tb = add_textbox(slide, x, detail_top, col_w, 0.5)
            write_paragraph(tb.text_frame, st["headline"], theme=theme,
                             size=T.body_size + 1, bold=True, color=P.gray_1,
                             align=PP_ALIGN.CENTER)
        if st.get("desc"):
            tb = add_textbox(slide, x, detail_top + 0.55, col_w, 2.5)
            write_paragraph(tb.text_frame, st["desc"], theme=theme,
                             size=T.body_size - 1, color=P.gray_2,
                             align=PP_ALIGN.CENTER, line_spacing=1.45)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("vertical_steps")
def vertical_steps(slide, spec, theme, *, page_num, total):
    """Vertical numbered-step list, optional right takeaway panel.

    spec:
        steps: [{title, desc}, ...]
        takeaway: {label, headline, bullets} (optional)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    steps = spec.get("steps", [])
    has_panel = bool(spec.get("takeaway"))

    body_top = L.content_top_in + 0.2
    body_h = L.bottom_bar_y_in - body_top - 0.2
    if has_panel:
        panel_w = 3.5
        left_w = L.content_width_in - panel_w - 0.4
    else:
        left_w = L.content_width_in

    n = max(len(steps), 1)
    step_h = min(0.9, body_h / n)

    for i, st in enumerate(steps):
        y = body_top + i * step_h
        # Number badge
        is_final = i == len(steps) - 1
        col = P.accent if is_final else P.surface_inverse
        fg = P.surface_inverse_fg if not is_final else P.white
        add_oval(slide, L.margin_left_in, y + 0.05, 0.6, 0.6, col)
        tb = add_textbox(slide, L.margin_left_in, y + 0.1, 0.6, 0.5)
        write_paragraph(tb.text_frame, str(i + 1), theme=theme,
                         size=T.sub_header_size, bold=True,
                         color=fg, align=PP_ALIGN.CENTER)
        # Title
        tb = add_textbox(slide, L.margin_left_in + 0.85, y + 0.05,
                          left_w - 0.85, 0.4)
        write_paragraph(tb.text_frame, st.get("title", ""), theme=theme,
                         size=T.body_size + 2, bold=True, color=P.gray_1,
                         line_spacing=1.2)
        # Desc
        if st.get("desc"):
            tb = add_textbox(slide, L.margin_left_in + 0.85, y + 0.45,
                              left_w - 0.85, step_h - 0.5)
            write_paragraph(tb.text_frame, st["desc"], theme=theme,
                             size=T.body_size - 1, color=P.gray_2,
                             line_spacing=1.45)
        # Connector to next
        if i < len(steps) - 1:
            add_rect(slide, L.margin_left_in + 0.295, y + 0.65,
                      0.01, step_h - 0.6, P.gray_3)

    # Right takeaway panel
    if has_panel:
        t = spec["takeaway"]
        px = L.margin_left_in + left_w + 0.4
        add_rect(slide, px, body_top, panel_w, body_h, P.gray_4)
        tb = add_textbox(slide, px + 0.25, body_top + 0.2, panel_w - 0.5, 0.3)
        write_paragraph(tb.text_frame, t.get("label", "Takeaway"),
                         theme=theme, size=T.small_size - 1, bold=True,
                         color=P.primary)
        if t.get("headline"):
            tb = add_textbox(slide, px + 0.25, body_top + 0.55,
                              panel_w - 0.5, 0.8)
            write_paragraph(tb.text_frame, t["headline"], theme=theme,
                             size=T.body_size + 3, bold=True, color=P.gray_1,
                             line_spacing=1.3)
        for j, b in enumerate(t.get("bullets", [])):
            tb = add_textbox(slide, px + 0.25, body_top + 1.5 + j * 0.55,
                              panel_w - 0.5, 0.5)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, "• ", theme=theme, size=T.body_size - 1, color=P.primary)
            r2 = p.add_run()
            set_run(r2, b, theme=theme, size=T.body_size - 1, color=P.gray_1)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("value_chain")
def value_chain(slide, spec, theme, *, page_num, total):
    """Horizontal value-chain pipeline (3-7 stages, arrows between).

    spec:
        stages: [{label, kpi?}, ...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    stages = spec.get("stages", [])
    n = max(len(stages), 1)
    body_top = L.content_top_in + 0.6
    arrow_w = 0.4
    stage_w = (L.content_width_in - arrow_w * (n - 1)) / n
    stage_h = 1.4

    for i, st in enumerate(stages):
        x = L.margin_left_in + i * (stage_w + arrow_w)
        # Pentagon/right-arrow box
        shape = slide.shapes.add_shape(
            MSO_SHAPE.PENTAGON, Inches(x), Inches(body_top),
            Inches(stage_w), Inches(stage_h),
        )
        col = P.surface_inverse if i % 2 == 0 else P.accent
        shape.fill.solid()
        shape.fill.fore_color.rgb = hex_to_rgb(col)
        shape.line.fill.background()
        _clean_shape(shape)
        # Label
        tb = add_textbox(slide, x + 0.15, body_top + 0.35,
                          stage_w - 0.5, 0.7)
        write_paragraph(tb.text_frame, st.get("label", f"Stage {i + 1}"),
                         theme=theme, size=T.body_size + 1, bold=True,
                         color=P.surface_inverse_fg, align=PP_ALIGN.CENTER,
                         line_spacing=1.2)

    # KPI row below
    kpi_y = body_top + stage_h + 0.3
    for i, st in enumerate(stages):
        x = L.margin_left_in + i * (stage_w + arrow_w)
        if st.get("kpi"):
            tb = add_textbox(slide, x, kpi_y, stage_w, 1.2)
            write_paragraph(tb.text_frame, str(st["kpi"]), theme=theme,
                             size=T.body_size, color=P.gray_2,
                             align=PP_ALIGN.CENTER, line_spacing=1.4)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("funnel")
def funnel(slide, spec, theme, *, page_num, total):
    """Sales/conversion funnel — trapezoidal stages, descending width.

    spec:
        stages: [{label, value?, conversion?}, ...]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    stages = spec.get("stages", [])
    n = max(len(stages), 1)
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    stage_h = body_h / n
    max_w = L.content_width_in * 0.7
    min_w = max_w * 0.35
    center_x = L.margin_left_in + L.content_width_in / 2

    for i, st in enumerate(stages):
        # Width decreases linearly
        w = max_w - (max_w - min_w) * (i / max(n - 1, 1))
        x = center_x - w / 2
        y = body_top + i * stage_h
        col = P.surface_inverse if i == 0 else (
            P.accent if i == 1 else P.gray_2 if i < n - 1 else P.positive
        )
        add_rect(slide, x, y + 0.05, w, stage_h - 0.15, col)
        # Label (left-aligned inside)
        tb = add_textbox(slide, x + 0.25, y + 0.1, w - 0.5, stage_h - 0.25)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r1 = p.add_run()
        set_run(r1, st.get("label", ""), theme=theme,
                size=T.body_size + 1, bold=True, color=P.white)
        # Value on the right (in a separate textbox so alignment works)
        if st.get("value") is not None:
            tb = add_textbox(slide, x + w + 0.2, y + 0.1, 2.5, 0.5)
            write_paragraph(tb.text_frame, str(st["value"]), theme=theme,
                             size=T.body_size + 2, bold=True, color=P.gray_1)
        if st.get("conversion"):
            tb = add_textbox(slide, x + w + 0.2, y + 0.6, 2.5, 0.4)
            write_paragraph(tb.text_frame, str(st["conversion"]), theme=theme,
                             size=T.body_size - 1, color=P.gray_2)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("pyramid")
def pyramid(slide, spec, theme, *, page_num, total):
    """Hierarchical pyramid (3-5 tiers, ascending importance bottom-up).

    spec:
        tiers: [{label, desc?}, ...] (top to bottom)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    tiers = spec.get("tiers", [])
    n = max(len(tiers), 1)
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    tier_h = (body_h - 0.05 * (n - 1)) / n
    top_w = 2.5
    bottom_w = L.content_width_in * 0.55
    center_x = L.margin_left_in + L.content_width_in * 0.3

    for i, t in enumerate(tiers):
        # Linear width interp
        w = top_w + (bottom_w - top_w) * (i / max(n - 1, 1))
        x = center_x - w / 2
        y = body_top + i * (tier_h + 0.05)
        col = P.accent if i == 0 else (
            P.surface_inverse if i == 1 else P.gray_2
        )
        add_rect(slide, x, y, w, tier_h, col)
        tb = add_textbox(slide, x + 0.2, y + 0.1, w - 0.4, tier_h - 0.2)
        write_paragraph(tb.text_frame, t.get("label", ""), theme=theme,
                         size=T.body_size + 1, bold=True,
                         color=P.white, align=PP_ALIGN.CENTER)

        # Description column on the right
        if t.get("desc"):
            dx = center_x + bottom_w / 2 + 0.3
            tb = add_textbox(slide, dx, y, L.slide_width_in - L.margin_right_in - dx,
                              tier_h)
            write_paragraph(tb.text_frame, t["desc"], theme=theme,
                             size=T.body_size, color=P.gray_1,
                             line_spacing=1.45)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("gantt_timeline")
def gantt_timeline(slide, spec, theme, *, page_num, total):
    """Simple Gantt — tasks × weeks/months.

    spec:
        periods: ["Q1","Q2",...] (column headers)
        tasks: [{label, start: int, end: int}] (0-indexed period)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    periods = spec.get("periods", [])
    tasks = spec.get("tasks", [])
    body_left = L.margin_left_in
    body_top = L.content_top_in + 0.3
    body_w = L.content_width_in
    label_w = body_w * 0.25
    period_total_w = body_w - label_w
    n_p = max(len(periods), 1)
    period_w = period_total_w / n_p
    header_h = 0.5
    row_h = 0.45

    # Period headers
    add_rect(slide, body_left + label_w, body_top, period_total_w, header_h,
              P.surface_inverse)
    for i, p in enumerate(periods):
        tb = add_textbox(slide, body_left + label_w + i * period_w,
                          body_top + 0.12, period_w, header_h - 0.2)
        write_paragraph(tb.text_frame, str(p), theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.surface_inverse_fg, align=PP_ALIGN.CENTER)

    # Task rows
    for i, task in enumerate(tasks):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, body_left, y, body_w, row_h, P.gray_4)
        # Label
        tb = add_textbox(slide, body_left + 0.15, y + 0.07,
                          label_w - 0.3, row_h - 0.1)
        write_paragraph(tb.text_frame, task.get("label", ""), theme=theme,
                         size=T.body_size - 1, color=P.gray_1, bold=True)
        # Bar
        start = max(0, int(task.get("start", 0)))
        end = min(n_p - 1, int(task.get("end", start)))
        bx = body_left + label_w + start * period_w + 0.1
        bw = (end - start + 1) * period_w - 0.2
        if bw > 0:
            add_rect(slide, bx, y + 0.1, bw, row_h - 0.2, P.accent)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("waves_timeline")
def waves_timeline(slide, spec, theme, *, page_num, total):
    """Wave-based phased plan — 3-4 horizontal bands across time.

    spec:
        waves: [{label, period, focus?, bullets?}]
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    waves = spec.get("waves", [])
    n = max(len(waves), 1)
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    wave_h = (body_h - 0.2 * (n - 1)) / n

    for i, w in enumerate(waves):
        y = body_top + i * (wave_h + 0.2)
        col = P.surface_inverse if i % 2 == 0 else P.accent
        # Wave header strip (left 25%)
        header_w = L.content_width_in * 0.25
        add_rect(slide, L.margin_left_in, y, header_w, wave_h, col)
        tb = add_textbox(slide, L.margin_left_in + 0.2, y + 0.15,
                          header_w - 0.4, 0.5)
        write_paragraph(tb.text_frame, w.get("label", f"Wave {i + 1}"),
                         theme=theme, size=T.sub_header_size, bold=True,
                         color=P.white)
        if w.get("period"):
            tb = add_textbox(slide, L.margin_left_in + 0.2, y + 0.7,
                              header_w - 0.4, 0.4)
            write_paragraph(tb.text_frame, str(w["period"]), theme=theme,
                             size=T.body_size - 1, color=P.white)

        # Content area (right 75%)
        cx = L.margin_left_in + header_w + 0.3
        cw = L.content_width_in - header_w - 0.3
        if w.get("focus"):
            tb = add_textbox(slide, cx, y + 0.1, cw, 0.5)
            write_paragraph(tb.text_frame, w["focus"], theme=theme,
                             size=T.body_size + 1, bold=True, color=P.gray_1,
                             line_spacing=1.25)
        for j, b in enumerate(w.get("bullets", [])[:3]):
            tb = add_textbox(slide, cx, y + 0.65 + j * 0.35, cw, 0.32)
            p = tb.text_frame.paragraphs[0]
            r1 = p.add_run()
            set_run(r1, "• ", theme=theme, size=T.body_size - 1,
                    color=P.accent)
            r2 = p.add_run()
            set_run(r2, b, theme=theme, size=T.body_size - 1,
                    color=P.gray_1)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


@register("cycle")
def cycle(slide, spec, theme, *, page_num, total):
    """Cyclic process diagram — N steps in a circle with arrows.

    spec:
        steps: [{label, desc?}, ...] (3-6 steps)
        source, bottom_bar
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    steps = spec.get("steps", [])[:6]
    n = max(len(steps), 1)
    body_top = L.content_top_in + 0.3
    body_h = L.bottom_bar_y_in - body_top - 0.3
    # Circle layout
    radius = min(body_h / 2 - 0.5, 2.2)
    cx = L.margin_left_in + L.content_width_in * 0.32
    cy = body_top + body_h / 2
    node_size = 1.1

    for i, st in enumerate(steps):
        angle = -pi / 2 + 2 * pi * i / n
        nx = cx + radius * cos(angle) - node_size / 2
        ny = cy + radius * sin(angle) - node_size / 2
        # Node
        col = P.surface_inverse if i == 0 else P.accent
        add_oval(slide, nx, ny, node_size, node_size, col)
        tb = add_textbox(slide, nx, ny + node_size / 3, node_size, node_size / 3)
        write_paragraph(tb.text_frame, str(i + 1), theme=theme,
                         size=T.sub_header_size + 2, bold=True,
                         color=P.white, align=PP_ALIGN.CENTER)
        # Label outside the circle
        lx = cx + (radius + 1.1) * cos(angle) - 1.5
        ly = cy + (radius + 1.1) * sin(angle) - 0.15
        tb = add_textbox(slide, lx, ly, 3.0, 0.4)
        write_paragraph(tb.text_frame, st.get("label", ""), theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1,
                         align=PP_ALIGN.CENTER, line_spacing=1.2)

    # Right description list
    desc_x = L.margin_left_in + L.content_width_in * 0.62
    desc_w = L.content_width_in - L.content_width_in * 0.62
    for i, st in enumerate(steps):
        if not st.get("desc"):
            continue
        y = body_top + 0.1 + i * 0.65
        tb = add_textbox(slide, desc_x, y, desc_w, 0.5)
        p = tb.text_frame.paragraphs[0]
        r1 = p.add_run()
        set_run(r1, f"{i + 1}. ", theme=theme,
                size=T.body_size, bold=True, color=P.accent)
        r2 = p.add_run()
        set_run(r2, st["desc"], theme=theme,
                size=T.body_size - 1, color=P.gray_1)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
