"""Analityka — filtry (bez wykresów), historia działań, eksport PDF/CSV/XLSX.

Dwa tryby: „Klienci" (lista filtrowana po danych podstawowych i statusach)
oraz „Historia działań" (zadania/kontakty/szkolenia w okresie). Każdy wynik
jest klikalny i prowadzi do karty klienta.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Callable, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config import TABLE_HEADER_HEIGHT, TABLE_ROW_HEIGHT
from exporters.table_export import TableData, export_csv, export_pdf, export_xlsx
from models.entities import (
    CLIENT_STATUS_LABELS,
    CV_STATUS_LABELS,
    CV_STATUSES,
    EMPLOYMENT_LABELS,
    INTERNSHIP_LABELS,
    IPD_STATUS_LABELS,
)
from services.analytics import (
    ANY,
    DONE,
    NOT_DONE,
    AnalyticsService,
    ClientFilter,
    HistoryFilter,
)
from services.store import DataStore
from ui.styles.theme import Palette

GENDERS = ["Kobieta", "Mężczyzna", "Inna"]
DEGREES = ["Lekki", "Umiarkowany", "Znaczny"]


class AnalyticsPage(QWidget):
    def __init__(
        self,
        store: DataStore,
        palette: Palette,
        open_client: Callable[[int], None],
    ) -> None:
        super().__init__()
        self._store = store
        self._service = AnalyticsService(store)
        self._palette = palette
        self._open_client = open_client
        self._mode = "clients"  # clients | history
        self._last_table: Optional[TableData] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # --- przełącznik trybu ---
        mode_row = QHBoxLayout()
        self._clients_btn = QPushButton("Klienci")
        self._clients_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clients_btn.clicked.connect(lambda: self._set_mode("clients"))
        self._history_btn = QPushButton("Historia działań")
        self._history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._history_btn.clicked.connect(lambda: self._set_mode("history"))
        mode_row.addWidget(self._clients_btn)
        mode_row.addWidget(self._history_btn)
        mode_row.addStretch(1)

        self._result_lbl = QLabel("")
        mode_row.addWidget(self._result_lbl)
        mode_row.addSpacing(10)

        for text, handler in (
            ("Eksport CSV", lambda: self._export("csv")),
            ("Eksport XLSX", lambda: self._export("xlsx")),
            ("Eksport PDF", lambda: self._export("pdf")),
        ):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(handler)
            mode_row.addWidget(btn)
        root.addLayout(mode_row)

        # --- panel filtrów (zwijalny, aby lista wyników mogła zająć większość ekranu) ---
        self._filters_panel = QFrame()
        self._filters_panel.setObjectName("Panel")
        fl = QVBoxLayout(self._filters_panel)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(10)

        # nagłówek panelu: przełącznik zwijania + akcje (zawsze widoczne)
        fhead = QHBoxLayout()
        self._filters_toggle = QPushButton("▾  Filtry")
        self._filters_toggle.setObjectName("Ghost")
        self._filters_toggle.setCheckable(True)
        self._filters_toggle.setChecked(True)
        self._filters_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._filters_toggle.toggled.connect(self._toggle_filters)
        fhead.addWidget(self._filters_toggle)
        fhead.addStretch(1)
        reset = QPushButton("Wyczyść filtry")
        reset.setCursor(Qt.CursorShape.PointingHandCursor)
        reset.clicked.connect(self._reset_filters)
        apply_btn = QPushButton("Zastosuj")
        apply_btn.setObjectName("Primary")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.clicked.connect(self.refresh)
        fhead.addWidget(reset)
        fhead.addWidget(apply_btn)
        fl.addLayout(fhead)

        # pola filtrów w zwijalnym kontenerze
        self._fields_container = QWidget()
        fcv = QVBoxLayout(self._fields_container)
        fcv.setContentsMargins(0, 4, 0, 0)
        fcv.setSpacing(10)
        self._client_filters = self._build_client_filters()
        self._history_filters = self._build_history_filters()
        fcv.addWidget(self._client_filters)
        fcv.addWidget(self._history_filters)
        fl.addWidget(self._fields_container)
        root.addWidget(self._filters_panel)

        # --- tabela wyników ---
        panel = QFrame()
        panel.setObjectName("Panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(16, 12, 16, 12)
        self._table = QTableWidget(0, 0)
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
        self._table.cellClicked.connect(self._row_clicked)
        pl.addWidget(self._table)
        root.addWidget(panel, 1)

        self.set_palette(palette)

    # ------------------------------------------------------------------
    def _build_client_filters(self) -> QWidget:
        w = QWidget()
        grid = QGridLayout(w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)

        self.f_text = QLineEdit()
        self.f_text.setPlaceholderText("ID / imię / nazwisko / poszukiwana praca")

        self.f_client_status = self._combo(CLIENT_STATUS_LABELS)
        self.f_cv = self._combo({v: CV_STATUS_LABELS[v] for v in CV_STATUSES})
        self.f_ipd = self._combo(IPD_STATUS_LABELS)
        self.f_dm = self._combo({DONE: "Zrobiony", NOT_DONE: "Nie ma"})
        self.f_aneks = self._combo({DONE: "Zrobiony", NOT_DONE: "Nie ma"})
        self.f_internship = self._combo(INTERNSHIP_LABELS)
        self.f_employment = self._combo(EMPLOYMENT_LABELS)
        self.f_gender = self._combo({g: g for g in GENDERS})
        self.f_degree = self._combo({d: d for d in DEGREES})

        self.f_has_tasks = QCheckBox("Ma zadania")
        self.f_has_contacts = QCheckBox("Ma kontakty")
        self.f_has_trainings = QCheckBox("Ma szkolenia")

        self._client_labels: list[QLabel] = []
        # pole „Szukaj" na własnym wierszu (pełna szerokość), reszta w siatce 4-kolumnowej
        def add_field(label: str, widget, row: int, col: int, span: int = 1) -> None:
            cell = QVBoxLayout()
            cap = QLabel(label)
            self._client_labels.append(cap)
            cell.addWidget(cap)
            cell.addWidget(widget)
            holder = QWidget()
            holder.setLayout(cell)
            grid.addWidget(holder, row, col, 1, span)

        add_field("Szukaj", self.f_text, 0, 0, 4)
        combos = [
            ("Status klienta", self.f_client_status),
            ("CV", self.f_cv),
            ("IPD", self.f_ipd),
            ("DM", self.f_dm),
            ("Aneks", self.f_aneks),
            ("Staż", self.f_internship),
            ("Zatrudnienie", self.f_employment),
            ("Płeć", self.f_gender),
            ("Stopień niepełnosprawności", self.f_degree),
        ]
        for i, (label, widget) in enumerate(combos):
            row, col = divmod(i, 4)
            add_field(label, widget, row + 1, col)
        for col in range(4):
            grid.setColumnStretch(col, 1)

        checks = QHBoxLayout()
        checks.addWidget(self.f_has_tasks)
        checks.addWidget(self.f_has_contacts)
        checks.addWidget(self.f_has_trainings)
        checks.addStretch(1)
        holder = QWidget()
        holder.setLayout(checks)
        # 9 combo-boxów zajmuje wiersze 1–3, checkboxy pod nimi (wiersz 4)
        grid.addWidget(holder, 4, 0, 1, 4)
        return w

    def _build_history_filters(self) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        self.h_start = QDateEdit(QDate.currentDate().addDays(-30))
        self.h_start.setDisplayFormat("dd.MM.yyyy")
        self.h_start.setCalendarPopup(True)
        self.h_end = QDateEdit(QDate.currentDate().addDays(30))
        self.h_end.setDisplayFormat("dd.MM.yyyy")
        self.h_end.setCalendarPopup(True)
        self.h_tasks = QCheckBox("Zadania")
        self.h_tasks.setChecked(True)
        self.h_contacts = QCheckBox("Kontakty")
        self.h_contacts.setChecked(True)
        self.h_trainings = QCheckBox("Szkolenia")
        self.h_trainings.setChecked(True)

        self._history_labels = []
        for label, widget in (("Od", self.h_start), ("Do", self.h_end)):
            cell = QVBoxLayout()
            cap = QLabel(label)
            self._history_labels.append(cap)
            cell.addWidget(cap)
            cell.addWidget(widget)
            holder = QWidget()
            holder.setLayout(cell)
            row.addWidget(holder)
        row.addWidget(self.h_tasks)
        row.addWidget(self.h_contacts)
        row.addWidget(self.h_trainings)
        row.addStretch(1)
        return w

    def _combo(self, labels: dict[str, str]) -> QComboBox:
        box = QComboBox()
        box.addItem("Dowolny", ANY)
        for value, text in labels.items():
            box.addItem(text, value)
        return box

    # ------------------------------------------------------------------
    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        p = palette
        self._result_lbl.setStyleSheet(
            f"color: {p.text}; font-size: 14px; font-weight: 700;"
            f" background: {p.card}; border: 1px solid {p.line};"
            " border-radius: 8px; padding: 6px 14px;"
        )
        for btn, active in ((self._clients_btn, self._mode == "clients"),
                            (self._history_btn, self._mode == "history")):
            btn.setStyleSheet(
                f"QPushButton {{ background: {p.accent if active else p.card}; "
                f"color: {'#FFFFFF' if active else p.text}; border: 1px solid "
                f"{p.accent if active else p.line}; border-radius: 8px; padding: 7px 16px; "
                "font-weight: 600; }"
            )
        cap_css = f"color: {p.text_muted}; font-size: 11px; text-transform: uppercase;"
        for lbl in getattr(self, "_client_labels", []) + getattr(self, "_history_labels", []):
            lbl.setStyleSheet(cap_css)
        self._client_filters.setVisible(self._mode == "clients")
        self._history_filters.setVisible(self._mode == "history")
        self.refresh()

    def _set_mode(self, mode: str) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self.set_palette(self._palette)

    def _toggle_filters(self, expanded: bool) -> None:
        """Zwija/rozwija pola filtrów — po zwinięciu lista wyników zajmuje niemal cały ekran."""
        self._fields_container.setVisible(expanded)
        self._filters_toggle.setText("▾  Filtry" if expanded else "▸  Filtry (rozwiń)")

    def _reset_filters(self) -> None:
        if self._mode == "clients":
            self.f_text.clear()
            for box in (self.f_client_status, self.f_cv, self.f_ipd, self.f_dm, self.f_aneks,
                        self.f_internship, self.f_employment, self.f_gender, self.f_degree):
                box.setCurrentIndex(0)
            for chk in (self.f_has_tasks, self.f_has_contacts, self.f_has_trainings):
                chk.setChecked(False)
        else:
            self.h_start.setDate(QDate.currentDate().addDays(-30))
            self.h_end.setDate(QDate.currentDate().addDays(30))
            for chk in (self.h_tasks, self.h_contacts, self.h_trainings):
                chk.setChecked(True)
        self.refresh()

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        if self._mode == "clients":
            self._render_clients()
        else:
            self._render_history()

    def _render_clients(self) -> None:
        flt = ClientFilter(
            text=self.f_text.text(),
            client_status=self.f_client_status.currentData(),
            cv_status=self.f_cv.currentData(),
            ipd_status=self.f_ipd.currentData(),
            dm=self.f_dm.currentData(),
            aneks=self.f_aneks.currentData(),
            internship_status=self.f_internship.currentData(),
            employment_status=self.f_employment.currentData(),
            gender=self.f_gender.currentData(),
            disability_degree=self.f_degree.currentData(),
            has_tasks=self.f_has_tasks.isChecked(),
            has_contacts=self.f_has_contacts.isChecked(),
            has_trainings=self.f_has_trainings.isChecked(),
        )
        rows = self._service.filter_clients(flt)
        headers = ["ID", "Nazwisko", "Imię", "Status", "CV", "Zatrudnienie",
                   "Zadania", "Kontakty", "Szkolenia"]
        table_rows: list[list[str]] = []
        self._row_client_ids: list[int] = []
        for r in rows:
            c = r.client
            table_rows.append([
                c.external_id, c.last_name, c.first_name,
                CLIENT_STATUS_LABELS.get(c.client_status, c.client_status),
                CV_STATUS_LABELS.get(c.cv_status, c.cv_status),
                EMPLOYMENT_LABELS.get(c.employment_status, c.employment_status),
                str(r.task_count), str(r.contact_count), str(r.training_count),
            ])
            self._row_client_ids.append(c.id)
        self._last_table = TableData("Analityka — klienci", headers, table_rows)
        self._fill_table(headers, table_rows)
        self._result_lbl.setText(f"Znaleziono klientów: {len(table_rows)}")

    def _render_history(self) -> None:
        flt = HistoryFilter(
            start=self.h_start.date().toPython(),
            end=self.h_end.date().toPython(),
            include_tasks=self.h_tasks.isChecked(),
            include_contacts=self.h_contacts.isChecked(),
            include_trainings=self.h_trainings.isChecked(),
        )
        rows = self._service.activity_history(flt)
        headers = ["Data", "Klient", "ID", "Typ", "Opis", "Status"]
        table_rows: list[list[str]] = []
        self._row_client_ids = []
        kind_labels = {"zadanie": "Zadanie", "kontakt": "Kontakt", "szkolenie": "Szkolenie"}
        for a in rows:
            when = a.when.strftime("%d.%m.%Y %H:%M") if a.has_time else a.when.strftime("%d.%m.%Y")
            table_rows.append([
                when, a.client_name, a.external_id,
                kind_labels.get(a.kind, a.kind), a.description, a.status,
            ])
            self._row_client_ids.append(a.client_id)
        self._last_table = TableData("Analityka — historia działań", headers, table_rows)
        self._fill_table(headers, table_rows)
        self._result_lbl.setText(f"Działań w okresie: {len(table_rows)}")

    def _fill_table(self, headers: list[str], rows: list[list[str]]) -> None:
        # kolumna „Lp." (1..N) — od razu widać, ilu klientów/działań; ostatni numer = łącznie
        disp_headers = ["Lp."] + headers
        self._table.clear()
        self._table.setColumnCount(len(disp_headers))
        self._table.setHorizontalHeaderLabels(disp_headers)
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self._table.setItem(r, 0, QTableWidgetItem(str(r + 1)))
            for c, value in enumerate(row):
                self._table.setItem(r, c + 1, QTableWidgetItem(value))
        # kolumny dopasowane do treści, jedna opisowa rozciągliwa (indeks +1 za kolumnę Lp.)
        header = self._table.horizontalHeader()
        stretch_col = (4 if self._mode == "history" else 1) + 1
        for col in range(len(disp_headers)):
            mode = (
                QHeaderView.ResizeMode.Stretch
                if col == stretch_col
                else QHeaderView.ResizeMode.ResizeToContents
            )
            header.setSectionResizeMode(col, mode)

    def _row_clicked(self, row: int, _col: int) -> None:
        if 0 <= row < len(getattr(self, "_row_client_ids", [])):
            self._open_client(self._row_client_ids[row])

    # ------------------------------------------------------------------
    def _export(self, fmt: str) -> None:
        if not self._last_table or not self._last_table.rows:
            QMessageBox.information(self, "Eksport", "Brak wyników do wyeksportowania.")
            return
        try:
            if fmt == "csv":
                path = export_csv(self._last_table)
            elif fmt == "xlsx":
                path = export_xlsx(self._last_table)
            else:
                path = export_pdf(self._last_table)
        except Exception as exc:  # pragma: no cover - komunikat dla użytkownika
            QMessageBox.critical(self, "Eksport", f"Nie udało się wyeksportować:\n{exc}")
            return
        QMessageBox.information(self, "Eksport", f"Zapisano plik:\n{path}")
