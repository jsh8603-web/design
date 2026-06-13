"""Modern theme — slate navy + warm orange.  Default for FP&A quarterly review.

HTML parity: matches `[data-theme="modern"]` in colors_and_type.css.
"""
from .base import Theme, Palette

_PALETTE = Palette(
    primary="#1A2332",         # slate navy
    accent="#E87722",          # warm orange
    positive="#2E844A",
    negative="#C5394A",
    gray_1="#2C2C2C",
    gray_2="#666666",
    gray_3="#B0B0B0",
    gray_4="#F0F0F0",
    white="#FFFFFF",
    black="#000000",
    surface_inverse="#1A2332",      # = primary in light theme
    surface_inverse_fg="#FFFFFF",
)

MODERN = Theme(palette=_PALETTE)
