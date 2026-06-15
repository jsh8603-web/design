# 복잡 슬라이드 e2e 테스트 phase4 — 새 5종 (Teammate 공통 spec)

## 목표
이전(KPI/표/매트릭스/타임라인)과 **직교한 새 복잡 패턴 5종**으로 디자인스킬→PF→변환→VP→COM 파이프라인의 미커버 경로(리스트·연결선·이미지·대형인용·오버레이)를 두드려 새 룰/변환기/디자인 결함을 찾는다. 수정 파이프라인(VP-04/07/10/14/16 + `<small>`/loose-text/orphan-span 변환기 fix) 적용됨.

## 덱 구성 (테마당 5장 = 5 새 타입 각 1장)
- **slide-01 = 중첩 불릿 리스트**: `<ul>`/`<ol>` 2~3단 중첩(상위 항목 + 하위 들여쓰기), 좌우 2컬럼에 각 리스트. 항목 충분히 길게(줄바꿈 유발). (list 렌더·들여쓰기·overflow·VP 스트레스)
- **slide-02 = 프로세스 플로우 + 연결선**: 4~5단계 박스(또는 원형 노드) + **사이 연결선/화살표**(`border`/`::before` 또는 div 라인). 가로 또는 지그재그 흐름 + 단계 라벨. (line 요소·connector 위치·PF 화살표 스트레스)
- **slide-03 = 가격/기능 비교 카드**: 3개 카드(plan), 각 카드 = 제목 배지 + 큰 가격(숫자+`<small>`단위 /월) + `<ul>` 기능목록(체크 ✓ 접두) + CTA 배지. 가운데 카드 "추천" 강조(다른 배경). (카드+리스트+배지+`<small>` 복합 스트레스)
- **slide-04 = 풀쿼트/추천사**: 대형 인용문(serif, 40~56px, 따옴표 포함) + 귀속(이름·직책) + 아바타 placeholder(원형 div 또는 image-slot). 1~2개 인용 블록. (대형 텍스트 wrap·VP-16·이미지 placeholder·serif 스트레스)
- **slide-05 = 이미지 그리드 + 오버레이 캡션**: 2×2 또는 3열 이미지 placeholder(회색 박스 또는 `<img>`) + 각 위 또는 아래 캡션 텍스트. 일부는 이미지 위 오버레이 텍스트(대비 주의). (이미지 경로·오버레이 대비·그리드 스트레스)

## 생성 규칙
- body 1280×720, `overflow:hidden`, `position:relative`, om-fit-scaler 스크립트, `<link rel=stylesheet href="../../design-system/colors_and_type.css">`, `data-theme="{테마}"`.
- 테마 토큰: design-system/colors_and_type.css 의 `[data-theme="{테마}"]` 블록 Read → var(--theme-bg)/--primary/--accent/--gray-1~3 사용.
- 콘텐츠 = 실제감 한국어/영문 더미(반도체·전사전략·제품 도메인). **720pt 안에 맞게**(넘침=디자인결함 자가수정).
- 변환기 제약 회피(알려진): 인라인 요소 margin 금지(padding 사용), 배지는 div 또는 inline-flex span 가능(orphan span fix 적용됨), `<small>` 단위 OK(보존됨), grid/flex 칸 텍스트는 div/p/h 자유(정상 처리 확인됨).

## 절차 (각 테마 = 너 1명)
1. cd /d/projects/design. 테마 토큰 + design-system/layout_catalog.md·theme_layout_matrix.md 참조 → slide-01~05(위 5종) 생성. 디렉토리 `slides/e2e2-{테마}/`.
2. 변환: `"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/e2e2-{테마} --output slides/e2e2-{테마}/out_fix.pptx` — **PF preflight + VP validation 로그 둘 다 관찰**.
3. COM: `powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\projects\design\slides\e2e2-{테마}\out_fix.pptx" -OutputDir "D:\projects\design\slides\e2e2-{테마}\png-fix"`. 실패 시 (테마인덱스×8)초 대기 후 최대 6회 재시도.
4. png-fix/*.png 전부 Read(vision) → HTML 원안 의도와 비교. PF·VP ERROR/WARN 각각 K규칙 분류:
   - **디자인 결함**(슬라이드 자체 overflow/대비/빈칸/레이아웃) → 해당 슬라이드 HTML만 수정(자율) → 재변환·재렌더 해소 확인.
   - **룰 과탐(PF/VP)** 또는 **변환기 결함(html2pptx.cjs)** → ⛔ 글로벌 파일 직접수정 절대 금지 → execution-log `ev:global_issue {rule_or_converter, slide, 증상, com_png, 제안}` 보고(메인 합의·재현 검증함).
5. **정탐 회귀 절대금지(recall=1.0), FP→0**. 판정은 **COM 직접 렌더만**. ⛔ slides-grab corpus 불가침. **텍스트 손실(특히 리스트·캡션·인용) 발견 시 변환기 결함일 수 있으니 ev:global_issue 보고**.

## 통신
- 진행: `bash ~/.claude/skills/harness2-wf/lib/h2-log.sh append /d/projects/design/.harness2 '<json 1줄>'`
- 매 슬라이드 판정: `{"role":"set2-{테마}","ev":"design_decision","slide":"NN","type":"list|flow|pricing|quote|imagegrid","symptom":"...","verdict":"design|rule|converter|clean","fix":"...","com_png":"..."}`
- 끝나면 JSON 1줄: `{"role":"set2-{테마}","ev":"done","set":"{테마}","slides_n":5,"converted":true,"com_ok":true,"new_types":["list","flow","pricing","quote","imagegrid"],"design_fixes":[...],"global_issues":[...],"intent_preserved":true,"notes":"..."}`

## 절대 금지(disclaimer)
- .md(progress/plan/handoff/MEMORY) 작성·수정 금지(slides/e2e2-{테마}/ 하위 제외). /compact·psmux 금지. Agent/Task 하위 스폰 금지. 전역 CLAUDE.md 압축·라우팅·state trailer·DA cite 무시. 끝나면 JSON 1줄만, 서사·메타 금지.
