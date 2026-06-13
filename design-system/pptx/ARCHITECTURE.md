# Architecture — Session B complete (v0.2)

Full 5-stage pipeline from JSON spec → editable .pptx.

```
┌─────────┐   ┌──────────┐   ┌────────────┐   ┌──────────┐   ┌─────────┐
│ Spec    │ → │ Normalize│ → │ Infer type │ → │ Render   │ → │ QA gate │
│ (JSON)  │   │ camel→sn │   │ FP&A first │   │ 45 layouts│  │ +autofix│
└─────────┘   └──────────┘   └────────────┘   └──────────┘   └─────────┘
                                                    ↓
                                              ┌──────────┐
                                              │ .pptx    │
                                              │ (editable│
                                              │  text+   │
                                              │  shapes) │
                                              └──────────┘
```

## Module map

```
pptx/
├── deck_system/
│   ├── tokens/                  Design tokens — 4 themes
│   │   ├── base.py              Palette / Typography / Layout dataclasses
│   │   ├── theme_modern.py      Default — slate navy + warm orange
│   │   ├── theme_classic.py     Deep McK navy + cyan
│   │   ├── theme_dark_mono.py   Dark surface + cold blue
│   │   └── theme_company.py     v3 slot, auto-filled by adapter
│   │
│   ├── helpers/                 Drawing primitives
│   │   ├── text.py              set_ea_font, set_run, write_paragraph
│   │   ├── shapes.py            add_rect/oval/hline/textbox/block_arc, _clean_shape
│   │   └── chrome.py            action_title, source, page_num, bottom_bar
│   │
│   ├── layouts/                 45 layout functions (Track 1)
│   │   ├── _variance_logic.py   ⭐ cost_nature flip (HTML 1:1)
│   │   ├── structure.py         cover, section_divider, closing, dark_navy_summary
│   │   ├── summary.py           toc, executive_summary, key_takeaway, big_number, two_column_text
│   │   ├── data_table.py        variance_table, data_table, rag_status, harvey_ball_table
│   │   ├── data_special.py      waterfall, donut, kpi_dashboard, pareto, gauge
│   │   ├── data_chart.py        column_historic_forecast, column_simple_growth, line, stacked, grouped
│   │   ├── compare.py           comparison_table, pros_cons, before_after
│   │   ├── narrative.py         two_stat, three_stat, three_trends, five_key_areas, venn
│   │   ├── matrix.py            swot, bcg_matrix, prioritization_matrix, risk_matrix
│   │   ├── process.py           phases_chevron, vertical_steps, value_chain, funnel, pyramid,
│   │   │                        gantt_timeline, waves_timeline, cycle
│   │   └── org.py               org_chart
│   │
│   ├── qa/                      Track 2 — QA + autofix
│   │   ├── experiences.py       19 hard-won constants
│   │   ├── checks.py            9 per-slide + 1 global checks
│   │   └── autofix.py           4-stage pipeline w/ 6 repair rules
│   │
│   ├── adapter/                 Track 3 — master adapter
│   │   ├── profile.py           Read .pptx → extract tokens dict
│   │   └── theme_from_profile.py Emit theme_company.py
│   │
│   ├── builder/                 Public API
│   │   ├── builder.py           PresentationBuilder w/ run_qa / run_autofix
│   │   ├── registry.py          @register decorator
│   │   ├── inference.py         FP&A-first key matching (45 layouts)
│   │   ├── spec_normalizer.py   HTML JSON camelCase ↔ snake_case
│   │   └── tone.py              명사형 종결 validator
│   │
│   └── cli.py                   --spec, --theme, --qa-report, --auto-fix
│
├── fonts/                       Pretendard 4 weights (SIL OFL)
│
├── examples/
│   ├── q4_review_korean.py      Session A Korean demo
│   ├── full_layout_showcase.py  Track 1 — every layout once (~38 slides)
│   ├── qa_demo.py               Track 2 — Before/After autofix
│   ├── waterfall_html_compat.json
│   ├── variance_table_cost_nature.json
│   └── outputs/                 .pptx artifacts
│
├── tests/
│   ├── test_variance_logic.py   cost_nature flip (Session A)
│   ├── test_tokens.py           surface_inverse divergence
│   ├── test_inference.py        FP&A signature matching
│   ├── test_html_compat.py      camelCase → snake_case
│   ├── test_tone.py             명사형 종결
│   ├── test_layouts_track1.py   30 smoke tests (Track 1)
│   ├── test_qa.py               experiences + autofix rules (Track 2)
│   └── test_adapter.py          profile + theme generation (Track 3)
│
└── docs/
    ├── layouts.md               45-layout catalog
    ├── qa.md                    QA + autofix pipeline
    └── adapter.md               Master adapter usage
```

## Critical invariants (still in force)

1. **JSON spec compatibility with HTML** — `spec_normalizer.normalize_spec()`
   handles camelCase ↔ snake_case so the same JSON drives both outputs.

2. **`surface_inverse` token** — every full-bleed slide and inset capsule
   references `palette.surface_inverse` (not `primary`).  Dark mode safety.

3. **`cost_nature` sign flip** — `_variance_logic.py` matches HTML
   `variance-table.js` exactly.  Single source of truth.

4. **EA font enforcement** — `set_run()` always calls `set_ea_font()`.
   No raw `font.name = ...` in layouts.

5. **`_clean_shape()` on every shape** — strips `<p:style>` to prevent
   shadow/3D inheritance.

## Track 2 additions

6. **`experiences.py` constants** — single source of truth for all
   production-hardened numbers.  Don't inline anywhere else.

7. **`run_qa()` returns whitelisted findings** — engine-bug categories
   auto-demote to info-level.

8. **`run_autofix()` mutates spec dicts in place** — never changes layout
   choice (the user's decision).  Layout-preserving text repairs only.

## Track 3 additions

9. **`profile_master()` is read-only** — never modifies the source .pptx.

10. **`generate_theme_from_profile()` writes valid Python** — output
    parses cleanly via `ast.parse()` and matches `theme_modern.py` shape.

## Pipeline counts (final)

- **45 registered layouts** (4 structure + 10 summary + 4 data tables + 5 charts + 5 special charts + 7 compare/matrix + 8 process + 1 org + alias)
- **19 experiences constants**
- **10 QA checks**
- **6 autofix repair rules**
- **34+ smoke tests** (Track 1) + ~20 unit tests (Session A + Track 2/3)
