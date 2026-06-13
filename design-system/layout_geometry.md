# Layout Geometry — 각 레이아웃의 공간 레시피

> mck 의 5번째 레이어 (`layouts/*.py`). **각 레이아웃 함수가 spec 의 어느 필드를 어디에 그릴지** 정의. Schema 가 "무엇" 이라면, Geometry 는 **"어디·얼마·어떻게"**.
>
> 권위 코드: `mck/deck_system/layouts/*.py` — 45개 layout 함수.
> 이 문서는 7개 반복 패턴 + 레이아웃별 1-line 요약 + invariants. 정확한 px/inch 값은 소스 코드 참조.

---

## 0. 공통 골격 — 모든 콘텐츠 슬라이드

```
┌─────────────────────────────────────────────────────────┐  ← 0, 0
│  ┌─ TITLE_BAND (0.15"~1.05") ────────────────────────┐  │
│  │  add_action_title(slide, title, theme)            │  │  ← 22pt bold primary
│  │   ↓ 2pt primary horizontal rule at 1.05"          │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ CONTENT_BAND (1.3"~6.2") ────────────────────────┐  │
│  │                                                    │  │  ← 레이아웃별 본문
│  │   (layout-specific geometry)                       │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ BOTTOM_BAR (6.2"~6.85") — optional ──────────────┐  │
│  │  "시사점 — " + takeaway message (16pt gray-1)      │  │  ← gray-4 fill
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Source: 재무팀 KPI…           ← (0.8, 7.05) 9pt gray-2  │
│                                  n / total → (12.2, 7.05) │
└─────────────────────────────────────────────────────────┘
  margin_left=0.8"        slide_width=13.333"         margin_right=0.8"
```

이 골격은 `helpers/chrome.py` 의 4개 헬퍼로 자동 그려짐:
- `add_action_title(slide, title, theme)` — 타이틀 + 룰
- `add_bottom_bar(slide, text, theme, tag="시사점 —")` — 옵셔널
- `add_source(slide, source_text, theme)`
- `add_page_number(slide, num, total, theme)`

레이아웃 함수는 이 4개를 호출 + 자기 고유의 CONTENT_BAND 본문을 그림.

---

## 1. 7개 반복 패턴

### Pattern A — Full-bleed inverse 배경

**적용**: `cover`, `section_divider`, `closing`, `dark_navy_summary`

```python
add_rect(slide, 0, 0, L.slide_width_in, L.slide_height_in, P.surface_inverse)
# 그 위에 큰 텍스트 + 메타
```

특징:
- 첫 줄에 풀블리드 inverse 배경
- 그 위에 모든 텍스트는 `P.surface_inverse_fg` 색
- chrome (action_title / source / page_num) 미사용 — 자체 chrome
- top hairline (0.8, 0.8) → (2.05, 0.8) 흰색 2pt 룰이 시그니처

### Pattern B — 표준 chrome (가장 많이 사용)

**적용**: `toc`, `executive_summary`, `key_takeaway`, `big_number`, `variance_table`, `data_table`, `rag_status`, `harvey_ball_table`, `waterfall`, `donut`, `kpi_dashboard`, 그 외 35+

```python
add_action_title(slide, title, theme=theme)
# CONTENT_BAND 본문 (layout-specific)
if spec.get("bottom_bar"):
    add_bottom_bar(slide, spec["bottom_bar"], theme=theme, tag=...)
add_source(slide, spec.get("source", ""), theme=theme)
add_page_number(slide, page_num, total, theme=theme)
```

### Pattern C — Header-then-rows 테이블

**적용**: `variance_table`, `data_table`, `rag_status`, `harvey_ball_table`, `comparison_table`

구조:
```
┌──────────────────────────────────────────────────────┐
│ 헤더 row (height 0.4~0.5") — surface_inverse 배경     │  ← 헤더 텍스트 inverse_fg
├──────────────────────────────────────────────────────┤
│ Row 1                                                │  ← (i%2==1 → gray_4 배경)
│   gray_4 hairline (0.5~0.75pt) at bottom             │
├──────────────────────────────────────────────────────┤
│ Row 2 (highlight 시 → gray_4 풀 배경)                  │
├──────────────────────────────────────────────────────┤
│ …                                                    │
└──────────────────────────────────────────────────────┘
```

컬럼 폭 규칙:
- 라벨 열: body_width × 0.26~0.35 (변동)
- 데이터 열: 나머지를 균등 분배
- 정렬: 라벨 LEFT, 데이터 RIGHT, 상태칩 CENTER
- 폰트: 헤더 13pt bold inverse_fg, 본문 14pt gray-1 (positive/negative 강조 시 색 + bold)

행 높이: 0.40~0.55"

### Pattern D — N-column equal split

**적용**: `executive_summary` 본문 (3-col), `three_trends`, `five_key_areas`, `four_column`, `three_stat`, `two_stat`, `three_images`

```python
n = len(items)
col_gap = 0.3
col_w = (L.content_width_in - col_gap * (n - 1)) / n
for i, it in enumerate(items):
    x = L.margin_left_in + i * (col_w + col_gap)
    # 컬럼 본문: kicker → title → desc 3-tier
```

컬럼 안 3-tier:
1. **Kicker** (small_size - 1, bold, accent color) — `01 · 매출`
2. **Title** (sub_header_size, bold, gray_1, line-spacing 1.25)
3. **Description** (body_size - 1, gray_2, line-spacing 1.45)

### Pattern E — Left-hero + right-stack

**적용**: `big_number`

```
┌─────────────────────────────────────────────────────────┐
│  HERO              │  Item 1 (accent bar + value + desc)│
│  Number 160pt      │  Item 2                            │
│  Unit  64pt        │  Item 3                            │
│  Description       │  Item 4 (max 4)                    │
│  (left 40%)        │  (right 60%, accent bars 0.04" w)  │
└─────────────────────────────────────────────────────────┘
```

좌측: 160pt number + 64pt unit + body description
우측: 4개 supporting items, 각 1.2" 높이, 왼쪽에 0.04" accent bar (1=primary, 2=accent, 3+=negative 패턴)

### Pattern F — Left-detail + right-cards

**적용**: `key_takeaway`

```
┌────────────────────────────┬─────────────────────────┐
│  Detail 1 (label + body)   │  Card 1 (inverse fill)  │
│                            ├─────────────────────────┤
│  Detail 2                  │  Card 2 (inverse fill)  │
│                            ├─────────────────────────┤
│  Detail 3                  │  Card 3 (gray_4 fill)   │
│                            ├─────────────────────────┤
│  (left 58%)                │  Card 4… (gray_4 fill)  │
└────────────────────────────┴─────────────────────────┘
```

특징: 우측 카드 **첫 2개는 inverse, 그 이후는 gray_4** — 우선순위 시각화.

### Pattern G — Annotated capsule + supporting

**적용**: `executive_summary`

```
┌─────────────────────────────────────────────────────┐
│  surface_inverse 캡슐 (height 1.4")                 │
│  "Bottom line" 라벨 (small)  ┃  Headline 본문 (22pt) │
└─────────────────────────────────────────────────────┘
                                                       
┌──── 3-column supporting ────┬──────────┬──────────┐
│  01 · 매출                  │  02 · …   │  03 · …  │
│  1,260억                    │           │          │
│  desc…                      │           │          │
└────────────────────────────┴───────────┴──────────┘
```

---

## 2. 레이아웃별 1-line geometry 요약

### Structure (5)

| Layout | Pattern | 시그니처 좌표 |
|--------|---------|-------------|
| `cover` | A 변형 (좌 패널) | 좌측 (0, 0, 3.8", full_h) inverse panel + 우측 (4.6", 2.0") 타이틀 |
| `section_divider` | A 풀블리드 | (0.8, 1.25) 라벨 + (0.8, 2.1) 80pt title + (0.8, 4.1) subtitle |
| `closing` | A 풀블리드 | (0.8, 1.25) pretitle + (0.8, 2.3) 64pt title + contact (0.8, 7.0) |
| `dark_navy_summary` | A 풀블리드 | (0.8, 2.6) label + (0.8, 3.2) 28pt body — 짧은 한 문장 |
| `appendix_title` | A 변형 | 좌측 inverse 작은 패널 + "APPENDIX" 라벨 |

### Summary / Narrative (10)

| Layout | Pattern | 시그니처 |
|--------|---------|---------|
| `toc` / `agenda` | B + 큰 번호 | 행마다: 좌 44pt 번호 + 우 24pt title + desc, line-spacing 1.4 |
| `executive_summary` | G | inverse 캡슐 1.4" + 3-col supporting items |
| `key_takeaway` | F | 좌 58% details + 우 42% 카드 (첫 2개 inverse) |
| `big_number` | E | 좌 160pt number + 우 4 items w/ 0.04" accent bar |
| `two_column_text` | D (n=2) | gap 0.5", bullet "• " prefix, sub_header title |
| `two_stat` | D (n=2) | hero number + label, 2 column |
| `three_stat` | D (n=3) | hero number + label, 3 column |
| `three_trends` | D (n=3) | 각 컬럼: headline + bullets (≤4) |
| `five_key_areas` | D (n=3..5) | 각 영역: badge num + label + desc |
| `venn` | 자체 geometry | 2-3 oval, blend 영역, 중앙 intersection label |

### Data tables (4)

| Layout | Pattern | 컬럼 폭 / 행 높이 |
|--------|---------|----------------|
| `data_table` | C | n_cols 균등, header 0.4", row 0.4" |
| `variance_table` ⭐ | C | label 30%, 나머지 균등; 5 컬럼 default; **cost_nature 부호 반전 색** |
| `rag_status` | C | 프로젝트 35% / 상태 15% / 담당 15% / 비고 35%; row 0.55" |
| `harvey_ball_table` | C + Harvey ball oval | label 32% + 옵션 균등; row 0.55"; ball 0.36" diameter |

### Data charts (5)

| Layout | 패턴 | 시그니처 |
|--------|------|---------|
| `column_historic_forecast` | native PowerPoint chart | forecast_from_index 이후 컬럼은 outline only |
| `column_simple_growth` | native chart + CAGR | 우측 상단 CAGR 캡션 |
| `line_chart` | native chart + 마커 | series ≤4, 각 data point 마커 |
| `stacked_column` | native stacked | 누적 < single max × 1.4 가독성 |
| `grouped_column` | native grouped | series ≤3 (`MAX_GROUPED_BAR_SERIES`) |

### Special charts (5)

| Layout | 패턴 | 시그니처 |
|--------|------|---------|
| `waterfall` ⭐ | base/up/down/subtotal rect + connector line | 자동 running total, 자동 Y-max (×1.15), net change callout |
| `donut` | BLOCK_ARC segments + leader lines | center value + label; >6 segments → "기타" 자동 머지 |
| `kpi_dashboard` | grid (auto layout) | 3→1×3, 4→2×2, 6→2×3, 8→2×4; tile gap 0.18" |
| `pareto` | 막대 (descending) + 누적선 + 80% callout | bars ≤10, 80% cutoff 라벨 |
| `gauge` | 반원 + 상태색 채움 | threshold_good/warn 에 따라 positive/amber/negative |

### Compare / Matrix (7)

| Layout | 패턴 | 시그니처 |
|--------|------|---------|
| `comparison_table` | C | 옵션 헤더 + criteria 행, 추천안 강조 (gray_4 column) |
| `pros_cons` | D (n=2) | ✓ / ✗ 인라인 prefix, 좌 pros 우 cons |
| `before_after` | D (n=2) + 화살표 | 좌 gray_4 / 우 inverse + 중앙 → 디바이더 |
| `swot` | 2×2 grid | strengths/weaknesses (gray_4) + opportunities/threats (inverse) |
| `bcg_matrix` | 2×2 grid + axes | growth × share, 각 사분면 라벨 (Stars/Q?/CashCow/Dog) |
| `prioritization_matrix` | 2×2 grid + axes | impact × effort, quick wins 강조 |
| `risk_matrix` | 3×3 heat map | likelihood × impact, 색상 코딩 (green→amber→red) |

### Process / Timeline (8)

| Layout | 패턴 | 시그니처 |
|--------|------|---------|
| `phases_chevron` | 수평 5-step chevron | 각 step 0.04" 화살표 prefix, label 줄바꿈 금지 |
| `vertical_steps` | 1-7 step 좌 number + 우 본문 | 큰 step 번호 + 가로 룰 |
| `value_chain` | pentagon stages | 각 stage 화살표 형태, KPI 라벨 |
| `funnel` | 사다리꼴 stages descending | width 점감 (top 1000→bottom 170 default) |
| `pyramid` | 3-5 tier 사다리꼴 | 위가 좁고 아래가 넓음, tier 라벨 |
| `gantt_timeline` | tasks × periods grid | 가로 bar 가 period 셀 채움 |
| `waves_timeline` | 3-4 가로 phase band | 각 wave 다른 색 (primary→accent→gray) |
| `cycle` | 원형 N-step | 각 step 사각형 + 화살표 (PDCA-style) |

### Org / Insight (2)

| Layout | 패턴 | 시그니처 |
|--------|------|---------|
| `org_chart` | 3-tier tree | 루트 → heads → members, hairline connector |
| `table_insight` ⭐ | C + 우측 캡슐 | 좌 표 60% + 우 인사이트 캡슐 40% (gray_4 fill) — **McK 시그니처** |

---

## 3. 색상 사용 패턴

각 레이아웃의 색 적용 규칙 (geometry 와 함께 박제):

### 3.1 데이터 행/카드/배지

| 의도 | 채움 | 텍스트 |
|------|------|------|
| 우선순위 1 (강조) | `surface_inverse` | `surface_inverse_fg` |
| 우선순위 2 (보조) | `gray_4` | `gray_1` |
| 강조 액센트 | `accent` | (자동 대비) |
| 양수 / 성장 | (텍스트만) `positive` | `positive` |
| 음수 / 손실 | (텍스트만) `negative` | `negative` |
| 중립 / 비활성 | (텍스트만) `gray_2` | `gray_2` |
| Outline | `background()` (no fill) | `primary` border |

### 3.2 액센트 바 (big_number)

```python
accent_color = it.get("color", P.primary if i == 0
                                  else (P.accent if i == 1 else P.negative))
```

→ 1번째 = primary, 2번째 = accent, 3+번째 = negative.

### 3.3 inverse → gray_4 폴백 (key_takeaway 카드)

```python
is_primary = i < 2  # 첫 2개만 inverse
fill = P.surface_inverse if is_primary else P.gray_4
fg = P.surface_inverse_fg if is_primary else P.gray_1
```

### 3.4 alternating 행 배경 (테이블)

```python
if i % 2 == 1:
    add_rect(slide, body_left, y, body_width, row_h, P.gray_4)
# 짝수 행: 배경 없음 (canvas bg = theme_bg)
# 홀수 행: gray_4
```

---

## 4. 슬라이드 함수 시그니처 표준

모든 layout 함수는 다음 시그니처:

```python
@register("layout_name")
def render_layout(slide, spec, theme, *, page_num, total):
    """슬라이드에 layout_name 형식으로 그린다.

    Args:
        slide: python-pptx Slide 객체 (빈 blank layout)
        spec: 정규화된 dict (camelCase → snake_case 적용 완료)
        theme: deck_system.tokens.base.Theme (palette + typography + layout)
        page_num: 1-based 현재 슬라이드 번호
        total: 전체 슬라이드 수 (페이지 번호용)
    """
    L = theme.layout
    P = theme.palette
    T = theme.typography

    # 1. chrome (필요 시)
    add_action_title(slide, spec.get("title", ""), theme=theme)

    # 2. layout-specific geometry
    # ... add_rect / add_textbox / add_hline / add_block_arc / add_oval

    # 3. chrome 마무리
    if spec.get("bottom_bar"):
        add_bottom_bar(slide, spec["bottom_bar"], theme=theme, tag=...)
    add_source(slide, spec.get("source", ""), theme=theme)
    add_page_number(slide, page_num, total, theme=theme)
```

이 시그니처는 **42 + 3 = 45개 registered layout 함수 모두 공통**. 새 레이아웃 추가 시 정확히 이 시그니처로 작성.

---

## 5. registry — 레이아웃 등록 시스템

```python
# mck/deck_system/builder/registry.py
@register("layout_name")
def fn(slide, spec, theme, *, page_num, total): ...

# Builder 가 dispatch:
render_fn = get_layout(name)
render_fn(slide, kwargs, self.theme, page_num=idx, total=total)
```

**Flat dispatch — if/elif 체인 없음.** 새 레이아웃이 import 되면 자동 등록.

```python
# 등록된 모든 레이아웃 조회:
from deck_system.builder.registry import all_names
print(all_names())  # ['agenda', 'bcg_matrix', 'before_after', ..., 'waterfall']
```

---

## 6. 슬라이드그랩 HTML 으로의 매핑

이 geometry 가 양쪽 시스템에서 1:1 매칭되어야 sync 가능. HTML 시스템에서 같은 레이아웃은:

```html
<section data-layout="variance_table" data-screen-label="04">
  <div class="slide__title">
    <h1 class="t-action">매출원가 +50억 초과, 영업이익 −15억 미달</h1>
  </div>
  <div class="slide__rule"></div>

  <div class="slide__content">
    <!-- Pattern C: header row + body rows -->
    <div class="vt-header" style="display:grid; grid-template-columns: 30% repeat(4, 1fr);
                                   background: var(--surface-inverse);
                                   color: var(--surface-inverse-fg);">
      <div>항목</div><div>예산</div><div>실적</div><div>차이</div><div>차이 %</div>
    </div>
    <!-- body rows ... -->
  </div>

  <div class="slide__bottombar">
    <span class="t-emphasis">시사점 — 영업이익 가이던스 하향 권고</span>
  </div>
  <div class="slide__source">Source: 재무팀 KPI, FY26.Q1</div>
  <div class="slide__pagenum">4 / 18</div>
</section>
```

**핵심**: HTML 의 grid 좌표가 Python 의 inch 좌표와 정합. 양쪽 sync 시 — 한 쪽만 바꾸면 PPTX 와 HTML 결과가 달라짐. 동시 갱신 필요.

JS 데이터-드리븐 차트 (assets/waterfall.js, donut.js, kpi-dashboard.js, variance-table.js) 는 python-pptx 의 동일 layout 함수와 **같은 JSON spec** 을 받음 → `spec_normalizer.py` 가 camelCase ↔ snake_case 정규화 자동.

---

## 7. 누락된 layout 함수 (이 프로젝트 미박제)

mck 의 `layouts/` 디렉토리에는 45개 함수. 이 중 `theme_layout_matrix.md` 의 46개와 거의 1:1 매칭. **단 다음은 mck 코드만 있고 매트릭스에 명시 안 됨**:

- `v21_additions.py` — table_insight, meet_the_team, case_study, action_items, timeline, side_by_side, four_column, stakeholder_map, decision_tree
- `v22_additions.py` — horizontal_bar, metric_cards, stacked_area, bubble, dashboard_kpi, dashboard_table, numbered_list_panel, gauge_pair
- `v23_additions.py` — scorecard, checklist, temple, pie, appendix_title, three_images, two_col_image_grid, metric_comparison

→ 위는 mck 의 v2.1/v2.2/v2.3 점진 추가분. 우리 매트릭스 §2 (46개) 에 이미 포함. geometry 는 mck 소스에서 참조.

---

## 8. 변경 절차

새 레이아웃 추가 시:

1. **Schema 추가** (`layout_catalog.md` + mck `validation.py`)
2. **Inference 추가** (`mck/builder/inference.py` — 키 시그니처)
3. **Geometry 작성** — 이 파일에 1-line 요약 + 7 패턴 중 어느 것 사용 표시
4. **함수 구현** — mck `layouts/*.py` 또는 새 모듈
5. **HTML 등가물 작성** — slides-grab 의 `slides/<deck>/` 에 같은 spec 으로 렌더되는 HTML
6. **테마 매트릭스 갱신** (`theme_layout_matrix.md`)
7. **회귀 테스트 추가** — `tests/test_robustness.py` 가 schema 기반 자동 4-case

빠뜨리면: schema 만 있고 geometry 없으면 → 빈 슬라이드. geometry 만 있고 schema 없으면 → 무엇이 와야 할지 사용자가 모름.
