"""Ustawienia: motyw dark/light, kopie zapasowe (backup/restore), zmiana PIN."""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.store import DataStore
from ui.styles.theme import Palette


class SettingsPage(QWidget):
    def __init__(
        self,
        palette: Palette,
        store: DataStore,
        on_toggle_theme: Callable[[], None],
        on_change_pin: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__()
        self._palette = palette
        self._store = store
        self._on_change_pin = on_change_pin

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- wygląd ---
        appearance = QFrame()
        appearance.setObjectName("Panel")
        al = QVBoxLayout(appearance)
        al.setContentsMargins(20, 16, 20, 16)
        al.setSpacing(12)
        title = QLabel("Wygląd")
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        al.addWidget(title)
        row = QHBoxLayout()
        self._desc = QLabel("Motyw interfejsu (ciemny to projekt bazowy, jasny to opcja).")
        row.addWidget(self._desc)
        row.addStretch(1)
        toggle_btn = QPushButton("Przełącz dark / light")
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_btn.clicked.connect(on_toggle_theme)
        row.addWidget(toggle_btn)
        al.addLayout(row)
        root.addWidget(appearance)

        # --- kopie zapasowe ---
        backup = QFrame()
        backup.setObjectName("Panel")
        bl = QVBoxLayout(backup)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(12)
        b_title = QLabel("Kopie zapasowe")
        b_title.setStyleSheet("font-size: 17px; font-weight: 700;")
        bl.addWidget(b_title)

        self._backup_desc = QLabel(
            "Kopia obejmuje bazę, zdjęcia i ustawienia. Tworzona automatycznie raz dziennie; "
            "zachowywanych jest 10 ostatnich."
        )
        self._backup_desc.setWordWrap(True)
        bl.addWidget(self._backup_desc)

        actions = QHBoxLayout()
        now_btn = QPushButton("Utwórz kopię teraz")
        now_btn.setObjectName("Primary")
        now_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        now_btn.clicked.connect(self._create_backup)
        actions.addWidget(now_btn)

        self._backup_combo = QComboBox()
        self._backup_combo.setMinimumWidth(320)
        actions.addWidget(self._backup_combo)

        restore_btn = QPushButton("Przywróć wybraną")
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.clicked.connect(self._restore_backup)
        actions.addWidget(restore_btn)
        actions.addStretch(1)
        bl.addLayout(actions)
        root.addWidget(backup)

        # --- bezpieczeństwo ---
        security = QFrame()
        security.setObjectName("Panel")
        sl = QVBoxLayout(security)
        sl.setContentsMargins(20, 16, 20, 16)
        sl.setSpacing(12)
        s_title = QLabel("Bezpieczeństwo")
        s_title.setStyleSheet("font-size: 17px; font-weight: 700;")
        sl.addWidget(s_title)
        srow = QHBoxLayout()
        self._pin_desc = QLabel("PIN (4 cyfry) chroni dostęp i blokuje aplikację po bezczynności.")
        srow.addWidget(self._pin_desc)
        srow.addStretch(1)
        pin_btn = QPushButton("Zmień PIN")
        pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pin_btn.clicked.connect(lambda: self._on_change_pin() if self._on_change_pin else None)
        srow.addWidget(pin_btn)
        sl.addLayout(srow)
        root.addWidget(security)

        self.set_palette(palette)
        self.refresh()

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        muted = f"color: {palette.text_muted}; font-size: 12px;"
        self._desc.setStyleSheet(f"color: {palette.text};")
        self._backup_desc.setStyleSheet(muted)
        self._pin_desc.setStyleSheet(f"color: {palette.text};")

    def refresh(self) -> None:
        from services.backup import list_backups

        self._backup_combo.clear()
        for path in list_backups():
            self._backup_combo.addItem(path.name, str(path))
        if self._backup_combo.count() == 0:
            self._backup_combo.addItem("Brak kopii zapasowych", "")

    # ------------------------------------------------------------------
    def _create_backup(self) -> None:
        from services.backup import create_backup

        try:
            self._store.checkpoint()
            path = create_backup()
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Kopia zapasowa", f"Nie udało się utworzyć kopii:\n{exc}")
            return
        self.refresh()
        QMessageBox.information(self, "Kopia zapasowa", f"Utworzono kopię:\n{path.name}")

    def _restore_backup(self) -> None:
        archive = self._backup_combo.currentData()
        if not archive:
            QMessageBox.information(self, "Przywracanie", "Brak kopii do przywrócenia.")
            return
        reply = QMessageBox.warning(
            self, "Przywracanie kopii",
            "Przywrócenie zastąpi bieżące dane zawartością wybranej kopii.\n"
            "Tej operacji nie można cofnąć. Kontynuować?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        from services.backup import restore_backup

        try:
            self._store.close()
            restore_backup(archive)
            self._store.reopen()
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Przywracanie", f"Nie udało się przywrócić:\n{exc}")
            return
        QMessageBox.information(
            self, "Przywracanie",
            "Dane zostały przywrócone. Odśwież widoki lub uruchom aplikację ponownie.",
        )
        self.refresh()
