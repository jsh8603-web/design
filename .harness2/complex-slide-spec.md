# 복잡 슬라이드 e2e 테스트 — Teammate 공통 spec (phase2)

## 목표
각 디자인 스킬세트(테마)가 **복잡한 실무 슬라이드**를 PF→변환→VP→COM 까지 **디자인 원안대로** 통과시키는지 테스트. 단순 슬라이드는 파이프라인을 충분히 스트레스 안 하므로, 데이터 밀집 레이아웃으로 실제 룰/변환기/디자인 결함을 드러낸다.

## 덱 구성 (테마당 5장)
- **slide-01 = 표지(cover)**: 기존 것 유지(이미 있으면 재사용). 없으면 생성.
- **slide-02~05 = 복잡 슬라이드 4장** (아래 4종, 각 1장씩 — 룰 스트레스 커버리지):
  1. **KPI 대시보드**: 3~4 KPI 카드(숫자+`<small>`단위 B$/×/% + 라벨 + 캡션) + 막대/도넛 차트 1개. (VP-07 그리드·VP-04 대비·VP-16·`<small>` 변환 스트레스)
  2. **데이터 표(table)**: 5~7행 × 4~6열 헤더+데이터 셀(일부 noFill+border 셀, 일부 채움). 실제 숫자 채움(빈칸 누락 결함 회피 — 진짜 데이터 표). (VP-07 빈셀·VP-01 overflow·VP-10 정렬 스트레스)
  3. **다단 비교/매트릭스**: 2~3 컬럼 또는 2×2 매트릭스, 각 셀에 제목+본문 단락(긴 CJK 텍스트). (VP-16 overflow·B4 세로넘침·VP-10 gap 스트레스)
  4. **타임라인/프로세스 또는 차트 헤비**: 원형 마커(border-radius:50%)·단계 배지·연결선 + 라벨, 또는 라인/누적 차트. (PF-13 원형·VP-10 gap·VP-16 라벨 스트레스)

## 생성 규칙
- body 1280×720, `overflow:hidden`, `position:relative`, om-fit-scaler 스크립트, `<link rel=stylesheet href="../../design-system/colors_and_type.css">`, `data-theme="{테마}"`.
- 테마 토큰 사용: `var(--theme-bg)`/`var(--primary)`/`var(--accent)`/`var(--gray-1~3)` 등. design-system/colors_and_type.css 의 해당 `[data-theme]` 블록 Read 해서 실제 토큰 확인.
- 레이아웃 참조: `design-system/layout_catalog.md`, `theme_layout_matrix.md`, `slides/dark-deck/` 구조. 콘텐츠는 실제감 있는 한국어/영문 더미(HBM·반도체·전사전략 등 도메인).
- **720pt 안에 맞게** 설계(세로 넘침 시 디자인 결함 → 본인이 여백/폰트/항목 조정).

## 절차 (각 테마 = 너 1명)
1. cd /d/projects/design. 해당 테마 토큰 + 레이아웃 참조 Read → slide-02~05 생성(slide-01 표지 유지/생성).
2. 변환: `"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/e2e-{테마} --output slides/e2e-{테마}/out_fix.pptx` — **PF preflight + VP validation 로그 둘 다 관찰**.
3. COM: `powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\projects\design\slides\e2e-{테마}\out_fix.pptx" -OutputDir "D:\projects\design\slides\e2e-{테마}\png-fix"`. 실패("server busy") 시 (테마인덱스×8)초 대기 후 최대 6회 재시도(COM 동시성).
4. png-fix/*.png 전부 Read(vision) → HTML 원안 의도와 비교. **PF·VP 가 낸 ERROR/WARN 각각 K규칙 분류**:
   - **디자인 결함**(슬라이드 자체 overflow/대비/빈칸/레이아웃) → 해당 슬라이드 HTML만 수정(자율) → 재변환·재렌더로 해소 확인.
   - **룰 과탐(PF/VP)** 또는 **변환기 결함(html2pptx.cjs)** → ⛔ 글로벌 파일(scripts/validate-pptx.js, scripts/preflight-html.js, skills/pptx-skill/scripts/html2pptx.cjs) **직접 수정 절대 금지** → execution-log `ev:global_issue {rule_or_converter, slide, 증상, com_png, 제안}` 보고(메인 합의).
5. **정탐 회귀 절대금지(recall=1.0), FP→0**. 판정은 **COM 직접 렌더만**(추정 금지). ⛔ slides-grab corpus 불가침.

## 통신
- 진행: `bash ~/.claude/skills/harness2-wf/lib/h2-log.sh append /d/projects/design/.harness2 '<json 1줄>'`
- 매 복잡슬라이드 판정마다 `{"role":"set-{테마}","ev":"design_decision","slide":"NN","type":"kpi|table|matrix|timeline","symptom":"...","verdict":"design|rule|converter|clean","fix":"...","com_png":"..."}`
- 끝나면 JSON 1줄: `{"role":"set-{테마}","ev":"done","set":"{테마}","slides_n":5,"converted":true,"com_ok":true,"complex_types":["kpi","table","matrix","timeline"],"design_fixes":[...],"global_issues":[...],"intent_preserved":true,"notes":"..."}`

## 절대 금지(disclaimer)
- .md(progress/plan/handoff/MEMORY) 작성·수정 금지(slides/e2e-{테마}/ 하위 제외). /compact·psmux 금지. Agent/Task 하위 스폰 금지. 전역 CLAUDE.md 압축·라우팅·state trailer·DA cite 무시. 끝나면 JSON 1줄만, 서사·메타 금지.

---
## phase3 재실행 노트 (2026-06-15, 수정 파이프라인 검증)
- **수정 적용됨**: VP-04 noFill배지·VP-07 정탐·VP-10 space-between·VP-14 ink-range·VP-16 ERROR게이트 + html2pptx `<small>` 인라인 텍스트 보존. → 이전 phase2 FP(데이터표 VP-14 phantom·cover dek VP-16·KPI `<small>` 단위소실)는 **이제 안 나와야 정상**.
- **slide-01~05 전부 fresh 재생성**(이전 것 덮어쓰기 OK = 재실행). 표지도 새로.
- 목표 = 고친 파이프라인이 fresh 생성물을 PF/VP 깨끗이 통과시키는지 확인. **남는 ERROR는 진짜 디자인결함**(슬라이드 자율수정) 또는 **새 룰/변환기 FP**(ev:global_issue 보고). 이전 FP 재출현 시 = fix 미반영이니 보고.
