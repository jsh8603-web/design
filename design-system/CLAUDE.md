# CLAUDE.md — slides-grab Design System

This repository **is a design system** (an Agent Skill). When you work in this repo,
you are a designer who has internalized its rules. Do not invent new colors, themes,
or layouts — use the ones defined here.

## What this is

An agent-first design system for **slides-grab**: PPTX/PDF-safe HTML slide decks
(constrained by **PF rules**) plus the slides-grab **editor app** (browser-only,
dark slate). 8 themes · 48-layout catalog · FP&A domain invariants · QA pipeline.

## Read these in order before building (the Skill)

The canonical entry point is **`SKILL.md`**. It lists the read order:

1. `README.md` — system overview, two surfaces (slides vs editor app)
2. `theme_layout_matrix.md` ⭐ — theme × layout lock matrix (prevents mixing)
3. `prompting_rules.md` ⭐ — agent behavior contract (action titles, type scale, color tokens, CJK)
4. `layout_catalog.md` — LayoutSchema for all 48 layouts (required/optional/bounds)
5. `domain/fpna_invariants.md` — cost_nature, surface_inverse, EA font invariants
6. `pf_rules.md` — PPTX-safe HTML constraints (PF-XX ruleset)
7. `qa_rules.md` — 9 per-slide checks + autofix rules
8. `image_slot_contract.md` — image-slot markup contract (사내: AI 생성 대신 수동/사내DB 이미지 배치용)
9. ~~`nano_banana_guide.md`~~ — **사내 미사용** (Gemini 이미지 생성 의존, `_archive-company-blocked/` 분리). 이미지는 차트/표/도형 우선.
10. `pipeline_handoff.md` — cloud ↔ local responsibility split + sync
11. `colors_and_type.css` — foundation tokens

## Mandatory slide-build order (prompting_rules.md §0)

1. Pick theme → `<html data-theme="modern|classic|dark-mono|company|executive-editorial|dark-pitch|academic|editorial">`
2. Pick layout from `layout_catalog.md` (no free invention)
3. Verify (theme, layout) ✅ in `theme_layout_matrix.md`
4. Obey LayoutSchema required fields + bounds
5. Apply domain invariants
6. Obey PF rules
7. Self-check against `qa_rules.md`

## Cardinal rules (never violate)

- Slide titles are **noun-ending assertions** ("Q3 매출, 전년 대비 +23%"), never topic labels
- 1 slide = 1 message; max 3 content blocks; ≤120 EN / ≤80 CJK words
- Numbers are the visual: hero them at 48pt+, weight 800
- 10pt is the absolute floor for any slide text
- No `<table>` — use CSS grid
- Slides: solid hex only; gradient/shadow live only in the editor app
- Full-bleed uses `var(--surface-inverse)`, not `var(--primary)`
- `<html data-theme>` + `<section data-layout>` are mandatory (PF-70 / PF-71)

## Surfaces

- **Slide deliverable** (PPTX-bound): 1280×720, PF-compliant, Pretendard, warm canvas. Start from `ui_kits/slides/` + `slides/` + `mck/slides/` references.
- **Editor app** (browser-only, PF-exempt): dark slate, blue accent, M3 elevation, JetBrains Mono. Start from `ui_kits/editor/`.

## Generated files — do not hand-edit

`_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json` are compiler output.
