"""QA checks — 9 per-slide + 1 global.  Reads a built Presentation
and returns a QAReport.

Inspired by likaku/qa.py.  Each check returns 0+ findings; a finding
has a level (error/warning/info), a category (whitelist-aware), and a
message.  Findings classified into ENGINE_BUG_WHITELIST are demoted
to 'info' (autofix won't touch them, gate won't fail).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Iterable

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Emu

from .experiences import (
    MAX_ACTION_TITLE_CHARS, MAX_FOUR_COL_DESC_CHARS,
    MAX_PROCESS_CHEVRON_STEPS, MAX_PROCESS_CHEVRON_DESC_CHARS,
    PROCESS_STEP_LABEL_NO_NEWLINE, MAX_DONUT_SEGMENTS,
    MAX_TWO_COLUMN_TEXT_PER_DECK, BOTTOM_BAR_MIN_Y_IN,
    BOTTOM_BAR_MAX_Y_IN, USE_CONNECTORS, EA_FONT_REQUIRED_FOR_KOREAN,
    ENGINE_BUG_WHITELIST, SHAPE_MIN_GAP_IN,
    MAX_DECK_SLIDES, MAX_FONT_FAMILIES_PER_DECK,
)


# ─── Finding / Report ────────────────────────────────────────────────

@dataclass
class Finding:
    slide_idx: int           # 1-based
    check: str               # check name
    category: str            # short category, used for whitelist match
    level: str               # "error" | "warning" | "info"
    message: str

    def to_dict(self) -> dict:
        return {
            "slide": self.slide_idx, "check": self.check,
            "category": self.category, "level": self.level,
            "message": self.message,
        }


@dataclass
class QAReport:
    findings: List[Finding] = field(default_factory=list)
    slides: int = 0

    @property
    def errors(self) -> List[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self) -> List[Finding]:
        return [f for f in self.findings if f.level == "warning"]

    @property
    def infos(self) -> List[Finding]:
        return [f for f in self.findings if f.level == "info"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "slides": self.slides,
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "infos": len(self.infos),
            },
            "findings": [f.to_dict() for f in self.findings],
        }


# ─── Utility: walk text in a slide ───────────────────────────────────

def _iter_text(slide):
    """Yield (shape, paragraph, run) for every text run on a slide."""
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                yield shape, p, r


def _shape_bbox(shape):
    """Return (left, top, right, bottom) in EMU, or None if shape has no geometry."""
    try:
        l, t = shape.left, shape.top
        w, h = shape.width, shape.height
        if l is None or t is None or w is None or h is None:
            return None
        return (l, t, l + w, t + h)
    except Exception:
        return None


# ─── Individual checks ───────────────────────────────────────────────

def _check_action_title(slide, idx, spec=None) -> Iterable[Finding]:
    """Action title length + line count."""
    found = False
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        if shape.top is None:
            continue
        if shape.top.inches > 1.0:   # only the topmost shape qualifies
            continue
        text = shape.text_frame.text
        if not text.strip():
            continue
        # First text shape near the top is the action title
        if not found:
            found = True
            stripped = text.strip()
            if len(stripped) > MAX_ACTION_TITLE_CHARS:
                yield Finding(idx, "action_title", "title_overflow", "warning",
                              f"Action title {len(stripped)} chars > limit {MAX_ACTION_TITLE_CHARS}")
            if "\n" in text or text.count("\r") > 0:
                line_count = text.count("\n") + 1
                if line_count > 2:
                    yield Finding(idx, "action_title", "title_overflow",
                                  "warning",
                                  f"Action title spans {line_count} lines")


def _check_body_overflow(slide, idx, spec=None) -> Iterable[Finding]:
    """Any shape that pushes past the slide right/bottom margin."""
    slide_w_emu = slide.part.package.presentation_part.presentation.slide_width
    slide_h_emu = slide.part.package.presentation_part.presentation.slide_height
    margin = Emu(int(0.05 * 914400))   # 0.05" tolerance
    for shape in slide.shapes:
        bb = _shape_bbox(shape)
        if not bb:
            continue
        l, t, r, b = bb
        if r > slide_w_emu + margin:
            yield Finding(idx, "body_overflow", "geometry", "error",
                          f"Shape '{shape.name}' extends past right edge by "
                          f"{(r - slide_w_emu) / 914400:.2f}in")
        if b > slide_h_emu + margin:
            yield Finding(idx, "body_overflow", "geometry", "error",
                          f"Shape '{shape.name}' extends past bottom edge by "
                          f"{(b - slide_h_emu) / 914400:.2f}in")


def _check_text_overflow(slide, idx, spec=None) -> Iterable[Finding]:
    """Text content per shape vs shape capacity (rough heuristic)."""
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text_frame.text
        if not text:
            continue
        try:
            area_in2 = (shape.width.inches * shape.height.inches)
        except Exception:
            continue
        # Korean: ~3.5 chars per 0.1 in² at 14pt; rough cap
        if area_in2 < 0.5 and len(text) > 80:
            yield Finding(idx, "text_overflow", "geometry", "warning",
                          f"Shape area {area_in2:.2f}in² may not fit {len(text)} chars")


def _check_whitespace(slide, idx, spec=None) -> Iterable[Finding]:
    """Slide dead-zone detection.

    Conceptually parallel to the HTML system's data-rendered guard:
    HTML: prevents un-rendered slide → JS pre-block
    PPTX: catches un-rendered slide → QA post-check
    Both encode 'a slide must not have a blank content area'.
    """
    n_shapes = len(slide.shapes)
    has_text = any(s.has_text_frame and s.text_frame.text.strip()
                   for s in slide.shapes)
    if n_shapes < 2:
        yield Finding(idx, "whitespace", "empty_slide", "error",
                      f"Slide has only {n_shapes} shape(s) — looks empty")
    elif not has_text:
        yield Finding(idx, "whitespace", "empty_slide", "warning",
                      "Slide has shapes but no text content")


def _check_shape_overlap(slide, idx, spec=None) -> Iterable[Finding]:
    """Detect overlapping content shapes (excludes chrome — rules etc)."""
    bboxes = []
    for s in slide.shapes:
        if s.has_text_frame and not s.text_frame.text.strip():
            continue
        bb = _shape_bbox(s)
        if bb:
            bboxes.append((s.name, bb))
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            (na, (la, ta, ra, ba)) = bboxes[i]
            (nb, (lb, tb, rb, bb)) = bboxes[j]
            # Compute overlap area
            ox = max(0, min(ra, rb) - max(la, lb))
            oy = max(0, min(ba, bb) - max(ta, tb))
            if ox > 0 and oy > 0:
                # Filter out trivial overlap (e.g. chrome rules over content)
                aa = (ra - la) * (ba - ta)
                ab = (rb - lb) * (bb - tb)
                if ox * oy < 0.05 * min(aa, ab):
                    continue
                yield Finding(idx, "shape_overlap", "geometry", "info",
                              f"Shapes '{na}' and '{nb}' overlap "
                              f"~{(ox * oy) / 914400 ** 2:.2f}in²")


def _check_fonts(slide, idx, spec=None) -> Iterable[Finding]:
    """Detect Korean text runs without EA font set.

    Pretendard's <a:ea> tag in every CJK-containing run is required;
    set_run() enforces this, but spot-check here for regressions.
    """
    if not EA_FONT_REQUIRED_FOR_KOREAN:
        return
    for shape, p, r in _iter_text(slide):
        if not _has_korean(r.text):
            continue
        rPr = r._r.find("{http://schemas.openxmlformats.org/drawingml/2006/main}rPr")
        if rPr is None:
            yield Finding(idx, "ea_font", "cjk", "error",
                          f"Korean run '{r.text[:20]}…' missing <a:rPr>")
            continue
        ea = rPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}ea")
        if ea is None or not ea.get("typeface"):
            yield Finding(idx, "ea_font", "cjk", "error",
                          f"Korean run '{r.text[:20]}…' missing EA font")


def _has_korean(text: str) -> bool:
    return any("\uac00" <= c <= "\ud7a3" or "\u3131" <= c <= "\u3163"
                for c in (text or ""))


def _check_peer_font_consistency(slide, idx, spec=None) -> Iterable[Finding]:
    """Sibling shapes in a row should share font size."""
    rows = {}
    for s in slide.shapes:
        if not s.has_text_frame or not s.text_frame.text.strip():
            continue
        bb = _shape_bbox(s)
        if not bb: continue
        top_in = bb[1] / 914400
        # Bucket by 0.1" top alignment
        key = round(top_in, 1)
        sizes = set()
        for p in s.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size is not None:
                    sizes.add(r.font.size.pt)
        if sizes:
            rows.setdefault(key, []).append(sizes)
    for top, size_sets in rows.items():
        if len(size_sets) <= 1: continue
        all_sizes = set()
        for ss in size_sets: all_sizes.update(ss)
        if len(all_sizes) > 2:  # more than 2 distinct sizes in a "row" is suspect
            yield Finding(idx, "peer_font",
                          "peer_font_inconsistency", "info",
                          f"Row at y={top}in has {len(all_sizes)} distinct font sizes")


def _check_chart_legend_overflow(slide, idx, spec=None) -> Iterable[Finding]:
    """Detect chart shapes whose legend extends past plot area."""
    for shape in slide.shapes:
        if shape.shape_type != MSO_SHAPE_TYPE.CHART:
            continue
        try:
            chart = shape.chart
            if not chart.has_legend:
                continue
            # Heuristic: count series; >5 = potential overflow
            n_ser = len(list(chart.series))
            if n_ser > 5:
                yield Finding(idx, "chart_legend",
                              "chart_legend_pixel_drift", "info",
                              f"Chart has {n_ser} series — legend may overflow")
        except Exception:
            pass


def _check_connectors(slide, idx, spec=None) -> Iterable[Finding]:
    """Detect add_connector() use — corrupts files via <p:style>."""
    if USE_CONNECTORS:
        return  # disabled
    for shape in slide.shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.LINE:
            yield Finding(idx, "connector", "file_corruption", "error",
                          f"Shape '{shape.name}' is a connector — use add_hline() instead")


def _check_text_line_collision(slide, idx, spec=None) -> Iterable[Finding]:
    """Detect text shapes that overlap horizontal rules."""
    rules = []
    texts = []
    for s in slide.shapes:
        bb = _shape_bbox(s)
        if not bb: continue
        l, t, r, b = bb
        h_in = (b - t) / 914400
        # Horizontal rule: thin (<0.05in) and wide
        if h_in < 0.05 and (r - l) / 914400 > 2:
            rules.append((s.name, bb))
        elif s.has_text_frame and s.text_frame.text.strip():
            texts.append((s.name, bb))
    for tn, (tl, tt, tr_, tb) in texts:
        for rn, (rl, rt, rr_, rb) in rules:
            # Text overlaps rule if any y-range intersects
            if not (tb <= rt or tt >= rb):
                if not (tr_ <= rl or tl >= rr_):
                    yield Finding(idx, "text_line_collision",
                                  "geometry", "warning",
                                  f"Text '{tn}' overlaps rule '{rn}'")


# ─── Global checks ───────────────────────────────────────────────────

def _check_global_two_column_text(prs, slides_by_type) -> Iterable[Finding]:
    """At most 1 two_column_text per deck (HTML guidance)."""
    n = slides_by_type.get("two_column_text", 0)
    if n > MAX_TWO_COLUMN_TEXT_PER_DECK:
        yield Finding(0, "global_two_column_text", "layout_overuse", "warning",
                      f"Deck has {n} two_column_text slides — limit {MAX_TWO_COLUMN_TEXT_PER_DECK}")


def _check_global_slide_count(prs, slides_by_type) -> Iterable[Finding]:
    """Deck slide-count check (V2.1).

    McKinsey guidance: 'one deck, one message'.  >50 slides usually
    means the deck is doing too much — split by topic.
    Source: likaku qa.py _check_global rule set.
    """
    n = len(prs.slides)
    if n > MAX_DECK_SLIDES:
        yield Finding(0, "global_slide_count", "deck_too_long", "warning",
                      f"Deck has {n} slides (max recommended: {MAX_DECK_SLIDES}). "
                      f"Consider splitting into multiple decks by topic.")


def _check_global_font_consistency(prs, slides_by_type) -> Iterable[Finding]:
    """Deck-wide font consistency (V2.1).

    More than ~3 font families across a deck usually signals a paste-in
    of foreign content or an inconsistent build.  Allowed: Pretendard +
    1-2 supplementary fonts (e.g. mono for code snippets).
    Source: likaku qa.py _check_global rule set.
    """
    fonts_used = set()
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.name:
                        fonts_used.add(run.font.name)
    if len(fonts_used) > MAX_FONT_FAMILIES_PER_DECK:
        yield Finding(0, "global_font_consistency", "deck_font_inconsistency",
                      "warning",
                      f"Deck uses {len(fonts_used)} font families: "
                      f"{sorted(fonts_used)}. "
                      f"Reduce to Pretendard + max "
                      f"{MAX_FONT_FAMILIES_PER_DECK - 1} supplementary fonts.")


# ─── Runner ──────────────────────────────────────────────────────────

_PER_SLIDE_CHECKS = [
    _check_action_title,
    _check_body_overflow,
    _check_text_overflow,
    _check_whitespace,
    _check_shape_overlap,
    _check_fonts,
    _check_peer_font_consistency,
    _check_chart_legend_overflow,
    _check_connectors,
    _check_text_line_collision,
]


def run_qa(prs: Presentation, *, slide_specs: Optional[List[dict]] = None) -> QAReport:
    """Run all checks on a built Presentation, return QAReport."""
    rep = QAReport(slides=len(prs.slides))
    slide_specs = slide_specs or []

    slides_by_type = {}
    for i, slide in enumerate(prs.slides, start=1):
        spec = slide_specs[i - 1] if i - 1 < len(slide_specs) else None
        if spec and "type" in spec:
            slides_by_type[spec["type"]] = slides_by_type.get(spec["type"], 0) + 1
        for check in _PER_SLIDE_CHECKS:
            try:
                for finding in check(slide, i, spec):
                    rep.findings.append(_apply_whitelist(finding))
            except Exception as e:
                # Never let a buggy check abort the whole QA pass
                rep.findings.append(Finding(
                    i, check.__name__, "check_internal", "info",
                    f"Check {check.__name__} raised {type(e).__name__}: {e}",
                ))

    # Global checks
    for finding in _check_global_two_column_text(prs, slides_by_type):
        rep.findings.append(_apply_whitelist(finding))
    for finding in _check_global_slide_count(prs, slides_by_type):
        rep.findings.append(_apply_whitelist(finding))
    for finding in _check_global_font_consistency(prs, slides_by_type):
        rep.findings.append(_apply_whitelist(finding))

    return rep


def _apply_whitelist(f: Finding) -> Finding:
    """Demote whitelisted categories to info level."""
    if f.category in ENGINE_BUG_WHITELIST and f.level in ("error", "warning"):
        return Finding(f.slide_idx, f.check, f.category, "info",
                       f"[whitelisted] {f.message}")
    return f
