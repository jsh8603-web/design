# Newsreader TTF (PPTX rendering)

The design system ships brand fonts as **woff2** (`../files/`) for the browser/HTML
surface. PowerPoint/PPTX cannot use woff2 — it matches fonts by their **internal
family name** against system-installed TTF/OTF.

Two gotchas this directory fixes for the Newsreader serif (editorial / dark-pitch hero):

1. The shipped Newsreader woff2 has internal family name **"Newsreader 16pt 16pt"**,
   not "Newsreader". The browser `@font-face { font-family:'Newsreader' }` renames it,
   so HTML is fine — but PowerPoint sees the raw internal name and **fails to match**
   `typeface="Newsreader"`, falling back to a sans substitute (and, during substitution
   wrap, PowerPoint can duplicate a word — the "shape … shape" artifact).
2. PowerPoint (Windows COM) does **not** honor raw-TTF-embedded fonts (`.fntdata`),
   so embedding alone is insufficient on Windows. The font must be **installed**.

These TTFs are regenerated from `../files/Newsreader-*.woff2` (fontTools) with the
name table corrected to family **"Newsreader"** (RIBBI: Regular/Bold/Italic).

## Install (per-user, no admin) on a PPTX-render machine
Right-click each `.ttf` → "Install", or programmatically via the shell "Install" verb.
After install, PowerPoint COM renders the Newsreader serif and the wrap artifact is gone.

Pretendard (the default slide body font) is assumed already installed system-wide.
