"""One-line helpers for common use cases."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Union

from deck_system.builder.builder import PresentationBuilder
from deck_system.tokens import get_theme


def quick_deck(slides: list[dict], output: Union[str, Path],
               theme: str = "modern") -> Path:
    """Build a deck from a list of slide specs in one call.

        quick_deck([{"type": "cover", "title": "x"}, ...], "out.pptx")
    """
    b = PresentationBuilder(theme=get_theme(theme))
    b.add_specs(slides)
    return b.save(output)


def quick_from_json(spec_path: Union[str, Path],
                    output: Union[str, Path],
                    theme: str = "modern") -> Path:
    """Build a deck from a JSON file in one call."""
    with open(spec_path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    if isinstance(spec, dict):
        if "slides" in spec:
            return quick_deck(spec["slides"], output, theme)
        return quick_deck([spec], output, theme)
    return quick_deck(spec, output, theme)
