# Pipeline 3 — PPTX (발표자료)

**출력**: `.pptx` (편집 가능한 네이티브 텍스트/도형)
**용처**: 발표·배포용 슬라이드.

## 전제
- 본문은 **파이프라인 1** 에서 완성(`deck.md` + §13 검증 통과).
- 디자인은 `design-system/` 규칙으로 HTML 슬라이드 작성.

## 흐름 (SKILL.md §2.5 Step 0~7 준수 — 사내용)
1. **본문 확정** — `../1-report-text/` 완료.
2. **HTML 슬라이드 생성** — `deck.md` → design-system 적용. `design-system/SKILL.md` 7-step 준수.
   - 720pt×405pt, `<html data-theme>` + `<section data-layout>` 의무, 액션 타이틀 명사형, 10pt 하한.
   - 이미지: 차트/표/도형 우선. 사진은 placeholder/수동 배치(`design-system/image_slot_contract.md`).
3. **Preflight** — PPTX-safe HTML 정적·동적 검증.
   ```bash
   node scripts/preflight-html.js --slides-dir slides/<slug> --full
   ```
4. **변환 (HTML→PPTX)** — 네이티브 텍스트/도형.
   ```bash
   node scripts/convert-native.mjs --slides-dir slides/<slug> --output <slug>.pptx --full
   ```
   - 내부 단계: preflight → PptxGenJS 변환 → PPTX XML 검증(VP). `--full` 이면 Playwright 동적 검증까지.
5. **시각 검증 (필수) = COM + Playwright** — Gemini Vision 자리를 **사내 가용한 COM(PowerPoint) + Playwright** 로 대체한다(`validate-pptx-com.mjs` 류 Gemini VQA 만 제외; 시각 비교 자체는 아래로 수행):
   ```bash
   node scripts/screenshot-html.mjs --slides-dir slides/<slug> --output slides/<slug>/html-preview          # Playwright 1600×900
   powershell -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "slides/<slug>/<slug>.pptx" -OutputDir "slides/<slug>/preview"   # COM 300DPI
   ```
   각 `slide-NN.png` 두 장을 `Read` 로 나란히 비교 — 형태변형·텍스트잘림·색상차이·이미지깨짐. 차이 시 HTML 수정→재변환(최대 2회). **통과 전 에디터/다운로드 링크 금지**. (`SKILL.md §2.5 Step 2.5`, `PF_STEP_2_2_5.md`)
6. **QA** — `design-system/qa_rules.md` 9-check + autofix.
7. **비주얼 에디터 (필수 — 브라우저 자동 오픈)** — viewer 미리보기 대신 에디터를 띄운다:
   ```bash
   node scripts/editor-server.js --slides-dir slides/<slug> --port 3456 &
   sleep 2; start http://localhost:3456/ 2>/dev/null || powershell -Command "Start-Process 'http://localhost:3456/'"
   ```
   클릭=텍스트 직접편집, 드래그=AI 수정. **URL만 안내 금지(자동 오픈)**. 터널은 사내망 제약 가능 → 로컬 우선. (`SKILL.md §2.5 Step 3`, `PF_STEP_3_4.md`)

> **Step 0 소스 협의 + Step 1.5A Marp plain 초안은 이 README 흐름 진입 전에 필수** — `SKILL.md §2.5` 참조. 초안: `node scripts/draft-marp.mjs --outline slide-outline.md --output slides/<slug>/draft.pptx --open`

## 주의
- 변환 엔진은 임의 HTML 을 받는 범용 도구다. **디자인 품질은 design-system 준수에서 나온다** — 변환 전 7-step·PF 룰을 반드시 통과시킨다.
- `<table>` 금지(PF), 그라디언트/섀도는 슬라이드 금지(에디터 앱 전용), 풀블리드는 `--surface-inverse`.
