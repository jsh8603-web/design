"""Generate a Theme module from a profile dict.

Output: a Python file matching the format of theme_modern.py etc, so the
generated module plugs into the existing tokens system.  Special care:
surface_inverse is derived from the master's accent1 (light themes) or
gray_4 (dark themes detected by lt1/bg1 luminance).
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional


def _luminance(hex_color: str) -> float:
    """Approximate perceived luminance 0..1."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return 1.0
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _is_dark_theme(profile: dict) -> bool:
    bg = profile.get("color_scheme", {}).get("bg1", "#FFFFFF")
    return _luminance(bg) < 0.5


def generate_theme_from_profile(
    profile: dict,
    output_path: "str | Path",
    *,
    theme_var_name: str = "COMPANY",
) -> Path:
    """Write a theme module that exposes `<theme_var_name>: Theme`.

    The shape mirrors deck_system/tokens/theme_modern.py.
    """
    cs = profile.get("color_scheme", {})
    fs = profile.get("font_scheme", {})

    dark = _is_dark_theme(profile)
    primary = cs.get("accent1", "#1A2332")
    accent = cs.get("accent2", "#E87722")
    positive = cs.get("accent3", "#2E844A")
    negative = cs.get("accent4", "#C5394A")
    gray_1 = cs.get("tx1", "#2C2C2C")
    gray_2 = cs.get("accent5", "#666666")
    gray_3 = cs.get("accent6", "#B0B0B0")
    gray_4 = cs.get("bg2", "#F0F0F0")
    white = cs.get("bg1", "#FFFFFF")
    black = "#000000"

    # surface_inverse divergence: in dark themes, point at gray_4 so the
    # full-bleed slides remain visible.  In light themes, equals primary.
    if dark:
        surface_inverse = gray_4
        surface_inverse_fg = gray_1
    else:
        surface_inverse = primary
        surface_inverse_fg = white

    major_font = fs.get("major", "Pretendard")
    minor_font = fs.get("minor", "Pretendard")

    src = f'''# Auto-generated from {profile.get("source", "<unknown>")}
# By deck_system.adapter — DO NOT EDIT MANUALLY.
#
# To regenerate:
#     python -m deck_system.adapter.profile path/to/master.pptx \\
#         --output-dir deck_system/tokens/ --name {theme_var_name.lower()}
from deck_system.tokens.base import Theme, Palette, Typography

_PALETTE = Palette(
    primary="{primary}",
    accent="{accent}",
    positive="{positive}",
    negative="{negative}",
    gray_1="{gray_1}",
    gray_2="{gray_2}",
    gray_3="{gray_3}",
    gray_4="{gray_4}",
    white="{white}",
    black="{black}",
    surface_inverse="{surface_inverse}",
    surface_inverse_fg="{surface_inverse_fg}",
)

_TYPOGRAPHY = Typography(
    family_kr="{major_font}",
    family_en="{minor_font}",
    family_ea="{major_font}",
)

{theme_var_name} = Theme(palette=_PALETTE, typography=_TYPOGRAPHY,
                         copyright_text="© Auto-generated from {Path(profile.get("source", "")).name}")
'''
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(src)
    return out
