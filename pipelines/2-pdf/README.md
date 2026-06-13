# Pipeline 2 — PDF (회람용 문서)

**출력**: `.pdf`
**용처**: 발표 없이 회람·열람하는 문서. 자가완결(화자 없이 읽힘)이 중요.

## 전제
- 본문은 **파이프라인 1** 에서 완성(`deck.md` + §13 검증 통과).
- 디자인은 `design-system/` 규칙으로 HTML 슬라이드/페이지 작성.

## 흐름
1. **본문 확정** — `../1-report-text/` 완료(검증 원장 `unsupported` 0건).
2. **HTML 렌더** — `deck.md` → design-system 테마 적용 HTML.
   - 테마·레이아웃은 `design-system/SKILL.md` 의 7-step(테마→레이아웃→매트릭스→schema→불변→PF→QA).
   - 폰트는 로컬 `.woff2`(사내망 CDN 차단 대비, `design-system/colors_and_type.css`).
3. **PDF 변환** —
   ```bash
   node scripts/html2pdf.js --slides-dir slides/<slug> --output <slug>.pdf
   ```
   (Playwright 인쇄 기반. Gemini/외부 호출 없음.)
4. **자가완결 점검** — 화자 노트 없이 각 페이지가 결론을 전달하는지(`content-authoring.md §3` self-sufficient slide).

## 주의
- 회람용이라 **annotation(주석·콜아웃)** 으로 exhibit 의 결론을 명시한다. PDF 는 발표자가 없다.
- 이미지 슬롯 최소화 — 차트/표/도형 우선.
