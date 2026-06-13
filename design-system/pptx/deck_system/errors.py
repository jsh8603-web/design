"""deck_system friendly error classes — V2.3-B.

All errors inherit from DeckSystemError. Each carries structured fields
(layout_name, expected, got, fix, example) so the user can see what's
wrong, how to fix it, and a working example in 5 seconds.

Five categories:
    InputValidationError  — wrong/missing input field
    CJKFontError          — Korean/CJK rendering issue
    ThemeError            — theme lookup / token resolution failed
    LayoutOverflowError   — input violates experiences.py constants
    ImagePlaceholderError — image_placeholder helper failed
"""
from __future__ import annotations
import json
from typing import Any, Optional


class DeckSystemError(Exception):
    """Base for all deck_system errors.

    Initialize with keyword fields only; positional args are ignored
    so existing `raise DeckSystemError("msg")` calls still work via
    the `message` kwarg.
    """

    def __init__(
        self,
        *args,
        layout_name: Optional[str] = None,
        slide_num: Optional[int] = None,
        message: Optional[str] = None,
        expected: Optional[str] = None,
        got: Optional[str] = None,
        fix: Optional[str] = None,
        example: Optional[Any] = None,
        **context,
    ):
        if args and message is None:
            message = str(args[0])
        self.layout_name = layout_name
        self.slide_num = slide_num
        self.message = message
        self.expected = expected
        self.got = got
        self.fix = fix
        self.example = example
        self.context = context
        super().__init__(self._format())

    def _format(self) -> str:
        parts = []
        head = ""
        if self.layout_name:
            head += f"[{self.layout_name}]"
        if self.slide_num is not None:
            head += f" slide {self.slide_num}"
        if head:
            parts.append(head.strip())
        if self.message:
            parts.append(self.message)
        ctx = []
        for k, v in (self.context or {}).items():
            ctx.append(f"  {k}: {v}")
        if ctx:
            parts.append("Context:\n" + "\n".join(ctx))
        if self.expected:
            parts.append(f"Expected: {self.expected}")
        if self.got:
            parts.append(f"Got: {self.got}")
        if self.fix:
            parts.append(f"Fix: {self.fix}")
        if self.example is not None:
            try:
                ex_str = json.dumps(self.example, ensure_ascii=False, indent=2)
            except (TypeError, ValueError):
                ex_str = repr(self.example)
            # Truncate long examples
            if len(ex_str) > 400:
                ex_str = ex_str[:400] + "\n  …"
            parts.append("Example:\n" + ex_str)
        return "\n".join(parts)


class InputValidationError(DeckSystemError):
    """A required field is missing, has wrong type, or violates bounds."""


class CJKFontError(DeckSystemError):
    """East Asian font (Pretendard) could not be applied to a run."""


class ThemeError(DeckSystemError):
    """Theme lookup or token resolution failed."""


class LayoutOverflowError(DeckSystemError):
    """Input violates an experiences.py constant (chart/text limits)."""


class ImagePlaceholderError(DeckSystemError):
    """The image_placeholder helper could not render its rectangle."""
