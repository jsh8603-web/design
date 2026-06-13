# Layout Catalog — 48 레이아웃 v3.1

> 슬라이드 1개 = 1 레이아웃. 새 레이아웃을 만들지 말고 이 목록에서 골라라. 새 레이아웃이 정말 필요하면 이 파일에 먼저 LayoutSchema 를 추가하고 `theme_layout_matrix.md` §2 에 등록한 뒤 사용한다.
>
> **Marking convention**:
> - `<section data-layout="<id>">` 가 모든 슬라이드의 의무 속성 (PF-70).
> - `<id>` 는 이 카탈로그의 ID. 별칭 사용 금지.
> - 레이아웃별 schema 위반은 PF-72 ERROR (LayoutSchema validator).
>
> mck `deck_system/builder/validation.py` 의 LayoutSchema 와 1:1 매칭됨. 변경 시 양쪽 동기화 필요.

---

## 카테고리 — 8개 / 46 레이아웃

| 카테고리 | 개수 | 레이아웃 ID |
|----------|:---:|------------|
| **Structure** | 5 | `cover` · `section_divider` · `closing` · `dark_navy_summary` · `appendix_title` |
| **Summary** | 10 | `toc` · `executive_summary` · `key_takeaway` · `big_number` · `two_column_text` · `two_stat` · `three_stat` · `three_trends` · `five_key_areas` · `venn` |
| **Data tables** | 4 | `data_table` · `variance_table` ⭐ · `rag_status` · `harvey_ball_table` |
| **Data charts** | 5 | `column_historic_forecast` · `column_simple_growth` · `line_chart` · `stacked_column` · `grouped_column` |
| **Special charts** | 5 | `waterfall` ⭐ · `donut` · `kpi_dashboard` · `pareto` · `gauge` |
| **Compare / Matrix** | 7 | `comparison_table` · `pros_cons` · `before_after` · `swot` · `bcg_matrix` · `prioritization_matrix` · `risk_matrix` |
| **Process / Timeline** | 8 | `phases_chevron` · `vertical_steps` · `value_chain` · `funnel` · `pyramid` · `gantt_timeline` · `waves_timeline` · `cycle` |
| **Org / Insight** | 2 | `org_chart` · `table_insight` ⭐ |

⭐ FP&A signature.

---

## Schema 표기 규약

```
<id>
  required: field (type, bound)
  optional: field (type, default)
  bounds:   N ≤ items ≤ M
  forbidden_themes: [...]   # theme_layout_matrix.md에서 ❌ 인 테마
  invariants: [...]         # domain/fpna_invariants.md에서 적용되는 규칙
  example: { ... }
```

---

## 1. Structure

### `cover`
```
required: title (str, 1..60)
optional: subtitle (str), author (str), date (str)
forbidden_themes: []
example:
  { title: "FY26.Q1 매출, 전년 대비 +14.3%",
    subtitle: "2026년 4월 25일 분기 리뷰",
    author: "FP&A 팀", date: "2026.04.25" }
```

### `section_divider`
```
required: title (str, 1..60)
optional: section_label (str, "01"~"99"), subtitle (str)
invariants: [surface_inverse]   # 풀블리드 inverse 사용
example:
  { title: "북미 시장 회복", section_label: "02" }
```

### `closing`
```
required: title (str, 1..40, default "Thank you")
optional: subtitle (str), contact (str)
invariants: [surface_inverse]
example:
  { title: "Thank you", contact: "fpna@company.com" }
```

### `dark_navy_summary`
```
required: title (str, 1..30), body (str, 5..200)
invariants: [surface_inverse]
forbidden_themes: [dark-mono]   # 다크 위에 다크 캡슐 = 시각적 무대응
example:
  { title: "Bottom line",
    body: "Q2까지 매출 +14.3%, 영업이익 +8.2%p — 가이던스 상향" }
```

### `appendix_title`
```
required: title (str, default "부록" / "Appendix")
optional: subtitle (str), label (str)
example: { title: "부록", label: "APPENDIX" }
```

---

## 2. Summary / Narrative

### `toc` (별칭: `agenda`)
```
required: items (list, 1..7) — each [num, label, desc] tuple or {num, label, desc}
example:
  { title: "목차",
    items: [["01", "시장 맥락", "Q1 환경 회복"], ["02", "북미", "..."]] }
```

### `executive_summary`
```
required: headline (str, 5..80), items (list, 1..4)
  items[i]: { num: "01", kicker, title, desc }
invariants: [surface_inverse]   # 헤드라인은 inverse capsule
example:
  { title: "Q1 핵심 메시지",
    headline: "전년 대비 +14.3% 성장, 가이던스 상향 결정",
    items: [{ num: "01", kicker: "매출", title: "1,260억", desc: "..." }, ...] }
```

### `key_takeaway`
```
required: details (list, 1..3), takeaways (list, 1..3)
  details[i]: { label, body }
  takeaways[i]: { num, title }
example:
  { title: "북미 회복, 유럽 정체",
    details: [{ label: "북미", body: "+18% YoY, 신제품 효과" }, ...],
    takeaways: [{ num: "01", title: "북미 추가 투자 권고" }, ...] }
```

### `big_number`
```
required: number (str, 1..8), title (str)
optional: unit (str), description (str), detail_items (list, ≤4)
example:
  { title: "분기 신고점", number: "1,260", unit: "억원",
    description: "전년 동기 1,103억 대비 +14.3%",
    detail_items: ["북미 +18%", "유럽 +2%", "아시아 +21%"] }
```

### `two_column_text`
```
required: columns (list, ==2) — [{ title, bullets: list }, { title, bullets: list }]
forbidden_themes: [dark-mono]
bounds: bullets/column ≤ 5
invariants: deck-wide limit: 1 per deck (experiences.MAX_TWO_COLUMN_TEXT_PER_DECK)
```

### `two_stat`, `three_stat`
```
required: stats (list, ==2 or ==3) — [{ number, label }]
bounds: label ≤ 30 chars (two_stat) / ≤ 25 chars (three_stat)
```

### `three_trends`
```
required: trends (list, ==3) — [{ headline, bullets }]
bounds: bullets/trend ≤ 4
```

### `five_key_areas`
```
required: areas (list, 3..5) — [{ label, desc }]
bounds: label ≤ 12 chars
```

### `venn`
```
required: circles (list, 2..3) — [{ label }]
optional: intersection (str)
forbidden_themes: [dark-mono]   # blend fill 다크에서 깨짐
```

---

## 3. Data Tables

### `data_table`
```
required: headers (list, 2..6), rows (list, 1..10)
bounds:   각 cell str ≤ 40 chars
```

### `variance_table` ⭐
```
required: items (list, 1..10) — [{ label, budget, actual }]
optional: cost_nature (bool, per item), unit_default (str), columns (list)
invariants:
  - cost_nature: true → 양수 variance = 빨강 (비용 증가는 손실)
  - columns ⊂ ["label","budget","actual","variance_abs","variance_pct"]
example:
  { items: [{ label: "매출", budget: 1200, actual: 1260 },
            { label: "매출원가", budget: 720, actual: 770, cost_nature: true }] }
```

### `rag_status`
```
required: projects (list, 1..10) — [{ name, status: "g"|"a"|"r", owner?, note?, gate? }]
```

### `harvey_ball_table`
```
required: options (list, 2..4), criteria (list, 1..6)
  criteria[i]: { label, scores: list[0..100] } — len == len(options)
forbidden_themes: [dark-mono]   # 75%/100% 채움 단계 식별 불가
invariants:
  - Harvey ball ≥ 32px (≤14px 에서 구별 불가)
```

---

## 4. Data Charts

### `column_historic_forecast`
```
required: categories (list, 2+), values (list, 2+), forecast_from_index (int)
optional: unit (str)
bounds:   len(categories) == len(values)
```

### `column_simple_growth`
```
required: categories (list, 2+), values (list, 2+)
optional: cagr_label (str)
```

### `line_chart`
```
required: categories (list, 2+), series (list, 1+)
  series[i]: { label, values: list }
bounds: len(series) ≤ 4, marker per data point
```

### `stacked_column`
```
required: categories (list, 1+), series (list, 1+)
bounds: stacked total < 1.4× single max (가독성)
```

### `grouped_column`
```
required: categories (list, 1..6), series (list, 1..3)
invariants: MAX_GROUPED_BAR_SERIES = 3 (experiences)
```

---

## 5. Special Charts

### `waterfall` ⭐
```
required: items (list, 2+) — [{ label, value, type: base|up|down|subtotal }]
optional: unit (str), max_value (number), show_connector (bool, true), show_net (bool, true)
invariants:
  - 자동 running total / 자동 Y-max (× 1.15)
  - type 자동 부호 정규화 (input + or -)
  - net change callout
```

### `donut`
```
required: segments (list, 1..6) — [{ label, value, color? }]
optional: center_value, center_label, callout_position ("right"|"left"),
          max_segments (int, 6), show_percent (bool), show_value (bool)
invariants:
  - MAX_DONUT_SEGMENTS = 6 (experiences) — 초과분 "기타" 자동 머지
  - BLOCK_ARC label anchor 약간 오프셋 — engine bug whitelist
```

### `kpi_dashboard`
```
required: kpis (list, 1..8) — [{ label, value, yoy?, yoy_label?, detail?, value_suffix? }]
optional: layout ("auto"|"1x3"|"2x2"|"2x3"|"2x4"|"1x5"), neutral_threshold (0)
invariants:
  - auto layout: 3→1×3, 4→2×2, 6→2×3, 8→2×4
  - yoy_label "%p" → suffix renders as %p
  - |yoy| ≤ neutral_threshold → 중립 ● (gray)
```

### `pareto`
```
required: items (list, 2..10) — [{ label, value }]
optional: threshold (number, 0.8 = 80% cutoff)
forbidden_themes: [dark-mono]
invariants: MAX_PARETO_BARS = 10
```

### `gauge`
```
required: value (number), label (str)
optional: sub (str), threshold_good (number), threshold_warn (number)
forbidden_themes: [dark-mono]
```

---

## 6. Compare / Matrix

### `comparison_table`
```
required: options (list, 2..5), criteria (list, 1..6)
  criteria[i]: { label, values: list } — len == len(options)
```

### `pros_cons`
```
required: pros (list, 1..5), cons (list, 1..5)
```

### `before_after`
```
required: before (list, 1..4), after (list, 1..4)
forbidden_themes: [dark-mono]
```

### `swot`
```
required: strengths (list), weaknesses (list), opportunities (list), threats (list)
bounds: each list 1..4
```

### `bcg_matrix`
```
optional: stars, question_marks, cash_cows, dogs (each list)
bounds: each list ≤ 3
```

### `prioritization_matrix`
```
optional: quick_wins, major_projects, fill_ins, hard_slogs (each list ≤ 3)
```

### `risk_matrix`
```
required: risks (list, 1..9) — [{ label, likelihood: 1..3, impact: 1..3 }]
forbidden_themes: [dark-mono]
```

---

## 7. Process / Timeline

### `phases_chevron`
```
required: steps (list, 2..5) — [{ label, sub? }]
invariants:
  - MAX_PROCESS_CHEVRON_STEPS = 5
  - 라벨 줄바꿈 금지 (PROCESS_STEP_LABEL_NO_NEWLINE = True)
  - 라벨 ≤ 50 chars (MAX_PROCESS_CHEVRON_DESC_CHARS)
```

### `vertical_steps`
```
required: steps (list, 1..7) — [{ title, desc, num? }]
```

### `value_chain`
```
required: stages (list, 2..7) — [{ label, kpi? }]
```

### `funnel`
```
required: stages (list, 2..6) — [{ label, value, conversion? }]
```

### `pyramid`
```
required: tiers (list, 2..5) — [{ label, sub? }]
```

### `gantt_timeline`
```
required: periods (list, 2..12), tasks (list, 1..8)
  tasks[i]: { label, start: int, end: int }
```

### `waves_timeline`
```
required: waves (list, 1..4) — [{ label, period, sub? }]
```

### `cycle`
```
required: steps (list, 3..6) — [{ label, num? }]
```

---

## 8. Org / Insight

### `org_chart`
```
required: root (dict: { name, role }), heads (list, 1..6)
  heads[i]: { name, role, members?: list }
```

### `table_insight` ⭐ (McK 시그니처)
```
required: headers (list, 2..6), rows (list, 1..6), insights (list, 1..3)
forbidden_themes: [dark-mono]
invariants:
  - 좌측 표 + 우측 회색 캡슐 (insights)
  - 캡슐은 gray-4 배경, action title 톤
```

### `quote` (slides-grab 흡수)
```
required: quote (str), author (str)
optional: role (str), source (str)
invariants:
  - 풀블리드 surface_inverse 배경 (모든 테마에서 톤 시프트)
  - accent 인용 글리프 + em 강조 1회
example:
  { quote: "자본은 가장 먼저 확신이 서는 곳으로 흐른다",
    author: "이재훈, CFA", role: "CFO" }
```

### `meet_the_team` (slides-grab 흡수)
```
required: people (list, 2..6) — [{ name, role, bio?, photo_slot_id }]
optional: title (str)
invariants:
  - 각 인물 image-slot (data-shape="rounded", 1:1) — image_slot_contract.md
  - role 은 accent 색, bio 는 gray-2
```

---

## HTML reference 위치 — 48 레이아웃 전수 커버

각 레이아웃의 동작하는 HTML 레퍼런스가 다음 4개 파일에 분산 박제됨. 모두 1280×720, `[data-theme]` 전환, 의미적 토큰.

| 파일 | 레이아웃 |
|------|---------|
| `mck/slides/index.html` (17 deck) | cover · toc · section_divider · table_insight · big_number · bcg_matrix(2×2) · four_column · waves_timeline · key_takeaway · closing · executive_summary · kpi_dashboard · waterfall · variance_table · vertical_steps · swot · donut |
| `mck/slides/catalog-additions.html` (10) | column_simple_growth · line_chart · rag_status · harvey_ball_table · pareto · phases_chevron · cycle · comparison_table · funnel · action_items |
| `mck/slides/catalog-additions-2.html` (21) | dark_navy_summary · appendix_title · two_stat · three_stat · three_trends · five_key_areas · two_column_text · pros_cons · before_after · bcg_matrix · prioritization_matrix · risk_matrix · value_chain · pyramid · gantt_timeline · org_chart · venn · column_historic_forecast · stacked_column · grouped_column · gauge |
| `mck/slides/catalog-additions-3.html` (16, v3.2) | horizontal_bar · metric_cards · numbered_list_panel · temple · scorecard · checklist · pie · metric_comparison · three_images · two_col_image_grid · dashboard_kpi · dashboard_table · bubble · stacked_area |
| `slides/` (slides-grab 흡수) | quote · meet_the_team(team) · data_table(content) · side_by_side(split-layout) · statistics · contents |

→ **46 core + quote + meet_the_team + v3.2 보조 16 = 64 레이아웃**, 전부 HTML 레퍼런스 존재.

---

## Quick Reference — required keys lookup

특정 키가 보이면 어떤 레이아웃인지 추론 가능. `mck/deck_system/builder/inference.py` 의 로직을 박제한 표:

| 키 패턴 | 추정 레이아웃 |
|---------|-------------|
| `items[].type ∈ {base,up,down,subtotal}` | `waterfall` |
| `items[].budget + items[].actual` | `variance_table` |
| `kpis` | `kpi_dashboard` |
| `segments + center_value` | `donut` |
| `segments` (no center) | `pie` |
| `number + title` | `big_number` |
| `stats` (len 2 or 3) | `two_stat` / `three_stat` |
| `strengths + weaknesses` | `swot` |
| `pros + cons` | `pros_cons` |
| `before + after` | `before_after` |
| `risks` | `risk_matrix` |
| `categories + values + forecast_from_index` | `column_historic_forecast` |
| `categories + series` | `line_chart` / `stacked_column` / `grouped_column` |
| `value + label + threshold_good` | `gauge` |
| `steps` (≤5, horizontal) | `phases_chevron` |
| `steps` (>5, vertical) | `vertical_steps` |
| `stages` + `value` | `funnel` |
| `stages` (no value) | `value_chain` |
| `headers + rows + insights` | `table_insight` |
| `headers + rows` (no insights) | `data_table` |
| `projects` w/ status | `rag_status` |
| `options + criteria[].scores` | `harvey_ball_table` |
| `options + criteria[].values` | `comparison_table` |
| `root + heads` | `org_chart` |
| `circles` | `venn` |
| `tiers` | `pyramid` |
| `waves` | `waves_timeline` |
| `periods + tasks` | `gantt_timeline` |
| `trends` | `three_trends` |
| `areas` | `five_key_areas` |

---

## 변경 로그

- **v3.2**: v3.2 보조 16종 HTML 레퍼런스 작성 (`catalog-additions-3.html`) — horizontal_bar · metric_cards · numbered_list_panel · temple · scorecard · checklist · pie · metric_comparison · three_images · two_col_image_grid · dashboard_kpi · dashboard_table · bubble · stacked_area. mck v22/v23 geometry 이식. **64 레이아웃 전수 HTML 커버.** 전 standalone 슬라이드에 뷰포트 맞춤 스케일러 주입.
- **v3.1**: 누락 21 레이아웃 HTML 레퍼런스 작성 (`catalog-additions-2.html`) + slides-grab 흡수 `quote`·`meet_the_team` 추가 → 48 레이아웃. 전 슬라이드 1280×720 캔버스 마이그레이션.
- **v3.0 (통합)**: 46 레이아웃 LayoutSchema 박제 (mck v2.1 + 슬라이드그랩 PF 흡수).
- 이전: 슬라이드그랩에는 5개 슬라이드 + 4 aesthetic × 5 = 22 자유 변형. 카탈로그/스키마 없음.

## 전수 완료

mck `deck_system` 의 70 레이아웃 + slides-grab 고유 디자인이 모두 HTML 레퍼런스로 박제됨 (64 종 + 변형). 남은 mck 미작성분: `temple`(✅) 외 거의 없음. 신규 필요 시 `catalog-additions-4.html` 신설.
