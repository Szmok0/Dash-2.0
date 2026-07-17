"""Kolorowe etykiety (pill) priorytetu i statusu oraz klikalne statusy karty."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton

from ui.styles.theme import Palette


def priority_color(p: Palette, priority: str) -> str:
    return {"wysoki": p.red, "sredni": p.yellow, "niski": p.green}.get(priority, p.text_muted)


def task_status_color(p: Palette, status: str) -> str:
    return {
        "do_zrobienia": p.accent,
        "w_trakcie": p.purple,
        "zakonczone": p.text_muted,
        "oczekuje_na": p.yellow,
        "anulowane": p.text_muted,
    }.get(status, p.text_muted)


def with_alpha(color: str, alpha: float) -> str:
    """Hex #RRGGBB -> rgba(r,g,b,a) zrozumiałe dla QSS."""
    color = color.lstrip("#")
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{int(alpha * 255)})"


def make_pill(text: str, color: str) -> QLabel:
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet(
        f"background: {with_alpha(color, 0.15)}; color: {color};"
        f"border: 1px solid {with_alpha(color, 0.33)};"
        "border-radius: 9px; padding: 2px 10px; font-size: 11px; font-weight: 600;"
    )
    return label


class QuickStatusPill(QPushButton):
    """Status szybkiego podglądu na karcie klienta — zmiana jednym kliknięciem."""

    def __init__(
        self,
        title: str,
        values: list[str],
        labels: dict[str, str],
        current: str,
        color_for: Callable[[str], str],
        on_change: Callable[[str], None],
    ) -> None:
        super().__init__()
        self._title = title
        self._values = values
        self._labels = labels
        self._value = current
        self._color_for = color_for
        self._on_change = on_change
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Kliknij, aby zmienić status")
        self.clicked.connect(self._cycle)
        self._refresh()

    def _cycle(self) -> None:
        idx = self._values.index(self._value)
        self._value = self._values[(idx + 1) % len(self._values)]
        self._on_change(self._value)
        self._refresh()

    def _refresh(self) -> None:
        color = self._color_for(self._value)
        label = self._labels.get(self._value, self._value)
        self.setText(f"{self._title}\n{label}")
        self.setStyleSheet(
            f"QPushButton {{ background: {with_alpha(color, 0.12)}; color: {color};"
            f"border: 1px solid {with_alpha(color, 0.33)};"
            "border-radius: 10px; padding: 8px 14px; font-size: 12px; font-weight: 600;"
            "text-align: center; }"
            f"QPushButton:hover {{ background: {with_alpha(color, 0.19)}; }}"
        )


class StatusDropdown(QComboBox):
    """Status z listą wyboru (np. CV: brak / do poprawy / aktualne), kolorowany wg wartości."""

    def __init__(
        self,
        title: str,
        values: list[str],
        labels: dict[str, str],
        current: str,
        colors: dict[str, str],
        on_change: Callable[[str], None],
        palette: Palette,
    ) -> None:
        super().__init__()
        self._title = title
        self._values = values
        self._colors = colors
        self._palette = palette
        self._on_change = on_change
        for v in values:
            self.addItem(labels.get(v, v), v)
        idx = self.findData(current)
        if idx >= 0:
            self.setCurrentIndex(idx)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{title} — wybierz status")
        self.currentIndexChanged.connect(self._changed)
        self._restyle()

    def _changed(self) -> None:
        self._restyle()
        self._on_change(self.currentData())

    def _restyle(self) -> None:
        color = self._colors.get(self.currentData(), self._palette.text_muted)
        self.setStyleSheet(
            f"QComboBox {{ background: {with_alpha(color, 0.14)}; color: {color};"
            f"border: 1px solid {with_alpha(color, 0.4)}; border-radius: 10px;"
            "padding: 7px 12px; font-size: 12px; font-weight: 600; min-width: 128px; }"
            "QComboBox::drop-down { border: none; width: 22px; }"
            f"QComboBox QAbstractItemView {{ background: {self._palette.card};"
            f"color: {self._palette.text}; selection-background-color: {self._palette.selection}; }}"
        )


class YesNoFlag(QPushButton):
    """Dwustanowy przełącznik ma/nie ma — zielony (ma) / czerwony (nie ma)."""

    def __init__(self, title: str, has: bool, on_toggle: Callable[[bool], None], palette: Palette) -> None:
        super().__init__()
        self._title = title
        self._has = has
        self._palette = palette
        self._on_toggle = on_toggle
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{title}: kliknij, aby przełączyć „ma / nie ma”")
        self.clicked.connect(self._flip)
        self._refresh()

    def _flip(self) -> None:
        self._has = not self._has
        self._on_toggle(self._has)
        self._refresh()

    def _refresh(self) -> None:
        color = self._palette.green if self._has else self._palette.red
        self.setText(self._title)
        self.setStyleSheet(
            f"QPushButton {{ background: {with_alpha(color, 0.16)}; color: {color};"
            f"border: 1px solid {with_alpha(color, 0.45)}; border-radius: 9px;"
            "padding: 6px 14px; font-size: 12px; font-weight: 700; }"
            f"QPushButton:hover {{ background: {with_alpha(color, 0.26)}; }}"
        )
