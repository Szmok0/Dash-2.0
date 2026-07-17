"""Ekrany PIN: ustawianie, weryfikacja (odblokowanie), zmiana."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.security import SecurityService
from ui.styles.theme import Palette, build_qss


class _PinField(QLineEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setMaxLength(4)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(46)
        self.setInputMask("9999")
        self.setStyleSheet("font-size: 26px; letter-spacing: 12px;")


class PinDialog(QDialog):
    """Tryby: 'set' (ustaw), 'verify' (odblokuj), 'change' (zmień)."""

    def __init__(
        self,
        parent: Optional[QWidget],
        security: SecurityService,
        palette: Palette,
        mode: str = "verify",
    ) -> None:
        super().__init__(parent)
        self._security = security
        self._palette = palette
        self._mode = mode
        self.setModal(True)
        self.setFixedWidth(360)
        self.setWindowTitle("Client Workbench")
        self.setStyleSheet(build_qss(palette))
        # ekran blokady: bez ramki, na wierzchu
        if mode == "verify":
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        titles = {
            "set": "Ustaw PIN (4 cyfry)",
            "verify": "Wprowadź PIN",
            "change": "Zmień PIN",
        }
        title = QLabel(titles.get(mode, "PIN"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        self._current: Optional[_PinField] = None
        if mode == "change":
            layout.addWidget(self._caption("Obecny PIN"))
            self._current = _PinField()
            layout.addWidget(self._current)

        layout.addWidget(self._caption("PIN" if mode == "verify" else "Nowy PIN"))
        self._pin = _PinField()
        layout.addWidget(self._pin)

        self._confirm_field: Optional[_PinField] = None
        if mode in ("set", "change"):
            layout.addWidget(self._caption("Powtórz PIN"))
            self._confirm_field = _PinField()
            layout.addWidget(self._confirm_field)

        self._error = QLabel("")
        self._error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error.setStyleSheet(f"color: {palette.red}; font-size: 12px;")
        self._error.setVisible(False)
        layout.addWidget(self._error)

        self._ok = QPushButton("Odblokuj" if mode == "verify" else "Zapisz")
        self._ok.setObjectName("Primary")
        self._ok.setCursor(Qt.CursorShape.PointingHandCursor)
        self._ok.clicked.connect(self._submit)
        layout.addWidget(self._ok)

        if mode != "verify":
            cancel = QPushButton("Anuluj")
            cancel.clicked.connect(self.reject)
            layout.addWidget(cancel)

        self._pin.returnPressed.connect(self._submit)
        if self._confirm_field:
            self._confirm_field.returnPressed.connect(self._submit)

    def _caption(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {self._palette.text_muted}; font-size: 11px; text-transform: uppercase;")
        return lbl

    def _fail(self, message: str) -> None:
        self._error.setText(message)
        self._error.setVisible(True)

    def _submit(self) -> None:
        pin = self._pin.text()
        if not (pin.isdigit() and len(pin) == 4):
            self._fail("PIN musi mieć 4 cyfry.")
            return

        if self._mode == "verify":
            if self._security.verify_pin(pin):
                self.accept()
            else:
                self._pin.clear()
                self._fail("Nieprawidłowy PIN.")
            return

        if self._mode == "change":
            assert self._current is not None
            if not self._security.verify_pin(self._current.text()):
                self._fail("Obecny PIN jest nieprawidłowy.")
                return

        if self._confirm_field is not None and pin != self._confirm_field.text():
            self._fail("PIN-y nie są zgodne.")
            return

        self._security.set_pin(pin)
        self.accept()

    # ekran blokady nie może być zamknięty Esc/krzyżykiem
    def reject(self) -> None:  # noqa: D401
        if self._mode == "verify":
            return
        super().reject()
