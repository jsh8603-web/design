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
- [x] 2.1 코어 선별 복사 (convert-native/preflight/validate-slides/validate-pptx/html2pptx(+local)/html2pdf/auto-checklist/editor-server/build-viewer/draft-marp + html2pptx.cjs + src/ + bin/ppt-agent + convert.cjs) `model: sonnet`
- [x] 2.2 사내불가 의존 제거: html2pptx.cjs import경로 수정 / validate-pptx-com(Gemini Vision)→archive(existsSync 가드로 자동 skip) / editor-server Cloudflare 터널 전체 제거. NotebookLM/nodemailer 는 애초 미복사 `model: opus`
  - 회귀 확인: 전 11파일 node --check 통과 + 잔존 외부의존(GEMINI/터널/notebooklm/nodemailer/.claude경로) grep 0건
- [x] 2.3 package.json (commander/express/jszip/pdf-lib/playwright/pptxgenjs/sharp + marp dev. nodemailer/react-icons/xml2js 제외) `model: sonnet`

## Phase 3 — 규칙 머지
- [x] 3.1 rules/content-authoring.md = 루트 md 뼈대 이동 + §17 사내환경/엑셀 데이터 보고서 보완 추가 `model: opus`
- [x] 3.2~3.4 ~~html-prevention/design-modes/verification-gate 별도 생성~~ → **design-system/ + content-authoring §13 이 SSOT (중복 제거, 설계 조정)** `model: opus`
- [x] 3.5 rules/research-sourcing.md (사내DB+WebFetch+Confluence 3소스, Source 태그, 보강 트리거) `model: opus`

## Phase 4 — 파이프라인 + 진입점
- [x] 4.1 SKILL.md 라우터 (의도 판별 → 1/2/3 분기 + 공통 코어 + 규칙 SSOT 맵) `model: opus`
- [x] 4.2 pipelines/1-report-text/README.md (본문, 엑셀 derived 기준 포함) `model: opus`
- [x] 4.3 pipelines/2-pdf/README.md `model: sonnet`
- [x] 4.4 pipelines/3-pptx/README.md (사내용 스텝, Gemini 단계 제거 명시) `model: sonnet`

## Phase 5 — 실동작 테스트
- [x] 5.1 npm install (47pkg, 0 vuln) + chromium 확인, 샘플 HTML→PPTX e2e: slide1.xml 생성·텍스트/도형 변환 OK / HTML→PDF v1.7 생성 OK `model: sonnet`
  - 회귀 확인: 규격 정합 검증 — design-system deliverable=720pt×405pt(960×540px)=엔진 SLIDE_W/H 10×5.625" 일치. body 크기 명시 시 변환 통과. mck/slides 1280px 는 데모 참고용(변환대상 아님)
- [x] 5.2 preflight 단독 통과, VP XML 검증 동작(테스트 HTML 한계로 VP-04 false positive, 엔진 무결) `model: sonnet`

## Phase 6 — 마무리
- [x] 6.1 README.md 작성 `model: sonnet`
- [x] 6.2 git commit + repo push (main → github.com/jsh8603-web/design) `model: sonnet`

---
**1차 완료** 2026-06-13. 5커밋 push. 변환 코어 검증(PPTX/PDF/preflight).

## 보완 (2차 — 처음요청 누락 점검 후) `model: opus`
사용자 지적: 디자인/규칙=제공분 우선·우수점만 머지 / 나머지=의존성 제거하고 누락 0.
1차에서 변환 코어 코드만 가져오고 운영 자산을 대거 누락한 것 교정.
- [x] B1 규칙 문서 이식 → docs/conversion-rules/ (html-prevention-rules, HTML_RULE_EXAMPLES, pptx-inspection-log, TESTING_RULES, VQA_PIPELINE_MAINTENANCE, PRODUCTION_REPORTING_RULES)
- [x] B2 파이프라인 스텝 → docs/pipeline-steps/ (PF_STEP_0_1~5_6_7, PRESENTATION_FLOW)
- [x] B3 디자인/리서치 레퍼런스 → docs/design-reference/ (DESIGN_MODES, RESEARCH_SUPPLEMENT)
- [x] B4 에이전트 스킬 → skills/ (ppt-plan/design/pptx/presentation + **pptx-skill 변환엔진 통째**: html2pptx.cjs/.js, thumbnail.py, ooxml 도구, SKILL/html2pptx/ooxml.md)
- [x] B5 운영규약 → docs/ (AGENTS.md, slides-grab-CLAUDE.md), docs/slides-grab-docs/ (installation, prompts, plans, README-KO)
- [x] B6 유효 스크립트 → scripts/ (가드 3종, screenshot-html, install-codex-skills, export-png, convert-native.cjs/local.mjs) + tests/ (vision-ground-truth 제외)
- [x] B7 의존성 제거: convert-native.mjs/.cjs require 경로 → ../skills/pptx-skill/ 복원 / 회사의존 문서 12종 사내 배너 / 가드 사내적용 노트(docs/slides-grab-guards-note.md)
  - 회귀 확인: convert e2e 재검증(slide xml 생성·Saved) + 실행경로(scripts/src/bin/skills/convert.cjs) 회사의존 grep 0건
- [x] B8 제외 결정(보고): 회사의존(NLM/Gemini이미지/Vision/email 스크립트, GEMINI/NOTEBOOKLM md)→archive / 일회성 디버그(fix-slides-*, gen-slides-* 구버전)·중복 / 디자인열위(templates/themes — design-system 우월)·CI(.github)·데모미디어(demo.gif 5.4MB)
</content>

## Working Notes
> [ckpt-202606131410:btn-design]
- 마지막 결정: excel `metric_table.py` 생성(사용자 제공 코드 그대로, /d/projects/excel/fpna/templates/). design 개선 9건 = LICENSE만 생성, 나머지 8건 미적용.
- 다음 의도: (1) excel `fpna/templates/__init__.py` _MODULES 에 metric_table 등록 + `py main.py selftest` 검증 (2) design 9건 = `handoff-improvements-20260613.md` 대로 §A embed-fonts/gen-report/test-fonts/CI-yml + §B convert-native 가드·package.json vr:test·thresholds.json·.aiignore 적용.
- 동기화 필요: design push 완료(ad3ff36). LICENSE·handoff md·excel metric_table = 미커밋. HANDOFF 9건 전문 = 사용자 2026-06-13 14:07 메시지(다음 세션 재요청).
