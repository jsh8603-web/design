# Nano Banana — image generation guide for this design system

> **v3 update**: 이 파일의 슬롯 마크업은 이제 `image_slot_contract.md` 에 권위 있게 정의됨. 이 파일은 **프롬프트 작성 가이드** 로 좁혀 사용. 4-aesthetic-direction (executive / dark-pitch / academic / editorial) 은 **mck 4-테마 시스템** (modern / classic / dark-mono / company) 으로 매핑됨 (§5 참조).

When you (Claude / human designer) work on a slide that *needs* a photo
or illustration, **do not invent a fake SVG, do not ask an external
image-gen service mid-design, and never call a model directly from
HTML**. Instead, this design system uses a two-step pattern:

1. **At design time** — place an `image_slot_contract.md` 규격의 슬롯 (`<div class="image-slot" data-slot-id=…>`) where the image goes. The slot carries `data-nano-prompt` 가 generation 시 사용될 영문 프롬프트.
2. **At image-gen time** — the user runs the slides-grab pipeline (`scripts/generate-images.mjs`) which reads `data-nano-prompt`, calls Gemini, drops `.png` into `assets/`, swaps the slot for `<img>`.

테마별 무드 prefix 는 generate-images.mjs 가 **자동으로 prepend** 합니다 (§5 매트릭스).

This file is the **design-system-facing summary** of the full
`nanoBanana-guide.md` that lives in the slides-grab codebase. Read this
first; consult the full guide when you need to write a new prompt or
debug a generation failure.

---

## Pipeline location (slides-grab/.claude/docs/nanoBanana-guide.md)

The authoritative rules live in:

- `slides-grab/.claude/docs/nanoBanana-guide.md` — 10 prompt rules,
  aspect ratio table, IV/IP/IC/VQA validators
- `slides-grab/.claude/docs/nanoBanana-prompt-library.md` — validated
  prompt templates by category
- `slides-grab/.claude/skills/plan-skill/SKILL.md` — outline tag format

This file mirrors the parts a designer touches.

---

## Claude can NOT generate images

When you (Claude / an HTML designer) are placing an image, you are
**only choosing the slot's size, position, prompt and alt text** —
never the pixels. The user invokes Gemini (`gemini-2.5-flash-image`
default, `gemini-3-pro-image-preview` for covers) via the pipeline.

If you find yourself drawing a fake "photo" SVG by hand, stop. Use the
slot pattern below.

---

## 1. The `<image-slot>` HTML pattern

The slot is a `<div>` with a fixed aspect, a dashed border, and a
visible prompt label. Once the image is generated, the user (or the
script) drops the rendered `.png` in and the slot becomes an `<img>`.

```html
<!-- Design-time placeholder -->
<div class="image-slot"
     data-slot-id="slide-03-hbm-cover"
     data-aspect="16:9"
     data-tier="1"
     data-prompt="A photorealistic aerial view of a semiconductor fab campus at golden hour, warm directional light, deep navy and electric blue tones, large empty area at top for text overlay, cinematic wide-angle composition, no text. 16:9 aspect ratio."
     style="aspect-ratio: 16/9; width: 100%;">
  <div class="image-slot__meta">
    <div class="image-slot__label">NanoBanana · slide-03 · 16:9 · Tier 1</div>
    <div class="image-slot__prompt">aerial view of a semiconductor fab campus at golden hour…</div>
  </div>
</div>

<!-- After image generation, replace with: -->
<img src="assets/slide-03-hbm-cover.png"
     alt="Semiconductor fab at golden hour"
     style="width: 100%; aspect-ratio: 16/9; object-fit: cover;">
```

CSS for the slot (drop into any slide-using CSS file):

```css
.image-slot {
  background: repeating-linear-gradient(
    45deg, #F0EBE3 0 8px, #FAF8F5 8px 16px);
  border: 1.5px dashed #C45A3B;
  border-radius: 4pt;
  position: relative;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.image-slot__meta {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  text-align: center; padding: 8pt 12pt;
  background: rgba(255,255,255,0.9); border-radius: 4pt;
  max-width: 80%;
}
.image-slot__label {
  font-size: 10pt; font-weight: 700;
  color: #C45A3B; letter-spacing: 0.06em; text-transform: uppercase;
}
.image-slot__prompt {
  font-size: 9pt; color: #5A554F;
  margin-top: 4pt; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}
```

See `_image-slot.css` in this folder for a ready-to-include version.

> **Note on PPTX export.** The `image-slot` placeholder violates PF
> rules (dashed border + decorative gradient) on purpose — it's a
> design-time-only marker that's *replaced before export*. If a slot
> ships to PPTX, the conversion will warn loudly.

---

## 2. Aspect ratio decision (don't default to 16:9)

| Layout in the slide | Container size | Aspect to request |
|---|---|---|
| Full-bleed cover / background | 720×405pt | **16:9** |
| 50:50 split, no inner padding | 360×405pt | **3:4** |
| 55:45 split, no inner padding | 396×405pt | **1:1** |
| Split with inner padding | ~330–360×290pt | **4:3** |
| Standalone icon / illustration | square | **1:1** |

Gemini supports: 16:9, 4:3, 3:4, 1:1, 3:2, 2:3, 9:16, 21:9.

**Don't use 16:9 for split layouts** — it crops the subject. The
`data-aspect` attribute on the slot must match what the container
actually offers.

---

## 3. Tier system (how much the image carries the slide)

| Tier | Concepts on slide | NanoBanana role |
|---|---|---|
| **1** | 1–2 | Hero photograph, fills ≥50% of slide |
| **2** | 3–5 | Background or icon set, HTML does the data |
| **3** | 6+ | Decoration only — or skip and go HTML-only |

A Tier 3 slide should usually **not** have a NanoBanana tag.
A 6-icon set spread across one slide is Tier 2, not 3.

---

## 4. The 10 prompt rules (slides-grab canon)

| # | Rule | One-line summary |
|---|---|---|
| 1 | **Sentences, not keyword soup** | `BAD: "dog, park, 4k"` → `GOOD: "A golden retriever playing fetch in a sunlit park, 85mm lens, shallow DOF"` |
| 2 | **Declare intent first** | `"A professional presentation slide background for a tech quarterly report…"` |
| 3 | **No text** | Always end with `"No text whatsoever."` Avoid prompt subjects with inherent text (compass, clock, gauges, keyboards, newspaper, signs, license plates). |
| 4 | **Positive phrasing only** | `BAD: "no cars"` → `GOOD: "An empty serene street with clean sidewalks"` |
| 5 | **Camera language for framing** | `wide-angle`, `85mm portrait lens`, `low-angle`, `bird's-eye`, `elevated 45°`, `macro shot`. |
| 6 | **Always describe light** | `soft golden-hour light`, `three-point softbox`, `cinematic lighting`, `cold clinical`, `warm ambient glow`, `rim lighting`. |
| 7 | **Color names, never hex** | Gemini renders hex codes as literal text. Say `deep navy`, `warm amber`, not `#1428A0`. |
| 8 | **Style anchors** | Combine 2–4 (max — over-stacking lowers VQA). See per-direction presets below. |
| 9 | **Background slides need negative space** | `"muted, subtle, desaturated"` + `"large negative space for text overlay"`. Frame/diagram → use `"light gray background"` (`#E5E7EB`–`#F1F5F9`) — pure white fails IV-03. |
| 10 | **Split layouts (4:3, 3:4) need framefill** | The text lives in another column, so don't ask for negative space. Use `"centered composition, subject fills the frame, even balanced lighting, sharp focus"`. |

Plus rule 11 (consistency): generate the **first** image, then pass it
as a reference image for the rest of the deck via `--chain` mode.

---

## 5. Per-theme prompt presets (v3 — 8-테마 통합 시스템)

각 테마는 **2~4 단어 style anchor + 색 톤 + 금지 단어** 를 가짐. 슬라이드의 `[data-theme]` 가 결정하면 slot 의 `data-theme-mood` 가 자동으로 그 테마. `generate-images.mjs` 가 아래 prefix 를 NanoBanana prompt 에 prepend.

**v3 통합 결과**: slides-grab v2 의 4 aesthetic direction 은 별도 매핑 대신 자체 테마로 승격. 모두 mck 와 동등한 peer level.

| 테마 | 출처 | 용도 |
|---|---|---|
| `modern` | mck v3 | FP&A 분기 리뷰, 사내 보고 |
| `classic` | mck v3 | 임원·이사회, 정통 McKinsey |
| `dark-mono` | mck v3 | 기술 컨설팅, 키노트 (다크) |
| `company` | mck v3 | (v3) 사내 마스터 어댑터 |
| `executive-editorial` | slides-grab v2 흡수 | 한국 IR / 투자메모 / 임원보고 |
| `dark-pitch` | slides-grab v2 흡수 | AI 스타트업 IR / YC-스타일 키노트 |
| `academic` | slides-grab v2 흡수 | 학술 / 연구 / 백서 |
| `editorial` | slides-grab v2 흡수 | 분기 에세이 / 연간보고 / 창립자 letter (Track B chrome) |

---

### Theme `modern` → cool editorial (FP&A / 사내 보고)

```
Prefix:        "cool editorial photography, mid-key lighting,
                desaturated, neutral gray with steel blue cast,
                no warm tones, magazine-quality"
Style anchors: corporate, polished editorial, professional, clean
Tone words:    neutral, mid-key, restrained
Color names:   warm graphite, deep navy, muted amber, charcoal,
               steel blue
Avoid:         vibrant, neon, cartoon, hand-drawn, warm stock photo,
               smiling people in meetings, golden hour
Tier policy:   1~2 only. Tier 3 slides go HTML-only.
```

예시 cover prompt (modern):

```
A photorealistic aerial photograph of a semiconductor fab campus, mid-key
diffused daylight, cool overcast lighting. Cooling towers and a substation
visible across a flat industrial landscape. Steel blue and neutral gray
palette, slight desaturation. Cinematic wide-angle composition. Large
empty area at top for text overlay. Polished editorial corporate
aesthetic. No text whatsoever. 16:9 aspect ratio.
```

---

### Theme `classic` → formal heritage (임원·이사회)

```
Prefix:        "high-formality photograph, near-monochrome with subtle
                warmth, low saturation, classical composition, Bauhaus
                or 1930s editorial tone"
Style anchors: formal, heritage, near-monochrome, classical
Tone words:    serious, considered, restrained, dignified
Color names:   warm graphite, cream, charcoal, deep navy
Avoid:         colorful, casual, video thumbnail style, modern tech,
               group casual photos
Tier policy:   1 only. Heavily prefer HTML/CSS for data.
```

예시 cover prompt (classic):

```
A black-and-white photograph of a modernist boardroom interior with
classical proportions, single subject (an empty leather chair at the
head of a polished wood table), soft directional north light, deep
shadow areas, restrained composition with strong vertical lines. Near-
monochrome with subtle warm cream undertones. Large negative space on
the right. No text whatsoever. 16:9 aspect ratio.
```

---

### Theme `dark-mono` → high-contrast tech (키노트 / 발표)

```
Prefix:        "high contrast tech photography, deep blacks, single-color
                highlight, abstract industrial texture or close-up macro,
                no harsh sun"
Style anchors: cinematic, neon noir, high contrast, futuristic
Tone words:    bold, expressive, dark mode
Color names:   jet black, electric cyan, charcoal, amber accent
Avoid:         pastel, soft, daylight, "smiling people", warm tones,
               group photos
Tier policy:   1~2. Heavy hero photographs; avoid icon sets.
```

예시 cover prompt (dark-mono):

```
A macro photograph of a cutting-edge AI accelerator chip on a dark
circuit board, intricate copper traces and electric cyan light bleeding
from the under-side, jet-black surroundings, rim lighting, shallow
depth of field with the chip in sharp focus. Cinematic, futuristic,
high-contrast tech aesthetic. No text whatsoever. 16:9 aspect ratio.
```

---

### Theme `company` → v3 슬롯

사내 master 어댑터가 채우기 전까지 `modern` prefix 폴백.
master 가 채워지면 사내 브랜드 사진 라이브러리 인덱스 참조로 전환 예정 — Gemini 호출 자체가 생략될 수 있음.

---

### (별도 트랙) Academic / Editorial

이 두 트랙은 **mck 매트릭스 밖** 에 있는 별도 트랙. theme_layout_matrix.md 의 4-테마와 섞이지 않음.

`academic`: 커버에만 NanoBanana 허용. 나머지는 HTML/CSS.
`editorial`: hero + photo essay grids 만. 잡지 무드.

원하면 별도 `theme_layout_matrix_editorial.md` 와 묶어서 다른 deck 트랙으로 사용.

---

### Theme `executive-editorial` → warm corporate editorial (한국 IR / 투자메모)

```
Prefix:        "warm corporate editorial photography, soft directional
                lighting, restrained palette of warm graphite and deep
                navy, professional polish, hairline detail focus"
Style anchors: corporate, polished editorial, restrained, professional
Tone words:    warm, considered, polished
Color names:   warm graphite, deep navy, muted amber, ivory, charcoal
Avoid:         neon, cartoon, hand-drawn, smiling group photos, harsh sun
Tier policy:   1~2 (hero photo, occasional context). Tier 3 → HTML only.
```

예시 cover prompt:

```
A wide-angle photograph of a semiconductor fab campus at golden hour,
cooling towers and substation visible across a flat landscape. Warm
directional light, deep navy and muted amber palette. Restrained corporate
editorial aesthetic, polished detail. Large empty area at top for text
overlay. No text whatsoever. 16:9 aspect ratio.
```

---

### Theme `dark-pitch` → cinematic neon noir (스타트업 IR / 키노트)

```
Prefix:        "cinematic neon noir photography, jet-black surroundings,
                electric cyan highlights, rim lighting, futuristic tech
                aesthetic, deep contrast"
Style anchors: cinematic, neon noir, futuristic, high contrast
Tone words:    bold, expressive, dark mode
Color names:   jet black, electric cyan, charcoal, amber accent
Avoid:         pastel, soft daylight, "smiling people", warm wood tones
Tier policy:   1~2. Heavy hero photographs; avoid icon sets.
```

예시 cover prompt:

```
A macro photograph of a cutting-edge AI accelerator chip on a dark circuit
board, intricate copper traces, electric cyan light bleeding from
underneath, jet-black surroundings, rim lighting, shallow DOF with chip
in sharp focus. Cinematic futuristic high-contrast tech aesthetic. No
text whatsoever. 16:9 aspect ratio.
```

---

### Theme `academic` → scholarly research photography (학술 / 백서)

```
Prefix:        "scholarly research photograph, neutral muted palette,
                soft diffused light, clean architectural lines,
                restrained composition"
Style anchors: scholarly, neutral, restrained, photographic
Tone words:    formal, considered, calm
Color names:   neutral gray, navy blue, ivory, muted slate
Avoid:         vibrant, cartoon, infographic, stock photo people
Tier policy:   COVER ONLY. All other slides → HTML/CSS charts and tables.
```

예시 cover prompt (academic mode 의 유일한 NanoBanana):

```
A wide-angle photograph of a modern university research building at dawn,
soft diffused light, clean architectural lines, scholarly atmosphere,
large empty area on the right for text overlay. Neutral muted gray and
navy palette. No text whatsoever. 16:9 aspect ratio.
```

---

### Theme `editorial` → warm magazine editorial (분기 에세이 / 연간보고)

```
Prefix:        "warm editorial magazine photography, golden hour lighting,
                fine grain texture, terracotta and cream palette,
                hand-crafted considered composition, magazine quality"
Style anchors: magazine editorial, fine-grain, warm, organic
Tone words:    contemplative, hand-crafted, considered
Color names:   terracotta, cream, charcoal, muted moss
Avoid:         tech, neon, screens, UI, harsh fluorescent
Tier policy:   1 (hero) and 2 (photo essay grids).
```

예시 cover prompt:

```
A photograph of a single seedling pushing through cracked concrete,
dramatic side lighting, fine grain texture, warm cream and terracotta
palette, magazine editorial aesthetic, hand-crafted composition. Subject
fills the frame, centered, sharp focus. No text whatsoever. 3:4 portrait
aspect ratio.
```

---

### `editorial` 트랙 특수성

`editorial` 은 다른 7 테마와 다른 chrome 시스템 (essay headline serif, drop cap, italic em accent). action title 룰 적용 안 됨. NanoBanana 사용 빈도 가장 높음 (잡지 photo essay 등).

---

## 6. The `NanoBanana:` outline tag — what the pipeline actually reads

When the slide is finalised, transcribe the slot into the slide outline
file (`slide-outline.md`) as a single line:

```
- NanoBanana: [한글 설명] | [English prompt with rules 1–10 applied]
```

Examples (from real slides-grab decks):

```
- NanoBanana: AI 데이터센터 네트워크 표지 |
  [16:9] A photorealistic aerial view of Earth at night showing
  interconnected city lights and glowing network lines spanning across
  continents, warm golden light reflecting off the ocean surface, deep
  navy and electric blue tones, full cinematic composition, no text.
  16:9 aspect ratio.

- NanoBanana: NVIDIA Blackwell GPU 클로즈업 |
  [3:4] A photorealistic macro photograph of a cutting-edge AI
  accelerator chip on a circuit board, intricate copper traces and
  brass-toned metallic contacts visible across the surface, warm
  directional studio lighting highlighting the chip architecture,
  shallow depth of field with the chip in sharp focus, no text. 3:4
  portrait aspect ratio.
```

If the slide doesn't need an image:

```
- NanoBanana: 없음
```

---

## 7. The validators (so you can read failure messages)

The pipeline runs 4 validators on generated images. You don't run these
yourself — but if a generation fails, the error code tells you which
rule to revisit.

| Code | Stage | Checks | If it fires |
|---|---|---|---|
| **IP** Image Preflight | before generation | Korean in prompt, hex codes, fake data, text-rendering keywords | Edit the prompt. Re-run `--dry`. |
| **IV** Image Validate | after generation | Safety filter, brightness (<30 or >240), file size, aspect ratio drift, palette match (CIEDE2000) | Tweak prompt brightness/composition. `--regenerate N`. |
| **VQA** Visual QA | after generation | 5-axis 1–5 score: prompt fidelity, no-text, composition, color harmony, presentation fit. Total 23+ PASS, 20–22 WARN, <gate FAIL. | Apply VQA feedback. Switch image type as last resort. |
| **IC** Image in Context | after PPTX insertion | Loading, contrast against overlay text, crop/aspect, resolution | Usually adjust HTML overlay, not the image. |

The full validator table is in
`slides-grab/.claude/docs/nanoBanana-guide.md`.

---

## 8. When to NOT use NanoBanana

Refuse the image if:

- The slide has **numeric data** to communicate → HTML/CSS chart
- The slide has a **process/flow with 3+ steps** of real data → HTML diagram
- You'd be asking Gemini to render **Korean text** (always wrong)
- The slide is **Academic mode** and you've already used the cover image
- A **single SVG icon** would do — use one from `assets/icons/` instead
- You're tempted to ask for an **infographic with fake numbers** —
  never. It produces "AI slop" that looks confident and is wrong.

---

## 9. Quick checklist before saving a prompt

- [ ] Begins with intent declaration ("A professional presentation
      background for…")
- [ ] Camera language for framing
- [ ] Light description
- [ ] Color names (no hex)
- [ ] 2–4 style anchors from your direction's preset
- [ ] Negative-space clause (cover/bg) OR fills-frame clause (split)
- [ ] Ends with `"No text whatsoever."`
- [ ] Aspect ratio matches container
- [ ] Tier matches concept count
- [ ] Korean only in the `[한글 설명]` part, never in the English prompt
