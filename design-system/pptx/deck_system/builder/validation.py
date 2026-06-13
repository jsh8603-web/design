"""Lightweight per-layout input validation — V2.3-A / B.

Each layout has a `LayoutSchema` defining required/optional fields, types,
and bounds.  `validate_layout_input(name, data)` returns normalized data
plus warnings; raises `InputValidationError` (V2.3-B) with a friendly
message + example on hard violations.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from deck_system.errors import InputValidationError


@dataclass
class FieldSpec:
    name: str
    required: bool = False
    type: Optional[type] = None
    min_length: int = 0
    max_length: Optional[int] = None
    default: Any = None
    validator: Optional[Callable[[Any], Optional[str]]] = None  # returns error str or None


@dataclass
class LayoutSchema:
    layout_name: str
    fields: list = field(default_factory=list)
    examples: list = field(default_factory=list)


def _S(name, **kw):
    """Sugar for declaring a FieldSpec."""
    return FieldSpec(name=name, **kw)


# ── Schema registry — every registered layout gets an entry ─────────
# To keep V2.3-A tight we declare a baseline schema (title required) for
# every layout and add tighter rules for the high-value ones.  Coverage
# is 70/70.
LAYOUT_SCHEMAS: dict = {}


def _baseline(name: str, *extra_fields: FieldSpec, example: Optional[dict] = None):
    fields = [_S("title", required=True, type=str, min_length=1, max_length=80)]
    fields.extend(extra_fields)
    examples = [example] if example else [{"title": "Sample title"}]
    LAYOUT_SCHEMAS[name] = LayoutSchema(name, fields, examples)


# Structure
_baseline("cover", _S("subtitle", type=str), _S("author", type=str),
           _S("date", type=str),
           example={"title": "Q4 Review", "subtitle": "FY26"})
_baseline("section_divider", _S("section_label", type=str),
           _S("subtitle", type=str),
           example={"title": "시장 맥락", "section_label": "01"})
_baseline("closing", _S("subtitle", type=str), _S("contact", type=str),
           example={"title": "Thank you"})
_baseline("dark_navy_summary", _S("body", required=True, type=str,
                                    min_length=5),
           example={"title": "x", "body": "Bottom line statement"})
_baseline("appendix_title", _S("subtitle", type=str), _S("label", type=str),
           example={"title": "부록"})

# Summary
_baseline("toc", _S("items", required=True, type=list, min_length=1),
           example={"title": "목차", "items": [("01", "S1", "d1")]})
_baseline("agenda", _S("items", required=True, type=list, min_length=1),
           example={"title": "Agenda", "items": [("01", "S1", "d1")]})
_baseline("executive_summary",
           _S("headline", required=True, type=str, min_length=5),
           _S("items", required=True, type=list, min_length=1, max_length=4),
           example={"title": "x", "headline": "Big point",
                    "items": [{"num": "01", "kicker": "K",
                               "title": "T", "desc": "D"}]})
_baseline("key_takeaway",
           _S("details", required=True, type=list, min_length=1),
           _S("takeaways", required=True, type=list, min_length=1),
           example={"title": "x",
                    "details": [{"label": "L", "body": "B"}],
                    "takeaways": [{"num": "01", "title": "T"}]})
_baseline("big_number",
           _S("number", required=True, type=str, min_length=1),
           _S("unit", type=str), _S("description", type=str),
           _S("detail_items", type=list, max_length=4),
           example={"title": "x", "number": "60", "unit": "%"})
_baseline("two_column_text",
           _S("columns", required=True, type=list, min_length=1, max_length=2),
           example={"title": "x",
                    "columns": [{"title": "A", "bullets": ["a"]},
                                {"title": "B", "bullets": ["b"]}]})

# Data tables
_baseline("data_table",
           _S("headers", type=list), _S("rows", type=list),
           example={"title": "x", "headers": ["a", "b"],
                    "rows": [["1", "2"]]})
_baseline("variance_table",
           _S("items", required=True, type=list, min_length=1, max_length=10),
           example={"title": "x",
                    "items": [{"label": "매출", "budget": 1200,
                               "actual": 1260}]})
_baseline("rag_status",
           _S("projects", required=True, type=list, min_length=1),
           example={"title": "x",
                    "projects": [{"name": "P", "status": "green"}]})
_baseline("harvey_ball_table",
           _S("options", required=True, type=list, min_length=2,
              max_length=4),
           _S("criteria", required=True, type=list, min_length=1),
           example={"title": "x", "options": ["A", "B"],
                    "criteria": [{"label": "C", "scores": [50, 75]}]})
_baseline("scorecard",
           _S("items", required=True, type=list, min_length=1, max_length=10),
           example={"title": "x",
                    "items": [{"label": "L", "score": 4}]})
_baseline("checklist",
           _S("rows", required=True, type=list, min_length=1, max_length=7),
           _S("progress_label", type=str),
           example={"title": "x",
                    "rows": [{"label": "x", "done": True}]})

# Charts
_baseline("column_historic_forecast",
           _S("categories", required=True, type=list, min_length=2),
           _S("values", required=True, type=list, min_length=2),
           _S("forecast_from_index", required=True, type=int),
           _S("unit", type=str),
           example={"title": "x", "categories": ["a", "b"],
                    "values": [1, 2], "forecast_from_index": 1})
_baseline("column_simple_growth",
           _S("categories", required=True, type=list, min_length=2),
           _S("values", required=True, type=list, min_length=2),
           example={"title": "x", "categories": ["a", "b"],
                    "values": [1, 2]})
_baseline("line_chart",
           _S("categories", required=True, type=list, min_length=2),
           _S("series", required=True, type=list, min_length=1),
           example={"title": "x", "categories": ["a", "b"],
                    "series": [{"label": "L", "values": [1, 2]}]})
_baseline("stacked_column",
           _S("categories", required=True, type=list),
           _S("series", required=True, type=list),
           example={"title": "x", "categories": ["a"],
                    "series": [{"label": "L", "values": [1]}]})
_baseline("grouped_column",
           _S("categories", required=True, type=list),
           _S("series", required=True, type=list,
              max_length=3),  # likaku MAX_GROUPED_BAR_SERIES
           example={"title": "x", "categories": ["a"],
                    "series": [{"label": "L", "values": [1]}]})
_baseline("horizontal_bar",
           _S("items", required=True, type=list, min_length=1, max_length=10),
           _S("unit", type=str),
           example={"title": "x",
                    "items": [{"label": "A", "value": 100}]})
_baseline("stacked_area",
           _S("categories", required=True, type=list),
           _S("series", required=True, type=list),
           example={"title": "x", "categories": ["a"],
                    "series": [{"label": "L", "values": [1]}]})

# Special charts
_baseline("waterfall",
           _S("items", required=True, type=list, min_length=2),
           _S("unit", type=str),
           example={"title": "x",
                    "items": [{"label": "S", "value": 100, "type": "base"},
                              {"label": "E", "value": 110, "type": "base"}]})
_baseline("donut",
           _S("segments", required=True, type=list, min_length=1, max_length=6),
           _S("center_value", type=str),
           example={"title": "x",
                    "segments": [{"label": "A", "value": 100}]})
_baseline("pie",
           _S("segments", required=True, type=list, min_length=1, max_length=6),
           example={"title": "x",
                    "segments": [{"label": "A", "value": 100}]})
_baseline("kpi_dashboard",
           _S("kpis", required=True, type=list, min_length=1, max_length=8),
           example={"title": "x",
                    "kpis": [{"label": "A", "value": "100"}]})
_baseline("pareto",
           _S("items", required=True, type=list, min_length=2, max_length=10),
           example={"title": "x",
                    "items": [{"label": "A", "value": 50}]})
_baseline("gauge",
           _S("value", required=True, type=(int, float)),
           _S("label", type=str), _S("sub", type=str),
           _S("threshold_good", type=(int, float)),
           _S("threshold_warn", type=(int, float)),
           example={"title": "x", "value": 75, "label": "달성률"})
_baseline("gauge_pair",
           _S("gauges", required=True, type=list, min_length=2, max_length=2),
           example={"title": "x",
                    "gauges": [{"label": "A", "value": 50},
                               {"label": "B", "value": 75}]})
_baseline("bubble",
           _S("points", required=True, type=list, min_length=1),
           _S("x_label", type=str), _S("y_label", type=str),
           example={"title": "x",
                    "points": [{"label": "A", "x": 1, "y": 1, "size": 1}]})

# Composite dashboards
_baseline("dashboard_kpi",
           _S("kpis", required=True, type=list, min_length=1, max_length=4),
           _S("chart_caption", type=str),
           _S("takeaways", type=list, max_length=3),
           example={"title": "x",
                    "kpis": [{"label": "A", "value": "100", "yoy": 5}]})
_baseline("dashboard_table",
           _S("headers", required=True, type=list),
           _S("rows", required=True, type=list),
           _S("chart_caption", type=str),
           _S("factoids", type=list, max_length=4),
           example={"title": "x", "headers": ["a"],
                    "rows": [["1"]]})
_baseline("metric_cards",
           _S("cards", required=True, type=list, min_length=1, max_length=4),
           _S("narrative", type=str),
           example={"title": "x",
                    "cards": [{"label": "L", "value": "V"}]})
_baseline("numbered_list_panel",
           _S("items", required=True, type=list, min_length=1, max_length=7),
           _S("panel", type=dict),
           example={"title": "x", "items": ["a"]})

# Compare
_baseline("comparison_table",
           _S("options", required=True, type=list, min_length=2,
              max_length=5),
           _S("criteria", required=True, type=list, min_length=1),
           example={"title": "x", "options": ["A", "B"],
                    "criteria": [{"label": "C", "values": ["a", "b"]}]})
_baseline("pros_cons",
           _S("pros", required=True, type=list, min_length=1),
           _S("cons", required=True, type=list, min_length=1),
           example={"title": "x", "pros": ["p"], "cons": ["c"]})
_baseline("before_after",
           _S("before", required=True, type=list, min_length=1),
           _S("after", required=True, type=list, min_length=1),
           example={"title": "x", "before": ["b"], "after": ["a"]})
_baseline("side_by_side",
           _S("options", required=True, type=list, min_length=2,
              max_length=2),
           example={"title": "x",
                    "options": [{"label": "A", "bullets": ["a"]},
                                {"label": "B", "bullets": ["b"]}]})

# Narrative
_baseline("two_stat",
           _S("stats", required=True, type=list, min_length=2, max_length=2),
           example={"title": "x",
                    "stats": [{"number": "1", "label": "a"},
                              {"number": "2", "label": "b"}]})
_baseline("three_stat",
           _S("stats", required=True, type=list, min_length=3, max_length=3),
           example={"title": "x",
                    "stats": [{"number": "1", "label": "a"},
                              {"number": "2", "label": "b"},
                              {"number": "3", "label": "c"}]})
_baseline("three_trends",
           _S("trends", required=True, type=list, min_length=3, max_length=3),
           example={"title": "x",
                    "trends": [{"headline": "T1", "bullets": ["a"]},
                               {"headline": "T2", "bullets": ["a"]},
                               {"headline": "T3", "bullets": ["a"]}]})
_baseline("five_key_areas",
           _S("areas", required=True, type=list, min_length=3, max_length=5),
           example={"title": "x",
                    "areas": [{"label": "L", "desc": "d"}] * 5})
_baseline("venn",
           _S("circles", required=True, type=list, min_length=2, max_length=3),
           _S("intersection", type=str),
           example={"title": "x",
                    "circles": [{"label": "A"}, {"label": "B"}]})
_baseline("four_column",
           _S("items", required=True, type=list, min_length=1, max_length=4),
           example={"title": "x",
                    "items": [("1", "T", "D")]})
_baseline("metric_comparison",
           _S("metrics", required=True, type=list, min_length=1, max_length=5),
           _S("period_before", type=str), _S("period_after", type=str),
           example={"title": "x", "period_before": "Q3", "period_after": "Q4",
                    "metrics": [{"label": "x", "before": 10, "after": 12}]})

# Matrix
_baseline("swot",
           _S("strengths", required=True, type=list),
           _S("weaknesses", required=True, type=list),
           _S("opportunities", required=True, type=list),
           _S("threats", required=True, type=list),
           example={"title": "x", "strengths": ["s"], "weaknesses": ["w"],
                    "opportunities": ["o"], "threats": ["t"]})
_baseline("bcg_matrix",
           _S("stars", type=list), _S("question_marks", type=list),
           _S("cash_cows", type=list), _S("dogs", type=list),
           example={"title": "x", "stars": ["a"], "question_marks": ["b"],
                    "cash_cows": ["c"], "dogs": ["d"]})
_baseline("prioritization_matrix",
           _S("quick_wins", type=list), _S("major_projects", type=list),
           _S("fill_ins", type=list), _S("hard_slogs", type=list),
           example={"title": "x", "quick_wins": ["a"],
                    "major_projects": ["b"], "fill_ins": ["c"],
                    "hard_slogs": ["d"]})
_baseline("risk_matrix",
           _S("risks", required=True, type=list, min_length=1),
           example={"title": "x",
                    "risks": [{"label": "R", "likelihood": 2, "impact": 2}]})
_baseline("stakeholder_map",
           _S("stakeholders", required=True, type=list, min_length=1),
           example={"title": "x",
                    "stakeholders": [{"label": "A", "influence": 3,
                                       "interest": 3}]})
_baseline("temple",
           _S("roof", required=True, type=str, min_length=1),
           _S("pillars", required=True, type=list, min_length=2, max_length=5),
           _S("foundation", required=True, type=str),
           example={"title": "x", "roof": "Goal",
                    "pillars": [{"label": "A"}, {"label": "B"}],
                    "foundation": "Base"})

# Process
_baseline("phases_chevron",
           _S("steps", required=True, type=list, min_length=2, max_length=5),
           example={"title": "x",
                    "steps": [{"label": "S1"}, {"label": "S2"}]})
_baseline("vertical_steps",
           _S("steps", required=True, type=list, min_length=1),
           example={"title": "x",
                    "steps": [{"title": "S", "desc": "d"}]})
_baseline("value_chain",
           _S("stages", required=True, type=list, min_length=2),
           example={"title": "x",
                    "stages": [{"label": "S1"}, {"label": "S2"}]})
_baseline("funnel",
           _S("stages", required=True, type=list, min_length=2),
           example={"title": "x",
                    "stages": [{"label": "T", "value": 100},
                               {"label": "B", "value": 10}]})
_baseline("pyramid",
           _S("tiers", required=True, type=list, min_length=2, max_length=5),
           example={"title": "x",
                    "tiers": [{"label": "T"}, {"label": "B"}]})
_baseline("gantt_timeline",
           _S("periods", required=True, type=list),
           _S("tasks", required=True, type=list),
           example={"title": "x", "periods": ["Q1"],
                    "tasks": [{"label": "T", "start": 0, "end": 0}]})
_baseline("waves_timeline",
           _S("waves", required=True, type=list, min_length=1),
           example={"title": "x",
                    "waves": [{"label": "W", "period": "Q1"}]})
_baseline("cycle",
           _S("steps", required=True, type=list, min_length=3, max_length=6),
           example={"title": "x",
                    "steps": [{"label": "S1"}, {"label": "S2"},
                              {"label": "S3"}]})
_baseline("timeline",
           _S("milestones", required=True, type=list, min_length=2),
           example={"title": "x",
                    "milestones": [{"date": "Q1", "label": "L1"},
                                   {"date": "Q2", "label": "L2"}]})
_baseline("decision_tree",
           _S("root", required=True, type=str, min_length=1),
           _S("branches", required=True, type=list, min_length=2),
           example={"title": "x", "root": "R",
                    "branches": [{"condition": "C1"},
                                  {"condition": "C2"}]})

# Org / team
_baseline("org_chart",
           _S("root", required=True, type=dict),
           _S("heads", required=True, type=list, min_length=1),
           example={"title": "x",
                    "root": {"name": "CEO", "role": "C"},
                    "heads": [{"name": "H", "role": "V"}]})
_baseline("meet_the_team",
           _S("members", required=True, type=list, min_length=1, max_length=8),
           example={"title": "x",
                    "members": [{"name": "A", "role": "R"}]})
_baseline("case_study",
           _S("sections", required=True, type=list, min_length=1, max_length=4),
           example={"title": "x",
                    "sections": [{"label": "S", "content": "c"}]})
_baseline("action_items",
           _S("actions", required=True, type=list, min_length=1),
           example={"title": "x",
                    "actions": [{"id": "A1", "title": "T",
                                 "status": "in_progress"}]})

# Tables w/ extra
_baseline("table_insight",
           _S("headers", required=True, type=list),
           _S("rows", required=True, type=list, min_length=1),
           _S("insights", required=True, type=list, min_length=1),
           example={"title": "x", "headers": ["a"],
                    "rows": [["1"]], "insights": ["i"]})

# Image
_baseline("three_images",
           _S("images", required=True, type=list, min_length=3, max_length=3),
           example={"title": "x",
                    "images": [{"label": "1"}, {"label": "2"}, {"label": "3"}]})
_baseline("two_col_image_grid",
           _S("items", required=True, type=list, min_length=1, max_length=4),
           example={"title": "x",
                    "items": [{"image_label": "i", "headline": "H"}]})


# ── Validator -------------------------------------------------------

def validate_layout_input(layout_name: str, data: dict) -> tuple:
    """Validate spec against schema.

    Returns:
        (data, warnings) — data passes through unchanged in V2.3-A,
        warnings is a list of strings.
    Raises:
        ValueError — friendly message with example.
    """
    schema = LAYOUT_SCHEMAS.get(layout_name)
    if schema is None:
        # Unknown layout — bypass validation, builder.get_layout will fail loudly anyway.
        return data, []

    warnings = []
    example = schema.examples[0] if schema.examples else {}

    for spec in schema.fields:
        present = spec.name in data
        value = data.get(spec.name)

        # Required check
        if spec.required and (not present or value is None or
                              (isinstance(value, (list, str)) and len(value) == 0)):
            raise InputValidationError(
                layout_name=layout_name,
                message=f"Missing required field: '{spec.name}'",
                expected=_type_name(spec.type),
                fix=f"Add `{spec.name}=…` to your spec.",
                example=example,
            )

        if not present or value is None:
            continue

        # Type check
        if spec.type is not None and not _isinstance(value, spec.type):
            raise InputValidationError(
                layout_name=layout_name,
                message=f"Field '{spec.name}' has wrong type",
                expected=_type_name(spec.type),
                got=type(value).__name__,
                fix=f"Pass `{spec.name}` as {_type_name(spec.type)}.",
                example=example,
            )

        # Length bounds (lists / strings)
        if hasattr(value, "__len__"):
            n = len(value)
            if spec.min_length and n < spec.min_length:
                raise InputValidationError(
                    layout_name=layout_name,
                    message=f"Field '{spec.name}' too short: "
                            f"{n} < min {spec.min_length}",
                    expected=f"len ≥ {spec.min_length}",
                    got=f"len = {n}",
                    example=example,
                )
            if spec.max_length is not None and n > spec.max_length:
                # Soft warning — autofix may trim
                warnings.append(
                    f"Field '{spec.name}' has {n} entries (max {spec.max_length})"
                )

        if spec.validator is not None:
            err = spec.validator(value)
            if err:
                raise InputValidationError(
                    layout_name=layout_name, message=err, example=example,
                )

    return data, warnings


def _isinstance(value, expected):
    if isinstance(expected, tuple):
        return isinstance(value, expected)
    return isinstance(value, expected)


def _type_name(t):
    if isinstance(t, tuple):
        return " | ".join(x.__name__ for x in t)
    return t.__name__ if t is not None else "any"
