# Theme × Layout Matrix — 잠금 매트릭스

> **이 파일은 명령이다.** 슬라이드 생성 시 `[data-theme="…"]` 가 선언되면, 그 테마가 **허용하는 레이아웃만** 사용해야 한다. 다른 테마의 레이아웃을 끌어다 섞으면 안 된다.
>
> 이전 시스템에서는 4개 aesthetic direction(executive / dark-pitch / academic / editorial)이 자유 혼합 가능했고, 그 결과 한 덱 안에서 톤이 깨졌다. v3부터는 **테마가 곧 레이아웃 카탈로그**다.

---

## 0. 핵심 규칙

1. **한 덱(deck) = 한 테마.** `<html data-theme="…">` 는 덱 전체에서 한 번만 선언. 슬라이드 단위로 바꾸지 않는다.
2. **레이아웃은 테마의 허용 셋(`allowed`)에서만 고른다.** 이 표를 어기면 게이트(`scripts/checklist-guard.mjs` + `pf_rules.md` PF-69) 가 차단해야 한다.
3. **테마 폴백 금지.** `data-theme` 누락 시 `modern` 으로 자동 적용 — 명시적이지 않은 동작은 버그.
4. **`company` 테마는 v3 슬롯.** 사내 마스터 어댑터가 채우기 전까지 `modern` 폴백.
5. **레이아웃 추가 시 이 표를 먼저 갱신.** 새 레이아웃이 어느 테마에 속하는지 결정 못 하면 — 추가하지 않는다.

---

## 1. 4-테마 정체성 (mck 통합 v3 기준)

| 테마 | 정체성 | 캔버스 톤 | 액센트 | 주요 용도 |
|------|--------|----------|--------|----------|
| `modern` (기본) | FP&A 분기 리뷰, 사내 일상 보고. 슬레이트 네이비 + 웜 오렌지 | white (`#FFFFFF`) | orange (`#E87722`) | 분기 리뷰, KPI, P&L bridge |
| `classic` | 정통 McKinsey 톤. 임원·이사회 자료 | white (`#FFFFFF`) | cyan (`#00A3E0`) | 임원 보고, 이사회, 전략 추천안 |
| `dark-mono` | 기술 컨설팅, 발표용 (스크린 우선) | near-black (`#0F1419`) | cold blue (`#4A9EFF`) | 키노트, 데모데이, DA 시연 |
| `company` | (v3) 사내 마스터 어댑터 자동 채움 | TBD | TBD | 사내 표준 마스터 사용 시 |

### 1.1 slides-grab v2 흡수 — 추가 4 테마

| 테마 | 정체성 | 캔버스 톤 | 액센트 | 시그니처 decoration |
|------|--------|----------|--------|----------------------|
| `executive-editorial` | 한국 IR/투자메모/임원보고. warm graphite + navy + orange | warm white (`#F5F5F0`) | navy (`#1428A0`) + orange (`#FF6F00`) | hairline circle + ↗ 화살표 (28~38pt) |
| `dark-pitch` | AI 스타트업 시리즈 IR / 키노트 / YC-스타일 | jet (`#0A0A0B`) | electric cyan (`#00A9E0`) | 80~96pt 헤로 + `// kicker` (JetBrains Mono) |
| `academic` | 학술/연구/정책 백서. 순백 + navy | locked white (`#FFFFFF`) | navy (`#1F4E79`) + chart blue (`#2E75B6`) | 2pt navy 룰 + F-1/D-1 인덱스 |
| `editorial` | 분기 에세이/연간보고/창립자 letter — **Track B (별도)** | cream (`#FAF8F5`) | terracotta (`#C45A3B`) | Newsreader serif + italic em + 드롭캡 |

→ 8 테마 모두 동일 의미적 토큰 contract (`--primary` / `--accent` / `--gray-1..4` / `--surface-inverse` / ...). `colors_and_type.css` 의 `[data-theme]` 블록 8개로 관리.

`editorial` 만 **별도 트랙 (Track B)** — Newsreader serif chrome + 드롭캡 + 인용 글리프 등 다른 chrome 시스템 (action title 룰 적용 안 됨). 다른 7 테마는 모두 mck consulting chrome (action title + 2pt rule + body + bottom_bar + source/page).

`editorial-magazine` 의 5-aesthetic-direction 원본은 v2 매트릭스 밖. 이번에 `editorial` 테마로 정식 흡수.

---

## 2. 레이아웃 카탈로그 (v3.2 — 64개)

레이아웃 ID는 `layout_catalog.md` 의 LayoutSchema 이름과 1:1 매칭.

### 2.1 Structure (구조) — 5개

| ID | 설명 | modern | classic | dark-mono | company |
|----|------|:------:|:-------:|:---------:|:-------:|
| `cover` | 표지 — 좌 네이비 패널 + 우 타이틀 블록 | ✅ | ✅ | ✅ | ✅ |
| `section_divider` | 풀블리드 `surface_inverse` + 큰 섹션 번호/타이틀 | ✅ | ✅ | ✅ | ✅ |
| `closing` | Thank-you — 풀블리드 inverse + 연락처 | ✅ | ✅ | ✅ | ✅ |
| `dark_navy_summary` | bottom-line capsule — inverse 한 문장 | ✅ | ✅ | ❌* | ✅ |
| `appendix_title` | 부록 표지 | ✅ | ✅ | ✅ | ✅ |

\* `dark-mono` 는 이미 다크 → `dark_navy_summary` 가 시각적 대비 없음. **금지.**

### 2.2 Summary / Narrative — 10개

| ID | modern | classic | dark-mono | company |
|----|:------:|:-------:|:---------:|:-------:|
| `toc` (`agenda`) | ✅ | ✅ | ✅ | ✅ |
| `executive_summary` | ✅ | ✅ | ✅ | ✅ |
| `key_takeaway` | ✅ | ✅ | ✅ | ✅ |
| `big_number` | ✅ | ✅ | ✅ | ✅ |
| `two_column_text` | ✅ | ✅ | ❌* | ✅ |
| `two_stat` | ✅ | ✅ | ✅ | ✅ |
| `three_stat` | ✅ | ✅ | ✅ | ✅ |
| `three_trends` | ✅ | ✅ | ✅ | ✅ |
| `five_key_areas` | ✅ | ✅ | ✅ | ✅ |
| `venn` | ✅ | ✅ | ❌* | ✅ |

\* `two_column_text` 는 다크 모노에서 가독성 저하 (얇은 본문 위주). `venn` 은 다크에서 원 교집합 fill blend가 깨짐.

### 2.3 Data Tables — 4개

| ID | modern | classic | dark-mono | company |
|----|:------:|:-------:|:---------:|:-------:|
| `data_table` | ✅ | ✅ | ✅ | ✅ |
| `variance_table` ⭐ | ✅ | ✅ | ✅ | ✅ |
| `rag_status` | ✅ | ✅ | ✅ | ✅ |
| `harvey_ball_table` | ✅ | ✅ | ❌* | ✅ |

⭐ `variance_table` — `cost_nature` 부호 반전 적용 (`domain/fpna_invariants.md`).
\* Harvey ball 채움 단계는 다크에서 75%/100% 식별 불가.

### 2.4 Data Charts — 5개

| ID | modern | classic | dark-mono | company |
|----|:------:|:-------:|:---------:|:-------:|
| `column_historic_forecast` | ✅ | ✅ | ✅ | ✅ |
| `column_simple_growth` | ✅ | ✅ | ✅ | ✅ |
| `line_chart` | ✅ | ✅ | ✅ | ✅ |
| `stacked_column` | ✅ | ✅ | ✅ | ✅ |
| `grouped_column` | ✅ | ✅ | ✅ | ✅ |

### 2.5 Special Charts — 5개

| ID | modern | classic | dark-mono | company |
|----|:------:|:-------:|:---------:|:-------:|
| `waterfall` ⭐ | ✅ | ✅ | ✅ | ✅ |
| `donut` | ✅ | ✅ | ✅ | ✅ |
| `kpi_dashboard` | ✅ | ✅ | ✅ | ✅ |
| `pareto` | ✅ | ✅ | ❌* | ✅ |
| `gauge` | ✅ | ✅ | ❌* | ✅ |

⭐ `waterfall` — base/up/down/subtotal 부호 자동 인지.
\* `pareto` 의 누적선 라벨, `gauge` 의 상태색 (green/amber/red) 이 다크 배경에서 대비 부족.

### 2.6 Compare / Matrix — 7개

| ID | modern | classic | dark-mono | company |
|----|:------:|:-------:|:---------:|:-------:|
| `comparison_table` | ✅ | ✅ | ✅ | ✅ |
| `pros_cons` | ✅ | ✅ | ✅ | ✅ |
| `before_after` | ✅ | ✅ | ❌* | ✅ |
| `swot` | ✅ | ✅ | ✅ | ✅ |
| `bcg_matrix` | ✅ | ✅ | ✅ | ✅ |
| `prioritization_matrix` | ✅ | ✅ | ✅ | ✅ |
| `risk_matrix` | ✅ | ✅ | ❌* | ✅ |

\* `before_after` 의 gray↔inverse 대비 패턴이 다크에서 무너짐. `risk_matrix` 의 3×3 heat map 색상 코딩 다크에서 식별 불가.

### 2.7 Process / Timeline — 8개

| ID | modern | classic | dark-mono | company |
|----|:------:|:-------:|:---------:|:-------:|
| `phases_chevron` | ✅ | ✅ | ✅ | ✅ |
| `vertical_steps` | ✅ | ✅ | ✅ | ✅ |
| `value_chain` | ✅ | ✅ | ✅ | ✅ |
| `funnel` | ✅ | ✅ | ✅ | ✅ |
| `pyramid` | ✅ | ✅ | ✅ | ✅ |
| `gantt_timeline` | ✅ | ✅ | ✅ | ✅ |
| `waves_timeline` | ✅ | ✅ | ✅ | ✅ |
| `cycle` | ✅ | ✅ | ✅ | ✅ |

### 2.8 Org / Insight — 4개

| ID | modern | classic | dark-mono | company |
|----|:------:|:-------:|:---------:|:-------:|
| `org_chart` | ✅ | ✅ | ✅ | ✅ |
| `table_insight` ⭐ | ✅ | ✅ | ❌* | ✅ |
| `quote` (slides-grab) | ✅ | ✅ | ✅ | ✅ |
| `meet_the_team` (slides-grab) | ✅ | ✅ | ✅ | ✅ |

⭐ McK 시그니처 오프너. 인사이트 우측 캡슐.
\* `table_insight` 의 좌측 표 + 우측 회색 캡슐 패턴이 다크에서 약함 (대안: `key_takeaway`).
`quote` 는 풀블리드 surface_inverse 라 dark-mono 에서도 안전. `meet_the_team` 은 image-slot 사진 기반.

### 2.9 v3.2 보조 레이아웃 — 16개

mck v22/v23 흡수. `catalog-additions-3.html` 에 HTML 레퍼런스.

| ID | modern | classic | dark-mono | company | 카테고리 |
|----|:------:|:-------:|:---------:|:-------:|---------|
| `horizontal_bar` | ✅ | ✅ | ✅ | ✅ | 차트 |
| `metric_cards` | ✅ | ✅ | ✅ | ✅ | summary |
| `numbered_list_panel` | ✅ | ✅ | ✅ | ✅ | narrative |
| `temple` | ✅ | ✅ | ✅ | ✅ | framework |
| `scorecard` | ✅ | ✅ | ❌* | ✅ | table |
| `checklist` | ✅ | ✅ | ✅ | ✅ | table |
| `pie` | ✅ | ✅ | ✅ | ✅ | chart |
| `metric_comparison` | ✅ | ✅ | ✅ | ✅ | compare |
| `three_images` | ✅ | ✅ | ✅ | ✅ | image |
| `two_col_image_grid` | ✅ | ✅ | ✅ | ✅ | image |
| `dashboard_kpi` | ✅ | ✅ | ✅ | ✅ | composite |
| `dashboard_table` | ✅ | ✅ | ❌* | ✅ | composite |
| `bubble` | ✅ | ✅ | ✅ | ✅ | chart |
| `stacked_area` | ✅ | ✅ | ✅ | ✅ | chart |
| `gauge_pair` | ✅ | ✅ | ❌* | ✅ | chart |
| `case_study` | ✅ | ✅ | ✅ | ✅ | narrative |

\* `scorecard` 의 5점 도트, `dashboard_table` 의 조밀한 표, `gauge_pair` 의 상태색이 다크에서 식별 저하.
`gauge_pair`·`case_study` 는 schema 정의됨, HTML 레퍼런스는 v3.3 예정.

---

## 3. 권장 데크 구성 (테마별)

### `modern` — FP&A 분기 리뷰 (15–20p)

순서: `cover` → `toc` → `executive_summary` → `section_divider` → **본문** (`big_number` / `variance_table` / `waterfall` / `kpi_dashboard` / `column_historic_forecast`) → `section_divider` → **시사점** (`key_takeaway` / `three_trends`) → **액션** (`vertical_steps` / `phases_chevron`) → `closing`

### `classic` — 임원·이사회 (10–15p)

순서: `cover` → `executive_summary` → **추천안** (`comparison_table` / `pros_cons`) → **근거** (`swot` / `harvey_ball_table` / `risk_matrix`) → **임팩트** (`big_number` / `variance_table`) → **결정 요청** (`dark_navy_summary`) → `closing`

### `dark-mono` — 기술 컨설팅 / 키노트 (12–18p)

순서: `cover` → **문제** (`big_number` / `three_stat`) → **솔루션** (`phases_chevron` / `vertical_steps` / `value_chain`) → **데이터** (`column_simple_growth` / `line_chart` / `kpi_dashboard`) → **로드맵** (`waves_timeline` / `gantt_timeline`) → `closing`

---

## 4. 게이트(차단) — 자동 검증

### 4.1 정적 검증 (HTML 생성 시점)

`scripts/preflight-html.js` 에 신규 룰 추가:

```js
// PF-69 — 테마 × 레이아웃 매트릭스 위반
function checkThemeLayoutMatrix(html) {
  const theme = extractDataTheme(html);              // <html data-theme="...">
  if (!theme) return error("PF-69: <html data-theme='…'> 누락");

  const allowed = THEME_ALLOWED_LAYOUTS[theme];      // 이 파일에서 빌드된 셋
  const usedLayout = extractLayoutId(html);          // <section data-layout="...">

  if (!allowed.has(usedLayout)) {
    return error(
      `PF-69: ${theme} 테마에서 '${usedLayout}' 레이아웃 사용 금지. ` +
      `허용: [${[...allowed].join(", ")}]. ` +
      `theme_layout_matrix.md §2 참조.`
    );
  }
}
```

### 4.2 슬라이드 마크업 의무

모든 슬라이드 `<section>` 에 `data-layout` 명시 필수:

```html
<section data-layout="variance_table" data-screen-label="04">
  …
</section>
```

`data-layout` 없으면 PF-70 ERROR.

### 4.3 폴백 동작

- `data-theme` 누락 → ERROR (PF-71). 자동 폴백 금지.
- 레이아웃 ID 가 매트릭스에 없음 → ERROR (PF-69). 새 레이아웃이라면 이 파일에 먼저 등록.

---

## 5. 추가 규칙 (편집 시)

1. **새 레이아웃을 추가하려면**: `layout_catalog.md` 에 LayoutSchema 추가 → 이 매트릭스 §2.X 에 행 추가 → 각 테마에 대해 ✅/❌ 결정 → 게이트가 자동으로 인식.
2. **테마를 추가하려면**: `colors_and_type.css` 에 `[data-theme="<new>"]` 블록 → 이 매트릭스 §2 의 모든 표에 열 추가 → 각 레이아웃에 대해 ✅/❌ 결정.
3. **레이아웃을 한 테마에서 빼려면 (✅ → ❌)**: 변경 사유를 `audit/` 에 한 줄 기록 (mck의 `experiences.md` 패턴).
4. **`editorial` 트랙**: 이 매트릭스 밖. 별도 파일 `theme_layout_matrix_editorial.md` 로 분리 예정 — 연간보고/창립자 에세이/사진 에세이 전용.

---

## 6. 매트릭스 요약 (한눈에)

| 테마 | 허용 레이아웃 수 | 핵심 시그니처 |
|------|:---------------:|--------------|
| `modern` | 48 / 48 | `variance_table` ⭐ · `waterfall` ⭐ · `kpi_dashboard` |
| `classic` | 48 / 48 | `executive_summary` · `comparison_table` · `harvey_ball_table` |
| `dark-mono` | **39 / 48** | `big_number` · `phases_chevron` · `line_chart` · `gantt_timeline` |
| `company` | 48 / 48 (modern 폴백) | TBD (v3) |

다크모노가 9개 적은 이유: `dark_navy_summary` · `two_column_text` · `venn` · `harvey_ball_table` · `pareto` · `gauge` · `before_after` · `risk_matrix` · `table_insight` — **다크 배경에서 식별 불가능한 시각 요소** (얇은 라인, 미세 컬러 코딩, 백+inverse 패턴) 를 명시적으로 제외했다.

> 48 = 46 core + slides-grab 흡수 `quote` · `meet_the_team`. 전 레이아웃 HTML 레퍼런스 위치는 `layout_catalog.md` §"HTML reference 위치".
