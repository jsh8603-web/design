# Slides UI Kit

The slide deliverable system — the warm executive editorial look slides-grab
ships by default. `index.html` is the kit overview: hero, template gallery,
theme strip, voice/PF guidance.

## Components in scope

All templates referenced here live in **`/slides/`** at the project root —
they were copied verbatim from `slides-grab/templates/*.html` and are still
the source of truth.

| Template | File |
|---|---|
| Cover | `slides/cover.html` |
| Section divider | `slides/section-divider.html` |
| Contents (TOC) | `slides/contents.html` |
| Two-column content | `slides/content.html` |
| Split image + text | `slides/split-layout.html` |
| KPI statistics | `slides/statistics.html` |
| Horizontal timeline | `slides/timeline.html` |
| 4-up team grid | `slides/team.html` |
| Centered quote | `slides/quote.html` |
| Closing / thank you | `slides/closing.html` |

## Themes

| Theme | File | Vibe |
|---|---|---|
| Executive | `themes/executive.css` | Warm white `#F5F5F0` · dark ink · the default |
| Corporate | `themes/corporate.css` | Pure white · navy text · blue accent |
| Modern Dark | `themes/modern-dark.css` | Pure black · white accent |
| Sage | `themes/sage.css` | Mossy green `#B8C4B8` canvas |
| Warm | `themes/warm.css` | Cream `#FAF8F5` · terracotta accent |

## Cardinal rules (see `pf_rules.md` for the full set)

- 720pt × 405pt canvas; min 10pt text
- Action titles, not topic labels
- 1 slide = 1 message; max 3 content blocks
- White-on-warm card surfaces — no `box-shadow` (PF-66)
- CSS grid only — no `<table>` (PF-63)
