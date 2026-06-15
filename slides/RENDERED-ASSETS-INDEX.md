---
title: 디자인 스킬세트 렌더 자산 인덱스 (한곳 모음)
tags: [index, design-system, rendered-assets, e2e, btn-design]
date: 2026-06-15
---

# 디자인 스킬세트 렌더 자산 — 전수 인덱스

> 디자인 스킬(design-system)로 생성한 슬라이드 → PPTX 변환 → COM 렌더한 **모든 자산**을 한곳에 정리. 각 덱 = `slide-NN.html`(원안) + `out_fix.pptx`(변환) + `png-fix/slide_NN.png`(COM 300DPI 렌더). 프로젝트 루트 = `D:/projects/design`. 모든 경로 = repo 상대.

## A. 검증 라운드 덱 (이번 세션 + dark-deck) — HTML→PPTX→COM 전 과정
복잡 슬라이드 5종씩 × 테마, 매 라운드 다른 5종. 디자인스킬→PF→VP→COM 검증·정합.

| 라운드 | 디렉토리 패턴 | 테마 수 | 복잡 슬라이드 5종 | 자산(덱당) |
|---|---|---|---|---|
| R0(이전세션) | `slides/dark-deck/` | 1(dark-pitch) | 표지+히어로+KPI+콘텐츠(4장) | slide-01~04.html · dark.pptx · pptx-png/ |
| R1 | `slides/e2e-{theme}/` | 8 | 표지/KPI/표/매트릭스/타임라인 | slide-01~05.html · out_fix.pptx · png-fix/ |
| R2 | `slides/e2e2-{theme}/` | 5 | 리스트/플로우/가격카드/풀쿼트/이미지그리드 | slide-01~05.html · out_fix.pptx · png-fix/ |
| R3 | `slides/e2e3-{theme}/` | 8 | stat-hero/조직도/퍼널/아이콘비교표/칸반 | slide-01~05.html · out_fix.pptx · png-fix/ |
| R4 | `slides/e2e4-{theme}/` | 8 | 간트/히트맵/게이지/워터폴/아젠다 | slide-01~05.html · out_fix.pptx · png-fix/ |

**테마 목록**(8): editorial · modern · executive(executive-editorial) · academic · classic · dark-mono · company · dark-pitch.
- R2는 5테마(editorial/modern/executive/dark-mono/company), 나머지 라운드는 8테마.
- 합계: **30 덱, ~145 슬라이드 HTML, 29 PPTX, ~137 COM PNG**.
- 각 덱 COM 렌더 위치: `slides/{덱}/png-fix/slide_01.png ~ slide_05.png` (dark-deck/e2e-academic은 `pptx-png/`).

### 라운드별 결과 요약
- R1: 8테마 전부 ERROR=0(수정후). 룰FP 다수 수정(VP-04/07/10/14/16), B6 masthead.
- R2: blockquote drop·중첩ul 이중방출 변환기버그 발견·수정.
- R3: VP-07 칸반·VP-16 퍼널 WARN FP(advisory), span-bg/rgba 패턴.
- R4: 6/8 ERROR=0. classic(워터폴 VP-07)·dark-pitch(게이지 VP-04) = COM 확정 룰FP(디자인 멀쩡, recall-lock 미수정). spec idiomatic 강화로 변환기 global_issue 0.

## B. 이전 세션 design-system 원본·참조 (디자인스킬 소스 템플릿)
| 자산 | 위치 | 내용 |
|---|---|---|
| 레이아웃 템플릿 10종 | `design-system/slides/*.html` | cover/content/contents/quote/section-divider/split-layout/statistics/team/timeline/closing |
| 테마 aesthetic 참조 | `design-system/aesthetics/{01-executive,02-dark-pitch,03-academic,04-editorial}/*.html` | 테마별 cover·kpi 레퍼런스(20 HTML) — R1 e2e- 생성의 원본 |
| 밀집 테스트 | `slides/mock-dense/*.html` (6장, PPTX 없음, png-fix/ 프리뷰) | 이전 세션 밀집 레이아웃 테스트 |

## C. GT(검증대상 아님 — 참고용 경계 명시)
- `D:/projects/slides-grab/slides/` (27덱) = PF/VP 룰 정답화 **read-only GT**. ⛔디자인스킬 산출 아님·삭제금지·검증대상 아님. 본 인덱스 A/B 만 디자인스킬 자산.

## 변환·렌더 재현 명령
- 변환: `"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/{덱} --output slides/{덱}/out_fix.pptx`
- COM 렌더: `powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\projects\design\slides\{덱}\out_fix.pptx" -OutputDir "D:\projects\design\slides\{덱}\png-fix"`
- 생성덱 전수 회귀: `bash tests/regress-generated.sh`
