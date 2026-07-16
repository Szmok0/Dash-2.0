"""Sidebar nawigacyjny — pozycje tekstowe, zwijany do wąskiej listwy z ikonami."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from config import SIDEBAR_COLLAPSED_WIDTH, SIDEBAR_WIDTH
from ui.styles.theme import Palette
from ui.widgets.icons import make_icon

NAV_ITEMS = [
    ("dashboard", "Dashboard"),
    ("klienci", "Klienci"),
    ("kalendarz", "Kalendarz"),
    ("analityka", "Analityka"),
    ("import", "Import"),
    ("ustawienia", "Ustawienia"),
]


class Sidebar(QFrame):
    def __init__(self, palette: Palette, on_navigate: Callable[[str], None]) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self._palette = palette
        self._on_navigate = on_navigate
        self._collapsed = False
        self._active = "dashboard"
        self._buttons: dict[str, QPushButton] = {}

        self.setFixedWidth(SIDEBAR_WIDTH)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)

        self._logo = QLabel("Client\nWorkbench")
        self._logo.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {palette.text}; padding: 4px 14px 16px 14px;"
        )
        layout.addWidget(self._logo)

        for key, label in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("NavItem")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, k=key: self._on_navigate(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch(1)

        self._toggle = QPushButton("‹ Zwiń menu")
        self._toggle.setObjectName("NavItem")
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle.clicked.connect(self.toggle_collapsed)
        layout.addWidget(self._toggle)

        self.set_active("dashboard")

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self._logo.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {palette.text}; padding: 4px 14px 16px 14px;"
        )
        self._apply_collapsed_state()

    def set_active(self, key: str) -> None:
        self._active = key
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def toggle_collapsed(self) -> None:
        self.set_collapsed(not self._collapsed)

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        self._apply_collapsed_state()

    def _apply_collapsed_state(self) -> None:
        if self._collapsed:
            self.setFixedWidth(SIDEBAR_COLLAPSED_WIDTH)
            self._logo.setText("CW")
            self._logo.setStyleSheet(
                f"font-size: 15px; font-weight: 700; color: {self._palette.text};"
                "padding: 4px 0 16px 0;"
            )
            self._logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._toggle.setText("›")
            self._toggle.setToolTip("Rozwiń menu")
            for key, label in NAV_ITEMS:
                btn = self._buttons[key]
                btn.setText("")
                btn.setIcon(make_icon(key, self._palette.text_muted, 20))
                btn.setToolTip(label)
        else:
            self.setFixedWidth(SIDEBAR_WIDTH)
            self._logo.setText("Client\nWorkbench")
            self._logo.setStyleSheet(
                f"font-size: 17px; font-weight: 700; color: {self._palette.text};"
                "padding: 4px 14px 16px 14px;"
            )
            self._logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self._toggle.setText("‹ Zwiń menu")
            self._toggle.setToolTip("")
            for key, label in NAV_ITEMS:
                btn = self._buttons[key]
                btn.setText(label)
                btn.setIcon(QIcon())
                btn.setToolTip("")
