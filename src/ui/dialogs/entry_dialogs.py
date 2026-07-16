"""Formularze + Dodaj: Zadanie / Kontakt / Szkolenie / Notatka (Sprint 0: zapis do pamięci)."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import FORM_WIDTH
from data.sample_data import (
    CONTACT_STATUSES,
    CONTACT_TYPE_LABELS,
    CONTACT_TYPES,
    Contact,
    Note,
    PRIORITIES,
    PRIORITY_LABELS,
    SampleStore,
    TASK_STATUS_LABELS,
    TASK_STATUSES,
    Task,
    TRAINING_STATUS_LABELS,
    TRAINING_STATUSES,
    TRAINING_TYPE_LABELS,
    TRAINING_TYPES,
    Training,
)


class _BaseDialog(QDialog):
    """Wspólny szkielet formularza: stała szerokość, Zapisz / Anuluj / Usuń."""

    def __init__(self, parent: QWidget, title: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(FORM_WIDTH)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(24, 20, 24, 20)
        self._root.setSpacing(16)

        header = QLabel(title)
        header.setStyleSheet("font-size: 17px; font-weight: 700;")
        self._root.addWidget(header)

        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self._root.addLayout(self.form)

        buttons = QHBoxLayout()
        delete_btn = QPushButton("Usuń")
        delete_btn.setObjectName("Danger")
        delete_btn.setEnabled(False)  # Sprint 0: edycja istniejących wpisów poza zakresem
        buttons.addWidget(delete_btn)
        buttons.addStretch(1)
        cancel = QPushButton("Anuluj")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        save = QPushButton("Zapisz")
        save.setObjectName("Primary")
        save.clicked.connect(self._save)
        buttons.addWidget(save)
        self._root.addLayout(buttons)

    def _note_field(self) -> QTextEdit:
        note = QTextEdit()
        note.setMinimumHeight(80)
        note.setAcceptRichText(False)
        return note

    def _save(self) -> None:  # nadpisywane w podklasach
        self.accept()


class TaskDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: SampleStore, client_id: int) -> None:
        super().__init__(parent, "Nowe zadanie")
        self._store = store
        self._client_id = client_id

        self.title_edit = QLineEdit()
        self.due_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.due_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.due_edit.setCalendarPopup(True)
        self.priority_box = QComboBox()
        for value in PRIORITIES:
            self.priority_box.addItem(PRIORITY_LABELS[value], value)
        self.status_box = QComboBox()
        for value in TASK_STATUSES:
            self.status_box.addItem(TASK_STATUS_LABELS[value], value)
        self.note_edit = self._note_field()

        self.form.addRow("Nazwa", self.title_edit)
        self.form.addRow("Termin", self.due_edit)
        self.form.addRow("Priorytet", self.priority_box)
        self.form.addRow("Status", self.status_box)
        self.form.addRow("Notatka", self.note_edit)

    def _save(self) -> None:
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return
        status = self.status_box.currentData()
        self._store.tasks.append(
            Task(
                id=self._store.next_id(),
                client_id=self._client_id,
                title=title,
                due_at=self.due_edit.dateTime().toPython(),
                priority=self.priority_box.currentData(),
                status=status,
                note=self.note_edit.toPlainText().strip(),
                completed_at=datetime.now() if status == "zakonczone" else None,
            )
        )
        self.accept()


class ContactDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: SampleStore, client_id: int) -> None:
        super().__init__(parent, "Nowy kontakt")
        self._store = store
        self._client_id = client_id

        self.type_box = QComboBox()
        for value in CONTACT_TYPES:
            self.type_box.addItem(CONTACT_TYPE_LABELS[value], value)
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.datetime_edit.setCalendarPopup(True)
        self.status_box = QComboBox()
        for value in CONTACT_STATUSES:
            self.status_box.addItem(value.capitalize(), value)
        self.note_edit = self._note_field()

        self.form.addRow("Typ", self.type_box)
        self.form.addRow("Data i godzina", self.datetime_edit)
        self.form.addRow("Status", self.status_box)
        self.form.addRow("Notatka", self.note_edit)

    def _save(self) -> None:
        self._store.contacts.append(
            Contact(
                id=self._store.next_id(),
                client_id=self._client_id,
                contact_type=self.type_box.currentData(),
                contact_at=self.datetime_edit.dateTime().toPython(),
                status=self.status_box.currentData(),
                note=self.note_edit.toPlainText().strip(),
            )
        )
        self.accept()


class TrainingDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: SampleStore, client_id: int) -> None:
        super().__init__(parent, "Nowe szkolenie")
        self._store = store
        self._client_id = client_id

        self.name_edit = QLineEdit()
        self.date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setCalendarPopup(True)
        self.type_box = QComboBox()
        for value in TRAINING_TYPES:
            self.type_box.addItem(TRAINING_TYPE_LABELS[value], value)
        self.status_box = QComboBox()
        for value in TRAINING_STATUSES:
            self.status_box.addItem(TRAINING_STATUS_LABELS[value], value)
        self.note_edit = self._note_field()

        self.form.addRow("Nazwa", self.name_edit)
        self.form.addRow("Data", self.date_edit)
        self.form.addRow("Rodzaj", self.type_box)
        self.form.addRow("Status", self.status_box)
        self.form.addRow("Notatka", self.note_edit)

    def _save(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            self.name_edit.setFocus()
            return
        self._store.trainings.append(
            Training(
                id=self._store.next_id(),
                client_id=self._client_id,
                name=name,
                training_date=self.date_edit.dateTime().toPython().date(),
                training_type=self.type_box.currentData(),
                status=self.status_box.currentData(),
                note=self.note_edit.toPlainText().strip(),
            )
        )
        self.accept()


class NoteDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: SampleStore, client_id: int) -> None:
        super().__init__(parent, "Nowa notatka")
        self._store = store
        self._client_id = client_id
        self.note_edit = self._note_field()
        self.note_edit.setMinimumHeight(140)
        self.form.addRow("Treść", self.note_edit)

    def _save(self) -> None:
        content = self.note_edit.toPlainText().strip()
        if not content:
            self.note_edit.setFocus()
            return
        self._store.notes.append(
            Note(
                id=self._store.next_id(),
                client_id=self._client_id,
                content=content,
                created_at=datetime.now(),
            )
        )
        self.accept()


DIALOGS = {
    "Zadanie": TaskDialog,
    "Kontakt": ContactDialog,
    "Szkolenie": TrainingDialog,
    "Notatka": NoteDialog,
}
