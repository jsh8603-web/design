"""JSON spec normalizer — accepts HTML system input shapes verbatim.

HTML data files may use either camelCase (older convention) or snake_case
(matched 1:1 with Python).  This module converts any camelCase keys to
snake_case while leaving values (including Korean text) untouched.

Result: the same JSON file drives HTML rendering AND .pptx generation.
"""
from __future__ import annotations
import re
from typing import Any


_CAMEL_RE = re.compile(r"(?<!^)(?=[A-Z])")


def _to_snake(name: str) -> str:
    """fooBarBaz → foo_bar_baz.  Already-snake stays snake."""
    if "_" in name or name.islower():
        return name.lower()
    return _CAMEL_RE.sub("_", name).lower()


def normalize_spec(spec: Any) -> Any:
    """Recursively convert dict keys to snake_case.  Lists / scalars untouched."""
    if isinstance(spec, dict):
        return {_to_snake(k): normalize_spec(v) for k, v in spec.items()}
    if isinstance(spec, list):
        return [normalize_spec(item) for item in spec]
    return spec


# ── Convenience: load from path ────────────────────────────────────────
import json
from pathlib import Path


def load_spec(path: str | Path) -> dict:
    """Read a JSON file and normalize keys.  Convenience for CLI / examples."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return normalize_spec(raw)
