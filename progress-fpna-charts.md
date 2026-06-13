---
title: FP&A 차트 보완 진행
tags: [progress, fpna, charts]
date: 2026-06-13
---

# progress — FP&A 핸드오프 차트 보완

> plan-fpna-charts.md 참조. 각 차트 = 7지점 구현 + QA 게이트(preflight/validate-slides/screenshot) 통과 후 다음.

> **현 단계 = JS/SVG 시각본 갤러리** (병렬 subagent). PPTX 풀스택(.py + inference + validation + catalog)은 갤러리 승인 후 별도 단계.

## Phase 0 — 공유 프리미티브 / 레퍼런스
- [x] 0.1 chart-helpers.js 정독 (el/createSVG/fmt/colorVar/snap 프리미티브 확인) `model: opus`
- [x] 0.2 waterfall.js/py + donut.js 정독 — 색 전략 결정: **colorVar 인라인**(donut식), class 방식(waterfall)은 _ds_bundle 컴파일 의존이라 회피 `model: opus`

## Phase 1 — Bullet chart (1순위) — JS 시각본
- [x] 1.1 `assets/bullet.js` 렌더러 (밴드 rect + 측정 bar + target tick, 행별 독립 스케일) `model: opus`
- [x] 1.5 ★QA: 렌더 스크린샷 육안확인 → 틀어짐 0, `_review/1-bullet.png` 통과 `model: opus`
- [ ] 1.2~1.4 PPTX 렌더러 + inference + validation + catalog (갤러리 승인 후) `model: opus`

## Phase 2 — Tornado (2순위) — JS 시각본
- [x] 2.1 `assets/tornado.js` (발산막대, swing 내림차순, base 점선) — subagent `model: opus`
- [x] 2.4 ★QA: `_review/2-tornado.png` 육안 통과 (깔때기/색/라벨 정상) `model: opus`
- [ ] 2.2~2.3 PPTX + inference + validation + catalog (갤러리 승인 후) `model: opus`

## Phase 3 — PVM bridge (3순위) — JS 시각본
- [x] 3.1 `assets/pvm-bridge.js` (waterfall 확장, 가격/물량/믹스 색분리) — subagent `model: opus`
- [x] 3.4 ★QA: `_review/3-pvm.png` 육안 통과 (누적/색분리/connector/callout 정상) `model: opus`
- [ ] 3.2~3.3 PPTX + inference + validation + catalog (갤러리 승인 후) `model: opus`

## Phase 4 — Cohort heatmap (4순위) — JS 시각본
- [x] 4.1 `assets/cohort-heatmap.js` (ColorBrewer 연속 색보간, null 빈칸) — subagent `model: opus`
- [x] 4.4 ★QA: `_review/4-cohort.png` 육안 OK (세로채움+명도전환 수정 완료, 클리핑 회귀 되잡음) `model: opus`

## 갤러리 (사용자 리뷰)
- [x] G.1 `_review/index.html` — 4종 한 페이지 갤러리 (1-bullet/2-tornado/3-pvm/4-cohort .png) `model: opus`

## Phase 6 — 차트 선택 가이드 (자문 3R → decision tree 분기)
- [x] 6.1 자문 3R — gemini R1+R3 / claude R1+R2+R3. 수렴: 의도주축+시제게이트+파이프라인+변별cascade+핸드오프계약. SSOT=md(YAML 아님) `model: opus`
- [x] 6.2 `chart-routing-guide.md` — Gate0→시제→의도3패밀리→공통가지 파이프라인 + 변별 cascade + Excel↔Slide 핸드오프 계약 + mermaid `model: opus`
- [x] 6.3 claude-web runner-basic.js 수정 (Opus dropdown aria-label 보강 + 실패내성) — 자문 인프라 복구 `model: opus`

## Phase 7 — (자문 발견) 커버리지 보완 신규 차트 8종 — subagent 병렬, 전수 육안검증
- [x] 7.1 combo/dual_axis (매출막대+마진%선) — `_review/5-combo.png` 육안 OK `model: opus`
- [x] 7.2 driver_tree (ROIC=수익성×자산회전 분해) — `_review/6-driver-tree.png` OK `model: opus`
- [x] 7.3 scatter (조업도×원가+회귀) — `_review/7-scatter.png` OK `model: opus`
- [x] 7.4 scenario_summary (Base/Up/Down) — `_review/8-scenario.png` OK `model: opus`
- [x] 7.5 overlapping_line (계절성) — `_review/9-overlapping.png` OK `model: opus`
- [x] 7.6 heatmap (범용 발산) — `_review/10-heatmap.png` OK `model: opus`
- [x] 7.7 treemap (squarified) — `_review/11-treemap.png` OK `model: opus`
- [x] 7.8 breakeven (CVP) — `_review/12-breakeven.png` OK `model: opus`
- [x] 7.9 갤러리 index.html 12종 갱신 + guide §7 구현완료 반영 `model: opus`

## 남은 것 (사용자 승인 후)
- [ ] 8.1 신규 12종 PPTX 렌더러(.py) + inference 시그니처 + validation baseline + layout_catalog 등록 (현재는 JS/HTML 시각본만)
- [ ] 8.2 git 커밋 + push (현재 미커밋)
- [ ] 4.2~4.3 PPTX + inference + validation + catalog (갤러리 승인 후) `model: opus`

## Phase 5 — (선택) Small multiples + 통합 검증
- [ ] 5.1 small_multiples/trellis 레이아웃 (사용자 승인 시) `model: opus`
- [ ] 5.2 전체 회귀: 기존 64레이아웃 validate-slides 재확인 (신규 추가가 기존 깨뜨림 0) `model: opus`
- [ ] 5.3 커밋 + push `model: sonnet`
