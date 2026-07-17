"""Rejestracja czcionki Unicode dla PDF (polskie znaki)."""
from __future__ import annotations

from pathlib import Path

from config import resource_path

_FONTS_DIR = resource_path("resources", "fonts")
_registered = False

FONT_NAME = "CWSans"
FONT_BOLD = "CWSans-Bold"


def register_pdf_fonts() -> str:
    """Rejestruje DejaVuSans (regular + bold) w reportlab. Zwraca nazwę czcionki.

    Jeśli plików czcionek brak, wraca do Helvetiki (bez polskich znaków).
    """
    global _registered
    if _registered:
        return FONT_NAME

    regular = _FONTS_DIR / "DejaVuSans.ttf"
    bold = _FONTS_DIR / "DejaVuSans-Bold.ttf"
    if not regular.exists():
        return "Helvetica"

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont(FONT_NAME, str(regular)))
    if bold.exists():
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
    else:
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(regular)))
    pdfmetrics.registerFontFamily(FONT_NAME, normal=FONT_NAME, bold=FONT_BOLD)
    _registered = True
    return FONT_NAME
