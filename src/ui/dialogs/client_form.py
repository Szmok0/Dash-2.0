"""Stały formularz klienta — identyczny zakres pól co import XLSX (WORKFLOW.md)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.entities import Client
from services.store import DataStore

FORM_WIDTH = 640


def _parse_date(text: str) -> Optional[date]:
    """dd.mm.rrrr -> date; pusty tekst -> None; błąd -> ValueError."""
    text = text.strip()
    if not text:
        return None
    return datetime.strptime(text, "%d.%m.%Y").date()


def _fmt(d: Optional[date]) -> str:
    return d.strftime("%d.%m.%Y") if d else ""


class ClientFormDialog(QDialog):
    """Dodawanie klienta ręcznie; external_id obowiązkowy i unikalny."""

    def __init__(self, parent: QWidget, store: DataStore) -> None:
        super().__init__(parent)
        self.setWindowTitle("Dodaj klienta")
        self.setModal(True)
        self.setFixedWidth(FORM_WIDTH)
        self._store = store
        self.created_client_id: Optional[int] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        header = QLabel("Dodaj klienta")
        header.setStyleSheet("font-size: 17px; font-weight: 700;")
        root.addWidget(header)

        self._error = QLabel("")
        self._error.setWordWrap(True)
        self._error.setVisible(False)
        root.addWidget(self._error)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }")
        host = QWidget()
        form = QFormLayout(host)
        form.setSpacing(9)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(host)
        root.addWidget(scroll, 1)
        self.setMinimumHeight(620)

        def line(placeholder: str = "") -> QLineEdit:
            edit = QLineEdit()
            if placeholder:
                edit.setPlaceholderText(placeholder)
            return edit

        self.external_id = line("np. AS-1070 (wymagane, unikalne)")
        self.first_name = line("wymagane")
        self.last_name = line("wymagane")
        self.phone = line()
        self.email = line()
        self.recruitment_date = line("dd.mm.rrrr")
        self.ipd_date = line("dd.mm.rrrr")
        self.dz = line()
        self.jc = line()
        self.rp = line()
        self.psychologist = line()
        self.lawyer = line()
        self.gender = QComboBox()
        self.gender.addItems(["", "Kobieta", "Mężczyzna", "Inna"])
        self.disability_degree = QComboBox()
        self.disability_degree.addItems(["", "Lekki", "Umiarkowany", "Znaczny"])
        self.disability_symbol = line()
        self.combined_symbols = line()
        self.education = line()
        self.certificate_valid_until = line("dd.mm.rrrr")
        self.desired_job = line()
        self.comment = QTextEdit()
        self.comment.setAcceptRichText(False)
        self.comment.setFixedHeight(70)

        form.addRow("ASII LP. / ID klienta *", self.external_id)
        form.addRow("Imię *", self.first_name)
        form.addRow("Nazwisko *", self.last_name)
        form.addRow("Telefon", self.phone)
        form.addRow("E-mail", self.email)
        form.addRow("Data rekrutacji", self.recruitment_date)
        form.addRow("Data IPD", self.ipd_date)
        form.addRow("DZ", self.dz)
        form.addRow("JC", self.jc)
        form.addRow("RP", self.rp)
        form.addRow("Psycholog", self.psychologist)
        form.addRow("Prawnik", self.lawyer)
        form.addRow("Płeć", self.gender)
        form.addRow("Stopień niepełnosprawności", self.disability_degree)
        form.addRow("Symbol", self.disability_symbol)
        form.addRow("Symbole sprzężone", self.combined_symbols)
        form.addRow("Wykształcenie", self.education)
        form.addRow("Data ważności orzeczenia", self.certificate_valid_until)
        form.addRow("Poszukiwana praca", self.desired_job)
        form.addRow("Komentarz", self.comment)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("Anuluj")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        save = QPushButton("Zapisz")
        save.setObjectName("Primary")
        save.clicked.connect(self._save)
        buttons.addWidget(save)
        root.addLayout(buttons)

    def set_error_color(self, color: str) -> None:
        self._error.setStyleSheet(f"color: {color}; font-size: 12px;")

    def _fail(self, message: str) -> None:
        self._error.setText(message)
        self._error.setVisible(True)

    def _save(self) -> None:
        self._error.setVisible(False)
        external_id = self.external_id.text().strip()
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()

        if not external_id:
            self._fail("ID klienta jest wymagane.")
            return
        if self._store.find_by_external_id(external_id) is not None:
            self._fail(f"Klient o ID „{external_id}” już istnieje w bazie.")
            return
        if not first_name or not last_name:
            self._fail("Imię i nazwisko są wymagane.")
            return
        try:
            recruitment = _parse_date(self.recruitment_date.text())
            ipd = _parse_date(self.ipd_date.text())
            certificate = _parse_date(self.certificate_valid_until.text())
        except ValueError:
            self._fail("Nieprawidłowy format daty — użyj dd.mm.rrrr.")
            return

        client = Client(
            id=0,
            external_id=external_id,
            first_name=first_name,
            last_name=last_name,
            phone=self.phone.text().strip(),
            email=self.email.text().strip(),
            recruitment_date=recruitment,
            ipd_date=ipd,
            dz=self.dz.text().strip(),
            jc=self.jc.text().strip(),
            rp=self.rp.text().strip(),
            psychologist=self.psychologist.text().strip(),
            lawyer=self.lawyer.text().strip(),
            gender=self.gender.currentText(),
            disability_degree=self.disability_degree.currentText(),
            disability_symbol=self.disability_symbol.text().strip(),
            combined_symbols=self.combined_symbols.text().strip(),
            education=self.education.text().strip(),
            certificate_valid_until=certificate,
            desired_job=self.desired_job.text().strip(),
            import_comment=self.comment.toPlainText().strip(),
        )
        self.created_client_id = self._store.add_client(client)
        self.accept()
