# 복잡 슬라이드 e2e R5 — 새 5종 (Teammate 공통 spec)

## 목표
이전 20종과 직교한 **새 복잡 5종**으로 또 다른 경로(원 overlap·아바타·split·체크박스 glyph·축 버블)를 두드린다. 수정 파이프라인 적용됨 → 이전 결함 안 나와야 정상.

## ★변환기 idiomatic 필수 체크리스트 (생성단계부터 준수 — R4서 효과 입증)
1. 배경·테두리는 `<div>`에만(텍스트태그/span에 bg·border 금지, 배지=div).
2. 배경색 solid hex만(⛔rgba/hsla 금지 — alpha 무시→텍스트 invisible).
3. 인라인 요소 margin 금지 → padding/flex gap.
4. 텍스트는 자신의 색 배경 `<div>`의 자손으로(형제 overlay 위 absolute 금지 — resolveBackground 못 읽음).
5. clip-path·pseudo-element(::before/::after) 시각 소멸 → 연결선·장식·비사각은 실 `<div>`(폭 계단 등 실 geometry). 화살표=border+rotate.
6. 흰/연한 텍스트는 실제 어둡게 렌더되는 bg 위에만. 720pt 안에 맞게.

## 덱 구성 (테마당 5장)
- **slide-01 = 벤다이어그램/교집합**: 2~3개 겹치는 원(실 div border-radius:50%, solid 배경) + 각 원 라벨 + 교집합 텍스트. (원 overlap·교집합 위치 스트레스)
- **slide-02 = 팀 그리드/조직 로스터**: 6~8명 카드 그리드(아바타=원형 div placeholder + 이름 + 역할 + 부서 태그). (아바타 원·카드 그리드·VP-07 스트레스)
- **slide-03 = 비포/애프터 비교**: 2단 split(좌=현행/우=개선), 각 단에 제목 + 항목 리스트 또는 지표 + 중앙 화살표/구분선(실 div). (split 레이아웃·대비 스트레스)
- **slide-04 = 체크리스트/요건**: 2~3 그룹 × 항목들, 각 항목 ✓/☐ 글리프 + 텍스트 + 상태. (체크박스 glyph·그룹 리스트·정렬 스트레스)
- **slide-05 = 사분면 버블차트**: 2축(x/y 라벨) + 4분면 + 위치된 버블 5~7개(크기=값, 실 div 원 + 라벨). (축·위치 버블·겹침 VP-14 스트레스)

## 생성·절차·통신·금지
- body 1280×720, overflow:hidden, om-fit-scaler, colors_and_type.css link, data-theme. 토큰 var(--theme-bg/primary/accent/gray-1~3). 실제감 더미. 720 안에.
- 디렉토리 `slides/e2e5-{테마}/`. 변환=`"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/e2e5-{테마} --output slides/e2e5-{테마}/out_fix.pptx`(PF+VP 관찰). COM=`powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\projects\design\slides\e2e5-{테마}\out_fix.pptx" -OutputDir "D:\projects\design\slides\e2e5-{테마}\png-fix"`(실패시 인덱스×8초 대기 최대6회).
- png 전부 Read(vision)→원안 비교. K규칙: 디자인결함=슬라이드수정 자율 / 룰과탐·변환기결함=ev:global_issue 보고+재현(직접수정 금지). **advisory WARN(theme accent 토큰·flow/funnel/kanban류 VP-07/16 fits·clip-path PF-22)은 워크어라운드 말고 note만**. 정탐회귀0·FP0, COM 직접렌더만. ⛔slides-grab 불가침.
- 끝: `{"role":"set5-{테마}","ev":"done","set":"{테마}","slides_n":5,"converted":true,"com_ok":true,"new_types":["venn","teamgrid","beforeafter","checklist","quadbubble"],"design_fixes":[...],"global_issues":[...],"intent_preserved":true,"notes":"..."}`
- ⛔.md(progress/plan/handoff) 작성금지(slides/e2e5-{테마}/ 제외). /compact·psmux 금지. Agent/Task 하위스폰 금지. 끝나면 JSON 1줄만.
