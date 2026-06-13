---
name: slides-grab-design
description: Use this skill to generate well-branded interfaces and assets for slides-grab, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping HTML slide decks (PPTX-safe via PF rules) and the slides-grab editor app. v3 integrates the mck-slide-design 4-theme system, 27-layout catalog, FP&A domain invariants, and QA pipeline rules.
user-invocable: true
---

Read these files in order, then build:

1. **`README.md`** — system overview, file index, two surfaces (slides vs editor app)
2. **`theme_layout_matrix.md`** ⭐ — 테마×레이아웃 잠금 매트릭스. **mixing 방지의 핵심**. 슬라이드 만들기 전에 반드시 본다.
3. **`prompting_rules.md`** ⭐ — 에이전트 행동 계약 (액션 타이틀, 명사형 종결, 잠금 타입 스케일, 색 토큰, CJK 규칙)
4. **`layout_catalog.md`** — 46 레이아웃의 LayoutSchema (required/optional/bounds)
5. **`domain/fpna_invariants.md`** — cost_nature, surface_inverse, EA font 등 도메인 불변
6. **`pf_rules.md`** — PPTX 변환 안전 규칙 (PF-XX 룰셋)
7. **`qa_rules.md`** — 9-check + 6-autofix (mck 흡수)
8. **`image_slot_contract.md`** — 이미지 슬롯 마크업 계약 (사내 환경: AI 생성 대신 **수동/사내DB 이미지 배치**용 마크업 규칙으로 사용)
9. ~~`nano_banana_guide.md`~~ — **사내 환경 미사용** (Gemini 이미지 생성 의존). `_archive-company-blocked/` 로 분리됨. 이미지는 차트/표/도형 우선, 사진은 수동 배치.
10. **`pipeline_handoff.md`** — 클라우드 / 로컬 책임 분담, sync 절차
11. **`colors_and_type.css`** — 토큰 (mck 4-테마 + slides-grab 기존 호환)

## 슬라이드 생성 절차 (의무)

`prompting_rules.md` §0 의 7-step 체크리스트 따른다:

1. **테마 결정** (`modern` / `classic` / `dark-mono` / `company` / `executive-editorial` / `dark-pitch` / `academic` / `editorial`) — `<html data-theme="...">`
2. **레이아웃 카탈로그 확인** — `layout_catalog.md` 에서 선택
3. **테마×레이아웃 매트릭스 확인** — `theme_layout_matrix.md` 에서 ✅
4. **schema 준수** — LayoutSchema required / bounds
5. **불변 적용** — `domain/fpna_invariants.md`
6. **PF rules 준수** — `pf_rules.md`
7. **품질 체크** — `qa_rules.md`

## 출력 형태

If creating visual artifacts (slides, mocks, throwaway prototypes), copy assets out and create static HTML files for the user to view. If working on production code, copy assets and read the rules here to become an expert in designing with this brand.

만약 사용자가 다른 가이드 없이 이 스킬을 호출하면, 무엇을 만들지 묻고, 몇 가지 질문을 한 뒤 — 위 11개 파일을 읽은 디자이너로 행동.

## Quick orientation (한 줄 요약)

- 슬라이드 deliverable (PPTX 변환 대상): 720pt × 405pt, `<html data-theme>` 의무, 액션 타이틀 명사형, `--surface-inverse` for 풀블리드, `cost_nature` for FP&A.
- 에디터 앱 (브라우저 only): dark slate, blue accent, M3 elevation, JetBrains Mono. PF 룰 면제.

## Cardinal rules (절대 위반 금지)

- 슬라이드 타이틀은 **명사형 종결 assertion** ("Q3 매출, 전년 대비 +23%"), 토픽 라벨 금지
- 1 슬라이드 = 1 메시지; 최대 3 콘텐츠 블록; ≤120 EN / ≤80 CJK 단어
- 숫자는 시각 자체: hero them at 48pt+, weight 800
- 10pt 는 모든 슬라이드 텍스트의 절대 하한
- `<table>` 금지 — CSS grid 사용
- 솔리드 hex 만 슬라이드에; gradient/shadow 는 에디터 앱에만
- 풀블리드는 `var(--primary)` 가 아닌 **`var(--surface-inverse)`** — `dark-mono` 안전성
- 테마 × 레이아웃 매트릭스 위반 금지 (PF-69)
- LayoutSchema 위반 금지 (PF-72)
- `<html data-theme="...">` + `<section data-layout="...">` 의무 (PF-70 / PF-71)
