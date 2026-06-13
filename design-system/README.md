# slides-grab Design System

An agent-first design system for **slides-grab** — a presentation framework that lets
coding agents (Claude Code, Codex) **plan → design → visually edit → export** HTML
slides to PPTX/PDF. The aesthetic blends **Material 3** foundations (elevation by
tint, dynamic accent, density tokens, shape scale) with **slides-grab's** signature
warm-graphite editorial slide look — and is constrained throughout by the project's
**PF (Presentation Flow) safety rules** so anything we design here converts cleanly
to PowerPoint.

> 한국어 메모: HTML 생성시에 PPTX 로 대체로 안전한 전환이 보장되는 PF 규칙을 사용한다.
> Every CSS choice in this system is PF-compliant. See VISUAL FOUNDATIONS → PF rules.

---

## v3 — mck-slide-design 통합 (2026.05)

이 디자인 시스템은 v3 부터 **mck-slide-design-system** 을 흡수하고 slides-grab v2 의 4 aesthetic direction 을 정식 테마로 승격해 **단일 8-테마 시스템 + 48-레이아웃 카탈로그 + 도메인 invariants + QA 파이프라인**으로 통합됨. 이전 9-테마 + 4-aesthetic-direction 의 자유 혼합 문제는 **테마×레이아웃 잠금 매트릭스**로 차단.

### v3 핵심 변경

| 영역 | v2 (이전) | v3 (이번 통합) |
|------|----------|---------------|
| **테마 수** | 9개 + 4 aesthetic direction (불통일) | **8개 통합** (`modern` · `classic` · `dark-mono` · `company` + `executive-editorial` · `dark-pitch` · `academic` · `editorial`) |
| **토큰 모델** | 표면-명명 (`--bg-primary` 등) | **의미적** (`--primary` / `--accent` / `--surface-inverse` …) |
| **테마 전환** | 파일별 다른 CSS | **`[data-theme]` 한 줄** |
| **타입 스케일** | 정의는 있으나 자유 | **잠금** (44 / 28 / 24 / 22 / 18 / 16 / 14 / 12 / 9pt) |
| **레이아웃 카탈로그** | 5 슬라이드 + 4×5 aesthetic = 자유 | **48 LayoutSchema 박제 + 전수 HTML 레퍼런스** (`layout_catalog.md`) |
| **테마-레이아웃 결합** | 자유 혼합 (문제) | **잠금 매트릭스** (`theme_layout_matrix.md`) ⭐ |
| **액션 타이틀** | 정성 가이드 | **명사형 종결 자동 검증** (tone.py 박제) |
| **도메인 invariants** | 없음 | `cost_nature` · `surface_inverse` · EA font · `_clean_shape` |
| **QA 파이프라인** | PF rules (HTML 단계만) | + **9 per-slide check + 6 autofix** (post-convert) |
| **이미지 슬롯** | `<image-slot>` 단일 형식 | **계약 박제** (`image_slot_contract.md`) — 테마별 무드 매트릭스 |
| **클라우드↔로컬** | 비공식 | **공식 분담 + sync 절차** (`pipeline_handoff.md`) |

### v3 새로 추가된 파일

| 파일 | 목적 |
|------|-----|
| `theme_layout_matrix.md` ⭐ | 8 테마 × 48 레이아웃 잠금 매트릭스. **mixing 차단 핵심.** |
| `layout_catalog.md` | 48 레이아웃의 LayoutSchema + 전수 HTML 레퍼런스 위치 — **layer 2 Schema** |
| `layout_geometry.md` ⭐ | 46 레이아웃의 **정확한 좌표·치수·색 매칭** + 7개 반복 패턴 — **layer 4 Geometry** |
| `prompting_rules.md` | 에이전트 행동 계약 (액션 타이틀, 타입 스케일, 색 토큰, CJK) |
| `domain/fpna_invariants.md` | `cost_nature` · `surface_inverse` · EA font 도메인 불변 |
| `qa_rules.md` | 9 per-slide check + 8 autofix rule (mck 흡수) |
| `code_inventory.md` | mck 5-레이어 전체 인벤토리 (spec_normalizer, errors, adapter, builder API, robustness test) |
| `image_slot_contract.md` | 이미지 슬롯 계약 + 테마별 무드 매트릭스 |
| `pipeline_handoff.md` | 클라우드 ↔ 로컬 책임 분담, sync 절차 |
| `mck/slides/*.html` | mck reference 17 + catalog-additions 10 + **catalog-additions-2 21** = 48 전수 (1280×720, theme toggle) |
| `mck/assets/*.js` | 데이터-드리븐 차트 (waterfall, donut, kpi-dashboard, variance-table) + chart-helpers |

### mck 5-레이어 아키텍처 (이제 모두 박제됨)

| # | 레이어 | 위치 | 역할 |
|---|------|-----|-----|
| 1 | **Token** | `colors_and_type.css` `[data-theme]` | 색·폰트·치수 (4 테마) |
| 2 | **Schema** | `layout_catalog.md` | spec 키 계약 (required/optional/bounds) |
| 3 | **Inference** | `layout_catalog.md` §Quick Reference + `code_inventory.md` §⑨ | spec → 레이아웃 추론 |
| 4 | **Geometry** | `layout_geometry.md` | **각 레이아웃의 정확한 공간 레시피** (7 패턴 + 46 layout 1-line) |
| 5 | **Builder / QA** | `qa_rules.md` + `code_inventory.md` §⑤⑥⑦⑪ | 빌드·검증·autofix·CLI |

### 슬라이드 생성 의무 순서 (v3)

`prompting_rules.md` §0:

1. **테마 결정** — `<html data-theme="modern|classic|dark-mono|company">`
2. **레이아웃 선택** — `layout_catalog.md` 카탈로그에서. 자유 발명 금지.
3. **매트릭스 검증** — `theme_layout_matrix.md` 에서 (theme, layout) ✅ 확인
4. **LayoutSchema 준수** — required 필드 + bounds
5. **invariants 적용** — `cost_nature`, `surface_inverse` 등
6. **PF rules 준수** — `pf_rules.md`
7. **QA 통과 가능성** — `qa_rules.md` 의 9 체크 정신으로 자가 검토

PF 룰 신규: PF-69 (테마×레이아웃 매트릭스), PF-70 (`data-layout` 의무), PF-71 (`data-theme` 의무), PF-72 (LayoutSchema 위반), PF-73 (`primary` 풀블리드 금지), PF-74 (whitespace), PF-75 (명사형 종결).

### 기존 시스템의 위치

- v2 의 `themes/` 9개 파일, `aesthetics/` 4 direction × 5 = 20 슬라이드는 **레거시로 보존**. 새 deck 에서 직접 참조하지 않는다.
- `ui_kits/editor/` (에디터 앱) 은 v3 매트릭스 밖. 별도 다크 슬레이트 시스템 유지.
- `slides/` 의 slides-grab 원본은 v3.1 에서 전부 1280×720 마이그레이션 + `data-theme`/`data-layout` 태깅 완료 (PF-70·71 정합). `quote`·`meet_the_team` 은 토큰화 + image-slot 로 정식 카탈로그 레이아웃 승격. 나머지 8개(cover/section_divider/closing/data_table/side_by_side/toc/three_stat/waves_timeline)는 **legacy 데모 템플릿** — 고정 팔레트 유지, 동일 레이아웃의 canonical 레퍼런스는 `mck/slides/` 에 있다.

---

## Sources

| Source | Path / URL | Role |
|---|---|---|
| `slides-grab/` codebase | local mount, read-only | Templates, themes, editor, PF rules — **source of truth** |
| `material3.fig` | Figma virtual mount (`/Page-1`, 0 frames) | Empty stub — Material 3 used as **principles**, not assets |
| GitHub | <https://github.com/vkehfdl1/slides-grab> | Upstream repository |
| Built on | [ppt_team_agent](https://github.com/uxjoseph/ppt_team_agent) by Builder Josh | Acknowledged predecessor |

---

## Products represented

The system covers **two distinct visual surfaces**. Treat them as separate UI kits;
they share tokens but diverge in tone.

1. **The Editor** (`ui_kits/editor/`) — the in-browser tool agents and humans use to
   bbox-select, direct-edit, and agent-rewrite slides. **Dark slate, Inter-like
   density, blue accent.**
2. **The Slide System** (`ui_kits/slides/`) — the deliverable. Pretendard, warm
   off-white canvas, dark ink, pill section badges, hairline circles with arrows
   (↗ ↘ →), bold action titles, hero KPI numbers. Five sub-themes available:
   *Executive*, *Corporate*, *Modern Dark*, *Sage*, *Warm*.

---

## Index

| File / folder | Purpose |
|---|---|
| `README.md` | This file — context, foundations, fundamentals |
| `LOCAL_SETUP.md` | **Running locally** (Claude Code / Codex) — preview server + PPTX setup |
| `serve.py` | Local static preview server (`python serve.py --open`) for ES-module slides |
| `SKILL.md` | Cross-compatible Agent Skill manifest |
| `colors_and_type.css` | Foundation tokens — colors, type, spacing, radii, motion |
| `_image-slot.css` | Image-slot HTML pattern (nano-banana placeholder) |
| `nano_banana_guide.md` | **Design-time guide for image generation via Gemini NanoBanana** |
| `fonts/` | `fonts.css` (@font-face) + `README.md` (download URLs) + `files/` (drop .woff2 here) |
| `assets/` | Logos, icon registry, sample illustrations |
| `preview/` | Cards rendered into the Design System review tab |
| `ui_kits/editor/` | The slides-grab editor app (dark slate) |
| `ui_kits/slides/` | The slide deliverable system (warm executive default) |
| `slides/` | Five reference slide types: cover, content, statistics, quote, contents |
| `themes/` | **Nine theme CSS files** — 5 original + 4 aesthetic directions |
| `aesthetics/` | **4 aesthetic directions × 5 templates** (20 slides) + comparison index |
| `pf_rules.md` | Quick reference of PPTX-safe HTML constraints |

---

## CONTENT FUNDAMENTALS

### Voice & tone

slides-grab is **engineer-direct, lowercase, lightly opinionated**. The README opens
with a centered tagline ("Select context for agents directly from AI-generated HTML
slides") and immediately tells you *how* — no marketing throat-clearing.

- **Audience:** developers and AI agents. Copy is read by Claude Code / Codex
  as often as by humans, so it must parse cleanly: short sentences, terse lists,
  predictable headers (e.g. "Quick Start", "Why This Project?", "CLI Commands").
- **Person:** **you** for the user. The product itself ("the Agent", "the
  Converter") is named, not "we". No "I".
- **Casing:** Title Case for primary headers, sentence case for body. CLI commands
  in `monospace` always.
- **Emoji:** **avoid in product UI and English copy.** The deliverable slides do
  occasionally use emoji as feature icons (🌐 🔍 ✍️ 🖼️) where the design mode
  permits it — but PF rules forbid country-flag emoji and rely on PNG/SVG icons
  for anything load-bearing.
- **Korean is first-class.** README-KO.md mirrors README.md. Production slides
  routinely interleave English (`Q4 OP 20.1조 최초 분기 20조 돌파`) — Pretendard
  is chosen precisely for this CJK/Latin balance.

### Slide copywriting — the "Action Title" rule

This is the most distinctive content rule in the system. Every slide title is an
**assertion (a complete sentence)**, not a topic label.

| ❌ Topic label | ✅ Action title |
|---|---|
| "Market Analysis" | "동남아 시장이 3년 내 2배 성장한다" |
| "Q3 Performance" | "Q3 매출이 전년 대비 23% 증가했다" |
| "Conclusions" | "처리군이 대조군 대비 37% 높은 반응률을 보였다" |

Supplementary rules from the codebase:

- **Ghost Deck Test:** read titles in order — the deck's argument must land.
- **1 slide = 1 message.** Supporting data → appendix.
- **Numbers are the visual.** Display them as Hero Numbers (48pt+, weight 800),
  not buried in paragraphs.
- **Word ceiling:** 120 EN / 80 CJK words per slide (excluding sources & captions).
- **Sources are mandatory.** Bottom-right, 10pt, gray (`#999`), `Author, Year`
  for academic; institutional name + report date for business.

### Quick examples of in-product copy

- CLI verbs: `edit`, `build-viewer`, `validate`, `convert`, `pdf`, `list-templates`.
  Verbs only, lowercase. (See `bin/ppt-agent.js`.)
- Validator names: `PF` (Preflight), `VP` (Validate PPTX), `COM` (Vision),
  `IV` (Image Validation), `VQA`. Two-letter codes feel like CI checks.
- Issue classification taxonomy: **False Positive / True Positive (fixable) /
  True Positive (limitation).** This taxonomy is the canonical way to talk about
  any detector output in product copy.

---

## VISUAL FOUNDATIONS

### Type

- **Primary:** **Pretendard** (orioncactus, v1.3.9) loaded via jsDelivr CDN.
  Chosen for Korean + Latin balance and a wider x-height than Inter. Weights
  used: 400, 500, 600, 700, 800.
- **Mono:** **JetBrains Mono** (Google Fonts) — only in the editor, never on slides.
- **Hard floor (Minimal mode):** 24pt title, 14pt body, 10pt caption. **Never
  render text smaller than 10pt** in PPTX-bound HTML.
- **Action titles** use 17pt / weight 700 / line-height 1.25 / `letter-spacing:
  -0.01em`. **Hero KPI numbers** use 48pt / weight 800 / line-height 1.10 /
  `letter-spacing: -0.02em`.

### Color

The system has three palette layers:

1. **Neutrals** — warm graphite (`#1A1A1A` → `#F5F5F0`). The canonical canvas is
   `#F5F5F0` (Executive warm white), with `#FFFFFF` as elevated card surface and
   `#1A1A1A` as ink.
2. **Five named themes** — `executive` (warm white default), `corporate` (clean
   white + blue), `modern-dark` (pure black), `sage` (`#B8C4B8` mossy green),
   `warm` (terracotta `#C45A3B`). Each defined in a small `themes/*.css` file
   with `--bg-*` / `--text-*` / `--accent` / `--border` vars.
3. **Professional palettes (10 numbered options)** — *Midnight Executive*,
   *Forest & Moss*, *Slate Authority*, *Navy Precision*, *Charcoal & Gold*, *Deep
   Burgundy*, *Steel & Teal*, *Warm Graphite*, *Cobalt Strategy*, *Monochrome
   Power*. Selected per-deck in the outline metadata.

**Editor app** uses a separate, darker palette: `--app-bg-0: #030711`, panel
`#0F172A`, border `#1E293B`, blue accent `#3B82F6`.

### Backgrounds

- **Mostly solid hex.** PF rules forbid `rgba()` backgrounds and `linear-gradient`
  under light text. Tinted elevation is via solid `#FFFFFF` cards on warm canvas,
  not shadow.
- **Body backgrounds may be images** (`background: url()` on `<body>` only — never
  on child divs, PF-05).
- **Hero cover slides** use a full-bleed `<img class="bg">` + a solid-color
  overlay div (`#121726` at full opacity, not `rgba`) + text on top with
  `text-shadow: 0 2px 12px rgba(0,0,0,0.5)`. This is the only place rgba lives,
  and only in shadow.
- **No** repeating patterns, no noise textures, no grain.

### Borders & dividers

- Hairline: `1px solid #E5E5E0` (or `#eee`) for card separators.
- Strong: `1.5px solid` for input focus, `2px` for primary buttons in app.
- Section dividers in TOC: `border-bottom: 1px solid rgba(0,0,0,0.1)` on rows.
- Pill badges: `border: 1px solid #1A1A1A; border-radius: 12pt; padding: 4pt 10pt`.

### Cards

Two patterns coexist:

1. **Slide cards** (PPTX-safe): `background: #FFFFFF; border-radius: 8pt; padding:
   14pt 16pt;`. **No shadow.** Elevation conveyed by surface lift (white on warm
   canvas).
2. **App cards** (browser-only): `background: #0F172A; border: 1px solid #1E293B;
   border-radius: 8px; box-shadow: var(--elev-1);`.

### Shadow & elevation

- **In slides: forbidden.** `box-shadow` is a PF ERROR (PF-66) — PPTX strips all
  shadows. Use surface tint instead.
- **In editor app:** 5-level M3 elevation tokens (`--elev-1` … `--elev-5`) define
  shadow stacks. Modals lift to `--elev-4`, popovers to `--elev-3`, cards rest
  at `--elev-1`.

### Corner radii (Material 3 shape scale)

| Token | px | Use |
|---|---|---|
| `--r-xs` | 4px | inline tags |
| `--r-sm` | 8px | buttons, slide cards (`8pt`) |
| `--r-md` | 12px | input fields |
| `--r-lg` | 16px | panels, modals |
| `--r-xl` | 24px | hero cards, education-mode everything |
| `--r-full` | 9999px | pills, badges, circle icons |

### Transparency & blur

**Avoid in slides.** `opacity < 1.0` and `mix-blend-mode` both fail PPTX
conversion (PF-42, PF-49). The only sanctioned uses of transparency are:

- `rgba()` inside `text-shadow` (passes through cleanly).
- Decorative `rgba(255,255,255,0.5)` on hero-cover badge borders — accepted because
  it's interpreted as a solid blend during PF preflight.

The editor app may use `backdrop-filter: blur(12px)` freely.

### Iconography

- **Glyph icons in slides**: ASCII arrows `↗ ↘ → ↑ ↓ ←` inside hairline 28pt
  circles, set in Pretendard. Material Symbols are NOT used on slides (font
  conversion risk).
- **Emoji** is permitted as a *feature icon* in Education / Creative modes only
  (🌐 🔍 ✍️ 🖼️ 📄 💬 etc.). Flag emoji is **banned** (PF-12 ERROR).
- **App icons** use a small inline-SVG icon set (chevron, plus, settings, close,
  copy, check, alert) sized to 16px or 20px, stroked 1.5px, currentColor.
- See `ICONOGRAPHY` below for the full register.

### Animation

- **Slides:** no transitions, no animations — `transform: rotate()` is the only
  CSS transform PF-17 allows (and even that is rare).
- **Editor app:** 150ms standard transitions on hover/focus, M3 emphasized
  easings (`--ease-standard`, `--ease-emph-out`) on layout shifts.

### Hover / press states

- **App buttons:** hover lifts opacity/borders by one neutral step; press scales
  to `transform: scale(0.98)`; focus shows `box-shadow: 0 0 0 3px var(--ring)`.
- **App secondary controls:** hover transitions border from `#1B2028` to
  `#2A323B`.
- **Slides:** no hover/press — slides are static.

### Layout rules

- **Slide canvas:** 1280×720px (16:9, = 13.333×7.5", PowerPoint Widescreen 기본).
  v3.1 표준. 양옆 margin 76.8px (0.8"), source line at 676.8px (7.05"). 모든
  슬라이드 마이그레이션 완료 (이전 720×405pt 는 legacy).
- **Grid system:** primarily CSS `grid` with `grid-template-columns`. `<table>`
  is banned (PF-63) — grids only.
- **Density caps:** max 3 independent content blocks per slide (PF-26). Lists
  cap at 5 items, 4-card grids at 4. Beyond → split slides.
- **Aspect-ratio asymmetry:** Editorial / Creative modes prefer 30:70 or
  1:1.618 over 50:50.

### Imagery vibe

- Subject photography (semiconductor fabs, executives, products) is shot **cool
  and editorial** — desaturated, mid-key, neutral grays + steel blues. Not
  warm-stock-photo.
- Avoid stock-photo "smiling people in a meeting" — see PF DESIGN_MODES Creative
  Mode Forbidden list.
- PF-21 mandates `object-fit: cover` (never `contain`, never `fill`).

### PF (Presentation Flow) rules — quick reference

Anything below will fail the preflight validator and break PPTX export. The full
set lives in `pf_rules.md`; here are the load-bearing ones:

| Rule | Constraint |
|---|---|
| PF-01 | No `linear-gradient` under light text |
| PF-05 | Background images only on `<body>` |
| PF-07 | No background/border on `<p>`/`<h*>`/`<li>` — wrap in `<div>` |
| PF-12 | Flag emojis → PNG/SVG `<img>` |
| PF-25 | Hard floor: 24/14/10pt |
| PF-26 | Max 3 independent content blocks per slide |
| PF-28 | ≤120 EN / ≤80 CJK words per slide |
| PF-42 | No `opacity < 1.0` on backgrounds |
| PF-57 | Content image ≥ 25% of slide area (≥260pt × 180pt) |
| PF-63 | No `<table>` — use CSS grid |
| PF-66 | No `box-shadow` (full ERROR) |

---

## ICONOGRAPHY

slides-grab uses **three distinct icon registers**, intentionally separated.

### 1. Slide glyphs — ASCII / Unicode arrows in hairline circles

The signature slide motif. A small (28pt) circle outlined `1px solid #1A1A1A`
with a Unicode arrow (`↗ ↘ → ←`) at 12–14pt, centered. Used as a "more"
affordance on covers, section dividers, and feature cards. **Never replaced by
SVG** — the arrow IS the icon. This is what gives slides-grab its editorial feel.

### 2. App icons — inline SVG, 1.5px stroke, currentColor

In `assets/icons/` we ship a small set extracted from the editor: `chevron`,
`plus`, `settings`, `close`, `copy`, `check`, `alert`, `search`, `drag`, `eye`,
`bolt`, `export`. Geometry mirrors **Lucide** (1.5px stroke, square caps,
rounded joins), so if you need more, pull them from
<https://lucide.dev> — that is a *flagged CDN substitution*: the codebase does
not ship lucide, but Lucide is the closest match in stroke/joint style.

### 3. Feature emoji — slide-only, Creative/Education modes only

Permitted: `🌐 🔍 ✍️ 🖼️ 📄 💬 ⚡ 📊 🎯 🚀 ✅`. Always at 20pt, centered in a
feature card. **Forbidden:** country flags (PF-12), faces, hand gestures, food.

### Logos

There is no formal slides-grab logo. The slides themselves use a placeholder
"LogoName" wordmark next to an 18pt black square containing a `*` glyph. We
keep that placeholder available in `assets/logo-placeholder.svg` for use in
sample slides, and recommend users replace it with their own.

---

## Substitutions flagged for the user

- **JetBrains Mono** is loaded from Google Fonts CDN — the codebase does not
  ship a mono font. If you need mono on slides (you shouldn't — PF prefers
  Pretendard everywhere), confirm the substitution.
- **Lucide icons** are referenced as the design-language match for the editor's
  internal SVG set. We did not bulk-copy Lucide; we copied only the icons that
  appear in `slides-grab/src/editor/`. Pull more from Lucide if needed and the
  visual feel will hold.
- The Figma file is an empty stub (0 frames, 0 components, 0 images). All
  visual fidelity in this design system was sourced from the `slides-grab`
  codebase. **No Figma assets were imported.**

---

## How to use this system

1. Building a **slide deliverable**? Start from `ui_kits/slides/index.html` and
   the templates in `slides/`. Stay PF-compliant; export via `slides-grab convert`.
2. Building a tool / editor / dashboard? Start from `ui_kits/editor/index.html`.
   PF rules do not apply (browser-only).
3. Need just colors and type? `colors_and_type.css` is self-contained — include
   it directly.

---

*Material 3 references — elevation by tint, shape scale, density tokens, dynamic
accents — are interpretive. We do not link the Material 3 component library; we
fold the principles into slides-grab's own visual idiom.*
