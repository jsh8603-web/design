# QA Rules — 9-check + 6-autofix (mck 흡수)

> 이 파일은 PF rules 의 보완. PF rules (`pf_rules.md`) 는 **HTML 단계** PPTX-safe 검증, QA rules (이 파일) 는 **PPTX 변환 직후** post-check + autofix.
>
> 출처: mck `deck_system/qa/checks.py` + `autofix.py` + `experiences.py`.
>
> 로컬 slides-grab 의 `vqa-batch.mjs` / `validate-pptx.js` 와 같은 의도. 둘은 점진적 통합 대상.

---

## 0. 적용 시점

```
[1] HTML 작성              ← prompting_rules.md (에이전트)
        ↓
[2] HTML preflight         ← pf_rules.md  (preflight-html.js)
        ↓
[3] PPTX 변환              ← html2pptx.cjs (Playwright + PptxGenJS)
        ↓
[4] QA 9-check + autofix   ← 이 파일 (mck/deck_system/qa/)
        ↓
[5] Vision validation      ← vqa-batch.mjs (LLM PNG 비교)
```

이 파일은 **[4] 단계 게이트.** 통과 못 하면 PPTX 폐기 후 재생성.

---

## 1. 9 Per-Slide Checks

mck `qa/checks.py` 에서 흡수. 각 체크 함수가 슬라이드별로 `QAFinding` 을 발행.

| Check | Level | Category | 무엇을 잡나 |
|-------|-------|----------|------------|
| `_check_action_title` | warning | title_overflow | 액션 타이틀 > 40자, `_BAD_ENDINGS` 매칭 |
| `_check_body_overflow` | **error** | geometry | body 영역이 content_top..source_y 범위 초과 |
| `_check_text_overflow` | warning | geometry | shape 내 텍스트가 shape 영역 초과 (scrollHeight > clientHeight) |
| `_check_whitespace` | error/warning | empty_slide | 슬라이드 콘텐츠 영역이 80% 이상 빈 영역 |
| `_check_shape_overlap` | info | geometry | 두 shape 의 bounding box 겹침 (단, `surface-inverse` capsule 위 콘텐츠는 면제) |
| `_check_fonts` | **error** | cjk | 한국어 run 에 EA font 미설정 |
| `_check_peer_font_consistency` | info | peer_font_inconsistency ⚠️ whitelisted | legend vs axis font size 차이 ≤ 0.5pt (엔진 quirk) |
| `_check_chart_legend_overflow` | info | chart_legend_pixel_drift ⚠️ whitelisted | python-pptx 가 legend bbox 를 nearest pt 로 반올림 |
| `_check_connectors` | **error** | file_corruption | `add_connector()` 사용 — PPTX 파일 손상 위험 |

추가 1개 (글로벌, 슬라이드 무관):

| `_check_global_two_column_text` | warning | layout_overuse | `two_column_text` 가 덱당 > 1 개 |

### 1.1 화이트리스트 (engine bugs, NOT user bugs)

```python
ENGINE_BUG_WHITELIST = [
    "peer_font_inconsistency",   # legend vs axis font 0.5pt 차이
    "chart_legend_pixel_drift",  # legend bbox pt 반올림
    "block_arc_label_anchor",    # BLOCK_ARC center label 0.02" off
]
```

이 카테고리들은 자동으로 `info` 레벨로 demote → 게이트가 fail 하지 않음.

### 1.2 `_check_whitespace` ↔ HTML `data-rendered` 등가성

```python
def _check_whitespace(slide, idx, spec=None):
    """슬라이드 dead-zone 검출.

    HTML 시스템의 data-rendered guard 와 등가:
    - HTML: 렌더 안 된 슬라이드 → JS 사전 차단
    - PPTX: 렌더 안 된 슬라이드 → QA 사후 검출
    둘 다 '슬라이드에 빈 콘텐츠 영역 금지' 를 인코딩한다.
    """
```

→ HTML 단계의 `safeRender()` 가드 와 PPTX 단계의 whitespace 체크가 **같은 의도**를 양 끝에서 인코딩.

---

## 2. 8 Autofix Repair Rules

mck `qa/autofix.py` 에서 흡수. **레이아웃 선택은 절대 안 바꾼다** (사용자 결정). 텍스트 수준 수리만.

| Rule | What it does | 임계값 |
|------|-------------|-------|
| `_fix_action_title` | `"…"` 로 truncate | > `MAX_ACTION_TITLE_CHARS` (40) |
| `_fix_donut_segments` | 꼬리 segments 를 "기타" 로 머지 | > `MAX_DONUT_SEGMENTS` (6) |
| `_fix_chevron_steps` | 초과 step 제거 + 라벨에서 `\n` 제거 | > `MAX_PROCESS_CHEVRON_STEPS` (5) |
| `_fix_kpi_tiles` | 초과 KPI tile 제거 | > `MAX_KPI_TILES` (8) |
| `_fix_big_number_details` | 초과 detail item 제거 | > `MAX_BIG_NUMBER_DETAIL_ITEMS` (4) |
| `_fix_four_column_desc` | description truncate | > `MAX_FOUR_COL_DESC_CHARS` (120) |
| **`_fix_pareto_overflow`** ⭐ | top-(N-1) + "기타" 머지 | > `MAX_PARETO_BARS` (10) |
| **`_fix_grouped_bar_series`** ⭐ | series cap + dropped 라벨 로깅 | > `MAX_GROUPED_BAR_SERIES` (3) |

⭐ 이전 박제에서 누락 — v3.1 에 추가.

각 rule 은 `AutofixAction(slide_idx, rule, before, after)` 를 발행해 누적 → reviewer 가 어떤 자동 수정이 일어났는지 확인.

각 rule 의 정확한 동작 + 코드 참조: `code_inventory.md` §⑦.

---

## 3. 4-Stage Autofix Pipeline

```
[A] Page brief        — 각 슬라이드 spec 요약 (type, title 길이, 키)
[B] Dual QA           — qa_runner 가 있으면 1회 실행 (선택)
[C] Auto-fix          — repair rule 들이 spec dict 를 in-place 수정
[D] Gate              — QA 재실행. passed=true 될 때까지 max_rounds (default 3) 반복
```

### 3.1 호출 방법

```python
# mck CLI
fpna-deck --spec deck.json -o out.pptx --auto-fix --max-rounds 3

# Builder API
b = PresentationBuilder()
b.add_specs(specs)
result = b.run_autofix(max_rounds=3)
for action in result.actions:
    print(f"  [{action.slide_idx}] {action.rule}: {action.before} → {action.after}")
b.save("out.pptx", auto_fix=True)
```

### 3.2 slides-grab 등가물

slides-grab 에서는 별도 autofix 단계가 없고, preflight-html.js 가 ERROR → 빌드 중단 → 에이전트가 수동 수정. 통합 시 두 접근의 절충:

- **로컬 (slides-grab)**: preflight-html.js 가 PF-XX ERROR 검출 → autofix 시도 가능 한 룰은 자동 수리 후 재검 → 통과 시 빌드, 불통 시 정지
- **이 프로젝트 (클라우드)**: 에이전트가 HTML 작성 단계에서 prompting_rules + LayoutSchema 준수해 사전 방지. autofix 가 backup safety net.

---

## 4. QA Report 포맷

```json
{
  "passed": false,
  "errors": [
    { "slide_idx": 4, "category": "geometry",
      "check": "_check_body_overflow",
      "message": "body extends below source_y by 12pt",
      "fix": "split into 2 slides or trim 2 bullets" }
  ],
  "warnings": [...],
  "infos": [...]
}
```

`.to_dict()` 호출 시 JSON 직렬화. `--qa-report out_qa.json` 로 파일 저장.

---

## 5. 슬라이드그랩 PF rules 와의 매핑

이 QA 체크들은 slides-grab 의 PF-XX 룰과 **다른 단계 같은 의도**:

| QA check | slides-grab PF |
|----------|---------------|
| `_check_body_overflow` | PF-26 (3 block max), PF-66 (overflow:hidden 콘텐츠 초과) |
| `_check_text_overflow` | PF-65 (Grid cell scrollWidth > clientWidth), PF-66 (text-clipped) |
| `_check_fonts` | (전용 PF 없음 — EA font 박제만 있음) |
| `_check_action_title` | PF-25 (10pt floor) — 직접 매핑 없음. 명사형 종결은 PF 룰에 없었음 (이번에 박제) |
| `_check_shape_overlap` | PF-41 (장식 요소 간격 20pt) |
| `_check_whitespace` | (slides-grab 에는 동일 항목 없음 — 흡수 가치 있음) |
| `_check_chart_legend_overflow` | (없음 — whitelist 박제 필요) |
| `_check_connectors` | (없음 — slides-grab 은 connector 사용 빈도 낮음) |

**박제 우선순위:**
1. `_check_whitespace` → preflight-html.js 에 추가 (PF-74 신규)
2. `_check_action_title` 명사형 검증 → preflight-html.js 에 추가 (PF-75 신규)
3. ENGINE_BUG_WHITELIST → slides-grab `pptx-inspection-log.md` 에 카테고리 추가

---

## 6. 실패 모드 발견 시 절차 (Auto-Improvement Loop)

```
[1] 실패 검출
    ├─ PF preflight WARN/ERROR
    ├─ QA check 실패
    ├─ Vision Validation 차이
    └─ 사용자 reviewer 가 손가락질

[2] 분류 (mck 의 3-class taxonomy)
    ├─ FP (False Positive)        — 검출 자체가 틀림. 검사 룰 완화 또는 whitelist.
    ├─ TP-fixable (정탐, 수정 가능) — 사용자 데이터 문제. autofix 룰 추가 가능.
    └─ TP-limitation (정탐, 한계) — 엔진 quirk. ENGINE_BUG_WHITELIST 추가.

[3] 박제 위치 결정
    ├─ FP   → `qa/checks.py` 의 해당 함수 수정 + whitelist
    ├─ TP-F → `qa/autofix.py` 의 repair rule 추가 + `experiences.py` 상수
    └─ TP-L → `experiences.ENGINE_BUG_WHITELIST` 추가 + 코멘트로 이유 명시

[4] 동기화
    ├─ mck `experiences.py` 갱신
    ├─ slides-grab `pf_rules.md` 갱신 (등가 PF-XX 룰 추가)
    ├─ 이 파일에 매핑 행 추가
    └─ slides-grab `pptx-inspection-log.md` 에 한 줄 기록 (51KB 누적)

[5] 회귀 테스트
    ├─ mck `tests/test_qa.py` 에 fixture 추가
    └─ slides-grab `tests/run-full-regression.mjs` 에 fixture 추가
```

이 절차가 곧 **자가학습 루프**. 인라인 매직 넘버 / 일회성 audit / 메모리 안에 두지 말고 **양쪽 시스템 파일에 박제**한다.

---

## 7. 새 체크 추가 절차

1. `mck/deck_system/qa/checks.py` 에 함수 추가 (`_check_<name>`)
2. `experiences.py` 에 상수 추가 (임계값)
3. autofix 가 가능하다면 `qa/autofix.py` 에 rule 추가
4. 이 파일 §1 / §2 에 행 추가
5. slides-grab 등가 PF-XX 룰 작성 (`pf_rules.md`)
6. `tests/test_qa.py` 에 케이스 추가 (pass + fail 둘 다)

원칙: **체크 1개 = 임계값 1개 = autofix 1개 (가능 시) = 테스트 1개**. 인라인 매직 금지.
