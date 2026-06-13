---
title: FP&A 핸드오프 차트 보완 (Excel ↔ 슬라이드 패리티)
tags: [plan, fpna, charts, design-system, parity]
date: 2026-06-13
---

# FP&A 핸드오프 차트 보완 — 슬라이드측 갭 4종 추가

## 배경 / 결론 (자문 2모델 + 코드검증 종합)
- Excel 도구(28템플릿)와 슬라이드 도구(64레이아웃)의 포맷 겹침/갭 분석 결과,
  **갭의 거의 전부가 슬라이드(design)측**이다. Excel은 `add_waterfall`(floating base)·
  `add_bar_chart`(tornado swing) 헬퍼로 PVM·민감도 이미 완성.
- FP&A 핸드오프(임원이 보는 숫자) = variance/PVM · KPI/scorecard · trend/forecast ·
  sensitivity · unit_economics. 계산전용(debt/lease/allocation)·비주얼전용(swot/org)은 한쪽만 있어도 정상.

## 자문 출처 (provenance)
- Gemini Pro 1R: 우선순위 PVM>Tornado>Bullet>Cohort. 추가갭 = driver tree, forecast cone.
- Claude Opus 1R (Gemini 정정): `XL_CHART_TYPE.WATERFALL` python-pptx 미존재(PR#778 미머지) /
  `d3/d3-bullet` deprecated v3 / ECharts 워터폴도 비네이티브. 우선순위 Bullet>Tornado>PVM.
  핵심 통찰 = "공유 SVG bar-primitive 1개로 waterfall·PVM·tornado·bullet 4종 커버".
- 코드검증(adoption gate): design `chart-helpers.js` 공용 레이어 확인 → 공유 프리미티브 구조 타당.
  design `scorecard`=dots(정성)만 → bullet 정량 갭 진짜. Excel PVM/tornado 이미 완성.

## 우선순위 (Claude 순위 채택 — 결정변수 = 슬라이드 빌드원가, Excel측 이미 완성)
1. **Bullet chart** — 양쪽 진짜 0, scorecard(dots)로도 미커버, 빌드 최저, kpi_dashboard/scorecard/board_kpi_pack 동시 업그레이드. 레버리지 최고.
2. **Tornado** — Excel 완성·슬라이드 0. 1번 bar-primitive 재사용(중심축 대칭 발산). 한계원가≈0.
3. **PVM 전용 bridge** — Excel `pvm_bridge.py` 완성. `waterfall.js`/`data_special.py:waterfall` 확장(price/volume/mix 색분리 + subtotal).
4. **Cohort heatmap** — Excel `cohort_retention` 완성. table cell fill + HSL/ColorBrewer 보간(선형 RGB 금지=탁함).
5. (선택) **Small multiples/trellis** — 보드팩 단골(Claude 추가갭). 레이아웃 반복.

범위 제외: maturity wall(트레저리 한정+근사 존재), Excel측 신규(이미 충실).

## 구현 단위 — 신규 차트 1종 = 7지점 (waterfall 레퍼런스)
1. `design-system/pptx/deck_system/layouts/data_special.py` — `@register("X")` PPTX 렌더러(도형 좌표계산)
2. `design-system/mck/assets/X.js` — JS/SVG 렌더러 (chart-helpers.js 프리미티브 import)
3. `design-system/pptx/deck_system/builder/inference.py` — 시그니처 키 매핑
4. `design-system/pptx/deck_system/builder/validation.py` — `_baseline("X", ...)`
5. `design-system/layout_catalog.md` — 카탈로그 항목
6. `design-system/mck/slides/catalog-additions-*.html` — HTML 데모 1슬라이드
7. `design-system/pptx/deck_system/builder/builder.py` — 데모 빌드(선택)

## ★ 차트별 QA 게이트 (구현 중 깨짐 차단 — 사용자 명시 요구)
각 차트 구현 직후, 다음 통과해야 다음 차트 착수 (회귀 게이트):
1. **preflight** — `node scripts/preflight-html.js <html>` HTML 단계 9-check
2. **validate-slides** — `npm run validate` → 720×405pt 프레임 out-of-bounds 0건 (텍스트 오버플로우 자동 검출)
3. **convert-screenshot** — `npm run convert-screenshot` → 렌더 이미지 육안으로 겹침/잘림/정렬 확인 (사용자에게 SendUserFile)
4. PPTX 렌더러는 별도 `validate-pptx` 통과

## 공유 프리미티브 전략 (ROI 언락)
- JS측: `chart-helpers.js`에 `barPrimitive(svg, {x,y,w,h,fill,...})` + `divergingAxis` 헬퍼 신설
  → bullet(밴드+측정바+target tick) · tornado(중심대칭 발산막대) 공유.
- PPTX측: `data_special.py`에 동일 역할 도형 헬퍼.
- PVM = 기존 waterfall 확장(신규 수학 없음). Cohort = 독립(table fill).

## 리스크
- PPTX 렌더러는 SVG 아닌 python-pptx 도형 직접 그림 → JS와 좌표계 별도. 두 렌더러 동기 유지 필요.
- 색 보간(cohort) 선형 RGB 금지 → HSL/ColorBrewer hex stop 사용(런타임 의존성 0).
- 신규 양식 텍스트 오버플로우 = validate-slides 게이트로 매 차트 차단.
