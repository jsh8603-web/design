# Editor UI Kit

A fidelity recreation of the slides-grab visual editor — the in-browser app that
agents and humans use to bbox-select, direct-edit, and agent-rewrite slides.

## Surfaces in this kit

- `index.html` — the full editor app shell. Three-pane layout (slide list /
  stage / right sidebar) with nav bar and status bar. The bbox tool is
  partially interactive (drag on the slide to add a red box).

## Sources

Recreated from `slides-grab/src/editor/editor.html` (1848 lines). Component
styles, color tokens, and layout pulled verbatim from that file.

## Visual rules in play

- Background ramp `#030711` → `#0A0F1A` → `#0F172A` (panel)
- Border `#1E293B`, border-soft `#172033`
- Text `#F8FAFC` / `#94A3B8` / `#64748B`
- Accent `#3B82F6`, with a 3px focus ring at 18% alpha
- Pill-shaped controls (`border-radius: 999px`) for buttons; 10px radii for inputs
- Pretendard for everything; mono only inside `.kbd` and counter
- Real M3 shadows allowed (this is browser-only — PF rules don't apply)
