"""Organization layouts — org_chart.

Reference: likaku/seulee26 org_charts.py.
"""
from __future__ import annotations
from typing import List

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)


def _draw_node(slide, x, y, w, h, name, role, theme, *, is_root=False):
    P, T = theme.palette, theme.typography
    fill = P.surface_inverse if is_root else P.gray_4
    fg = P.surface_inverse_fg if is_root else P.gray_1
    sub_fg = P.surface_inverse_fg if is_root else P.gray_2
    add_rect(slide, x, y, w, h, fill)
    tb = add_textbox(slide, x + 0.15, y + 0.12, w - 0.3, 0.5)
    write_paragraph(tb.text_frame, name, theme=theme,
                     size=T.body_size, bold=True, color=fg,
                     align=PP_ALIGN.CENTER)
    if role:
        tb = add_textbox(slide, x + 0.15, y + 0.6, w - 0.3, 0.3)
        write_paragraph(tb.text_frame, role, theme=theme,
                         size=T.small_size - 1, color=sub_fg,
                         align=PP_ALIGN.CENTER)


@register("org_chart")
def org_chart(slide, spec, theme, *, page_num, total):
    """3-tier org chart: CEO → heads → team members.

    spec:
        root: {name, role}
        heads: [{name, role, members?: [{name, role}, ...]}, ...]
        source, bottom_bar

    Max 4 heads; max 4 members per head — beyond that gets cramped.
    """
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    root = spec.get("root", {})
    heads = spec.get("heads", [])[:4]

    body_top = L.content_top_in + 0.2

    # Root
    root_w = 2.5
    root_h = 1.0
    root_x = L.margin_left_in + (L.content_width_in - root_w) / 2
    root_y = body_top
    _draw_node(slide, root_x, root_y, root_w, root_h,
                root.get("name", ""), root.get("role", ""),
                theme, is_root=True)

    # Heads
    n_heads = max(len(heads), 1)
    head_w = 2.2
    head_h = 0.9
    head_y = body_top + root_h + 0.8
    spacing = L.content_width_in / n_heads
    head_xs = [L.margin_left_in + i * spacing + (spacing - head_w) / 2
                for i in range(n_heads)]

    # Connectors: root bottom → trunk → heads top
    trunk_y = root_y + root_h + 0.3
    root_bottom_cx = root_x + root_w / 2
    add_rect(slide, root_bottom_cx - 0.01, root_y + root_h,
              0.02, 0.3, P.gray_3)
    if n_heads > 1:
        first = head_xs[0] + head_w / 2
        last = head_xs[-1] + head_w / 2
        add_rect(slide, first, trunk_y, last - first, 0.02, P.gray_3)
    for hx in head_xs:
        cx = hx + head_w / 2
        add_rect(slide, cx - 0.01, trunk_y, 0.02, head_y - trunk_y, P.gray_3)

    for i, h in enumerate(heads):
        _draw_node(slide, head_xs[i], head_y, head_w, head_h,
                    h.get("name", ""), h.get("role", ""), theme)

    # Members (per head, vertical stack under each)
    member_y0 = head_y + head_h + 0.4
    member_h = 0.6
    member_w = 2.0
    for i, h in enumerate(heads):
        members = h.get("members", [])[:4]
        # Connector from head bottom to first member
        cx = head_xs[i] + head_w / 2
        if members:
            add_rect(slide, cx - 0.01, head_y + head_h,
                      0.02, member_y0 - (head_y + head_h),
                      P.gray_3)
        for j, m in enumerate(members):
            mx = head_xs[i] + (head_w - member_w) / 2
            my = member_y0 + j * (member_h + 0.1)
            # Connector tee — horizontal from trunk to member
            add_rect(slide, cx - 0.01, my + member_h / 2,
                      mx - cx + 0.01, 0.02, P.gray_3)
            # Extend vertical trunk
            if j > 0:
                add_rect(slide, cx - 0.01,
                          member_y0 + (j - 1) * (member_h + 0.1) + member_h / 2,
                          0.02, member_h + 0.1, P.gray_3)
            _draw_node(slide, mx, my, member_w, member_h,
                        m.get("name", ""), m.get("role", ""), theme)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                       tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
