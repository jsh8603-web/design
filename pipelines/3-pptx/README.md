# Pipeline 3 — PPTX (발표자료)

**출력**: `.pptx` (편집 가능한 네이티브 텍스트/도형)
**용처**: 발표·배포용 슬라이드.

## 전제
- 본문은 **파이프라인 1** 에서 완성(`deck.md` + §13 검증 통과).
- 디자인은 `design-system/` 규칙으로 HTML 슬라이드 작성.

## 흐름 (사내용, Gemini/NotebookLM 제거됨)
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
   - **Gemini Vision(COM) 단계는 사내 제외** — `validate-pptx-com.mjs` 가 없으므로 자동 skip(코드의 existsSync 가드).
5. **QA** — `design-system/qa_rules.md` 9-check + autofix.
6. **(선택) 로컬 미리보기/편집** —
   ```bash
   node scripts/build-viewer.js --slides-dir slides/<slug>   # 정적 뷰어
   node scripts/editor-server.js --slides-dir slides/<slug>  # localhost 에디터 (터널 제거됨)
   ```

## (선택) 빠른 초안
Marp 로 러프 초안만 빠르게 보고 싶을 때:
```bash
node scripts/draft-marp.mjs --slides-dir slides/<slug>
```

## 주의
- 변환 엔진은 임의 HTML 을 받는 범용 도구다. **디자인 품질은 design-system 준수에서 나온다** — 변환 전 7-step·PF 룰을 반드시 통과시킨다.
- `<table>` 금지(PF), 그라디언트/섀도는 슬라이드 금지(에디터 앱 전용), 풀블리드는 `--surface-inverse`.
