# Master adapter (`deck_system/adapter/`)

Read an existing in-house `.pptx` master, extract design tokens, emit a
theme module that plugs into the `[data-theme="company"]` slot.

Inspired by [tristan-mcinnis/pptx-from-layouts-skill](
https://github.com/tristan-mcinnis/pptx-from-layouts-skill)'s `profile.py`.

## Two modules

### `profile.py` — extract tokens

```python
from deck_system.adapter import profile_master, write_profile_json

profile = profile_master("/path/to/company_master.pptx")
# profile = {
#   "source": "...",
#   "color_scheme": {"bg1": "#FFFFFF", "tx1": "#000000",
#                    "accent1": "#003B71", ..., "accent6": "..."},
#   "font_scheme": {"major": "Arial", "minor": "Arial"},
#   "slide_master_dims": {"width_in": 13.333, "height_in": 7.5},
#   "n_slides": 14, "n_masters": 1,
# }

write_profile_json(profile, "deck_system/tokens/_company_profile.json")
```

### `theme_from_profile.py` — emit `theme_company.py`

```python
from deck_system.adapter import generate_theme_from_profile

generate_theme_from_profile(
    profile,
    "deck_system/tokens/theme_company.py",
    theme_var_name="COMPANY",
)
```

Output (auto-generated, do not hand-edit):

```python
# Auto-generated from /path/to/company_master.pptx
# By deck_system.adapter — DO NOT EDIT MANUALLY.
from deck_system.tokens.base import Theme, Palette, Typography

_PALETTE = Palette(
    primary="#003B71",
    accent="#F2A900",
    positive="#2E844A",
    ...
    surface_inverse="#003B71",     # = primary on light masters
    surface_inverse_fg="#FFFFFF",
)
COMPANY = Theme(...)
```

## `surface_inverse` mapping

Light masters: `surface_inverse = accent1` (the master's primary brand color)
Dark masters: `surface_inverse = bg2` (a slightly-lighter panel tone)

Detection: `_is_dark_theme(profile)` uses luminance(bg1) < 0.5.

This preserves the same invariant the HTML system enforces — full-bleed
slides stay visible regardless of theme polarity.

## CLI

```bash
python -m deck_system.adapter.profile \
    /path/to/company_master.pptx \
    --output-dir deck_system/tokens/ \
    --name company

# Then use the theme:
python -m deck_system.cli \
    --spec examples/q4_review_spec.json \
    -o output/q4_company.pptx \
    --theme company
```

## What gets profiled

| Field | OOXML source | Fallback if missing |
|-------|--------------|---------------------|
| `bg1`, `tx1` | `<a:lt1>`, `<a:dk1>` | white / black |
| `bg2`, `tx2` | `<a:lt2>`, `<a:dk2>` | gray_4 / gray_1 |
| `accent1..6` | `<a:accent1..6>` | modern palette values |
| `font_scheme.major` | `<a:majorFont><a:latin>` | "Pretendard" |
| `font_scheme.minor` | `<a:minorFont><a:latin>` | "Pretendard" |
| `slide_master_dims` | `<p:sldSz>` | 13.333 × 7.5 |

## What's NOT profiled (limitations)

- Slide-layout-specific accents (only theme-level colors)
- Image background graphics (logos, watermarks)
- Custom font substitutions
- Per-master typography overrides

For full master adoption (including layout placeholders), use the upstream
tristan-mcinnis approach to copy master/layouts directly — this adapter
extracts tokens only.
