"""Górny pasek: tytuł, wyszukiwarka ID/nazwisko, liczniki, przycisk + Dodaj."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton

from config import HEADER_HEIGHT, SEARCH_HEIGHT, SEARCH_WIDTH
from ui.styles.theme import Palette


class Header(QFrame):
    def __init__(
        self,
        palette: Palette,
        on_search: Callable[[str], None],
        on_add: Callable[[], None],
        on_search_submit: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("Header")
        self.setFixedHeight(HEADER_HEIGHT)
        self._palette = palette

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        self._title = QLabel("Dashboard")
        self._title.setStyleSheet("font-size: 20px; font-weight: 700;")
        layout.addWidget(self._title)

        layout.addStretch(1)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Szukaj: ID lub nazwisko…  (Ctrl+K, Enter → Klienci)")
        self._search.setFixedSize(SEARCH_WIDTH, SEARCH_HEIGHT)
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(on_search)
        if on_search_submit is not None:
            self._search.returnPressed.connect(lambda: on_search_submit(self._search.text()))
        layout.addWidget(self._search)

        self._active_label = QLabel()
        self._meetings_label = QLabel()
        for lbl in (self._active_label, self._meetings_label):
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._active_label)
        layout.addWidget(self._meetings_label)

        self._add_btn = QPushButton("+ Dodaj")
        self._add_btn.setObjectName("Primary")
        self._add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_btn.clicked.connect(on_add)
        layout.addWidget(self._add_btn)

        self.set_palette(palette)

    @property
    def add_button(self) -> QPushButton:
        return self._add_btn

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        badge = (
            f"background: {palette.card}; border: 1px solid {palette.line};"
            "border-radius: 8px; padding: 7px 12px; font-size: 12px;"
            f"color: {palette.text_muted};"
        )
        self._active_label.setStyleSheet(badge)
        self._meetings_label.setStyleSheet(badge)

    def set_title(self, title: str) -> None:
        self._title.setText(title)

    def set_counters(self, active_clients: int, meetings_info: str) -> None:
        self._active_label.setText(
            f"Aktywni klienci: <b style='color:{self._palette.text}'>{active_clients}</b>"
        )
        self._meetings_label.setText(f"Dzisiejsze spotkania: {meetings_info}")

    def search_text(self) -> str:
        return self._search.text()

    def focus_search(self) -> None:
        self._search.setFocus()
        self._search.selectAll()
