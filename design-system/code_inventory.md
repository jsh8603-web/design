# Code-level Inventory — mck pptx 엔진 흡수 카탈로그

> 처음 통합 라운드에서 놓친 mck 의 **코드 레벨 자산** 을 박제. 모듈별로 정리. 코드 자체는 로컬에서 실행 (`mck/deck_system/` Python), 이 문서는 **계약·인터페이스·정책** 의 단일 출처.
>
> 권위: mck `pptx/` 디렉토리 (cross-project read-only). 이 프로젝트에 사본 복사 옵션 — 점진적.

---

## ① spec_normalizer.py — JSON spec dual-target 계약 ⭐⭐⭐

**핵심 가치:** 같은 JSON 이 HTML 과 PPTX 양쪽을 구동. 사용자가 한 번만 작성한 spec 으로 두 출력 가능.

```python
# mck/deck_system/builder/spec_normalizer.py
def normalize_spec(spec: Any) -> Any:
    """재귀적으로 dict 키를 snake_case 로 변환. 값(한국어 포함) 불변."""
    # fooBarBaz → foo_bar_baz, 이미 snake_case 면 그대로
    # 리스트는 재귀, 스칼라는 그대로
```

### 사용 예

```js
// HTML 시스템 (JavaScript) 에서 작성한 spec
const spec = {
  "type": "varianceTable",          // camelCase OK
  "items": [{ "label": "매출", "budget": 1200, "actual": 1260 }],
  "unitDefault": "억",
  "costNature": false
};

// → Python pptx 엔진이 자동으로 normalize:
// {"type": "variance_table", "items": [...], "unit_default": "억", "cost_nature": false}
```

### 계약 결과

- **단일 출처 (JSON)** 이 HTML + PPTX 양쪽 출력 가능
- 사용자가 어느 쪽 표기 (camelCase / snake_case) 를 쓰든 동일 결과
- 신규 필드 추가 시 양쪽 시스템에서 동일 키로 명명 의무

### slides-grab 와의 매핑

slides-grab 의 outline 포맷 (`slide-outline.md` 의 NanoBanana: tag 등) → JSON spec 으로 정규화 → 양쪽 출력. 통합 시 outline → spec 변환 단계가 추가됨.

---

## ② errors.py — 5-class friendly errors ⭐⭐⭐

**핵심 가치:** 디버깅 시간 5분 → 30초.

### 5 카테고리

| 클래스 | 발생 시점 |
|--------|---------|
| `InputValidationError` | spec 필드 누락/타입 오류/bound 위반 |
| `CJKFontError` | EA font (Pretendard) 적용 실패 |
| `ThemeError` | 테마 조회/팔레트 해석 실패 |
| `LayoutOverflowError` | experiences.py 상수 위반 (donut > 6 segments 등) |
| `ImagePlaceholderError` | image_placeholder helper 렌더 실패 |

모두 `DeckSystemError` 상속. 구조화 필드:

```python
class DeckSystemError(Exception):
    layout_name: str        # 어느 레이아웃에서
    slide_num: int          # 1-based 슬라이드 번호
    message: str            # 짧은 설명
    expected: str           # 무엇이 와야 했나
    got: str                # 실제 무엇이 왔나
    fix: str                # 해결 방법 (한 줄)
    example: dict           # 동작하는 예시 dict
```

### 출력 예 (CLI)

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

### slides-grab 박제 매핑

- `preflight-html.js` 의 PF-XX ERROR 메시지를 이 5-class 패턴으로 재구성 권장
- structured fields → JSON 직렬화 → CI 도구 친화
- example dict — 사용자가 복붙해서 즉시 동작 가능한 코드 조각

---

## ③ Typography Tier v2 ⭐⭐⭐ — body 최소 16pt

**중요: 이전 박제한 룰 (10pt floor) 보다 보수적.** mck 의 새 tier system 으로 갱신.

### 7-tier 매핑

| Tier | pt | px @ 1.333 | Token | 언제 |
|------|----|-----------:|-------|------|
| action | 22 | 29.33 | `--fs-action` | 슬라이드-레벨 결론 타이틀 (one per slide) |
| sub_header | 18 | 24 | `--fs-subheader` | 카드 헤딩, 섹션 타이틀 |
| body | 17 | 22.67 | `--fs-body` | 본문 문장, 단락 — **슬라이드 기본** |
| **body_compact** ⭐ | **16** | **21.33** | `--fs-body-compact` | 3+ 열 dense 그리드의 카드 본문 |
| small | 15 | 20 | `--fs-small` | 캡션, 짧은 메타, 카드 sub-label |
| chart_label | 10 | 13.33 | `--fs-chart` | mono 라벨, 차트 축, 카테고리 태그 |
| footer | 9 | 12 | `--fs-foot` | 출처, 페이지 번호 ONLY |

⭐ `body_compact` 가 small↔chart_label 사이 5pt 갭을 메움.

### 핵심 원칙 — "사이즈로 위계 후퇴 금지"

**시각적 후퇴가 필요할 때 사이즈를 줄이지 마라.** 대신:
- **Weight** 후퇴: 600 → 400
- **Color** 후퇴: gray-1 → gray-2
- **Indent / 디바이더** 추가

### Author self-check (body 이하로 내리기 전)

- [ ] 문장/항목/설명인가? → `body` 또는 `body_compact` (16pt+)
- [ ] 카드 내부 + 카드 좁음 (3+ 열)? → `body_compact` 허용
- [ ] 메타데이터/캡션? → `small` (15pt)
- [ ] eyebrow / 카테고리 라벨 / mono uppercase 태그? → `chart_label` (10pt)
- [ ] 출처/페이지 번호? → `footer` (9pt) — **다른 body 콘텐츠 NEVER 9pt**
- [ ] "그냥 작아 보이게 하고 싶다"? → **REJECT.** weight/color 로 후퇴.

### 금지

- ❌ 임의 px 값 — system token 만
- ❌ body content < 12pt (footer 외)
- ❌ 사이즈로 hierarchy 후퇴

### 이전 룰 ("10pt floor") 와의 관계

PF-25 의 "10pt 절대 하한" 은 여전히 유효 (시스템 차원의 보호). 하지만 **mck Tier v2 는 더 보수적 (16pt body floor)** — body content 는 16pt 이상이어야 함. 10pt 는 chart_label / footer 에만.

→ `prompting_rules.md` §3 갱신 완료 (별도).

---

## ④ helpers/shapes.py — Shape primitives ⭐⭐

PPTX 파일 손상을 방지하는 5개 핵심 헬퍼.

### 함수 인벤토리

| 함수 | 역할 | invariant |
|------|-----|---------|
| `_clean_shape(shape)` | `<p:style>` 자동 strip — shadow/3D 상속 차단 | 모든 add_* 함수에서 자동 호출 |
| `add_rect(slide, x, y, w, h, fill_hex)` | 솔리드 fill 사각형, no border (flat 시스템) | `_clean_shape` 자동 |
| `add_oval(...)` | 솔리드 fill 타원 | `_clean_shape` 자동 |
| `add_hline(slide, x, y, length, color, thickness_pt=2.0)` | **수평선 — `add_connector()` 대체** | `add_connector` 는 `<p:style>` 누설 → 파일 손상 |
| `add_textbox(slide, x, y, w, h)` | 빈 textbox + 0 margins | text helpers 가 populate |
| `add_block_arc(slide, x, y, size, fill, start, end)` | donut/pie segment — native BLOCK_ARC, segment 당 1 shape | 6개 segment 초과 시 label anchor 미세 오프셋 (engine bug whitelist) |

### 절대 금지

- `add_connector()` — `<p:style>` 잔여 → PPTX 파일 손상. **`add_hline()` 사용.**
- shape 추가 후 `_clean_shape()` 호출 누락 — shadow 상속 위험.
- raw `font.name = ...` — EA font 우회. `set_run()` 사용.

### slides-grab 박제 매핑

slides-grab 의 `convert-native.cjs` 는 PptxGenJS 사용. PptxGenJS 의 line/shape 헬퍼는 자체 검증 — 별도 `_clean_shape` 불필요. 하지만 **invariant 자체 (no shadow, no 3D, flat fills)** 는 양쪽 공통:
- HTML 단계: PF-66 (box-shadow 금지)
- python-pptx: `_clean_shape()` strip
- PptxGenJS: 기본값에서 shadow 미생성 — 명시적으로 추가하지 않으면 안전

---

## ⑤ helpers/text.py — set_run + set_ea_font ⭐⭐

EA font 자동 적용으로 PowerPoint 가 Gulim/SimSun 으로 fallback 되는 것 차단.

### 함수 인벤토리

```python
def set_ea_font(run, typeface: str) -> None:
    """run 의 <a:ea> 엘리먼트에 typeface 설정.
    python-pptx 가 직접 노출 안 함 — XML 패치."""

def set_run(run, text, *, theme, size=None, bold=False,
            color=None, family=None, ea_font=True) -> None:
    """run 의 텍스트 + 포맷팅 한 번에. ea_font=True 가 기본."""

def write_paragraph(tf, text, *, theme, size, bold=False,
                    color=None, align=PP_ALIGN.LEFT, line_spacing=None) -> None:
    """첫 paragraph 의 run 들을 모두 지우고 새 run 으로 교체."""
```

### invariant

- 모든 텍스트 run 은 `set_run()` 경유. raw `font.name = ...` 금지.
- `ea_font=True` 가 기본값 — Korean 안전.
- `font.name = theme.typography.family_en` (Latin) + `<a:ea> = family_ea` (Korean) → CJK 자동 fallback 없음.

---

## ⑥ helpers/chrome.py — 슬라이드 chrome 헬퍼 ⭐⭐

콘텐츠 슬라이드의 6요소를 자동 그리는 헬퍼. 모든 슬라이드 의무 (cover/divider/closing 예외).

### 함수 인벤토리

| 함수 | 그리는 것 | 위치 (mck 13.333×7.5") |
|------|---------|-----------------------|
| `add_action_title(slide, title, theme, warn_callback)` | 타이틀 + 2pt primary 가로선 | (0.8, 0.15) ~ (12.533, 1.05) |
| `add_source(slide, text, theme)` | "Source: ..." bottom-left, 9pt gray-2 | (0.8, 7.05) |
| `add_page_number(slide, num, total, theme)` | "N/M" bottom-right, 9pt gray-2 | (12.2, 7.05) |
| `add_section_marker(slide, marker, theme)` | top-right uppercase 라벨 (cover/divider 용) | (slide_w - margin - 2, 0.15) |
| `add_bottom_bar(slide, text, theme, tag="한 줄로 —")` | gray-4 takeaway capsule, 16pt bold | (0.8, 6.2) ~ (12.533, 6.85) |

### tone validator callback

`add_action_title` 가 `warn_callback` 받음:
- `validate_action_title(title)` 결과 → stderr WARN
- 빌드는 통과 (autofix 가 라운드에서 수정 시도)

---

## ⑦ qa/autofix.py — **8 repair rules** (이전 박제 6개에서 +2) ⭐⭐

이전 `qa_rules.md` 에 6개로 박제했지만 mck 코드 실제로는 **8개 룰**.

### 정확한 8 rules

| Rule | What | 임계값 |
|------|------|------|
| `_fix_action_title` | `…` 로 truncate | > MAX_ACTION_TITLE_CHARS (40) |
| `_fix_donut_segments` | 꼬리 "기타" 머지 | > MAX_DONUT_SEGMENTS (6) |
| `_fix_chevron_steps` | 초과 step 제거 + `\n` 제거 | > MAX_PROCESS_CHEVRON_STEPS (5) |
| `_fix_kpi_tiles` | 초과 KPI tile 제거 | > MAX_KPI_TILES (8) |
| `_fix_big_number_details` | 초과 detail 제거 | > MAX_BIG_NUMBER_DETAIL_ITEMS (4) |
| `_fix_four_column_desc` | description truncate | > MAX_FOUR_COL_DESC_CHARS (120) |
| **`_fix_pareto_overflow`** ⭐ | top-(N-1) + "기타" 머지 | > MAX_PARETO_BARS (10) |
| **`_fix_grouped_bar_series`** ⭐ | series cap + dropped 라벨 로깅 | > MAX_GROUPED_BAR_SERIES (3) |

⭐ 이번 박제에 추가. `qa_rules.md` §2 갱신.

### Pipeline (4-stage)

```
[1] Page brief        — 각 spec 요약
[2] Dual QA           — qa_runner 가 있으면 실행
[3] Auto-fix          — _RULES predicate 매칭 → fix 함수 호출 (in-place)
[4] Gate              — QA 재실행. passed=true 까지 max_rounds (default 3) 반복
```

각 rule 은 `AutofixAction(slide_idx, rule, before, after)` 발행.

---

## ⑧ adapter/profile.py — 사내 .pptx master 어댑터 ⭐⭐⭐

**v3 `[data-theme="company"]` 슬롯의 핵심.** 사내 마스터 PPTX 를 읽어 token 자동 추출 → `theme_company.py` 자동 생성.

### profile_master() 추출 항목

```python
profile = profile_master("/path/to/company_master.pptx")
# {
#   "source": "...",
#   "color_scheme": {
#     "bg1": "#FFFFFF",     # OOXML a:lt1 → background light
#     "tx1": "#000000",     # a:dk1 → text dark
#     "bg2": "...",          # a:lt2 → background lighter
#     "tx2": "...",          # a:dk2 → text darker
#     "accent1": "...",     # a:accent1 → primary brand
#     "accent2": "...",     # a:accent2 → accent
#     ...                    # accent3..6
#   },
#   "font_scheme": {
#     "major": "Arial",     # a:majorFont/a:latin
#     "minor": "Arial"      # a:minorFont/a:latin
#   },
#   "slide_master_dims": {"width_in": 13.333, "height_in": 7.5},
#   "n_slides": 14, "n_masters": 1,
# }
```

### `surface_inverse` 자동 매핑

`theme_from_profile.py` 가 light/dark 마스터 자동 감지:

```
light master (luminance(bg1) >= 0.5):
  surface_inverse = accent1   # = primary brand color
  surface_inverse_fg = "#FFFFFF"

dark master (luminance(bg1) < 0.5):
  surface_inverse = bg2       # 약간 lighter panel — 시각적 변화 유지
  surface_inverse_fg = "#E5E7EB"
```

→ light/dark 무관하게 풀블리드 슬라이드가 항상 visible.

### CLI

```bash
python -m deck_system.adapter.profile \
    /path/to/company_master.pptx \
    --output-dir deck_system/tokens/ \
    --name company

# 결과:
# deck_system/tokens/_company_profile.json   ← raw 추출
# deck_system/tokens/theme_company.py        ← 자동 생성된 theme 모듈

# 사용:
python -m deck_system.cli build deck.json -o out.pptx --theme company
```

### 추출 안 되는 것 (한계)

- 슬라이드 layout-specific accents (theme-level color 만)
- 이미지 배경 (로고, 워터마크)
- 커스텀 font substitution
- per-master typography override

→ 위 추출하려면 tristan-mcinnis 의 마스터 layout 복사 방식 (별도 도구) 사용.

### slides-grab 박제 매핑

slides-grab 에는 사내 마스터 어댑터 없음 (v3 추가). 이 어댑터는 **로컬 only** — 클라우드는 사내 .pptx 마스터를 받아 처리할 환경 아님.

→ 사내 마스터 → adapter → `theme_company.py` → slides-grab `themes/company.css` 자동 동기화 (양방향 sync 절차에 포함).

---

## ⑨ builder/inference.py — FP&A 우선 시그니처 ⭐⭐

JSON spec 에서 명시적 `type` 없을 때, 어떤 레이아웃인지 자동 추론. **FP&A 시그니처가 generic 보다 먼저** 검사됨.

### 우선순위 (코드 순서대로)

1. **명시적 `type` 필드** → 그대로 사용 (passthrough)
2. **FP&A 우선** (가장 specific):
   - `items[].type ∈ {base, up, down, subtotal}` → `waterfall`
   - `items[].budget + items[].actual` → `variance_table`
   - `kpis` (list) → `kpi_dashboard`
   - `segments + center_value` → `donut`
   - `number + title` → `big_number`
3. **Track 1 generic** (mck v2):
   - `stats` → two/three_stat
   - `trends` → three_trends
   - `swot`, `pros_cons`, `risk_matrix` 등
4. **V2.2 / V2.3 추가** (대략 25개 더)

### Fallthrough 에러

```
ValueError: Cannot infer slide type from spec keys: ['foo', 'bar']
```

→ 명시적 `"type": "..."` 추가 또는 schema 매칭되는 필드명으로 정정.

---

## ⑩ tests/test_robustness.py — schema-parametrized 회귀 ⭐⭐

**모든 LayoutSchema 에 대해 자동으로 4 케이스씩 회귀 테스트.** 

```python
import pytest
from deck_system.builder.validation import LAYOUT_SCHEMAS

@pytest.mark.parametrize("layout_name", LAYOUT_SCHEMAS.keys())
def test_minimal_example_renders(layout_name):
    """schema 의 example dict 가 실제로 렌더되는지."""

@pytest.mark.parametrize("layout_name", LAYOUT_SCHEMAS.keys())
def test_missing_required_raises(layout_name):
    """required 필드 누락 시 InputValidationError 인지."""

@pytest.mark.parametrize("layout_name", LAYOUT_SCHEMAS.keys())
def test_wrong_type_raises(layout_name):
    """type 위반 시 InputValidationError 인지."""

@pytest.mark.parametrize("layout_name", LAYOUT_SCHEMAS.keys())
def test_bounds_violation_warns(layout_name):
    """min/max bound 초과 시 warning 또는 autofix 대상인지."""
```

### 가치

- 새 레이아웃 등록 시 → schema 추가만으로 자동 4 테스트
- 회귀 방지 — schema 가 바뀌면 즉시 발견
- 통합 시 slides-grab `tests/run-full-regression.mjs` 에 동일 패턴 적용

---

## ⑪ Builder API surface (호출 표면) ⭐

```python
from deck_system import PresentationBuilder, MODERN, CLASSIC, DARK_MONO

b = PresentationBuilder(theme=MODERN)

# Spec 추가 (단일)
b.add("variance_table",
      title="매출원가 +50억 초과",
      items=[{"label": "매출", "budget": 1200, "actual": 1260},
             {"label": "매출원가", "budget": 720, "actual": 770, "cost_nature": True}])

# 또는 spec dict 리스트 일괄
b.add_specs(spec_list)

# QA 실행
report = b.run_qa()
print(report.errors)        # List[Finding]
print(report.warnings)
print(report.to_dict())     # JSON 직렬화

# Autofix (4-stage pipeline)
result = b.run_autofix(max_rounds=3)
for action in result.actions:
    print(f"[{action.slide_idx}] {action.rule}: {action.before} → {action.after}")

# 저장 + QA 보고서
b.save("out.pptx",
       qa_report_path="out_qa.json",   # 옵션: QA report JSON 동시 저장
       auto_fix=True)                   # 옵션: 저장 전 autofix 자동 실행
```

### CLI 매핑

| Command | Builder API |
|---------|-------------|
| `build SPEC -o OUT` | `add_specs(load_spec(SPEC))` + `save(OUT)` |
| `list-layouts [--category C]` | `registry.list_layouts(category=C)` |
| `show-schema LAYOUT` | `LAYOUT_SCHEMAS[LAYOUT]` |
| `validate SPEC` | `add_specs(...)` → `validate_layout_input` exceptions |
| `themes` | `[MODERN, CLASSIC, DARK_MONO, COMPANY]` |
| `init [DIR]` | starter spec 템플릿 작성 |

---

## ⑫ 누적 변경 요약 (이 라운드 추가)

| 자산 | 어디에 박제 |
|------|----------|
| spec_normalizer dual-target | 이 파일 §① + `pipeline_handoff.md` §sync 절차 |
| 5-class errors | 이 파일 §② + `qa_rules.md` §5 (신규) |
| Typography Tier v2 | `prompting_rules.md` §3 갱신 (별도 작업) |
| 8 autofix rules | `qa_rules.md` §2 갱신 (8개로) |
| Shape primitives | 이 파일 §④ |
| set_ea_font / set_run | `domain/fpna_invariants.md` §3 (기존) + 이 파일 §⑤ |
| Chrome helpers | 이 파일 §⑥ |
| Master adapter | 이 파일 §⑧ + `pipeline_handoff.md` §company 슬롯 |
| Inference priority | `layout_catalog.md` (기존) + 이 파일 §⑨ |
| Robustness test pattern | 이 파일 §⑩ |
| Builder API | 이 파일 §⑪ |
| 캔버스 13.333×7.5" 표준 | `colors_and_type.css` `.slide--themed` + `prompting_rules.md` §10 |
