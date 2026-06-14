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

---

# 규칙 감사 후속 (rule-audit) — 2026-06-14

> 출처: 사용자 전달 핸드오프 "규칙 감사 후속 (불만 제기 이후 누적분)". 전달완료 base(VP-16 0.92·PF-25·PF-28·PF-18, 커밋 0de6ba7~73c8a4c) 위에 **11규칙 후속 패치**를 적용한다.
> 사용자 지시: "이전과 같은 방법으로 검증하며 적용" = 직접검증→A/B(수정전 사본 vs 수정후)→FP/FN 전수 렌더→추가수정→커밋. diff 무비판 코드화 금지.

## 핵심 설계 결정 (적용 전 확정)
1. **diff 통째 `git apply` 금지** — 규칙 그룹별로 적용하고 각 그룹 직후 실 PPTX before/after 실증. (consult-adoption-gate: 적용 전 falsify)
2. **VP-09 계수 충돌 해소** — 핸드오프 diff 는 `CJK×1.0`(작성 시점 VP-16=1.0 기준)이나 우리 VP-16(validate-pptx.js:1149)은 이미 `0.92`로 재보정됨. → VP-09 도 **0.92 로 맞춰 적용**(핸드오프의 "VP-16과 일관" 의도를 현행값으로 재해석). 라틴 0.5·공백 0.25·행높이 1.3 은 diff 그대로.
3. **검증 환경 대체** — 핸드오프의 `pw-shim.mjs` 없음 → 직전 검증과 동일하게 `convert-native --skip-preflight`로 실 PPTX 생성. 수정전 = `git stash`/사본, 수정후 = 현재.
4. **픽스처 신규 제작** — VP-04(어두운 이미지 위 흰 글자 + 흰-on-흰 대조군)·VP-10(KPI 3행: 균등/겹침/불일치) 전용 슬라이드 신규. 기존 mock-dense(slide-1~6) 는 px·CJK 룰 재활용.

## 11규칙 그룹 (전부 validate-pptx.js 2 + preflight-html.js 9, 2파일)
| 그룹 | 규칙 | 종류 | 검증 방식 |
|---|---|---|---|
| A (validate-pptx) | VP-04 contrast / VP-10 gap / VP-09 shrink | 검출 계약 변경 | 실 PPTX before/after + FP/FN 렌더 |
| B (preflight 렌더) | PF-23 realOverflow / PF-65 Range측정 / PF-66 ellipsis제외 | FP 제거(--full 실렌더) | --full DOM 측정 before/after |
| C (preflight 정적) | PF-15·30·41·45 px→pt / PF-34 blockSpans | px FN·FP(결정형) | 픽스처 발화 전수 분류 |

## FP/FN 회귀 규율 (직전 K-202606140510 준수)
- 각 규칙: 수정으로 **제거된 발화(OLD→NEW 소멸)** 전수를 렌더 대조 → 실제 안 넘침/안 겹침이면 FP 제거 정당, 넘침/겹침이면 FN(과제거).
- **will-overflow 뿐 아니라 may-wrap→pass 격하분도 전수**(직전 누락 교훈).
- 의도 룰(VP-02/03/07/08/11·PF-20 등 코퍼스전용)은 이번 범위 밖 — 카운트 불변(회귀 안전) 확인만.
