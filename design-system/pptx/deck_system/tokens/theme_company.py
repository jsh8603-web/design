"""Company slot — v3 master-adapter target.  Currently falls back to modern.

When the in-house .pptx master is wired in (Session B), this module will
import a generated palette from `deck_system/tokens/_company_generated.py`.
"""
from .base import Theme, Palette

# Fallback = modern values until the adapter populates this slot
_PALETTE = Palette(
    primary="#1A2332",
    accent="#E87722",
    positive="#2E844A",
    negative="#C5394A",
    gray_1="#2C2C2C",
    gray_2="#666666",
    gray_3="#B0B0B0",
    gray_4="#F0F0F0",
    white="#FFFFFF",
    black="#000000",
    surface_inverse="#1A2332",
    surface_inverse_fg="#FFFFFF",
)

COMPANY = Theme(palette=_PALETTE, copyright_text="© Company FY26")
