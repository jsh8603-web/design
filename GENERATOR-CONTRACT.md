---
title: 생성기 변환-안전 계약 (Generator Converter-Safety Contract)
tags: [design-e2e, generator, converter-safety, contract, ssot]
date: 2026-06-18
scope: "슬라이드 HTML 생성 주체(메인·서브에이전트)가 생성 단계부터 준수하는 변환-안전 마크업 계약 SSOT"
note: "★루트 배치 의도 = design-system/ 물리적 무수정(핸드오프 §3 드리프트 경계 준수). 본 파일은 기존 규칙의 통합·포인터이며 새 토큰/테마/레이아웃을 발명하지 않는다(prompting_rules.md §12 sanctioned)."
---

# 생성기 변환-안전 계약 (Generator Converter-Safety Contract)

> **목적**: html→pptx 변환에서 "매 라운드 1~3개씩 재발하던 결함"의 근본은, 이미 아는 마크업-안전 규칙(누적학습 16 + idiomatic 6)이 **생성기에 박혀있지 않고 수동 적용**돼 빠뜨려서다. 이 파일은 그 규칙 전부를 **한 곳에 front-load** 해서 "한 번에 제대로 변환"되게 한다.
>
> **드리프트 경계 (핸드오프 §3)**: 본 계약의 모든 규칙은 **"같은 그림을 변환기가 그릴 수 있게 마크업 구조만 바꾸는 것"** — 디자인 언어(색/테마/레이아웃/크기/간격)는 **불변**. 시각이 1px이라도 바뀌면 그건 계약이 아니라 드리프트다(§D 게이트가 차단).
>
> **원본 SSOT**: `design-system/prompting_rules.md` §7·§10 + `slides/handoff-design-e2e-20260616.md` §6(학습 16) + `.harness2/complex-spec5.md`(idiomatic 6). 본 파일은 그 통합 뷰 + 정적-린트 매핑.

---

## §A 변환-안전 하드 규칙 (생성 시 절대 준수)

각 규칙 = **금지 패턴 → 시각 동일 안전 대체 → 린트 상태**. 린트 상태: `[PF-NN ✅]`=정적 차단됨 / `[동적]`=변환·렌더 시 검출 / `[GAP→P1]`=정적 갭, Phase 1 신규 룰 예정 / `[규약]`=작성 규약(자동검사 없음).

### ★A0 슬라이드 Envelope (최우선 필수 — 누락 시 변환 FAILED)

⚠️ **모든 슬라이드는 아래 골격을 그대로 써야 한다.** stress-c1 사이클1에서 6장 중 5장이 이 골격 누락으로 변환 FAILED(body 0.8"~4.4" 붕괴 / 가로 overflow). 작동하는 round 슬라이드는 전부 이 골격이고, `prompting_rules.md §9` 스켈레톤(`<section class="slide--themed">` + `.t-*` 클래스)은 **이 골격을 누락한 drift** — §9 글자 그대로 따르면 실패한다. (§9는 design-system 동결이라 본 A0가 실효 SSOT.)

```html
<!DOCTYPE html>
<html lang="ko" data-theme="modern"><head><meta charset="UTF-8">
<link rel="stylesheet" href="../../design-system/colors_and_type.css">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }            /* 필수 reset */
  body { width:1280px; height:720px; overflow:hidden;          /* ★고정 캔버스 — 누락 시 body 붕괴=FAILED */
         font-family:'Pretendard',-apple-system,sans-serif;
         background:var(--theme-bg); color:var(--gray-1);
         padding:46px 58px 40px 58px; display:flex; flex-direction:column; }
  /* 슬라이드별 스타일은 여기에 px 단위로 직접 정의 (미정의 .t-* 클래스 의존 금지) */
</style></head>
<body data-layout="<layout_id>">
  <!-- 콘텐츠를 body flex-column에 직접 배치. 마지막에 Source 라인. -->
<style id="om-fit-scaler-style">html { overflow:hidden !important; background:#0a0a0a; }</style>
<script id="om-fit-scaler">
(function(){function fit(){var s=Math.min(window.innerWidth/1280,window.innerHeight/720);var b=document.body;b.style.width='1280px';b.style.height='720px';b.style.position='absolute';b.style.transformOrigin='top left';b.style.left=((window.innerWidth-1280*s)/2)+'px';b.style.top=((window.innerHeight-720*s)/2)+'px';b.style.transform='scale('+s+')';}window.addEventListener('resize',fit,{passive:true});if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fit);fit();})();
</script>
</body></html>
```

- **width:1280px; height:720px; overflow:hidden** 은 절대 생략 금지. 콘텐츠는 이 안에 맞춘다(가로도 ≤1280px, 요소 폭 ≤ 가용폭). 넘치면 변환기가 FAILED/CLAMP.
- **om-fit-scaler 스크립트**는 그대로 복붙(미리보기 자동맞춤 + 변환기 dimension 보장).
- **`.t-body-compact` 등 일부 `.t-*` 클래스는 colors_and_type.css에 미vendored** → 의존 말고 px로 직접 정의(또는 vendored 토큰 `var(--pt-*)` 확인 후 사용).

| # | 금지 패턴 | 시각 동일 안전 대체 | 린트 | 근거(학습/커밋) |
|---|---|---|---|---|
| A1 | 텍스트태그(`p/h*/li/span/small/blockquote`)에 `background`·`border`·`box-shadow` | `<div class=bg><p>텍스트</p></div>` — bg/border는 div, 텍스트는 자식 p | `[PF-07 ✅]` | 학습⑥⑮⑯ / 586f16a |
| A2 | `rgba()`·`hsla()` 반투명 배경 **또는 `opacity:<1` 속성** (alpha/opacity 무시→PPTX서 fully opaque, 색 진해짐·텍스트 invisible) | 사전합성 solid hex 또는 테마토큰 `var(--gray-N)`. 반투명 효과 필요시 합성색을 직접 계산해 solid 지정 | `[PF-33·PF-42 ✅]` | 학습⑤ / idiomatic2 / stress-c5 slide-02 |
| A3 | 인라인 요소(`span`/`small`)에 `margin` | `padding` 또는 부모 flex `gap` | `[동적]` warn (586f16a) | idiomatic3 |
| A4 | 색배경을 형제 overlay div로 두고 텍스트를 그 위 `absolute` | 텍스트를 **자기 색배경 div의 자손**으로 (resolveBackground는 ancestor만 봄) | `[규약]` | idiomatic4 |
| A5 | `clip-path`·`::before/::after` content 로 도형·연결선·장식 | 실제 `<div>`(실 geometry). 화살표=직교 글리프 또는 실 rect `<div>` 연결선. ⛔`border`-삼각형 트릭(`border:…transparent`)=PF-37 흰블록 | `[PF-22·PF-37]` | idiomatic5 / 학습⑪ / stress-c1 |
| A6 | 라벨좌+값우 양끝정렬을 `display:flex; justify-content:space-between` (2텍스트 병합 "기본급100%") | `display:grid; grid-template-columns:1fr auto` + **자식 block(p)**. ⛔grid item에 inline `span` 금지(텍스트노드 병합) | **`[GAP→P1]`** | 학습⑭ / R12 s01 |
| A7 | 카드 라벨+본문에서 본문 itext에 `white-space:nowrap` (변환기 인라인 오인→형제 겹침) | `flex-direction:column` 명시. 긴텍스트 nowrap 필요시 `<div><p nowrap>` 분리 | **`[GAP→P1]`** (IL-34는 反방향) | 학습③⑫ / R11 |
| A8 | 다이어그램 대각 화살표 글리프 `↘ ↗ ↙ ↖` (폰트폴백 깨짐) / `border`-삼각형 화살촉 (PF-37 흰블록) | 직교 `→ ↑ ← ↓` 글리프만. 연결선=실 rect `<div>`. ⛔border-삼각형 | `[PF-76 ✅ + PF-37]` | 학습⑪ / R9 / stress-c1 |
| A9 | **flex/grid 컨테이너의 직속 텍스트노드** (색칩·배지 등) — 변환기 loose-text 위치계산이 flex서 붕괴→런 겹침 garble | flex/grid 자식 텍스트는 **반드시 `<div><p>라벨</p><p>메타</p></div>`** (직속 텍스트노드 금지). `width`·`height` 명시 | `[동적]` | 학습⑧ 정밀화 / stress-c1 slide-06 + probe E |
| A10 | 다크패널(`surface-inverse`) 내 강조에 `var(--accent)` 색 (navy 1.5~1.8:1 저대비) | `surface-inverse-fg` + weight 차이. accent 색강조는 **라이트 배경만**. 데이터 의미색 navy `#1F4E79`→다크는 cobalt `#2563EB` | `[동적]` VP-04 | 학습②⑬ / prompting §4.3 |
| A11 | 행 많은 표가 720pt 초과 (silent drop) / 텍스트박스 바닥 <0.5"(48px) | head/td padding 축소 또는 슬라이드 분할. body `padding-bottom ≥40px` | `[동적]` PF-23/28 | 학습⑦⑮ |
| A12 | 좌우분할 head 한쪽만 width / **또는 `grid-template-columns:1fr 1fr`·`1fr 1px 1fr` 등 비명시 fr 분할**(변환기가 fr 폭·`1px` divider 컬럼 위치 못 풀어 **우측 컬럼이 좌측으로 이동·겹침** garble) | 양쪽 다 `width`+`flex-shrink:0` (flex-row 권장, slide-02 패턴) **또는 grid는 명시 px 컬럼**(`512px 1fr`, slide-05 패턴). divider는 컬럼 **사이 1px div / border**로, ⛔grid의 `1px` 중간컬럼 금지 | `[동적]` VP/렌더 | 학습⑩ / stress-c5 slide-08 |
| A13 | 복합셀에 여러 자식 요소 | 표패턴 **단일 p + `<br>`** | `[규약]` | 학습④⑨ |
| A14 | 슬라이드 타이틀·룰에 `var(--primary)` (dark-mono서 primary==bg→소멸) / 풀블리드에 primary | 타이틀·룰=`var(--heading)`, 풀블리드=`var(--surface-inverse)` | `[동적]` | 학습① / prompting §4.3·§4.3b |
| A15 | 상태·범례 글리프(`● ○ ◆ ◇ ■ □ ▪ ▸ • - *`)를 `<p>` **첫 문자**로 (변환기가 manual bullet로 오인→변환 거부, html2pptx.cjs:1620) | 글리프를 **별도 색 div dot** 또는 텍스트 뒤/중간에 배치. 진짜 목록은 `<ul>/<ol>` | `[변환검증]` | stress-c4 slide-03 |
| A16 | `writing-mode:vertical-*` / `transform:rotate(±90)` 세로 텍스트가 레이아웃 폭을 키워 **가로 overflow**(회전 전 폭으로 측정) | 세로축 라벨은 폭 좁게 고정 + 회전 후 실폭 확인, 또는 짧은 라벨. 컨테이너 `overflow:hidden`+명시 width | `[변환검증]` | stress-c4 slide-02 |
| A17 | **`conic-gradient()`·`radial-gradient()` 로 그린 도넛·파이 차트** (PPTX서 완전 손실=빈 원) | 비중 시각화는 **수평/수직 stacked-bar**(각 세그먼트=`div` width/height) 또는 막대그래프. 진짜 원형 필요시 segment별 실 `<div>` (단순 비율은 bar 권장) | `[PF-62 ✅]` | 학습 / stress-c5 slide-01 |
| A18 | serif 테마(`academic`/`editorial`)서 `font-family:Georgia`(또는 PPTX 미존재 serif) — PowerPoint에 없어 **Arial 폴백→serif 의도 소실** | **`'Times New Roman'`**(PPTX 표준 serif) 우선 + 스택에 Georgia 폴백: `font-family:'Times New Roman',Georgia,serif`. 테마 토큰에 serif 정의 있으면 그것 사용 | `[PF-19 ✅]` warn | stress-c5 slide-07 |
| A19 | 다크 배경(dark-pitch/다크패널) 위 **출처·footnote·캡션**을 배경과 유사한 어두운 색(예 `#141416` on `#0a0a0b`=1.08:1) | 다크 배경 보조텍스트도 최소 대비 확보 — `var(--gray-2/3)` 라이트 톤 또는 명시 밝은 hex(`#9CA3AF`+). A10(강조)과 동일 원칙을 footnote까지 확장 | `[동적]` PF-71/VP-04 | stress-c5 slide-06 |
| A20 | **방사형/레이더 차트를 div 다각형·회전 spoke 로 근사**(conic/svg 금지 A17 + div 회전 한계로 넥타이·비대칭 형태로 깨짐) | 축별 **수평 막대 묶음**(축=행, 점수=막대 width %)으로 표현 권장 — 데이터 정확 전달 + 변환 안정. 진짜 방사형 불가피 시 div 다각형은 장식 최소(우측 축별 막대 병행해 데이터는 막대로) | `[규약/시각]` | stress-c7 slide-03 |

### A 적용 골격 (복붙용)
```html
<!-- A1·A6·A9 동시 준수: 라벨/값 양끝정렬 카드 -->
<div class="card" style="background: var(--gray-4); display:grid; grid-template-columns:1fr auto;">
  <p class="t-body">기본급</p>      <!-- 자식 block, inline span 금지 -->
  <p class="t-body">100%</p>
</div>
<!-- A8 준수: 직교 화살표만 -->
<div class="flow"><p>입력</p><span class="t-chart-label">→</span><p>처리</p></div>
```

---

## §B 정적-린트 커버리지 맵 (Phase 1 작업 정의)

| 상태 | 규칙 | 비고 |
|---|---|---|
| ✅ 정적 차단 | A1(PF-07) · A2(PF-33) · narrow-CJK(IL-34) · `<table>`(PF-63) · gradient(PF-01/39/62) · 국기이모지(PF-12) · **A8(PF-76 ✅신규 2026-06-18)** | 생성 즉시 잡힘 |
| **Playwright phase(DOM) 예정** | **A6**(flex space-between + 직속 inline/text 자식 → 병합) · **A7**(card itext harmful nowrap) | 정규식으론 nested 자식 block/inline 판별 불안정→FP. PF-25/28과 동일 이유로 실 DOM(`page.evaluate` 자식 nodeType 검사)에 배치. 78 GT + round 전수로 FP 보정 |
| 동적(변환·렌더 검출) | A3 · A9 · A10(VP-04) · A11(PF-23/28) · A14 | |
| 규약(자동검사 없음) | A4 · A12 · A13 | 계약 문서로만 강제 |

→ **A8=PF-76 완료**(char-scan ERROR, 합성 정탐✅·round FP0). **A6/A7=Playwright DOM 검사 예정**(직속 자식이 block(p/div)이면 안전, raw text/inline span이면 발화). 추가 후 GT 17덱 정탐회귀=0 + 신규 FP=0 확인.

---

## §C 결함 Triage 결정트리 (2축, 핸드오프 §3b 정합)

결함(HTML이 잘못 변환/렌더됨) 발견 시:

```
① 이 PF/VP 플래그가 룰 오발(실제론 정상인데 ERROR / 잡아야 할 걸 놓침)인가?
   └─ YES → 룰 수정 (preflight/validate) — GT 17덱 정탐회귀=0 게이트
   └─ NO ↓ (진짜 변환 문제)
② 시각적으로 동일한 안전 마크업 대체가 있나? (§A 규칙류)
   └─ YES → ★생성기 계약 수정 (안전 대체 박제 + 슬라이드 적용) — §D 드리프트 게이트(PNG 동일) 통과 의무
   └─ NO  → 안전 대체가 없음 = 깎아야만 변환됨 ↓
③ 변환기가 원안을 못 살리는 진짜 엔진 결함
   └─ 변환기 수정 (scripts/html2pptx.cjs) — §3b 2순위 — GT 17덱 전수 회귀=0 게이트
      ⛔ "슬라이드 깎기"는 최후수단 (디자인 원안 손상 = 드리프트의 일종)
```

**우선순위 요지**: 생성기(시각동일 회피) > 변환기(원안보존) > 룰(미세조정) > 디자인 깎기(최후). 이번 세션 지시 + §3b 동일.

---

## §D 드리프트 게이트 (★절대 드리프트 0 — 3중 잠금)

생성기 계약 수정이 디자인 의도를 바꾸지 않음을 **기계적으로 증명**한다.

1. **수정 범위 제약**: 계약 규칙은 **"시각적으로 증명 가능한 동일 변환"만** 허용. 레이아웃·색·폰트·크기·간격을 바꾸는 변경은 계약에 못 들어온다(정의상 시각 변화=드리프트).
2. **베이스라인 박제**: 각 슬라이드의 **최초 시각승인된 COM 렌더 PNG**(신규 소재는 원안 HTML 렌더)를 design-intent ground truth로 고정.
3. **PNG diff 게이트**: 계약 변경 후 재생성→재렌더 → 베이스라인 대비 비교. **현 도구 = vision 판정**(COM PNG 원안 Read 비교, 핸드오프 §5 기존 절차). 시각 변화 감지 시 → 그 "안전 대체"는 시각 비동일 → 채택 거부 + 원인 조사. (선택 강화: `pixelmatch`+`pngjs` 설치 시 픽셀 변화%/SSIM 기계 게이트로 전환 — 현재 미설치라 vision 기본.)

추가 안전망: 변환기/룰 수정 시 **GT 17~27덱 코퍼스 회귀=0** (`tests/regress-generated.sh`).

---

## §E Phase 2 stress 채굴 차원 (병렬 배치 대상)

서브에이전트 N개가 각자 한 차원을 극단으로 밀며 **§A 계약 준수** 생성 → 한 배치로 미지 버그 대량 수확.

| # | stress 차원 | 노리는 변환기 경로 |
|---|---|---|
| 1 | 고밀도 표(720pt 경계) | silent omit / 컬럼 snap (A11) |
| 2 | 깊은 중첩 ul/ol | 이중방출 / 들여쓰기 |
| 3 | 인라인 KPI(small/sup/sub 혼합 run) | run 분해 / 단위 소실 |
| 4 | 배지·pill 군집(inline-flex) | orphan span / 배경 미렌더 (A1) |
| 5 | 다크패널 + 긴 본문 | 대비 오판 / 텍스트 잘림 (A10·A11) |
| 6 | 색칩/스와치(div 직속 텍스트) | shape+text 분리 (A9) |
| 7 | blockquote + figcaption + 캡션 | textTag 누락 |
| 8 | 좌우분할 다단 | 폭 저측정 / 겹침 (A12) |
| 9 | 차트·다이어그램(canvas/화살표) | 래스터화 / 글리프 (A8) |
| 10 | absolute overlay / clip-path류 | bbox 렌더 (A4·A5) |

---

## 헤드라인 지표
**first-try clean rate** = (PF+VP 통과 ∧ 드리프트0 슬라이드) / 전체. 현재 "매 라운드 1~3 버그" → 목표 "2배치 연속 신규결함 0".
