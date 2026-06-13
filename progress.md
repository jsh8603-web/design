---
title: 마이그레이션 진행 상황
tags: [progress, migration]
date: 2026-06-13
---

# progress — 보고서 생성 자산 마이그레이션

> plan.md 참조. 각 step = model 직접 지정.

## Phase 0 — 골격
- [x] 0.1 git init + .gitignore (node_modules, .env 등) `model: sonnet`
- [x] 0.2 폴더 골격 생성 (rules/ design-system/ pipelines/ scripts/ assets/) `model: sonnet`

## Phase 1 — 디자인 시스템 이식
- [x] 1.1 "slides-grab Design System/" → design-system/ 이동, nano_banana 만 archive 분리(image_slot 은 수동배치용 잔류) `model: sonnet`
- [x] 1.2 폰트 CDN 제거 → 로컬 .woff2 (colors_and_type.css + HTML 32개 link 제거) `model: sonnet`
  - 회귀 확인: fonts.css 가 3패밀리 local()+url(files/) 완비 → CDN 제거해도 오프라인 렌더 정상 (수동 확인)
- [ ] 1.3 mck 차트JS 중복/유효성 확인 `model: sonnet`

## Phase 2 — 변환 엔진 이식
- [ ] 2.1 원본 slides-grab scripts/ 중 변환·검증 코어만 선별 복사 `model: sonnet`
- [ ] 2.2 사내불가 의존 떼어내기 (Gemini/NotebookLM/터널 호출부 제거) `model: opus`
- [ ] 2.3 package.json 정리 (불필요 deps 제거) `model: sonnet`

## Phase 3 — 규칙 머지
- [ ] 3.1 rules/content-authoring.md = 루트 md 뼈대 + slides-grab 정량규칙 흡수 `model: opus`
- [ ] 3.2 rules/html-prevention.md (PF/IL 정량 제약) `model: sonnet`
- [ ] 3.3 rules/design-modes.md `model: sonnet`
- [ ] 3.4 rules/verification-gate.md (§13 internal/external/derived) `model: opus`
- [ ] 3.5 rules/research-sourcing.md (WebFetch+사내DB+Confluence 3소스) `model: opus`

## Phase 4 — 파이프라인 + 진입점
- [ ] 4.1 SKILL.md 라우터 (의도 판별 → 1/2/3 분기) `model: opus`
- [ ] 4.2 pipelines/1-report-text/ (본문, 엑셀 derived 기준 포함) `model: opus`
- [ ] 4.3 pipelines/2-pdf/ `model: sonnet`
- [ ] 4.4 pipelines/3-pptx/ (스텝 문서) `model: sonnet`

## Phase 5 — 실동작 테스트
- [ ] 5.1 npm install + Chromium, 샘플 HTML→PPTX e2e `model: sonnet`
- [ ] 5.2 회귀 확인 (preflight/QA 동작) `model: sonnet`

## Phase 6 — 마무리
- [ ] 6.1 README.md 작성 `model: sonnet`
- [ ] 6.2 git commit + repo push `model: sonnet`
</content>
