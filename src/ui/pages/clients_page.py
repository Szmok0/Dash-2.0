"""Lista klientów (Sprint 0: statyczna lista z wyszukiwaniem, klik otwiera kartę)."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config import TABLE_HEADER_HEIGHT, TABLE_ROW_HEIGHT
from models.entities import CLIENT_STATUS_LABELS
from services.store import DataStore
from ui.styles.theme import Palette
from ui.widgets.pills import make_pill

COLUMNS = ["ID", "Nazwisko", "Imię", "Telefon", "E-mail", "Status"]


class ClientsPage(QWidget):
    def __init__(
        self,
        store: DataStore,
        palette: Palette,
        open_client: Callable[[int], None],
    ) -> None:
        super().__init__()
        self._store = store
        self._palette = palette
        self._open_client = open_client
        self._filter = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.setSpacing(10)

        head = QHBoxLayout()
        title = QLabel("Klienci")
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        head.addWidget(title)
        head.addStretch(1)
        add_btn = QPushButton("+ Dodaj klienta")
        add_btn.setObjectName("Primary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_client)
        head.addWidget(add_btn)
        layout.addLayout(head)

        self._table = QTableWidget(0, len(COLUMNS))
        self._table.setHorizontalHeaderLabels(COLUMNS)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.setWordWrap(False)
        self._table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._table.horizontalHeader().setFixedHeight(TABLE_HEADER_HEIGHT)
        self._table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        self._table.cellClicked.connect(self._row_clicked)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 100)
        layout.addWidget(self._table, 1)

        root.addWidget(panel, 1)
        self.refresh()

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self.refresh()

    def set_filter(self, text: str) -> None:
        self._filter = text.strip().lower()
        self.refresh()

    def refresh(self) -> None:
        p = self._palette
        clients = self._store.search_clients(self._filter)
        self._table.setRowCount(len(clients))
        for row, c in enumerate(clients):
            self._table.setItem(row, 0, QTableWidgetItem(c.external_id))
            self._table.setItem(row, 1, QTableWidgetItem(c.last_name))
            self._table.setItem(row, 2, QTableWidgetItem(c.first_name))
            self._table.setItem(row, 3, QTableWidgetItem(c.phone or "—"))
            self._table.setItem(row, 4, QTableWidgetItem(c.email or "—"))
            color = p.accent if c.client_status == "aktywny" else p.text_muted
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(8, 0, 8, 0)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            cell_layout.addWidget(make_pill(CLIENT_STATUS_LABELS[c.client_status], color))
            cell.setStyleSheet(f"background: transparent; border-bottom: 1px solid {p.line};")
            self._table.setCellWidget(row, 5, cell)

    def _add_client(self) -> None:
        from ui.dialogs.client_form import ClientFormDialog

        dialog = ClientFormDialog(self, self._store)
        dialog.set_error_color(self._palette.red)
        if dialog.exec() and dialog.created_client_id is not None:
            self.refresh()
            self._open_client(dialog.created_client_id)

    def _row_clicked(self, row: int, _column: int) -> None:
        item = self._table.item(row, 0)
        if item is None:
            return
        client = self._store.find_by_external_id(item.text())
        if client is not None:
            self._open_client(client.id)
