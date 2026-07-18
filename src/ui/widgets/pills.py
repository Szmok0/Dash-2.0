"""Kolorowe etykiety (pill) priorytetu i statusu oraz klikalne statusy karty."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton

from ui.styles.theme import Palette


# Wspólne wymiary kontrolek statusu (jednolity kształt w rzędzie karty klienta)
STATUS_PILL_HEIGHT = 50
STATUS_PILL_MIN_WIDTH = 98


def _pill_qss(color: str) -> str:
    return (
        f"QPushButton {{ background: {with_alpha(color, 0.12)}; color: {color};"
        f"border: 1px solid {with_alpha(color, 0.33)};"
        "border-radius: 10px; padding: 6px 14px; font-size: 12px; font-weight: 600;"
        "text-align: center; }"
        f"QPushButton:hover {{ background: {with_alpha(color, 0.19)}; }}"
    )


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
        self.setFixedHeight(STATUS_PILL_HEIGHT)
        self.setMinimumWidth(STATUS_PILL_MIN_WIDTH)
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
        self.setStyleSheet(_pill_qss(color))


class MenuPill(QPushButton):
    """Status wielostanowy w kształcie pill (jak QuickStatusPill), z rozwijanym menu wyboru.

    Wygląda identycznie jak pozostałe statusy (2 linie, ta sama wysokość), a klik
    otwiera listę do wyboru — dla CV (brak / do poprawy / aktualne).
    """

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
        self._labels = labels
        self._value = current
        self._colors = colors
        self._palette = palette
        self._on_change = on_change
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{title} — kliknij, aby wybrać")
        self.setFixedHeight(STATUS_PILL_HEIGHT)
        self.setMinimumWidth(STATUS_PILL_MIN_WIDTH)
        self.clicked.connect(self._open_menu)
        self._refresh()

    def _open_menu(self) -> None:
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        for v in self._values:
            menu.addAction(self._labels.get(v, v), lambda val=v: self._select(val))
        menu.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def _select(self, value: str) -> None:
        self._value = value
        self._on_change(value)
        self._refresh()

    def _refresh(self) -> None:
        color = self._colors.get(self._value, self._palette.text_muted)
        label = self._labels.get(self._value, self._value)
        self.setText(f"{self._title}  ▾\n{label}")
        self.setStyleSheet(_pill_qss(color))


class YesNoFlag(QPushButton):
    """Dwustanowy przełącznik ma/nie ma — 2 linie, zielony (ma) / czerwony (nie ma)."""

    def __init__(self, title: str, has: bool, on_toggle: Callable[[bool], None], palette: Palette) -> None:
        super().__init__()
        self._title = title
        self._has = has
        self._palette = palette
        self._on_toggle = on_toggle
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{title}: kliknij, aby przełączyć „ma / nie ma”")
        self.setFixedHeight(STATUS_PILL_HEIGHT)
        self.setMinimumWidth(STATUS_PILL_MIN_WIDTH)
        self.clicked.connect(self._flip)
        self._refresh()

    def _flip(self) -> None:
        self._has = not self._has
        self._on_toggle(self._has)
        self._refresh()

    def _refresh(self) -> None:
        # „ma" = kolor pozytywny, „nie ma" = szary (spokojna, dwubarwna paleta)
        color = self._palette.green if self._has else self._palette.text_muted
        self.setText(f"{self._title}\n{'Ma' if self._has else 'Nie ma'}")
        self.setStyleSheet(_pill_qss(color))
