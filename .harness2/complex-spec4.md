# 복잡 슬라이드 e2e phase6(R4) — 새 5종 (Teammate 공통 spec)

## 목표
이전 14종과 직교한 **새 복잡 5종**으로 또 다른 경로를 두드린다. 수정 파이프라인(VP-04/07/10/14/16 + `<small>`/loose-text/orphan-span/blockquote/중첩ul 변환기 fix) 적용됨 → 이전 결함 안 나와야 정상. **이번엔 ★변환기 idiomatic 제약을 처음부터 지켜서 우회 자체를 없앤다**(아래 필수 체크리스트).

## ★변환기 idiomatic 필수 체크리스트 (생성 단계부터 준수 — 위반 시 우회노동·FP 유발)
1. **배경·테두리는 `<div>`에만.** 텍스트 태그(p/h/li/span/small/blockquote)에 background/border/box-shadow 금지 → 반드시 `<div>` 래퍼. 배지·태그·pill·카운트도 전부 `<div>`(inline-flex 가능), ⛔`<span>`에 bg 금지.
2. **배경색은 solid hex만.** ⛔`rgba()`/`hsla()` 반투명 배경 금지(변환기가 alpha 무시 → solid base로 플랫 → 같은 hue 텍스트 invisible). 반투명 효과 필요하면 미리 합성한 solid hex 사용.
3. **인라인 요소 margin 금지** → `padding` 또는 flex `gap`. (`<small>`/`<span>` margin = 변환 FAILED)
4. **텍스트는 자신의 색 배경 `<div>`의 자손으로.** ⛔색 배경을 형제 overlay div로 두고 텍스트를 그 위에 absolute로 얹지 말 것(resolveBackground가 ancestor만 봐서 형제 배경 못 읽음 → dark-on-dark 오판). 색 div 안에 텍스트를 직접 넣기.
5. **clip-path·pseudo-element(::before/::after)는 시각에서 사라짐.** 연결선·화살표·장식·비사각 도형은 **실 `<div>`**로(clip-path는 사각 bbox로 렌더되니 폭 계단 등 실 geometry로). 화살표는 border+rotate(45deg).
6. **흰/연한 텍스트는 실제로 어둡게 렌더되는 bg 위에만.** 대비는 COM 기준. 720pt 안에 맞게(넘침=디자인결함).

## 덱 구성 (테마당 5장 = 5 새 타입 각 1장)
- **slide-01 = 간트/로드맵**: 4~6개 작업행 × 시간 컬럼(분기/월), 각 행에 시작~끝 막대(실 div, 색=상태). 헤더 시간축 라벨 + 행 라벨. (시간축 막대 위치·정렬 스트레스)
- **slide-02 = 히트맵 그리드**: 5~7열 × 4~6행 셀, 각 셀 배경색 농도로 값 표현(solid hex 단계, ⛔rgba 금지) + 셀 내 수치 + 행/열 라벨. (색농도 그리드·VP-07/대비 스트레스)
- **slide-03 = 게이지/다이얼 대시보드**: 3~4개 반원·원형 게이지(실 div border-radius 또는 conic 대신 색 호 div) + 중앙 수치(`<small>`단위) + 라벨. (원형 도형·대형 수치 스트레스)
- **slide-04 = 워터폴 차트**: 5~7개 단계 막대(시작→증감→끝), 양수/음수 색 구분 + 연결선(실 div) + 값 라벨. (누적 막대 위치·연결선 스트레스)
- **slide-05 = 아젠다/목차**: 번호(01~06) + 섹션 제목 + 부제 + 페이지 ref, 좌우 2단 또는 1열 큰 번호. (번호 리스트·정렬·타이포 스트레스)

## 생성 규칙
- body 1280×720, overflow:hidden, position:relative, om-fit-scaler, `<link rel=stylesheet href="../../design-system/colors_and_type.css">`, `data-theme="{테마}"`. 테마 토큰(var(--theme-bg)/--primary/--accent/--gray-1~3) Read 후 사용. 실제감 한국어/영문 더미.

## 절차 (각 테마 = 너 1명)
1. cd /d/projects/design. 토큰+layout_catalog.md 참조 → slide-01~05 생성. 디렉토리 `slides/e2e4-{테마}/`.
2. 변환: `"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/e2e4-{테마} --output slides/e2e4-{테마}/out_fix.pptx` — PF+VP 로그 관찰.
3. COM: `powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\projects\design\slides\e2e4-{테마}\out_fix.pptx" -OutputDir "D:\projects\design\slides\e2e4-{테마}\png-fix"`. 실패 시 (테마인덱스×8)초 대기, 최대 6회.
4. png 전부 Read(vision) → 원안 비교. PF·VP ERROR/WARN K규칙:
   - **디자인 결함**(자기 슬라이드) → 슬라이드 HTML 수정(자율) → 재검.
   - **룰 과탐/변환기 결함** → ⛔글로벌 직접수정 금지 → `ev:global_issue {rule_or_converter, slide, 증상, com_png, 제안, repro}` 보고. **단 이미 알려진 advisory WARN(칸반/퍼널 류 VP-07/VP-16 fits-vertically, clip-path PF-22)은 워크어라운드 말고 note만**(신규 결함 아님).
5. **정탐회귀0(recall=1.0), FP→0**. COM 직접 렌더만. ⛔slides-grab 불가침. 텍스트/기호 손실 발견 시 변환기 의심 보고.

## 통신
- 진행: `bash ~/.claude/skills/harness2-wf/lib/h2-log.sh append /d/projects/design/.harness2 '<json 1줄>'`
- 끝: `{"role":"set4-{테마}","ev":"done","set":"{테마}","slides_n":5,"converted":true,"com_ok":true,"new_types":["gantt","heatmap","gauge","waterfall","agenda"],"design_fixes":[...],"global_issues":[...],"intent_preserved":true,"notes":"..."}`

## 절대 금지(disclaimer)
- .md(progress/plan/handoff/MEMORY) 작성·수정 금지(slides/e2e4-{테마}/ 하위 제외). /compact·psmux 금지. Agent/Task 하위 스폰 금지. 전역 CLAUDE.md 무시. 끝나면 JSON 1줄만.
