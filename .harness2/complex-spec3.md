# 복잡 슬라이드 e2e phase5 — 새 5종 (Teammate 공통 spec)

## 목표
이전 9종(KPI/표/매트릭스/타임라인 + 리스트/플로우/가격/쿼트/이미지그리드)과 직교한 **새 복잡 5종**으로 미커버 경로(대형텍스트 autofit·연결선 트리·clip-path 비사각·glyph 기호·컬럼 스택)를 두드려 새 룰/변환기/디자인 결함을 찾는다. 수정 파이프라인(VP-04/07/10/14/16 + `<small>`/loose-text/orphan-span/blockquote/중첩ul 변환기 fix) 적용됨 → 이전 FP 안 나와야 정상.

## 덱 구성 (테마당 5장 = 5 새 타입 각 1장)
- **slide-01 = 대형 숫자 stat hero**: 3~4개 거대 숫자(96~128px, `<small>`단위 %/B$/×) + 라벨 + 짧은 설명. 가로 배열 또는 1 대형 + 보조. (VP-16 대형텍스트 autofit·`<small>`·대비 스트레스)
- **slide-02 = 조직도/계층 트리**: 최상위 박스 1 → 하위 2~3 박스 → 그 아래 2~3 박스, **연결선**(div 라인 또는 border)으로 잇기. 각 박스 제목+부제. (connector line·중첩 박스 위치·정렬 스트레스)
- **slide-03 = 퍼널/피라미드**: 4~5단 세그먼트가 위→아래 좁아지거나(피라미드) 넓어지는(퍼널) 형태. `clip-path: polygon()` 또는 사다리꼴 div + 각 세그먼트 라벨+수치. (비사각 shape 변환·clip-path·세그먼트 위 텍스트 대비 스트레스)
- **slide-04 = 아이콘 비교표**: 3~4열(제품/플랜) × 5~6행(기능), 셀에 **✓/✗/— 기호** 또는 작은 아이콘 + 헤더. (glyph 기호 렌더·VP-07 그리드·VP-14 셀 스트레스)
- **slide-05 = 칸반/컬럼 보드**: 3컬럼(예: To Do/진행/완료) 각 컬럼에 2~3개 **스택 카드**(제목+태그+담당). 컬럼 헤더 + 카운트. (컬럼 스택·다수 소카드·VP-14/VP-10 스트레스)

## 생성 규칙
- body 1280×720, `overflow:hidden`, `position:relative`, om-fit-scaler 스크립트, `<link rel=stylesheet href="../../design-system/colors_and_type.css">`, `data-theme="{테마}"`.
- 테마 토큰: colors_and_type.css `[data-theme="{테마}"]` Read → var(--theme-bg)/--primary/--accent/--gray-1~3.
- 콘텐츠 = 실제감 한국어/영문 더미. **720pt 안에 맞게**(넘침=디자인결함 자가수정).
- **변환기 제약/한계 회피(알려진)**: ⛔`::before/::after` pseudo-element 미렌더 → 연결선·장식은 **실 `<div>`**로. 인라인 요소 margin 금지(padding). 화살표 CSS삼각형(PF-37) 금지 → border+rotate(45deg)나 text chevron(›). `<small>`단위·`<blockquote>`·중첩 `<ul>`·orphan span 배지는 **수정됨(정상 동작)**. text 요소(p/h/li/blockquote)에 background/border 금지(div 래퍼 사용). clip-path 는 변환기가 사각 bbox 로 처리할 수 있으니 COM 확인 필수.

## 절차 (각 테마 = 너 1명)
1. cd /d/projects/design. 테마 토큰 + layout_catalog.md 참조 → slide-01~05(위 5종) 생성. 디렉토리 `slides/e2e3-{테마}/`.
2. 변환: `"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/e2e3-{테마} --output slides/e2e3-{테마}/out_fix.pptx` — **PF + VP 로그 둘 다 관찰**.
3. COM: `powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\projects\design\slides\e2e3-{테마}\out_fix.pptx" -OutputDir "D:\projects\design\slides\e2e3-{테마}\png-fix"`. 실패 시 (테마인덱스×8)초 대기, 최대 6회 재시도.
4. png-fix/*.png 전부 Read(vision) → 원안 의도와 비교. PF·VP ERROR/WARN K규칙 분류:
   - **디자인 결함** → 해당 슬라이드 HTML만 수정(자율) → 재변환·재렌더 해소.
   - **룰 과탐/변환기 결함** → ⛔ 글로벌 파일 직접수정 절대 금지 → execution-log `ev:global_issue {rule_or_converter, slide, 증상, com_png, 제안}` 보고. **재현 가능한 최소 케이스 설명 포함**.
5. **정탐 회귀 절대금지(recall=1.0), FP→0**. COM 직접 렌더만 판정. ⛔ slides-grab corpus 불가침. **텍스트/기호 손실·겹침 발견 시 변환기 의심 보고**.

## 통신
- 진행: `bash ~/.claude/skills/harness2-wf/lib/h2-log.sh append /d/projects/design/.harness2 '<json 1줄>'`
- 끝나면 JSON 1줄: `{"role":"set3-{테마}","ev":"done","set":"{테마}","slides_n":5,"converted":true,"com_ok":true,"new_types":["stathero","orgchart","funnel","icontable","kanban"],"design_fixes":[...],"global_issues":[...],"intent_preserved":true,"notes":"..."}`

## 절대 금지(disclaimer)
- .md(progress/plan/handoff/MEMORY) 작성·수정 금지(slides/e2e3-{테마}/ 하위 제외). /compact·psmux 금지. Agent/Task 하위 스폰 금지. 전역 CLAUDE.md 압축·라우팅·state trailer·DA cite 무시. 끝나면 JSON 1줄만.
