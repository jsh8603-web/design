# LOCAL_SETUP.md — running this design system locally (Claude Code / Codex)

This repo is an **agent-first design system**. Locally it gives you two runnable
pipelines plus the full rule/skill set. This page is the one-stop "make it work
the same as the hosted environment" guide.

> TL;DR — the rules, tokens, fonts, and HTML references work anywhere. The two
> *runnable* pipelines below need a one-time setup each:
>
> | Pipeline | Setup | Run |
> |---|---|---|
> | HTML slide preview (ES-module slides) | none | `python serve.py --open` |
> | PPTX generation (Python `deck_system`) | `cd pptx && pip install -e .` | `python -m deck_system.cli build …` |

---

## 0. What runs locally vs. what is hosted-only

| Capability | Local? | Notes |
|---|---|---|
| Read the Skill & build slides by the rules | ✅ identical | `SKILL.md` is a portable Agent Skill — point Claude Code at it |
| All tokens / 8 themes / fonts | ✅ identical | `styles.css` → `colors_and_type.css` + fonts |
| HTML slide references (mck, aesthetics, ui_kits) | ✅ via `serve.py` | ES modules need a server, not `file://` |
| PPTX generation (70 layouts, QA, autofix) | ✅ via `pip install -e .` | only dependency is `python-pptx` |
| Live preview pane / screenshot / **Design System tab** | ❌ hosted-only | locally you just open pages in a browser |
| Auto-rebuild of `_ds_bundle.js` / `_ds_manifest.json` / `_adherence.oxlintrc.json` | ❌ hosted-only | the shipped snapshots are fine to use as-is; don't hand-edit |

Nothing about **making slides** is hosted-only. The hosted-only items are
authoring conveniences for editing the design system itself.

---

## 1. Preview the HTML slides

Native ES modules + local `@font-face` mean browsers block `file://`. Use the
bundled static server (standard library, no install):

```bash
python serve.py --open          # opens the deck index automatically
python serve.py --port 9000     # pick a port
```

Then visit any reference:

- `http://localhost:8000/mck/slides/index.html` — 17-slide reference deck, 8-theme toggle
- `http://localhost:8000/aesthetics/index.html` — 4 aesthetic directions
- `http://localhost:8000/ui_kits/editor/index.html` — the editor app shell
- `http://localhost:8000/preview/integration-overview.html` — design-system cards

When **you** author a new deck, follow the mandatory order in
`prompting_rules.md` §0 (theme → layout → matrix → schema → invariants → PF → QA)
and load the foundation with one line:

```html
<link rel="stylesheet" href="/styles.css">
<html data-theme="modern">   <!-- one of the 8 themes -->
```

## 2. Generate PPTX

```bash
cd pptx
pip install -e .                # installs python-pptx + the `fpna-deck` CLI

# JSON spec → .pptx
python -m deck_system.cli init my_deck/
python -m deck_system.cli build my_deck/deck.json -o my_deck/out.pptx
python -m deck_system.cli build my_deck/deck.json -o my_deck/dark.pptx --theme dark_mono

# inspect the catalog
python -m deck_system.cli list-layouts
python -m deck_system.cli show-schema waterfall
python -m deck_system.cli themes
```

Or from Python:

```python
from deck_system import quick_deck
quick_deck(
    [
        {"type": "cover", "title": "Q4 review"},
        {"type": "variance_table", "title": "예산 대비",
         "items": [{"label": "매출", "budget": 1200, "actual": 1260}],
         "unit_default": "억"},
        {"type": "closing", "title": "Thanks"},
    ],
    "out.pptx", theme="modern",
)
```

Full CLI + FP&A specifics (cost_nature sign-flip, waterfall, surface_inverse) are
in `pptx/README.md`.

## 3. Point Claude Code at the Skill

From a local clone, tell Claude Code to read `SKILL.md` first — it lists the
canonical read order (`README.md` → `theme_layout_matrix.md` → `prompting_rules.md`
→ `layout_catalog.md` → domain invariants → `pf_rules.md` → `qa_rules.md` → …).
`CLAUDE.md` is loaded automatically as project instructions and enforces the same
cardinal rules used in the hosted environment.

## 4. Generated files

`_ds_bundle.js`, `_ds_manifest.json`, and `_adherence.oxlintrc.json` are compiler
output from the hosted environment. The shipped snapshots are valid — use them
as-is. **Do not hand-edit them** (per `CLAUDE.md`); they only regenerate in the
hosted environment.

---

## Requirements

- **HTML preview:** Python 3.9+ (standard library only).
- **PPTX:** Python 3.9+ and `python-pptx` (installed by `pip install -e .`).
  Optional `Pillow` only if you push real raster images through the
  image-placeholder helpers: `pip install -e ".[images]"`.
