# QA + Auto-fix pipeline

Three layers, mirroring likaku/qa.py + review.py:

## 1. Experiences (`deck_system/qa/experiences.py`)

19 hard-won constants from likaku/experiences/*.md.  Examples:

```python
MAX_ACTION_TITLE_CHARS = 40         # overflow.md
MAX_DONUT_SEGMENTS = 6              # chart-limits.md
MAX_PROCESS_CHEVRON_STEPS = 5       # overflow.md
PROCESS_STEP_LABEL_NO_NEWLINE = True  # overflow.md
EA_FONT_REQUIRED_FOR_KOREAN = True  # cjk-issues.md
ALLOW_PRIMARY_FOR_FULL_BLEED = False # layout-pitfalls.md
ENGINE_BUG_WHITELIST = [...]        # whitelisted (info-level)
```

**Update protocol**: when a new failure mode is observed in real decks,
add a constant here + a check in checks.py.  Don't inline numbers in
layout code.

## 2. Checks (`deck_system/qa/checks.py`)

10 functions — 9 per-slide + 1 global:

| check | level | category | source |
|-------|-------|----------|--------|
| `_check_action_title` | warning | title_overflow | overflow.md |
| `_check_body_overflow` | error | geometry | overflow.md |
| `_check_text_overflow` | warning | geometry | overflow.md |
| `_check_whitespace` | error/warning | empty_slide | **parallels HTML data-rendered guard** |
| `_check_shape_overlap` | info | geometry | overflow.md |
| `_check_fonts` | error | cjk | cjk-issues.md |
| `_check_peer_font_consistency` | info | peer_font_inconsistency (whitelisted) | layout-pitfalls.md |
| `_check_chart_legend_overflow` | info | chart_legend_pixel_drift (whitelisted) | chart-limits.md |
| `_check_connectors` | error | file_corruption | layout-pitfalls.md |
| `_check_text_line_collision` | warning | geometry | layout-pitfalls.md |
| `_check_global_two_column_text` | warning | layout_overuse | layout-pitfalls.md |

`run_qa(prs, slide_specs=...)` returns a `QAReport` with `.errors`,
`.warnings`, `.infos`, `.passed`, and `.to_dict()` for JSON serialization.

Whitelisted categories (engine quirks, not user bugs) auto-demote to
`info` level so the gate doesn't fail on them.

### `_check_whitespace` ↔ HTML `data-rendered`

```python
def _check_whitespace(slide, idx, spec=None):
    """Slide dead-zone detection.

    Conceptually parallel to the HTML system's data-rendered guard:
    HTML: prevents un-rendered slide → JS pre-block
    PPTX: catches un-rendered slide → QA post-check
    Both encode 'a slide must not have a blank content area'.
    """
```

## 3. Autofix (`deck_system/qa/autofix.py`)

4-stage pipeline:

1. **Page brief** — summarize each slide spec (type, title length, keys)
2. **Dual QA** (optional; runs only if `qa_runner` provided)
3. **Auto-fix** — apply repair rules to spec dicts IN PLACE
4. **Gate** — re-run QA; repeat up to `max_rounds` until passed

### Repair rules (text-level only — NEVER changes layout choice)

| rule | what it does |
|------|--------------|
| `_fix_action_title` | Truncate w/ "…" if > MAX_ACTION_TITLE_CHARS |
| `_fix_donut_segments` | Merge tail past MAX_DONUT_SEGMENTS into "기타" |
| `_fix_chevron_steps` | Cap at MAX_PROCESS_CHEVRON_STEPS + strip `\n` from labels |
| `_fix_kpi_tiles` | Cap at MAX_KPI_TILES |
| `_fix_big_number_details` | Cap at MAX_BIG_NUMBER_DETAIL_ITEMS |
| `_fix_four_column_desc` | Truncate descriptions > MAX_FOUR_COL_DESC_CHARS |

Each rule returns an `AutofixAction(slide_idx, rule, before, after)` or
`None`.  Actions accumulate across rounds into `AutofixResult.actions`.

## Builder integration

```python
b = PresentationBuilder()
b.add_specs(specs)

# Run QA on buffered specs
report = b.run_qa()
print(report.errors)

# Apply autofix in-place
result = b.run_autofix(max_rounds=3)
for action in result.actions:
    print(f"  [{action.slide_idx}] {action.rule}: {action.before} → {action.after}")

# Save with QA report alongside
b.save("out.pptx", qa_report_path="out_qa.json", auto_fix=True)
```

## CLI

```bash
# Just build
fpna-deck --spec deck.json -o out.pptx

# Build + write QA report
fpna-deck --spec deck.json -o out.pptx --qa-report out_qa.json

# Autofix before build
fpna-deck --spec deck.json -o out.pptx --auto-fix --max-rounds 3
```
