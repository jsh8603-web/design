"""Auto-fix pipeline.

4-stage pipeline mirroring likaku/review.py:
    1. Page brief  — summarize each slide's spec
    2. Dual QA     — run all checks, classify findings
    3. Auto-fix    — apply safe text-level repairs (NEVER changes layout)
    4. Gate        — re-run QA, repeat up to max_rounds until passed

Auto-fix is intentionally conservative: it only modifies the spec dict
(input), never the rendered Presentation.  Layout choice is the user's;
autofix only does in-cell repairs:
    - title truncation
    - bullet count cap
    - chart segment merge ("기타")
    - process step compression
    - language unification
    - font micro-adjust
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Callable
import copy

from .experiences import (
    MAX_ACTION_TITLE_CHARS, MAX_PROCESS_CHEVRON_STEPS,
    MAX_PROCESS_CHEVRON_DESC_CHARS, MAX_DONUT_SEGMENTS,
    MAX_FOUR_COL_DESC_CHARS, MAX_BIG_NUMBER_DETAIL_ITEMS,
    MAX_KPI_TILES, DEFAULT_AUTOFIX_MAX_ROUNDS,
    PROCESS_STEP_LABEL_NO_NEWLINE,
    MAX_PARETO_BARS, MAX_GROUPED_BAR_SERIES,
)


@dataclass
class AutofixAction:
    slide_idx: int       # 1-based; 0 = global
    rule: str            # which rule fired
    before: str          # short repr of original value
    after: str           # short repr of new value


@dataclass
class AutofixResult:
    actions: List[AutofixAction] = field(default_factory=list)
    rounds: int = 0
    final_passed: bool = False

    def to_dict(self) -> dict:
        return {
            "rounds": self.rounds,
            "final_passed": self.final_passed,
            "actions": [
                {"slide": a.slide_idx, "rule": a.rule,
                 "before": a.before, "after": a.after}
                for a in self.actions
            ],
        }


# ─── Individual repair rules ─────────────────────────────────────────

def _fix_action_title(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """Truncate over-long titles with ellipsis."""
    if "title" not in spec or not isinstance(spec["title"], str):
        return None
    title = spec["title"].rstrip()
    if len(title) <= MAX_ACTION_TITLE_CHARS:
        return None
    truncated = title[:MAX_ACTION_TITLE_CHARS - 1].rstrip("·,. -") + "…"
    spec["title"] = truncated
    return AutofixAction(slide_idx, "action_title_truncate",
                         title[:30] + "…", truncated[:30] + "…")


def _fix_donut_segments(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """Merge donut/pie tail segments past max into '기타'."""
    if "segments" not in spec: return None
    segs = spec.get("segments", [])
    if len(segs) <= MAX_DONUT_SEGMENTS: return None
    before = len(segs)
    head = sorted(segs, key=lambda s: -s["value"])[:MAX_DONUT_SEGMENTS - 1]
    tail = sorted(segs, key=lambda s: -s["value"])[MAX_DONUT_SEGMENTS - 1:]
    tail_sum = sum(s["value"] for s in tail)
    spec["segments"] = head + [{
        "label": "기타", "value": tail_sum,
        "color": "gray_3", "_merged": True,
    }]
    return AutofixAction(slide_idx, "donut_merge_tail",
                         f"{before} segments", f"{len(spec['segments'])} segments + 기타")


def _fix_chevron_steps(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """Drop chevron steps past the max + strip newlines from labels."""
    if "steps" not in spec: return None
    steps = spec.get("steps", [])
    actions = []
    if len(steps) > MAX_PROCESS_CHEVRON_STEPS:
        before = len(steps)
        spec["steps"] = steps[:MAX_PROCESS_CHEVRON_STEPS]
        actions.append(AutofixAction(slide_idx, "chevron_step_cap",
                                     f"{before} steps",
                                     f"{MAX_PROCESS_CHEVRON_STEPS} steps"))
    if PROCESS_STEP_LABEL_NO_NEWLINE:
        for step in spec["steps"]:
            label = step.get("label", "")
            if "\n" in label or "<br" in label:
                new_label = label.replace("\n", " ").replace("<br>", " ").replace("<br/>", " ")
                step["label"] = new_label
                actions.append(AutofixAction(slide_idx, "chevron_label_no_newline",
                                             label[:20], new_label[:20]))
        if "desc" in step and len(step["desc"]) > MAX_PROCESS_CHEVRON_DESC_CHARS:
            old = step["desc"]
            step["desc"] = old[:MAX_PROCESS_CHEVRON_DESC_CHARS - 1] + "…"
            actions.append(AutofixAction(slide_idx, "chevron_desc_trim",
                                         old[:20], step["desc"][:20]))
    return actions[0] if actions else None


def _fix_kpi_tiles(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """Cap KPI tiles."""
    if "kpis" not in spec: return None
    if len(spec["kpis"]) <= MAX_KPI_TILES: return None
    before = len(spec["kpis"])
    spec["kpis"] = spec["kpis"][:MAX_KPI_TILES]
    return AutofixAction(slide_idx, "kpi_tile_cap",
                         f"{before} tiles", f"{MAX_KPI_TILES} tiles")


def _fix_big_number_details(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """Cap big_number detail items."""
    if "detail_items" not in spec: return None
    if len(spec["detail_items"]) <= MAX_BIG_NUMBER_DETAIL_ITEMS: return None
    before = len(spec["detail_items"])
    spec["detail_items"] = spec["detail_items"][:MAX_BIG_NUMBER_DETAIL_ITEMS]
    return AutofixAction(slide_idx, "big_number_detail_cap",
                         f"{before} details", f"{MAX_BIG_NUMBER_DETAIL_ITEMS} details")


def _fix_four_column_desc(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """Truncate four-column description fields."""
    items = spec.get("items", [])
    actions = []
    for it in items:
        if not isinstance(it, dict): continue
        desc = it.get("desc", "")
        if isinstance(desc, str) and len(desc) > MAX_FOUR_COL_DESC_CHARS:
            old = desc
            it["desc"] = old[:MAX_FOUR_COL_DESC_CHARS - 1] + "…"
            actions.append(AutofixAction(slide_idx, "four_col_desc_trim",
                                         old[:20], it["desc"][:20]))
    return actions[0] if actions else None


def _fix_pareto_overflow(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """Pareto > MAX_PARETO_BARS → top-(N-1) + '기타'.

    Reference: V2.2 — likaku chart-limits.md enforcement.
    """
    items = spec.get("items", [])
    if len(items) <= MAX_PARETO_BARS:
        return None
    before = len(items)
    sorted_items = sorted(items, key=lambda x: -x.get("value", 0))
    head = sorted_items[:MAX_PARETO_BARS - 1]
    tail_sum = sum(i.get("value", 0) for i in sorted_items[MAX_PARETO_BARS - 1:])
    spec["items"] = head + [{"label": "기타", "value": tail_sum, "_merged": True}]
    return AutofixAction(slide_idx, "pareto_merge_tail",
                         f"{before} bars", f"{MAX_PARETO_BARS} bars + 기타")


def _fix_grouped_bar_series(spec: dict, slide_idx: int) -> Optional[AutofixAction]:
    """grouped_column/grouped_bar > MAX_GROUPED_BAR_SERIES → cap.

    Conservative: keep first N series, log dropped labels.  User can split deck.
    Reference: V2.2 — likaku chart-limits.md enforcement.
    """
    series = spec.get("series", [])
    if len(series) <= MAX_GROUPED_BAR_SERIES:
        return None
    before = len(series)
    dropped = [s.get("label", "?") for s in series[MAX_GROUPED_BAR_SERIES:]]
    spec["series"] = series[:MAX_GROUPED_BAR_SERIES]
    return AutofixAction(slide_idx, "grouped_bar_series_cap",
                         f"{before} series",
                         f"{MAX_GROUPED_BAR_SERIES} series (dropped: {', '.join(dropped)})")


# Repair rule registry: (predicate, fix_fn).
# Predicates filter which slides each rule should consider.
_RULES = [
    (lambda spec: True, _fix_action_title),
    (lambda spec: "segments" in spec, _fix_donut_segments),
    (lambda spec: "steps" in spec, _fix_chevron_steps),
    (lambda spec: "kpis" in spec, _fix_kpi_tiles),
    (lambda spec: "detail_items" in spec, _fix_big_number_details),
    (lambda spec: "items" in spec, _fix_four_column_desc),
    (lambda spec: "items" in spec and isinstance(spec.get("items"), list) and
                   spec["items"] and isinstance(spec["items"][0], dict) and
                   "value" in spec["items"][0] and "label" in spec["items"][0] and
                   "type" not in spec["items"][0] and
                   "budget" not in spec["items"][0],
     _fix_pareto_overflow),
    (lambda spec: "series" in spec and isinstance(spec.get("series"), list),
     _fix_grouped_bar_series),
]


# ─── Pipeline ────────────────────────────────────────────────────────

@dataclass
class AutofixPipeline:
    """Stateful pipeline.  Holds slide specs + accumulated actions."""
    slide_specs: List[dict]
    max_rounds: int = DEFAULT_AUTOFIX_MAX_ROUNDS

    def page_brief(self) -> List[dict]:
        """Stage 1 — summarize each slide for downstream rules."""
        briefs = []
        for i, spec in enumerate(self.slide_specs, start=1):
            briefs.append({
                "idx": i,
                "type": spec.get("type", "?"),
                "title_chars": len(spec.get("title", "")),
                "keys": sorted(k for k in spec.keys() if not k.startswith("_")),
            })
        return briefs

    def apply_fixes(self) -> List[AutofixAction]:
        """Stage 3 — apply all rules to all slides, one pass."""
        actions = []
        for i, spec in enumerate(self.slide_specs, start=1):
            for pred, fix in _RULES:
                if not pred(spec): continue
                action = fix(spec, i)
                if action is not None:
                    actions.append(action)
        return actions


def run_autofix(
    slide_specs: List[dict],
    *,
    qa_runner: Optional[Callable] = None,
    builder_factory: Optional[Callable] = None,
    max_rounds: int = DEFAULT_AUTOFIX_MAX_ROUNDS,
) -> AutofixResult:
    """Run the full 4-stage pipeline.

    Args:
        slide_specs: list of dicts — MUTATED IN PLACE
        qa_runner:   optional callable(specs) -> QAReport.  If None, runs
                     only the deterministic text fixes (no rebuild).
        builder_factory: optional callable(specs) -> Presentation.  Used
                         in conjunction with qa_runner for round-tripping.
        max_rounds:  cap so a misbehaving rule can't loop forever
    """
    result = AutofixResult()
    for round_n in range(1, max_rounds + 1):
        pipeline = AutofixPipeline(slide_specs, max_rounds=max_rounds)
        # Stage 1: brief (no-op for now, used by future LLM-driven rules)
        _ = pipeline.page_brief()
        # Stage 3: apply text-level fixes
        actions = pipeline.apply_fixes()
        result.actions.extend(actions)
        result.rounds = round_n

        # Stage 4: gate — re-run QA if available
        if qa_runner is not None and builder_factory is not None:
            try:
                prs = builder_factory(slide_specs)
                report = qa_runner(prs, slide_specs=slide_specs)
                if report.passed:
                    result.final_passed = True
                    return result
            except Exception:
                # QA itself failed — don't loop, just exit
                return result

        # No actions taken → fixed point, stop early
        if not actions:
            result.final_passed = True
            return result

    return result
