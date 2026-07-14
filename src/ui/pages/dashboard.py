"""Dashboard page for Sprint 0."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from src.models.sample_data import ATTENTION, CLIENTS, NO_CONTACT, TASKS
from src.ui.widgets.common import Pill, PRIORITY_COLORS, STATUS_COLORS

class DashboardPage(QWidget):
    open_client = Signal(int)
    def __init__(self) -> None:
        super().__init__()
        root = QHBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(16)
        table_wrap = QFrame(); table_wrap.setObjectName("TableWrap")
        table_layout = QVBoxLayout(table_wrap); table_layout.setContentsMargins(12,12,12,12)
        title = QLabel("Zadania na dziś i bieżące działania"); title.setObjectName("SectionTitle"); table_layout.addWidget(title)
        table = QTableWidget(len(TASKS), 8); table.setHorizontalHeaderLabels(["✓", "typ", "zadanie", "klient", "ID", "termin", "priorytet", "status"])
        table.verticalHeader().hide(); table.setShowGrid(False); table.setAlternatingRowColors(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setColumnWidth(0, 34); table.setColumnWidth(1, 92); table.setColumnWidth(2, 310); table.setColumnWidth(3, 150); table.setColumnWidth(4, 86); table.setColumnWidth(5, 96); table.setColumnWidth(6, 94)
        clients = {c["id"]: c for c in CLIENTS}
        for row, task in enumerate(TASKS):
            client = clients[task["client_id"]]
            values = ["☑" if task["done"] else "☐", task["type"], task["title"], f"{client['first_name']} {client['last_name']}", client["external_id"], task["due"], task["priority"], task["status"]]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value); item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if task["done"]:
                    font = item.font(); font.setStrikeOut(True); item.setFont(font); item.setForeground(Qt.gray)
                table.setItem(row, col, item)
            table.setCellWidget(row, 6, Pill(task["priority"], PRIORITY_COLORS[task["priority"]]))
            table.setCellWidget(row, 7, Pill(task["status"], STATUS_COLORS[task["status"]]))
            table.setRowHeight(row, 40)
        table.cellDoubleClicked.connect(lambda r, _c: self.open_client.emit(TASKS[r]["client_id"]))
        table_layout.addWidget(table)
        side = QVBoxLayout(); side.setSpacing(16)
        side.addWidget(self._list_panel("Bez kontaktu >30 dni", NO_CONTACT))
        side.addWidget(self._list_panel("Wymagają uwagi", ATTENTION))
        root.addWidget(table_wrap, 3); root.addLayout(side, 1)
    def _list_panel(self, title: str, rows: list[str]) -> QFrame:
        panel = QFrame(); panel.setObjectName("Panel")
        layout = QVBoxLayout(panel); layout.setContentsMargins(12,12,12,12); layout.setSpacing(8)
        label = QLabel(title); label.setObjectName("SectionTitle"); layout.addWidget(label)
        for row in rows:
            item = QLabel(row); item.setStyleSheet("background:#202737; border:1px solid #2B3245; border-radius:8px; padding:9px;"); layout.addWidget(item)
        layout.addStretch(); return panel
