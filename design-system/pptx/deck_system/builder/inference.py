"""infer_slide_type(spec) — pick a layout from the spec shape.

FP&A-specific signatures take precedence (waterfall items have `type`,
variance items have `budget`/`actual`, etc).  Falls through to seulee26-style
generic detection.

v0.2 (Session B Track 1): added inference for chart layouts, RAG, harvey ball,
SWOT, BCG, prioritization, risk_matrix, comparison, pros_cons, before_after,
stats, trends, areas, venn, phases/steps/value_chain/funnel/pyramid/gantt/waves/cycle,
org_chart, pareto, gauge.
"""
from __future__ import annotations
from typing import Any


# Slide types that take "type" verbatim (no items array to confuse with)
_PASS_THROUGH_TYPES = {
    "cover", "section_divider", "closing", "dark_navy_summary",
    "toc", "agenda", "key_takeaway", "executive_summary",
    "two_column_text", "swot", "bcg_matrix", "prioritization_matrix",
    "risk_matrix", "comparison_table", "pros_cons", "before_after",
    "two_stat", "three_stat", "three_trends", "five_key_areas", "venn",
    "phases_chevron", "vertical_steps", "value_chain", "funnel", "pyramid",
    "gantt_timeline", "waves_timeline", "cycle", "org_chart",
    "pareto", "gauge",
    "column_historic_forecast", "column_simple_growth", "line_chart",
    "stacked_column", "grouped_column",
    "rag_status", "harvey_ball_table",
    # V2.1 additions
    "table_insight", "meet_the_team", "case_study", "action_items",
    "timeline", "side_by_side", "four_column", "stakeholder_map",
    "decision_tree",
    # V2.2 additions
    "horizontal_bar", "metric_cards", "stacked_area", "bubble",
    "dashboard_kpi", "dashboard_table", "numbered_list_panel", "gauge_pair",
    # V2.3-A additions
    "scorecard", "checklist", "temple", "pie", "appendix_title",
    "three_images", "two_col_image_grid", "metric_comparison",
}


def infer_slide_type(spec: dict) -> str:
    """Return a registry name based on which keys are present."""
    if not isinstance(spec, dict):
        raise TypeError(f"spec must be a dict, got {type(spec).__name__}")

    # Explicit type field is authoritative
    if "type" in spec and isinstance(spec["type"], str):
        return spec["type"]

    # ── FP&A priority signatures ───────────────────────────────────────
    items = spec.get("items")
    if isinstance(items, list) and items and isinstance(items[0], dict):
        first = items[0]
        if first.get("type") in ("base", "up", "down", "subtotal"):
            return "waterfall"
        if "budget" in first and "actual" in first:
            return "variance_table"
        if "cells" in first:
            return "data_table"
        if "value" in first and "label" in first and len(items) > 0 and \
                any("value" in i and "label" in i for i in items):
            return "pareto"

    if "kpis" in spec and isinstance(spec["kpis"], list):
        return "kpi_dashboard"

    if "segments" in spec and "center_value" in spec:
        return "donut"

    if "number" in spec and "title" in spec:
        return "big_number"

    # ── Track 1 signatures ─────────────────────────────────────────────
    if "stats" in spec:
        n = len(spec.get("stats", []))
        return "three_stat" if n >= 3 else "two_stat"

    if "trends" in spec:
        return "three_trends"

    if "areas" in spec:
        return "five_key_areas"

    if "circles" in spec:
        return "venn"

    if "steps" in spec:
        # process: phases_chevron if horizontal-ish (≤5), else vertical_steps
        return "vertical_steps" if len(spec.get("steps", [])) > 5 else "phases_chevron"

    if "stages" in spec:
        # value_chain has stages[].label; funnel has stages[].value or .conversion
        first = spec["stages"][0] if spec.get("stages") else {}
        if "conversion" in first or "value" in first:
            return "funnel"
        return "value_chain"

    if "tiers" in spec:
        return "pyramid"

    if "waves" in spec:
        return "waves_timeline"

    if "periods" in spec and "tasks" in spec:
        return "gantt_timeline"

    if "root" in spec and "heads" in spec:
        return "org_chart"

    if "projects" in spec:
        return "rag_status"

    if "options" in spec and "criteria" in spec:
        # comparison_table has criteria[].values; harvey_ball has criteria[].scores
        first_c = spec["criteria"][0] if spec.get("criteria") else {}
        if "scores" in first_c:
            return "harvey_ball_table"
        return "comparison_table"

    if "pros" in spec and "cons" in spec:
        return "pros_cons"

    if "before" in spec and "after" in spec:
        return "before_after"

    if "strengths" in spec and "weaknesses" in spec:
        return "swot"

    if "stars" in spec or "cash_cows" in spec:
        return "bcg_matrix"

    if "quick_wins" in spec or "major_projects" in spec:
        return "prioritization_matrix"

    if "risks" in spec:
        return "risk_matrix"

    if "categories" in spec and "values" in spec and "forecast_from_index" in spec:
        return "column_historic_forecast"
    if "categories" in spec and "values" in spec:
        return "column_simple_growth"
    if "categories" in spec and "series" in spec:
        first_s = spec["series"][0] if spec.get("series") else {}
        # stacked_column vs grouped_column vs line_chart — default to grouped
        if "values" in first_s:
            return spec.get("chart_kind", "grouped_column")

    if "value" in spec and "label" in spec and "threshold_good" in spec:
        return "gauge"

    # ── V2.2 signatures ────────────────────────────────────────────────
    if "gauges" in spec:
        return "gauge_pair"
    if "cards" in spec:
        return "metric_cards"
    if "panel" in spec and "items" in spec and isinstance(spec.get("items"), list) and \
            spec["items"] and isinstance(spec["items"][0], str):
        return "numbered_list_panel"
    if "factoids" in spec:
        return "dashboard_table"
    if "chart_caption" in spec and "kpis" in spec:
        return "dashboard_kpi"
    if "points" in spec:
        return "bubble"

    # ── V2.3-A signatures ──────────────────────────────────────────────
    if "rows" in spec and isinstance(spec.get("rows"), list) and \
            spec["rows"] and isinstance(spec["rows"][0], dict) and \
            "done" in spec["rows"][0]:
        return "checklist"
    if "metrics" in spec and isinstance(spec.get("metrics"), list) and \
            spec["metrics"] and isinstance(spec["metrics"][0], dict) and \
            "before" in spec["metrics"][0]:
        return "metric_comparison"
    if "roof" in spec and "pillars" in spec:
        return "temple"
    if "segments" in spec and "center_value" not in spec:
        return "pie"
    if "images" in spec:
        return "three_images"
    if "items" in spec and isinstance(spec.get("items"), list) and \
            spec["items"] and isinstance(spec["items"][0], dict) and \
            "image_label" in spec["items"][0]:
        return "two_col_image_grid"
    if "items" in spec and isinstance(spec.get("items"), list) and \
            spec["items"] and isinstance(spec["items"][0], dict) and \
            "score" in spec["items"][0]:
        return "scorecard"
    if spec.get("label") == "APPENDIX" or "appendix" in str(spec.get("title", "")).lower():
        return "appendix_title"

    # ── V2.1 signatures ────────────────────────────────────────────────
    if "milestones" in spec:
        return "timeline"
    if "members" in spec:
        return "meet_the_team"
    if "actions" in spec:
        return "action_items"
    if "sections" in spec:
        return "case_study"
    if "stakeholders" in spec:
        return "stakeholder_map"
    if "branches" in spec and "root" in spec:
        return "decision_tree"
    if "headers" in spec and "rows" in spec and "insights" in spec:
        return "table_insight"
    if "options" in spec and len(spec.get("options", [])) == 2 and \
            not "criteria" in spec:
        return "side_by_side"
    if "items" in spec and isinstance(spec["items"], list) and \
            spec["items"] and isinstance(spec["items"][0], (list, tuple)) and \
            len(spec["items"][0]) == 3:
        return "four_column"

    if "columns" in spec and isinstance(spec.get("columns"), list) and \
            "items" not in spec and "kpis" not in spec:
        return "two_column_text"

    raise ValueError(
        f"Cannot infer slide type from spec keys: {list(spec.keys())}"
    )
