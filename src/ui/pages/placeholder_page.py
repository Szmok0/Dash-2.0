"""Strony-zaślepki dla widoków realizowanych w kolejnych sprintach."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ui.styles.theme import Palette


class PlaceholderPage(QWidget):
    def __init__(self, palette: Palette, title: str, sprint_info: str) -> None:
        super().__init__()
        self._palette = palette

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)

        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title_lbl)

        self._info = QLabel(sprint_info)
        self._info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._info)

        root.addWidget(panel, 1)
        self.set_palette(palette)

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self._info.setStyleSheet(f"color: {palette.text_muted}; font-size: 14px; padding-top: 8px;")
