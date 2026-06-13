---
name: report-builder
description: 사내 Claude Code 에서 보고서를 만든다. 의도(본문 텍스트 / PDF / PPTX)를 판별해 알맞은 파이프라인으로 라우팅한다. 본문은 액션 타이틀·근거 태그·환각 검증 게이트로, 디자인은 design-system(토큰·테마·레이아웃)으로, 변환은 scripts(HTML→PPTX/PDF)로 처리한다. 지식 소스는 사내 DB + WebFetch + Confluence 로 한정(OAuth·Gemini 이미지·NotebookLM 불가). 트리거 — "보고", "보고서", "발표자료", "슬라이드", "덱", "deck", "PPT", "PPTX", "PDF 보고서", "엑셀 보고서".
user-invocable: true
---

# Report Builder (사내 / Claude Code)

보고서 생성의 단일 진입점. 사용자의 **의도**를 먼저 판별하고, 공통 코어를 거친 뒤 1·2·3 중 한 파이프라인으로 간다.

## 0. 사내 환경 전제 (항상)

- 지식 소스 = **사내 DB + WebFetch/WebSearch 직접 + Confluence** 3종 (`rules/research-sourcing.md`).
- OAuth 키 불가 → **Gemini 이미지 생성·Gemini Vision·NotebookLM 전부 불가**. 이미지는 차트/표/도형 우선, 사진은 placeholder/수동 배치.
- 외부 자료가 안 닿으면 추정치로 메우지 말고 사용자에게 추출본을 요청한다.

## 1. 의도 판별 → 라우팅

먼저 묻거나 맥락에서 판단한다: **무엇을 산출하나?**

| 의도 | 파이프라인 | 출력 | 폴더 |
|---|---|---|---|
| 본문 텍스트만 (초안·메모·엑셀 데이터 보고서) | **1. report-text** | `.md` | `pipelines/1-report-text/` |
| 회람용 문서 (발표 없음) | **2. pdf** | `.pdf` | `pipelines/2-pdf/` |
| 발표자료 | **3. pptx** | `.pptx` | `pipelines/3-pptx/` |

- 불분명하면 1개만 물어 확정한다. 2·3 도 내부적으로 **1을 먼저** 거친다(본문이 있어야 디자인·변환 가능).
- 엑셀/데이터 위주 보고서도 1의 작성 기준을 따른다(`rules/content-authoring.md §17.1`).

## 2. 공통 코어 (1·2·3 진입 전 공통)

1. **Brief 1장** — `slides/<slug>/00-brief.md` 생성. 방향·근거맵·정치적 맥락·검증 원장. (`content-authoring.md §10`)
2. **고스트덱 아웃라인** — 액션 타이틀만으로 논리 흐름 확인. (`§2`, `§11.2`)
3. **§13 검증 게이트** — 모든 주장을 internal(사내DB NLI) / external(권위출처·Confluence RARR) / derived(코드 재계산)로 분류해 검증. 출구 = 검증 원장에 `unsupported` 0건. (`§13`)

## 2.5 생성 운영 절차 (Step 0~7) — slides-grab flow

진입점에서 **이 순서를 지킨다**. 건너뛰면 소스 협의·plain 초안·비주얼 에디터·시각 검증이 통째로 누락된다(이식 시 빠졌던 부분). 상세 절차서 = `docs/pipeline-steps/PF_STEP_*.md` + `docs/pipeline-steps/PRESENTATION_FLOW.md`.

**Step 0 — 소스 협의 (필수, 자동 진행 금지)**
주제가 주어지면 임의 판단 말고 선택형으로 묻고 **사용자가 번호로 답할 때까지 대기**:
```
소스 자료를 어떻게 준비할까요?
  1. URL/파일 직접 제공 (웹페이지·PDF·문서)
  2. 사내 DB / Confluence 추출본 제공
  3. AI가 WebSearch/WebFetch 로 조사 (일반 주제)
  4. 추출본을 직접 작성해 전달
```
(원본 NotebookLM 1~4 는 OAuth 불가로 위 4지 대체 — `rules/research-sourcing.md` 3소스)

**Step 1 — 아웃라인 + 승인**
`slides/<슬러그>/` 생성 → `progress.md` 초기화 → `slide-outline.md` 작성 → **사용자 승인**. 승인 전 슬라이드 생성 금지. (본문 작성 기준 = 위 §2 Brief·고스트덱·§13 검증)

**Step 1.5A — 디자인 미적용 plain 초안 (필수, 건너뛰기 금지)**
HTML 슬라이드로 바로 가지 말고 **Marp 초안으로 구성/분량부터 확인**:
```bash
node scripts/draft-marp.mjs --outline slide-outline.md --output slides/<명>/draft.pptx --open
```
이미지 기반이라 텍스트 편집 불가 — 구성/분량 전용. 수정 요청 = 아웃라인 수정 → 초안 재생성 루프. (`PF_STEP_0_1.md §1.5A`)

**Step 2 — HTML 생성**
design-system + `rules/` 규칙으로 `slide-NN.html` 생성 → preflight:
```bash
node scripts/preflight-html.js --slides-dir slides/<명>
```
(`PF_STEP_2_2_5.md §2`)

**Step 2.5 — 시각 검증 (필수, 에디터 전) = COM + Playwright 비교**
시각 검사는 Gemini Vision 자리를 **사내 가용한 COM(PowerPoint) + Playwright** 로 대체한다(OAuth 불가로 Gemini VQA 제거 — VQA 는 이미지 검수 한정이라 사내 skip). 변환 후 HTML 스크린샷 ↔ PPTX COM 300DPI 프리뷰를 나란히 비교:
```bash
node scripts/convert-native.mjs --slides-dir slides/<명> --output slides/<명>/<명>.pptx
node scripts/screenshot-html.mjs --slides-dir slides/<명> --output slides/<명>/html-preview          # Playwright 1600×900
powershell -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "slides/<명>/<명>.pptx" -OutputDir "slides/<명>/preview"   # COM 300DPI
```
각 `slide-NN.png` 두 장을 `Read` 로 나란히 확인 — 형태변형·텍스트잘림·색상차이·이미지깨짐. 차이 발견 시 HTML 수정 → 재변환(최대 2회). **이 비교 통과 전 에디터/다운로드 링크 제공 금지**. (`PF_STEP_2_2_5.md §2.5`)

**Step 3 — 비주얼 에디터 (브라우저 자동 오픈 필수)**
기존 에디터(포트 3456~3460) 종료 → editor-server 실행 → **브라우저 자동 오픈**:
```bash
node scripts/editor-server.js --slides-dir slides/<명> --port 3456 &
sleep 2; start http://localhost:3456/ 2>/dev/null || powershell -Command "Start-Process 'http://localhost:3456/'"
```
URL만 안내하는 것 금지 — 자동으로 연다. 클릭=텍스트 직접편집, 드래그=AI 수정 요청. (외부 터널은 사내망 제약 가능 → 로컬 우선) (`PF_STEP_3_4.md §3`)

**Step 4 — 수정 반복**
사용자 피드백 = 정탐. 수정 전 번호 리스트로 확인 → HTML 수정 → 에디터 자동 갱신(fsWatch→SSE). 레이아웃/구조 수정 시 **Step 2.5 재검증 필수**. (`PF_STEP_3_4.md §4`)

**Step 5~7 — 변환 (사용자 형식 선택 후)**
```bash
node scripts/convert-native.mjs --slides-dir slides/<명> --output <명>.pptx --full   # PPTX
node scripts/html2pdf.js        --slides-dir slides/<명> --output <명>.pdf            # PDF
```
(`docs/pipeline-steps/PF_STEP_5_6_7.md`)

## 3. 규칙 SSOT (어디를 보나)

| 영역 | 위치 |
|---|---|
| 본문 작성·논증·검증 게이트·워크플로우 | `rules/content-authoring.md` (뼈대) |
| 리서치 소스(사내DB/WebFetch/Confluence)·출처 태그 | `rules/research-sourcing.md` |
| 디자인·HTML·PPTX-safe·테마·레이아웃·QA | `design-system/` (SKILL.md → prompting_rules / pf_rules / qa_rules / theme_layout_matrix / layout_catalog) |
| 변환·검증 엔진(코드) | `scripts/` |

## 4. 빠른 시작

- 본문만: `pipelines/1-report-text/README.md`
- PDF: `pipelines/2-pdf/README.md`
- PPTX: `pipelines/3-pptx/README.md`

본문 → (디자인 HTML) → 변환 순. 자세한 실행 명령은 각 파이프라인 README 참조.

## 5. 숫자 정합 검증 (excel 위임)

숫자 정합은 design 이 직접 하지 않고 **excel 레포에 위임**한다(검증 책임 분리 유지). 원본 데이터가 있는 보고서는 렌더 후 산출물의 모든 숫자가 원본으로 추적되는지 게이트한다.

```
python3 $EXCEL_REPO/main.py ingest <source.xlsx> out/ingest                                  # → tidy.csv (정답)
python3 $EXCEL_REPO/tools/content-gate.py <deck.html|pptx> out/ingest/tidy.csv --excel-repo $EXCEL_REPO
```

출처로 추적 안 되는 숫자가 있으면 게이트가 exit 1. `EXCEL_REPO` 는 submodule(`vendor/excel`) 권장. 공통 코어 §13 검증 게이트의 **derived(코드 재계산)** 축이 이 위임으로 닫힌다.

> `content-gate.py` 는 excel 레포 소유물 — design 작업 범위가 아니라 **호출 계약만** 박는다. excel 측 게이트 구현은 별도.
