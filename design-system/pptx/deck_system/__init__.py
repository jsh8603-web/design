"""FP&A deck system — .pptx engine."""
from deck_system.builder.builder import PresentationBuilder
from deck_system.tokens import MODERN, CLASSIC, DARK_MONO, COMPANY
from deck_system.builder.validation import LAYOUT_SCHEMAS
from deck_system.errors import (
    DeckSystemError, InputValidationError, CJKFontError,
    ThemeError, LayoutOverflowError, ImagePlaceholderError,
)
from deck_system.quick import quick_deck, quick_from_json

__all__ = ["PresentationBuilder", "MODERN", "CLASSIC", "DARK_MONO", "COMPANY",
           "LAYOUT_SCHEMAS",
           "DeckSystemError", "InputValidationError", "CJKFontError",
           "ThemeError", "LayoutOverflowError", "ImagePlaceholderError",
           "quick_deck", "quick_from_json"]
__version__ = "0.3.0"
