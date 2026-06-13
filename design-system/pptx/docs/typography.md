# Typography Rules — Tier Classification v2

Adopted 2026-05-29. Replaces the implicit "pick the closest size" pattern
with explicit **semantics × density** decision rules.

## Core principle

1. **Content semantics is the primary tier decider** — "I want it to look smaller
   for design balance" is NOT a valid reason to downgrade a tier.
2. **Card/column density is the secondary decider** — a 4-column dense card's
   body can drop one tier (body → body_compact) vs a 3-column layout.
3. **Hierarchy uses size + weight + color + layout together** — never carry
   hierarchy on size alone.

## Tier mapping

| Tier | pt | px @ 1.333 | Token | When |
|------|----|-----------:|-------|------|
| action | 22 | 29.33 | `--fs-action` | Slide-level conclusion title (one per slide) |
| sub_header | 18 | 24 | `--fs-subheader` | Card heading, section title |
| body | 17 | 22.67 | `--fs-body` | Body sentences, paragraphs — **slide default** |
| **body_compact** ⭐ | **16** | **21.33** | `--fs-body-compact` | Card body in 3+ column dense grids |
| small | 15 | 20 | `--fs-small` | Captions, short meta, card sub-labels |
| chart_label | 10 | 13.33 | `--fs-chart` | Mono labels, chart axes, category tags |
| footer | 9 | 12 | `--fs-foot` | Source attribution, page number ONLY |

⭐ = **NEW in v0.3.3** — fills the small↔chart_label gap.

## The 5pt gap (resolved)

Before v0.3.3 there was a 5pt jump between `small` (15pt) and
`chart_label` (10pt). Real content kept falling into the gap:
- 3-4 column card body items ("서울대·연세대 평생교육원")
- Card-internal answer/result panels ("총 32개 기관 식별…")
- Card body where `small` looks cramped but `chart_label` is illegible

`body_compact` (16pt) sits between `body` and `small`. Semantically it's
**body content** — the only reason to use it is **container density**.

## Author self-check (before downsizing)

Answer these BEFORE going below `body`:

- [ ] Is this a sentence, item list, or description? → `body` or `body_compact` (16pt+)
- [ ] Is this inside a card and the card is narrow (3+ cols)? → `body_compact` allowed
- [ ] Is this metadata or a caption? → `small` (15pt)
- [ ] Is this an eyebrow, category label, mono uppercase tag? → `chart_label` (10pt)
- [ ] Is this source / page number? → `footer` (9pt) — NO other body content
      may use footer tier
- [ ] If the honest answer is "I want it to look smaller for design" → **REJECT**.
      Retreat via weight (600 → 400) or color (gray_1 → gray_2) instead.

## Forbidden patterns

- ❌ **Arbitrary px values** — system tokens only. Need a missing size? Add a new tier.
- ❌ **Body content at chart_label or footer tier** — examples, descriptions,
  questions are NEVER < 12pt.
- ❌ **Size demotion as hierarchy retreat** — alternatives: `weight 600 → 400`,
  `color gray_1 → gray_2`, indent/divider.

## Recommended patterns

- ✅ Use `var(--fs-*)` tokens only.
- ✅ Hierarchy via weight + color — same size can express retreat.
- ✅ Body minimum = 16pt (`body_compact`). Slide bodies never drop below this line.
- ✅ Card body tier depends on card width — 600px+: `body`, 400–600px: `body_compact`,
  <400px: `small`.

## Author workflow

1. Write the content.
2. Classify each text block's **semantic tier**.
3. Evaluate container density (card width, column count).
4. Apply the token.
5. If visual retreat is still needed, adjust **weight/color** — size demotion
   is the last resort.
