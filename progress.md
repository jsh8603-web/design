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

## Phase C — VP/PF 정답화 마무리 + 교차검증 `2026-06-15` `model: opus`
> plan.md `# VP/PF 정답화 마무리` 참조. 판정기준 SSOT 5항(plan). 자율주행, 정탐회귀 절대금지.
- [x] C0 표본확대 발견 FP 처리 — phantom 흰글씨(VP-04 배경오측정 2종: 뱃지 미세이탈 톨러런스 + 막대=트랙 동률 타이브레이크) + 장식glyph("+") 제외. errors 14→4, WARN 119→115, GT 13/13. 커밋 (phantom)·(glyph)
  - 회귀 확인: VP-04 수정전후 diff = phantom 10건(s43/59/122/149/151)+glyph 4건(s123)만 제거, 새 발화 0. 이미지 직접판정(s43/59/122/149 정상슬라이드).
- [x] C1 VP-16 출처캡션 게이트(31→21) + autofit 게이트(21→16, normAutofit skip·겹침예외 GT보존). errors 4→2. GT VP-16 4/4
  - 회귀 확인: GT 13/13 전구간 유지. 잔존 비-GT 12건(s26/56/76/78/113/129/134)=autofit none이라 GT s71/99(none)와 추정구조 동일 → 정탐회귀 방지 보수유지(subagent FP확인했으나 안전신호 부재)
- [x] C2 VP-04 배경추적 정밀화 — phantom(뱃지 톨러런스+막대 타이브레이크) + 반투명 alpha 제외 + 2-tier 배경선택 + 장식T. A8B8CC 7·s144·s57 제거. VP-04 88→80
  - 회귀 확인: 각 수정 verify-gt 가드, GT 13/13. s71 2회 LOST→즉시 게이트 보정(톨러런스 0.15·2차 폭2배 제한)으로 복구
- [x] C3 PF-clean=VP-clean 교차검증(색 단위, 매핑우회) — VP-04 발화색 전부 PF-71도 발화 = PF 구멍 0. A8B8CC·FF9800 해소로 2색→0
- [x] C4 VERIFICATION.md 박제 + 커밋(phantom·glyph·출처·반투명·장식T·autofit 6커밋). VP 133→96, FP 37건 제거

## Phase D — PF 룰 정답화 `2026-06-15` `model: opus`
> plan.md `# PF 룰 정답화` 참조. PF-70부터, 끝까지 자율주행. 이미지 직접판정, FP는 로직게이트(회피금지), 정탐 놓침 금지.
- [ ] D1 PF-70(91건 이미지품질: object-fit/pt/border-radius/alt) 이미지 직접판정 → 게이트
- [ ] D2 PF-28/25/20 realmix 재판정
- [ ] D3 잔여 미판정 PF (PF-60/61/36/24 등)
- [ ] D4 VERIFICATION 박제 + 커밋

## Working Notes
> [ckpt-202606150000:btn-design] **STATUS: Phase C 완료 — VP 정답화 마무리 + PF교차검증**
- 마지막 결정: 사용자 "vp정답화→pf렌더링하면 vp 안잡혀야 정상, 잡히면 pf구멍. 정탐회귀 절대금지, fp 최대0, 기준명시" + 자율주행 on2. **판정기준 SSOT 5항 plan 박제**(recall=1.0 절대/이미지직접/TP=WCAG미달·잘림/accent=약한정탐 유지/PF-clean=VP-clean). **성과**: VP 133→96(E2 W94), FP 37건 제거(phantom10·glyph4·출처10·반투명A8B8CC7·장식T1·autofit5, 전부 이미지직접판정), GT 13/13 recall=1.0 전구간, ★PF-clean⊇VP-clean(VP-04 발화색 전부 PF-71 커버=구멍0). 커밋 6개.
- 다음 의도: 잔존 = (a)VP-16 비-GT 12건(autofit none, GT s71/99와 추정구조 동일 → 정탐회귀 위험 보수유지. 추가시 bodyPr tIns/bIns 파싱으로 padding 정밀화 여지) (b)VP-04 강조색 65건(기준4=WCAG미달 약한정탐 유지, GT가 REAL로 박음. 사용자가 FP로 재정의 원하면 floor·PF-71 동반조정+GT재산정 필요 — §4 미해결). PF 과민분(1B2A4A/FAFAF9/FFFFFF26=HTML단계 엄격경고, 변환후 무해).
- 동기화 필요: 엔진 scripts/validate-pptx.js(findBackgroundColor 2-tier+alpha, checkCjkTextOverflow autofit게이트)+preflight-html.js(PF-71). VERIFICATION.md 전과정 박제. 회귀이미지 regr-img/(s137/141/144/57 등 추가). long-mode on2(750k).
> ★인계(이전): [handoff-vp-pf-crossverify-20260615.md](./handoff-vp-pf-crossverify-20260615.md) — 표본확대 FP발견, §5 우선순위(①phantom ②glyph ③VP-16 ④강조색 — ①②③ 처리완료, ④ 미해결)
> 인계: [handoff-sweetspot-20260614.md](./handoff-sweetspot-20260614.md) — 정답지 기반 sweet-spot 튜닝
> [ckpt-202606142330:btn-design] **STATUS: VP 전수 정답화 + PF-71 보강 완료**
- 마지막 결정: 사용자 "VP 일부만 본다·정공법 FP0"+"PF는?"+"PF-clean인데 VP걸리면 PF구멍" → ★작업순서 재정립: Phase1 VP정답화→Phase2 PF보강. **Phase1**: VP 16룰 전수, VP-14 거짓ERROR7(장식글자 S/5)·VP-07 FP2(h0셀) 제거(GT밖 구멍), 미발화6 회귀✓. errors21→14·WARN129. **Phase2**: PF-VP교차테스트→VP-04저대비 PF구멍 발견→PF-71 신규(텍스트대비 floor2.124, --full Playwright). GT검증 VP-04동일ratio, realmix PF-71 99≈VP-04 92=PF-clean→VP-04clean 보장. 커밋 76ea1dd·efe858b 등.
- 다음 의도: VP-09 9 경계(추정한계 보수유지, 추가시 FN위험). PF 나머지룰(PF-25/03/36 등) 교차검증 여지. plan sweet-spot 완료, VP전수+PF-71은 확장분.
- 동기화 필요: VERIFICATION.md(전과정+교차검증+PF-71 박제). 회귀이미지 regr-img/(30+장). long-mode on2(750k). 엔진 scripts/validate-pptx.js+preflight-html.js(PF-71).
> [ckpt-202606142240:btn-design] **STATUS: sweet-spot 튜닝 완료**
- 마지막 결정: GT기반 sweet-spot 완결(이미지 직접판정, 등급회피 폐기). 전체 WARN 849→132(84%↓)·OLD 2014 대비 153(92%↓), GT 13/13 recall1.0. VP-04 floor2.124(92 TP)·VP-16 467→27(wraps겹침게이트+fills세로넘침+표격자)·VP-02 너비끔(0)·VP-03/11 끔. 커밋 28b2f80~45c2f5a(9개). plan sweet-spot 3항목 전부 [x].
- 다음 의도: plan 3항목 완료. 추가 여지=VP-09 9(빡빡카드 경계, 보수유지)·잔존 미검증 143장 TP 검증. 사용자 추가 지시 대기 or OLD/NEW 채점 후속.
- 동기화 필요: VERIFICATION.md(전 과정+채점 박제) slides/rule-audit/. 회귀이미지 regr-img/(20장). long-mode ON. 검출엔진 scripts/validate-pptx.js.
> [ckpt-202606142115:btn-design]
- 마지막 결정: ★등급추가=회피 폐기(사용자 "WARN 안뜨게/INFO 회피"). FP는 검출로직으로 발화제거, 판정은 이미지직접확인(realmix 12장 COM렌더). 적용완료: VP-04 floor 2.124(537→92, 강조색/캡션 raw 2.13~2.8 FP)·VP-16 1.1(467→172, fills100~110% 한줄확인 s7/9/63/124)·VP-02/10 표격자가드(45→9·38→1, 직교축짝 과반=격자 skip)·VP-03/11 끔(빈프레임투명·z-order, 함수보존 호출주석). GT 13/13 recall1.0. 전체 WARN 849→282(67%↓). 커밋 28b2f80·b679a54·d8058b4. INFO강등 d93e5cd는 원복.
- 다음 의도: 잔존 VP-02 9건 진짜 산발오정렬 1건 이미지확인(의도살림 검증)·VP-09 9건/VP-16 168건 sweet-spot 여지 점검. OLD/NEW/TUNED 부수채점(plan 마지막). VERIFICATION.md=slides/rule-audit/ (INFO섹션 정정완료, 실제처리 박제).
- 동기화 필요: 이미지 slides/rule-audit/regr-img/(s7·9·23·24·63·93·97·115·124·127·131·54). 정답지 slides/rule-audit/ab-verify/groundtruth.json. long-mode ON(cap500k). 검출엔진 scripts/validate-pptx.js.
> [ckpt-202606141016:btn-design]
- 마지막 결정: 정답지 = 3 blind Opus 다수결(split0) majority-REAL 13건(VP-04 저대비9·VP-16 실제잘림4, FP277·VP-11검증불가12). VP-04 WARN 임계 4.5→3.0 적용(validate-pptx.js:38), 운영 775→547, 정답 ratio2.1/1.9/2.3 생존=recall1.0. **미커밋**.
- 다음 의도: VP-16 sweet-spot("fills %" 추정→렌더잘림 검출 또는 임계1.0→1.1, 정답4 생존확인) → VP-08/03/02/10 고확신만 축소 → VP-11 WARN침묵 → 12장 재측정 recall1.0+precision↑. plan.md "정답지 기반 sweet-spot 튜닝" 체크리스트 기준.
- 동기화 필요: VP-04 변경 미커밋. 자산 slides/rule-audit/ab-verify/(judge1~3·groundtruth.json·gemini-judge.mjs). 정답지 C:/msys64/tmp/ab-verify/groundtruth.json. handoff-sweetspot-20260614.md 전체 맥락.

> [ckpt-202606131410:btn-design]
- 마지막 결정: excel `metric_table.py` 생성(사용자 제공 코드 그대로, /d/projects/excel/fpna/templates/). design 개선 9건 = LICENSE만 생성, 나머지 8건 미적용.
- 다음 의도: (1) excel `fpna/templates/__init__.py` _MODULES 에 metric_table 등록 + `py main.py selftest` 검증 (2) design 9건 = `handoff-improvements-20260613.md` 대로 §A embed-fonts/gen-report/test-fonts/CI-yml + §B convert-native 가드·package.json vr:test·thresholds.json·.aiignore 적용.
- 동기화 필요: design push 완료(ad3ff36). LICENSE·handoff md·excel metric_table = 미커밋. HANDOFF 9건 전문 = 사용자 2026-06-13 14:07 메시지(다음 세션 재요청).
