"""Master adapter — profile a .pptx into design tokens.

Inspired by tristan-mcinnis/pptx-from-layouts-skill.
"""
from .profile import profile_master, write_profile_json
from .theme_from_profile import generate_theme_from_profile

__all__ = ["profile_master", "write_profile_json", "generate_theme_from_profile"]
