"""PresentationBuilder — the public Python API.

    from deck_system import PresentationBuilder, MODERN

    b = PresentationBuilder(theme=MODERN)
    b.add("cover", title="Q4 review", subtitle="FY26")
    b.add("waterfall", title="OP bridge",
          items=[...], unit="억")
    b.save("output/q4.pptx")

`b.add()` accepts a layout name + kwargs (Python style).
`b.add_spec(spec)` accepts a dict and infers the type.
`b.add_specs([spec, …])` for bulk runs from JSON.

QA integration (v0.3 / Track 2):
- `b.run_qa()` returns a QAReport on the currently buffered specs
- `b.run_autofix()` applies safe text-level repairs in-place
- `b.save(path, qa_report_path=..., auto_fix=True)` does both inline
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Union, List

from pptx import Presentation
from pptx.util import Inches

from deck_system.tokens import Theme, MODERN
from deck_system.builder.registry import get as get_layout
from deck_system.builder.inference import infer_slide_type
from deck_system.builder.spec_normalizer import normalize_spec
from deck_system.builder.tone import warn_if_violations
from deck_system.builder.validation import validate_layout_input

# Force layout-module imports so @register decorators fire
from deck_system import layouts as _layouts  # noqa: F401


class PresentationBuilder:
    def __init__(
        self,
        theme: Theme = MODERN,
        *,
        default_section_marker: str = "",
        total_slides_hint: Optional[int] = None,
    ):
        self.theme = theme
        self.section_marker = default_section_marker
        self._slides_buffer: list[tuple[str, dict]] = []
        self._total_hint = total_slides_hint

    # ── add() — keyword-style ──────────────────────────────────────────
    def add(self, layout_name: str, **kwargs) -> "PresentationBuilder":
        """Add a slide by layout name + keyword arguments.

            b.add("cover", title="...", subtitle="...")

        V2.3-B: validation raises InputValidationError (friendly fields).
        """
        import sys
        from deck_system.errors import InputValidationError
        try:
            kwargs, warnings = validate_layout_input(layout_name, kwargs)
            for w in warnings:
                print(f"[WARN slide {len(self._slides_buffer)+1}] {w}",
                      file=sys.stderr)
        except InputValidationError as e:
            # Attach slide number and re-raise
            e.slide_num = len(self._slides_buffer) + 1
            raise
        self._slides_buffer.append((layout_name, kwargs))
        return self

    # ── add_spec() — dict-style with auto-inference ────────────────────
    def add_spec(self, spec: dict) -> "PresentationBuilder":
        """Add a slide from a dict spec.  Auto-detects layout name."""
        spec = normalize_spec(spec)
        layout_name = spec.pop("type", None) or infer_slide_type(spec)
        return self.add(layout_name, **spec)

    def add_specs(self, specs: list[dict]) -> "PresentationBuilder":
        for s in specs:
            self.add_spec(s)
        return self

    # ── QA / Autofix (Track 2) ────────────────────────────────────────
    def _spec_list_for_qa(self) -> List[dict]:
        """Reconstruct dict specs from the internal buffer."""
        return [{"type": name, **kwargs}
                for name, kwargs in self._slides_buffer]

    def run_qa(self) -> "QAReport":
        """Build presentation, then run all checks. Returns a QAReport."""
        from deck_system.qa import run_qa
        prs = self.build()
        specs = self._spec_list_for_qa()
        return run_qa(prs, slide_specs=specs)

    def run_autofix(self, *, max_rounds: int = 3) -> "AutofixResult":
        """Apply autofix repairs to buffered specs IN PLACE.

        Mutates self._slides_buffer and returns the action log.
        Layout names are preserved; only kwargs (titles, segment lists,
        steps, KPIs etc.) are repaired.
        """
        from deck_system.qa import run_autofix, run_qa
        # Pull spec dicts out, mutate them, push back into buffer
        specs = [dict(kwargs, type=name)
                 for name, kwargs in self._slides_buffer]

        def builder_factory(slide_specs):
            b = PresentationBuilder(theme=self.theme)
            for s in slide_specs:
                s2 = dict(s)
                t = s2.pop("type")
                b.add(t, **s2)
            return b.build()

        result = run_autofix(specs, qa_runner=run_qa,
                             builder_factory=builder_factory,
                             max_rounds=max_rounds)

        # Sync mutated specs back into buffer
        new_buffer = []
        for spec in specs:
            spec = dict(spec)
            t = spec.pop("type")
            new_buffer.append((t, spec))
        self._slides_buffer = new_buffer
        return result

    # ── render + save ─────────────────────────────────────────────────
    def build(self) -> Presentation:
        prs = Presentation()
        prs.slide_width = Inches(self.theme.layout.slide_width_in)
        prs.slide_height = Inches(self.theme.layout.slide_height_in)

        total = self._total_hint or len(self._slides_buffer)

        for idx, (name, kwargs) in enumerate(self._slides_buffer, start=1):
            # Blank layout — we draw everything ourselves
            slide_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(slide_layout)

            # Action title tone check
            if "title" in kwargs and isinstance(kwargs["title"], str):
                warn_if_violations(kwargs["title"])

            render_fn = get_layout(name)
            render_fn(slide, kwargs, self.theme,
                      page_num=idx, total=total)

        return prs

    def save(
        self,
        path: Union[str, Path],
        *,
        qa_report_path: Optional[Union[str, Path]] = None,
        auto_fix: bool = False,
        auto_fix_max_rounds: int = 3,
    ) -> Path:
        """Build + save.

        Optional extras:
            auto_fix=True             — run autofix BEFORE building
            qa_report_path=<path>     — write JSON QA report after building
        """
        if auto_fix:
            self.run_autofix(max_rounds=auto_fix_max_rounds)

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        prs = self.build()
        prs.save(str(path))

        if qa_report_path is not None:
            from deck_system.qa import run_qa
            specs = self._spec_list_for_qa()
            report = run_qa(prs, slide_specs=specs)
            qrp = Path(qa_report_path)
            qrp.parent.mkdir(parents=True, exist_ok=True)
            with open(qrp, "w", encoding="utf-8") as fh:
                json.dump(report.to_dict(), fh, ensure_ascii=False, indent=2)

        return path

