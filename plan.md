---
title: 보고서 생성 자산 사내 마이그레이션
tags: [plan, migration, slides-grab, report-pipeline]
date: 2026-06-13
---

# 보고서 생성 자산 사내 Claude Code 마이그레이션

## 목표
사내 Claude Code 에서 보고서를 생성할 때 쓸 자산을 이 프로젝트(`D:\projects\design`)로 통합하고
`github.com/jsh8603-web/design` 에 push 한다.

## 소스 3개
1. `analytical-slide-coauthoring-bundle.md` (루트) — 본문 작성 규칙의 **뼈대**. §13 환각 검증 게이트 핵심.
2. `slides-grab Design System/` (루트 하위) — 우수 디자인 시스템. 이미지 슬롯(nano_banana)만 Gemini 의존.
3. `D:\projects\slides-grab` (원본) — PPT 변환 엔진 + 파이프라인 스텝 + 규칙. NotebookLM/Gemini/OAuth 의존.

## 사내 환경 제약 (확정)
- OAuth 키 불가 → Gemini 이미지 생성·Gemini Vision 전부 불가
- NotebookLM 불가
- 지식 소스 = 사내 DB + WebFetch/WebSearch 직접 + Confluence 용어집
- npm install + Chromium 다운로드는 가능 (PPT 변환 엔진 이식 가능)
- 이미지 슬롯 최소화 (차트/표/도형 위주, 사진은 placeholder)
- 비주얼 에디터 = localhost 서버만 (Cloudflare 터널 제거)

## 파이프라인 3+1
- 공통 코어: 의도 판별 → 00-brief.md → 고스트덱 → §13 검증(internal 사내DB / external Confluence·권위출처 / derived 코드재계산)
- 1. 본문 텍스트 → .md (엑셀 데이터 보고서도 derived 재계산 기준 차용)
- 2. PDF → 디자인 HTML 렌더 → .pdf (회람용)
- 3. PPTX → 디자인 HTML → preflight → pptxgenjs → 9-check QA → .pptx (발표용)
- + 부가: localhost 미리보기/에디터, Marp 초안

## 폴더 구조
```
SKILL.md              # 진입점: 의도 판별 → 파이프라인 라우팅
rules/                # content-authoring · html-prevention · design-modes · verification-gate · research-sourcing
design-system/        # design 폴더 통째 (토큰·8테마·46레이아웃·QA·폰트·mck 차트JS)
pipelines/            # 1-report-text · 2-pdf · 3-pptx
scripts/              # 변환·검증 엔진 (사내불가 의존 떼어낸 버전)
assets/fonts/         # 로컬 .woff2 (CDN 대체)
```

## 제거 대상 (사내 의존)
- 이미지 생성: generate-images.mjs, nano_banana_guide.md, image_slot_contract.md
- NotebookLM: fetch-notebooklm.js, nlm-auto-research.js, NOTEBOOKLM_FETCH.md
- Gemini Vision VQA (opt-in이라 영향 0)
- Cloudflare 터널 (에디터는 localhost만)
- 키/MCP: .env API키, .mcp.json, GEMINI.md, .gemini-*

## 머지(보완)
- 본문 규칙: 루트 md(뼈대) + slides-grab html-prevention/DESIGN_MODES/PRODUCTION_REPORTING 정량규칙 흡수
- 디자인: design 폴더가 우수 → 통째 사용 (mck 차트JS 중복 확인만)
- 폰트: jsDelivr Pretendard → design 폴더 fonts/files/*.woff2 로컬 참조 교체
- 리서치: RESEARCH_SUPPLEMENT 를 WebFetch+사내DB+Confluence 3소스로 재구성
</content>
</invoke>
