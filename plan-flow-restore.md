# plan — slides-grab 운영 flow 복원 (Step 0~7 진입점 박제)

## 문제
design 레포가 slides-grab 이식 시, 운영 진입점 `SKILL.md` 가 원본 Step flow 를 안 담아
에이전트가 4단계를 통째로 건너뜀:
1. Step 0 소스 협의 (선택형 질문 + 사용자 대기)
2. Step 1.5A 디자인 미적용 Marp plain 초안 (+ 재생성 루프)
3. Step 3 비주얼 에디터 (editor-server + 브라우저 자동 오픈)
4. Step 2.5 COM 시각 검증 (HTML Playwright shot ↔ PPTX COM 300DPI 나란히 비교)

원본 절차서 `docs/pipeline-steps/PF_STEP_*.md` + `PRESENTATION_FLOW.md` 는 살아있으나
SKILL.md 가 참조·지시하지 않음. → **진입점에 운영 flow 복원**.

## 사내 대체 매핑 (원본 → 사내)
| 원본 | 사내 대체 | 근거 |
|---|---|---|
| Step 0 소스: NotebookLM 1~4 | URL/파일 직접(5) + WebSearch/사내DB(6) | OAuth 불가 → research-sourcing.md 3소스 |
| Step 1.5B NanoBanana 이미지 | 차트/표/도형 우선, 사진 placeholder | 이미지 생성 불가 |
| Step 2.5/4 Gemini VQA 시각검사 | COM `export-slides-png.ps1` + Playwright `screenshot-html.mjs` → Read 비교 | Gemini Vision 불가, COM/Playwright 가용 |
| editor-server `--tunnel`(cloudflared) | 로컬 `http://localhost:{port}` 우선, tunnel 선택 | 사내망 외부터널 제약 가능 |

## 변경 파일
1. `SKILL.md` — 공통 코어를 Step 0~7 운영 절차로 확장 + 각 Step PF_STEP 참조 + 사내 대체 명시
2. `pipelines/3-pptx/README.md` — Step 2.5 COM 시각검증 + Step 3 에디터 절차 정합
3. (확인) 시각검사 SSOT — Gemini 잔재 점검, COM/Playwright 경로 확정

## 단계
- [x] S1. SKILL.md §2.5 "생성 운영 절차 (Step 0~7)" 추가 — 협의/아웃라인승인/Marp초안/HTML/COM시각검증/에디터브라우저오픈/수정/변환 + PF_STEP 링크.
- [x] S2. SKILL.md §2.5 Step 2.5 = COM(export-slides-png.ps1)+Playwright(screenshot-html.mjs) 명시. Gemini VQA 이미지검수 한정·사내 skip 표기.
- [x] S3. pipelines/3-pptx/README.md 정정 — line 24 "Gemini Vision COM 사내제외" 오표기 → COM 시각검증 필수로 수정, 초안/에디터 (선택)→필수, Step 2.5 게이트 추가.
- [x] S4. scripts 6종 전부 실존 확인(draft-marp/editor-server/screenshot-html/export-slides-png/convert-native/preflight-html/html2pdf) + marp-cli devDep 확인. SKILL §2.5 flow ↔ scripts 1:1 일치.

## 검증 자산 (실존 확인 대상)
- `scripts/draft-marp.mjs` (Marp 초안)
- `scripts/editor-server.js` (비주얼 에디터)
- `scripts/screenshot-html.mjs` (Playwright HTML shot)
- `scripts/export-slides-png.ps1` (COM PPTX 프리뷰)
- `scripts/convert-native.mjs` (PPTX 변환)
- `scripts/preflight-html.js` (PF 검증)
