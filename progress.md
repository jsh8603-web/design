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
