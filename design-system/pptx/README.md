# fpna-deck-system

한국어 비즈니스 발표용 .pptx 생성 시스템.

## What it does

- **70개 슬라이드 레이아웃** (cover, waterfall, donut, kpi_dashboard, swot, gantt, …)
- **4개 테마** (modern · classic · dark_mono · company)
- **한국어 자동 처리** (Pretendard EA font 자동 적용)
- **FP&A 특화** — `cost_nature` 부호 반전, 예실 분석, P&L bridge, KPI 대시보드
- **입력 검증 + 친절한 에러** (70 LayoutSchema, 5종 에러 클래스)
- **HTML 시스템과 JSON spec 호환** (camelCase ↔ snake_case 자동)
- **QA + Auto-fix** (9 per-slide + 3 global checks, 8 repair rules)

## Quick Start (5분)

> 먼저 패키지를 설치하면 `deck_system` 이 어느 위치에서나 import 됩니다.

```bash
pip install -e .                # python-pptx + `fpna-deck` CLI 설치 (pyproject.toml)

# 1. 시작 템플릿 만들기
python -m deck_system.cli init my_deck/

# 2. JSON spec → .pptx
python -m deck_system.cli build my_deck/deck.json -o my_deck/out.pptx

# 3. 4테마 시도
python -m deck_system.cli build my_deck/deck.json -o my_deck/dark.pptx --theme dark_mono

# 4. 카탈로그 둘러보기
python -m deck_system.cli list-layouts
python -m deck_system.cli show-schema waterfall
```

또는 Python에서 한 줄:

```python
from deck_system import quick_deck
quick_deck([
    {"type": "cover", "title": "Q4 review"},
    {"type": "variance_table", "title": "예산 대비",
     "items": [{"label": "매출", "budget": 1200, "actual": 1260}],
     "unit_default": "억"},
    {"type": "closing", "title": "Thanks"},
], "out.pptx", theme="modern")
```

## CLI

| Command | Purpose |
|---------|---------|
| `build SPEC -o OUT` | Render `.pptx` from JSON spec |
| `list-layouts [--category C]` | All 70 registered layouts |
| `show-schema LAYOUT` | Layout's required/optional fields + example |
| `validate SPEC` | Validate without building (fast pre-flight) |
| `themes` | List 4 themes w/ primary colors |
| `init [DIR]` | Write starter `deck.json` template |

## Architecture (5-stage pipeline)

```
JSON spec → normalize → infer type → validate → render layout → QA
            (camelCase  (FP&A-first  (70 schemas  (45 layout    (9+3 checks
             → snake)    detection)   + example)   functions)    + autofix)
```

See `docs/architecture.md` for module map.

## Layout catalog (70 total)

| Category | Count | Examples |
|----------|-------|----------|
| Structure | 5 | cover · section_divider · closing · dark_navy_summary · appendix_title |
| Summary | 6 | toc · executive_summary · key_takeaway · big_number · two_column_text · agenda |
| Data tables | 6 | variance_table ⭐ · data_table · rag_status · harvey_ball_table · scorecard · checklist |
| Data charts | 7 | column_historic_forecast · line_chart · stacked_column · grouped_column · horizontal_bar · stacked_area · pie |
| Special charts | 7 | waterfall ⭐ · donut · kpi_dashboard · pareto · gauge · gauge_pair · bubble |
| Composite | 4 | dashboard_kpi · dashboard_table · metric_cards · numbered_list_panel |
| Compare | 4 | comparison_table · pros_cons · before_after · side_by_side |
| Narrative | 8 | two_stat · three_stat · three_trends · five_key_areas · venn · four_column · metric_comparison · temple |
| Matrix | 5 | swot · bcg_matrix · prioritization_matrix · risk_matrix · stakeholder_map |
| Process | 10 | phases_chevron · vertical_steps · value_chain · funnel · pyramid · gantt_timeline · waves_timeline · cycle · timeline · decision_tree |
| Team / org | 4 | org_chart · meet_the_team · case_study · action_items |
| Insight | 1 | table_insight ⭐ (McK signature opener) |
| Image | 2 | three_images · two_col_image_grid |

⭐ = FP&A signature layouts.

Run `python -m deck_system.cli list-layouts` for the full registry.

## FP&A specifics

### `cost_nature` sign flip

In `variance_table`, items with `cost_nature: true` invert the sign — a positive
variance on a cost row colors RED (cost increase = bad). HTML system matched 1:1.

```python
{"type": "variance_table",
 "items": [
   {"label": "매출",       "budget": 1200, "actual": 1260},
   {"label": "매출원가",   "budget": 720,  "actual": 770, "cost_nature": true},  # red even though +50
   {"label": "영업이익",   "budget": 180,  "actual": 165},
 ]}
```

### Waterfall (P&L bridge)

`items[].type ∈ {base, up, down, subtotal}` — auto-cumulates and colors.

### `surface_inverse` (dark-mode safety)

Full-bleed slides reference `palette.surface_inverse` (not `primary`) so the
`dark_mono` theme renders correctly — in dark mode `primary == bg`, but
`surface_inverse` diverges to `gray_4`.

## Input validation

`PresentationBuilder.add(layout, **kwargs)` runs `validate_layout_input()`
before buffering. Bad input raises `InputValidationError` with structured
fields:

```
InputValidationError: [waterfall] slide 2
Missing required field: 'items'
Expected: list
Fix: Add `items=…` to your spec.
Example:
{
  "title": "x",
  "items": [
    {"label": "S", "value": 100, "type": "base"},
    {"label": "E", "value": 110, "type": "base"}
  ]
}
```

Error classes: `InputValidationError`, `CJKFontError`, `ThemeError`,
`LayoutOverflowError`, `ImagePlaceholderError` — all inherit from
`DeckSystemError`.

## Themes

| theme | primary | accent | use |
|-------|---------|--------|-----|
| `modern` (default) | #1A2332 slate | #E87722 orange | FP&A quarterly review |
| `classic` | #051C2C McK navy | #00A3E0 cyan | board / executive |
| `dark_mono` | #0F1419 near-black | #4A9EFF blue | tech / DA presentations |
| `company` | auto-extracted | auto-extracted | from in-house `.pptx` master via adapter |

Set via CLI `--theme dark_mono` or `PresentationBuilder(theme=DARK_MONO)`.

## Roadmap

- ✅ V1 – V2.3-B (this release): 70 layouts + QA + validation + friendly errors + docs
- ⏳ V3: In-house master adapter (needs company `.pptx`)
- ⏳ Retro: visual bug fixes after real-world use

## Attribution

This project incorporates ideas from three upstream repos. See `NOTICE.md`.

- likaku/Mck-ppt-design-skill (Apache 2.0) — 70-layout catalog, experiences, QA
- seulee26/mckinsey-pptx (MIT) — Builder pattern, theme dataclass, Korean demo
- tristan-mcinnis/pptx-from-layouts-skill (MIT) — Master adapter pattern

## License

Apache License 2.0 — see `LICENSE`.
