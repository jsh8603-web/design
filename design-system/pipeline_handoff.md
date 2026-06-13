# Pipeline Handoff — 클라우드 ↔ 로컬 책임 분담

> 이 문서는 **두 환경 사이의 계약**이다. 어느 파일이 어디서 권위 있고, 어느 환경이 어떤 일을 하며, 어떻게 동기화하는지를 정의한다.
>
> 원칙: **클라우드 = 디자인 시스템 SoT (Source of Truth). 로컬 = 런타임.**

---

## 0. 두 환경 요약

### A. 클라우드 (이 프로젝트 — slides-grab Design System)

| | |
|---|---|
| **역할** | 디자인 시스템의 권위 있는 출처. 규칙·토큰·레이아웃·프롬프팅 룰 보관 + reference HTML 생성 |
| **읽기** | LLM (Claude) 이 슬라이드 생성 시 이 파일들을 읽고 따른다 |
| **쓰기** | 사용자 또는 LLM이 새 규칙/실패 모드를 박제 |
| **실행 가능** | HTML 프리뷰, JS eval, 스크린샷, `gen_pptx` (Playwright + PptxGenJS, sanity-check 수준) |
| **실행 불가** | bash/shell, Node 스크립트, Python, 장시간 서버 |

### B. 로컬 (사용자 머신 — `slides-grab/` 리포)

| | |
|---|---|
| **역할** | 런타임 + 자가학습 파이프라인 |
| **읽기** | preflight·QA·VQA가 클라우드 룰 사본을 읽음 |
| **쓰기** | 실패 모드 발견 시 audit/ + pptx-inspection-log.md 누적 |
| **실행 가능** | Playwright, html2pptx.cjs, Python deck_system, vqa-batch.mjs, editor-server.js, Cloudflare 터널 |

---

## 1. 파일 권위 (Source of Truth) 매트릭스

| 파일 / 자산 | 권위 위치 | 사본 위치 | Sync 방향 |
|------------|---------|---------|---------|
| `theme_layout_matrix.md` | **클라우드** | local: `.claude/docs/` (read-only 사본) | 클라우드 → 로컬 |
| `layout_catalog.md` | **클라우드** | local: `.claude/docs/` | 클라우드 → 로컬 |
| `prompting_rules.md` | **클라우드** | local: `.claude/docs/` | 클라우드 → 로컬 |
| `domain/fpna_invariants.md` | **클라우드** | local: `.claude/docs/` | 클라우드 → 로컬 |
| `qa_rules.md` | **클라우드** | local: `.claude/docs/` | 클라우드 → 로컬 |
| `colors_and_type.css` | **클라우드** | local: `slides-grab/styles/` | 클라우드 → 로컬 |
| `image_slot_contract.md` | **클라우드** | local: `.claude/docs/` | 클라우드 → 로컬 |
| `pf_rules.md` (현재) | **양쪽 권위** (다른 측면) | sync 필요 | **양방향** |
| `pptx-inspection-log.md` (51KB 누적 이슈) | **로컬** | (cloud 미러 없음 — 너무 큼) | 로컬 only |
| `scripts/preflight-html.js` | **로컬** | (cloud 사본은 reference) | 로컬 → 클라우드 (참조용) |
| `scripts/html2pptx.cjs` | **로컬** | (cloud 사본은 reference) | 로컬 → 클라우드 (참조용) |
| `scripts/vqa-batch.mjs` | **로컬** | (cloud 미러 없음) | 로컬 only |
| `mck/deck_system/` (Python pptx) | **로컬** | cloud: `pptx/` (reference) | 로컬 → 클라우드 (참조용) |
| `experiences.py` (19 상수) | **양쪽 권위** | sync 필요 | **양방향** |
| 슬라이드 HTML (`slides/*.html`) | **deck-by-deck** | 어느 쪽에서 시작했냐에 따라 | 케이스별 |
| 생성된 이미지 (`assets/*.png`) | **로컬** | (cloud 는 placeholder) | 로컬 only |
| 변환된 PPTX (`*.pptx`) | **로컬** | (cloud 미러 없음) | 로컬 only |

---

## 2. 환경별 단계 책임

```
┌─────────────────────────────────────────────────────────────────────┐
│ 단계 │ 환경     │ 도구                          │ 산출물            │
├─────────────────────────────────────────────────────────────────────┤
│ [1]  │ 클라우드 │ LLM + 룰 파일들              │ HTML 슬라이드     │
│      │ Outline & 슬라이드 HTML 생성             │ + image-slot 마커 │
├─────────────────────────────────────────────────────────────────────┤
│ [2a] │ 클라우드 │ preview iframe + 시각 검토   │ 사용자 승인       │
│      │ 디자인 리뷰 (사람 + image-slot drag)     │ + image 슬롯 입력 │
├─────────────────────────────────────────────────────────────────────┤
│ [2b] │ 클라우드 │ gen_pptx 툴 (sanity)         │ 미리보기 PPTX     │
│      │ (선택) 변환 미리보기                     │ (final 아님)      │
├─────────────────────────────────────────────────────────────────────┤
│ [3]  │ 로컬     │ generate-images.mjs (Gemini) │ assets/*.png      │
│      │ NanoBanana 이미지 생성                   │ + HTML 패치       │
├─────────────────────────────────────────────────────────────────────┤
│ [4]  │ 로컬     │ preflight-html.js (PF rules) │ PF report         │
│      │ HTML preflight                           │ 통과/실패         │
├─────────────────────────────────────────────────────────────────────┤
│ [5]  │ 로컬     │ html2pptx.cjs (Playwright)   │ deck.pptx (final) │
│      │ HTML → PPTX 변환                         │                   │
├─────────────────────────────────────────────────────────────────────┤
│ [6]  │ 로컬     │ QA 9-check + autofix         │ QA report         │
│      │ post-convert 검증                        │ + autofix 액션    │
├─────────────────────────────────────────────────────────────────────┤
│ [7]  │ 로컬     │ vqa-batch.mjs (LLM)          │ Vision report     │
│      │ Vision Validation                        │                   │
├─────────────────────────────────────────────────────────────────────┤
│ [8]  │ 로컬     │ audit/ + pptx-inspection-log │ 누적 학습          │
│      │ 새 실패 모드 박제                         │                   │
├─────────────────────────────────────────────────────────────────────┤
│ [9]  │ 클라우드 │ 룰 파일들 갱신               │ 다음 [1] 더 좋음  │
│      │ Sync back: 박제된 룰을 룰 파일로         │                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Sync 절차

### 3.1 클라우드 → 로컬 (룰 사본 갱신)

```bash
cd ~/slides-grab/

# git submodule 사용 (권장)
git submodule update --remote .claude/docs/design-system

# 또는 수동 sync (이 프로젝트를 zip 으로 다운받아 .claude/docs/ 에 풀기)
# (Claude Design tab → Files → "Download project" → 압축 해제)
```

이렇게 받은 룰 사본을 로컬 `preflight-html.js` 가 reference 함:

```js
// scripts/preflight-html.js
const themeMatrix = require('../.claude/docs/design-system/theme_layout_matrix.md');
// → parse markdown → enforce
```

### 3.2 로컬 → 클라우드 (새 룰 박제)

로컬에서 새 실패 모드 발견 시:

1. `pptx-inspection-log.md` 에 한 줄 기록 (로컬 only)
2. `experiences.py` 상수 추가 (양방향 SSOT 파일)
3. `qa/checks.py` 또는 `autofix.py` 함수 추가
4. **클라우드로 박제**: 이 프로젝트에 와서 `qa_rules.md` / `prompting_rules.md` / `theme_layout_matrix.md` 갱신
5. 다음 sync 때 양쪽 일치

### 3.3 sync 주기

| 빈도 | 액션 |
|------|------|
| **즉시** | 새 PF-XX ERROR 룰 추가, theme×layout 매트릭스 변경 |
| **주간** | experiences 상수 추가, autofix rule 추가 |
| **월간** | 전체 sync 점검, audit/ → audit-archive/ |

---

## 4. 두 환경에서 같은 일을 하는 것 (gen_pptx vs html2pptx.cjs)

이 점이 가장 헷갈리는 부분이다. **둘 다 HTML → PPTX 변환을 한다.** 차이:

| | gen_pptx (클라우드) | html2pptx.cjs (로컬) |
|---|---|---|
| 위치 | 이 환경의 백엔드 툴 | 로컬 `scripts/` |
| 백엔드 | Playwright (서버 측) | Playwright (사용자 측) |
| 출력 모드 | editable / screenshots | editable / screenshots |
| 통합 검증 | 자동 — duplicate_adjacent, slide_size_mismatch 플래그 | preflight + QA + VQA 별도 단계 |
| 자가학습 누적 | ❌ (이슈 메모만, 박제는 수동) | ✅ pptx-inspection-log.md 51KB |
| 용도 | **sanity check** — 디자인 리뷰 단계에서 1회 확인 | **final** — 실제 deliverable |

**권장 사용:**
- 클라우드 [2b]: gen_pptx 로 "변환했을 때 깨지는 것 없는지" 빠른 확인
- 로컬 [5]: html2pptx.cjs 로 최종 deliverable 생성 + QA + VQA

만약 둘이 다른 결과를 내면 → 로컬 결과를 정답으로 보고, gen_pptx 의 차이를 audit/ 에 기록.

---

## 5. mck/deck_system Python 엔진의 위치

mck 의 70 레이아웃 PPTX 엔진 (`mck/deck_system/`) 은:

| | |
|---|---|
| **권위 위치** | 로컬 (실행 가능) |
| **클라우드 사본** | `pptx/` 디렉토리 (read-only reference, 실행 불가) |
| **역할** | JSON spec → 직접 PPTX 생성 (HTML 우회) |
| **언제 사용** | 데이터-드리븐, 자주 갱신되는 분기 보고. HTML 단계 생략 |
| **언제 비사용** | 1회성 임원 보고, 디자인이 콘텐츠보다 중요한 경우 → HTML 경유 |

**두 경로:**
```
[HTML 경로]  outline → 이 프로젝트 LLM → HTML → html2pptx.cjs → PPTX
              ↑ 디자인 자유도 높음
[JSON 경로]  spec.json → mck/deck_system Python → PPTX (직접)
              ↑ 데이터 드리븐, 자동화 친화
```

**같은 LayoutSchema 를 공유** — `layout_catalog.md` 의 schema 정의는 두 경로 모두에서 강제.

---

## 6. 자산 디렉토리 매핑

```
[클라우드]                                  [로컬 slides-grab]
─────────────────                          ─────────────────────────
/  (이 프로젝트 root)                       slides-grab/  (로컬 리포)
├── theme_layout_matrix.md       ───→      .claude/docs/design-system/
├── layout_catalog.md             ───→      .claude/docs/design-system/
├── prompting_rules.md            ───→      .claude/docs/design-system/
├── domain/fpna_invariants.md     ───→      .claude/docs/design-system/
├── qa_rules.md                   ───→      .claude/docs/design-system/
├── image_slot_contract.md        ───→      .claude/docs/design-system/
├── pf_rules.md                   ◄══►      html-prevention-rules.md  (양방향)
├── colors_and_type.css           ───→      slides/<deck>/colors_and_type.css
├── nano_banana_guide.md          ◄══►      nanoBanana-guide.md  (양방향)
├── slides/*.html  (reference)    ───→      slides/<deck>/  (deck 사본)
├── pptx/  (Python 사본, 미실행)   ◄───      mck/deck_system/  (실행 가능 권위)
└── preview/*.html  (DS 카드)               (없음)

                                            scripts/
                                            ├── preflight-html.js   (PF 실행)
                                            ├── html2pptx.cjs       (변환 실행)
                                            ├── vqa-batch.mjs       (Vision 검증)
                                            ├── generate-images.mjs (이미지 생성)
                                            ├── checklist-guard.mjs (코드 게이트)
                                            └── editor-server.js    (편집기)

                                            audit/           (실패 모드 누적)
                                            pptx-inspection-log.md  (51KB)
```

---

## 7. 충돌 해결

두 환경의 룰이 서로 다르면:

1. **`theme_layout_matrix.md` / `layout_catalog.md` 충돌** → 클라우드 우선. 로컬 사본 갱신.
2. **`pf_rules.md` vs `html-prevention-rules.md` 충돌** → 로컬 우선 (실제 변환에서 발견된 룰이라). 클라우드에 박제.
3. **`experiences.py` 충돌** → mck 의 권위 우선 — 같은 코드가 양쪽에서 호출되어야 하므로 단일 출처 유지.
4. **렌더 결과 차이** → 로컬 결과를 정답. gen_pptx 차이는 audit 기록.

원칙: **권위가 명확한 쪽이 이긴다.** 어느 쪽이 권위인지 §1 표에서 확인.

---

## 8. 어느 작업을 어느 환경에서 하나 (Quick Decision)

| 작업 | 환경 |
|------|-----|
| 새 슬라이드 디자인 (LLM) | 클라우드 |
| 디자인 리뷰 + 코멘트 | 클라우드 |
| 변환 sanity check | 클라우드 (gen_pptx) |
| 최종 PPTX 빌드 | 로컬 (html2pptx.cjs) |
| 이미지 생성 (Gemini) | 로컬 (generate-images.mjs) |
| 룰 박제 / 갱신 | 클라우드 (먼저), 로컬 sync |
| 실패 모드 발견 | 로컬 (자동 검출) |
| 실패 모드 박제 | 클라우드 룰 파일에 |
| 누적 이슈 로그 | 로컬 `pptx-inspection-log.md` |
| 회귀 테스트 | 로컬 (`tests/run-full-regression.mjs`) |
| 사내 PPTX 마스터 어댑터 | 로컬 (`mck/adapter/profile.py`) |
| design system 검토 (이해관계자) | 클라우드 (이 프로젝트의 Design System 탭) |

---

## 9. 단순화 — 한 줄 mental model

> **클라우드는 룰북이다. 로컬은 공장이다. 룰북이 바뀌면 공장이 따른다. 공장에서 새 실패를 발견하면 룰북이 갱신된다.**
