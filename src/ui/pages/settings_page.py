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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from services.store import DataStore
from ui.styles.theme import THEME_LABELS, Palette


class SettingsPage(QWidget):
    def __init__(
        self,
        palette: Palette,
        store: DataStore,
        on_set_theme: Callable[[str], None],
        on_change_pin: Optional[Callable[[], None]] = None,
        on_data_changed: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__()
        self._palette = palette
        self._store = store
        self._on_set_theme = on_set_theme
        self._on_change_pin = on_change_pin
        self._on_data_changed = on_data_changed

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
        self._desc = QLabel(
            "Motyw interfejsu. „Daltonizm” używa kolorów bezpiecznych dla osób\n"
            "z zaburzeniami rozróżniania barw (czerwień/zieleń)."
        )
        self._desc.setWordWrap(True)
        row.addWidget(self._desc)
        row.addStretch(1)
        self._theme_combo = QComboBox()
        for key, label in THEME_LABELS.items():
            self._theme_combo.addItem(label, key)
        current = self._store.get_setting("theme", "dark")
        idx = self._theme_combo.findData(current)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        self._theme_combo.setMinimumWidth(260)
        self._theme_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_combo.currentIndexChanged.connect(
            lambda: self._on_set_theme(self._theme_combo.currentData())
        )
        row.addWidget(self._theme_combo)
        al.addLayout(row)
        root.addWidget(appearance)

        # --- przypomnienia ---
        reminders = QFrame()
        reminders.setObjectName("Panel")
        rl = QVBoxLayout(reminders)
        rl.setContentsMargins(20, 16, 20, 16)
        rl.setSpacing(12)
        r_title = QLabel("Przypomnienia")
        r_title.setStyleSheet("font-size: 17px; font-weight: 700;")
        rl.addWidget(r_title)
        rrow = QHBoxLayout()
        self._followup_desc = QLabel(
            "Po ilu dniach bez kontaktu klient trafia do panelu „Bez kontaktu” na Dashboardzie.\n"
            "Zatrudnieni oraz osoby na stażu nie są pokazywani."
        )
        self._followup_desc.setWordWrap(True)
        rrow.addWidget(self._followup_desc)
        rrow.addStretch(1)
        self._followup_spin = QSpinBox()
        self._followup_spin.setRange(1, 365)
        self._followup_spin.setSuffix(" dni")
        self._followup_spin.setValue(self._store.follow_up_days())
        self._followup_spin.setMinimumWidth(120)
        self._followup_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        self._followup_spin.valueChanged.connect(self._on_followup_changed)
        rrow.addWidget(self._followup_spin)
        rl.addLayout(rrow)
        root.addWidget(reminders)

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
        self._pin_desc = QLabel("PIN (4 cyfry) chroni dostęp — pojawia się tylko przy uruchomieniu programu.")
        srow.addWidget(self._pin_desc)
        srow.addStretch(1)
        pin_btn = QPushButton("Zmień PIN")
        pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pin_btn.clicked.connect(lambda: self._on_change_pin() if self._on_change_pin else None)
        srow.addWidget(pin_btn)
        sl.addLayout(srow)
        root.addWidget(security)

        # --- dane (wyczyszczenie bazy) ---
        data = QFrame()
        data.setObjectName("Panel")
        dl = QVBoxLayout(data)
        dl.setContentsMargins(20, 16, 20, 16)
        dl.setSpacing(12)
        d_title = QLabel("Dane")
        d_title.setStyleSheet("font-size: 17px; font-weight: 700;")
        dl.addWidget(d_title)
        self._data_desc = QLabel(
            "Usuwa wszystkich klientów oraz powiązane dane (zadania, kontakty, szkolenia, "
            "notatki, zdjęcia). Ustawienia i PIN pozostają. Przydatne przy przygotowaniu "
            "aplikacji dla innego projektu. Operacji nie można cofnąć — najpierw rozważ kopię zapasową."
        )
        self._data_desc.setWordWrap(True)
        dl.addWidget(self._data_desc)
        drow = QHBoxLayout()
        self._clear_btn = QPushButton("Wyczyść bazę")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.clicked.connect(self._clear_database)
        drow.addWidget(self._clear_btn)
        drow.addStretch(1)
        dl.addLayout(drow)
        root.addWidget(data)

        self.set_palette(palette)
        self.refresh()

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        muted = f"color: {palette.text_muted}; font-size: 12px;"
        self._desc.setStyleSheet(f"color: {palette.text};")
        self._followup_desc.setStyleSheet(muted)
        self._backup_desc.setStyleSheet(muted)
        self._pin_desc.setStyleSheet(f"color: {palette.text};")
        self._data_desc.setStyleSheet(muted)
        from ui.widgets.pills import with_alpha

        red = palette.red
        self._clear_btn.setStyleSheet(
            f"QPushButton {{ background: {with_alpha(red, 0.12)}; color: {red};"
            f" border: 1px solid {with_alpha(red, 0.45)}; border-radius: 8px;"
            " padding: 7px 16px; font-weight: 600; }"
            f"QPushButton:hover {{ background: {with_alpha(red, 0.2)}; }}"
        )

    def _on_followup_changed(self, value: int) -> None:
        self._store.set_setting("follow_up_days", str(value))
        if self._on_data_changed:
            self._on_data_changed()

    def refresh(self) -> None:
        from services.backup import list_backups

        self._backup_combo.clear()
        for path in list_backups():
            self._backup_combo.addItem(path.name, str(path))
        if self._backup_combo.count() == 0:
            self._backup_combo.addItem("Brak kopii zapasowych", "")

    def _clear_database(self) -> None:
        count = len(self._store.clients)
        reply = QMessageBox.warning(
            self, "Wyczyść bazę",
            f"Zostanie trwale usuniętych {count} klientów wraz ze wszystkimi zadaniami, "
            "kontaktami, szkoleniami, notatkami i zdjęciami.\n\n"
            "Tej operacji NIE można cofnąć. Kontynuować?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self._store.clear_all_data()
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Wyczyść bazę", f"Nie udało się wyczyścić bazy:\n{exc}")
            return
        if self._on_data_changed:
            self._on_data_changed()
        QMessageBox.information(self, "Wyczyść bazę", "Baza została wyczyszczona.")

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
