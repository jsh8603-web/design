"""Classic theme — deep McKinsey navy + cyan accent.  Board/executive register.

HTML parity: matches `[data-theme="classic"]` in colors_and_type.css.
"""
from .base import Theme, Palette

_PALETTE = Palette(
    primary="#051C2C",         # deep McK navy
    accent="#00A3E0",          # cyan
    positive="#2E844A",
    negative="#C5394A",
    gray_1="#2C2C2C",
    gray_2="#666666",
    gray_3="#B0B0B0",
    gray_4="#F0F0F0",
    white="#FFFFFF",
    black="#000000",
    surface_inverse="#051C2C",
    surface_inverse_fg="#FFFFFF",
)

CLASSIC = Theme(palette=_PALETTE)
