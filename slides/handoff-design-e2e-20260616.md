---
title: 디자인 e2e 검증 핸드오프 — 테스트 자산 75장 + 워크플로우
tags: [handoff, design-system, e2e, btn-design, test-asset]
date: 2026-06-16
next-action: "R12 착수 — plan-design-e2e.md §0.6 R12 소재 5장(payroll-guide/02·payroll-v2/17·samsung/12·payroll-guide/07·15) Read 복잡도 검증(목차/단순이면 교체) → modern 베이스 생성 → sed 8테마+editorial serif → convert-native.mjs PF변환 → COM 의도보존+K규칙+정탐회귀0"
---

# 디자인 e2e 검증 핸드오프 (2026-06-16)

## §1 현재 상태 · 첫 행동
- **완료**: R1~R11 (8테마×5장 = 라운드당 40슬라이드, 총 440슬라이드). 최신 커밋 `96b5858`.
- **클린카운터 = 0** (R9 화살표글리프·R10 드리프트+규약·R11 nowrap겹침 = 모두 결함 발견·수정 라운드라 클린 아님). **종료조건 = 2연속 클린**(신규 변환기버그0+디자인결함0인 라운드 2회 연속).
- **★첫 행동**: R12 착수 — `plan-design-e2e.md §0.6` R12 소재 5장 **Read 복잡도 검증**(목차/단순/일러스트면 후보풀서 교체) → 생성 워크플로우(§5).

## §2 진행 맵 — 테스트 자산 SSOT
- **테스트 자산 정의**: slides-grab 복잡 슬라이드 = **복잡도 레퍼런스 소재 + 룰회귀 read-only GT**(변환 대상 아님). **변환·검증 대상 = `slides/round{N}-{theme}/slide-01~05.html` (N=1~15, theme=8종) = 라운드당 40장**.
- **라운드맵 = 75장** (15라운드 × 5장, plan §0.6): R1~R10 = 초기 50장(소진 완료) / **R11~R15 = 신규 25장**(2026-06-16 선발).
  - R11(✅생성·검증완료): seoul/29 SWOT · tax-jv/16 5step · payroll-guide/28 α계수표 · samsung/11 비교표 · payroll-v2/34 일정표
  - R12(✅Read검증완료·생성중): payroll-guide/10(누적비율9행표+스택바+계수패널) · payroll-v2/17(일용vs상용8행표) · samsung/12(듀얼패널비교표) · payroll-guide/07(최저임금3패널) · payroll-guide/13(4대보험5×5표+다크계산패널). ★02목차→10교체·15디바이더→13교체(Read검증서 목차/디바이더 판정)
  - R13(⏳): payroll-guide/22 · payroll-v2/19 · samsung/13 · payroll-guide/27 · payroll-guide/23
  - R14(⏳): payroll-guide/29 · payroll-v2/22 · samsung/15 · payroll-guide/33 · payroll-guide/24
  - R15(⏳): payroll-guide/36 · payroll-v2/23 · samsung/08 · payroll-guide/05 · payroll-v2/35
- **R12~R15 선발 근거**: 미사용 복잡 grep(`grid-template`/`display:grid` ≥2 AND `<img|<svg` ≤1) 데이터밀집. **⚠️ grep 잠정선정 — 착수 시 Read 검증 의무**(grep 高 ≠ 복잡: tax-jv/02·payroll-v2/30 목차/단순 사례 있음). 미사용 데이터밀집은 payroll/samsung 집중(다른 덱은 차트/목차/일러스트 혼재).
- **후보풀 잔여(교체용)**: payroll-guide/v2 미사용 다수 · tax-jv/03/09/10/11/12/15/17/18(목차/요약 주의) · seoul-marketing(차트/단순) · iran-crisis/mesozoic/noahs-ark(일러스트).

## §3 사용자 박제 (대화 고유 framing)
1. **PF/VP 통과만이 목표 아님 — 원안 디자인 의도 구현도 동급 목표**. PF/VP 맞추려 디자인 깎지 말 것.
2. **⛔검증 중 디자인시스템(검증 대상) 임의 개조 = 드리프트**. `design-system/` 토큰(colors_and_type.css)·규칙(*.md)·템플릿 수정 금지. 허용 수정범위 = 변환기(scripts/·html2pptx)·룰게이트(validate/preflight)·슬라이드 산출물(slides/round*)뿐. 시스템 본체 개선 필요시 검증 **밖** 별도 작업+사용자 승인. (근거: 내가 executive 저대비에 `--accent-on-dark` 토큰 발명→사용자 "스킬 개조=드리프트" 지적→원복)
3. **타협선**: 결함은 "원복 vs 개조" 이분법 아님 — 디자인시스템 규약(prompting_rules)에 답이 있으면 **슬라이드를 규약에 맞춤**. executive navy 다크저대비 = 슬라이드가 §4.3(다크는 surface-inverse-fg) 위반 → 다크패널 강조를 fg+weight로 수정(시스템 무개조).
3b. **★수정 우선순위 (사용자 2026-06-16 명시)**: 결함 발견 시 (1순위) **디자인 원안 최대한 살림** — PF/VP 통과 위해 디자인 깎기 최소화 (2순위) **엔진(변환기 html2pptx.cjs) 수정** — 변환기가 원안을 못 살리면 변환기를 고침 (3순위) **회귀 보면서 PF/VP 룰 미세 수정 가능** — 룰 과탐이면 GT 17덱 정탐회귀0 확인하며 게이트 미세조정. 즉 "슬라이드 깎기"는 최후순위, 엔진/룰 수정이 원안 보존에 우선.
4. **합성 e2e 자산(`slides/e2e-*`/e2e2-*/e2e3-*/e2e4-*) = 폐기대상**(타입발명 드리프트). 삭제 여부 사용자 확인 대기.
5. **자율주행**: 2연속 클린까지 진행, ctx 한계 시 압축 후 재개.

## §4 파일 inventory (절대경로)
- 정식 자산: `D:/projects/design/slides/round{1..11}-{theme}/slide-0{1..5}.html` (+ png/, out.pptx)
- 라운드맵 SSOT: `D:/projects/design/plan-design-e2e.md` §0.6 (75장)
- 진행 마커: `D:/projects/design/slides/progress.md` (Working Notes ckpt)
- 자산 인덱스: `D:/projects/design/slides/RENDERED-ASSETS-INDEX.md`
- 디자인시스템(검증대상): `D:/projects/design/design-system/` (colors_and_type.css 토큰, prompting_rules.md §4.2 accent 1곳/§4.3 다크=inverse-fg)
- 변환기: `D:/projects/design/scripts/convert-native.mjs` → `skills/pptx-skill/scripts/html2pptx.cjs`. NODE=`/c/Program Files/nodejs/node.exe`
- 폐기대상: `D:/projects/design/slides/e2e-*`·`e2e2-*`·`e2e3-*`·`e2e4-*`

## §5 워크플로우 (라운드당 5단계) — 방법 SSOT
1. **소재 검증**: plan §0.6 해당 R 5장 경로 → **각 Read 복잡도 확인**(목차/단순/일러스트면 후보풀서 교체).
2. **modern 베이스 생성**: 각 소재 내용·구조를 design-system 토큰으로 `slides/round{N}-modern/slide-01~05.html` 5장. ★학습 선적용(§6).
3. **8테마 propagate**: sed 6테마(`s/data-theme="modern"/data-theme="{t}"/`: classic·company·academic·dark-mono·dark-pitch) + executive(`executive-editorial`) + editorial(sed + awk serif 주입: `box-sizing:border-box; }` 줄 뒤 `.serif-head, h1,h2,h3,h4,h5,.ctitle,.kicker { font-family:'Newsreader','Times New Roman',serif; }`).
4. **PF변환**: `"$NODE" scripts/convert-native.mjs --slides-dir slides/round{N}-{t} --output slides/round{N}-{t}/out.pptx` (8테마, ⛔--skip-preflight 금지). ERROR 4종 grep = `found N ERROR|❌|invisible-text|failed to convert|omitted|0-byte`.
5. **COM + 판정**: `export-slides-png.ps1` → png 1366px resize(System.Drawing, `-replace '\.png$'` escape 주의) → Read 핵심 계열(modern 5장+다크2+executive+editorial). 의도보존 + K규칙(룰과탐=게이트수정/변환기결함=변환기수정/디자인결함=슬라이드수정) + 정탐회귀0(GT 17덱 ERROR delta0).

## §6 누적 학습 (생성 시 선적용 체크리스트) — promotion-log K 박제
- ①heading=`var(--heading,var(--primary))` ②**다크패널(surface-inverse) 내 강조=`surface-inverse-fg`+weight 차이, accent 색강조는 라이트 배경에서만**(K-202606161045, navy 다크저대비 회피) ③긴텍스트 nowrap은 div+p ④복합셀=표패턴 단일p ⑤연한톤bg 고정hex/rgba 금지→테마토큰 ⑥배지=div>p+nowrap ⑦행많은표 720초과 silent drop→padding축소 ⑧색칩=div 직속텍스트+width명시(invisible방지) ⑨카드불릿=단일p ⑩좌우분할 head=htext/hero 둘다 width+flex-shrink:0 ⑪다이어그램=직교화살표만(↘↗ 폰트폴백 깨짐) ⑫**카드형 라벨+본문에서 본문 itext에 white-space:nowrap ⛔금지**(변환기 인라인 오인→형제 겹침, K-202606161200, nowrap 제거+flex column) ⑬데이터 의미색 중 어두운색(navy)은 다크테마 카드 저대비→밝은 대체(cobalt #2563EB) ⑭**박스/행 내 라벨좌+값우 양끝정렬=`display:grid;grid-template-columns:1fr auto`+자식 block(p)**. ⛔flex justify-content:space-between 변환기 미지원(2텍스트 병합 "기본급100%"), ⛔grid item에 inline span 금지(텍스트노드 병합)—표(.gt)가 정상인 이유=div>p block셀. (K-202606162210, R12 slide-01).

## §7 미해결 · 자문종합
- **미해결**: (a) e2e-* 합성자산 삭제 여부(사용자 확인 대기) (b) R12~R15 복잡도 미검증(착수 시) (c) 클린 2연속 미달성(현 카운터 0).
- **드리프트 전수검토(Explore subagent a3d165d, 2026-06-16)**: R1~R10 design-system 변경 커밋 전수 → **임의개조 드리프트 0건**. 폰트추가·pf_rules 문서↔코드 동기화·템플릿 PF-07준수·legacy토큰14개 추가 전부 정당. working tree clean.
- **학습 ERROR**: ERROR-202606161030(검증 중 디자인시스템 토큰 발명 드리프트→원복). promotion-log head 참조.
