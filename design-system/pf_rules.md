# HTML 작성 시 금지/필수 규칙 (Quick Reference)

슬라이드 HTML 생성/수정 시 준수. 상세 예시: `docs/html-rule-examples.md`. 이슈 이력: `docs/pptx-inspection-log.md`.

## 규칙 작성 메타규칙

모든 규칙은 **정량적** 작성. 정성적 표현("적절히", "여유 확보") 금지 → 에이전트가 무시함.
필수: ① 수치 임계값 ② 계산 공식 ③ 위반/수정 예시 (`docs/html-rule-examples.md`에)

_파이프라인 수정 의무 (3분류 판정: 오탐/정탐-수정/정탐-한계, A~I 절차) → `CLAUDE.md` §자가 개선 피드백 루프_

## 금지 (ERROR — 변환 실패 또는 텍스트 불가시)

- `linear-gradient` + 흰색/밝은 텍스트 → 단색 `background` 대체 [IL-14,16 / PF-01]
- `<p>`,`<h1>`~`<h6>`,`<li>`에 background/border → `<div>`로 래핑 [PF-07]
- 비-body DIV에 `background: url()` → body만 허용 [IL-04 / PF-05]
- `rgba()` 반투명 배경(alpha < 1.0) → 솔리드 hex 블렌딩: `ch = parent×(1-a) + rgba×a` [IL-14,43]
- 배경 있는 자식 div와 형제 `<span>` → `<span>` 대신 `<p>` 사용 [IL-24 / PF-14]
- `border-radius:50%` + `border` 원형 차트 → PNG `<img>` + 텍스트 오버레이 [IL-25 / PF-13]
- 국기 이모지(🇺🇸🇰🇷) → PNG/SVG `<img>` [IL-26 / PF-12]
- `text-decoration: underline` → `color` 또는 `font-weight:700` [IL-38]
- 비-body DIV `background-image: linear-gradient()` → 솔리드 사각형으로 변환 [IL-39]
- `border-*` + `transparent` 삼각형 → 수직/수평 분할로 대체 [IL-28]
- `<li>` + `::before`/`::after` → `<p>` + 인라인 불릿("·","•") [IL-44]
- 텍스트 요소 내 `<span>` 색상 변경 → 별도 `<p>` + 클래스로 전체 행 지정 [IL-45]
- `<span>`에 `background`/`background-color` → 텍스트 색상+font-weight로 강조 [IL-60 / PF-55]
- `conic-gradient()` → PPTX에서 완전 소실. 가로 바 차트(div+width%) 또는 테이블로 대체 [IL-70 / PF-62]
- `radial-gradient()` (비-body) → 솔리드 배경색 또는 PNG로 대체 [IL-70 / PF-62]
- `column-count: N` (N≥2) → grid/flex로 다단 구현 [IL-53 / PF-48]
- 슬라이드 HTML 파일명 불일치 → 반드시 `slide-NN.html` (NN은 01부터 시작하는 두 자리 숫자) 형식 준수 [PF-68]

## 금지 — `<table>` 태그 [PF-63]

- `<table>`, `<tr>`, `<td>`, `<th>` 태그 사용 금지 → CSS Grid(`grid-template-columns`)로 대체
- PPTX 변환 시 `<table>`은 PptxGenJS의 테이블 렌더러를 거쳐 셀 크기/정렬이 달라짐
- 대체 패턴: `<div style="display:grid; grid-template-columns: ...">` + `<div class="cell"><span>텍스트</span></div>`
- 상세: §필수 — Grid 테이블 [IL-17,40 / PF-65] 참조

## 경고 — 슬라이드당 단어 수 [PF-28]

- 슬라이드당 **영문 120단어 / CJK 80단어 이하** (출처·캡션 제외)
- 초과 시 조치 (폰트 축소 대신): ① 텍스트 축약 ② 항목 수 감소 ③ 슬라이드 분할
- PF-28 WARN: 슬라이드당 단어 수 초과 감지

## 금지 — 배지/라벨 내 flex + `<br>` [IL-73 / VP-14,VP-16]

- 배지/라벨(`border-radius`, 소형 컨테이너) 내부에 `display:flex` + `<br>` 또는 다중 `<p>` 사용 금지
- PPTX 변환 시 flex 자식이 각각 별도 쉐이프로 분리 → 겹침(VP-14) 또는 텍스트 오버플로(VP-16) 발생
- 대체 패턴: 단일 `<p>` 안에 `<span>` 인라인으로 구성
- 예: `<p class="badge"><span class="num">60</span><span>개국 가입</span></p>`

## 필수 — Flex/Box 모델 [IL-13 / PF-02,06]

- `flex:1` div → `box-sizing:border-box; min-width:0` 필수
- flex 컨테이너 → `overflow:hidden` 필수
- 이미지 div → `min-width:0` 필수

## 필수 — 이미지 컨테이너 수직 정렬 [IL-62 / PF-56]

- 이미지 컨테이너에 `display:flex; align-items:center` 사용 시 반드시 `height:100%` 또는 명시적 height 설정
- height 없으면 컨테이너가 이미지 높이로 축소 → `align-items:center` 무효
- 분할 레이아웃(.image-col) 필수: `height: 100%`

## 필수 — 이미지 최소 크기 (슬라이드 면적 1/4) [IL-63 / PF-57, PF-70]

- **핵심 원칙**: 콘텐츠 이미지(`assets/`)는 슬라이드 면적(720×405=291,600 sq pt)의 **최소 1/4(≈25%)**을 차지해야 한다
- **명시적 pt 치수 필수**: `<img>` 태그에 `width: Npt; height: Npt` inline style 지정. flex 비율만으로 크기 결정 금지 → PF-70 ERROR
- **최소 치수**: width ≥ 260pt, height ≥ 180pt (미달 시 PF-70 ERROR)
- **권장 치수**: 좌우 분할 300~360pt × 220~280pt, 히어로 420~560pt × 200~280pt
- 면적 부족 시 조치: ① 텍스트 비율 축소 ② 콘텐츠 재배치 ③ 슬라이드 분할 (폰트 축소 대신)

## 필수 — 이미지 원본 비율 보호 (왜곡 금지 + cover 크롭) [PF-43 / PF-21]

- **비율 왜곡 절대 금지**: `<img>` 태그에 width/height를 지정할 때, 원본 이미지의 종횡비(aspect ratio)를 변경하는 조합 금지 → PF-21 ERROR
- **object-fit: cover 필수**: 이미지가 레이아웃 영역에 맞지 않을 때 **비율 유지 + 여백 크롭**(cover)으로 처리. 비율을 찌그러뜨리거나(stretch) 축소하여 여백을 남기는(contain) 방식 금지
- **PPTX 변환 동작**: html2pptx.cjs가 `sizing: { type: 'cover' }`로 변환 — 이미지 비율 유지하면서 지정 영역을 꽉 채우고 초과분은 자동 크롭
- **이미지 컨테이너 규칙**: 컨테이너 비율이 이미지 비율과 크게 다를 경우(>20% 차이), 핵심 피사체가 잘리지 않도록 컨테이너 비율을 이미지에 맞춰 조정
- **사전 크롭 권장**: 이미지 생성 시 목표 레이아웃 비율(4:3 또는 16:9)에 맞춰 생성하면 변환 시 크롭 손실 최소화

## 경고 — flex:1 + overflow:hidden 내 고정높이 잘림 [IL-65 / PF-59]

- `flex:1; overflow:hidden` 컨테이너 안에 `height > 90pt` 자식 → 상단 콘텐츠 잘릴 수 있음
- 막대 차트: 최대 막대 높이 80pt 이하 권장, 라벨 공간 확보
- `align-items: flex-end` 사용 시 특히 주의 — 상단 라벨이 먼저 잘림

## 금지 — overflow:hidden 카드/컨테이너 콘텐츠 초과 [PF-66]

- `overflow:hidden` 컨테이너에 콘텐츠 배치 시 **총 콘텐츠 높이가 컨테이너 높이를 초과하면 안 됨** — 초과분은 잘려서 보이지 않음
- 검증 공식: `padding_top + Σ(자식_height + gap) + padding_bottom ≤ container_height`
- 초과 시 조치: ① 텍스트 축약 ② 항목 수 감소 ③ font-size 축소 ④ 슬라이드 분할
- PF-66 ERROR (--full): scrollHeight > clientHeight + 2px인 overflow:hidden 컨테이너 탐지, 잘린 텍스트 내용 리포트

## 금지 — line-height: 1 대형 폰트 text-clipped [PF-66 연관]

- **24pt 이상 폰트에 `line-height: 1` 사용 금지** — 폰트 메트릭(ascender+descender)이 line box를 초과하여 scrollHeight > clientHeight 발생, PF-66 dynamic 검증에서 text-clipped ERROR
- 대형 숫자/타이틀 요소: `line-height: 1.15` 이상 사용
- hero 숫자 요소 뒤 `margin-bottom: 12pt` 이상 확보 (VP-14 shape overlap 방지 — PPTX 변환 시 shape 겹침)

## 주의 — 배경이미지 커버/분할 레이아웃 COM 점수 저하 [COM 한계]

- 배경이미지 전체 커버 슬라이드(`background: url() center/cover`) → PPTX 변환 시 content completeness 저하 (COM VC-03 1~2/5)
- 이미지+텍스트 분할 레이아웃(`object-fit: cover` 이미지 열) → text fidelity 저하 (COM VC-02 2~3/5)
- **수정 불가** (html2pptx 변환 엔진 한계) — PowerPoint에서 수동 보정 필요
- 이 패턴을 사용해도 HTML 품질은 정상이므로 디자인 판단에 따라 허용. COM ERROR는 예상된 한계로 처리

## 경고 — 배지/장식 div 내 텍스트 색상 불가시 [IL-66 / PF-60]

- `border-radius: 50%` 또는 width/height ≤ 40pt인 장식 div 내 텍스트 → PPTX에서 배지 배경이 텍스트에 전달 안 됨
- 텍스트 `color`는 **해당 div의 부모 배경** 대비 3:1 이상 필수
- 흰색 텍스트(#FFFFFF)를 배지 안에 쓸 때: 부모 배경이 밝으면(#F8FAFC, #FFF7ED 등) 불가시 → 어두운 색(#92400E, #065F46 등) 사용

## 경고 — 배경 이미지 위 텍스트 대비 부족 [IL-69 / PF-61]

- 배경 `<img>`(absolute) 위에 텍스트를 배치할 때 반드시 **불투명 오버레이 + text-shadow** 필요
- 오버레이: `background: #1E293B; opacity: 0.5~0.7` (rgba() 금지 — PF-36 위반)
- text-shadow: `text-shadow: 0 2px 8pt rgba(0,0,0,0.5)` 등
- PF-61 WARN (--full 모드): Playwright가 조상/형제에서 absolute `<img>` 탐지 → overlay/text-shadow 없으면 경고

## 금지 — 이미지 src 경로 불일치 [IL-64 / PF-58]

- `<img src="assets/...">` 작성 시 반드시 `ls assets/` 실행하여 실제 파일명 확인
- NanoBanana 생성 파일명은 generate-images.mjs가 결정 → 아웃라인 slug와 다를 수 있음
- PF-58 ERROR: 존재하지 않는 파일 참조 시 에러

## 필수 — 이미지 높이 [IL-04 / PF-04]

- `height:100%` 금지 → `max-height:{N}pt` 또는 고정 pt

## 필수 — CJK 텍스트 폭 공식 (전 규칙 공통)

- `text_width = CJK문자수 × font_size + 라틴문자수 × font_size × 0.6`
- 검증: `text_width ≤ container_width × 0.8` (20% 여유) [IL-37]

## 필수 — CJK 카드 텍스트 [IL-06 / PF-08]

- 카드 내 CJK font-size ≤ 11pt
- `card_width = (body_width - padding_lr - gap×(N-1)) ÷ N`
- 검증: `text_width < card_width × 0.8` (전 규칙 공통 20% 여유 기준)

## 필수 — 3열+ 그리드 CJK [IL-27 / PF-15]

- font-size ≤ 7.5pt, line-height ≤ 1.4, padding ≤ 8pt
- 텍스트 폭 > 셀 가용 폭 85% → font-size 1pt 축소 또는 축약

## 필수 — 50% 분할 [IL-18]

- 한글 제목 font-size ≤ 14pt, `<br>` ≤ 3줄

## 필수 — 밀집 레이아웃 [IL-10]

- 4+카드: body padding ≤ 32pt, gap ≤ 10pt
- 5+리스트: gap ≤ 7pt, 아이템 padding ≤ 10pt
- 높이: `padding_tb + title_h + Σ(item_h) + gap×(N-1) ≤ 405pt`

## 필수 — 배경 이미지 + 텍스트 오버레이 [IL-07 / PF-16]

- gradient: 상단 ≥ 0.7, 텍스트 영역 ≥ 0.9
- `text-shadow: 0 2px 8px rgba(0,0,0,0.5)` 필수
- CSS transform: `rotate`만 지원 [PF-17]

## 필수 — 오버레이 CTA 리스트 (클로징 슬라이드) [IL-72]

- 배경 이미지 + 오버레이 위 CTA 리스트(3개+)에서 VP-16 CJK 오버플로 방지
- CTA 텍스트: **10자 이내**, font-size **≤ 11pt**
- CTA 텍스트 색상: **부모 배경 제외 시 #FFFFFF 대비 3:1 이상** (PPTX가 배경 이미지 무시하므로)
- 검증 공식: `CJK문자수 × font_size + 라틴문자수 × font_size × 0.6 ≤ shape_width × 0.8`
- content padding: **≤ 32pt** (CTA 항목 수 3개+ 시)
- 위반 시: 텍스트 축약 → font-size 축소 → 항목 수 감소 순으로 조치

## 필수 — Grid 테이블 [IL-17,40 / PF-65]

- `grid-template-columns: 고정pt ...` 사용
- 열 합계: `Σ(columns) ≥ 가용폭 × 0.9`
- 헤더 행 배경색 필수, 셀: `<div class="cell"><span>텍스트</span></div>`
- **컬럼 너비 최소 기준**: CJK 텍스트 최장 항목의 `문자수 × font_size × 0.8 + padding_lr` 이상. 텍스트가 줄밀림되면 컬럼 너비 확대 또는 텍스트 축약
- PF-65 WARN (--full): 셀 scrollWidth > clientWidth 또는 padding 보정 후 2줄 이상인 짧은 텍스트(≤12자) 탐지

## 필수 — Flex Row 오버플로 [IL-42]

- 4+아이템: `(body_w - padding_lr - gap×(N-1)) ÷ N - item_padding_lr` = 가용 폭
- 검증: `text_width < available × 0.85`

## 필수 — 바 차트 [IL-42]

- 바 내부 텍스트 시: `bar_height ≥ font_size + 8pt`

## 필수 — 장식 요소 간격 [IL-41]

- 텍스트 직후 accent-bar: `margin-top ≥ 20pt` (미만이면 밑줄로 오인)
- 20pt 불가 → 장식 요소 제거

## 필수 — 장식용 absolute [IL-39]

- absolute 영역이 텍스트/테이블과 겹치면 → 콘텐츠 외곽 이동 또는 body background

## 하이라이트 셀 [IL-29]

- font-size ≤ 7.5pt + `white-space:nowrap`
- 셀 폭 ≥ CJK: `문자수 × fs × 0.7`, 라틴: `문자수 × fs × 0.45` + padding

## AI 생성 이미지 [IL-30]

- 가짜 데이터 인포그래픽 금지, AI 한글 텍스트 금지
- 허용: 사진, 아이콘(SVG), 추상 일러스트, 스크린샷

## 최소 폰트 사이즈 [IL-31 / PF-25]

| 용도 | 최소pt | 용도 | 최소pt |
|------|:------:|------|:------:|
| Hero Title | 48 | Subtitle | 16 |
| Section Title | 36 | Body | 14 |
| Slide Title | 24 | Caption/Label | 10 |

**10pt 미만 절대 금지.** (특히 Badge, Footer 등 부수적 요소에서도 9pt 사용 금지). 콘텐츠 초과 시 폰트 축소 대신 슬라이드 분할.

## 밀도 제한 [IL-33 / PF-26]

- 독립 콘텐츠 블록 **최대 3개** (4+ → 분할). 12개월 타임라인 → 2슬라이드.

## CJK 배지/라벨 [IL-34 / PF-27]

- width < 150pt → `white-space:nowrap` 필수
- ≤ 8자, 컨테이너 폭 = `CJK수 × fs × 1.3`

## 타임라인/다열 라벨 [IL-35]

- 열 폭 < 60pt → CJK ≤ 3자, < 40pt → ≤ 2자 또는 아이콘
- 12개월 → 6개월씩 분할

## 이미지 z-order [IL-36]

- 이미지 배경 → body `background-image`만 허용. 겹침 방지: 좌우/상하 분할.

## 경고 — CSS 특이성 충돌로 텍스트 색상 소실 [IL-71]

- CSS 클래스로 텍스트 색상을 지정할 때, **더 구체적인 선택자가 덮어쓰지 않는지** 확인 필수
- 위반 예: `.r-odd .tc p { color: #1A1A2E; }` (특이성 0,2,1) vs `.tc-risk-high p { color: #EF4444; }` (특이성 0,1,1) → 빨간색이 적용 안 됨
- 수정: 특이성을 맞추거나 높이기 — `.r-odd .tc.tc-risk-high p { color: #EF4444; }` 또는 inline `style="color:#EF4444"`
- 검증: 브라우저 DevTools에서 해당 요소의 computed color가 의도한 색상인지 확인
- **탐지 한계**: PF/VP/Vision 모두 못 잡음 — HTML 렌더링 자체가 잘못되어 PPTX와 동일하게 보이므로 Vision PASS. 생성 시 방지만 가능

## PPTX 미지원 CSS (preflight 자동 검출)

| 속성 | 수준 | 대안 | PF |
|------|:----:|------|:--:|
| `letter-spacing` >1pt | WARN | thin space(U+2009) | 41 |
| `opacity` <1.0 | WARN | 솔리드 hex 블렌딩 | 42 |
| `object-fit: cover/fill` | WARN | 사전 크롭 이미지 | 43 |
| `outline` (≠none/0) | WARN | `border`로 대체 | 44 |
| `box-shadow` (전체) | **ERROR** | border 또는 background-color로 대체. PPTX는 모든 shadow 무시 | 66 |
| `box-shadow: inset` | WARN | 배경색 또는 중첩 div | 22 |
| `margin-*: -N` (≥5pt) | WARN | `position:absolute` | 45 |
| `text-indent` (≠0) | WARN | `padding-left` | 46 |
| `word-break: break-all` | WARN | 수동 폭 검증 | 47 |
| `mix-blend-mode` (≠normal) | WARN | 사전 렌더링 이미지 | 49 |
| `border-image` | WARN | `border:solid` 단색 | 50 |
| `position: sticky` | WARN | 슬라이드에서 무의미 | 51 |
| `@font-face` | WARN | 시스템 폰트 사용 | 52 |
| `direction: rtl` | WARN | — | 53 |
| `white-space: pre/pre-line` | WARN | `<br>` + `&nbsp;` | 54 |

---

## v3 통합 신규 룰 (PF-69 ~ PF-75) — mck 흡수

slides-grab Design System v3 통합으로 추가된 7 룰. 모두 `scripts/preflight-html.js` 에서 자동 검출 대상 (구현 시).

### PF-69 — 테마 × 레이아웃 매트릭스 위반 (ERROR)

`<html data-theme="X">` 가 선언되었을 때, `<section data-layout="Y">` 가 매트릭스 `theme_layout_matrix.md` §2 에서 ❌ 인 경우.

**검증 의사코드:**
```js
const theme = doc.documentElement.dataset.theme;
const layout = section.dataset.layout;
if (!THEME_ALLOWED_LAYOUTS[theme].has(layout)) {
  error(`PF-69: ${theme} 테마에서 '${layout}' 레이아웃 금지. 허용 셋: [...]. theme_layout_matrix.md §2 참조`);
}
```

**예시 위반:**
- `<html data-theme="dark-mono">` + `<section data-layout="harvey_ball_table">` → ❌ (다크에서 채움 단계 식별 불가)
- `<html data-theme="dark-mono">` + `<section data-layout="venn">` → ❌ (다크에서 blend 깨짐)

**수정:** 매트릭스 §2 에서 ✅ 인 다른 레이아웃 사용. 또는 다른 테마로 전환.

### PF-70 — `data-layout` 속성 의무 (ERROR)

모든 슬라이드 `<section>` 은 `data-layout="<id>"` 명시 필수. ID 는 `layout_catalog.md` 카탈로그의 46개 중 하나.

**위반 예:**
```html
<section data-screen-label="04">     ❌ data-layout 누락
  ...
</section>
```

**수정:**
```html
<section data-layout="variance_table" data-screen-label="04">
  ...
</section>
```

**검증:** 모든 `<section>` 자식이 `<deck-stage>` 또는 `<body data-layout>` 안에 있을 때 검사. 단독 `<body data-layout="...">` 도 허용 (single-slide HTML).

### PF-71 — `data-theme` 속성 의무 (ERROR)

`<html>` 또는 `<body>` 가 `data-theme="<id>"` 명시 필수. ID 는 8개 테마 중 하나:
`modern · classic · dark-mono · company · executive-editorial · dark-pitch · academic · editorial`.

**자동 폴백 금지.** 누락 시 `modern` 으로 가지 않고 ERROR.

**수정:**
```html
<html lang="ko" data-theme="modern">    ← 의무
```

### PF-72 — LayoutSchema 위반 (ERROR)

`<section data-layout="Y">` 의 콘텐츠가 `layout_catalog.md` 의 LayoutSchema 의 required / type / bounds 를 위반.

**예시 위반:**
- `variance_table` 인데 `items` 가 0개 → ERROR (`min_length=1`)
- `donut` 인데 `segments` 가 8개 → WARN (>`MAX_DONUT_SEGMENTS=6`, autofix 대상)
- `cover` 인데 `title` 누락 → ERROR (required)

**자동 수리:** 6개는 ERROR (autofix 불가), bound 위반은 `qa/autofix.py` 의 8개 룰이 시도.

### PF-73 — `primary` 풀블리드 금지 (WARN)

CSS 또는 inline 에 `var(--primary)` 가 풀블리드 (100% width × 100% height) 배경으로 사용 시 WARN. `dark-mono` 테마에서 `primary == bg` 라 invisible 가 됨.

**위반 예:**
```css
.section-divider {
  background: var(--primary);          ❌ dark-mono 에서 사라짐
  width: 100%; height: 100%;
}
```

**수정:**
```css
.section-divider {
  background: var(--surface-inverse);  ✅ 다크 안전
}
```

**검증:** computed style 에서 `var(--primary)` 가 background 로 풀블리드 (보더 거의 없음) 인 요소 탐지. `surface_inverse` 권장.

experiences 상수: `ALLOW_PRIMARY_FOR_FULL_BLEED = False` (`domain/fpna_invariants.md` §2.5).

### PF-74 — whitespace / dead-zone (WARN/ERROR)

슬라이드의 콘텐츠 영역 (title rule 아래 ~ source line 위) 가 80% 이상 빈 채로 남으면 WARN. 95% 이상이면 ERROR. mck `qa/checks.py` 의 `_check_whitespace` 등가물.

**의미:** 슬라이드가 렌더 안 됐거나, autofix 가 너무 많이 깎았거나, 콘텐츠가 빠짐.

**검증:** content area의 visible pixel 비율 측정. 임계값 80% / 95%.

**수정:** 콘텐츠 추가, 슬라이드 분할 점검, autofix 룰 재확인.

### PF-75 — 액션 타이틀 명사형 종결 위반 (WARN)

`<h1 class="t-action">` 또는 `<h1 class="slide__title">` 의 텍스트가 다음 어미로 끝나면 WARN:

```
습니다 · 합니다 · 있다 · 없다 · 했다 · 이다 · 된다 · 하다 · 한다
```

mck `builder/tone.py` 의 `_BAD_ENDINGS` 박제. 길이 > 40자 도 WARN.

**예시 위반:**
- `"북미 매출이 전년 대비 14% 성장했다"` → WARN (`했다` 종결)
- `"북미 매출이 전년 대비 14% 성장합니다"` → WARN (`합니다` 종결)

**수정:** `"북미 매출, 전년 대비 +14% 성장"` (명사형)

experiences 상수: `MAX_ACTION_TITLE_CHARS = 40`.

---

## v3 통합 룰 매핑 — single source of truth

| PF 룰 | 등가 mck 출처 | experiences 상수 |
|------|------------|----------------|
| PF-69 | `theme_layout_matrix.md` §2 | (matrix 자체) |
| PF-70 | `layout_catalog.md` schema | (registry presence) |
| PF-71 | `colors_and_type.css` `[data-theme]` | (8 theme list) |
| PF-72 | `validation.py` `LAYOUT_SCHEMAS` | (per-layout) |
| PF-73 | `helpers/_check_full_bleed_primary` (proposal) | `ALLOW_PRIMARY_FOR_FULL_BLEED = False` |
| PF-74 | `qa/checks.py` `_check_whitespace` | (80% / 95%) |
| PF-75 | `builder/tone.py` `validate_action_title` | `MAX_ACTION_TITLE_CHARS = 40`, `_BAD_ENDINGS` |

이 7 룰은 양쪽 시스템 (slides-grab HTML preflight + mck Python qa) 에서 **같은 의도** 를 양 끝에서 인코딩. 한쪽만 갱신 금지.
