"""Scenario summary — PPTX renderer (mirror of mck/assets/scenario-summary.js).

Executive scenario comparison (Downside / Base / Upside) of key P&L results.
One group per KPI metric; within each group, the scenario bars sit side-by-side
with the value labelled above each bar. Scenario color is fixed across all
groups (name-keyed, case-insensitive) so the eye reads
"red = Downside, navy = Base, green = Upside".

KEY DESIGN DECISION — per-KPI independent scale.
  Metrics mix units & magnitudes (매출 ~1500억 vs 영업이익률 ~16.7%). A single
  shared scale would crush the small metric to a sliver, so each KPI group gets
  its own local scale: bar height is relative to the max of *that group's*
  values only. Cross-group magnitude is intentionally NOT comparable — values
  are printed above each bar for the absolute read.
"""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from deck_system.builder.registry import register
from deck_system.helpers.shapes import add_rect, add_textbox, add_hline
from deck_system.helpers.text import write_paragraph
from deck_system.helpers.chrome import add_action_title, add_source, add_page_number


def _fmt(v, unit: str = "") -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}{unit}"


# Fixed scenario → semantic color token. Name-keyed (case-insensitive) so the
# order in the `scenarios` array doesn't change the color mapping. Unknown names
# fall back to a positional ring so the chart still renders.
_SCENARIO_TOKEN = {
    "downside": "negative",
    "base": "surface_inverse",
    "upside": "positive",
}
_FALLBACK_RING = ["negative", "surface_inverse", "positive"]


def _scenario_color(palette, name, idx):
    token = _SCENARIO_TOKEN.get(str(name).strip().lower())
    if token is None:
        token = _FALLBACK_RING[idx % len(_FALLBACK_RING)]
    return getattr(palette, token)


# ────────────────────────────────────────────────────────────────────
# SCENARIO_SUMMARY — scenarios:[...], metrics:[{label, values, unit?}]
# One group per KPI; scenario bars within. Per-KPI independent scale.
# ────────────────────────────────────────────────────────────────────
@register("scenario_summary")
def scenario_summary(slide, spec, theme, *, page_num, total):
    L, P, T = theme.layout, theme.palette, theme.typography
    add_action_title(slide, spec.get("title", ""), theme=theme)

    scenarios = spec.get("scenarios", [])
    metrics = spec.get("metrics", [])
    if not scenarios:
        raise ValueError("[scenario_summary] need at least 1 scenario")
    if not metrics:
        raise ValueError("[scenario_summary] need at least 1 metric")

    chart_left = L.margin_left_in
    chart_top = L.content_top_in + 0.2
    chart_w = L.content_width_in
    chart_h = 4.3

    legend_h = 0.4          # legend band at the very top of the chart area
    label_h = 0.4           # KPI group label band at the bottom
    value_h = 0.3           # value label that floats above the tallest bar
    plot_top = chart_top + legend_h
    baseline_y = chart_top + chart_h - label_h
    plot_h = baseline_y - plot_top - value_h

    n_groups = len(metrics)
    group_w = chart_w / n_groups
    n_bars = len(scenarios)
    group_gutter = group_w * 0.16
    inner_w = group_w - group_gutter * 2
    bar_gap = inner_w * 0.08
    bar_w = (inner_w - bar_gap * (n_bars - 1)) / n_bars if n_bars else inner_w

    # ── Legend (top) — centered cluster of [chip + name] pairs ──────────
    chip = 0.16
    chip_gap = 0.08
    item_gap = 0.4
    char_w = T.body_size / 72.0 * 0.62      # rough glyph width in inches
    item_widths = [chip + chip_gap + len(str(s)) * char_w for s in scenarios]
    legend_w = sum(item_widths) + item_gap * (n_bars - 1)
    lx = chart_left + (chart_w - legend_w) / 2.0
    ly = chart_top + (legend_h - chip) / 2.0
    for i, s in enumerate(scenarios):
        color = _scenario_color(P, s, i)
        add_rect(slide, lx, ly, chip, chip, color)
        tb = add_textbox(slide, lx + chip + chip_gap, ly - 0.05,
                         item_widths[i], chip + 0.1)
        write_paragraph(tb.text_frame, str(s), theme=theme,
                        size=T.body_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.LEFT)
        lx += item_widths[i] + item_gap

    # ── Groups (one per metric, independent scale) ──────────────────────
    for gi, m in enumerate(metrics):
        values = m.get("values", [])
        unit = m.get("unit", "")
        group_max = (max([abs(float(v)) for v in values] + [0.0]) * 1.18) or 1.0
        gx0 = chart_left + gi * group_w + group_gutter

        for bi, v_raw in enumerate(values):
            v = float(v_raw or 0)
            name = scenarios[bi] if bi < n_bars else ""
            color = _scenario_color(P, name, bi)
            bx = gx0 + bi * (bar_w + bar_gap)
            h = max(0.04, (abs(v) / group_max) * plot_h)
            by = baseline_y - h

            add_rect(slide, bx, by, bar_w, h, color)

            # Value above the bar
            tb = add_textbox(slide, bx - bar_w * 0.3, by - value_h,
                             bar_w * 1.6, value_h)
            write_paragraph(tb.text_frame, _fmt(v, unit), theme=theme,
                            size=T.small_size, bold=True, color=P.gray_1,
                            align=PP_ALIGN.CENTER)

        # KPI group label (bottom, centered under the group)
        tb = add_textbox(slide, gx0, baseline_y + 0.08, inner_w, label_h - 0.1)
        write_paragraph(tb.text_frame, str(m.get("label", "")), theme=theme,
                        size=T.body_size, bold=True, color=P.gray_1,
                        align=PP_ALIGN.CENTER)

    # Baseline rule
    add_hline(slide, chart_left, baseline_y, chart_w, P.gray_3, thickness_pt=1.5)

    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)


# ── schema registration (self-contained; avoids editing validation.py and
#    lets parallel workers add charts conflict-free) ──
from deck_system.builder.validation import _baseline, _S  # noqa: E402

_baseline("scenario_summary",
          _S("scenarios", required=True, type=list),
          _S("metrics", required=True, type=list),
          example={"title": "시나리오 분석",
                   "scenarios": ["Downside", "Base", "Upside"],
                   "metrics": [
                       {"label": "매출", "values": [1100, 1300, 1500], "unit": "억"},
                       {"label": "영업이익", "values": [120, 180, 250], "unit": "억"},
                       {"label": "영업이익률", "values": [10.9, 13.8, 16.7], "unit": "%"}]})
