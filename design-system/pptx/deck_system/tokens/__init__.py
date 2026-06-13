"""Design tokens — synchronized with HTML system v2.2."""
from .base import Palette, Typography, Layout, Theme
from .theme_modern import MODERN
from .theme_classic import CLASSIC
from .theme_dark_mono import DARK_MONO
from .theme_company import COMPANY

THEMES = {
    "modern": MODERN,
    "classic": CLASSIC,
    "dark_mono": DARK_MONO,
    "dark-mono": DARK_MONO,  # HTML uses kebab-case in data-theme
    "company": COMPANY,
}

def get_theme(name: str) -> Theme:
    """Lookup by name (accepts kebab-case from HTML data-theme attr)."""
    key = name.replace("-", "_").lower()
    if key not in THEMES:
        raise ValueError(f"Unknown theme: {name}. Options: {list(THEMES)}")
    return THEMES[key]

__all__ = ["Palette", "Typography", "Layout", "Theme",
           "MODERN", "CLASSIC", "DARK_MONO", "COMPANY",
           "THEMES", "get_theme"]
