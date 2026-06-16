---
title: 10슬라이드 × 8테마 e2e 검증 결과 (R13+R14 = 80장)
tags: [design-system, e2e, findings, multi-format-verify]
date: 2026-06-17
method: 헤드리스 Chrome HTML 렌더(1280×720, ~1초/장) ↔ COM PPTX 렌더(4000×2250) 교차비교 + 변환기 CONTRAST/ERROR 전수 sweep
---

# 10×8 테스트 결과 — 80장 (R13+R14, 8테마)

## 검증 방법 (다중포맷 교차)
- **HTML 원본**: `scripts/render-html-batch.sh` → 헤드리스 Chrome 1280×720 PNG, `slides/_render-check/r{R}-{theme}-s{NN}.png`. 80장 ~3분. 디자인 의도 기준.
- **PPTX 실전**: COM 렌더 `slides/round{R}-{theme}/png/slide_0{N}.png` (4000×2250).
- **변환기 sweep**: 16덱 재변환하며 `CONTRAST WARN|VP-04|ERROR|invisible|omitted` 전수 캡처. = 색 대비 ground truth (눈대중 대체).
- ⚠️ **이미지 API 한도**: COM PNG 4000px라 한 컨텍스트 누적 시 many-image 거부. 색 검증은 변환기 sweep로 우회(색=HTML=PPTX 동일).

## 변환 충실도 (실전 = PPTX)
- **ERROR / invisible-text / omitted / failed = 8테마 16덱 전수 0건.** 변환 실패·요소 누락·투명텍스트 없음.
- modern 10장 중 레이아웃/잘림 결함 = R14 s02 1건뿐. 나머지 9장(표·막대차트·타임라인·3패널·4단계·다크체크리스트) 완전 보존.

## 수정 현황 요약 (2026-06-17)
- **D2 [색] = 수정완료·검증✅** — "금액" 헤더 `.chd.cv p { color:surface-inverse-fg }` 1줄. academic·executive 재변환서 저대비 warn 소멸.
- **D1 [잘림] = 수정완료·검증✅** — g-note `<div><p>텍스트</p></div>` 분리(학습⑮). 엔진 무수정. 서브에이전트 풀사이즈 재확인: "금 유출" 온전·.g-d 온전·레이아웃 정상. 근본 = bordered leaf-div→shape+text→PptxGenJS가 fit:'shrink' 무시(html2pptx 420-425). ⑮ 분리로 text 경로 복귀.
- **D3 [텍스트버그] = 미수정** — 엔진(변환기) 버그라 GT baseline 재구축 후 진단 필요. 아래.

## 확정 결함 (원본 기록)
### D1 [변환/레이아웃] R14 slide-02 가이드 다크패널 텍스트 잘림 → ✅수정
- `.g-d`/`.g-note` 가 우측 패널경계서 잘림 → 글자 유실. 실측: g-note "…매년 현[줄바꿈]이 고정된다"에서 "금 유출" 소실. modern+executive PPTX 양쪽 확인. 모든 테마 공통(테마불변).
- **근본 가설**: `.guide` = grid `0.9fr` narrow 컬럼. 변환기가 `.g-d` 박스를 1줄 높이로 측정 + 패널폭 clamp → HTML에선 wrap되던 텍스트가 PPTX선 가로 overflow 잘림. (HTML 원본은 패널이 넓어 1줄에 들어가나, PPTX는 패널이 좁게 렌더돼 폭 불일치.)
- **수정 방향** (사용자 우선순위): (2순위) 엔진 = html2pptx 측정/clamp가 narrow 패널 wrap 텍스트를 세로로 키우게 / (1순위 fallback) 슬라이드 = `.g-item` min-width:0 또는 텍스트 패널폭 맞춤. ⛔ 정탐회귀0(GT) 필수.

### D2 [색 · academic+executive 한정] R14 slide-01 패널3 "금액" 표 헤더 저대비
- "금액" 헤더 셀이 `var(--accent)` 색 → 다크 surface-inverse 헤더 위. academic #2E75B6 on #1F4E79 = **1.79:1**, executive #1428A0 on #1A1A1A = **1.53:1** (VP-04 fail). modern 등 밝은 accent 테마는 통과.
- 같은 슬라이드 "구분" 헤더는 `surface-inverse-fg`(정상). "금액"만 accent 오용.
- **수정** (1순위, 원안보존): "금액" 헤더 color를 `var(--accent)` → `var(--surface-inverse-fg)`로 (형제 "구분"과 동일). 헤더 라벨은 강조 대상 아니므로 의도 손상 0. 슬라이드 1줄 수정.

### D1 정밀확정 (서브에이전트 a0ff4e17, 풀사이즈)
- modern note "…매년 현[잘림]이 고정된다" = **"금 유출" 3음절 유실 확정**. ★executive 변형은 전문 온전 = **테마불변 아님, modern 폰트 메트릭이 needLines=1.19 경계를 넘김**. → fit:'shrink'가 g-note(leaf-div) 경로엔 안 먹는 의심.

### D3 [확정·변환기 텍스트버그] R13 slide-01 각주 "분." 중복
- 서브에이전트 풀사이즈 확정: HTML 정상("…산입분. 퇴"/"직 직전…"), PPTX는 "…산입분."/**"분.** 퇴직…" = 2행 첫머리 "분." 중복 삽입. 클리핑과 별개 = 줄바꿈 경계 텍스트 이중방출 의심(loose-text Range 경로 1108~1130 또는 wrap 처리).

## 비결함 (의도된 디자인 — 수정 대상 아님)
- 주황 accent #E87722/#FF6F00 on 라이트(#F0F0F0/#FFFFFF) = 2.60~2.96:1. 브랜드 강조색(보통 굵게), 전 테마 균일. WCAG AA(4.5) 미만이나 의도된 accent 처리 → 디자인시스템 속성이지 라운드 결함 아님 (시스템 수정 = 검증대상 개조라 범위 밖).
- 배지 숫자 흰글씨 on accent원(#4A9EFF/#00A9E0 등) = 2.5~2.85:1. 동일 범주, 가독 OK.

## 자기정정 기록
- 중간보고서 "executive navy 다크패널 제목 6슬라이드 체계적 저대비"는 **눈대중 오판**. grep 결과 다크패널 제목 전부 #FF6F00 하드코딩(학습② 준수)이고, 변환기 sweep 결과 진짜 <2.0 저대비는 "금액" 셀 1개뿐. → 눈대중 대신 변환기 대비데이터를 ground truth로 채택(empirical-claim 정정).

## 최종 상태 (2026-06-17)
- **D1·D2 = 수정·검증·락인 완료.** R14 8테마 전수 재변환 = ERROR 0 / 저대비<2.0 0. D1은 modern 풀사이즈 서브에이전트 재확인 OK.
- **R13 = 무수정** (D3만 있고 보류). R13 다크패널 제목은 전부 #FF6F00이라 색 문제 없음(sweep 확인).

## D3 큐잉 — 다음 엔진패스 (회귀가드 선행 필수)
- **증상**: R13 s01 좌패널 각주(`.fm-note`, leaf-div 무border) "…산입분.[줄바꿈]**분.**퇴직…" = 줄바꿈 직후 "분." 음절 중복 방출. 변환기 텍스트버그(클리핑·누락 아님).
- **진단 시작점**: `.fm-note`는 border 없는 leaf-div → text 경로. 중복은 wrap 경계 텍스트 이중방출 의심. 후보: (a) loose-text Range 경로 html2pptx 1108~1130 (block자식 보유 컨테이너의 직속 텍스트노드 emit) — 단 fm-note는 leaf라 비해당 가능 (b) leaf-div parseInlineFormatting(1363~1384) + 별도 경로 중복 (c) CJK width보정 후 PptxGenJS 줄나눔 시 음절 재삽입. 재현 = R13 s01만, 특정 wrap 지점.
- **선행조건**: ⛔ 엔진 수정 전 **slides-grab GT baseline 재저장** 필수. 현 `full-baseline.json`은 design repo round 덱 기준(미스매치, 5970 resolved+570 new). 명령: `REGRESSION_SLIDES_DIR=/d/projects/slides-grab/slides node tests/run-full-regression.mjs --save` → 수정 후 동일 env로 재실행 delta=0 확인.
- **우선순위**: 경미(각주 1음절). 엔진 버그라 다른 슬라이드 재발 가능성만 주의.

## 잔여 (light)
- R14 non-modern 테마 png/ = 수정 전 렌더(stale). 변환기 sweep로 클린 확인했으나, 원하면 COM 재렌더 후 테마별 풀사이즈 최종 시각재판정.
