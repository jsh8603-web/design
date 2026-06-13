"""Hard-won production constants from likaku/experiences/*.md.

Centralized so QA + autofix + builder pre-validation all reference one truth.
Don't edit values without updating the upstream HTML system too.

References:
  likaku/experiences/overflow.md         — 6 cases
  likaku/experiences/chart-limits.md     — 2 cases
  likaku/experiences/layout-pitfalls.md  — 5 cases
  likaku/experiences/cjk-issues.md       — 2 cases
"""
from __future__ import annotations

# ─── OVERFLOW ────────────────────────────────────────────────────────
# experiences/overflow.md: action-title is the single most overflow-prone
# element; chevron labels with newlines push outside the shape; etc.
MAX_ACTION_TITLE_CHARS = 40
MAX_FOUR_COL_DESC_CHARS = 120
MAX_PROCESS_CHEVRON_STEPS = 5
MAX_PROCESS_CHEVRON_DESC_CHARS = 50
PROCESS_STEP_LABEL_NO_NEWLINE = True   # chevron labels MUST be single-line
MAX_TIMELINE_LAST_LABEL_CHARS = 6
MAX_BIG_NUMBER_DETAIL_ITEMS = 4
MAX_KPI_TILES = 8
MAX_TWO_STAT_LABEL_CHARS = 30
MAX_THREE_STAT_LABEL_CHARS = 25

# ─── CHART LIMITS ────────────────────────────────────────────────────
# experiences/chart-limits.md: BLOCK_ARC + python-pptx can't render >6
# segments without label overlap; grouped bar series=3 is the legend
# legibility threshold.
MAX_DONUT_SEGMENTS = 6
MAX_PIE_SEGMENTS = 6
MAX_GROUPED_BAR_CATEGORIES = 6
MAX_GROUPED_BAR_SERIES = 3
MAX_PARETO_BARS = 10
MAX_RAG_ROWS = 10
MAX_HARVEY_BALL_OPTIONS = 4
MAX_VARIANCE_TABLE_ROWS = 10

# ─── LAYOUT PITFALLS ─────────────────────────────────────────────────
# experiences/layout-pitfalls.md: connectors via add_connector() corrupt
# files; primary direct refs collapse in dark mode; two_column_text is the
# least-impact slide type and should be rationed.
MAX_TWO_COLUMN_TEXT_PER_DECK = 1
CONTENT_START_AFTER_ACTION_TITLE_IN = 1.3
BOTTOM_BAR_MIN_Y_IN = 6.1
BOTTOM_BAR_MAX_Y_IN = 6.4
USE_CONNECTORS = False                  # always False — use add_hline()
ALLOW_PRIMARY_FOR_FULL_BLEED = False    # always False — use surface_inverse
SHAPE_MIN_GAP_IN = 0.05                 # min gap between non-overlapping shapes

# ─── CJK ─────────────────────────────────────────────────────────────
# experiences/cjk-issues.md: every run with Korean MUST have <a:ea> set;
# Korean lines need 1.4× height vs Latin 1.2×.
EA_FONT_REQUIRED_FOR_KOREAN = True
CJK_LINE_HEIGHT_RATIO = 1.4
LATIN_LINE_HEIGHT_RATIO = 1.2

# ─── ENGINE BUG WHITELIST ────────────────────────────────────────────
# Errors classified as engine quirks, not user bugs.  Whitelist them so
# autofix doesn't try to "fix" them and gate doesn't fail.
ENGINE_BUG_WHITELIST = [
    "peer_font_inconsistency",   # legend vs axis font size diffs by 0.5pt
    "chart_legend_pixel_drift",  # python-pptx rounds legend bbox to nearest pt
    "block_arc_label_anchor",    # BLOCK_ARC center label off by 0.02"
]

# ─── ROUNDS ──────────────────────────────────────────────────────────
DEFAULT_AUTOFIX_MAX_ROUNDS = 3

# ─── DECK-WIDE LIMITS (V2.1 — global checks) ─────────────────────────
# Source: likaku qa.py _check_global rule set.
# Beyond 50 slides → McK guidance "one deck, one message" → split.
MAX_DECK_SLIDES = 50
# Pretendard + at most 1-2 supplementary fonts (e.g. mono code).
MAX_FONT_FAMILIES_PER_DECK = 3
