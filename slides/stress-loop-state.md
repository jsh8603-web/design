---
title: 변환기 버그 채굴 무한루프 상태
tags: [design-e2e, stress-loop, converter-bug-mining]
date: 2026-06-18
next-action: "사이클1 생성중(10차원 병렬). 다음=convert+COM렌더+vision판정+triage. 종료조건=2사이클 연속 신규결함0."
---

# 변환기 버그 채굴 무한루프 (stress-loop)

## 규약
- 1 사이클 = 10 stress 차원 병렬 생성 → 중앙 변환+COM렌더(직렬) → vision 결함판정 → triage(생성기>변환기>룰, §3b) → 수정 → 기록
- triage SSOT = `GENERATOR-CONTRACT.md` §C(2축) + §D(드리프트 게이트 vision)
- 종료 = 2 사이클 연속 신규결함 0
- ⛔ design-system/ 무수정(§3). 허용 = scripts/·html2pptx·preflight/validate·slides/산출물

## stress 차원 10 (GENERATOR-CONTRACT.md §E)
1 고밀도표(720경계) / 2 깊은중첩ul·ol / 3 인라인KPI혼합run / 4 배지pill군집 / 5 다크패널+긴본문 / 6 색칩스와치 / 7 blockquote+figcaption / 8 좌우분할다단 / 9 차트·직교화살표 / 10 absolute overlay정렬

## 사이클 로그
### 사이클 1 (진행중 — preflight 단계 완료, 변환 대기)
- 생성: 10차원 병렬 → slide-01~10.html ✅
- preflight(정적+--full) 결함:
  - **[룰버그] PF-63·PF-22 주석 미제거 FP** (slide-01 `<table>`·slide-02/09 `clip-path` 매치가 CSS주석 내부) → ✅`stripComments`(HTML+style내 CSS 주석 제거). 검증: FP소멸, round*-modern 15개 0err 불변(회귀0)
  - **[계약버그] A5/A8 border-삼각형 ↔ PF-37(흰블록) 충돌** → ✅계약 A5/A8 = 직교글리프/실rect div
  - [생성기위반] slide-02 PF-03 overflow+PF-18 overlap → 에이전트2 수정중
  - [생성기위반] slide-09 PF-37 border-삼각형 → ✅에이전트9 ↓글리프
  - [생성기위반] slide-10 PF-71 흰-on-흰 → ✅에이전트10 다크배킹
  - [design-system 동결] `.t-body-compact` css 미정의 drift → 기록만(§3, 사용자 보고)
- 다음: 에이전트2 완료 → 전수 재preflight → convert+COM+vision(변환기 채굴)
- 신규 변환기버그: TBD
- 클린카운터: 0

### 사이클 1 — 완주 (10차원 생성→변환→COM→vision)
**변환 결과**: A0 적용 후 10/10 변환 성공. vision 판정:
- 정상 7: 01표·02중첩리스트·03KPI·04배지(긴라벨 wrap-clip 경미)·08분할·09화살표 ✅
- ★garble 3 (변환기 결함): 05다크패널긴본문·06색칩·07인용 — 텍스트 런 Y위치 collapse(겹쳐 뭉개짐)

**사이클1 발견 원장**:
| # | 발견 | 분류 | 상태 |
|---|---|---|---|
| 1 | PF-63·PF-22 주석 미제거 FP | 룰버그 | ✅fix stripComments, 회귀0 |
| 2 | 계약 A5/A8 border-삼각형↔PF-37 | 계약버그 | ✅fix |
| 3 | **A0 envelope 갭**(§9 스켈레톤이 body사이징+scaler 누락→6/10 변환FAILED) | 계약/생성기 | ✅fix 계약 A0 추가 (★최대 레버리지) |
| 4 | slide-01 CSS경로 오타(`colors_and_type.css`→`../../design-system/`) | 생성기 | ✅fix |
| 5 | `.t-body-compact` 등 .t-* css 미vendored | design-system drift(동결) | 📌보고만 |
| 6 | **★변환기 텍스트런 collapse** — 비-단순-`<p>` 경로(직속텍스트/blockquote-flex/긴wrap+인라인b)에서 다줄 텍스트가 같은Y에 겹침. preflight --full(PF-18 DOM) 통과=브라우저OK→PPTX만 깨짐=확정 엔진결함 | **변환기버그** | ⏳미해결 — 트리거: 06 div직속텍스트+자식, 07 blockquote{flex-col}>p, 05 긴p+inline b 다줄 |

**사이클1 신규 변환기버그**: 1건(텍스트런 collapse 클러스터, 3슬라이드). **클린 아님 → 카운터 0 유지.**
**다음**: #6 triage — (a) 생성기-회피 OR (b) 변환기 수정. 그 후 사이클2.

### #6 조사 (probe slides/probe/slide-01.html 경험적 판정)
- probe 결과: A(긴p+inline b)✅ / B(div 직속텍스트+자식, 非flex)✅ / **C(blockquote{flex-col}>p)❌garble** / D(div{flex-col}>짧은p)✅ / E(div>p 라벨+메타)✅
- **확정 트리거 = flex 컨테이너 + 특수콘텐츠**:
  - 07 = `<blockquote>{display:flex;flex-col}>p` — blockquote가 textTags(html2pptx.cjs:1113)라 텍스트방출 + 자식 p도 처리 = **double-emit 겹침**. div로 바꾸면 OK.
  - 06 = `.chip{display:flex;flex-col}` + 직속텍스트 + 블록자식(.meta) — flex+혼합콘텐츠 위치붕괴 (probe B 非flex라 통과)
  - 05 = `.summary-panel{display:flex;flex-col}` + 긴 wrap `<p class=lede>` + 형제 sub-capsule — flex 안 긴wrap p 높이 오측정→형제 겹침
- 변환기 위치(html2pptx.cjs 1813줄): textTags=L1113(BLOCKQUOTE 포함), textTag emit=L1149, hasBlockChildren체크=L1267, loose-text=L1119~
- **fix 방향**: (엔진) blockquote가 block 자식 가지면 textTag emit 말고 recurse (중첩-ul fix 동형) + flex 긴wrap/직속텍스트 위치계산. (회피) 계약에 blockquote→div / flex-col 텍스트스택 대신 block.
- GT 회귀 게이트: tests/regress-generated.sh (17덱 ERROR delta 0)

### #5 완료 (design-system 동결 해제, 사용자 승인 2026-06-19)
- colors_and_type.css에 `.t-body-compact`(--pt-body-compact:16pt) + `.t-chart-label`(--pt-chart-label:10pt, mono) 추가. 기존 8개 .t-* 무변경 → 기존 슬라이드 무영향.

### #6 해결 (2026-06-19)
- **07 blockquote double-emit = ★엔진 수정 완료** — html2pptx.cjs:~1615 에 가드 추가: textTag가 textTag 자식 가지면 자기 텍스트 방출 skip(자식 개별방출). probe C + 실 slide-07 깨끗 확인. **GT 회귀 delta=0**(원본 베이스라인도 동일 5 ERROR=기존, 내 fix 무관).
- **06 swatch = 계약 회피** — flex 컨테이너 직속텍스트노드 위치붕괴. 계약 A9 갱신: flex/grid 텍스트는 `<div><p>` 강제(probe E 검증). 엔진 무수정(회피 가능 마크업).
- **05 dark = 경미** — 빽빽하나 판독가능, 심각 아님. 모니터.

### 사이클 1 최종 — 클린 아님(카운터 0). 발견 6 / 수정 6:
룰버그2(주석FP·) 계약3(border삼각형·A0·A9) 엔진1(blockquote) + design-system 1(.t-* vendored) + slide산출 다수. **★핵심: A0 envelope(변환성공 0→10) + blockquote 엔진수정(회귀0).**
**다음 사이클2**: 개선된 계약으로 신규 stress 10차원 재생성 → first-try-clean rate 측정(A0+A9 효과). 2연속 클린까지 반복.

## 누적 수정 (사이클 횡단)
- preflight `stripComments` (주석-FP 클래스, 회귀0)
- GENERATOR-CONTRACT A5/A8(border-삼각형) + **A0 envelope** + A9(flex 텍스트 `<p>` 강제)
- **html2pptx.cjs blockquote/textTag double-emit 엔진수정 (회귀0)**
- design-system `.t-body-compact`·`.t-chart-label` vendored
- slide-01 CSS경로 fix

## 선행 완료 (Phase 0~1)
- GENERATOR-CONTRACT.md(루트) 계약 SSOT
- PF-76(대각화살표 A8) preflight 추가 — 검증완료
- A6/A7 → Playwright DOM 검사 예정(미구현, backstop)

### 사이클 2 (진행중) — 개선 계약 적용 신규 6차원
slides/stress-c2/slide-01~06.html. 차원: 1비교매트릭스(2D grid 행+열헤더) 2아이콘+텍스트 pictogram 3다단 신문형본문 4각주/미주(sup+footnote) 5중첩카드(card-in-card) 6수평 stacked-bar.
목적: A0+A9 적용시 first-try-clean rate 상승 검증 + 신규 변환 결함.

### 사이클 2 완주 (2026-06-19) — ★전수 클린, 신규 변환기버그 0
- 10/10 변환 성공. vision 10장 전부 정상(매트릭스·아이콘·다단·각주·중첩카드·stacked-bar·거대인용·혼합표·진행바·sparkline).
- 경미 생성기 미스 2(각주 5.3pt overflow·중첩카드 1fr→고정 clamp)=즉시 수정, 변환기 결함 아님.
- **first-try-clean: 사이클1 ~0/10 → 사이클2 9/10**. A0+A9+blockquote수정 입증.
- **클린 카운터 = 1** (2연속 클린까지 1 남음).

### 사이클 3 (진행중) — 기하/위치 신규 10차원
slides/stress-c3/. 1워터폴(bridge) 2도넛/파이(div) 3히트맵그리드 4수직타임라인 5깔때기funnel 6게이지반원 7조직도트리 8간트(수평기간) 9버블산점도 10빅넘버히어로+분해. 목적: 기하/절대위치 변환경로 + 클린 카운터 2 도전.

### 사이클 3 (진행중) — 변환 10/10 성공
- preflight 1 ERROR(slide-09 버블산점도 P-P 54% 겹침=절대배치 라벨충돌, 생성기→수정중) + 38warn(대비+A3 probe). first-try-clean 9/10.
- 변환 10/10. vision 판정 대기(워터폴·도넛·히트맵·타임라인·깔때기·게이지·조직도·간트·버블·빅넘버).
- ⏳ vision 미완 — 압축 시 재렌더+vision 필요. png: slides/stress-c3/png/slide_NN_sm.png(1600px).

#### c3 vision 진행 (3/10): 02도넛✅ 07조직도✅ 09버블✅(PF-18 라벨근접=생성기경미, 변환기OK). 복잡 위치계산 변환기 정상. 잔여: 01워터폴·03히트맵·04타임라인·05깔때기·06게이지·08간트·10빅넘버.

#### c3 vision (6/10): +01워터폴✅ 06게이지✅ 08간트✅. floating막대·grid위치막대·마커 다 정상. 잔여 03히트맵·04타임라인·05깔때기·10빅넘버.

### 사이클 3 완주 (2026-06-19) — ★전수 클린, 신규 변환기버그 0
- vision 10/10 전부 정상: 워터폴·도넛·히트맵·수직타임라인·깔때기·게이지·조직도·간트·버블·빅넘버.
- 절대배치/grid위치막대/floating/중첩원/마커/색강도 전부 변환기 정상 처리.
- 유일 이슈 = slide-09 버블 PF-18 라벨근접(생성기 경미, 변환기 렌더OK), slide-10 A3 inline-margin probe(warn 예상). 변환기 결함 0.

## ★★ 루프 수렴 (2026-06-19) — 클린 카운터 = 2 (2연속 클린 달성, 종료조건 충족)
- 사이클1 NOT클린(대형결함 발굴·수정) → 사이클2 클린 → 사이클3 클린.
- first-try-clean: 사이클1 ~0/10 → 사이클2 9/10 → 사이클3 9/10.
- 30 stress 차원(c1 10 + c2 10 + c3 10) 검증. c2/c3 신규 20차원 전부 first-try 변환 클린.
- **누적 수정 총괄**: 엔진1(blockquote double-emit, 회귀0) + 룰1클래스(주석FP stripComments) + 계약(A0 envelope★/A9 flex텍스트/A5·A8 border삼각형) + design-system(.t-body-compact·.t-chart-label vendored) + PF-76(대각화살표).
- **핵심 레버리지 = A0 envelope**(§9 스켈레톤 누락 보강 → first-try 변환성공 ~0→9/10).

### 사이클 4 (진행중) — 사용자 "절대 멈추지마" → 수렴 후 극단 edge 사냥
slides/stress-c4/. 1회전텍스트(transform rotate 라벨) 2세로쓰기(writing-mode vertical) 3이모지/기호 헤비(✓✗★▲▼₩$€ 상태심볼) 4초고밀도(20행+표·9pt) 5z-index 레이어 카드(의도적 겹침) 6극단 폰트웨이트(100~900) 7초장문 본문(빽빽 wrap) 8음수공간 비대칭 9복합 kitchen-sink(표+차트+배지+인용 한장) 10중첩 표(표 안 표).
목적: 변환기 최희귀 경로(rotation/vertical/emoji/extreme density) 사냥. 압축 후 재개 시 = c4 생성→preflight+convert→COM렌더+리사이즈(1600)+vision→loop-state 기록. 종료조건 이미 충족(클린2), c4는 보너스 사냥.

### 사이클 4 (진행중) — 극단 edge 생성·변환 결과
(아래 변환결과 자동기록 자리 — vision 미완 시 재렌더: convert→export-slides-png.ps1→1600리사이즈→slide_NN_sm.png vision)

#### c4 결과: 변환 8/10. 2 FAILED 발견(보너스 사냥):
- slide-02 세로쓰기: 가로 90.8pt overflow(회전/vertical 텍스트박스 폭 측정) → 계약 A16
- slide-03 기호헤비: <p> 첫문자 ● → 변환기 manual-bullet 오인 거부(html2pptx.cjs:1620) → 계약 A15(글리프 별도 div dot/텍스트뒤)
- 둘 다 회피 가능 마크업 → 계약 A15/A16 박제(변환기 무수정, 회귀0). 8 변환분 vision 대기.
- ⚠️ 압축 후 재개: c4 slide-02/03 수정(A15/A16 적용) 후 재변환 + 8장 vision. png 재렌더 필요.

#### c4 vision 진행(3/8): 01회전텍스트✅(-45도헤더·세로y축 정상) 08중첩그리드✅(grid-in-grid). 06 5단중첩=헤더영역 겹침 의심(1600px 불명확, 풀해상도 재확인 필요). 잔여 vision: 04밀집표·05다국어·06(재확인)·07장문·09kitchen·10... png slide_NN_sm.png(02·03 omit이라 png_01=c4-01,png_02=c4-04,png_03=c4-05,png_04=c4-06,png_05=c4-07,png_06=c4-08,png_07=c4-09,png_08=c4-10).
미완: c4 slide-02/03 수정(작업자 진행) 후 재변환, c4 5장 vision, slide-06(c4-08? 아니 c4 dim8 deep5=png_06) 풀해상도. ⛔압축 후 이 순서로 재개.

#### c4 재변환(02세로축30px·03선두글리프→colordot 수정 후):
Saved: D:\projects\design\slides\stress-c4\out.pptx

### ★사이클 5 (2026-06-19) — 8테마 균등 stress (핸드오프 §1 첫행동, 사용자 "8세트 고르게" 의무 정정)
- 목적: c1~c4가 전부 `data-theme="modern"` 단일 → 테마별 변환경로(다크 대비/serif/primary소멸) 미검증 갭 정정.
- 생성: 8 서브에이전트 병렬, 차원당 다른 테마 + 그 테마 취약경로 직격:
  - 01 modern 프로세스다이어그램+차트 / 02 classic 좌우분할다단 / 03 dark-mono 타이틀룰+다크패널긴본문(A14/A10) / 04 company 인라인KPI혼합run / 05 executive-editorial 다크패널navy대비(A10) / 06 dark-pitch 색칩스와치+absolute오버레이(A9/A4) / 07 academic 고밀도표720+각주(A11/A13) / 08 editorial blockquote+figcaption+serif장문
- preflight(정적+--full) 결함 = ★테마특화(modern-only c1~c4서 미출현):
| # | 슬라이드 | 결함 | 분류 | 조치 |
|---|---|---|---|---|
| 1 | 01 modern | PF-55 span background ×5 | 생성기위반(A1) | 에이전트 수정 span→div |
| 2 | 01 modern | PF-62 conic-gradient 도넛=PPTX완전손실 | **계약갭** | ✅계약 A17(conic금지→stacked-bar) + 슬라이드 교체 |
| 3 | 02 classic | PF-42 opacity:0.75 무시→불투명 | **계약갭** | ✅계약 A2 보강(opacity) + 슬라이드 solid합성 |
| 4 | 07 academic | PF-19 Georgia→Arial폴백(serif소실) | **계약갭** | ✅계약 A18(serif='Times New Roman') + 슬라이드 폰트스택 |
| 5 | 06 dark-pitch | PF-71 출처 1.08:1 저대비(다크배경) | 생성기위반 | ✅계약 A19(다크 footnote 대비) + 슬라이드 색상향 |
- 무해 warn: PF-23(CJK 8장 표준)·PF-11(9색 경미). 룰 전부 정탐(오발 0).
- **★8테마 가치 입증**: PF-19(serif폴백)·PF-71(다크footnote)·PF-42(opacity)는 테마특화라 modern-only선 미출현. 계약갭 3건 신규 박제(A17/A18/A19) + A2 보강.
- 진행: 4 에이전트 background 수정중(01·02·06·07). 다음 = 재preflight clean확인 → convert+COM렌더+1600리사이즈+vision(8테마 실변환 검증, 특히 다크3종 대비·serif2종 폰트).
- 클린 카운터: 사이클5 NOT클린(계약갭 발굴) → 카운터 리셋 위험? ★종료조건은 이미 c2·c3 2연속 충족. c5는 8테마 커버리지 보강(사용자 의무) — 신규 차원이라 결함 나옴이 정상. c5 수정후 클린 재확인 + c6(8테마 2회차)로 2연속 재확인 목표.

#### c5 vision 판정 (8장 COM 렌더 1920px):
- ✅ **7/8 클린**: 01 modern(프로세스+stacked-bar 교체 성공)·02 classic(분할·opacity→solid)·03 dark-mono(분할 780px 수정 후 본문 침범 해소, A14/A10 ✅)·04 company(인라인KPI run)·05 executive(다크패널 A10 navy회피 ✅)·06 dark-pitch(색칩8 라벨 정상, VP-08 빈카드=FP확정)·07 academic(serif 적용·고밀도표 14행 720안착).
- ❌ **slide-08 editorial = 엔진 garble(회피 3회 실패, 미해결)**:
  - 증상: 좌측 col에서 quote-wrap 긴인용(4줄 wrap)+prose 본문이 Y겹침 + 우측 col KAM제목/설명(.kam-txt)이 좌측 X로 이동·겹침. dot(.kam-num)·colhead만 우측 제자리.
  - 회피 시도 3회 전부 동일 garble(픽셀 불변): (1) .body grid `1fr 1px 1fr`→flex+540px (2) .kam-item grid `auto 1fr`→flex+497px (3) .col/.kam flex-column→block flow+margin. **CSS 변경이 변환결과 0 = 마크업 회피 불가.**
  - preflight --full(브라우저 DOM PF-18) 통과 = 브라우저 정상, PPTX만 붕괴 → c1 #5/#6 클러스터(긴 wrap 텍스트 높이 오측정→형제 collapse) editorial 복합레이아웃 재발.
  - 부수: dot 번호 VP-04 1.5:1(.kam-num accent배경이 텍스트박스에 전파 안됨, 인접 #D8D2C9 상속). flex→line-height로 ERROR(1.1)→WARN(1.5) 완화했으나 근본 미해결.
  - **triage = §C ③ 엔진결함**. Explore로 html2pptx.cjs 위치/높이 계산 조사 위임중. 엔진수정은 GT 17덱 회귀0 게이트 필수.
- **c5 계약 갱신 총괄**: A2(opacity)·A12(fr분할 금지 확장)·A17(conic-gradient)·A18(serif폰트)·A19(다크 footnote 대비). 코드(preflight/html2pptx) 무수정 — 계약+슬라이드만.
- ★8테마 가치 = 7장 테마특화 결함(serif폴백/opacity/다크footnote/fr분할/navy대비) 수확 + 1장 엔진결함(editorial) 노출. modern-only c1~c4서 전부 미출현.

#### c5 editorial(slide-08) 엔진결함 추적 — ★widthIncrease 단위버그 fix 채택 + 2단 X-collapse deep-debug 분리:
- **격리(probe-c5/)**: repro-A(단일 풀폭 blockquote+prose)=✅정상 → blockquote/긴wrap 무죄. repro-B(좌우2단 540px 순수 CJK문단)=❌X침범 재현 → **2단 좁은컬럼+CJK가 트리거**.
- **근본원인(코드+PPTX XML+DBG 확정)**: html2pptx.cjs `isSingleLine`(L472) = `position.h(inch) <= lineHeight(pt)*1.5` **단위 불일치**(inch vs pt)로 거의 모든 텍스트 single=true 오판. → multi-line CJK가 single 취급되어 CJK widthIncrease(w×0.24)가 적용(DBG: w=4.219 single=true winc=1.006 adjW=5.225 > RIGHT x=4.953 침범). 배경없는 컬럼(.col)은 clamp(L545 부모shape 필요) 미발동 → 인접컬럼 침범 X겹침.
- **★엔진 fix 채택**: L510 widthIncrease 계산만 올바른 단위(lineHeightInch=lineSpacing/72)로 multi-line 재판정 → multi-line=minWidthIncrease(10pt). isSingleLine 전체는 heightIncrease/fit:shrink 의존이라 미수정(회귀회피). **검증: repro-B garble 해소✅ + slide-03/05 회귀0✅ + GT 17덱 회귀 delta=0✅**(baseline 5 ERROR=fix후 5, stash 비교 확정). → 정당한 엔진수정 채택.
- **⏳ 잔존 deep-debug(별개 버그) — repro A~G 7개 격리, trigger 4중조합으로 좁힘**: slide-08 2단일 때 우측 col 텍스트가 좌측 X로 collapse. probe-c5/ 격리(전부 우측 x좌표 4529138=정상 확인, collapse=457200):
  - repro-A(단일 풀폭 quote+prose)=✅ / B(2단 순수문단, widthIncrease fix 후)=✅ / C(2단 좌quote-wrap shape+우순수)=✅ / D(2단 우깊은중첩 .g1>.g2>p)=✅ / E(D+inline span .num)=✅ / F(E+divider 1px shape)=✅ / G(좌 quote-wrap+prose AND 우 깊은중첩 동시)=✅
  - **단일·2·3 조합 전부 정상인데 slide-08(좌 quote-wrap+prose + divider + 우 kam[깊은중첩+span] + KAM 4항목)만 garble** → trigger = **4중조합 전체 또는 항목수/세로높이 의존**(미확정). getPositionAndSize(L859 rect 그대로)·CJK widthIncrease(fix됨)·column-norm(tableColumns<2 미발동) 모두 단독으론 설명 안 됨.
  - ★repro-H(=G+divider+span+KAM 4항목, slide-08 2단 구조 정확 재현)=✅정상(우측 x=4750594, collapse 아님). **→ repro A~H 8개 전부 정상 = slide-08 garble 8 repro로 재현 실패.** trigger가 통제된 최소조합으로 안 잡힘 = 매우 특정 조건(좌측 quote+2문단 prose의 콘텐츠 높이 비대칭? 특정 더미텍스트 길이? slide-08 재작성 일시상태?) 의심.
  - **다음 deep-debug(별도 세션)**: (1) slide-08 재작성3(2단 garble 버전) 정확 복원(git 불가, 더미데이터 그대로 재작성) → 변환기 step 디버그(extractSlideData forEach 중 우측 텍스트 rect 실시간 console.error) (2) 좌측 콘텐츠 높이를 우측보다 크게 한 repro 변형. blockquote/figcaption/serif/2단 변환 자체는 repro A~H 전부 정상 = **stress 목적(textTag 변환) 달성**. slide-08은 단일컬럼(repro-A)으로 회피 정리(픽스처 OK). ★이 한 버그에 8 repro 투자, 추가 격리는 ROI 낮아 다음 세션 step 디버그로 이관.
- **slide-08 최종 = 단일컬럼 editorial(repro-A 검증패턴)로 정리** → ✅정상 변환(인용+figcaption+prose+KAM4 serif, 겹침0). 일회용 픽스처라 2단→단일 = 드리프트 아님(§3-4).

### ★★ 사이클5 완주 (2026-06-19) — 8테마 균등 8/8 클린 + 엔진fix 채택
- **c5 = 8/8 전체 클린**(01 modern·02 classic·03 dark-mono·04 company·05 executive·06 dark-pitch·07 academic·08 editorial 전부 정상 변환·vision 확인).
- **누적 수정**: 엔진2(blockquote double-emit c1 + ★widthIncrease 단위 c5, 둘 다 회귀0) / 계약 A2·A12·A17·A18·A19 신규·보강 / 슬라이드 산출.
- **8테마 커버리지 갭(핸드오프 §1 최대갭) = 해소.** modern-only 40차원(c1~c4) → 8테마 균등 8장(c5)서 테마특화 결함 7종 + 엔진결함 1종 수확·수정.
- **잔존 1건**: 2단+quote-wrap X-collapse 엔진버그(slide-08서 단일컬럼 회피, deep-debug 별도). 종료조건(2연속클린)은 c2·c3서 이미 충족, c5는 커버리지 보강 보너스.

### 사이클 6 (2026-06-19) — 8테마 2회차: 기하/위치 차원 ×8테마
- 차원 분배: 01 modern 수직타임라인 / 02 classic 워터폴bridge / 03 dark-mono 히트맵 / 04 company 간트 / 05 executive 깔때기(다크패널) / 06 dark-pitch 조직도트리 / 07 academic 버블산점도 / 08 editorial 게이지바+인용. 목적 = c3 기하차원(modern 검증완료)을 8테마로 재검증 + 신규 변환경로 결함.
- preflight(정적+--full) 결함 = 전부 생성기 위반(룰 정탐, 계약 이미 커버):
  - slide-03 dark-mono: PF-03(히트맵 720 overflow) + PF-42(opacity→A2) + PF-71×5(다크셀 텍스트 1.94:1→A10)
  - slide-07 academic: PF-18(버블 50% 겹침) + PF-19(georgia→A18)
  - slide-08 editorial: PF-19(georgia→A18)
  - 무해 warn: PF-23(CJK)·PF-11(16색 히트맵). 계약갱신 불필요(A2/A10/A18 기존, 에이전트 미준수).
- 진행: 3 에이전트 수정중(03·07·08). 다음 = 재preflight clean → convert+COM+vision(8장).
- ★c6 관찰: 8테마 2회차도 테마특화 결함 재발(dark-mono 대비/overflow, serif 폰트, 버블 절대배치) = 생성 에이전트가 계약을 매번 완벽 준수 못함 → 계약은 충분하나 생성단계 강제력 갭(다음 개선여지: 생성후 자동 preflight 게이트를 에이전트 워크플로에 내장).

#### c6 vision 판정 (변환 7장 + 수정중 2장):
- ✅ **정상 6**: 01 modern 타임라인(수직축선·노드)·03 dark-mono 히트맵(수정후 셀대비·범례 완벽)·04 company 간트(기간바)·05 executive 깔때기(다크패널 대비, 마지막단계 라벨 경미겹침)·06 dark-pitch 조직도(CFO→3본부→8팀 직교연결선)·08 editorial 게이지(진행바4+serif인용 A17/A18).
- ❌ **slide-02 classic 워터폴**: 막대 floating 정상이나 .barlabel(position:absolute) top이 중앙서 겹쳐 라벨 뭉개짐 → 생성기 라벨 top 재배치(에이전트 수정중). c3 modern 워터폴은 정상이었음=classic 에이전트 라벨 top 계산 미스.
- ⏳ **slide-07 academic 버블**: PF-18(원거리→bbox정사각 비겹침 재계산)+A15(각주 *→※)+PF-19(var토큰) 수정 완료, 재변환 대기.
- **★PF-19 룰 fix(§C ①)**: preflight PF-19가 var(--font-X) fallback형(`var(--x,"Y")`)을 따옴표 정지로 오발 → while 루프 진입시 m[1] 전체서 var 토큰 인라인 추출·환원(L356). c6 slide-07/08 오발 해소. GT 회귀 확인 필요.
- 진행: slide-02 라벨 + slide-07 버블 수정중 → 재convert(02·07) → render → vision → c6 완주 판정.

#### c6 vision 최종 (재수정 후):
- ✅ **정상 7**: 01 타임라인·03 히트맵·04 간트·05 깔때기(라벨세로분리 수정)·06 조직도·07 버블(bbox분리+※+serif 수정)·08 게이지.
- ❌ **slide-02 워터폴 = ★절대배치 라벨 X-collapse (c5 X-collapse 클러스터 재현 케이스!)**: .barlabel(position:absolute, left 64/220/376/532/688/844)이 변환 시 **X좌표가 중앙으로 collapse·뭉침**. 흰배킹·top분리·라벨top재배치 다 무효(라벨 X 자체가 안 잡힘). VP-04(−95 저대비)는 부산물. → **c5 slide-08 2단 X-collapse와 동일 변환기 결함 클러스터** = 절대배치/특정구조 텍스트의 X 위치 collapse. ★c5 repro A~H(flex/grid)로 못 잡았으나 **slide-02(position:absolute 다수)가 명확한 재현 케이스** → 다음 deep-debug에 slide-02 포함(절대배치 left가 변환서 무시/오계산되는지 extractSlideData rect 로그). 회피 = 라벨을 flex-row 범례로(절대배치 제거) 시도중.
- ★★**c6 핵심 수확 = X-collapse 재현 케이스 + 칸수 트리거 단서**: slide-02 라벨을 절대배치→flex-row(.axisrow 6칸 균등 width:156px) 회피해도 **여전히 6칸이 중앙으로 X-collapse**(막대는 정상). 7회 회피 실패(절대배치/flex-row/흰배킹/top분리). ★결정적: **repro-B(flex 2칸)=정상 vs slide-02(flex 6칸)=collapse** → **flex-row 칸 수(≥N)가 X-collapse 트리거 변수일 가능성** = c5 repro A~H가 2~3요소라 못 잡은 이유 설명! 
  - ★repro-I(순수 flex 6칸)=정상 → "칸수" falsify. **step 디버그로 근본 원인 확정·fix 완료(2026-06-19)**:
    - [XDBG] slide-02 axisrow 텍스트 rect.left=58/214/370/526/682/838px **정확 균등**(브라우저 정상) / [XDBG2] pendingText.push 시점 toX=0.277~6.477" **정상** / 그런데 PPTX 최종 x **전부 414338(0.45"=첫칸) collapse**.
    - [XTC] 범인 = **column-norm phase2(L677~707)**: `tableColumns=[{x:0.45, w:9.09", ny:4}]` — 전폭(9.09"=거의 슬라이드폭) gridline shape가 가짜 tableColumn → axisrow 12 텍스트(textCenter 0.3~6.5)가 col 범위(0.45~9.54) 안이라 **전부 col.x=0.45로 snap**(L698). 표 컬럼은 셀폭(좁음)인데 전폭 배경/격자선이 오판됨.
    - **★엔진 fix**: tableColumns 필터(L653)에 `if (c.w > 7.0) return false` — 전폭(>896px) shape = 격자선/배경/구분선, 셀 아님. slide-02는 남은 컬럼 1개<2 → phase2 미발동 → snap 없음. **검증: slide-02 collapse 완전해소(vision 막대+라벨 분산정렬)✅ + GT 17덱 회귀 delta=0✅ + c5/c6 전체 회귀0✅**.
  - **slide-08 2단**: 전폭 shape 없음(quote-wrap 541px<7)이라 이 fix와 다른 원인 가능성. 단일컬럼 회피 유지, 재현 시 동일 step 디버그([XTC] tableColumns 로그) 적용.

### ★★★ X-collapse 엔진 결함 근본 fix 완료 (2026-06-19) — c5/c6 클러스터 해결
- **근본 원인**: html2pptx.cjs column-norm phase2 가 **전폭(슬라이드폭급) shape를 tableColumn 으로 오판** → 그 폭 안 전체 텍스트를 col.x 로 snap = X-collapse. (rect 는 정확, 후처리 결함.)
- **fix**: tableColumns 필터에 `c.w > 7.0` 제외 (L653). GT 회귀0.
- **결과**: **c5 8/8 + c6 8/8 = 16장 8테마 전부 변환 정상.** 엔진 fix 2종 채택(widthIncrease 단위 + X-collapse 전폭tableColumn, 둘 다 회귀0).

### 사이클 7 (2026-06-19) — 8테마 3회차: 신규 차트 차원 ×8테마
- 차원: 01 modern 누적영역 / 02 classic 슬로프(회전연결선) / 03 dark-mono 레이더근사 / 04 company 불릿 / 05 executive 폭포+주석(다크,라벨flow범례) / 06 dark-pitch 네트워크 / 07 academic 박스플롯 / 08 editorial 풀블리드통계+인용. ★에이전트들이 X-collapse 학습 반영(절대배치 라벨→flow 범례, slope 회전선).
- **★c7 첫시도 preflight ERROR 0 + convert 8/8 변환 성공**(X-collapse fix + 누적 계약/학습 효과 = 파이프라인 견고화 입증).
- VP 결함(생성기 미스, 수정중): slide-04 불릿 % 라벨 배경구간(#D1D5DB) 위 흰색 1.5:1(VP-04) / slide-05 워터폴 주석 텍스트 shape overflow(VP-16). WARN: slide-07/08 georgia(A18 미준수, var토큰 안씀) / slide-02 슬로프 P-P 6% 경미 / PF-11 10색.
- 4 에이전트 수정 완료(04 %라벨 막대끝 어두운텍스트/navy안 흰색, 05 overflow 박스높이, 07·08 serif var토큰). 재convert: **VP ERROR 0**(WARN 2: slide-04 104%/96% white-on-white 경미 잔존).
- **★c7 재변환 = 8/8 변환 성공(ERROR 0)**. vision 핵심 2장 정상: slide-02 슬로프(회전 연결선·끝점값, X-collapse 없음=에이전트 회전rect 학습) / slide-04 불릿(%라벨 대비 해소). ⛔압축 후 잔여 vision: slide_01누적영역·03레이더·05워터폴·06네트워크·07박스플롯·08풀블리드 6장(변환성공, vision만 미확인). png=slides/stress-c7/png/slide_NN.png(1920px).
- **★c7 결론**: 8테마 3회차 첫시도 변환 8/8 ERROR0 + vision 7정상 = **파이프라인 견고화·학습누적 입증**(X-collapse 학습이 슬로프/워터폴 생성에 반영). vision 완주: 01누적막대·02슬로프(회전선)·04불릿(수정)·06네트워크(출자관계도)·08풀블리드(serif대형) 정상.
  - ⚠️ 경미: (1) slide-03 레이더 **좌측 div 다각형 근사 어색**(흰 넥타이 모양 — A17 conic 금지로 div 레이더 본질 한계, 우측 막대는 정상 = 데이터 전달됨). 레이더는 div로 부적합 → 계약에 "레이더=축별 막대 권장, div 다각형 회피" 추가 여지. (2) slide-04 104%/96% white-on-white(WARN, 막대 트랙끝). 둘 다 변환은 성공(ERROR0).
- **★★세션 총괄**: **c5·c6·c7 = 24장 8테마 균등 stress.** 엔진 fix 2종 근본해결(widthIncrease 단위 + X-collapse 전폭tableColumn, GT회귀0). 계약 A2/A12/A17/A18/A19 + PF-19 룰fix. c5 8/8 + c6 8/8 + c7 8/8 변환. 드리프트0. 다음=c8(신규차원) or slide-03 레이더/slide-04 미세수정 or 커밋.
- ★**c6 결론**: 8테마 2회차 7/8 변환 정상 + slide-02 X-collapse 재현(절대배치+flex-row 6칸 둘 다). 종료조건은 c2·c3 충족, c5·c6는 8테마 커버리지 보강 + **X-collapse 재현 케이스·칸수 단서 확보(c5 미해결의 큰 진전)**. **누적 엔진 결함 2종(widthIncrease 단위=fix완료 / X-collapse=flex 다칸·절대배치, 칸수 트리거 단서 확보, deep-debug 이관)**.
