---
title: 디자인 스킬세트 렌더 자산 인덱스 (한곳 모음)
tags: [index, design-system, rendered-assets, e2e, btn-design]
date: 2026-06-15
---

# 디자인 스킬세트 렌더 자산 — 전수 인덱스

> 디자인 스킬(design-system)로 생성한 슬라이드 → PPTX 변환 → COM 렌더한 **모든 자산**을 한곳에 정리. 각 덱 = `slide-NN.html`(원안) + `out_fix.pptx`(변환) + `png-fix/slide_NN.png`(COM 300DPI 렌더). 프로젝트 루트 = `D:/projects/design`. 모든 경로 = repo 상대.

## A. 정식 검증 라운드 (slides-grab 복잡슬라이드 5장 → 디자인스킬 8테마 재현)
★워크플로우(plan §0.6 SSOT): 매 라운드 = slides-grab 복잡 5장 **소재 선택** → 디자인스킬 8테마 **재현생성**(40장) → preflight 포함 변환 → VP → COM 의도보존. ⛔타입발명 금지·⛔slides-grab HTML 직접변환 금지.

| 라운드 | 디렉토리 패턴 | 테마 | 소재 5장(slides-grab) | 상태 |
|---|---|---|---|---|
| **R1** | `slides/round1-{theme}/` | 8 | payroll-guide/14·payroll-v2/11·discounted/13·samsung/14·naver/17 | ✅ 완료(8테마 ERROR0+COM의도보존+정탐회귀0) |
| **R2** | `slides/round2-{theme}/` | 8 | payroll-guide/04·payroll-v2/07·kakao/07·payroll-guide/12·lg-hynix/09 | ✅ 완료(8테마 ERROR0+COM의도보존+정탐회귀0). VS비교·4열표·컬러도트매트릭스·투패널KPI·투패널타임라인 |
| **R3** | `slides/round3-{theme}/` | 8 | payroll-guide/06·payroll-guide/08·discounted/18·payroll-guide/10·coupang/08 | ✅ 완료·**첫클린**(8테마 ERROR0 첫시도+COM의도보존+정탐회귀0). 프로세스흐름·navy패널detail·토네이도차트·워터폴·metric그리드 |
| **R4** | `slides/round4-{theme}/` | 8 | payroll-v2/15·payroll-v2/13·triassic/05·samsung/16·tax-jv/04 | ✅ 완료(8테마 ERROR0+COM의도보존+정탐회귀0). 8열계산표·5열비교표·수평타임라인(교대)·리스크매트릭스·JV비교표. ★매트릭스=변환기 flex칩 겹침→표셀패턴 재설계로 해결 |
| **R5** | `slides/round5-{theme}/` | 8 | payroll-guide/20·31·35·space-resource/02·ai-infra/09 | ✅ 완료(8테마 ERROR0+COM+정탐회귀0). KPI+시나리오표·step+환급표·차트복합·타임라인+표·월별캘린더. ★연한톤bg고정hex 다크충돌→테마토큰 수정 |
| **R6** | `slides/round6-{theme}/` | 8 | apartment/06·posco/07·space-economy/03-newspace·apartment/10·global-space/08 | ✅ 완료(8테마 ERROR0+COM+정탐회귀0). 권역비교표·재무추이표·투패널비용+stat·정책카드·outlook카드. ★배지/태그 span→div>p+nowrap 수정 |
| **R7** | `slides/round7-{theme}/` | 8 | payroll-v2/28·posco/12·naver/15·payroll-v2/31·payroll-guide/17 | ✅ 완료(8테마 ERROR0+FAILED0+COM+정탐회귀0). 요율표+계수·리튬현황표·재무전망표·KPI+step+표·일용vs상용 12행표. ★slide-05 720초과 silent drop→높이축소 수정 |
| **R8** | `slides/round8-{theme}/` | 8 | manuf-kpi/03·payroll-v2/14·payroll-guide/19·34·13 | ✅ 완료(8테마 ERROR0+FAIL0+COM의도보존+정탐회귀0). PQCD색아이콘카드·6열표·BEFORE/AFTER+영향표·9행캘린더·요율표+calc. ★변환기수정(정사각아이콘 table-column 오인→텍스트겹침 해결)+학습8(색칩=div직속텍스트, invisible방지)+학습9(불릿=단일p) |
| R9~R10 | `slides/round{N}-{theme}/` | 8 | plan §0.6 표 참조 | ⏳ 예정 |

**테마 목록**(8): editorial(Track B serif) · modern · executive(executive-editorial) · academic · classic · dark-mono · company · dark-pitch.
- 각 덱 COM 렌더 위치: `slides/round{N}-{theme}/png/slide_01.png ~ slide_05.png`.

### R1 결과 (2026-06-16)
- 8테마 전부 convert ERROR=0 + COM 의도보존 확인. dark-mono ERROR88 fix(텍스트 `color:var(--primary)`→`var(--heading, var(--primary))`, primary==bg 1.00:1 정탐 = 디자인수정, 룰 무수정).
- 정탐회귀 0: GT 17덱 정상파이프라인(preflight포함) ERROR=0. ★`--skip-preflight` 변환은 preflight 자동보정 빠져 VP-04 오탐 → 회귀측정 시 preflight 포함 필수.

## A-구. ⛔폐기대상 — 구 드리프트 라운드 (타입발명, 사용자기준 위반)
> `slides/e2e-*`·`e2e2-*`·`e2e3-*`·`e2e4-*` = 이전 세션 드리프트 산출물. 임의 타입(KPI/간트/히트맵/게이지/워터폴/퍼널 등) 발명 = 사용자기준("slides-grab 복잡슬라이드 재현") 위반. **검증대상 아님·정식자산 아님**. 자체결함 ERROR 잔존(e2e2-executive VP-07·e2e4-dark-pitch VP-04 등 = 진짜정탐). regress-generated.sh가 아직 이것들 스캔 → baseline 재정의 필요(round1-* 포함). 삭제 여부 = 사용자 확인 대기.

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
