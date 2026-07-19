"""Import XLSX — wybór pliku, podgląd zmian, zatwierdzenie w jednej transakcji."""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config import TABLE_HEADER_HEIGHT, TABLE_ROW_HEIGHT
from services.store import DataStore
from ui.styles.theme import Palette


class ImportPage(QWidget):
    def __init__(self, store: DataStore, palette: Palette, on_imported: Callable[[], None]) -> None:
        super().__init__()
        self._store = store
        self._palette = palette
        self._on_imported = on_imported
        self._preview = None

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # pasek akcji
        bar = QHBoxLayout()
        pick = QPushButton("Wybierz plik XLSX…")
        pick.setObjectName("Primary")
        pick.setCursor(Qt.CursorShape.PointingHandCursor)
        pick.clicked.connect(self._pick_file)
        bar.addWidget(pick)
        self._file_lbl = QLabel("Nie wybrano pliku.")
        bar.addWidget(self._file_lbl)
        bar.addStretch(1)
        self._confirm_btn = QPushButton("Zatwierdź import")
        self._confirm_btn.setObjectName("Primary")
        self._confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.clicked.connect(self._confirm)
        bar.addWidget(self._confirm_btn)
        root.addLayout(bar)

        # kafelki podsumowania
        self._summary = QHBoxLayout()
        self._summary.setSpacing(12)
        self._tiles: dict[str, QLabel] = {}
        for key, title in (
            ("new", "Nowi"), ("updated", "Aktualizowani"), ("unchanged", "Bez zmian"),
            ("errors", "Błędy"), ("duplicates", "Duplikaty"),
        ):
            tile, value = self._make_tile(title)
            self._tiles[key] = value
            self._summary.addWidget(tile)
        self._summary.addStretch(1)
        root.addLayout(self._summary)

        # tabela szczegółów
        panel = QFrame()
        panel.setObjectName("Panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(16, 12, 16, 12)
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Status", "ID klienta", "Klient", "Szczegóły"])
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.setWordWrap(False)
        self._table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._table.horizontalHeader().setFixedHeight(TABLE_HEADER_HEIGHT)
        self._table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        pl.addWidget(self._table)
        root.addWidget(panel, 1)

        self._hint = QLabel(
            "Identyfikacja po kolumnie ID (rozpoznaje m.in. „ASII LP.”, „ID klienta”, „LP”, „Nr”, "
            "„Numer”, „Poz.”). Ponowny import aktualizuje wyłącznie dane podstawowe — zadania, "
            "kontakty, szkolenia, notatki i zdjęcie pozostają bez zmian. "
            "Klient nieobecny w pliku nie jest usuwany."
        )
        self._hint.setWordWrap(True)
        root.addWidget(self._hint)

        self.set_palette(palette)

    # ------------------------------------------------------------------
    def _make_tile(self, title: str) -> tuple[QFrame, QLabel]:
        tile = QFrame()
        tile.setObjectName("Card")
        tile.setFixedWidth(150)
        layout = QVBoxLayout(tile)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)
        value = QLabel("0")
        value.setStyleSheet("font-size: 22px; font-weight: 700; border: none;")
        cap = QLabel(title)
        cap.setObjectName("tileCap")
        layout.addWidget(value)
        layout.addWidget(cap)
        return tile, value

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        p = palette
        self._file_lbl.setStyleSheet(f"color: {p.text_muted}; font-size: 13px;")
        self._hint.setStyleSheet(f"color: {p.text_muted}; font-size: 12px;")
        for cap in self.findChildren(QLabel, "tileCap"):
            cap.setStyleSheet(f"color: {p.text_muted}; font-size: 11px; text-transform: uppercase; border: none;")

    def refresh(self) -> None:
        pass

    # ------------------------------------------------------------------
    def _pick_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik XLSX do importu", "", "Pliki Excel (*.xlsx)"
        )
        if not path:
            return
        from importers.xlsx_import import build_preview

        try:
            self._preview = build_preview(self._store, path)
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Import", f"Nie udało się odczytać pliku:\n{exc}")
            return
        self._file_lbl.setText(self._preview.file_name)
        self._render_preview()
        pv = self._preview
        # twardy błąd (np. brak kolumny ID): nic nie da się zaimportować — pokaż wyraźny komunikat
        if not (pv.new or pv.updated or pv.unchanged) and pv.errors:
            QMessageBox.warning(self, "Import", pv.errors[0].message)
        has_changes = bool(pv.new or pv.updated)
        self._confirm_btn.setEnabled(has_changes)

    def _render_preview(self) -> None:
        pv = self._preview
        p = self._palette
        self._tiles["new"].setText(str(len(pv.new)))
        self._tiles["updated"].setText(str(len(pv.updated)))
        self._tiles["unchanged"].setText(str(len(pv.unchanged)))
        self._tiles["errors"].setText(str(len(pv.errors)))
        self._tiles["duplicates"].setText(str(len(pv.duplicates)))

        colors = {
            "Nowy": p.green, "Aktualizacja": p.accent, "Bez zmian": p.text_muted,
            "Błąd": p.red, "Duplikat": p.yellow,
        }
        rows: list[tuple[str, str, str, str]] = []
        for c in pv.new:
            rows.append(("Nowy", c.external_id, c.full_name, "Nowy klient"))
        for existing, target in pv.updated:
            changes = _describe_changes(existing, target)
            rows.append(("Aktualizacja", target.external_id, target.full_name, changes))
        for c in pv.unchanged:
            rows.append(("Bez zmian", c.external_id, c.full_name, "Dane identyczne"))
        for e in pv.duplicates:
            rows.append(("Duplikat", e.external_id, "—", e.message))
        for e in pv.errors:
            rows.append(("Błąd", e.external_id or "—", "—", e.message))

        self._table.setRowCount(len(rows))
        from ui.widgets.pills import make_pill

        for r, (status, ext, name, detail) in enumerate(rows):
            cell = QWidget()
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(8, 0, 8, 0)
            cl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            cl.addWidget(make_pill(status, colors.get(status, p.text_muted)))
            cell.setStyleSheet(f"background: transparent; border-bottom: 1px solid {p.line};")
            self._table.setCellWidget(r, 0, cell)
            self._table.setItem(r, 1, QTableWidgetItem(ext))
            self._table.setItem(r, 2, QTableWidgetItem(name))
            self._table.setItem(r, 3, QTableWidgetItem(detail))
        from PySide6.QtWidgets import QHeaderView

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(0, 130)

    def _confirm(self) -> None:
        if self._preview is None:
            return
        pv = self._preview
        reply = QMessageBox.question(
            self, "Zatwierdź import",
            f"Zaimportować {len(pv.new)} nowych i {len(pv.updated)} zaktualizowanych klientów?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self._store.apply_import(pv)
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Import", f"Import nie powiódł się:\n{exc}")
            return
        QMessageBox.information(
            self, "Import",
            f"Zaimportowano: {len(pv.new)} nowych, {len(pv.updated)} zaktualizowanych.",
        )
        self._confirm_btn.setEnabled(False)
        self._preview = None
        self._file_lbl.setText("Nie wybrano pliku.")
        self._table.setRowCount(0)
        for value in self._tiles.values():
            value.setText("0")
        self._on_imported()


def _describe_changes(existing, target) -> str:
    from importers.xlsx_import import UPDATABLE_FIELDS

    labels = {
        "first_name": "imię", "last_name": "nazwisko", "phone": "telefon", "email": "e-mail",
        "recruitment_date": "data rekrutacji", "ipd_date": "data IPD", "cv_status": "CV",
        "employment_status": "zatrudnienie", "internship_status": "staż", "gender": "płeć",
        "disability_degree": "stopień", "disability_symbol": "symbol",
        "combined_symbols": "symbole sprzężone", "education": "wykształcenie",
        "certificate_valid_until": "ważność orzeczenia", "desired_job": "poszukiwana praca",
        "import_comment": "komentarz", "dz": "DZ", "jc": "JC", "rp": "RP",
        "psychologist": "psycholog", "lawyer": "prawnik",
    }
    changed = [labels.get(f, f) for f in UPDATABLE_FIELDS if getattr(existing, f) != getattr(target, f)]
    return "Zmiana: " + ", ".join(changed) if changed else "—"
