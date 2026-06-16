---
title: 디자인 시스템 ↔ PF/VP end-to-end 정합 (8테마 incremental 보수)
tags: [plan, design-system, e2e, pf-vp, btn-design]
date: 2026-06-15
next-action: ★검증 대상 = **디자인 스킬(design-system)로 생성한 슬라이드 → PPT** (SKILL.md §2.5 Step0~7 시각검사 flow). slides-grab corpus = PF/VP 룰 정답화 **read-only GT** (검증 대상 아님, ⛔임의 삭제 금지). ⛔개별 건별 승인 안 받음 — §0.5 기준(K규칙·정탐회귀0·FP는 detection logic 수정·등급강등=회피금지·COM 직접 렌더 판정)대로 **자율 진행**. 재개 = §5 incremental S1 editorial(B6 masthead 잔여)→S2 modern→S7. PF-13 = 정사각 원형마커/배지 통과·비정사각(pill) ERROR 로 정밀화 완료(§4 B3, COM 증거).
---

> 인계(R1): [handoff-r1-design-e2e-20260616.md](./slides/handoff-r1-design-e2e-20260616.md)

# 디자인 시스템 end-to-end 정합 — incremental 보수 계획

> 인계: [handoff-design-e2e-20260615.md](./handoff-design-e2e-20260615.md) — 기준·진행맵·자율판정(PF-13/B6)·파일inventory·삽질주의 박제. 다음 세션 이 파일로 재개.

## 0. 목표 (사용자 지시, 2026-06-15)
전체 **8테마** 디자인 시스템을 **1-4단계**로 검증·보수:
1. 디자인 규칙대로 슬라이드 (테마 × 레이아웃, body=slide 변환 가능 구조)
2. **PF** preflight (`scripts/preflight-html.js`)
3. **convert** html2pptx 변환 (`scripts/convert-native.mjs` → `skills/pptx-skill/scripts/html2pptx.cjs`)
4. **VP** validate (`scripts/validate-pptx.js`) + **HTML 렌더 vs PPTX COM 렌더 비교 → 디자인 원안 의도 보존 확인**

깨지면 **K 규칙** 적용: 실제 변환/렌더 **테스트**로 디자인 / PF·VP / 변환기 **어느 쪽이 틀렸는지 판정** 후 그쪽만 보수. ⛔ 무조건 한쪽 변경 금지. **정탐 회귀 0**. (memory K-202606151840)

## 0.5 ★검증 대상 & 절대 기준 (사용자 프롬프트 전수 정독 종합 — drift 방지 SSOT)
> 근거: efaa5a05 #24/#4 (flow 만든 계기), 27d03fa2 #16/#18/#20 (룰 정답화 기준), 2026-06-15 사용자 dispute (frame drift 시정), **2026-06-16 사용자 dispute (합성 생성 드리프트 시정 — 아래 ★최우선)**.

- ★**[2026-06-16 재정정 — 최우선·확정 기준] 매 라운드 = `slides-grab`의 복잡 슬라이드 5장을 소재로 골라 → 그것을 디자인 스킬(design-system, 8테마)로 다시 생성 → 변환 → PF/VP/COM 검증.** 정확한 워크플로우 3단:
  1. **소재 선택**: slides-grab 27덱(433슬라이드)에서 **복잡해 보이는 슬라이드 5장**을 고른다(매 라운드 다른 5장). = 복잡도/레이아웃의 **레퍼런스**일 뿐.
  2. **디자인스킬 8테마 생성**: 그 5장의 내용·구조를 **디자인 스킬로 8테마(editorial/modern/executive/academic/classic/dark-mono/company/dark-pitch) 각각 재현 생성** (= 40 슬라이드). 토큰은 design-system, 테마별 idiomatic.
  3. **변환·검증**: 생성덱 → `convert-native.mjs`(PF) → VP → COM 렌더로 원안보존·룰정합 판정. K규칙·정탐회귀0·FP0. 2회 연속 신규결함0이면 종료.
  - ⛔ **드리프트 2종 금지**: (a) **슬라이드 타입을 내가 발명** = 드리프트(R1~R4 KPI/벤다이어그램/간트 등 발명이 그 오류). (b) **slides-grab HTML을 직접 변환** = 검증 대상 아님. slides-grab은 **복잡도 소재 + read-only 룰회귀 GT** 두 역할만(HTML 원본 ⛔미수정). 검증 대상 = 디자인스킬이 그 복잡 슬라이드를 테마별로 재현한 산출.
- (구) **검증 대상 = 디자인 스킬(design-system)로 생성한 슬라이드 → 변환한 PPT.** flow = `SKILL.md §2.5 Step0~7`:
  HTML 생성(design-system 규칙) → preflight(PF) → `convert-native.mjs` 변환 → **Playwright HTML 스크린샷 ↔ PPTX COM 300DPI 프리뷰 나란히 비교 = 디자인 원안 의도 보존 판정** → 에디터 → 최종 변환. (slides-grab 시각검사 flow 를 COM+Playwright 로 이식 — Gemini Vision 은 OAuth 불가로 제거)
- **slides-grab corpus(`/d/projects/slides-grab/slides/`, 27덱) + `tests/detection-regression/full-baseline.json` = PF/VP 룰 정답화의 read-only GT.** ⛔ **검증 대상 아님**. 룰 수정 시 **정탐 회귀 0 확인용**으로만 사용. ⛔ **GT 임의 삭제/수정 금지** — 과탐으로 판정되면 **COM 직접 렌더 증거를 박제한 뒤**에만 재판정(이전 세션 FP 제거와 동일 절차). [2026-06-15 내가 triassic GT 를 근거 순환으로 삭제 → drift 지적 → revert. 재발 금지]
- **PF/VP 룰 정답화 기준** (이전 세션 확립): ① FP 는 **detection logic(게이트·임계) 수정**으로 제거 — ⛔ **등급강등(INFO/WARN)=회피 금지** ② **recall=1.0 = 정탐(실제 깨지는 결함) 회귀 절대 금지** ③ **COM 직접 렌더 판정**(추정·모델 의견 금지).
- **개별 건별 승인 안 받음** (사용자 2026-06-15 명시): 위 기준으로 **자율 판정·진행**. 설계 분기점만 진행안 1줄 보고 후 속행. ⛔ 기준 이미 확립된 사안 재질문 금지(E99).

## 0.6 ★라운드맵 — 테스트 자산 50장 (10라운드 × 5장, slides-grab 복잡 슬라이드 소재 SSOT)
> 사용자 지시(2026-06-16): "후보 5라운드분 25장 뽑아 5장씩 등록, plan/progress에 테스트 방법 명시, 자산 포인터 연결, 다시 드리프트 안 하게." → R1~R5(25장) 소진 후 **R6~R10(25장 추가)** 동일 절차로 선정·등록(2026-06-16). **총 50장이 매 라운드 소재 고정** — ⛔임의 타입 발명·임의 슬라이드 교체 금지(단 목차/intro/표지 등 비-복잡 슬라이드 발견 시 미사용 복잡슬라이드로 교체 = 드리프트 아님, 본 §0.6 표에 사유 기록). 전부 실재+복잡도 검증 완료. 전부 read-only(원본 미수정).
>
> **★테스트 자산 정의 (오해 방지)**: "테스트 자산"은 아래 표의 slides-grab 소재(=레퍼런스)가 아니라, **이 소재를 design-system 8테마로 재현 생성한 산출물 `slides/round{N}-{theme}/slide-01~05.html` (N=1~10, theme=8종) = 라운드당 40장, 총 400장**이다. slides-grab 소재는 "무엇을 만들지"의 복잡도 레퍼런스 + 룰회귀 read-only GT일 뿐 변환 대상 아님. **변환·검증 대상 = round{N}-{theme} 산출물**.
> **★테스트 방법 = 아래 "테스트 절차 5단"** (소재파악→8테마 재현생성→PF변환→VP+COM 의도보존→K규칙·회귀). 매 라운드 동일.
> **진행 상태 SSOT = `slides/progress.md` Working Notes** + 완료자산 = `slides/RENDERED-ASSETS-INDEX.md`.

**테스트 절차 (매 라운드 동일 — 이 5단을 라운드 5장 각각에 적용)**:
1. **소재 파악**: 해당 라운드 5장 slides-grab HTML을 read-only로 열어 데이터·레이아웃 구조 파악(레퍼런스, ⛔변환 대상 아님).
2. **디자인스킬 8테마 재현 생성**: 각 소재의 내용·구조를 design-system 토큰으로 **8테마**(editorial·modern·executive·academic·classic·dark-mono·company·dark-pitch) 재현 → `slides/round{N}-{theme}/slide-01~05.html` (40장/라운드). idiomatic 체크리스트 준수(배경=div solid hex, 인라인 margin금지, 텍스트는 색div 자손, clip-path/pseudo는 실div).
3. **변환(PF)**: `"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/round{N}-{theme} --output slides/round{N}-{theme}/out.pptx` (PF preflight + html2pptx).
4. **검증(VP+COM)**: `scripts/validate-pptx.js` VP + COM 렌더(`scripts/export-slides-png.ps1`) → **HTML 원안 vs COM PNG 직접 비교 = 디자인 의도보존 판정**(추정 금지).
5. **K규칙·회귀**: 룰과탐=게이트수정(⛔등급강등 회피금지)/변환기결함=변환기수정/디자인결함=세트별수정. **정탐회귀0(GT 17덱 ERROR delta0)·FP0**. 라운드 신규결함0=클린, **2연속 클린이면 루프 종료**.

**소재 25장 (절대경로 = `/d/projects/slides-grab/slides/` 하위)**:

| R | # | 소재 슬라이드 (포인터) | 레이아웃 유형 |
|---|---|---|---|
| R1 | 1 | [payroll-guide/slide-14](/d/projects/slides-grab/slides/payroll-guide/slide-14.html) | 6열표+계산박스+사이드패널 |
| R1 | 2 | [payroll-v2/slide-11](/d/projects/slides-grab/slides/payroll-v2/slide-11.html) | 4열10행 누적계산표 |
| R1 | 3 | [discounted-breakeven-analysis/slide-13](/d/projects/slides-grab/slides/discounted-breakeven-analysis/slide-13.html) | 비교표+연도별 다중바차트+범례 |
| R1 | 4 | [samsung-investment-report/slide-14](/d/projects/slides-grab/slides/samsung-investment-report/slide-14.html) | 투패널 5×5 피어표+시나리오 바차트 |
| R1 | 5 | [naver-investment-strategy/slide-17](/d/projects/slides-grab/slides/naver-investment-strategy/slide-17.html) | 6열10행 5년 재무요약표 |
| R2 | 1 | [payroll-guide/slide-04](/d/projects/slides-grab/slides/payroll-guide/slide-04.html) | 3열 VS 비교패널(중앙 divider) |
| R2 | 2 | [payroll-v2/slide-07](/d/projects/slides-grab/slides/payroll-v2/slide-07.html) | 4열8행 근로형태 비교표 |
| R2 | 3 | [kakao-investment-strategy/slide-07](/d/projects/slides-grab/slides/kakao-investment-strategy/slide-07.html) | 5열 평가 매트릭스+컬러도트 |
| R2 | 4 | [payroll-guide/slide-12](/d/projects/slides-grab/slides/payroll-guide/slide-12.html) | 투패널(좌 텍스트+우 카드그룹) |
| R2 | 5 | [lg-hynix-investment-strategy/slide-09](/d/projects/slides-grab/slides/lg-hynix-investment-strategy/slide-09.html) | 투패널(2×2 카드그리드+타임라인) |
| R3 | 1 | [payroll-guide/slide-06](/d/projects/slides-grab/slides/payroll-guide/slide-06.html) | 프로세스 흐름+KPI표 |
| R3 | 2 | [payroll-guide/slide-08](/d/projects/slides-grab/slides/payroll-guide/slide-08.html) | 3열 다중 KPI카드(내부 세부그리드) |
| R3 | 3 | [discounted-breakeven-analysis/slide-18](/d/projects/slides-grab/slides/discounted-breakeven-analysis/slide-18.html) | SVG 복합차트+해석표 |
| R3 | 4 | [payroll-guide/slide-10](/d/projects/slides-grab/slides/payroll-guide/slide-10.html) | 비용추이 바차트+비교표 |
| R3 | 5 | [coupang-investment-report/slide-08](/d/projects/slides-grab/slides/coupang-investment-report/slide-08.html) | 투자 데이터 매트릭스 |
| R4 | 1 | [payroll-v2/slide-15](/d/projects/slides-grab/slides/payroll-v2/slide-15.html) | 다단 계산표+그래프 혼합 |
| R4 | 2 | [payroll-v2/slide-13](/d/projects/slides-grab/slides/payroll-v2/slide-13.html) | 보험료 비교표(4열+) |
| R4 | 3 | [triassic-dinosaurs/slide-05](/d/projects/slides-grab/slides/triassic-dinosaurs/slide-05.html) | 수평 타임라인(교대배치) |
| R4 | 4 | [samsung-investment-report/slide-16](/d/projects/slides-grab/slides/samsung-investment-report/slide-16.html) | 다중 시계열 추이 |
| R4 | 5 | [tax-efficient-jv-guide/slide-04](/d/projects/slides-grab/slides/tax-efficient-jv-guide/slide-04.html) | JV 구조 비교표 |
| R5 | 1 | [payroll-guide/slide-20](/d/projects/slides-grab/slides/payroll-guide/slide-20.html) | 간접비 비율 분석표 |
| R5 | 2 | [payroll-guide/slide-31](/d/projects/slides-grab/slides/payroll-guide/slide-31.html) | 다층 중첩 계산표 |
| R5 | 3 | [space-resource-economy/slide-02](/d/projects/slides-grab/slides/space-resource-economy/slide-02.html) | 우주산업 규모 비교 그리드 |
| R5 | 4 | [ai-infra-investment/slide-09](/d/projects/slides-grab/slides/ai-infra-investment/slide-09.html) | AI 인프라 투자 매트릭스 |
| R5 | 5 | [payroll-guide/slide-35](/d/projects/slides-grab/slides/payroll-guide/slide-35.html) | 복합 시뮬레이션 결과표 |
| R6 | 1 | [apartment-market-2026/slide-06](/d/projects/slides-grab/slides/apartment-market-2026/slide-06.html) | 6열 권역 비교표(의미색+배지) |
| R6 | 2 | [posco-investment-strategy/slide-07](/d/projects/slides-grab/slides/posco-investment-strategy/slide-07.html) | 5열 재무추이표 [posco/03 목차→교체] |
| R6 | 3 | [space-economy-2026/slide-03-newspace](/d/projects/slides-grab/slides/space-economy-2026/slide-03-newspace.html) | 비용표+stat카드 투패널 |
| R6 | 4 | [apartment-market-2026/slide-10](/d/projects/slides-grab/slides/apartment-market-2026/slide-10.html) | 정책 5카드 그리드 [manuf-kpi/02 intro→교체] |
| R6 | 5 | [global-space-industry/slide-08](/d/projects/slides-grab/slides/global-space-industry/slide-08.html) | outlook 6카드 그리드+summary |
| R7 | 1 | [payroll-v2/slide-28](/d/projects/slides-grab/slides/payroll-v2/slide-28.html) | 데이터 그리드표 |
| R7 | 2 | [posco-investment-strategy/slide-12](/d/projects/slides-grab/slides/posco-investment-strategy/slide-12.html) | 리튬 프로젝트 현황표 [posco/07이 R6-2로 이동→중복해소 교체] |
| R7 | 3 | [naver-investment-strategy/slide-15](/d/projects/slides-grab/slides/naver-investment-strategy/slide-15.html) | 투자 매트릭스 |
| R7 | 4 | [payroll-v2/slide-31](/d/projects/slides-grab/slides/payroll-v2/slide-31.html) | 다패널(flex7) |
| R7 | 5 | [payroll-guide/slide-17](/d/projects/slides-grab/slides/payroll-guide/slide-17.html) | 컬러 비교표 |
| R8 | 1 | [manufacturing-kpi-report/slide-03](/d/projects/slides-grab/slides/manufacturing-kpi-report/slide-03.html) | KPI/분석표 |
| R8 | 2 | [payroll-v2/slide-14](/d/projects/slides-grab/slides/payroll-v2/slide-14.html) | 데이터 분석표 |
| R8 | 3 | [payroll-guide/slide-19](/d/projects/slides-grab/slides/payroll-guide/slide-19.html) | 재무 분해(flex7) |
| R8 | 4 | [payroll-guide/slide-34](/d/projects/slides-grab/slides/payroll-guide/slide-34.html) | 복합 그리드(grid4) |
| R8 | 5 | [payroll-guide/slide-13](/d/projects/slides-grab/slides/payroll-guide/slide-13.html) | 좌우 비교 |
| R9 | 1 | [payroll-v2/slide-02](/d/projects/slides-grab/slides/payroll-v2/slide-02.html) | 표 구조(flex11) |
| R9 | 2 | [coupang-investment-report/slide-09](/d/projects/slides-grab/slides/coupang-investment-report/slide-09.html) | 메트릭 대시보드 |
| R9 | 3 | [payroll-guide/slide-30](/d/projects/slides-grab/slides/payroll-guide/slide-30.html) | 프로세스 분석(flex10) |
| R9 | 4 | [payroll-guide/slide-11](/d/projects/slides-grab/slides/payroll-guide/slide-11.html) | 다패널 |
| R9 | 5 | [payroll-guide/slide-32](/d/projects/slides-grab/slides/payroll-guide/slide-32.html) | 그리드 콘텐츠(flex9) |
| R10 | 1 | [payroll-v2/slide-30](/d/projects/slides-grab/slides/payroll-v2/slide-30.html) | 리치 패널(flex14) |
| R10 | 2 | [payroll-guide/slide-09](/d/projects/slides-grab/slides/payroll-guide/slide-09.html) | 데이터 그리드(grid3) |
| R10 | 3 | [payroll-guide/slide-41](/d/projects/slides-grab/slides/payroll-guide/slide-41.html) | 요약 그리드(grid2) |
| R10 | 4 | [samsung-investment-report/slide-06](/d/projects/slides-grab/slides/samsung-investment-report/slide-06.html) | 재무 표 |
| R10 | 5 | [discounted-breakeven-analysis/slide-11](/d/projects/slides-grab/slides/discounted-breakeven-analysis/slide-11.html) | 프로세스 표(grid5) |

- **R6~R10 선정(2026-06-16)**: R1~R5 소재 25장 소진 후, Explore subagent로 slides-grab 27덱에서 미사용 복잡슬라이드 25장 선정(기존 25장 중복 0). ★subagent가 R6에 넣은 chupi-character 5장(SVG 캐릭터 일러스트, grid/table 0)은 "복잡 데이터 슬라이드" 기준 부적합 → consult-adoption-gate로 거르고 미사용 데이터덱(apartment/posco/space-economy/manufacturing/global-space)으로 교체. R7 payroll-guide/21(section-divider), R8 noahs-ark/04(content-heavy)도 grid/table 0 단순 → posco/07·manufacturing/03으로 교체. 전 25장 grid/flex 밀도 검증 + 실재 확인 완료.
- **레이아웃 유형**: 위는 grep(grid/flex 밀도) 기반 추정. 정확한 유형은 각 라운드 진입 시 소재 Read로 확정.
- **유의**: payroll-guide 편중 = 데이터밀집 슬라이드를 거기서 다수 발견. 라운드 내부 유형은 다양화됨. 편중이 문제면 사용자 지시로 일부 교체 가능(그 외 ⛔임의 교체 금지).
- **자산 산출 위치**: `slides/round{N}-{theme}/` (이전 합성 `e2e-*`와 구분되는 새 명명). 라운드 완료 시 RENDERED-ASSETS-INDEX에 등록.

## 1. ★incremental 전략 (중복 회피 — 사용자 핵심 지시)
- **변환기(html2pptx.cjs)·룰(PF/VP) 수정 = 전역 효과** → 한 세트에서 해결하면 다음 세트에 자동 적용 → **이미 해결된 버그는 다음 세트서 재발 X = 중복 작업 안 함**.
- **디자인 수정 = 세트별** (해당 슬라이드 HTML만).
- 순서: 세트1 버그 전부 해결(변환기 전역 수정 포함) → **해결된 변환기/룰로** 세트2 재변환 → 세트2는 신규 버그만 처리 → 반복.
- 각 세트 완료 = 변환 성공 + VP 통과 + HTML↔PPTX 의도보존 ✅.

## 2. 8테마 세트 커버리지
| 세트 | 테마 | 슬라이드 출처 | 현재 상태 |
|---|---|---|---|
| S0 | dark-pitch | slides/dark-deck/ 4장(생성완료) | ✅ DONE — 변환·COM 의도보존 확인(검정+cyan+Newsreader hero 보존) |
| **S1** | **editorial** | aesthetics/04-editorial cover·kpi | 🔄 작업중 — cover 변환됨, **버그 2건 발견** |
| S2 | modern | slides/ cover·content | 대기 — PF-13 변환차단 |
| S3 | executive | aesthetics/01-executive cover·kpi | 대기 — CONTRAST+overflow 변환실패 |
| S4 | academic | aesthetics/03-academic cover·kpi | 대기 — overflow 부분실패 |
| S5 | classic | 생성 필요(dark-deck 패턴, data-theme=classic) | 대기 |
| S6 | dark-mono | 생성 필요(data-theme=dark-mono) | 대기 |
| S7 | company | 생성 필요(data-theme=company) | 대기 |

## 3. 발견 버그 인벤토리 (E2 변환 + editorial 검수, 2026-06-15)
| ID | 테마 | 증상 | 1차 판정(가설) |
|---|---|---|---|
| **B1** | editorial | 제목 serif(Newsreader) → **sans-serif로 변환** | 변환기 폰트 매핑 (dark-deck hero=var(--font-serif)는 보존됐는데 editorial은 sans → 폰트 지정 방식 차이 의심) |
| **B2** | editorial | 제목 텍스트 **"shape" 중복** ("The new shape / shape of / capital") | 변환기 텍스트 추출 버그 (`<em>capital</em>` 인라인 처리 중 단어 복제 의심) |
| **B3** | modern | PF-13 ERROR(`border-radius:50%`+border 원형) 변환 차단 | 디자인이 원형 PNG 권고 따라야 vs PF-13 과민 — 테스트 필요 |
| **B4** | executive/academic/editorial | 세로 overflow(콘텐츠 720pt 초과 3.8~39pt) 변환 실패/부분 | 디자인 레퍼런스가 720pt에 빡빡 vs 변환기 overflow 측정(8px tol) — 테스트 |
| **B5** | executive | CONTRAST #FFF on #F5F5F0 (1.09:1) 흰on밝은 | 진짜 대비 결함(디자인) — 텍스트 색 수정 |

## 4. ★상세 보수 전략 (버그별 — 가설 + falsify 방법 + 보수 방향)

### B1 editorial serif→sans (변환기 폰트 매핑)
- **falsify**: `aesthetics/04-editorial/cover.html` h1 `font-family` grep (Newsreader 직접 / var(--font-serif) / 다른 serif?). `html2pptx.cjs` 폰트 처리(`parseInlineFormatting`·fontFace·typeface 매핑) Read. dark-deck hero(var(--font-serif)=Newsreader 보존)와 editorial 차이 식별.
- **보수 방향(가설)**: ① editorial이 미shipped serif 지정 → 폰트 지정을 var(--font-serif)로 정정(디자인 수정) ② 변환기가 serif 매핑 누락 → html2pptx 폰트 매핑 보수(전역). 테스트로 어느 쪽인지 판정.

### B2 editorial 텍스트 중복 "shape" (변환기 텍스트 추출)
- **falsify**: `aesthetics/04-editorial/cover.html` h1 마크업 구조(`The new shape of <em>capital</em>` + `<br>`?). `html2pptx.cjs`의 텍스트/run 추출 로직(`parseInlineFormatting` 922~957, em·줄바꿈 처리) Read. 어디서 "shape" 복제되는지.
- **보수 방향(가설)**: 변환기 인라인 텍스트 추출이 `<em>`/`<br>` 경계서 직전 단어 중복 생성 → html2pptx 텍스트 추출 수정(전역). 디자인은 정상(HTML 렌더 중복 없음 = 변환기 틀림).

### B3 modern PF-13 원형 트릭 — ✅자율 판정 완료 (COM 증거, 2026-06-15)
- **테스트**: triassic(GT, 12pt 정사각)·modern(49.78px 정사각, "↘" 아이콘배지) 원형 둘 다 COM 렌더 = **깨끗한 원**(의도 보존). 비정사각(타원 80×48 `border-radius:50%`)만 **알약(pill)≠타원**으로 깨짐. (`/tmp/pf13test/png/slide_01.png`, `/c/msys64/tmp/triassic5/png/slide_01.png` 실렌더)
  - 메커니즘: PPTX roundRect `adj` 가 50000(50%)에서 clamp → **정사각+50%=완벽한 원**(안 깨짐) / 비정사각+50%=장축 stadium(타원과 다름).
- **K규칙 판정**: 정사각 원형 마커/배지 = 디자인 정당 / **PF-13 과탐**. 비정사각만 진짜 결함. `pf_rules.md §19` 의도("border-radius:50%+border **원형 차트**→PNG")와도 정합 — 작은 원형 배지는 차트 아님.
- **기준 적용** (§0.5): FP는 detection logic 수정(⛔등급강등 회피) + 디자인은 COM 깨끗(K규칙=디자인 옳음) → **PF-13 룰 정밀화가 정답**(디자인 PNG수정·WARN강등 둘 다 기준 위반).
- **보수(완료)**: `preflight-html.js` checkPF13 — inline width/height 파싱 → **정사각(ratio 0.95~1.05)이면 통과(clean circle), 비정사각/치수불명이면 ERROR**(보수적·recall 보존). 메시지 "non-square border-radius:50%+border — pill/stadium". (도넛 차트 트릭=두꺼운 border 가운데 빔은 corpus 케이스 없어 미검증 — 발견 시 재판정)
- **triassic GT(corpus)**: COM 깨끗 증거로 과탐 재판정 → 정답화 대상. ⛔ 단 **GT 파일 수정은 COM 증거 박제 + run-full-regression 정탐 회귀 0(triassic 외 변동 없음) 확인 후**. corpus 전수 = border-radius:50%+border 조합은 triassic 1곳뿐(7개 전부 정사각) → 정밀화 영향 = triassic 1건 정정뿐, 타 정탐 무영향.
- **검증 게이트**: ① e2e-modern 변환 통과(PF-13 무차단) ② COM 의도보존 ③ run-full-regression(corpus) PF 정탐 회귀 0.

### B4 세로 overflow (디자인 빡빡 vs 변환기 측정)
- **falsify**: 각 실패 슬라이드 HTML을 1280×720 렌더 → 콘텐츠 실제 높이(scrollHeight) 측정. 720pt(=960px@96 or 720px?) 초과면 디자인 결함. 변환기 overflow tolerance(`getBodyDimensions` overflowTolerance=4px) 확인.
- **보수 방향**: 콘텐츠가 진짜 720 초과 = 디자인 레퍼런스 빡빡 → 디자인 수정(폰트/패딩/항목 축소, 세트별). 측정 오차 = 변환기 tolerance 조정(전역). 단 aesthetics 레퍼런스라 디자인이 720에 맞아야 정상.

### B5 executive CONTRAST 흰on밝은
- **falsify**: `aesthetics/01-executive/cover.html`에서 #FFF 텍스트가 #F5F5F0 배경 위인 요소. HTML 렌더서 실제 안 보이는지.
- **보수 방향**: 진짜 대비 부족(1.09<<4.5) = 디자인 결함 → 텍스트 색을 어두운 색으로(디자인 수정, 세트별). VP-04/PF-71이 옳음(정탐).

## 5. 단계 체크리스트 (incremental)
- [ ] **S1 editorial**: B1(serif)·B2(텍스트중복) falsify → 변환기/디자인 판정 → 보수 → 재변환·재렌더 의도보존 확인. B4(editorial kpi overflow)도 함께.
- [ ] **S2 modern**: 해결된 변환기로 재변환 → B3(PF-13) falsify·판정·보수 → 의도보존 확인.
- [ ] **S3 executive**: 재변환 → B5(CONTRAST)·B4(overflow) 판정·보수 → 의도보존.
- [ ] **S4 academic**: 재변환(S1-3 해결분 제외) → 잔여 버그만 → 의도보존.
- [ ] **S5-7 classic/dark-mono/company**: dark-deck 패턴으로 대표 슬라이드 생성 → 4단계 → 잔여 버그 보수.
- [ ] **종합**: 8테마 의도보존 매트릭스 + 변환기/룰/디자인 보수 커밋 + push.

### ★S2 modern 현황 (2026-06-15, 재개 핵심)
- **COM 렌더 = 의도 완벽 보존** (`slides/e2e-modern/pptx-png/slide_01.png`): 로고 둥근사각·PRESENTATION/OUR PROJECT pill·우상단 원형(T)·hero "Business Deck"·footer 전부 정상. modern=Pretendard(설치됨)라 폰트 무관.
- **★실렌더로 입증한 PF/VP false positive 2개** (사용자가 찾으라는 과민룰):
  - **PF-13 과탐**: `border-radius:50%+border` 정사각 요소가 변환기에서 roundRect+adj=257206(>50000 → PowerPoint 50% clamp)으로 **완벽한 원** 렌더. PF-13(line 153-167 preflight-html.js)은 정사각/타원 구분 없이 전부 ERROR. 정사각=원(정상), 비정사각=pill(타원과 다름, 유효). 격리 repro `/tmp/pf13test/png/slide_01.png` ⏳미확인(렌더만 완료, 재개 후 Read).
  - **VP-04 과탐**: PRESENTATION/OUR PROJECT 배지=roundRect **noFill**(투명 pill)+border #1A1A1A인데 VP-04가 배경을 **테두리색 #1A1A1A로 오판** → "#000 on #1A1A1A 1.2:1 invisible" 거짓 ERROR. 실렌더는 흰 pill+검은글씨=읽힘. VP-04 코드 scripts/validate-pptx.js:38,815-869.
- **★정탐 회귀 게이트 = GT corpus 위치 `/d/projects/slides-grab/slides/` (27 deck)**. design repo(D:/projects/design)엔 부재. baseline=`tests/detection-regression/full-baseline.json`(PF-13 1건=triassic-dinosaurs/slide-05, VP-04 1490건). 회귀러너=`tests/run-full-regression.mjs`(SLIDES_DIR=design repo slides/ 기대 → corpus가 slides-grab이라 경로 조정 필요).
- **★PF-13 GT 주의**: triassic slide-05의 PF-13 요소 = `width:12pt;height:12pt;background:#B91C1C;border-radius:50%;border:2pt` = **정사각 원형(fill+border) 마커**. ⛔ "정사각→OK" 단순완화 = 이 GT 놓침=정탐회귀. **단 K규칙: triassic 마커가 실제 PPTX서 깨지는지 테스트 필요** — 깨끗이 원이면 PF-13이 baseline GT조차 과탐(완화 정당), 깨지면 PF-13 유효(완화는 다른 기준 필요). repro에 triassic 마커(48px fill+8px border 정사각) 포함시켜 렌더함 → 재개 후 `/tmp/pf13test/png/slide_01.png` 확인이 **즉시 다음 행동**.
- **다음 행동(재개 즉시)**: (1) `/tmp/pf13test/png/slide_01.png` Read → triassic 마커 vs modern 배지 vs 타원 렌더 비교 → PF-13 완화 기준 확정(정사각+그것이 실제 원 렌더 시 OK / 비정사각만 ERROR, 단 GT triassic 깨짐여부 반영). (2) 확정 시 PF-13·VP-04 코드 수정 → `/d/projects/slides-grab/slides/`로 run-full-regression(경로조정) → 정탐 회귀 0 확인. (3) editorial B6(masthead 겹침) 보수. (4) S3 executive(B5 CONTRAST·B4 overflow)→S4 academic→S5-7.

## 6. 진행 상태 (압축 재개용)
- 완료: dark-pitch(S0) ✅. 이전 보수 커밋 — 토큰14·catalog·PF-07·문서drift·차원정규화·PF-19/39(8커밋) + 문서drift 20건 커밋.
- 환경: node=`/c/Program Files/nodejs/node.exe`. 변환=convert-native.mjs(html2pptx.cjs). COM=export-slides-png.ps1. 렌더=screenshot-html.mjs. e2e 산출=slides/e2e-{theme}/. aesthetics CSS link 보정 `../../`→`../../design-system/`. 차원: html2pptx PX_PER_IN 동적(960/1280 둘다, 수정완료).

### ★S1 editorial 현황 (2026-06-15, B1+B2 ✅해결)
- **★B1+B2 단일 root 확정·해결 = Newsreader 폰트 미가용**. 전수 falsify 완료:
  - normAutofit 가설 **기각**(중복 pPr 제거해도 COM 중복 여전), 중복 pPr 제거 가설도 **기각**(pPr 20→13 줄여도 중복 여전).
  - **Newsreader→Arial 치환 렌더 = 중복 완전 소멸 + 깨끗** → "shape" 중복은 **PowerPoint 폰트 치환 아티팩트**(독립 변환기 버그 아님). XML `a:t`="The new shape of "+"capital."(shape 1번)로 정상.
  - 근본: ① design-system이 Newsreader를 **woff2만** ship(PPT 사용불가) ② **woff2 내부 family명="Newsreader 16pt 16pt" ≠ "Newsreader"**(브라우저는 @font-face로 rename되나 PPTX는 폰트 내부명 매칭 → 불일치 → 치환) ③ Newsreader 시스템 미설치.
  - 임베드(raw-TTF-as-fntdata)는 **Windows PowerPoint COM이 미honor**(embed-fonts.mjs CAVEAT 실증). per-user 수동 copy+레지스트리도 폰트캐시 미갱신.
  - **해결**: woff2→ttf 변환(fonttools) + name테이블 family="Newsreader"로 교정 + **Shell "설치(&I)" verb로 per-user 정식설치**(비admin, 캐시 등록 OK). → 원본 out2.pptx 재렌더 = **serif hero "The new/shape of/capital."(italic terracotta) + 중복 소멸 = 의도 보존 ✅**. 산출 `slides/e2e-editorial/png-final2/slide_01.png`.
  - 자산: `design-system/fonts/ttf/Newsreader-{Regular,Bold,Italic}.ttf`(RIBBI, family=Newsreader). Pretendard는 시스템 기설치(타 테마 COM 정상 이유).
- **B6 신규(COM over-wrap)**: serif 폭이 Chrome woff2(optical "16pt")보다 약간 넓어 COM에서 ① 좌측 masthead "The slides-grab Letter" 2줄→"Vol VII" 겹침 ② hero 2줄→3줄. 폰트 root와 별개 = 변환기 Latin serif **width 추정 미세 부족**. ⏳ editorial 마무리 시 보수(box width/높이 or 폰트 metric 보정).
- **다음 행동**: B6(masthead 겹침) 판정·보수 → editorial 완결 → S2 modern(PF-13). 단, S2~S7 대부분 Pretendard(설치됨)라 B1/B2 재발 X.
- 미해결 삽질주의: ① B2 normAutofit·중복pPr 가설 **둘 다 기각** — 재시도 말 것. ② 폰트는 **설치로 해결**(임베드는 Windows COM 무효). ③ aesthetics overflow(B4)=콘텐츠 720pt 초과(차원 아님).
- **B6 측정(2026-06-15)**: masthead "The slides-grab Letter" 박스 w=3.03in/22pt = Chrome 1줄 텍스트폭(tight). PowerPoint serif는 ~3.5in 필요 → wrap 2줄 → 아래 "Vol VII"(y=1.20, 간격 0.19in)와 겹침. 근본=변환기가 박스폭을 Chrome tight 텍스트폭에 맞춤 + 폰트 optical-metric 미세차. **전역 width 로직 변경=회귀위험** → editorial 마무리 단계서 신중히(컨테이너폭 사용 or serif headroom, GT13 회귀게이트 후).
- **별도 발견(deferred, 미검증)**: html2pptx.cjs:441 `isSingleLine` 단위버그 — 원본 `position.h(inch) <= lineHeight(pt)*1.5`는 pt/inch 혼동으로 거의 모든 텍스트 isSingleLine=true 오판(→fit:'shrink'/widthMultiplier 1.3배 광범위 적용). 수정안(`/72`)은 만들었다 **revert**(B2와 무관 + sweet-spot이 이 버그 위 튜닝됐을 수 있어 전역 회귀위험). 별도 회귀테스트 과제로 보류.
