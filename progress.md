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
**전체 완료** 2026-06-13. 5커밋 push. 변환 코어 검증(PPTX/PDF/preflight). 사내불가 의존(Gemini/NotebookLM/터널/nodemailer) 전부 제거 또는 archive.
</content>
