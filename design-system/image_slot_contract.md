# Image Slot Contract — 클라우드 ↔ 로컬 이미지 브릿지

> **한 위치에, 두 환경이 읽어가는 메타데이터를 박는다.** 클라우드는 미리보기·디자인 검토에 사용, 로컬은 generate-images.mjs 가 Gemini NanoBanana 호출에 사용. 슬롯 자체가 계약이다.

---

## 0. 슬롯 마크업 — 권위 있는 형식

모든 이미지가 들어갈 자리는 다음 형식의 **단일 `<div class="image-slot">`** 으로 표기. 다른 형식 금지.

```html
<div class="image-slot"
     data-slot-id="hero-q1-revenue"
     data-shape="rect"
     data-aspect="4:3"
     data-min-w="260pt"
     data-min-h="180pt"
     data-theme-mood="modern"
     data-nano-prompt="cool editorial photograph of a modern Korean
       semiconductor fab interior, desaturated, mid-key lighting,
       steel blue and neutral gray palette, no people visible,
       wide-angle, clean composition, magazine quality">
  <span class="slot-hint">Q1 매출 히어로 이미지</span>
</div>
```

`_image-slot.css` 가 점선 박스 + hint 텍스트를 렌더링.

---

## 1. 의무 속성 (required)

| 속성 | 형식 | 설명 |
|------|-----|------|
| `class="image-slot"` | 정확히 이 클래스 | preflight + generate-images.mjs 가 탐지 |
| `data-slot-id` | kebab-case, deck 내 유일 | 생성 후 `assets/<slot-id>.png` 로 저장 |
| `data-shape` | `rect` / `rounded` / `circle` / `pill` | 슬롯 외형 |
| `data-aspect` | `4:3` / `16:9` / `1:1` / `3:2` / `21:9` | 종횡비 |
| `data-min-w` | `Npt` (≥260pt) | 슬라이드 면적 25% 의무 (PF-70 — width<260pt ERROR) |
| `data-min-h` | `Npt` (≥180pt) | 슬라이드 면적 25% 의무 (PF-70 — height<180pt ERROR) |
| `data-nano-prompt` | 자연어 prompt | Gemini 호출 본문 |

---

## 2. 선택 속성 (optional)

| 속성 | 기본값 | 설명 |
|------|-------|-----|
| `data-theme-mood` | 슬라이드의 `[data-theme]` 자동 추론 | 강제 override 시 명시 |
| `data-radius` | shape 에 따름 | 명시 시 우선 (rect+12pt 등) |
| `data-mask-clip-path` | (없음) | 임의 SVG clip-path |
| `data-alt` | data-nano-prompt 의 첫 12 단어 | `<img alt>` 채울 텍스트 |
| `data-fallback-svg` | (없음) | 생성 실패 시 사용할 정적 SVG 경로 |
| `data-priority` | `normal` | `high` 시 generate-images.mjs 가 먼저 처리 |
| `data-seed` | (random) | Gemini seed 명시 (재현성) |

---

## 3. 테마별 무드 매트릭스 (data-theme-mood)

`data-theme-mood` 가 없으면 슬라이드의 `[data-theme]` 에서 자동 추론. generate-images.mjs 가 무드별 **prefix 를 NanoBanana prompt 에 prepend**.

| theme-mood | Prefix prepend | 허용 | 금지 |
|------------|---------------|-----|------|
| `modern` | `"cool editorial photography, mid-key lighting, desaturated, neutral gray with steel blue cast, no warm tones, magazine-quality, "` | semiconductor / lab / office architecture / abstract industrial | warm stock photo, smiling people in meetings, golden hour |
| `classic` | `"high-formality photograph, near-monochrome with subtle warmth, low saturation, classical composition, Bauhaus or 1930s editorial tone, "` | portraiture / heritage / architecture / serious business interior | colorful, casual, video thumbnail style, group casual photos |
| `dark-mono` | `"high contrast tech photography, deep blacks, single-color highlight, abstract industrial texture or close-up macro, no harsh sun, "` | abstract circuit / dark labs / single product on black / data visualizations | bright daylight, group photos, soft natural light, warm tones |
| `editorial` (별도 트랙) | `"warm editorial magazine photography, golden hour lighting, film grain, fashion-magazine composition, "` | heritage, lifestyle, products, environment | corporate stock, harsh fluorescent, isolated objects on white |
| `company` (v3) | TBD — 사내 마스터 이미지 라이브러리에서 참조 인덱스 사용 | TBD | TBD |

**공통 금지** (모든 무드):
- 국기 이모지 / 텍스트 in image
- AI 글자 (한글, 영문, 숫자 — 이미지 안에 들어가면 거의 항상 깨짐)
- 가짜 데이터 인포그래픽 (차트 모양 픽쳐) — IL-30
- "smiling people in meetings" stock photo cliche
- 회사 로고 / 상표 / 인지 가능한 브랜드 마크

---

## 4. 클라우드 (이 환경) 에서 슬롯의 동작

### 4.1 디자인 작성 단계

LLM 이 `image-slot` div 를 만들고 `data-nano-prompt` 를 채운다. 시각적으로는 `_image-slot.css` 가 다음을 렌더:

```
┌─────────────────────────────┐
│   ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
│   ┊                       ┊  │
│   ┊  Q1 매출 히어로 이미지   ┊  │
│   ┊  hero-q1-revenue       ┊  │
│   ┊  rect · 4:3 · modern   ┊  │
│   ┊                       ┊  │
│   └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
└─────────────────────────────┘
```

점선 박스 + slot ID + spec, hover 시 `data-nano-prompt` 전문 표시.

### 4.2 디자인 리뷰 단계 (사용자)

`image_slot.js` 스타터 컴포넌트 활성화 시:
- 사용자가 reference 이미지를 슬롯에 **드래그-드롭** 가능
- localStorage 에 보존 → 새로고침 후에도 유지
- 이는 **단지 디자인 검토용** 임시 이미지. 로컬에서 generate-images.mjs 가 진짜 이미지를 생성하면 교체됨.

### 4.3 변환 sanity check (gen_pptx)

gen_pptx 호출 시 슬롯이 있는 상태로 변환하면 — 점선 박스가 그대로 PPTX 에 들어감 (placeholder). 디자이너가 "변환 후 깨지지 않는지" 확인하는 용도. 최종 deliverable 은 로컬에서.

---

## 5. 로컬 (slides-grab) 에서 슬롯의 동작

### 5.1 generate-images.mjs 가 하는 일

```js
// scripts/generate-images.mjs (개요)
const slots = doc.querySelectorAll('.image-slot');
for (const slot of slots) {
  const id = slot.dataset.slotId;
  const prompt = slot.dataset.nanoPrompt;
  const mood = slot.dataset.themeMood || inferFromHtmlTheme();
  const aspect = slot.dataset.aspect;

  // theme-mood prefix prepend
  const fullPrompt = THEME_PROMPTS[mood] + prompt;

  // Gemini 호출 (NanoBanana)
  const png = await gemini.generate({
    prompt: fullPrompt,
    aspectRatio: aspect,
    seed: slot.dataset.seed,
  });

  // 저장
  await fs.writeFile(`assets/${id}.png`, png);

  // HTML 패치: 슬롯 div 를 <img> 로 교체
  slot.outerHTML = `<img src="assets/${id}.png"
                         alt="${slot.dataset.alt || prompt.split(' ').slice(0,12).join(' ')}"
                         style="width:${slot.dataset.minW}; height:${slot.dataset.minH};
                                object-fit:cover; border-radius:${getRadius(slot.dataset.shape)};">`;
}
```

### 5.2 검증 게이트

이미지 생성 후:
- **PF-70**: 이미지 면적 ≥ 슬라이드 면적의 25% (width≥260pt·height≥180pt 미달 시 ERROR) + width/height inline pt 명시 의무. *(PF-57 은 width<100pt / height<80pt "컨테이너 대비 과소" WARN 으로 별개 — 25%/260/180 게이트는 PF-70 소관)*
- **PF-58**: `<img src>` 파일이 `assets/` 에 실제로 존재
- **PF-43 / PF-21**: `object-fit: cover` 사용, 비율 왜곡 없음
- **PF-21**: 표시 박스 scale 축 차이 > 5% 면 distorted WARN. `object-fit: cover/contain/scale-down` 은 비율 보존이므로 면제 *(문서의 "±20%" 표현은 코드 게이트와 무관 — 실측은 scale 5% 기준)*

### 5.3 fallback

Gemini 호출 실패 시:
1. `data-fallback-svg` 명시되어 있으면 사용
2. 없으면 슬롯 div 그대로 유지 (placeholder) + audit 기록

---

## 6. 슬롯 ID 작명 규칙

`data-slot-id` 는 deck 내 unique + 의미 있는 kebab-case.

✅ `hero-q1-revenue`, `north-america-trend-chart`, `team-photo`, `factory-floor-overview`
❌ `image1`, `pic`, `placeholder`, `슬롯`

생성된 파일명도 동일: `assets/hero-q1-revenue.png`.

---

## 7. shape ↔ CSS 매핑

| `data-shape` | CSS |
|--------------|-----|
| `rect` | `border-radius: 0` |
| `rounded` | `border-radius: 12pt` |
| `circle` | `border-radius: 50%` + 정사각형 aspect 강제 (1:1) |
| `pill` | `border-radius: 9999px` |

`data-mask-clip-path` 명시 시 임의 SVG clip-path 적용 (shape 무시).

---

## 8. 새 슬롯 등록 시 체크리스트

1. [ ] `data-slot-id` 가 deck 내 유일한가?
2. [ ] `data-nano-prompt` 가 충분히 구체적인가? (≥ 15 단어 권장, ≤ 80 단어)
3. [ ] `data-theme-mood` 가 슬라이드 `[data-theme]` 와 일치하는가?
4. [ ] `data-aspect` 와 `data-min-w`/`data-min-h` 가 일관되는가?
5. [ ] 슬롯이 본문 영역 (source line 위) 안에 있는가?
6. [ ] 슬라이드당 슬롯 ≤ 3개인가? (PF-26 — 콘텐츠 블록 한도)

---

## 9. 변경 시 동기화

이 contract 가 갱신되면:

- 클라우드: 이 파일 + `_image-slot.css` + `nano_banana_guide.md` 동시 갱신
- 로컬: `scripts/generate-images.mjs` 의 prompt prefix + slot 탐지 로직 갱신
- 양쪽: 회귀 테스트 — 기존 deck 의 이미지가 동일하게 생성되는지 (`tests/image-regression/`)

원칙: 슬롯의 **마크업 형식이 바뀌면 generate-images.mjs 도 즉시 따라간다**. 한쪽만 바꾸면 다음 빌드부터 모든 슬롯이 빈 박스가 된다.

---

## 10. 반복 비용 가이드 — "이미지냐 레이아웃이냐"

final PPT 결과가 마음에 안 들 때, **어디서 고치는 게 싸냐**의 의사결정 트리.

### 10.1 비용 비대칭

| 변경 종류 | 비용 (시간) | 영향 범위 |
|---------|----------|---------|
| **이미지 prompt 수정** | ~30초 (Gemini 1콜) | 1 슬롯 |
| **이미지 seed 바꿔 재생성** | ~10초 | 1 슬롯 |
| **슬롯 aspect 변경** | ~1분 (HTML 1줄 + 재생성) | 1 슬롯 |
| **슬라이드 레이아웃 변경** | ~5분 (LLM 컨텍스트 + sync) | 1 슬라이드 |
| **테마 변경** | ~10분 (모든 슬라이드 영향 검토) | 덱 전체 |

→ **항상 위에서부터 시도. 안 되면 한 단계 내려간다.**

### 10.2 의사결정 트리

```
final PPT 보고 아쉬움
    │
    ├─ 이미지가 generic / 무드가 안 맞음
    │   → data-nano-prompt 수정 → 재생성 (30초)
    │
    ├─ 이미지가 prompt 와 다르게 나옴 (Gemini variance)
    │   → data-seed 바꿔 재시도 (10초)
    │
    ├─ 이미지가 잘림 / 비율 어색함
    │   → data-aspect 또는 data-min-w/h 수정 → 재생성 (1분)
    │
    ├─ 슬라이드가 답답함 / 빈 곳이 많음 / 구도 부조화
    │   → 진짜 생성된 이미지를 클라우드 슬롯에 drag-drop
    │   → 실물로 레이아웃 다시 보기
    │   → 슬롯 크기/위치 조정 또는 레이아웃 자체 교체 (5분)
    │
    └─ 메시지가 전달 안 됨 / 액션 타이틀 약함
        → 레이아웃 + 콘텐츠 모두 재검토. Claude Design 에서 새로 작성.
```

### 10.3 권장 반복 횟수

| 단계 | 1차 반복 횟수 (정상 범위) |
|-----|----------------------|
| 레이아웃 결정 | 1~2회 |
| 이미지 prompt 튜닝 | 2~4회 |
| 이미지 seed 시도 | 1~3회 |
| 슬롯 aspect 조정 | 0~1회 |

레이아웃을 3회 이상 다시 만들고 있다면 — 콘텐츠 자체를 재검토해야 함 (메시지가 흐트러진 것).
이미지를 5회 이상 재생성하고 있다면 — prompt 가 너무 추상적 (구체적으로 다시 작성).

### 10.4 "이미지를 클라우드로 옮겨와야 하나" 결정

기본 답: **아니오, 옮기지 마라.** 이미지는 로컬에만 두는 게 단순하고 빠르다.

옮기는 게 정당화되는 유일한 경우:
- 이미지 1~2개가 슬라이드 디자인 결정에 결정적 영향을 줄 때
- 위 트리의 "슬라이드가 답답함" 단계에 와서
- 그 한 슬라이드에 한해, 그 한 이미지에 한해

→ 수동 drag-drop 으로 충분. **자동 sync 단계 만들지 마라.** (오버엔지니어링)

---
