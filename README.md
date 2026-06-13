# design — 사내 보고서 생성 파이프라인

사내 Claude Code 에서 보고서를 만들 때 쓰는 자산 모음. **본문 텍스트 → PDF → PPTX** 세 갈래를
하나의 진입점(`SKILL.md`)에서 의도에 따라 라우팅한다.

slides-grab(변환 엔진·파이프라인)과 design-system(디자인)을 사내 환경에 맞게 이식했다.

## 사내 환경 전제

- **지식 소스 = 사내 DB + WebFetch/WebSearch 직접 + Confluence(위키·용어집)** 3종으로 한정.
- OAuth 키 불가 → **Gemini 이미지 생성·Gemini Vision·NotebookLM 전부 불가**. 관련 자산은 `_archive-company-blocked/` 로 분리.
- 이미지는 차트/표/도형 우선, 사진형은 placeholder/수동 배치.
- 폰트는 외부 CDN 대신 로컬 `.woff2` 번들(`design-system/fonts/files/`).

## 구조

```
SKILL.md                  진입점 — 의도(1/2/3) 판별 + 공통 코어 + 규칙 SSOT 맵
rules/
  content-authoring.md    본문 작성 뼈대 (논증·액션타이틀·§13 검증 게이트·워크플로우·엑셀 데이터 보고서)
  research-sourcing.md    사내 3소스 리서치 + 출처 태그 규칙
design-system/            디자인 SSOT — 8테마·레이아웃 카탈로그·PF룰·QA·토큰·로컬폰트
pipelines/
  1-report-text/          본문 텍스트(.md). 엑셀/DB 데이터 보고서도 여기 기준
  2-pdf/                  회람용 문서(.pdf)
  3-pptx/                발표자료(.pptx)
scripts/                  변환·검증 엔진 (HTML→PPTX/PDF, preflight, validate, 가드)
skills/                   pptx-skill(변환엔진 html2pptx+ooxml) · ppt-{plan,design,pptx,presentation}-skill
src/                      에디터 모듈 (localhost 전용)
bin/                      CLI 진입점
tests/                    회귀·e2e 테스트 (vision 제외)
docs/                     slides-grab 원본 운영자산 (참고)
  conversion-rules/       html-prevention·HTML예제·QA·테스트·보고 규칙
  pipeline-steps/         PF_STEP_*·PRESENTATION_FLOW (회사의존 단계 배너)
  design-reference/       DESIGN_MODES·RESEARCH_SUPPLEMENT
  slides-grab-docs/       설치·프롬프트·원본 plan·README-KO
assets/, _archive-company-blocked/
```

> `docs/` 의 slides-grab 원본 규칙은 **참고용**이다. 운영 SSOT 는 `SKILL.md`·`rules/`·`design-system/` 이 우선하며, 회사의존(Gemini/NotebookLM) 단계는 각 문서 상단 배너로 무력화했다.

## 파이프라인 (의도별)

| 의도 | 파이프라인 | 출력 |
|---|---|---|
| 본문만 / 엑셀·데이터 보고서 | 1. report-text | `.md` |
| 회람 문서 (발표 없음) | 2. pdf | `.pdf` |
| 발표자료 | 3. pptx | `.pptx` |

2·3 도 내부적으로 1(본문 확정 + 검증)을 먼저 거친다. 공통 코어 = brief 1장 → 고스트덱 → §13 검증 게이트.

## 설치 / 사용

```bash
npm install            # playwright chromium 포함 (postinstall)

# 본문 → HTML(design-system) → 변환
node scripts/convert-native.mjs --slides-dir slides/<slug> --output <slug>.pptx --full   # PPTX
node scripts/html2pdf.js        --slides-dir slides/<slug> --output <slug>.pdf            # PDF
node scripts/editor-server.js   --slides-dir slides/<slug>                                # 로컬 에디터
```

각 파이프라인 상세는 `pipelines/<n>/README.md`, 디자인 규칙은 `design-system/SKILL.md` 참조.

## 출처

- 변환 엔진·파이프라인: slides-grab (사내불가 의존 제거본)
- 디자인 시스템: slides-grab Design System
- 본문 작성 규칙: analytical-slide-coauthoring (사내 적응 + 환각 검증 게이트)
