---
title: 정답지 기반 룰 sweet-spot 튜닝 — 세션 인계
tags: [handoff, rule-audit, sweet-spot, ground-truth, btn-design]
date: 2026-06-14
next-action: VP-16 "fills %" 추정 폐기 → 렌더-잘림 검출로 교체(또는 임계 1.0→1.1). 그다음 VP-08/03/02/10 고확신만 남기고 축소, VP-11 WARN 침묵. plan.md "정답지 기반 sweet-spot 튜닝" 섹션 체크리스트가 기준.
---

# 정답지 기반 sweet-spot 튜닝 인계 (btn-design, 2026-06-14)

## 1. 현재 상태 · 첫 행동
- **목표 전환**: 개별 FP 줄이기(완료, 정밀도 35→47%) → **정답지 정의 + 정답 100% 잡는 한도(recall=1.0) 내 FP 최소화**. 사용자 핵심 지적: "예쁜 슬라이드에 경고 쏟아붓는 과민성이 문제".
- **방금 완료**: VP-04 WARN 임계 4.5→3.0 적용(`scripts/validate-pptx.js:38` CONTRAST_WARN). 운영 775→547, 정답 9건(ratio 2.1·1.9·2.3) 전부 생존=recall1.0. **미커밋** (다음 세션 커밋 또는 이어서).
- **첫 행동**: VP-16 sweet-spot. plan.md 체크리스트 순서대로.

## 2. 확정 정답지 (3-judge blind Opus 다수결, split 0 = 완전 합의)
**majority-REAL 13건** (룰이 반드시 잡아야 함, `C:/msys64/tmp/ab-verify/groundtruth.json`):
- VP-04 저대비 9: s2 청록"01~06"×6(#00C2FF 2.1:1), s7 청록2.1·초록1.9, s71 금색#D4A537 2.3:1
- VP-16 실제잘림 4: s71 막대내 "평균0.55"·"현재"(7pt 잘림), s99 제목wrap(부제 겹침)·"분석팀"(115% 잘림)
- FP 277 / UNVERIFIABLE(VP-11) 12

## 3. 사용자 박제 (대화 고유)
- "FP라 하면 너도 동의되는지 봐라. FP라 생각하고 보면 더 그렇게 보일수도" → 편향 프롬프트(범주별 "결함아님" 미리 알려줌) 교체 + 내가 직접 회의적으로 재확인 의무.
- "예쁘기만 하구만" → 린터 과민성이 진짜 문제. 잘 만든 슬라이드에 50+ 플래그.
- "정답은 다 맞추는 한도 내에서 fp 줄이는 sweet spot" → recall=1.0 hard 제약, precision 최대화.
- "Old new는 부수(副)로" → OLD/NEW 채점은 부차 지표로 유지(버리지 X).
- "teammate 3기 하네스2wf 스폰 참고" → 나는 Agent 도구로 in-process opus 3기 소환(blind). harness2-wf 완전 플로우(TeamCreate+role파일)는 아니고 그 핵심원리(공식프리미티브 in-process). 사용자가 완전형 원하면 전환.

## 4. 파일 인벤토리 (절대경로)
- 검증자산: `slides/rule-audit/ab-verify/` = gemini-judge.mjs(vision 헬퍼, GEMINI_RESEARCH_KEY 프로모키 필요·free키는 pro 미지원) / judge-criteria.txt(blind 렌더앵커 기준) / judge-flags.txt(302플래그 12장) / judge1~3.txt(3판정) / groundtruth.json(다수결 정답)
- 집계: `C:/msys64/tmp/ab-verify/aggregate.mjs`(OLD/NEW), 다수결은 inline node
- 12 검증슬라이드: 7·127·122·2·71·62·24·142·90·15·124·99 (이미지 `C:/msys64/tmp/ab-verify/img/slide_NN.png`)
- 코드: `scripts/validate-pptx.js` (CONTRAST_WARN:38, checkCjkTextOverflow:1226 VP-16 3분기, checkFilledEmptyShapes VP-08, checkContrast:740)
- OLD 룰 추출: `git show 7ba82bb:scripts/validate-pptx.js > scripts/_vOLD.js`(jszip 위해 design 내 실행, 후 rm)

## 5. 다음 단계 (sweet-spot, recall=1.0 제약)
- [ ] **VP-16**(최대 FP원): "fills %" 추정 발화 = 정답 0건인 95-110% FP 다수. 정답 4건은 실제잘림. → 옵션A: 임계 1.0→1.1(95-110% 침묵, >110% 유지) 옵션B: 렌더 텍스트↔소스 비교로 실제잘림만(정밀하나 렌더필요). 적용후 정답4 생존 확인.
- [ ] **VP-08/03/02/10**: 정답 0건 = 거의 전부 FP. 발화 자체 고확신만 남기고 축소 또는 INFO 강등.
- [ ] **VP-11**: UNVERIFIABLE → WARN 침묵(별도 a11y 채널 분리 가능).
- [ ] 튜닝후 12장 재측정: recall=1.0 유지 + precision 47%→↑. OLD/NEW/TUNED 3자 채점(부수).

## 6. 자문 종합
- **Gemini Pro vision 단독 = 신뢰불가**(검증): 같은 슬라이드서 110% "FP맞음"·95% "REAL위험"으로 모순 confabulate. VP-11(탭순서)은 못 보고 "접근성=REAL" 기본값. → 3 blind Opus 다수결로 교체(confabulation 2:1로 걸러짐, split 0 달성).
- 내 독립확인: s122 VP-16 "REAL"이 Gemini 지어냄(실제 한줄에 맞음) 직접 반증.
- 커밋 이력: 이번세션 b110263~57245ad(FP감축+FN검증+커버리지). VP-04 sweet-spot은 미커밋.

<!-- created: 2026-06-14, ctx 648k long-mode maxed -->
