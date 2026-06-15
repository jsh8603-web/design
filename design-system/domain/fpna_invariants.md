# Domain Invariants — FP&A / 한국어 콘텐츠 불변

> 이 시스템의 **고유 가치**: 컨설팅 일반 디자인 시스템에서는 박제되지 않는 도메인 지식이 토큰·검증·변환 곳곳에 박혀 있다. 이 파일은 그 invariants 의 단일 출처(SSOT).
>
> 위반 시 ERROR. 토큰 변경이나 레이아웃 추가 시 이 파일과 매핑 확인 필수.

---

## 1. `cost_nature` — 비용 항목 부호 반전 ⭐

**가장 중요한 FP&A invariant.** `variance_table` 의 비용 행에서는 양수 variance 가 **나쁜 일**(빨강), 음수 variance 가 좋은 일(초록).

### 1.1 정의

```python
# mck/deck_system/layouts/_variance_logic.py
def variance_sign(item):
    """매출 row: actual > budget → 양수 (good, green)
       비용 row: actual > budget → 음수 (bad, red) — cost_nature flip"""
    abs_var = item.actual - item.budget
    if item.get("cost_nature"):
        return -abs_var      # ← 부호 반전
    return abs_var
```

### 1.2 적용 대상

| 행 유형 | `cost_nature` | 양수 variance 표시 |
|---------|:------------:|-------------------|
| 매출 (Revenue) | false (default) | `+50` 초록 ▲ |
| 매출원가 (COGS) | **true** | `+50` 빨강 ▼ |
| 판관비 (SG&A) | **true** | `+50` 빨강 ▼ |
| 영업이익 (Operating profit) | false | `+50` 초록 ▲ |
| 순이익 (Net income) | false | `+50` 초록 ▲ |
| 인건비 | true | `+50` 빨강 ▼ |
| 마케팅비 | true | `+50` 빨강 ▼ |
| R&D 비용 | true (관점에 따라) | `+50` 빨강 ▼ |
| EBITDA | false | `+50` 초록 ▲ |

### 1.3 양쪽 시스템에서 동일

- HTML: `assets/variance-table.js` `renderVarianceTable()`
- PPTX: `mck/deck_system/layouts/_variance_logic.py`

**한쪽만 고치면 안 된다.** 두 파일은 같은 행동을 한다.

### 1.4 사용자 마크업

```json
{
  "type": "variance_table",
  "items": [
    { "label": "매출",     "budget": 1200, "actual": 1260 },
    { "label": "매출원가", "budget": 720,  "actual": 770, "cost_nature": true },
    { "label": "영업이익", "budget": 180,  "actual": 165 }
  ]
}
```

→ "매출원가" 행만 부호 반전. 변환 결과: +50억 → 빨강.

---

## 2. `surface_inverse` — 다크모드 안전 토큰

### 2.1 문제

`primary` 직접 참조하면 `dark-mono` 테마에서 `primary == bg` 라서 풀블리드 효과가 **사라진다**.

```css
/* ❌ */ background: var(--primary);    /* dark-mono 에서 bg와 동일 → invisible */
/* ✅ */ background: var(--surface-inverse);
```

### 2.2 정의 (colors_and_type.css)

| 테마 | `--primary` | `--bg` | `--surface-inverse` |
|------|------------|--------|-------------------|
| modern | `#1A2332` | `#FFFFFF` | `#1A2332` (= primary) |
| classic | `#051C2C` | `#FFFFFF` | `#051C2C` (= primary) |
| **dark-mono** | **`#0F1419`** | **`#0F1419`** | **`#1F2937`** ← 다름 |
| company | `#1A2332` | `#FFFFFF` | `#1A2332` |

### 2.3 적용 대상 (반드시 `--surface-inverse`)

- `section_divider` 풀블리드 배경
- `closing` 풀블리드 배경
- `cover` 좌측 navy 패널
- `dark_navy_summary` 캡슐
- `executive_summary` 의 headline inverse capsule
- 차트 base/subtotal bar (waterfall)
- variance_table 헤더 배경

### 2.4 적용 금지 (`--bg` 또는 `--gray-4`)

- 본문 카드 (takeaway 패널 등) → `--gray-4`
- 슬라이드 캔버스 배경 → `--bg`

### 2.5 게이트

`experiences.ALLOW_PRIMARY_FOR_FULL_BLEED = False` — CSS 또는 inline 에 `var(--primary)` 가 100% 영역 배경으로 사용되면 PF-73 WARN.

---

## 3. EA (East Asian) Font 자동 적용

### 3.1 문제

한국어 슬라이드를 PPTX 로 변환할 때 `<a:ea>` (East Asian fallback) 가 비어 있으면 PowerPoint 가 시스템 폰트(맑은 고딕 등)로 fallback → Pretendard 일관성 깨짐.

### 3.2 해법 (mck `helpers/text.py`)

```python
EA_FONT_REQUIRED_FOR_KOREAN = True   # experiences

def set_run(run, text, ...):
    run.text = text
    set_ea_font(run, "Pretendard")    # 모든 run 에서 자동
    # ...
```

### 3.3 HTML 단계 의무

```css
font-family: "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR",
             "Malgun Gothic", system-ui, sans-serif;
```

(이미 `colors_and_type.css` `--font-sans` 에 박제됨. 다른 font-family 직접 명시 금지.)

### 3.4 변환 단계 의무

`scripts/convert-native.cjs` 가 모든 텍스트 run 에 `eastAsianFont: "Pretendard"` 자동 설정 (이미 구현됨).

---

## 4. `_clean_shape` — Shadow / 3D 상속 차단

### 4.1 문제

python-pptx 가 슬라이드에 shape 추가 시 master/layout 의 `<p:style>` 가 상속됨 → 의도 안 한 shadow / 3D effect 발생.

### 4.2 해법 (mck `helpers/shapes.py`)

```python
def _clean_shape(shape):
    """Strip <p:style> from shape XML — prevents shadow/3D inheritance."""
    spPr = shape._element.find(".//p:spPr", ns)
    style = shape._element.find(".//p:style", ns)
    if style is not None:
        shape._element.remove(style)
```

모든 shape 추가 후 호출.

### 4.3 HTML 등가물 — box-shadow 미사용 (디자인 규약)

HTML 단계에서는 `box-shadow` 가 변환되지 않으므로 **소스에서 아예 금지**.

```css
/* ❌ */ .card { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
/* ✅ */ .card { background: var(--gray-4); border: 1px solid var(--gray-3); }
```

Tint(surface 색상 변화) 로 elevation 표현.

> **PF 번호 주의**: 일반 box-shadow 는 **전용 PF 룰로 자동 검출되지 않는다**(코드엔 `inset` 만 PF-22 WARN). 따라서 본 규약은 **설계 의도(소스 금지)** 이지 PF-66 게이트가 아니다 — 코드의 **PF-66 은 overflow:hidden 콘텐츠 클립**(scrollHeight 초과) 게이트다. 아래 §4.x line-height 1 항도 동일.

---

## 5. 한국어 명사형 종결 (Action Title Tone)

### 5.1 규칙

액션 타이틀은 명사형 종결만. 자세한 내용은 `prompting_rules.md` §1.2.

### 5.2 검증

```python
# mck/deck_system/builder/tone.py
_BAD_ENDINGS = ["습니다", "합니다", "있다", "없다",
                "했다", "이다", "된다", "하다", "한다"]
MAX_ACTION_TITLE_CHARS = 40
```

타이틀이 `_BAD_ENDINGS` 중 하나로 끝나면 WARN (stderr 출력). 빌드는 통과시키되 reviewer 가 알아챔.

### 5.3 HTML 단계 — 인라인 preflight (`scripts/inline-preflight.js`)

브라우저에서 슬라이드 프리뷰 열면 자동으로:
- `<h1 class="t-action">` 텍스트 추출
- `_BAD_ENDINGS` 매칭 → 콘솔 WARN
- 길이 > 40자 → 콘솔 WARN

---

## 6. CJK 줄 높이

| 텍스트 | line-height |
|--------|------------|
| 한국어 본문 | **1.4~1.45** |
| Latin 본문 | 1.20~1.30 |
| 한국어 + Latin 혼용 | **1.4** (CJK 기준) |

experiences 상수: `CJK_LINE_HEIGHT_RATIO = 1.4`, `LATIN_LINE_HEIGHT_RATIO = 1.2`.

### 6.1 큰 폰트 예외

`line-height: 1` + 24pt 이상 폰트 → metric overflow → PF-66 ERROR (text-clipped).
대형 숫자/타이틀: **line-height ≥ 1.15**.

---

## 7. 출처(Source) 의무 표시

모든 콘텐츠 슬라이드 (커버/섹션/클로징 제외) 는 출처 표시.

```html
<div class="slide__source">
  Source: 재무팀 KPI 대시보드, FY26.Q1 마감 · BI 시스템 자동 산출
</div>
```

- 위치: bottom-left
- 크기: 9pt (`var(--pt-foot)`)
- 색: `var(--gray-2)`
- 형식: `Source: [출처], [날짜]` — 자세한 규칙은 `prompting_rules.md` §6.

---

## 8. 슬라이드 챔(chrome) 6요소

모든 콘텐츠 슬라이드는 6요소 의무:

1. **Action title** (`<h1 class="t-action">`) — 명사형 종결
2. **Title rule** (`<div class="slide__rule">`) — 2pt primary 가로선
3. **Content area** (`<div class="slide__content">`) — 본문
4. **Bottom bar** (선택) — takeaway 캡슐
5. **Source line** (`<div class="slide__source">`) — bottom-left, 9pt
6. **Page number** (`<div class="slide__pagenum">`) — bottom-right, 9pt

기하학: `colors_and_type.css` 의 `.slide__title` / `.slide__rule` / etc. 가 자동 배치.

---

## 9. 변경 절차 — 새 invariant 추가

새 도메인 불변을 발견하면:

1. 이 파일에 §N 으로 추가 (정의 + 적용 대상 + 게이트)
2. 양쪽 시스템에 박제:
   - HTML: 해당 슬롯 코드 + `pf_rules.md` 또는 `qa_rules.md` 추가
   - PPTX (mck): `experiences.py` 상수 + `qa/checks.py` 함수
3. `prompting_rules.md` 에 한 줄 추가 (에이전트가 읽도록)
4. 이 변경 사유를 `audit/` 디렉토리에 한 줄 기록

원칙: **인라인 매직 넘버 금지.** 모든 상수는 이 파일 또는 `experiences.py` 의 단일 출처에서 참조.

---

## 10. 실패 모드 누적 (slides-grab 와 동기화)

mck 의 `experiences.py` 상수 19개:

```
MAX_ACTION_TITLE_CHARS = 40
MAX_FOUR_COL_DESC_CHARS = 120
MAX_PROCESS_CHEVRON_STEPS = 5
MAX_PROCESS_CHEVRON_DESC_CHARS = 50
PROCESS_STEP_LABEL_NO_NEWLINE = True
MAX_TIMELINE_LAST_LABEL_CHARS = 6
MAX_BIG_NUMBER_DETAIL_ITEMS = 4
MAX_KPI_TILES = 8
MAX_TWO_STAT_LABEL_CHARS = 30
MAX_THREE_STAT_LABEL_CHARS = 25
MAX_DONUT_SEGMENTS = 6
MAX_PIE_SEGMENTS = 6
MAX_GROUPED_BAR_CATEGORIES = 6
MAX_GROUPED_BAR_SERIES = 3
MAX_PARETO_BARS = 10
MAX_RAG_ROWS = 10
MAX_HARVEY_BALL_OPTIONS = 4
MAX_VARIANCE_TABLE_ROWS = 10
MAX_TWO_COLUMN_TEXT_PER_DECK = 1
```

slides-grab `pf_rules.md` 의 PF-XX 룰 + `pptx-inspection-log.md` 의 누적 이슈 (51KB) 와 **양방향 동기화**한다.

새 실패 → mck `experiences.py` + slides-grab `pf_rules.md` + 이 파일에 동시 추가.
