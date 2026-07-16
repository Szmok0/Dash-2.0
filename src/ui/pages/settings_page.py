"""Ustawienia (Sprint 0: przełącznik motywu dark/light)."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.styles.theme import Palette


class SettingsPage(QWidget):
    def __init__(self, palette: Palette, on_toggle_theme: Callable[[], None]) -> None:
        super().__init__()
        self._palette = palette

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("Wygląd")
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        layout.addWidget(title)

        row = QHBoxLayout()
        self._desc = QLabel("Motyw interfejsu (dark to projekt bazowy, light to opcja).")
        row.addWidget(self._desc)
        row.addStretch(1)
        self._toggle_btn = QPushButton("Przełącz dark / light")
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.clicked.connect(on_toggle_theme)
        row.addWidget(self._toggle_btn)
        layout.addLayout(row)

        self._note = QLabel(
            "PIN, blokada po bezczynności i backup pojawią się w kolejnych sprintach (BUILD.md)."
        )
        layout.addWidget(self._note)

        root.addWidget(panel)
        self.set_palette(palette)

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self._desc.setStyleSheet(f"color: {palette.text};")
        self._note.setStyleSheet(f"color: {palette.text_muted}; font-size: 12px;")
