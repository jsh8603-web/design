# Layout catalog — 45 registered slide types

Generated from `deck_system.builder.registry`.  Each layout function lives
in a module under `deck_system/layouts/` and follows the same calling
convention: `render(slide, spec, theme, *, page_num, total)`.

To add a layout: write the function, decorate with `@register("name")`,
add the module to `deck_system/layouts/__init__.py`.

## Structure (4)

| name | file | purpose |
|------|------|---------|
| `cover` | structure.py | Title slide — left navy panel + title block on white |
| `section_divider` | structure.py | Full-bleed surface_inverse + large section number/title |
| `closing` | structure.py | Thank-you slide — full-bleed inverse + contact line |
| `dark_navy_summary` | structure.py | Bottom-line capsule — single statement on inverse |

## Summary / narrative (10)

| name | file | purpose |
|------|------|---------|
| `toc` (`agenda` alias) | summary.py | Section list with chapter numbers |
| `executive_summary` | summary.py | Inverse capsule + 3 supporting bullets |
| `key_takeaway` | summary.py | Detail-left + takeaway-cards-right |
| `big_number` | summary.py | Hero number + 3 supporting facts |
| `two_column_text` | summary.py | Pros vs cons in plain bullet columns |
| `two_stat` | narrative.py | 2 huge stat tiles |
| `three_stat` | narrative.py | 3 huge stat tiles |
| `three_trends` | narrative.py | 3 numbered trend columns with bullets |
| `five_key_areas` | narrative.py | 5 numbered badge tiles |
| `venn` | narrative.py | 2-3 overlapping circles |

## Data tables (4)

| name | file | purpose |
|------|------|---------|
| `data_table` | data_table.py | Generic rows × cells table |
| `variance_table` | data_table.py | **Budget vs actual w/ cost_nature flip** |
| `rag_status` | data_table.py | Red/amber/green project status table |
| `harvey_ball_table` | data_table.py | Options × criteria w/ 0-100 Harvey balls |

## Data charts (5)

| name | file | purpose |
|------|------|---------|
| `column_historic_forecast` | data_chart.py | Past vs forecast clustered columns |
| `column_simple_growth` | data_chart.py | Single-series w/ CAGR callout |
| `line_chart` | data_chart.py | Multi-series line markers |
| `stacked_column` | data_chart.py | Part-of-whole over time |
| `grouped_column` | data_chart.py | Multi-series clustered columns |

## Special charts (5)

| name | file | purpose |
|------|------|---------|
| `waterfall` | data_special.py | **OP bridge w/ base/up/down/subtotal** |
| `donut` | data_special.py | BLOCK_ARC ring + leader callouts (auto-merge tail) |
| `kpi_dashboard` | data_special.py | Auto-layout KPI tiles w/ ▲▼ |
| `pareto` | data_special.py | Descending bars + cumulative line + 80% callout |
| `gauge` | data_special.py | Semicircle dial w/ state coloring |

## Compare / matrix (7)

| name | file | purpose |
|------|------|---------|
| `comparison_table` | compare.py | Side-by-side option × criterion |
| `pros_cons` | compare.py | ✓/✗ two-column |
| `before_after` | compare.py | Gray vs inverse blocks w/ arrow divider |
| `swot` | matrix.py | Strengths/Weaknesses/Opportunities/Threats 2×2 |
| `bcg_matrix` | matrix.py | Stars/Question/CashCow/Dog growth-share |
| `prioritization_matrix` | matrix.py | Impact × Effort 2×2 |
| `risk_matrix` | matrix.py | 3×3 likelihood × impact heat map |

## Process / timeline (8)

| name | file | purpose |
|------|------|---------|
| `phases_chevron` | process.py | Horizontal chevrons (≤5 steps) |
| `vertical_steps` | process.py | Numbered steps + optional right panel |
| `value_chain` | process.py | Pentagon stages with KPI labels |
| `funnel` | process.py | Trapezoidal stages descending |
| `pyramid` | process.py | 3-5 tier hierarchy |
| `gantt_timeline` | process.py | Tasks × periods bars |
| `waves_timeline` | process.py | 3-4 horizontal phase bands |
| `cycle` | process.py | Circular N-step PDCA-style |

## Org (1)

| name | file | purpose |
|------|------|---------|
| `org_chart` | org.py | 3-tier CEO → heads → members |

**Total: 4 + 10 + 4 + 5 + 5 + 7 + 8 + 1 = 44 registered + `agenda` alias = 45 names**
