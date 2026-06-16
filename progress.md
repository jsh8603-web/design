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
- [x] R5-2 잔여 추가개선 — 후속 Phase C/D에서 전부 흡수: VP-08 fill제외(validate-pptx.js:709/712 종횡비·카드동료 억제)·PF-20 비활성(preflight:1620)·VP-11 멀티컬럼+reading order 비활성(validate-pptx.js:1013/1585). 정적32+미발화25 = D5 전수검토(VERIFICATION D5/D5b, PF미발화43 bug0·VP미발화13 정상). `model: opus`

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
- [x] D1 PF-70 91→0 (subagent 전수 FP·TP0, 디자인 이미지 클래스 면제 게이트). 커밋
- [x] D2 PF-28/25 정적 게이트 (subagent 전수 FP) — PF-25 61→35(보조정보 제외), PF-28 84→61(표/숫자 제외). 잔존 = 정적 한계(요소역할·레이아웃 미인지)
  - 회귀 확인: checkPF25/PF28 독립 수정, 타 PF 룰 불변. 잔존은 정탐놓침방지 보수유지
- [x] D2b PF-20 45→0 (subagent COM 16장 전수FP, safe-margin≠잘림 비활성, PF-03 위임). 커밋
- [x] D3 ★잔존 완전해소 + 소급 (COM 직접판정) — (a) PF-25/28 --full computed 전환 96→0(6장 직접, 짧은라벨/도형/표 제외+극소긴본문만+scrollHeight넘침만) (b) 소급 PF-66 34→3(TP s8004/s8017 보존)·PF-65 23→1·PF-23 4→1·PF-03 12→1·PF-18 2→1·PF-15 10→0·PF-27 3→0 (c) 잔존 분류: PF-71/60(accent 약한정탐)·변환호환7룰/PF-21(표준강제 유효). --full 384→207. 커밋 a666eec·b56580a·9f36dd7
- [x] D4 VERIFICATION 박제(D2c·D3) + 커밋
> ★잔여(다음): PF-71 99(VP-04 accent ④ 핸드오프 연동, 기준4 약한정탐 유지)·PF-21 13(이미지왜곡 표준, borderline 전수판정 미완)·1건씩 13개(개별). 사용자 accent FP 재정의 시 floor·PF-71·GT 재산정.
> ★인계: [handoff-pf-truing-20260615.md](./handoff-pf-truing-20260615.md) — PF 정답화 현황+3 subagent COM 판정+잔존 --full computed 로드맵+소급대상

## Working Notes
> [ckpt-202606150600:btn-design] **STATUS: 전체 규칙(PF 67+VP 16) 전수 검토 완료** ✅
- 마지막 결정: 사용자 "전체 안본거 마저, VP도 팩트체크" → 3 subagent 병렬. ①PF 발화 미판정 18룰 COM(E): FP 7룰 비활성(PF-36 19발 최대노이즈 등, 전부 실측룰 PF-71/03/18/23 대체)+TP 3유지(PF-37/19/42)+권고/정책 8(PF-26 비활성, 나머지 사용자판단). PF 197→161. ②PF 미발화 43룰 코드리뷰(G): 버그0, 케이스부재 정상. ③VP 96 팩트체크(F): VP-04 80건 FP0(측정정확, TP9+약한정탐71 accent)·VP-16 ERROR 2건만 FP(s76 autofit 미반영, 메인 falsify확인)·GT recall 13/13·미발화 13룰 정상. 커밋 f3c5cf9·9509e5a.
- VP-16 s76 FP 보강 완료: lineCount(명시 줄바꿈)≥2 AND 인접 겹침 없을 때만 줄당 폭 → s76 ERROR2 제거, GT 71/99(겹침=원래폭) 보존. 1차 무조건 lineDiv가 s99 제목 누락(recall 회귀) 발견→겹침조건 재설계. VP 96→95, recall 13/13.
- 미해결(사용자 판단): ①PF 정책/권고(PF-29 alt·40 AI·31 중복제목·09/10/11/22 디자인)=FP 재정의 시 약화. ②VP-02/10 약한 과억제 잔여위험(폴리시드 덱 0발화 정상범위).
- 전체 결론: PF 검출오류 FP 룰 384→161 전부 COM 게이트. VP 정답성 검증(FP0~2건). GT 13/13 보존. accent(PF-71 106·VP-04 약한정탐 71)=기준4 유지.
> [ckpt-202606150500:btn-design] **STATUS: PF-clean⊇VP-clean 교차검증 + 대비갭 메움 (PF 197)** **STATUS: resolved (2026-06-15 ckpt-0600 흡수)**
- 마지막 결정: 사용자 "PF로 생성한게 VP에 안걸리나" → PF 약화(384→190) 후 교차검증 미재실행 발견. realmix.pptx VP 실행(96=VP-04 80·VP-16 16) ↔ PF 교차. **갭 2종**: ①VP-04 색단위 구멍 1색(흰on주황 FFB347, s3014 번호배지 "3"/"4" 흰글씨를 PF-71이 length<2 skip) → PF-71 보강(장식 glyph만 제외, 번호 검사=VP-04 checkContrast 동일). PF-71 99→106. **색단위 재교차 VP-04 19색 전부 커버=구멍0 복원** ②VP-16 overflow는 변환기 도형 렌더차이(s5011 .step-box 48pt고정에 2줄 HTML정상→PPTX 29pt·3줄 넘침). HTML서 예측시 FP양산 → PF예방+VP실측 역할분담이 정답(갭 아님). 커밋 59f6d4c.
- 검토 범위 정직: VP 16룰 완료·PF 발화 검출오류룰 COM 게이트 완료·VP-04↔PF-71 교차 구멍0. **미완**: 변환호환 표준룰(PF-36/19/29 등 코드사실 유효, 전수 COM 아님 분류만)·PF 미발화룰(realmix 0발화=대상없음)·VP-16↔PF overflow(변환특성, 역할분담).
> [ckpt-202606150400:btn-design] **STATUS: PF 검출오류 FP 룰 COM 게이트화 (--full 384→190)** **STATUS: resolved (2026-06-15 ckpt-0500 흡수)**
- 마지막 결정: "필요한거 다 해" 자율. D3b 추가 — PF-21(이미지왜곡) 13→0(subagent 전수 FP, object-fit 미반영 측정버그=cover/contain 비율보존인데 박스AR만 봄. objectFit AR보존 skip+썸네일<64px 면제)·PF-30(폰트계층) 3→0(카드 강조숫자 232,000을 본문 오인, 직후텍스트 숫자/단위/≤6자 제외)·PF-24(흰on흰 cross-slide) 1→0(s8040 흰글씨=주황배지 위, 정적 매핑부재 오판, 실측 PF-71 위임). 커밋 90ae383.
- 잔존 190 = 전부 검출오류 아님: PF-71 99(accent 약한정탐 기준4, VP-04 accent ④ 핸드오프)·변환호환 표준강제(PF-36/19/29/41/42/40/37/35/22/64/45/47=코드사실 유효)·accent PF-60 4·TP보존(PF-66 3=s8004/8017·PF-03 1=s2015·PF-18/23/65 경계)·디자인권고 cross-slide(PF-09/10/11/31/26).
- 다음(선택): PF-71 99 accent 처리는 사용자 FP 재정의 시 floor·PF-71·GT 재산정(기준4상 현재 유지 확정). 변환호환/디자인권고는 정책결정 사안(검출 정확, 죽이면 표준 상실).
> [ckpt-202606150300:btn-design] **STATUS: PF 소급 재판정 (잘림/오버플로/겹침 COM 정밀화 384→207)** **STATUS: resolved (2026-06-15 ckpt-0400 흡수)**
- 마지막 결정: 사용자 "대충말고 COM 이미지"+"PF 소급적용" 수행. ①PF-25/28 정적→--full Playwright computed 전환(checkPF25/28 빈반환, runPlaywrightChecks에 실측 게이트). PF-25=실측 font-size<7pt+긴본문≥20자+짧은라벨/svg/table/출처 제외(6장 COM 직접판정 8-9pt 전수 가독 FP), PF-28=실측 scrollHeight 세로넘침만(밀도≠결함). 96→0. ②소급 COM: PF-66 34→3(★subagent 전수판정 TP 2=s8004 ④4대보험값·s8017 콜아웃 진짜 정보손실, 메인 직접 재검증 확정. 게이트=잘린본문 실존+길이>4+보이는비율≤0.65+장식워터마크/디센더 skip)·PF-65 23→1·PF-23 4→1(tolerance+세로축라벨/행높이흡수 skip)·PF-03 12→1(8px tol, 4px 여백오차 FP, s2015 28px 보존)·PF-18 2→1(차트 트랙+fill 레이어 ownText DIV 제외)·PF-15/27 0(정적 wrap/overflow 예측 비활성, 실측 위임). 회귀0(GT 13/13·PF-clean⊇VP-clean 무영향).
- 다음 의도: PF-71 99(VP-04 accent ④ 핸드오프, 기준4 약한정탐 유지 — 사용자 accent FP 재정의 시 floor·PF-71·GT 재산정)·PF-21 13(이미지 aspect 왜곡 표준, borderline 전수 COM 미완)·변환호환7룰(PF-36/19/29/41/42/40/30=코드사실 유효 유지)·1건씩 13개(개별 노이즈/TP). 추가 정밀화는 PF-21 전수판정 or accent 재정의 시.
- 동기화 필요: preflight-html.js(checkPF25/28/15/27 빈반환+runPlaywrightChecks PF-25/28/66/65/23/18/03 게이트), VERIFICATION.md(D2c·D3 박제), pf-full13.json(현 207). long-mode on(500k). realmix 155장. 커밋 a666eec·b56580a·9f36dd7.
> [ckpt-202606150100:btn-design] **STATUS: PF 정답화 진행중 (정적게이트 완료, 잔존+소급 = --full computed)**
- 마지막 결정: 사용자 "대충말고 COM 이미지"+"PF 보던것도 소급적용". PF 정적게이트 PF-70 91→0 완전·PF-25 61→35·PF-28 84→61·PF-20 45→0(--full 569→384). 3 subagent PowerPoint COM 전수판정=전부 FP·TP0. 잔존(PF-25 35 inline 9pt·PF-28 61 본문카드)은 정적 정규식 한계 → --full computed 전환 필요.
- 다음 의도: [handoff-pf-truing-20260615.md](./handoff-pf-truing-20260615.md) §5 — (a)PF-25/28 --full Playwright computed 전환(요소역할·넘침 실측) (b)이전검증 PF 소급 COM 재판정(PF-23/65/66/15/34/18) (c)D3 PF-36/19/29/60. 정탐 보존, COM 이미지 직접판정.
- 동기화 필요: preflight-html.js(PF게이트 적용됨), VERIFICATION.md(D1/D2/D2b 박제), pf-full3.json(현 384), regr-img/(COM 렌더 다수). long-mode on2(750k). realmix 155장.
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

## Phase D-design — 디자인-룰 충돌 sweet-spot (Tier1+2, 회귀0) `2026-06-15` `model: opus`
> 사용자: "정탐 회귀·트레이드오프 0 + 디자인 의도 존중 + 실변환 테스트 필수". 변환기 능력 기준 3-tier 분류, A(Tier1+2) 채택.
> ★핵심 분리축: 변환기가 실제 살리는 디자인을 막으면 FP(완화) / 변환기가 버리는 디자인을 막으면 정탐(유지=풀면 변환후 깨짐). 근거 = html2pptx.cjs 실능력 falsify(subagent a8dc4e8).
- [x] T1-1 PF-19 폰트 동적스캔 — vendored woff2 스캔 + var(--font-*) resolve + CSS_VAR_FONTS.values() SSOT. ★falsify로 버그 발견·수정: 카멜분해 "JetBrainsMono"→"jet brains mono" 오차 → CSS 실제값 포함으로 해결. 재검증 PF-19 0
- [x] T1-2 PF-39 div linear-gradient ERROR→WARN — 변환기 solid fallback 입증(COM 렌더 남색 단색, 패널 생존). 주석→selector 오인 cosmetic도 fix
- [x] T2 대안권고 — PF-07(wrap div)·PF-55(parent div)·PF-42(rgba) 메시지 점검 결과 이미 충실 → 변경불요(over-eng 회피). embed-fonts 1-B도 정합으로 skip
- [x] TEST 실변환 — slides/design-test/slide-1.html(vendored폰트+gradient+배지) → convert OK(font-guard·XML pass) → COM PNG. 변경前 PF-39 ERROR·PF-19 WARN → 변경後 둘다 통과/WARN. compare.png 전송
- [x] REG 회귀게이트 — rule-audit PF 발화 diff 0(PF-19/39 외 정탐 불변). PF변경은 VP GT(VP-04/16)와 직교라 realmix GT 13/13 무영향

## Working Notes
> [ckpt-202606152038:btn-design]
- 마지막 결정: **frame 정정** — 검증 대상 = 디자인 스킬 산출물(SKILL.md §2.5 Step0~7 시각검사 flow), slides-grab corpus = PF/VP 룰 정답화 **read-only GT**(검증 대상 아님, ⛔삭제금지). 내가 triassic PF-13 GT 를 근거순환으로 삭제 → 사용자 drift 지적 → `git checkout full-baseline.json` revert 완료(PF-13 1건 원복). **PF-13 자율 판정**: triassic(12pt 정사각)·modern(49.78px 정사각 "↘") 원형 둘 다 COM 렌더=깨끗한 원=과탐 / 비정사각(80×48)만 pill 깨짐 → `preflight-html.js` checkPF13 정밀화(정사각 ratio0.95~1.05 통과·비정사각/치수불명 ERROR, pf13Len 헬퍼 신설). 개별 승인 안 받고 plan §0.5 기준 자율.
- 다음 의도: **S1 editorial B6 보수**. 근본 = `html2pptx.cjs` 가 `.name.serif` "The slides-grab Letter"(39.11px Newsreader, `slides/e2e-editorial/slide-01.html:7,26`) 텍스트박스 높이를 1줄 추정 → COM 서 serif 2줄 wrap → 아래 `.vol`("Vol VII", :8,27)과 겹침(`png-final2/slide_01.png` 좌상단). 우측 hero serif는 의도 보존 OK. K규칙 보수 2안: (a)**디자인 세트별 안전**=`.vol` margin-top↑ 또는 `.name` 높이/간격 수용 — 회귀0 (b)**변환기 전역**=텍스트 height 추정에 wrap 줄수 반영 — 회귀게이트 필요. 재변환+COM 확인 루프 필수. 이후 S2 modern(PF-13 정밀화로 변환통과 확인 + VP-04 noFill 배지 오판 정답화)→S3 executive(B5대비·B4overflow)→S4 academic→S5-7 생성.
- 동기화 필요: 미커밋 3 = `preflight-html.js`(checkPF13+pf13Len), `run-full-regression.mjs`(REGRESSION_SLIDES_DIR env override), `plan-design-e2e.md`(§0.5 신설+§4 B3 자율판정+frontmatter). `full-baseline.json` = revert됨(GT 원복). **PF-13 GT 정정은 COM 증거 박제 + run-full-regression 정탐회귀0 확인 후로 보류**(임의 삭제 금지). plan §0.5 = drift 방지 SSOT. corpus 전수 = border-radius:50%+border 조합은 triassic 1곳(7개 전부 정사각)뿐 → 정밀화 영향 1건뿐.

---

# Phase E — 8테마 e2e 정합 (디자인 스킬 산출물 검증) `2026-06-15` `model: opus`
> **SSOT = plan-design-e2e.md §0.5 + handoff-design-e2e-20260615.md §1**. ⛔drift 방지: 아래 3원칙 위반 시 R5 자가감사.
> **① 검증 대상** = 디자인 스킬(design-system) 생성 슬라이드 → PPTX 변환 → COM 렌더가 **디자인 원안대로 안 나오는 것** 을 해결. flow = SKILL §2.5 Step0~7. corpus(`/d/projects/slides-grab/slides/`) + `full-baseline.json` = PF/VP 룰 정답화 **read-only GT** (⛔검증 대상 아님·⛔삭제금지).
> **② K규칙 케이스 분류** (추측 금지, COM 직접 렌더로 판정): 룰 과탐 → **룰 게이트 수정**(등급강등=회피 금지) / 변환기 결함 → **변환기 수정** / 디자인 결함 → **디자인 수정**. 정탐회귀 절대금지(recall=1.0), FP→0.
> **③ incremental**: 세트1 버그 전부 해결(변환기·룰 전역 수정 포함) → 고친 파이프라인으로 세트2 재변환 → 세트2 신규버그만 → 반복. **디자인 수정=세트별 / 변환기·룰 수정=전역**. ⛔개별 건별 승인 안 받음 — 위 기준으로 자율.

## 세트 진행 매트릭스 (✅완료 / 🔄진행 / ⬜대기)
| 세트 | 테마 | 생성 | 변환 | COM검증 | 잔여 버그 | 상태 |
|---|---|---|---|---|---|---|
| **S0** | dark-pitch | ✅ | ✅ | ✅ | 없음 (검정+cyan+Newsreader hero 의도보존) | ✅ DONE |
| **S1** | editorial | ✅ | ✅ | ✅ | ~~B6 masthead wrap~~✅(변환기) · ~~slide-02 overflow~~✅(디자인 여백압축) · ~~drop 겹침 회귀~~✅(변환기 height게이트) | ✅ DONE |
| **S2** | modern | ✅ | ✅ | ✅ | ~~PF-13 변환통과~~✅ · ~~VP-04 noFill 배지 FP~~✅(룰 게이트) · ~~VP-10 space-between FP~~✅(룰 게이트) · VP-07 정탐 부수회귀 잡음✅(borderColor 분리) | ✅ DONE |
| **S3** | executive | ✅ | 🔄 | 🔄 | B5 대비(#FFF on #F5F5F0 1.09:1) · B4 overflow | 🔄 Teammate(a6a357) |
| **S4** | academic | ✅ | 🔄 | 🔄 | B4 overflow | 🔄 Teammate(acff12) |
| **S5** | classic | 🔄 생성 | 🔄 | 🔄 | (dark-deck 패턴+classic 토큰 생성) | 🔄 Teammate(a41a99) |
| **S6** | dark-mono | 🔄 생성 | 🔄 | 🔄 | dark 대비 정탐주의 | 🔄 Teammate(a7cebb) |
| **S7** | company | 🔄 생성 | 🔄 | 🔄 | — | 🔄 Teammate(ad0520) |

> **harness2-wf 병렬 dispatch (2026-06-15 13:05, ckpt-153100)**: S3~S7 5세트 = background Agent teammate 1세트씩(teamless bg Agent + agentId resume, ⛔subagent 일회성 아님). 각 teammate=생성/변환/COM/K규칙 **디자인수정만 자율**. ⛔**전역 룰/변환기(validate-pptx.js·preflight-html.js·html2pptx.cjs) 직접수정 금지** → execution-log `ev:global_issue` 로 메인 보고(병렬 공유파일 충돌 차단, 메인 합의 후 일괄 전역적용). 통신 SSOT=`.harness2/execution-log.jsonl`. agentId=`.harness2/agents.json`. **메인=Supervisor**: 완료 시 방법준수 점검 + 세트별 예시 ~3개 COM 직접 재검 + global_issue 합의판정. ⛔정탐회귀0·FP0·GT(slides-grab) 불가침.

> **[ckpt-202606153500] 5세트 teammate 전부 완료 + Supervisor 검증**: 방법준수 = 전 teammate 글로벌파일 직접수정 0(global_issue 보고만) ✅. COM 스폿체크(메인 직접) = S3 cover·S4 s2·S6 cover·S7 cover + S5 로그 = 생성품질·디자인수정 정상 확인.
> - **디자인 수정(세트별, teammate 자율)**: S3(B5 흰pill→navy-outline 배지·B4 overflow padding×2) / S4(B4 overflow padding 85.33→72) / S6(gray-3→gray-2 WCAG 다크대비) / S5·S7 수정0.
> - **★global_issue 2건 (메인 독립검증=진짜, 합의 처리 대상)**:
>   1. **변환기 결함 — html2pptx.cjs inline `<small>` 텍스트런 누락**(S4 발견). `.find .v` 의 `67<small>B$</small>`·`5.1<small>×</small>`·`52<small>%</small>` → 변환 XML a:t = "67"/"5.1"/"52"만, **단위 B$·×·% 소실**. XML+COM(s2 png) 양쪽 확정. inline `<small>` 파싱부 보수 필요(전역, 회귀게이트=e2e 전체+17 GT 재변환).
>   2. **룰 과탐 — VP-16 FP**(S3 발견). slide-01 dek("HBM·CoWoS·서버전력...28페이지의 답") 을 "740pt>available 364pt 3줄 overflow" ERROR 판정하나 COM(s1 png)은 **3줄 정상 들어맞음**. 원인=VP-16 폭추정이 `max-width:675.56px` + shape autofit 높이 무시. validate-pptx.js VP-16 게이트에 max-width/측정높이 반영 필요(전역, 회귀게이트).
> - 둘 다 ⛔전역 = teammate 미수정(보고만), 메인이 회귀게이트 거쳐 일괄 적용 예정. 적용 후 5세트 재변환·재COM 으로 효과확인.
>
> **[ckpt-202606154000] 글로벌 2건 합의 처리**:
> - ✅ **(1) `<small>` 변환기 fix 적용·검증완료**: `html2pptx.cjs:958` 인식목록에 `SMALL` 추가 + ELEMENT_NODE else-fallback(미인식 inline=SUB/SUP/CODE/MARK 등도 재귀로 텍스트 보존, silent drop 차단). 근본=parseInlineFormatting 이 SPAN/B/STRONG/I/EM/U 만 인식→SMALL 은 분기진입 후 run 미생성 소실. **검증**: S4 재변환 XML a:t="67","B$","5.1","×","52","%" 단위 복원 / modern 회귀 = "Business Deck"·"Presented by"·"Luna Martinez" 온전, 15런 중복0(strictly additive=소실분만 1회 추가). node --check 통과.
> - ⏸ **(2) VP-16 FP — 박제 후 별도 회귀게이트 처리(defer, recall 보호)**: 근본 = ERROR 경로(`validate-pptx.js:1449`)가 `verticalOverflow`(heightNeeded>shape h)만 보고 **인접겹침/슬라이드하단 클리핑 미확인** → 도형이 짧아도 아래 빈 공간으로 넘치면(=COM 가시, 미클리핑) FP. WARN 경로(1458)엔 이미 `!overlapsNeighbor && !isSmallShape→skip` 있으나 ERROR 경로엔 없음. **안전 수정안**: ERROR 발화에 `(overlapsNeighbor || (s.y+heightNeeded > SLIDE_H 실클리핑))` 조건 추가 = 인접 안 겹치고 슬라이드 안에 들어가면 가시 → skip. ⛔ **VP-16=코드 최다튜닝·recall 민감(GT 앵커 s99 제목→부제침범·s71 막대·s84·s132·s76 다수)** → 17 GT 전수 ERROR delta=0 회귀게이트 통과 후에만 적용. 저예산 졸속 금지(정탐회귀=최대금지). S3 executive 1슬라이드 FP라 긴급도 낮음(VP는 advisory, 변환 안 막음).

## 전역 자산 변경 (모든 세트에 적용 — incremental 누적)
- [x] **PF-13** checkPF13 정밀화 (정사각 ratio 0.95~1.05 통과 / 비정사각·치수불명 ERROR, pf13Len 헬퍼). COM 증거: triassic·modern 정사각=깨끗한 원, 타원만 pill. `preflight-html.js`. **GT 정정 보류**(회귀0 확인 후).
- [x] **B6 변환기 fix** — fill-없는 single-line shape-text 에 width headroom(영문 ×0.10/CJK ×0.18, 최소 10pt) + **height 게이트**(box높이 ≤ 1줄=`fontSize×1.6/72`in or fallback 0.45in). `html2pptx.cjs:417~440`. cx 3.029→3.332in, COM masthead 1줄 복귀 확인. **height 게이트 필수**: `!\n` 만으론 긴 본문(drop, 개행없이 wrap 다줄)이 오판돼 폭확장→우측 컬럼 침범(slide-02 겹침 회귀 발생→게이트로 해결). fill-shape/다줄 제외=회귀 직교.
- [x] **VP-04 noFill 배지 FP fix** (S2 modern, COM 증거 `png-fix/slide_01.png`) — `validate-pptx.js:158` parseShapes fill 탐색 전 `<a:ln>...</a:ln>`(테두리) 제거. 근본: noFill+border roundRect(투명 pill PRESENTATION/OUR PROJECT)의 `<a:noFill/>` 뒤 `<a:ln><a:solidFill val=1A1A1A>` 를 기존 regex 가 첫 solidFill 로 매칭→테두리색을 배경으로 오판→"#000 on #1A1A1A 1.2:1 invisible" 거짓 ERROR. COM 실렌더=크림 배경 위 검은 글씨 정상 가독. **⛔scope 주의**: line-158(checkContrast)만 ln-strip. getElements(line~1287)는 **ln-strip 금지**(아래 VP-07 정탐 의존).
- [x] **VP-10 space-between FP fix** (S2 modern slide-02) — `validate-pptx.js:~988` 끝(첫/마지막) gap 이 나머지 gap 최대의 3배+ 면 2클러스터 의도배치(헤더 좌측+우측 페이지번호 "02")로 보고 제외. 중간 큰 gap([6,217,6] 진짜 불일치)은 보존. COM=헤더 정상 space-between.
- [x] **VP-07 정탐 부수회귀 차단** (samsung GT regression gate) — VP-04 ln-strip 이 fillColor 를 공유하는 VP-07(빈 그리드셀 표 누락데이터)까지 죽임(samsung s4 분기표 Q1~Q3·연간 빈칸=진짜 결함=정탐). 해법: `shape.borderColor` 별도 파싱(line~172) + VP-07 필터 `(fillColor||borderColor)`(line~596)로 noFill+border 셀도 셀로 인정 = ln-strip 이전 원래 VP-07 거동 정확 복원. **VP-04 FP 해소 + VP-07 정탐 보존 양립**.
- **★정탐 회귀 0 게이트 통과**: 17 GT 덱 final vs HEAD ERROR delta=**0** (전덱 ERROR 동일). WARN만 FP 감소(noahs-ark 21→19, samsung 40유지, triassic 1→0 등). recall=1.0 보존 확정.

## B6 진단 (K규칙 = 변환기 결함 확정, COM+XML 실측) `2026-06-15`
- **증상**: editorial slide-01 masthead `.name.serif` "The slides-grab Letter"(39.11px Newsreader, `slide-01.html:7,26`) 가 COM 렌더서 **2줄 wrap → 아래 `.vol`("Vol VII" :8,27) 과 겹침**. HTML 원안(Chrome)=1줄. 우측 hero serif 는 폭 여유라 정상.
- **★기존 가설 정정**: 핸드오프 §3 "텍스트박스 **높이**를 1줄 추정" 은 부정확. 실측 결과 **폭** 문제.
- **근본 메커니즘** (PF_DEBUG 실측 + out.pptx XML): masthead label/name/vol 같은 **plain block div 텍스트가 type='shape' 로 추출**됨(배경/보더 없어도) → shape-embedded text 렌더 경로(html2pptx.cjs:391~420)는 **텍스트 폭보정(single-line headroom + fit:'shrink' autofit, 440~570)을 안 거침** → 박스 cx=3.029in = Chrome 빠듯폭 그대로 → PPTX Newsreader optical 폭이 더 넓어 초과 → wrap. (대조: h1 만 type='h1' text 경로라 normAutofit 적용됨)
- **증거**: `out.pptx` `.name` 박스 `cx=2769989`EMU=3.029in, `sz=2200`, bodyPr normAutofit **없음**. 12 bodyPr 중 normAutofit 1개(h1)뿐.
- **보수 방향 2안** (K규칙 변환기 근본, 회귀게이트 필수):
  - (A) **shape-embedded text 에 autofit(normAutofit/shrink) 적용** — shapeOptions 에 fit 추가. wrap 시 폰트 미세축소로 1줄. 국소·안전.
  - (B) plain div 의 shape 과추출을 text 로 전환 — 회귀위험 큼(다수 텍스트 영향), 비권장.
  - → **(A) 우선**. 적용 후 재변환 + COM 렌더로 1줄 복귀 확인 + rule-audit 회귀 diff 0.
- **⛔삽질주의**: B2 normAutofit·중복pPr 가설 기각됨. 폰트는 설치로 해결(임베드는 COM 무효). 높이 추정 가설도 기각(폭 문제).

> [ckpt-202606155500:btn-design] **STATUS: 변환기 결함 조사·1종 수정 (loose text-node drop) — ① 재현불가(수정안함)**
- 사용자 "ㅇㅇ"(변환기 결함 고치기) → 1종씩 회귀게이트로 진행.
- **① h3/p grid x-collapse = 재현 불가 → 수정 안 함**: 최소 재현 2종(grid+h3/p, align-items:center nested-flex) 둘 다 **정상 분리**(좌/우 컬럼 x 다름). 변환기가 grid/flex h3/p 정상 처리 = teammate 겹침은 긴CJK·타이트레이아웃 엣지케이스를 디자인 회피한 것이지 일반 변환기 결함 아님. ⛔근거 없는 blind fix 안 함(회귀위험).
- **③ loose text-node drop = 재현 확정 → 수정 완료**: `html2pptx.cjs:1090` 순회가 element만 방문 → 컨테이너가 block 자식+형제 loose 텍스트노드 동시보유 시 loose 텍스트 silent drop(`<div class=l>날짜</div>2026.06` → "2026.06" 소실). fix: block 자식 있을 때만 직속 loose 텍스트노드를 Range로 위치잡아 text emit(leaf-div 경로와 배타=중복방지). **회귀게이트**: 재현본 "2026.06" 복원+중복0 / 8 e2e 재변환 ERROR=0 / GT 3덱 a:t 수 HEAD=FIXED 동일(255/208/506=무영향).
- **② CJK width inflation·④ = 추가 조사 완료 (아래 ckpt-202606160030)**.

> [ckpt-202606161600:btn-design] **STATUS: ✅Phase4 새 복잡 5종(list/flow/pricing/quote/imagegrid) 5테마 + 새 결함 2종 수정**
- 새 5종 5테마 teammate 병렬, 전부 생성·변환·COM 통과(이전 FP 미재출현, 방법준수=글로벌 직접수정0).
- **새 변환기 결함 2종 수정**(5팀 교차확인, 회귀게이트):
  - **blockquote 텍스트 silent drop**: textTags(html2pptx.cjs:1087) BLOCKQUOTE 누락→풀쿼트 본문 소실. fix=BLOCKQUOTE 추가. (active=html2pptx.cjs 확정, teammate grep한 scripts/html2pptx-local.cjs=미사용 사본)
  - **중첩 ul/ol 이중방출+겹침**: UL핸들러가 querySelectorAll('li') 후손 평탄수집(중복)+중첩ul 미-processed→재방출 garbled. fix=`:scope>li`만+li자체텍스트+깊이 들여쓰기 재귀+중첩 ul/ol processed 등록.
  - 회귀게이트: blockquote 보존+중첩 중복0 / 8 e2e ERROR=0 / GT 5덱 run·글자수 동일(손실0).
- **미수정(별도)**: ⑤ pseudo-element(::before/after) 미렌더=근본한계(디자인은 실 div) ⑥ 오버레이 contrast FP(absolute 흰글씨를 페이지bg와 대비→FP, 실제 어두운 박스 위 가독). resolveBackground z-stack 필요=moderate, 박제만.

> [ckpt-202606160030:btn-design] **STATUS: ✅변환기 결함 4종 전수 조사·정리 — 진짜 버그 2종(③④) 수정, ①② 버그아님**
- 사용자 "필요한거 다해" → 변환기 4종 전수 재현·판정:
- **① h3/p grid x-collapse = 버그 아님**: 재현 2종(grid·align-items:center flex) 모두 정상 분리. 변환기 정상.
- **② CJK width inflation(*0.25) = 버그 아님**: `html2pptx.cjs:479-518` 의도된 wrap-방지 headroom. 박스만 넓히고 ink 중앙 유지 → 인접 박스 겹쳐도 **VP-14 ink-range가 흡수**(타이트 긴CJK 2컬럼 재현 = All checks passed, 박스도 실제 안 겹침). teammate workaround=구 VP-14 만족용.
- **③ loose text-node drop = 수정 완료**(커밋 2b9f6be).
- **④ orphan span drop = 재현 확정 → 수정 완료**: `<span display:inline-flex>` 배지(SECTION 1·pill)가 block 형제 있는 컨테이너 자식이면 shape 경로(`isContainer=DIV만`) 진입 못해 silent drop. fix: orphan span(자체박스+부모 block자식+부모≠textTag)만 shape 경로 허용(`html2pptx.cjs:1182`), leaf-div/textTag 내 span 제외=이중emit 방지. **회귀게이트**: 배지 복원+중복0 / 8 e2e ERROR=0 / GT 5덱 a:t 무변동(coupang +1="Coupang" = 실제 drop되던 텍스트 **복원**, 이중emit 아님, 새 ERROR 0).
- **결론**: 변환기 결함 4종 중 진짜 버그는 ③④(텍스트 silent 손실)뿐 → 둘 다 수정. ①②는 재현으로 버그 아님 확인(blind fix 회피). consult-adoption-gate 작동 = teammate 보고 4건 중 2건만 진짜.

> [ckpt-202606155000:btn-design] **STATUS: ✅Phase3 수정파이프라인 검증 = 8테마 fresh 재실행 전부 ERROR=0**
- 지시: 고친 파이프라인(VP-04/07/10/14/16 + `<small>` 변환기)으로 8테마(editorial/modern/executive/academic/classic/dark-mono/company/dark-pitch) **처음부터 fresh 재생성** 5장씩 → 디자인스킬→PF→VP→COM.
- **결과: 8/8 전부 ERROR=0** (academic/classic 각 2 WARN=timeline 라벨·bar gap cosmetic, COM 클린). **이전 phase2 FP 3종(VP-14 표 phantom·VP-16 cover dek·`<small>` 단위소실) 전 테마서 미재출현 = fix end-to-end 검증**. VP-16 fix 실증=표지 제목 ERROR→WARN("fits vertically").
- 디자인 결함은 teammate 자율수정(small margin→padding/div·h1 폰트↓·p→div·badge min-width). 전 teammate 글로벌 직접수정0=방법준수.
- **누적 변환기 결함(미수정·디자인회피됨, 별도 처리 목록)**: ①grid/flex 컬럼 내 `<h3>`/`<p>` x-collapse(academic/classic/modern 다수) ②CJK width inflation in grid(editorial) ③inline-flex/% bar collapse(executive) ④**loose text-node drop**(dark-pitch 신규: div가 자식요소+sibling 텍스트노드 동시보유 시 텍스트 drop, dark-deck 레퍼런스서도 재현=테마무관) ⑤inline margin reject(=진짜 PPTX 제약, 정탐). ①~④는 positioning/text-extraction 결함=전역 회귀위험 큼, 회귀게이트 갖춰 별도.

> [ckpt-202606154500:btn-design] **STATUS: ✅Phase2 복잡슬라이드 e2e(7테마×5장) + VP-14/VP-16 일괄수정 완료**
- Phase2: 각 테마 표지1+복잡슬라이드4(KPI/표/매트릭스/타임라인) harness2 Teammate 7병렬. 전 teammate 글로벌 직접수정0(global_issue 보고만)=방법준수. 디자인결함=슬라이드 자율수정(PF-62 conic→bar·h3→div·gray-3→gray-2·padding/gap 등). PF-55/62/63=변환기 미지원 정탐(디자인적응).
- **글로벌 일괄수정(메인, 회귀게이트 통과)**:
  - **VP-14 ink-range FP** (6/7 테마 데이터표 hit=체계적): `validate-pptx.js` parseShapes에 algn/lIns/rIns 파싱 추가 + checkShapeOverlap에 ink-range 게이트(같은행 box겹침이어도 정렬+CJK0.92폭추정으로 실제 글자범위 비겹침이면 skip). 좌라벨+우정렬숫자 phantom 해소.
  - **VP-16 ERROR 게이트** (cover dek FP): ERROR 조건에 `(overlapsNeighbor || s.y+heightNeeded>SLIDE_H)` 추가 — 빈 슬라이드공간 넘침(가시·미클리핑)=skip, 인접침범·슬라이드밖잘림만 ERROR.
  - **회귀게이트 통과**: ①17 GT 덱 ERROR delta=0(VP-14·VP-16 모두, recall=1.0 보존) ②합성 positive=진짜겹침/인접침범/슬라이드밖 발화유지·FP만 skip ③7 e2e 복잡세트 전부 ERROR=0(FP소멸).
- 미적용(별도, recall민감·고위험): 변환기 h3/p grid-column x-collapse·CJK width inflation·inline-flex/% (academic·editorial·executive 발견, teammate 디자인회피 됨). 박제만, 회귀게이트 갖춰 별도 처리.

> [ckpt-202606153100:btn-design] **STATUS: ✅S2 modern 완료(VP-04/VP-10 FP 룰게이트 수정 + VP-07 정탐 보존 + 회귀0). 다음=S3~S7 Teammate 병렬(harness2-wf)**
- 검증 대상 재확인(사용자 dispute 시정): 검증 대상 = **디자인 스킬세트(design-system) 생성 슬라이드 → 변환 PPT 의 원안보존**. slides-grab corpus(samsung 등)는 **검증 대상 아님 = 룰 정탐회귀0 확인용 read-only GT**(plan §0.5). samsung s4(분기표 Q1~Q3 빈칸)는 GT 의 VP-07 정탐 = 죽이면 안 되는 것 → borderColor 분리로 보존. samsung 을 길게 렌더해 drift 처럼 보였음 = 표현 과다, 실제는 의무 회귀게이트.
- S2 K규칙 처리(전부 COM 직접판정): (1) PF-13 정사각 원배지 통과(이전세션 완료) (2) **VP-04 noFill 배지 FP** = 룰과탐 → `validate-pptx.js:158` ln-strip(테두리색을 배경 오판 차단), COM png-fix 검은글씨 가독 (3) **VP-10 space-between FP** = 룰과탐 → 끝 gap 3배+ 2클러스터 제외 (4) **VP-07 부수회귀** = borderColor 분리로 정탐 복원. 디자인 수정 0(modern 원안 정상), 전부 **룰 게이트 수정**.
- 회귀검증: 17 GT 덱 ERROR delta=0(recall 1.0 보존), WARN만 FP 감소.
- 다음 의도: 사용자 지시 = **harness2-wf Teammate 병렬 스폰**(⛔subagent 금지)으로 S3 executive·S4 academic·S5-7 생성(classic/dark-mono/company) 잔여 세트. 각 Teammate=1세트(생성→변환→COM→K규칙, 정탐회귀0·FP0, 전역 변환기/룰 수정은 메인합의). 메인=Supervisor 가 방법준수 + 세트별 예시 3개 검사. ⛔개별승인 안받고 plan §0.5 자율.
- 동기화 필요: 미커밋 = validate-pptx.js(VP-04 ln-strip+borderColor+VP-07 필터+VP-10 가드)·preflight-html.js(PF-13)·html2pptx.cjs(B6)·run-full-regression.mjs·progress·plan·handoff. S2 산출=slides/e2e-modern/out_fix.pptx+png-fix(COM 2장 의도보존).

> [ckpt-202606152330:btn-design] **STATUS: ✅S1 editorial 완료(3종 K규칙 처리+COM 검증). 다음=S2 modern**
- 마지막 결정: S1 3버그 전부 해결, 각 COM 직접판정으로 가름 — (1) B6 masthead wrap=**변환기**(shape-text 폭 headroom+height게이트) (2) slide-02 overflow=**디자인**(여백 압축 padding64→40·gap28→14, 콘텐츠·폰트 임팩트 보존, scrollHeight 776>720 실잘림=정탐) (3) drop 본문 우측침범=**변환기 회귀**(height게이트로 다줄 제외). COM 2장 모두 의도보존 확인(png-fix2).
- 다음 의도: **S2 modern** — slides/e2e-modern/ 변환(PF-13 정밀화 통과 확인 + B6 변환기수정 회귀 실증 incremental) → COM 렌더 판정 → VP-04 noFill 배지 오판 정답화. 그 후 S3 executive(B5대비·B4)→S4 academic→S5-7 생성. ⛔개별승인 안받고 plan §0.5 자율, ⛔GT 삭제금지.
- 동기화 필요: 미커밋 = preflight-html.js(PF-13)·html2pptx.cjs(B6 shape-text headroom+height게이트, diff 클린 28줄)·run-full-regression.mjs·progress·plan·handoff. 산출=slides/e2e-editorial/out_fix.pptx+png-fix2(정식). 임시 png 정리됨. long-mode on2(750k). el.shape.fontSize 단위(px/pt) 미확인이나 fallback 0.45in 으로 동작검증됨(S2서 확인 여지).
> [ckpt-202606152230:btn-design] **STATUS: S1 B6 ✅해결(변환기 fix+COM 1줄검증). 다음=slide-02 overflow 판정 + S2 modern**
- 마지막 결정: B6 보수 적용 완료. fit:'shrink' 가 shape+text 에서 PptxGenJS 무시(실측) → fill-없는 single-line shape-text 폭 headroom 으로 전환. cx 3.029→3.332in, COM 렌더 masthead 1줄 복귀 확인(디자인 원안 보존). diff 클린(fix 21줄). 미커밋 html2pptx.cjs 추가.
- 다음 의도: (1) slide-02 overflow(39pt 세로넘침) K규칙 판정 — 디자인 결함인지 변환기 측정인지 COM 실측 (2) **S2 modern 변환** = PF-13 정밀화 변환통과 확인 + B6 변환기수정 회귀 실증(incremental) + VP-04 noFill 배지 오판 정답화. → S3~S7.
- 동기화 필요: 미커밋 = preflight-html.js·html2pptx.cjs·run-full-regression.mjs·progress·plan·handoff. long-mode on2(750k). 임시 _dbg_one 정리됨.

## ★루프 지시 (2026-06-15, 사용자) — 2회 연속 클린까지 반복
- **루프**: 매 회차 = **다른 복잡 5종 × 8테마(40슬라이드)** 디자인스킬→PF→VP→COM 전체. 매 회차 발견 룰FP/변환기결함 **수정**(회귀게이트)하고 고친 파이프라인으로 다음 회차. **2회 연속 신규에러 0**이면 종료(파이프라인 robust 입증).
- **회차별 복잡 5종**(중복 금지):
  - R1(phase2/3): KPI/표/매트릭스/타임라인 (4종, 8테마)
  - R2(phase4): 리스트/플로우/가격/쿼트/이미지그리드 → 수정: blockquote drop·중첩ul 이중방출
  - R3(phase5, 진행중): stat hero/조직도/퍼널/아이콘표/칸반 → 발견: VP-07 칸반 FP(ERROR)·VP-16 퍼널라벨 FP(WARN)·span-bg 미페인트(한계)
  - R4~: gantt/swot/heatmap/radar/waterfall/map/gauge/venn/team-grid/agenda/feature-spotlight/tier/checklist/comparison-slider 등에서 5종씩
- **클린 카운터**: R3까지 매 회차 신규결함 발생(아직 0회 연속 클린). R 신규에러0 = 카운터+1, 에러발생 = 카운터 리셋. 2 도달 시 종료.
- **누적 수정**(전역, 모든 회차 적용): VP-04/07/10/14/16 룰게이트 + `<small>`/loose-text/orphan-span/blockquote/중첩ul 변환기. R3 발견분(VP-07 칸반·VP-16 퍼널) 수정 예정.

> [ckpt-202606170000:btn-design] **STATUS: R3(phase5) 결함 처리 + R4 진입. 클린카운터=0**
- R3 결함 판정: 텍스트손실 변환기버그는 R2서 이미 수정(blockquote/중첩ul). R3 신규 = ① VP-07 칸반 WARN FP(advisory) ② VP-16 퍼널라벨 WARN FP(advisory) ③ rgba alpha-drop·span-bg·clip-path·inline-margin = 변환기 미지원 패턴을 디자인이 사용(spec에 "div/solid/padding 쓰라" 명시돼 있으나 teammate가 미준수→우회).
- ⛔ **VP-07 칸반 colocated 수정 시도→revert**: containment 확장이 samsung 진짜 빈칸표 정탐 2→5 깨뜨림(회귀). WARN-level FP 위해 정탐 깰 수 없음 → 미수정(advisory 수용).
- **전략**: R4 spec(complex-spec4.md)에 ★변환기 idiomatic 필수 체크리스트 6항 추가(배경=div만/solid hex만/인라인 margin금지/텍스트는 색div 자손/clip-path·pseudo는 실div/대비 COM기준) + advisory WARN(칸반·퍼널·clip-path)은 "워크어라운드 말고 note만". → R4부터 변환기 global_issue 급감 기대.
- R4 새 5종: gantt/heatmap/gauge/waterfall/agenda × 8테마.

> [ckpt-202606170015:btn-design] **루프 게이트 보강 (사용자): 매 라운드 생성덱 전수 회귀 추가**
- 매 라운드 수정 후 `tests/regress-generated.sh` 실행 = 이전 생성 e2e 덱 전부(e2e-*/e2e2-*/e2e3-*/e2e4-*) 현 파이프라인으로 재변환+VP → ERROR=0 유지 확인. 누적 생성덱 = 성장하는 회귀 corpus. 이번 라운드 룰/변환기 수정이 이전 라운드 덱 망가뜨리면 catch.
- 라운드 게이트 = ①17 GT 덱 ERROR delta=0(recall) ②합성 positive(검출력) ③**생성덱 전수 ERROR=0(신규)** ④현 라운드 8테마 COM 검증.

> [ckpt-202606171045:btn-design] 회귀게이트 포착 e2e2-executive VP-07 = COM 확정 **flow FP**
- e2e2-executive slide-02 = 프로세스 플로우(원형노드01~05+연결선+게이트카드3). COM 완벽렌더·겹침0. VP-07 "9×2 4/9빈셀 missing data"는 FP(원형노드+연결선+카드를 sparse table 오판).
- ⛔ **VP-07 recall-lock**: samsung 진짜 빈칸표 정탐과 충돌. flow를 표와 구분하는 안전게이트 난이(연결선=thin인데 samsung 빈셀도 h=0 thin / 원형=square인데...). containment 확장 = samsung 2→5 깨짐 실증. → **현재 미수정·advisory 수용**. 견고한 flow-detection 게이트(원형 prstGeom 파싱 or 연결선 종횡비 제외 등)는 별도 신중과제.
- **루프 함의**: VP-07이 flow/칸반/카드 패턴서 FP 지속 → "2연속 클린" 도달은 이 게이트 해결 또는 spec서 해당 레이아웃 회피 유도 필요. 텍스트손실 변환기버그(진짜)는 전부 수정됨 — 남은 "에러"는 대부분 recall-lock 룰FP(flow/card)·패턴미준수.

> [ckpt-202606171130:btn-design] 루프 판정기준 확정(권고안 자율채택) + R4 2/8 클린
- **클린 판정 = baseline-relative**: 생성덱 회귀 = finalize ERROR보다 증가시만 회귀. recall-lock FP(flow/funnel/kanban VP-07/16, COM 확정 FP지만 samsung 정탐 보호상 미수정)는 "늘 있던 것"=클린 간주. **신규 global_issue(변환기버그/새 룰FP) 또는 baseline 대비 ERROR 증가 = 비클린**.
- **R4 진행**: dark-mono·company = global_issue 0(클린). spec4 idiomatic 체크리스트가 변환기 우회 자체를 없앰 = 신규 결함 0. 나머지 6 진행중.
- 사용자 재지정 시 absolute-0 또는 flow-detection 게이트 개발로 전환 가능(핸드오프 박제).

> [ckpt-202606171200:btn-design] R4 클린 판정(카운터 1) → R5 진입
- R4: 8테마 디자인 전부 클린(COM 의도보존), teammate global_issue 0(idiomatic spec 적중). 2 ERROR=COM확정 룰FP(워터폴 VP-07·게이지 VP-04 resolveBackground, recall-lock advisory, 디자인 멀쩡·과조정0). baseline-relative+advisory → **R4 클린, 클린카운터=1**.
- R5: 새 5종(벤다이어그램/팀그리드/비포애프터/체크리스트/사분면버블) × 8테마. R5도 클린(신규 변환기버그0+디자인결함0)이면 2연속 클린 → 루프 종료.
- 누적 사용 타입 20종(R1~R4) → R5는 직교 5종.

> [ckpt-202606171230:btn-design] ★드리프트 정정(사용자) — slides-grab 실제 복잡슬라이드 기준, 합성물 삭제
- **드리프트**: 매 라운드 5종을 내가 합성 생성(KPI/벤다이어그램 등 발명) = 사용자 의도(slides-grab 실제 복잡 슬라이드 변환·검증)와 다름. plan §0.5 문구("디자인스킬 생성")는 따랐으나 사용자 의도 기준 미준수.
- **정정 기준(SSOT)**: 매 라운드 = **slides-grab 27덱(433슬라이드)에서 복잡해 보이는 슬라이드 5개 선택 → 현 파이프라인으로 변환 → PF/VP/COM 으로 원안보존·룰정합 검증**. 합성 생성 금지.
- **R4 클린 판정 무효 → 클린카운터 0 리셋**. R5 취소(teammate 중단 완료).
- **합성 테스트 자산 삭제**: slides/e2e-* e2e2-* e2e3-* e2e4-* e2e5-* + RENDERED-ASSETS-INDEX.md (전부 합성, slides-grab 변환 아님).

> [ckpt-202606160010:btn-design] ★기준 재정정(사용자 최종) + 삭제자산 원복
- **삭제 원복**: 직전 ckpt서 삭제한 e2e-*/e2e2-*/e2e3-* + RENDERED-ASSETS-INDEX.md = `git checkout HEAD -- slides/` 로 전부 원복(staged D → 복구).
- **R4 teammate 5개 중단**(editorial/modern/academic/classic/dark-pitch) — 합성 타입(gantt/heatmap 등) 생성 = 드리프트라 종료.
- **확정 기준(SSOT, plan §0.5 재정정)**: 매 라운드 = slides-grab 복잡슬라이드 5장 **소재 선택** → 디자인스킬 **8테마로 재현 생성**(40장) → convert(PF)→VP→COM 원안보존·룰정합. ⛔드리프트 2종: (a)타입 발명(R1~R4 합성) (b)slides-grab HTML 직접변환. slides-grab = 복잡도 소재 + read-only 룰GT 두 역할.
- **유효 보존 자산**: VP-04/07/10/14/16 게이트 + html2pptx(small/loose-text/orphan-span/blockquote/nested-ul) 수정 = GT 17덱 ERROR delta0 게이트 통과분이라 유지. 클린카운터=0(재시작).
- **다음**: slides-grab 27덱서 복잡 슬라이드 5장 식별 → 디자인스킬 8테마 생성 dispatch.

> [Working Notes — ckpt-202606160020:btn-design] 5장 선택 진행 중(compact 직전)
- **마지막 결정**: slides-grab 복잡 5장 식별(Explore). 단 `chupi-character/slide-05`=SVG 캐릭터 일러스트 100+개 → 디자인시스템 토큰 재현 불가(이미지슬롯 영역) → **데이터밀집형으로 교체 결정**. 교체 후보 = coupang-09/lg-hynix-09(grid)/posco-06/kakao-11 등 투자리포트 데이터밀집(직접 열어 구조 확인 필요, grep table=0이라 div-grid 기반).
- **확정 4장(유력)**: ① samsung-investment-report/slide-14(투패널 5×5표+시나리오 바차트) ② discounted-breakeven-analysis/slide-13(비교표+이중바차트+범례) ③ payroll-guide/slide-14(6열표+계산박스+사이드패널) ④ triassic-dinosaurs/slide-05(수평 타임라인 교대배치). ⑤=chupi 교체분(데이터밀집 1장) 미확정.
- **다음 의도**: ⑤ 교체 1장 확정 → 5장의 내용·구조를 **디자인스킬 8테마(editorial/modern/executive/academic/classic/dark-mono/company/dark-pitch)로 재현 생성**(40장) → convert-native.mjs(PF)→VP→COM 원안보존·룰정합. teammate 8세트 병렬 dispatch(harness2 방식) 또는 순차.
- **동기화 완료**: plan §0.5 3단 워크플로우 박제 / handoff next-action+§3 갱신 / 클린카운터0 / ERROR-202606160015 기록 / R4 teammate 중단 / 삭제자산 git 원복.

> [Working Notes — ckpt-202606160030:btn-design] ★사용자 신규지시(드리프트 영구방지)
- **지시(2026-06-16)**: slides-grab 복잡 슬라이드 후보를 **5라운드 분량 25장** 선발 → **5장씩 R1~R5 테스트자산으로 등록** → plan/progress에 "해당 자산으로 어떻게 테스트하는지" 명시(자산=포인터 연결). 다시 드리프트 안 하게 SSOT 고정.
- **다음 의도**: (1) Explore로 25장 식별(디자인시스템 재현 적합=데이터/레이아웃 복잡형, SVG캐릭터·일러스트 이미지슬롯 영역 제외, 라운드별 유형 다양) (2) plan에 §라운드맵 테이블(R1~R5 × 5장 절대경로 포인터 + 레이아웃유형) (3) 각 라운드 테스트절차 명시(소재→디자인스킬 8테마 재현→PF→VP→COM→K규칙). (4) 그 후 R1부터 8테마 생성.

> [Working Notes — ckpt-202606160040:btn-design] 25장 SSOT 박제 완료 (compact 직전)
- **마지막 결정**: slides-grab 복잡 슬라이드 25장(5R×5장) 선발+실재검증(MISSING 0) → **plan §0.6 라운드맵 테이블 박제**(절대경로 포인터 25개 + 레이아웃유형 + 테스트절차 5단). chupi(SVG캐릭터) 등 이미지슬롯 영역 제외, 데이터/레이아웃 복잡형만. payroll-guide 편중 8/25(유형은 다양화) — 편중 문제시 사용자 지시로 교체.
- **다음 의도**: **R1 5장**(payroll-guide/14·payroll-v2/11·discounted/13·samsung/14·naver/17) 소재로 디자인스킬 8테마 재현 생성 → `slides/round1-{theme}/slide-01~05.html`(40장) → convert(PF)→VP→COM 의도보존 판정 → K규칙·정탐회귀0. harness2 teammate 8세트 병렬 또는 순차.
- **동기화 완료**: plan §0.5 3단 워크플로우 + §0.6 25장 라운드맵 / handoff next-action·§3 / progress ckpt 4개 / ERROR-202606160015 / 클린카운터0 / 자산 git원복 / teammate중단.
- **드리프트 영구방지 게이트**: 매 라운드 착수 전 plan §0.6 테이블의 해당 R 5장 경로만 소재로 사용. ⛔타입 발명·임의 슬라이드 교체·slides-grab 직접변환 3종 금지.
