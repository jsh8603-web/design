# Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `InputValidationError: Missing required field` | Required field omitted | Read the `Example:` block in the error message; add the field. |
| `InputValidationError: wrong type` | e.g. passed a string where a list is expected | See `Expected:` line in error; rewrite as that type. |
| Korean text renders as Gulim/SimSun in PowerPoint | EA font not applied | Confirm `set_run()` is being used (it auto-applies `set_ea_font`). Direct `font.name=` calls bypass this — never use them. |
| Cover slide appears black in PowerPoint w/ `dark_mono` | A layout used `palette.primary` for full-bleed, which collapses to `bg` in dark mode | Replace with `palette.surface_inverse`. `palette.primary` for backgrounds is forbidden in `structure.py` and `summary.py`. |
| File corruption / "PowerPoint found a problem with content" | `add_connector()` left `<p:style>` references | Use `helpers/shapes.add_hline()` instead. Every shape goes through `_clean_shape()`. |
| Variance row shows GREEN despite positive variance on cost | `cost_nature: true` not set | Add `"cost_nature": true` to cost rows (매출원가, 판관비, 물류비, etc.). |
| `ValueError: Unknown theme: …` | Theme name not recognized | Use `modern` / `classic` / `dark_mono` / `company`. Hyphens accepted (`dark-mono`). |
| `KeyError: unknown layout: …` | Typo in slide type | Run `python -m deck_system.cli list-layouts` for the registry. |
| Build is slow | Many slides + chart-heavy | Expected: 14 slides ≈ 1s, 70 slides ≈ 4-5s. Set `--auto-fix` only when needed. |
| pytest fails on `test_robustness.py` | `LAYOUT_SCHEMAS` missing entry | Run `python -m deck_system.cli list-layouts | wc -l` — count must match `len(LAYOUT_SCHEMAS)`. |
| Image placeholder shows wrong color in `dark_mono` | Hardcoded fill | `helpers/image_placeholder.py` uses `gray_3` + `surface_inverse_fg` — both theme-safe. |
