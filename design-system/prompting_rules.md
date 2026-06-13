# Prompting Rules — 에이전트 슬라이드 생성 지시서

> 이 파일은 슬라이드 HTML을 생성하는 LLM의 **행동 계약**이다. 여기 박힌 규칙을 어기면 게이트가 차단한다.
>
> 출처: slides-grab `pf_rules.md` + mck `tone.py` + `experiences.py` + `SKILL.md`.

---

## 0. 슬라이드 생성 전 의무 체크리스트

순서대로 따라야 한다.

1. **테마 결정** — 사용자가 어느 테마인지 명시했나? `modern` / `classic` / `dark-mono` / `company` 중 하나. 명시 안 했으면 물어본다.
2. **레이아웃 카탈로그 확인** — `layout_catalog.md` 에서 콘텐츠에 맞는 레이아웃 ID 선택. 새 레이아웃 만들지 않는다.
3. **테마×레이아웃 매트릭스 확인** — `theme_layout_matrix.md` §2 에서 선택한 (theme, layout) 조합이 ✅ 인지 검증. ❌ 면 다른 레이아웃 선택.
4. **schema 준수** — `layout_catalog.md` 의 LayoutSchema 의 required / bounds 충족.
5. **불변(invariants) 적용** — `cost_nature`, `surface_inverse`, EA font 등 (`domain/fpna_invariants.md`).
6. **PF rules 준수** — `pf_rules.md` 의 PPTX-safe 규칙 전체.
7. **품질 체크** — `qa_rules.md` 의 9-check + 6-autofix 정신 적용.

---

## 1. 액션 타이틀 (Action Title) — 가장 중요한 규칙

### 1.1 모든 콘텐츠 슬라이드는 액션 타이틀을 갖는다

**액션 타이틀 = "주장" (assertion).** 토픽 라벨이 아니다.

| ❌ 토픽 라벨 | ✅ 액션 타이틀 |
|------------|---------------|
| "시장 분석" | "북미 시장이 3년 내 2배 성장한다" |
| "Q3 실적" | "Q3 매출, 전년 대비 +23%" |
| "결론" | "처리군이 대조군 대비 37% 높은 반응률" |
| "전략 옵션" | "스택 통합 옵션이 ROI 1.4× 우위" |

### 1.2 한국어 어조 — 명사형 종결 (필수)

`mck/deck_system/builder/tone.py` 에서 자동 검증:

```
❌ 평서문 / -다           "북미 매출이 전년 대비 14% 성장했다"
❌ 합니다체              "북미 매출이 전년 대비 14% 성장했습니다"
✅ 명사형 종결           "북미 매출, 전년 대비 +14% 성장"
```

**금지 어미** (tone.py `_BAD_ENDINGS`): `습니다 · 합니다 · 있다 · 없다 · 했다 · 이다 · 된다 · 하다 · 한다`

위반 시 에이전트가 즉시 수정. **본문 (body) 는 합니다체 허용**, 액션 타이틀만 명사형.

### 1.3 길이 제한

- **MAX_ACTION_TITLE_CHARS = 40** (한글 기준, experiences.py)
- 25~35자가 sweet spot.
- 초과 시 자르지 말고 → 메시지 두 개로 쪼개 슬라이드 분할.

### 1.4 Ghost Deck Test

타이틀만 순서대로 읽었을 때 **덱의 논증이 그대로 전달되어야** 한다. 안 되면 타이틀이 약하다.

---

## 2. 한 슬라이드 = 한 메시지

| 규칙 | 값 | 출처 |
|------|---|------|
| 독립 콘텐츠 블록 | 최대 3개 | PF-26 / experiences |
| 단어 수 (영문 / CJK) | ≤120 / ≤80 | PF-28 |
| 리스트 항목 | ≤5 | IL-10 |
| 카드 그리드 | ≤4 | IL-10 |
| Donut segments | ≤6 (초과 시 "기타") | MAX_DONUT_SEGMENTS |
| Process chevron 단계 | ≤5 | MAX_PROCESS_CHEVRON_STEPS |
| Pareto bars | ≤10 | MAX_PARETO_BARS |
| RAG rows | ≤10 | MAX_RAG_ROWS |
| Harvey ball options | ≤4 | MAX_HARVEY_BALL_OPTIONS |
| Variance table rows | ≤10 | MAX_VARIANCE_TABLE_ROWS |
| KPI tiles | ≤8 | MAX_KPI_TILES |
| BIG NUMBER detail items | ≤4 | MAX_BIG_NUMBER_DETAIL_ITEMS |
| Two column text per deck | ≤1 | MAX_TWO_COLUMN_TEXT_PER_DECK |
| 슬라이드 / 덱 | ≤50 | MAX_DECK_SLIDES |
| Font families / 덱 | ≤3 | MAX_FONT_FAMILIES_PER_DECK |

초과 시 조치 순서: ① 텍스트 축약 → ② 항목 수 감소 → ③ **슬라이드 분할** (폰트 축소 금지).

---

## 3. 잠금 타입 스케일 (slides only) — Tier v2

mck Tier v2 (2026.05). **사이즈로 hierarchy 후퇴 금지**; 후퇴는 weight/color 로.

| Tier | pt | px @ 1.333 | 역할 | CSS 클래스 |
|------|----|-----------:|------|-----------|
| **cover** | 44 | 58.7 | Cover title only | `.t-cover` |
| **section** | 28 | 37.3 | Section / TOC title | `.t-section` |
| **subtitle** | 24 | 32.0 | Cover subtitle | `.t-subtitle` |
| **action** | 22 | 29.3 | Action title (slide title) | `.t-action` |
| **sub_header** | 18 | 24.0 | 카드 헤딩, 섹션 타이틀 | `.t-subheader` |
| **body** | 17 | 22.7 | **Body — 슬라이드 기본** | `.t-body` |
| **body_compact** ⭐ | 16 | 21.3 | 3+ 열 dense 그리드 카드 본문 | `.t-body-compact` |
| **small** | 15 | 20.0 | 캡션, sub-label | `.t-small` |
| **chart_label** | 10 | 13.3 | mono 라벨, 차트 축 | `.t-chart-label` |
| **footer** | 9 | 12.0 | 출처, 페이지 번호 ONLY | `.t-foot` |

### 핵심 원칙

1. **Body content min = 16pt** (`body_compact`). 본문은 16pt 미만 금지.
2. **9pt 는 footer (출처/페이지) ONLY** — 다른 어떤 body 도 9pt 불가.
3. **사이즈로 위계 후퇴 금지** → `weight: 600 → 400` 또는 `color: gray-1 → gray-2` 로 후퇴.
4. **Hero number 변용** (`big_number` 레이아웃): 160pt 까지 허용 (unit 64pt).

### Author self-check (downsizing 전)

- [ ] 문장/항목/설명? → `body` 또는 `body_compact` (16pt+)
- [ ] 카드 안 + 좁은 카드 (3+ 열)? → `body_compact` 허용
- [ ] 메타데이터/캡션? → `small` (15pt)
- [ ] eyebrow / mono uppercase 태그? → `chart_label` (10pt)
- [ ] 출처/페이지 번호? → `footer` (9pt) **다른 body 절대 9pt 금지**
- [ ] "그냥 작아 보이게 하고 싶다"? → **REJECT.** weight/color 후퇴 사용.

Hero 변용: `.n-hero` 클래스 (48pt+, weight 800) — `big_number` 의 hero 영역 전용.

자세한 tier 적용 가이드: `code_inventory.md` §③.

---

## 4. 색 — 의미적 토큰만 사용

### 4.1 슬라이드는 의미적 토큰만 (raw hex 금지)

```css
✅ color: var(--primary);          /* 타이틀, TOC 번호, 디바이더 */
✅ color: var(--accent);           /* 슬라이드당 1개 강조 */
✅ color: var(--positive);         /* 양수 delta, ▲ */
✅ color: var(--negative);         /* 음수 delta, ▼ */
✅ background: var(--surface-inverse);     /* 풀블리드 inverse */
✅ background: var(--gray-4);              /* takeaway 패널 */
✅ color: var(--gray-1);                   /* body */
✅ color: var(--heading);                  /* 슬라이드 타이틀, 룰 (테마 안전) */

❌ color: #1A2332;        /* hex 직접 사용 — 다크모드에서 깨짐 */
❌ color: navy;
❌ background: linear-gradient(...);
```

### 4.2 accent 는 슬라이드당 1개

전체 슬라이드를 봤을 때 사용자의 시선이 **가장 먼저 가야 할 한 곳**에만 `--accent`. 그 외 모든 강조는 `--primary` 또는 weight 차이로 처리.

### 4.3 풀블리드 / 다크 캡슐은 `--surface-inverse`

`section_divider` / `closing` / `dark_navy_summary` / `executive_summary` 의 inverse capsule 전부 `--surface-inverse`. **절대 `--primary` 직접 참조 금지** — `dark-mono` 테마에서 primary == bg 라 풀블리드가 사라진다. (experiences: `ALLOW_PRIMARY_FOR_FULL_BLEED = False`)

### 4.3b 슬라이드 타이틀·룰은 `--heading` (절대 `--primary` 금지)

슬라이드 타이틀(`.s-title` / `.slide__title` / `.t-action` / `.t-section` / `.t-cover` / `.t-subheader`)과 타이틀 룰(`.s-rule` / `.slide__rule`)의 색은 **`var(--heading)`** 사용. `--heading` 은 라이트 테마에서 `var(--primary)`, `dark-mono` 에서 밝은 값(`#E5E7EB`)으로 해석된다.

```css
✅ .s-title { color: var(--heading); }
✅ .s-rule  { background: var(--heading); }
❌ .s-title { color: var(--primary); }   /* dark-mono 에서 primary==bg → 타이틀 소멸 */
```

`--surface-inverse` 와 같은 원리(§4.3): 라이트 전용 색을 다크에 그대로 쓰면 사라진다. 신규 chrome 요소도 동일 규칙 — verifier 가 잡은 실패 모드.

### 4.4 status color 페어링

| 의미 | 토큰 | 페어링 |
|------|------|-------|
| 달성 / 성장 | `--positive` | ▲ + 부호 (+14.3%) |
| 미달 / 손실 | `--negative` | ▼ + 부호 (−1.8%p) |
| 중립 | `--gray-2` | ● (neutral_threshold 이내) |

---

## 5. 한국어 (CJK) 전용 규칙

### 5.1 폰트 — Pretendard 통일

```css
font-family: var(--font-sans);   /* Pretendard + EA fallbacks */
```

다른 한국어 폰트 (Noto Sans KR, Malgun Gothic 등) 명시적 사용 금지. fallback 으로만.

### 5.2 EA font 자동 적용 (PPTX 변환 시)

mck `helpers/text.py` 의 `set_ea_font()` 가 모든 run 에 자동 적용. HTML 단계에서는 `font-family: var(--font-sans)` 만 쓰면 됨.

**위반 시**: PPTX 에서 한국어 글자가 시스템 폰트로 falls back → CJK rendering 깨짐.

### 5.3 줄 높이

| 텍스트 | line-height |
|--------|------------|
| 한국어 본문 | **1.4~1.45** (`CJK_LINE_HEIGHT_RATIO = 1.4`) |
| Latin 본문 | 1.20~1.30 (`LATIN_LINE_HEIGHT_RATIO = 1.2`) |
| Hero number (24pt+) | **≥ 1.15** (PF-66: line-height 1 + 큰 폰트 = text-clipped) |

### 5.4 CJK 텍스트 폭 공식

```
text_width = CJK문자수 × font_size + 라틴문자수 × font_size × 0.6
검증: text_width ≤ container_width × 0.8
```

위반 → 컨테이너 확대 or 텍스트 축약 (font 축소 금지).

### 5.5 숫자·단위

- 천 단위 구분: `,` — `1,260`
- 한국어 단위 인라인: `1,260억`, `2조 4,800억`, `60개국`
- 퍼센트: `14.3%`, `+14.3%`, `−1.8%p`
- delta: 부호 + 값 붙여서 — `+14.3%`. **공백 금지** (`+ 14.3 %` 금지)
- 기간: `YoY`, `QoQ`, `MoM`, `FY26.Q2`

---

## 6. 출처(Source) 의무 표시

**모든 콘텐츠 슬라이드는 출처를 갖는다.** 위치: bottom-left, 9pt, `--gray-2`.

```
Source: [출처명], [날짜]
Source: 재무팀 KPI 대시보드, FY26.Q1 마감 · BI 시스템 자동 산출
Source: McKinsey Korea Insight, 2024 · 산업통상자원부 시장보고서
Source: 내부 분석, FY26.Q1
```

Format:
- `Source:` prefix (영문, 콜론)
- 영한 혼용 OK
- 세미콜론 금지
- 날짜: `FY**.Q*` 또는 `YYYY` 또는 `YYYY.MM.DD`
- 여러 소스: `·` 로 join

**커버·섹션 디바이더·클로징** 슬라이드는 출처 면제.

---

## 7. 절대 금지 (PF-compliance 단축 목록)

전체 목록은 `pf_rules.md` 참조. 슬라이드 생성 시 절대 발생해선 안 되는 것:

- `<table>` 태그 (PF-63 → CSS grid 로 대체)
- `linear-gradient` + 흰색 텍스트 (PF-01)
- `rgba()` 배경 (PF-42 → 솔리드 hex)
- `<p>` / `<h*>` / `<li>` 에 background/border (PF-07 → `<div>` 래핑)
- `<body>` 외 element 에 `background: url(...)` (PF-05)
- 국기 이모지 🇰🇷🇺🇸 (PF-12 → PNG/SVG)
- `box-shadow` — 슬라이드 안 (PF-66, full ERROR)
- `text-decoration: underline` (IL-38)
- `opacity < 1.0` 배경 (PF-42)
- `<table>` 등가의 `column-count: N` (PF-48)
- `conic-gradient`, `radial-gradient` 비-body (PF-62)
- 슬라이드 파일명 ≠ `slide-NN.html` (PF-68)
- `<html data-theme="...">` 누락 (PF-71)
- `<section data-layout="...">` 누락 (PF-70)
- 매트릭스 위반 — 테마에서 금지된 레이아웃 사용 (PF-69)
- LayoutSchema 위반 — required 미충족 / type 불일치 / bounds 초과 (PF-72)

---

## 8. 절대 사용하지 않는 표현

| 카테고리 | 예시 | 대안 |
|---------|------|-----|
| 1인칭 | "we / our / 우리" | 3인칭 또는 명사형 |
| 헤지 부사 | "perhaps / arguably / 아마도 / 어쩌면" | 단정 또는 제거 |
| 글꼴체 | "-스럽다 / -같다 / -처럼" | 명사 또는 정량 |
| 느낌표 | `!` | 마침표 또는 명사형 종결 |
| 이모지 | 😊🎉✨ | (Creative/Education 모드 외 금지) |
| 국기 이모지 | 🇰🇷🇺🇸 | PNG/SVG `<img>` |

---

## 9. 슬라이드 마크업 의무 골격

```html
<!doctype html>
<html lang="ko" data-theme="modern">  <!-- PF-71 의무 -->
<head>
  <link rel="stylesheet" href="colors_and_type.css">
</head>
<body>
  <section
    class="slide--themed"
    data-layout="variance_table"          <!-- PF-70 의무 -->
    data-screen-label="04">               <!-- 코멘트 anchor -->

    <h1 class="slide__title t-action">    <!-- 액션 타이틀 — 명사형 종결 -->
      매출원가 +50억 초과, 영업이익 −15억 미달
    </h1>
    <div class="slide__rule"></div>

    <div class="slide__content">
      <!-- 레이아웃 본문 -->
    </div>

    <div class="slide__source">
      Source: 재무팀 KPI 대시보드, FY26.Q1 마감
    </div>
    <div class="slide__pagenum">4 / 18</div>
  </section>
</body>
</html>
```

---

## 10. 변환 (PPTX) 안전 — HTML 작성 시 미리 신경 쓸 것

| 항목 | 규칙 |
|------|-----|
| 이미지 컨테이너 | `min-width: 0`, `overflow: hidden`, `display: flex; align-items: center` 시 `height: 100%` 의무 |
| 이미지 최소 크기 | ≥ 260pt × 180pt (슬라이드 면적의 25%, PF-57 / PF-70) |
| 이미지 src | `<img>` 의 width/height inline pt 명시. `ls assets/` 로 파일 존재 확인 (PF-58) |
| 이미지 비율 | `object-fit: cover` 만 사용 (PF-21 / PF-43) |
| 이미지 비율 | `object-fit: cover` 만 사용 (PF-21 / PF-43) |
| 슬라이드 캔버스 | **13.333" × 7.5" (1280×720px)** — v3 표준 (mck 통합) |
| 슬라이드 padding | 양옆 0.8" (76.8px); bottom safe = source line at 7.05" |
| Grid table 컬럼 | 고정 inch/pt, 합계 ≥ 가용폭 × 0.9 |
| **레이아웃 함수 시그니처** | mck `render_fn(slide, spec, theme, *, page_num, total)` — `layout_geometry.md` §4 |
| **레이아웃 패턴 7가지** | A 풀블리드 / B 표준 chrome / C 헤더-행 테이블 / D N-col 균등 / E 좌-hero 우-stack / F 좌-detail 우-카드 / G annotated capsule — `layout_geometry.md` §1 |

---

## 11. 우선순위 충돌 해결

규칙이 충돌하면 우선순위:

1. **`pf_rules.md`** (PPTX 변환 안전) — 절대 우선
2. **`theme_layout_matrix.md`** — 테마 매트릭스
3. **`layout_catalog.md`** (LayoutSchema)
4. **`domain/fpna_invariants.md`** (도메인 불변)
5. **`prompting_rules.md`** (이 파일 — 어조, 길이)
6. **`qa_rules.md`** (사후 검증)
7. 미적 판단 — 위 모두 충족 후

---

## 12. 자가 개선 루프 (로컬 ↔ 클라우드)

로컬 slides-grab 에서 새 실패 모드 발견 → **항상 이 파일과 `experiences` 상수에 박제**한다.

```
[로컬 발견]                  [이 파일 갱신]
─────────────                ─────────────
PF/VP/VV 가 새 이슈 검출  →  prompting_rules.md 에 한 줄
generate-images.mjs 가       theme_layout_matrix.md 갱신
잘못된 이미지 생성        →  nano_banana_guide.md 무드 매트릭스
QA 가 새 카테고리 발견   →  qa_rules.md 추가

새 실패 모드 = 새 규칙. 인라인하지 말고 박제.
```

자세한 sync 절차는 `pipeline_handoff.md`.
