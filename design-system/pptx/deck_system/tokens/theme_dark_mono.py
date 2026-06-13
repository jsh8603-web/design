"""Dark-mono theme — near-black surface, cold blue accent.

CRITICAL: in this theme, `primary` (#0F1419) equals `bg` (#0F1419).
Layouts that need a full-bleed dark surface (cover, section_divider,
dark_navy_summary, closing) MUST reference `palette.surface_inverse`
(#1F2937 — a slightly-lighter panel tone) instead of `primary`.

HTML parity: matches `[data-theme="dark-mono"]` in colors_and_type.css.
"""
from .base import Theme, Palette

_PALETTE = Palette(
    primary="#0F1419",
    accent="#4A9EFF",
    positive="#34D399",
    negative="#F87171",
    # gray scale REVERSED for dark — gray_1 = lightest on dark
    gray_1="#E5E7EB",
    gray_2="#9CA3AF",
    gray_3="#4B5563",
    gray_4="#1F2937",
    white="#FFFFFF",
    black="#000000",
    # surface_inverse diverges from primary in dark mode — uses gray_4
    surface_inverse="#1F2937",
    surface_inverse_fg="#E5E7EB",
)

DARK_MONO = Theme(palette=_PALETTE)
