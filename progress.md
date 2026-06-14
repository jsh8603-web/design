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
- [x] 1.3 mck 차트JS 중복/유효성 확인 `model: opus`
  - 점검(읽기만, 코드변경 0): assets 차트 17종 전부 동적 import 유효(FAIL 0) / demo HTML = ES module 직접 참조(중복 정의 없음) / `_ds_bundle.js`는 레포 미참조 죽은 산물(신규 12종 미반영 stale이나 무해). 회귀=코드 무변경 직교

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

---

# Phase R — 규칙 감사 후속 (11규칙 후속 패치) `2026-06-14`
> plan.md `# 규칙 감사 후속` 참조. 검증 = 직접검증→A/B→FP/FN 전수→추가수정→커밋 (사용자 표준 1세트). 전부 `model: opus` (매 step FP/FN 판정이 핵심 = 거짓검증 금지 품질 요구).

- [x] R0 검증 환경 셋업 `model: opus`
  - 픽스처 신규: `slides/rule-audit/slide-1`(VP-04 어두운 img 위 흰글자+출처), `slide-2`(흰on흰 invisible), `slide-3`(VP-10 KPI 3행 균등/겹침/불일치), `slide-4`(VP-09 과밀/정상/푸터) + `assets/dark-bg.png`. 수정전 사본 `/c/msys64/tmp/{preflight,validate-pptx}-OLD.js`. 검증환경 = pw-shim 없음→`convert-native --skip-preflight`, OLD/NEW swap 측정
- [x] R1 그룹A 적용·검증 — VP-04 picture제외 / VP-10 중첩제외+음수스킵 / VP-09 shrink **0.92** `model: opus`
  - validate-pptx.js 5패치 적용(checkContrast pictures / overlapsPicture / VP-09 측정재보정 0.92 / VP-10 meaningfulRaw 중첩제외 / 음수gap 스킵 / 호출부). 구문 OK
  - **합성 4장 before/after**: VP-04 이미지위 흰글자 2 FP제거 + 흰on흰 2 TP유지 ✓ / VP-10 Row C `[9pt,159pt]` TP보존 + 중첩노이즈 4 제거 ✓ / VP-09 slide4 dense TP유지(4→5줄 측정정밀화)
  - **★운영덱 156장(slides-grab 8덱) OLD→NEW**: VP-04 776→742(−34) / VP-09 159→23(−136) / VP-10 467→46(−421) / **의도룰 VP-02·03·07·08·11·14·16 전부 불변 = 직교 회귀안전 ✓**
  - **FP/FN 이미지 직접판정**(export-slides-png COM 렌더 → Read):
    - VP-10 양수소멸 표본 5장(s17·27·32·68·122) 직접 확인 → 전부 카드 내부 중첩(배지/라벨/값)이 만든 가짜 불일치, 실제 카드 균등 → **FN 0**. (소멸421 = 겹침음수370 + 중첩노이즈51, 잔존46=진짜불일치)
    - VP-09 소멸 표본 3장(s130 표·s60 차트·s79 카드) 직접 확인 → 텍스트 전부 박스 정상수용, 과밀/잘림 0. 숫자·라틴 7pt/char 과대추정 FP를 라틴0.5 교정으로 제거 → **FN 0**
- [x] R1.5 ★추가개선 — VP-04 텍스트밝기 게이트 (개선안 위 정교화) `model: opus`
  - **발견(FN)**: ★핸드오프 "picture 겹치면 무조건 제외"는 **운영덱 소멸 34건 중 33건이 FN**(s3 청록 `$1,583억` luma143, s90 주황 "COVID 가속" 144, 회색 출처 161 등 — 연한 장식 picture 위 유채색/회색 저대비 텍스트 과잉제외). 밝은 흰글자 진짜 FP는 1건뿐. 핸드오프 그대로 채택했으면 33 FN 박을 뻔
  - **개선 적용**(validate-pptx.js checkContrast): picture 겹침 제외를 **도형의 모든 텍스트 run 이 밝을(luma>200) 때만** 적용. litRuns.every(luma>200) AND overlapsPicture
  - **검증**: 운영덱 VP-04 776→(무조건)742→**(게이트)775** = 밝은글자 1건만 제거, 33건 복원 ✓ / 합성 slide1 흰·연회 글자 FP제거 유지 ✓ + slide2 흰on흰 invisible TP유지 ✓. **FN 0**
- [x] R1.6 잔존 TP 정당성 검증 (사용자 지적: FP/FN 양방향) `model: opus`
  - VP-10 잔존(46) 표본 s7·s9 직접확인: 큰 FP(겹침/중첩) 제거됨, 잔존은 **약한 FP**(우측정렬 값간격·타임라인 텍스트폭 변동, stdDev 5pt 절대임계 민감). 진짜 불일치 TP는 소수. **FN(놓침) 0**
  - VP-09 잔존(23) 표본 s74 직접확인: 박스높이 작게 잡힌 경계 케이스, 렌더상 잘림 없음 = 약한 FP 경향. 명백 과밀 아님
  - **결론**: 잔존 약한 FP = 과발화지 정탐회귀 아님. 추가개선 여지(상대임계)는 핸드오프도 코퍼스 의존이라 보류 → L2 큐
  - **잔존 이슈**: 합성 slide1 부제 자연폭 1줄→2줄 오판(VP-09). 운영덱 순감소라 빈도 낮으나 L2 큐 기록
- [x] R2 그룹B 적용·검증 — PF-23 realOverflow / PF-65 Range측정 / PF-66 ellipsis제외 `model: opus`
  - preflight-html.js 3패치 적용. 구문 OK. **운영 156장 --full OLD→NEW**: PF-23 **156→4(−152)** / PF-65 33↔33 / PF-66 34↔34 / 나머지 PF 전부 불변 = 회귀안전 ✓
  - **PF-23**: OLD가 전 슬라이드 발화(scrollWidth≈clientWidth라 20%보정이 무조건 5%초과 = 버그). 이미지 직접판정: 사라진 s1003(ai-infra) 텍스트 정상수용=FP, 남은 4건 s8017"기본급(22일×10만)" 컬럼 빠듯=경계 TP → **−152 거대 FP제거, FN 0**
  - **PF-65**: 카운트 동일이나 발화 **대상 교체**. 이미지판정: 사라진 s4013 분기라벨"2024Q1~Q4" 1줄=FP제거 정당 / ★새로생긴 s4007 복합셀(원형배지+라벨 세로배치 "+12%/긍정적")을 Range가 도형높이 합산해 2줄 오판 = **새 FP 발견**
  - [x] ★R2 추가개선 — PF-65 blockKids 게이트: 셀에 블록자식 ≥2(배지+라벨 의도적 세로배치)면 wrap 아님 → 제외. 표본검증: s4007 FP 제거됨 ✓ + s4013 무발화·s8012/8017 scrollWidth TP 유지 ✓
  - **PF-66**: 운영덱 OLD=NEW 완전동일(ellipsis 케이스 부재) → 효과 0. 합성 픽스처로 검증 필요(R2b)
- [x] R2b PF-66 합성 검증 (slide-5) `model: opus`
  - before/after: OLD 2건(clamp+clip) → NEW 1건(clip만). **line-clamp/ellipsis FP 제거, 진짜 overflow:hidden 클리핑 TP 유지** ✓
- [x] R3 그룹C 적용·검증 — PF-15·30·41·45 px→pt / PF-34 blockSpans `model: opus`
  - preflight 8패치 적용. 운영 156장: PF-15/30/41/45 효과0(운영덱 pt만=안전망, 핸드오프 예측대로) / 나머지 PF 불변=회귀안전
  - **합성 slide-6/7 before/after**: PF-30(인라인 16px≤24px)·PF-41(자간2px)·PF-45(마진-12px) OLD 전부 무발화(px 미인식 FN) → NEW 발화 = px→pt 개선 입증 ✓ / PF-34 OLD 2(inline FP)→NEW 1(block TP) ✓. PF-15 동일 코드 패턴(코드 동일성 입증)
- [x] R4 통합 회귀 + 커밋 `model: opus` → **커밋 b304a40**
  - PF 156장 최종: PF-23 156→4, **PF-65 33→23(blockKids 순감소)**, PF-66/15/30/41/45 안전망, 의도룰(PF-20/25/28/36/70) 불변 ✓ / VP 최종 VP-04 775(밝기게이트)·VP-09 23·VP-10 46, 의도룰 불변 ✓
  - VERIFICATION.md(slides/rule-audit/) 박제 — 종합표 + FP/FN 이미지판정 + 추가개선2 + L2큐. 양파일 구문OK
  - PF-15 확인 완료(slide-6 3-col grid CJK 14px: OLD 무발화 FN→NEW 발화)
  - **L2 큐(추가개선 여지, 코퍼스 의존이라 보류)**: VP-10/09 잔존 약한FP(상대임계) / VP-09 합성 slide1 부제 자연폭 오판
  - 미푸시(사용자 확인 대기)

## Phase R5 — 핸드오프 "로컬/코퍼스 못본다" 분류 규칙 직접 판정 `2026-06-14`
> 사용자: "프롬프트는 로컬 환경 없어 못본다 했으니 너가 봐야한다". 핸드오프 코퍼스전용 7 + 정적32 + 미발화25 미점검분을 운영덱 156장 + 이미지로 직접 판정.
- [x] R5-1 코퍼스전용 7규칙 판정 (운영덱 + 이미지) `model: opus`
  - VP-03 423→362(fill 시각요소 제외)·VP-02 178→109(상대변동 게이트) 추가개선 적용. VP-11/PF-20/VP-08 FP패턴 식별(다음배치). VP-07/VP-01 저빈도. 상세 VERIFICATION §R5
- [ ] R5-2 잔여 추가개선(VP-08 fill제외·PF-20 푸터면제·VP-11 멀티컬럼) + 정적32 + 미발화25 `model: opus` (다음 배치)

## Working Notes
> [ckpt-202606131410:btn-design]
- 마지막 결정: excel `metric_table.py` 생성(사용자 제공 코드 그대로, /d/projects/excel/fpna/templates/). design 개선 9건 = LICENSE만 생성, 나머지 8건 미적용.
- 다음 의도: (1) excel `fpna/templates/__init__.py` _MODULES 에 metric_table 등록 + `py main.py selftest` 검증 (2) design 9건 = `handoff-improvements-20260613.md` 대로 §A embed-fonts/gen-report/test-fonts/CI-yml + §B convert-native 가드·package.json vr:test·thresholds.json·.aiignore 적용.
- 동기화 필요: design push 완료(ad3ff36). LICENSE·handoff md·excel metric_table = 미커밋. HANDOFF 9건 전문 = 사용자 2026-06-13 14:07 메시지(다음 세션 재요청).
