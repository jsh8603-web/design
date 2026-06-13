"""variance_table + data_table layouts.

variance_table is the FP&A-critical layout — cost_nature sign flip lives here.
data_table is a generic rows/cells layout (no calculation).
"""
from __future__ import annotations
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import set_run, write_paragraph
from deck_system.helpers.chrome import (
    add_action_title, add_source, add_page_number, add_bottom_bar,
)
from deck_system.layouts._variance_logic import (
    compute_variance, resolve_variance_color,
)


# ── variance_table (HTML JSON spec verbatim) ─────────────────────────
_DEFAULT_COLUMNS = ["label", "budget", "actual", "variance_abs", "variance_pct"]
_COL_HEADERS = {
    "label": "항목",
    "budget": "예산",
    "actual": "실적",
    "variance_abs": "차이",
    "variance_pct": "차이 %",
}


def _fmt_number(v, unit: str = "", decimals: int = 0, signed: bool = False) -> str:
    if v is None:
        return "—"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if decimals > 0:
        body = f"{abs(v):,.{decimals}f}"
    else:
        body = f"{abs(round(v)):,}" if isinstance(v, (int, float)) else str(v)
    sign = ""
    if signed and isinstance(v, (int, float)):
        if v > 0: sign = "+"
        elif v < 0: sign = "−"
    elif isinstance(v, (int, float)) and v < 0:
        sign = "−"
    return f"{sign}{body}{unit}"


@register("variance_table")
def variance_table(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    items = spec.get("items", [])
    columns = spec.get("columns", _DEFAULT_COLUMNS)
    unit_default = spec.get("unit_default", "")
    neutral_pct = float(spec.get("neutral_threshold_pct", 0.0))
    highlight_idx = spec.get("highlight_row_index")

    # Layout
    body_top = L.content_top_in + 0.1
    body_left = L.margin_left_in
    body_width = L.content_width_in
    header_h = 0.4
    row_h = 0.42

    # Column widths — label gets 26%, the rest split evenly
    n_cols = len(columns)
    label_w = body_width * 0.30
    other_w = (body_width - label_w) / max(n_cols - 1, 1)
    col_xs = []
    cursor = body_left
    for col in columns:
        col_xs.append((col, cursor, label_w if col == "label" else other_w))
        cursor += label_w if col == "label" else other_w

    # Header row — surface_inverse bg
    add_rect(slide, body_left, body_top, body_width, header_h, P.surface_inverse)
    for col, x, w in col_xs:
        tb = add_textbox(slide, x + 0.14, body_top + 0.04, w - 0.28, header_h - 0.08)
        write_paragraph(
            tb.text_frame, _COL_HEADERS.get(col, col),
            theme=theme, size=T.body_size - 1, bold=True,
            color=P.surface_inverse_fg,
            align=PP_ALIGN.LEFT if col == "label" else PP_ALIGN.RIGHT,
        )

    # Body rows
    for i, item in enumerate(items):
        y = body_top + header_h + i * row_h
        # Highlight row bg
        if highlight_idx == i:
            add_rect(slide, body_left, y, body_width, row_h, P.gray_4)

        abs_var, pct_var = compute_variance(item)
        item_unit = item.get("unit", unit_default)
        var_color = resolve_variance_color(item, pct_var, theme, neutral_pct)

        for col, x, w in col_xs:
            tb = add_textbox(slide, x + 0.14, y + 0.06, w - 0.28, row_h - 0.12)
            text, color, align, bold = "", P.gray_1, PP_ALIGN.RIGHT, False
            if col == "label":
                text, align, bold = item["label"], PP_ALIGN.LEFT, True
            elif col == "budget":
                decimals = 1 if item_unit == "%" else 0
                text = _fmt_number(item["budget"], unit=item_unit,
                                    decimals=decimals)
            elif col == "actual":
                decimals = 1 if item_unit == "%" else 0
                text = _fmt_number(item["actual"], unit=item_unit,
                                    decimals=decimals)
            elif col == "variance_abs":
                decimals = 1 if item_unit == "%" else 0
                text = _fmt_number(abs_var, unit=item_unit,
                                    decimals=decimals, signed=True)
                color = var_color
                bold = True
            elif col == "variance_pct":
                if pct_var is None:
                    text = "—"
                else:
                    text = _fmt_number(pct_var, unit="%",
                                        decimals=1, signed=True)
                color = var_color
                bold = True
            write_paragraph(
                tb.text_frame, text, theme=theme,
                size=T.body_size, bold=bold, color=color, align=align,
            )

        # Bottom rule under each row (gray_4)
        add_hline(slide, body_left, y + row_h - 0.01,
                  body_width, P.gray_4, thickness_pt=0.75)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── data_table — generic rows/cells, no calculation ────────────────
@register("data_table")
def data_table(slide, spec, theme, *, page_num, total):
    L = theme.layout
    P = theme.palette
    T = theme.typography

    add_action_title(slide, spec.get("title", ""), theme=theme)

    headers = spec.get("headers", [])
    rows = spec.get("rows", [])
    items = spec.get("items", [])  # alternative: [{cells:[...]}, …]
    if items and not rows:
        rows = [item["cells"] for item in items]

    body_top = L.content_top_in + 0.1
    body_left = L.margin_left_in
    body_width = L.content_width_in
    header_h = 0.4
    row_h = 0.4
    n_cols = max(len(headers), max((len(r) for r in rows), default=1))
    col_w = body_width / n_cols

    if headers:
        add_rect(slide, body_left, body_top, body_width, header_h, P.surface_inverse)
        for j, h in enumerate(headers):
            tb = add_textbox(slide, body_left + j * col_w + 0.14, body_top + 0.04,
                              col_w - 0.28, header_h - 0.08)
            write_paragraph(
                tb.text_frame, h, theme=theme,
                size=T.body_size - 1, bold=True,
                color=P.surface_inverse_fg,
                align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT,
            )

    for i, row in enumerate(rows):
        y = body_top + (header_h if headers else 0) + i * row_h
        for j, cell in enumerate(row):
            tb = add_textbox(slide, body_left + j * col_w + 0.14, y + 0.06,
                              col_w - 0.28, row_h - 0.12)
            write_paragraph(
                tb.text_frame, str(cell), theme=theme,
                size=T.body_size, bold=(j == 0), color=P.gray_1,
                align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT,
            )
        add_hline(slide, body_left, y + row_h - 0.01,
                  body_width, P.gray_4, thickness_pt=0.75)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── rag_status — red/amber/green project status table ───────────────
@register("rag_status")
def rag_status(slide, spec, theme, *, page_num, total):
    """Multi-project RAG status table.

    spec:
        projects: [{name, status: 'red'|'amber'|'green', owner?, note?}, ...]
        source, bottom_bar
    """
    from deck_system.helpers.shapes import add_oval
    L = theme.layout
    P = theme.palette
    T = theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    projects = spec.get("projects", [])
    body_top = L.content_top_in + 0.2
    body_left = L.margin_left_in
    body_width = L.content_width_in
    header_h = 0.45
    row_h = 0.55

    cols = [("프로젝트", 0.35), ("상태", 0.15), ("담당", 0.15), ("비고", 0.35)]
    add_rect(slide, body_left, body_top, body_width, header_h, P.surface_inverse)
    cursor = body_left
    col_xs = []
    for name, w_ratio in cols:
        w = body_width * w_ratio
        col_xs.append((cursor, w))
        tb = add_textbox(slide, cursor + 0.14, body_top + 0.08,
                          w - 0.28, header_h - 0.16)
        write_paragraph(tb.text_frame, name, theme=theme,
                         size=T.body_size - 1, bold=True,
                         color=P.surface_inverse_fg)
        cursor += w

    for i, prj in enumerate(projects):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, body_left, y, body_width, row_h, P.gray_4)
        status = str(prj.get("status", "amber")).lower()
        if status in ("red", "r"):
            dot_color, label = P.negative, "Red"
        elif status in ("green", "g"):
            dot_color, label = P.positive, "Green"
        else:
            dot_color, label = "#F4C57A", "Amber"

        x, w = col_xs[0]
        tb = add_textbox(slide, x + 0.14, y + 0.12, w - 0.28, row_h - 0.22)
        write_paragraph(tb.text_frame, prj.get("name", ""), theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1)
        x, w = col_xs[1]
        add_oval(slide, x + w / 2 - 0.4, y + row_h / 2 - 0.13,
                  0.26, 0.26, dot_color)
        tb = add_textbox(slide, x + w / 2, y + row_h / 2 - 0.15, 1.0, 0.3)
        write_paragraph(tb.text_frame, label, theme=theme,
                         size=T.body_size - 1, color=dot_color, bold=True)
        x, w = col_xs[2]
        tb = add_textbox(slide, x + 0.14, y + 0.12, w - 0.28, row_h - 0.22)
        write_paragraph(tb.text_frame, prj.get("owner", ""), theme=theme,
                         size=T.body_size, color=P.gray_2,
                         align=PP_ALIGN.CENTER)
        x, w = col_xs[3]
        tb = add_textbox(slide, x + 0.14, y + 0.12, w - 0.28, row_h - 0.22)
        write_paragraph(tb.text_frame, prj.get("note", ""), theme=theme,
                         size=T.body_size - 1, color=P.gray_2)
        add_hline(slide, body_left, y + row_h - 0.01,
                   body_width, P.gray_4, thickness_pt=0.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── harvey_ball_table — multi-criteria evaluation matrix ────────────
@register("harvey_ball_table")
def harvey_ball_table(slide, spec, theme, *, page_num, total):
    """Options × criteria with Harvey ball ratings (0/25/50/75/100).

    spec:
        options: ["Option A", "Option B", ...]
        criteria: [{label, scores: [0..100,...] per option}, ...]
        source, bottom_bar
    """
    L = theme.layout
    P = theme.palette
    T = theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    options = spec.get("options", [])
    criteria = spec.get("criteria", [])

    body_top = L.content_top_in + 0.2
    body_left = L.margin_left_in
    body_width = L.content_width_in
    header_h = 0.5
    row_h = 0.55
    label_w = body_width * 0.32
    n_opt = max(len(options), 1)
    opt_w = (body_width - label_w) / n_opt

    add_rect(slide, body_left, body_top, body_width, header_h, P.surface_inverse)
    for j, opt in enumerate(options):
        x = body_left + label_w + j * opt_w
        tb = add_textbox(slide, x + 0.1, body_top + 0.1, opt_w - 0.2, header_h - 0.2)
        write_paragraph(tb.text_frame, opt, theme=theme,
                         size=T.body_size, bold=True,
                         color=P.surface_inverse_fg,
                         align=PP_ALIGN.CENTER)

    for i, c in enumerate(criteria):
        y = body_top + header_h + i * row_h
        if i % 2 == 1:
            add_rect(slide, body_left, y, body_width, row_h, P.gray_4)
        tb = add_textbox(slide, body_left + 0.14, y + 0.1, label_w - 0.28, row_h - 0.2)
        write_paragraph(tb.text_frame, c.get("label", ""), theme=theme,
                         size=T.body_size, bold=True, color=P.gray_1)
        for j, score in enumerate(c.get("scores", [])):
            x = body_left + label_w + j * opt_w
            cx = x + opt_w / 2 - 0.18
            cy = y + row_h / 2 - 0.18
            _draw_harvey_ball(slide, cx, cy, 0.36, int(score), theme)
        add_hline(slide, body_left, y + row_h - 0.01,
                   body_width, P.gray_4, thickness_pt=0.5)

    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme,
                        tag=spec.get("bottom_tag", "시사점 —"))
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


def _draw_harvey_ball(slide, x, y, size, score, theme):
    """Outline circle + filled wedge proportional to score (0..100)."""
    from deck_system.helpers.shapes import add_block_arc, _clean_shape
    from deck_system.tokens.base import hex_to_rgb
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.util import Inches

    P = theme.palette
    score = max(0, min(100, score))

    # Outline (no-fill black circle)
    outline = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(size), Inches(size),
    )
    outline.fill.background()
    outline.line.color.rgb = hex_to_rgb(P.primary)
    outline.line.width = Inches(0.012)
    _clean_shape(outline)

    if score == 0:
        return
    if score == 100:
        fill = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(size), Inches(size),
        )
        fill.fill.solid()
        fill.fill.fore_color.rgb = hex_to_rgb(P.primary)
        fill.line.fill.background()
        _clean_shape(fill)
        return
    # Partial: BLOCK_ARC from 12 o'clock (=270° in pptx) sweeping clockwise
    start = 270
    end = (270 + score * 3.6) % 360
    add_block_arc(slide, x, y, size, P.primary, start, end)
