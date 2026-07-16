"""Dashboard: tabela zadań (70–75%) + prawy panel z dwoma równymi modułami."""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config import TABLE_HEADER_HEIGHT, TABLE_ROW_HEIGHT
from data.sample_data import (
    PRIORITY_LABELS,
    SampleStore,
    TASK_STATUS_LABELS,
    Task,
)
from ui.styles.theme import Palette
from ui.widgets.icons import make_icon
from ui.widgets.pills import make_pill, priority_color, task_status_color

ACTION_LABELS = {
    "telefon": "Telefon",
    "spotkanie": "Spotkanie",
    "email": "E-mail",
    "cv": "CV",
    "szkolenie": "Szkolenie",
    "notatka": "Notatka",
}

COLUMNS = ["", "Typ", "Zadanie", "Klient", "ID", "Termin", "Priorytet", "Status"]


class DashboardPage(QWidget):
    def __init__(
        self,
        store: SampleStore,
        palette: Palette,
        open_client: Callable[[int], None],
    ) -> None:
        super().__init__()
        self._store = store
        self._palette = palette
        self._open_client = open_client
        self._filter = ""

        root = QHBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # --- Tabela zadań ---
        table_panel = QFrame()
        table_panel.setObjectName("Panel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(16, 14, 16, 12)
        table_layout.setSpacing(10)

        self._table_title = QLabel("Zadania")
        self._table_title.setStyleSheet("font-size: 17px; font-weight: 700;")
        table_layout.addWidget(self._table_title)

        self._table = QTableWidget(0, len(COLUMNS))
        self._table.setHorizontalHeaderLabels(COLUMNS)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.horizontalHeader().setFixedHeight(TABLE_HEADER_HEIGHT)
        self._table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._table.cellClicked.connect(self._row_clicked)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(0, 44)
        self._table.setColumnWidth(1, 110)
        self._table.setColumnWidth(4, 84)
        self._table.setColumnWidth(5, 150)
        self._table.setColumnWidth(6, 104)
        self._table.setColumnWidth(7, 150)

        table_layout.addWidget(self._table, 1)
        root.addWidget(table_panel, 73)

        # --- Prawy panel: dwa równe moduły ---
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        self._no_contact_panel = self._make_side_module("Bez kontaktu >30 dni")
        self._attention_panel = self._make_side_module("Wymagają uwagi")
        right_layout.addWidget(self._no_contact_panel["frame"], 1)
        right_layout.addWidget(self._attention_panel["frame"], 1)
        root.addWidget(right, 27)

        self.refresh()

    # ------------------------------------------------------------------
    def _make_side_module(self, title: str) -> dict:
        frame = QFrame()
        frame.setObjectName("Panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.setSpacing(8)

        head = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700;")
        counter = QLabel("0")
        counter.setStyleSheet(
            f"background: {self._palette.card}; border: 1px solid {self._palette.line};"
            f"border-radius: 9px; padding: 1px 9px; font-size: 11px; color: {self._palette.text_muted};"
        )
        head.addWidget(title_lbl)
        head.addWidget(counter)
        head.addStretch(1)
        layout.addLayout(head)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(6)
        body_layout.addStretch(1)
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        return {"frame": frame, "counter": counter, "body": body_layout}

    def _side_entry(self, primary: str, secondary: str, client_id: int) -> QPushButton:
        btn = QPushButton(f"{primary}\n{secondary}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            f"QPushButton {{ background: {self._palette.card}; border: 1px solid {self._palette.line};"
            "border-radius: 8px; padding: 8px 12px; text-align: left; font-size: 13px; }"
            f"QPushButton:hover {{ border-color: {self._palette.accent}; }}"
        )
        btn.clicked.connect(lambda: self._open_client(client_id))
        return btn

    # ------------------------------------------------------------------
    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self.refresh()

    def set_filter(self, text: str) -> None:
        self._filter = text.strip().lower()
        self.refresh()

    def refresh(self) -> None:
        self._fill_table()
        self._fill_side_panels()

    def _matches_filter(self, task: Task) -> bool:
        if not self._filter:
            return True
        client = self._store.client(task.client_id)
        hay = f"{client.external_id} {client.first_name} {client.last_name}".lower()
        return self._filter in hay

    def _fill_table(self) -> None:
        p = self._palette
        tasks = [t for t in self._store.dashboard_tasks() if self._matches_filter(t)]
        self._table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            client = self._store.client(task.client_id)
            done = task.status == "zakonczone"
            muted = done or task.status == "anulowane"

            # checkbox zakończenia
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(12, 0, 0, 0)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(done)
            checkbox.toggled.connect(lambda checked, t=task: self._toggle_done(t, checked))
            cell_layout.addWidget(checkbox)
            cell.setStyleSheet(f"background: transparent; border-bottom: 1px solid {p.line};")
            self._table.setCellWidget(row, 0, cell)

            # typ działania — jedyna kolumna z ikoną
            type_item = QTableWidgetItem(ACTION_LABELS.get(task.action_type, task.action_type))
            type_item.setIcon(make_icon(task.action_type, p.text_muted if muted else p.text))
            self._table.setItem(row, 1, type_item)

            self._table.setItem(row, 2, QTableWidgetItem(task.title))
            self._table.setItem(row, 3, QTableWidgetItem(client.full_name))
            self._table.setItem(row, 4, QTableWidgetItem(client.external_id))
            due = task.due_at.strftime("%d.%m.%Y %H:%M") if task.due_at else "—"
            self._table.setItem(row, 5, QTableWidgetItem(due))

            self._table.setCellWidget(
                row, 6, _pill_cell(PRIORITY_LABELS[task.priority], priority_color(p, task.priority), p)
            )
            self._table.setCellWidget(
                row, 7, _pill_cell(TASK_STATUS_LABELS[task.status], task_status_color(p, task.status), p)
            )

            for col in (1, 2, 3, 4, 5):
                item = self._table.item(row, col)
                if item is None:
                    continue
                font: QFont = item.font()
                font.setStrikeOut(done)
                item.setFont(font)
                if muted:
                    item.setForeground(Qt.GlobalColor.gray)

    def _toggle_done(self, task: Task, checked: bool) -> None:
        from datetime import datetime

        if checked:
            task.status = "zakonczone"
            task.completed_at = datetime.now()
        else:
            task.status = "do_zrobienia"
            task.completed_at = None
        self.refresh()

    def _row_clicked(self, row: int, column: int) -> None:
        if column == 0:
            return
        item = self._table.item(row, 4)
        if item is None:
            return
        external_id = item.text()
        for client in self._store.clients:
            if client.external_id == external_id:
                self._open_client(client.id)
                return

    def _fill_side_panels(self) -> None:
        no_contact = self._store.no_contact_over(30)
        _replace_entries(
            self._no_contact_panel["body"],
            [
                self._side_entry(
                    c.full_name,
                    f"{c.external_id} · " + (f"{days} dni bez kontaktu" if days is not None else "brak kontaktów"),
                    c.id,
                )
                for c, days in no_contact
            ],
        )
        self._no_contact_panel["counter"].setText(str(len(no_contact)))

        attention = self._store.requires_attention()
        _replace_entries(
            self._attention_panel["body"],
            [
                self._side_entry(
                    c.full_name,
                    f"{c.external_id} · {c.attention_note or 'Wymaga uwagi'}",
                    c.id,
                )
                for c in attention
            ],
        )
        self._attention_panel["counter"].setText(str(len(attention)))


def _pill_cell(text: str, color: str, palette: Palette) -> QWidget:
    cell = QWidget()
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(8, 0, 8, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(make_pill(text, color))
    cell.setStyleSheet(f"background: transparent; border-bottom: 1px solid {palette.line};")
    return cell


def _replace_entries(layout: QVBoxLayout, widgets: list[QWidget]) -> None:
    while layout.count() > 1:  # ostatni element to stretch
        item = layout.takeAt(0)
        w: Optional[QWidget] = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
    for i, w in enumerate(widgets):
        layout.insertWidget(i, w)
