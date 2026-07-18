"""Motywy kolorystyczne (dark bazowy, light opcjonalny) i arkusz QSS."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    bg: str
    sidebar: str
    panel: str
    card: str
    line: str
    text: str
    text_muted: str
    accent: str
    red: str
    yellow: str
    green: str
    purple: str
    hover: str
    selection: str


DARK = Palette(
    bg="#171C26",
    sidebar="#121722",
    panel="#1D2330",
    card="#202737",
    line="#2B3245",
    text="#F2F4F7",
    text_muted="#A4ACB8",
    accent="#4C8DFF",
    red="#E85D68",
    yellow="#E8B44C",
    green="#4FBF78",
    purple="#8B7CF6",
    hover="#262E40",
    selection="#2A3650",
)

LIGHT = Palette(
    bg="#F3F5F8",
    sidebar="#E8EBF0",
    panel="#FFFFFF",
    card="#FFFFFF",
    line="#D6DAE3",
    text="#1B2430",
    text_muted="#5D6674",
    accent="#2F6FE0",
    red="#C93A46",
    yellow="#B07E1E",
    green="#2E8B57",
    purple="#6C5CE7",
    hover="#E3E8F0",
    selection="#D7E3FA",
)

# Motyw dla daltonistów — kolory semantyczne z palety Okabe–Ito,
# rozróżnialne przy najczęstszych typach daltonizmu (deuteran/protan/tritan).
# Neutralne tła jak w trybie ciemnym; „pozytywne" niebiesko-zielone, „ostrzeżenia" pomarańcz.
COLORBLIND = Palette(
    bg="#171C26",
    sidebar="#121722",
    panel="#1D2330",
    card="#202737",
    line="#2B3245",
    text="#F2F4F7",
    text_muted="#A4ACB8",
    accent="#56B4E9",   # sky blue — aktywny/neutralny
    red="#D55E00",      # vermillion — ostrzeżenie/negatyw znaczący
    yellow="#F0E442",   # jasny żółty — do poprawy/oczekuje
    green="#009E73",    # bluish green — pozytyw
    purple="#CC79A7",   # reddish purple — w trakcie
    hover="#262E40",
    selection="#2A3650",
)

THEMES: dict[str, Palette] = {"dark": DARK, "light": LIGHT, "cb": COLORBLIND}
THEME_LABELS = {"dark": "Ciemny", "light": "Jasny", "cb": "Daltonizm (kolory bezpieczne)"}


def build_qss(p: Palette) -> str:
    return f"""
    QWidget {{
        background: {p.bg};
        color: {p.text};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 13px;
    }}
    QLabel {{ background: transparent; }}
    QFrame#Sidebar {{ background: {p.sidebar}; border-right: 1px solid {p.line}; }}
    QFrame#Header {{ background: {p.panel}; border-bottom: 1px solid {p.line}; }}
    QFrame#Panel {{ background: {p.panel}; border: 1px solid {p.line}; border-radius: 10px; }}
    QFrame#Card {{ background: {p.card}; border: 1px solid {p.line}; border-radius: 10px; }}

    QPushButton {{
        background: {p.card};
        border: 1px solid {p.line};
        border-radius: 8px;
        padding: 7px 14px;
        font-size: 13px;
    }}
    QPushButton:hover {{ background: {p.hover}; }}
    QPushButton#Primary {{
        background: {p.accent};
        border: none;
        color: #FFFFFF;
        font-weight: 600;
    }}
    QPushButton#Primary:hover {{ background: {p.accent}; opacity: 0.9; }}
    QPushButton#NavItem {{
        background: transparent;
        border: none;
        border-radius: 8px;
        text-align: left;
        padding: 9px 14px;
        font-size: 14px;
        color: {p.text_muted};
    }}
    QPushButton#NavItem:hover {{ background: {p.hover}; color: {p.text}; }}
    QPushButton#NavItem[active="true"] {{
        background: {p.card};
        color: {p.text};
        font-weight: 600;
    }}
    QPushButton#Ghost {{
        background: transparent;
        border: none;
        color: {p.accent};
        padding: 4px 8px;
        font-weight: 600;
    }}
    QPushButton#Ghost:hover {{ background: {p.hover}; border-radius: 6px; }}
    QPushButton#Danger {{ color: {p.red}; }}

    QLineEdit, QComboBox, QDateEdit, QDateTimeEdit, QTextEdit, QPlainTextEdit {{
        background: {p.card};
        border: 1px solid {p.line};
        border-radius: 8px;
        padding: 7px 10px;
        selection-background-color: {p.selection};
    }}
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus,
    QDateEdit:focus, QDateTimeEdit:focus {{ border: 1px solid {p.accent}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background: {p.card};
        border: 1px solid {p.line};
        selection-background-color: {p.selection};
    }}

    QTableWidget {{
        background: {p.card};
        border: none;
        gridline-color: transparent;
        font-size: 13px;
    }}
    QTableWidget::item {{ border-bottom: 1px solid {p.line}; padding: 0 8px; }}
    QTableWidget::item:selected {{ background: {p.selection}; color: {p.text}; }}
    QHeaderView::section {{
        background: {p.card};
        color: {p.text_muted};
        border: none;
        border-bottom: 1px solid {p.line};
        padding: 0 8px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }}
    QTableCornerButton::section {{ background: {p.card}; border: none; }}

    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {p.line}; border-radius: 5px; min-height: 24px; }}
    QScrollBar::handle:vertical:hover {{ background: {p.text_muted}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
    QScrollBar::handle:horizontal {{ background: {p.line}; border-radius: 5px; min-width: 24px; }}

    QDialog {{ background: {p.panel}; }}
    QMenu {{ background: {p.card}; border: 1px solid {p.line}; border-radius: 8px; padding: 4px; }}
    QMenu::item {{ padding: 7px 20px; border-radius: 6px; }}
    QMenu::item:selected {{ background: {p.selection}; }}
    QCheckBox {{ background: transparent; spacing: 6px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 1px solid {p.line};
        border-radius: 4px;
        background: {p.card};
    }}
    QCheckBox::indicator:checked {{ background: {p.accent}; border-color: {p.accent}; }}
    QToolTip {{ background: {p.card}; color: {p.text}; border: 1px solid {p.line}; }}
    """
