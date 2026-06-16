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
| **R9** | `slides/round9-{theme}/` | 8 | coupang/09·payroll-guide/30·11·32·payroll-v2/20(02목차 교체) | ✅ 완료(8테마 ERROR0+6계열 COM 의도보존+정탐회귀0). 플라이휠다이어그램·2컬럼step·5열10행누적표·5단계체크리스트+다크타임라인·heroKPI+시뮬표. ★신규결함2 수정: slide05 좌우분리head flex겹침(VP-14)→명시width / slide01 대각선화살표글리프(↘↗ 폰트폴백깨짐)→직교화살표 |
| **R10** | `slides/round10-{theme}/` | 8 | payroll-v2/30·payroll-guide/09·41·samsung/06·discounted/11 | ✅ 완료·**클린아님**(결함 발견·수정 라운드, 8테마 ERROR0). 2컬럼step·2x2위반카드·Q&A+다크공식+민감도표·점유율누적바+4×5표·4step+5행비교표. ★재구성2(도넛SVG→누적바+KPI / 이미지슬롯→다크요약패널)=토큰범위내. ★드리프트 자해+원복: executive navy 다크패널 저대비에 `--accent-on-dark` 토큰 발명→사용자 지적("스킬 개조=드리프트")→전량 원복. ★①규약준수수정: 근본=슬라이드가 prompting_rules §4.3(다크는 fg, 라이트색 다크금지) 위반→다크패널 강조 accent→surface-inverse-fg+weight(라이트영역 색강조 유지). 디자인시스템 무개조. 과거 R1~R10 드리프트 0건(subagent 전수검토). **클린카운터 0 유지**(결함수정 라운드) |
| **R11** | `slides/round11-{theme}/` | 8 | seoul/29·tax-jv/16·payroll-guide/28·samsung/11·payroll-v2/34 | ✅ 완료·**클린아님**(결함 발견·수정, 8테마 ERROR0). SWOT 2x2·5단계프로세스·인건비α계수9행표·삼성vsSKH 7행비교표·1~6월 일정표. ★slide-04 투자시사점 카드 itext `nowrap`→변환기 인라인 겹침→nowrap제거+flex column 해결(K-202606161200). SEC 의미색 navy→cobalt#2563EB(다크테마 안전). 다크패널 강조=fg+weight(①학습). **클린카운터 0** |
| **R12** | `slides/round12-{theme}/` | 8 | payroll-guide/10·payroll-v2/17·samsung/12·payroll-guide/07·payroll-guide/13 | ✅ 완료·**클린아님**(결함 발견·수정, 8테마 ERROR0). 누적비율9행표+스택바·일용vs상용8행표·듀얼패널비교표·최저임금3패널·4대보험5×5표+다크계산패널. ★Read검증서 02목차→10·15디바이더→13 교체. ★slide-01 색칩 라벨좌/값우 양끝정렬: flex space-between 변환기 미지원→grid 2컬럼+자식 block(p) 전환 해결(K-202606162210). 변환기·룰 무수정→정탐회귀0. **클린카운터 0** |
| **R13** | `slides/round13-{theme}/` | 8 | payroll-guide/22·payroll-v2/19·samsung/13·payroll-guide/27·payroll-guide/23 | ✅ 완료·**클린아님**(결함 발견·수정, 8테마 ERROR0). 퇴직금공식+산입6행표+계산패널·BEFORE/AFTER+영향표+재무패널·hero KPI+타임라인+불릿·인건비공식+요율8행표+계수표+5배지·DBO 3박스+2표+인사이트3카드. ★FAILED2건 슬라이드수정: slide-01 결과텍스트 바닥경계 0.49"(<0.5") → body pad-bottom 30→42px+calc margin 축소 / slide-05 `.imp-note` **p에 border-top**(변환기 div만 지원) → div>p 분리(K-202606162310=학습⑮). 변환기·룰 무수정→정탐회귀0. **클린카운터 0** |
| **R14** | `slides/round14-{theme}/` | 8 | payroll-guide/29·payroll-v2/22·samsung/15·payroll-guide/33·payroll-guide/24 | ⚠️ 생성완료·**클린철회**(변환 ERROR0/FAILED0이나 풀사이즈 재검증서 결함 발견). 정산 3패널·DB/DC 비교+선택가이드·막대차트+부문표+Catalyst·월별타임라인+체크리스트·계리 4단계. ★**결함**: slide-02 우 가이드 다크패널 긴텍스트(.g-d/.g-note) **패널 우측경계 잘림**(8테마 공통, 변환기 parentShape clamp 포함체크 미통과 의심 html2pptx.cjs:532). ★검증오류: 다크2/exec/edit를 360px 몽타주로만 봐 놓침→풀사이즈 재검증 필수. **클린카운터 0**(R14 결함→리셋). 수정+R13 재검증 후 재판정 |
| R15 | `slides/round15-{theme}/` | 8 | 미정(plan §0.6: PG-36/05·PV-23/35·SS-08, 착수 Read검증) | ⏳ 예정 (R15 클린 시 **2연속=루프종료**) |

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
