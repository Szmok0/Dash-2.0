"""Formularze + Dodaj: Zadanie / Kontakt / Szkolenie / Notatka (zapis przez DataStore)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

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
from models.entities import (
    CONTACT_STATUSES,
    CONTACT_TYPE_LABELS,
    CONTACT_TYPES,
    Contact,
    Note,
    PRIORITIES,
    PRIORITY_LABELS,
    TASK_STATUS_LABELS,
    TASK_STATUSES,
    Task,
    TRAINING_STATUS_LABELS,
    TRAINING_STATUSES,
    TRAINING_TYPE_LABELS,
    TRAINING_TYPES,
    Training,
)
from services.store import DataStore


class _BaseDialog(QDialog):
    """Wspólny szkielet formularza: stała szerokość, Zapisz / Anuluj / Usuń."""

    def __init__(self, parent: QWidget, title: str, editing: bool = False) -> None:
        super().__init__(parent)
        self._editing = editing
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
        delete_btn.setEnabled(editing)  # usuwanie dostępne przy edycji istniejącego wpisu
        delete_btn.setVisible(editing)
        delete_btn.clicked.connect(self._delete)
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

    def _delete(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self, "Usuń wpis", "Czy na pewno usunąć ten wpis?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._do_delete()
            self.accept()

    def _do_delete(self) -> None:  # nadpisywane w podklasach z edycją
        pass

    def _note_field(self) -> QTextEdit:
        note = QTextEdit()
        note.setMinimumHeight(80)
        note.setAcceptRichText(False)
        return note

    def _save(self) -> None:  # nadpisywane w podklasach
        self.accept()


class TaskDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: DataStore, client_id: int, entry: Optional[Task] = None) -> None:
        super().__init__(parent, "Edytuj zadanie" if entry else "Nowe zadanie", editing=entry is not None)
        self._store = store
        self._client_id = client_id
        self._entry = entry

        self.title_edit = QLineEdit()
        self.action_box = QComboBox()
        for value, label in (
            ("telefon", "Telefon"), ("spotkanie", "Spotkanie"), ("email", "E-mail"),
            ("cv", "CV"), ("szkolenie", "Szkolenie"), ("notatka", "Notatka"),
        ):
            self.action_box.addItem(label, value)
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
        self.form.addRow("Typ działania", self.action_box)
        self.form.addRow("Termin", self.due_edit)
        self.form.addRow("Priorytet", self.priority_box)
        self.form.addRow("Status", self.status_box)
        self.form.addRow("Notatka", self.note_edit)

        if entry is not None:
            self.title_edit.setText(entry.title)
            self.action_box.setCurrentIndex(max(0, self.action_box.findData(entry.action_type)))
            if entry.due_at:
                self.due_edit.setDateTime(QDateTime(entry.due_at))
            self.priority_box.setCurrentIndex(max(0, self.priority_box.findData(entry.priority)))
            self.status_box.setCurrentIndex(max(0, self.status_box.findData(entry.status)))
            self.note_edit.setPlainText(entry.note)

    def _save(self) -> None:
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return
        status = self.status_box.currentData()
        completed = None
        if status == "zakonczone":
            completed = (self._entry.completed_at if self._entry and self._entry.completed_at else datetime.now())
        task = Task(
            id=self._entry.id if self._entry else 0,
            client_id=self._client_id,
            title=title,
            action_type=self.action_box.currentData(),
            due_at=self.due_edit.dateTime().toPython(),
            priority=self.priority_box.currentData(),
            status=status,
            note=self.note_edit.toPlainText().strip(),
            completed_at=completed,
        )
        if self._entry:
            self._store.update_task(task)
        else:
            self._store.add_task(task)
        self.accept()

    def _do_delete(self) -> None:
        if self._entry:
            self._store.delete_task(self._entry.id)


class ContactDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: DataStore, client_id: int, entry: Optional[Contact] = None) -> None:
        super().__init__(parent, "Edytuj kontakt" if entry else "Nowy kontakt", editing=entry is not None)
        self._store = store
        self._client_id = client_id
        self._entry = entry

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

        if entry is not None:
            self.type_box.setCurrentIndex(max(0, self.type_box.findData(entry.contact_type)))
            self.datetime_edit.setDateTime(QDateTime(entry.contact_at))
            self.status_box.setCurrentIndex(max(0, self.status_box.findData(entry.status)))
            self.note_edit.setPlainText(entry.note)

    def _save(self) -> None:
        contact = Contact(
            id=self._entry.id if self._entry else 0,
            client_id=self._client_id,
            contact_type=self.type_box.currentData(),
            contact_at=self.datetime_edit.dateTime().toPython(),
            status=self.status_box.currentData(),
            note=self.note_edit.toPlainText().strip(),
        )
        if self._entry:
            self._store.update_contact(contact)
        else:
            self._store.add_contact(contact)
        self.accept()

    def _do_delete(self) -> None:
        if self._entry:
            self._store.delete_contact(self._entry.id)


class TrainingDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: DataStore, client_id: int, entry: Optional[Training] = None) -> None:
        super().__init__(parent, "Edytuj szkolenie" if entry else "Nowe szkolenie", editing=entry is not None)
        self._store = store
        self._client_id = client_id
        self._entry = entry

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

        if entry is not None:
            self.name_edit.setText(entry.name)
            self.date_edit.setDateTime(QDateTime(entry.training_date, QDateTime.currentDateTime().time()))
            self.type_box.setCurrentIndex(max(0, self.type_box.findData(entry.training_type)))
            self.status_box.setCurrentIndex(max(0, self.status_box.findData(entry.status)))
            self.note_edit.setPlainText(entry.note)

    def _save(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            self.name_edit.setFocus()
            return
        training = Training(
            id=self._entry.id if self._entry else 0,
            client_id=self._client_id,
            name=name,
            training_date=self.date_edit.dateTime().toPython().date(),
            training_type=self.type_box.currentData(),
            status=self.status_box.currentData(),
            note=self.note_edit.toPlainText().strip(),
        )
        if self._entry:
            self._store.update_training(training)
        else:
            self._store.add_training(training)
        self.accept()

    def _do_delete(self) -> None:
        if self._entry:
            self._store.delete_training(self._entry.id)


class NoteDialog(_BaseDialog):
    def __init__(self, parent: QWidget, store: DataStore, client_id: int, entry: Optional[Note] = None) -> None:
        super().__init__(parent, "Edytuj notatkę" if entry else "Nowa notatka", editing=entry is not None)
        self._store = store
        self._client_id = client_id
        self._entry = entry
        self.note_edit = self._note_field()
        self.note_edit.setMinimumHeight(140)
        self.form.addRow("Treść", self.note_edit)
        if entry is not None:
            self.note_edit.setPlainText(entry.content)

    def _save(self) -> None:
        content = self.note_edit.toPlainText().strip()
        if not content:
            self.note_edit.setFocus()
            return
        if self._entry:
            self._entry.content = content
            self._store.update_note(self._entry)
        else:
            self._store.add_note(
                Note(id=0, client_id=self._client_id, content=content, created_at=datetime.now())
            )
        self.accept()

    def _do_delete(self) -> None:
        if self._entry:
            self._store.delete_note(self._entry.id)


DIALOGS = {
    "Zadanie": TaskDialog,
    "Kontakt": ContactDialog,
    "Szkolenie": TrainingDialog,
    "Notatka": NoteDialog,
}
