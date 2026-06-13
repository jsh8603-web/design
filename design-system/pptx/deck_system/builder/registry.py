"""Slide-type → layout function registry.

Layouts register themselves via `@register("name")` at import time;
Builder.add() looks up by string name.  This keeps the dispatch flat —
no giant if/elif chain — and lets new layouts drop in without touching
the builder.
"""
from __future__ import annotations
from typing import Callable, Dict

_REGISTRY: Dict[str, Callable] = {}


def register(name: str) -> Callable:
    """Decorator: register a layout function under `name`.

        @register("waterfall")
        def render_waterfall(slide, spec, theme, *, page_num, total): ...
    """
    def deco(fn: Callable) -> Callable:
        if name in _REGISTRY:
            raise ValueError(f"Layout already registered: {name}")
        _REGISTRY[name] = fn
        return fn
    return deco


def get(name: str) -> Callable:
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown layout: {name}.  Registered: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[name]


def all_names() -> list[str]:
    return sorted(_REGISTRY)
