"""Variance calculation + color-coding.

EXACT 1:1 match with HTML `assets/variance-table.js`.  Any change here
must be mirrored in the HTML file (or vice versa) — both systems share
this contract via the FP&A spec.

cost_nature flag semantics:
    - cost_nature=True  →  positive variance reads as NEGATIVE (cost up = bad)
    - cost_nature=False →  positive variance reads as POSITIVE
"""
from __future__ import annotations
from typing import Optional


def compute_variance(item: dict) -> tuple[float, Optional[float]]:
    """Returns (variance_abs, variance_pct).  pct is None if budget == 0."""
    budget = float(item["budget"])
    actual = float(item["actual"])
    abs_var = actual - budget
    pct_var = (abs_var / budget * 100.0) if budget != 0 else None
    return abs_var, pct_var


def resolve_variance_color(
    item: dict,
    variance_pct: Optional[float],
    theme,
    neutral_threshold_pct: float = 0.0,
) -> str:
    """Decide which palette color the variance cell should use.

    Mirrors HTML's variance-table.js:
        for cost_nature items, the sign is flipped before comparing
        against the neutral dead-band.

    Returns a hex color string from theme.palette.
    """
    if variance_pct is None:
        return theme.palette.gray_2

    is_cost = bool(item.get("cost_nature", False))
    effective = -variance_pct if is_cost else variance_pct

    if effective > neutral_threshold_pct:
        return theme.palette.positive
    if effective < -neutral_threshold_pct:
        return theme.palette.negative
    return theme.palette.gray_2


def resolve_variance_state(
    item: dict,
    variance_pct: Optional[float],
    neutral_threshold_pct: float = 0.0,
) -> str:
    """String state ('positive' / 'negative' / 'neutral') — for labels.

    Same sign-flip semantics as resolve_variance_color.
    """
    if variance_pct is None:
        return "neutral"
    is_cost = bool(item.get("cost_nature", False))
    effective = -variance_pct if is_cost else variance_pct
    if effective > neutral_threshold_pct:
        return "positive"
    if effective < -neutral_threshold_pct:
        return "negative"
    return "neutral"
