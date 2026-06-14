---
title: VP 정답화 + PF-71 보강 + 표본확대 FP발견 — 세션 인계
tags: [handoff, rule-audit, vp-pf-crossverify, sample-expand, btn-design]
date: 2026-06-15
next-action: 표본확대(subagent 38장)로 드러난 미확인 FP 처리 — ① phantom 흰글씨 배경추적 버그(VP-04 findBackgroundColor) ② VP-16 미확인 14장 잔존FP ③ ★강조색(청록#00C2FF·금색#D4A537·green#03C75A) GT충돌 = GT 재정의 결정(자문 권고). §5 우선순위 순.
---

# VP 정답화 + PF-71 + 표본확대 FP 인계 (btn-design, 2026-06-15)

## 1. 현재 상태 · 첫 행동
- **완료**: Phase1 VP 16룰 정답화(거짓FP 전수제거, 발화=VP-04 92+VP-16 27 TP만, errors14 WARN119 GT13/13) + Phase2 PF-71 신규(VP-04 floor2.124 이식, PF-clean→VP-04clean, realmix 99≈VP-04 92). 커밋 76ea1dd~22419b8.
- **미완(표본확대 발견)**: 이미지 직접판정이 ~30장(50미만)이라 사용자 "VP 일부만 본다" 지적 → subagent로 VP-04/16 미확인 38장 판정 → **다수 미확인 FP 발견**(§3). 이게 핵심 잔여.
- **첫 행동**: §5 우선순위 — phantom 흰글씨 버그 수정부터. ctx critical로 이번 세션 중단, 다음 세션 재개.

## 2. 진행 맵
- realmix.pptx(C:/msys64/tmp/realmix.pptx, 156장) 전수 발화측정 + 룰별 대표 이미지판정.
- 이번세션: VP-14 장식글자 E7→0 / VP-07 h0셀 W2→0 / VP-09 lines>=3 W9→0 / VP-10 그룹게이트 W1→0 / VP-02 너비끔 W9→0 → VP 발화=VP-04 92(저대비)+VP-16 27(잘림)만.
- PF-VP 교차테스트: VP-16잘림은 PF-25/03이 막음 ✓ / VP-04저대비는 PF구멍 → PF-71 신규.
- ★표본확대(subagent a04d73f5): VP-04 미확인27 + VP-16 미확인14 = 38장 이미지판정 → §3 FP발견.

## 3. ★표본확대 subagent 판정 (38장, 핵심 미해결)
**VP-04 (저대비)**:
- TP 4건만: s16/19/20/49 = 흰텍스트 on 연한파스텔(스틸블루#B0C4DE·회색#CCCCCC) 막대/원형 = 진짜 가독불량. (양쪽 동의)
- **FP 다수**:
  - ★phantom 흰글씨 오측정(s43/59/122): #FFFFFF-on-#F5F5F5/#EEEEEE ~1.1 — 실제 흰글씨는 컬러뱃지/막대 위인데 VP-04가 뒤 카드배경 대비로 오측정 = **findBackgroundColor 버그**(즉시배경 뱃지 대신 큰 카드배경).
  - 장식 glyph(s123): #CCCCCC "+" 구분기호를 본문 취급.
  - ★강조 accent color(s3/4/6/10 청록#00C2FF · s32/33/35/40/41 green#03C75A · s72/81/83/109 금색#D4A537): ratio 1.9~2.1로 floor에 걸리나 "대형 bold 강조라 또렷이 읽힘 FP" 판정.
**VP-16 (잘림/겹침)**:
- TP 0건. FP 15장 전부(s26/61/73/74/75/76/77/79/81/82/83/89/113/117): wraps=정상다단, fills 100~118%=막대/박스 내 수용, will overflow 미실현. 실제 잘림/겹침 0관측.

## 4. ★강조색 GT 충돌 (최중요 미해결, 자문 권고)
- subagent: 청록#00C2FF/금색#D4A537 = "읽힘 FP"
- GT(3-judge blind 다수결): **같은 청록#00C2FF(2.07)·금색#D4A537(2.118) = REAL** (groundtruth.json realIds 2.3~2.8, s2 청록6·s71 금색).
- 정면 충돌. GT 9건 중 VP-04가 이 강조색. subagent가 FP라면 GT 정의·floor2.124·PF-71 전부 흔들림.
- ⚠️ subagent도 "FP 찾아라" 프롬프트라 바이어스 가능(사용자 기존 경고 "FP라 생각하면 더 그렇게 보임"). 단일 subagent vs 3-judge.
- **결정 필요**: "읽히는 강조색 저대비(ratio 2.0~2.12)"를 REAL로 둘지 FP로 뺄지 = GT 기준 사용자 판단. 권장: /gemini-web + /claude-web 자문(제3 의견) 또는 사용자 직접 결정. floor를 더 낮추면(예 1.9) 강조색 빠지나 GT 금색2.118도 위태.

## 5. 다음 액션 우선순위 (recall=1.0 제약 유지)
1. **phantom 흰글씨 버그**(명백, GT무관): VP-04 checkContrast의 findBackgroundColor가 텍스트 즉시배경(작은 컬러뱃지/막대) 대신 큰 카드배경을 잡음. → 텍스트와 가장 작게 겹치거나 가장 가까운 fill 도형(뱃지) 우선 탐색. s43/59/122 phantom 흰글씨 제거. 회귀: GT 9건 영향 0 확인.
2. **장식 glyph**(명백): VP-04에서 단일 구분기호("+"·"·" 등 1자 비단어)를 본문 제외. s123.
3. **VP-16 미확인 14장 FP**: wraps/fills/will이 막대·박스 내 수용인데 발화. 이미 겹침/세로넘침/격자 게이트 적용했으나 14장 잔존. 추가 정밀화 or 막대(차트) 컨텍스트 제외. GT VP-16 4건(s71/99) 보존 필수.
4. **★강조색 GT 재정의**(§4, 자문/사용자 결정 후): REAL 유지 시 현행 / FP 결정 시 floor·PF-71 동반 조정 + GT 재산정.

## 6. 파일 인벤토리 (절대경로)
- 엔진: `D:/projects/design/scripts/validate-pptx.js`(VP, checkContrast=findBackgroundColor) + `preflight-html.js`(PF-71 line~1762)
- 기록: `D:/projects/design/slides/rule-audit/VERIFICATION.md`(전과정 박제, ★강조색 FP발견은 미기록 — 다음세션 추가)
- 정답지: `slides/rule-audit/ab-verify/groundtruth.json`(GT13, 청록/금색 REAL)
- 이미지: `slides/rule-audit/regr-img/`(40+장, subagent가 38장 추가렌더)
- subagent 결과: 대화로그(agentId a04d73f5ed110a013, SendMessage로 재개가능) — §3 데이터가 그 요약
- 측정 헬퍼: `/tmp/wrapfix.mjs`(GT13 보존+카운트), `/tmp/vpall.mjs`(VP룰별), `/tmp/vp10.mjs`(VP-10)

## 7. 미해결·실패한 시도
- 강조색 GT 충돌 = 미해결(§4). subagent 단일판정 신뢰도 의문(바이어스). 3-judge GT와 충돌.
- VP-09 slide4 FN 실측 실패: convert-native가 slide4(dense) omit/처리 → 게이트 전후 동일 0. 로직상 3줄+ 유지로 FN 안전 판단했으나 진짜 3줄과밀 실증은 미완.
- ctx: long-mode on2(750k) 가동 중. 이번세션 ~620k에서 핸드오프.

## 8. 사용자 박제 (대화 고유)
- "VP 일부만 본다·정공법 FP0" → 표본확대 동력. 30장→38장 추가로 FP 발견 = 지적 정당.
- "PF는 생성규칙(답)이라 PF-clean인데 VP걸리면 PF구멍" → PF-71 신설 근거.
- "잔존 ㄱ" → VP-09/10 게이트.
- 기존 경고 "FP라 생각하면 더 그렇게 보임" → subagent 강조색 FP판정 바이어스 의심 근거.
