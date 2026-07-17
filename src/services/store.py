"""DataStore — fasada usług nad SQLite; jedyny punkt dostępu UI do danych."""
from __future__ import annotations

import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from config import photos_dir
from database.connection import open_connection
from models.entities import (
    CONTACT_TYPE_LABELS,
    Client,
    Contact,
    Note,
    Task,
    Training,
)
from repositories.activities import (
    ContactRepository,
    NoteRepository,
    TaskRepository,
    TrainingRepository,
)
from repositories.analytics import AnalyticsRepository
from repositories.calendar import CalendarRepository
from repositories.clients import ClientRepository


class DataStore:
    def __init__(self, conn: Optional[sqlite3.Connection] = None) -> None:
        self._bind(conn or open_connection())

    def _bind(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._clients = ClientRepository(self._conn)
        self._tasks = TaskRepository(self._conn)
        self._contacts = ContactRepository(self._conn)
        self._trainings = TrainingRepository(self._conn)
        self._notes = NoteRepository(self._conn)
        self._calendar = CalendarRepository(self._conn)
        self._analytics = AnalyticsRepository(self._conn)
        from services.security import SecurityService

        self.security = SecurityService(self._conn)

    def checkpoint(self) -> None:
        """Zrzuca WAL do głównego pliku bazy (spójna kopia zapasowa)."""
        try:
            self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except sqlite3.Error:
            pass

    def close(self) -> None:
        self.checkpoint()
        self._conn.close()

    def reopen(self) -> None:
        """Ponownie otwiera połączenie (po odtworzeniu z kopii zapasowej)."""
        try:
            self._conn.close()
        except sqlite3.Error:
            pass
        self._bind(open_connection())

    # --- klienci -------------------------------------------------------
    @property
    def clients(self) -> list[Client]:
        return self._clients.list_all()

    def search_clients(self, text: str) -> list[Client]:
        return self._clients.list_all(text.strip())

    def client(self, client_id: int) -> Client:
        return self._clients.get(client_id)

    def find_by_external_id(self, external_id: str) -> Optional[Client]:
        return self._clients.get_by_external_id(external_id)

    def active_clients(self) -> list[Client]:
        return [c for c in self.clients if c.client_status == "aktywny"]

    def add_client(self, client: Client) -> int:
        return self._clients.insert(client)

    def update_client(self, client: Client) -> None:
        self._clients.update(client)

    def apply_import(self, preview) -> None:
        """Zatwierdza import w jednej transakcji; aktualizuje tylko dane podstawowe."""
        from importers.xlsx_import import UPDATABLE_FIELDS
        from repositories.mappers import d_to_db, now_db

        new_clients = preview.new
        updated = preview.updated  # list[(existing, target)]
        try:
            self._conn.execute("BEGIN")
            for client in new_clients:
                self._clients.insert_in_tx(client)
            for _existing, target in updated:
                self._clients.update_basic_in_tx(target, UPDATABLE_FIELDS)
            # dziennik importu
            self._conn.execute(
                "INSERT INTO imports (file_name, imported_at, total_rows, inserted_rows,"
                " updated_rows, unchanged_rows, error_rows, details_json)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (
                    preview.file_name, now_db(), preview.total, len(new_clients),
                    len(updated), len(preview.unchanged),
                    len(preview.errors) + len(preview.duplicates), None,
                ),
            )
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        # oznacz czas ostatniego importu (poza transakcją, best-effort)
        stamp = now_db()
        ids = [c.external_id for c in new_clients] + [t.external_id for _e, t in updated]
        for ext in ids:
            self._conn.execute(
                "UPDATE clients SET last_import_at = ? WHERE external_id = ?", (stamp, ext)
            )
        self._conn.commit()
        _ = d_to_db  # (import użyty pośrednio przez repo)

    def set_client_photo(self, client: Client, source_path: str) -> None:
        """Kopiuje zdjęcie do data/photos/client_<external_id>.<ext> (DATABASE.md)."""
        src = Path(source_path)
        target = photos_dir() / f"client_{client.external_id}{src.suffix.lower()}"
        # usuń poprzednie zdjęcie o innym rozszerzeniu, żeby pliki się nie duplikowały
        for old in photos_dir().glob(f"client_{client.external_id}.*"):
            if old != target:
                old.unlink(missing_ok=True)
        shutil.copyfile(src, target)
        client.photo_path = str(target)
        self._clients.update(client)

    # --- zadania -------------------------------------------------------
    def client_tasks(self, client_id: int) -> list[Task]:
        return self._tasks.for_client(client_id)

    def dashboard_tasks(self) -> list[Task]:
        return self._tasks.dashboard()

    def add_task(self, task: Task) -> int:
        return self._tasks.insert(task)

    def update_task(self, task: Task) -> None:
        self._tasks.update(task)

    def delete_task(self, task_id: int) -> None:
        self._tasks.delete(task_id)

    def set_task_done(self, task: Task, done: bool) -> None:
        if done:
            task.status = "zakonczone"
            task.completed_at = datetime.now()
        else:
            task.status = "do_zrobienia"
            task.completed_at = None
        self._tasks.set_status(task.id, task.status, task.completed_at)

    # --- kontakty ------------------------------------------------------
    def client_contacts(self, client_id: int) -> list[Contact]:
        return self._contacts.for_client(client_id)

    def todays_meetings(self) -> list[Contact]:
        return self._contacts.meetings_on(date.today())

    def no_contact_over(self, days: int = 30) -> list[tuple[Client, Optional[int]]]:
        return [
            (self._clients.get(client_id), days_since)
            for client_id, days_since in self._contacts.no_contact_over(days)
        ]

    def requires_attention(self) -> list[Client]:
        return [c for c in self.active_clients() if c.requires_attention]

    def add_contact(self, contact: Contact) -> int:
        return self._contacts.insert(contact)

    def update_contact(self, contact: Contact) -> None:
        self._contacts.update(contact)

    def delete_contact(self, contact_id: int) -> None:
        self._contacts.delete(contact_id)

    # --- szkolenia -----------------------------------------------------
    def client_trainings(self, client_id: int) -> list[Training]:
        return self._trainings.for_client(client_id)

    def add_training(self, training: Training) -> int:
        return self._trainings.insert(training)

    def update_training(self, training: Training) -> None:
        self._trainings.update(training)

    def delete_training(self, training_id: int) -> None:
        self._trainings.delete(training_id)

    # --- kalendarz -----------------------------------------------------
    def calendar_events(self, start: date, end: date):
        return self._calendar.events_between(start, end)

    # --- analityka -----------------------------------------------------
    def activity_history(
        self, start: date, end: date, tasks: bool = True, contacts: bool = True, trainings: bool = True
    ):
        return self._analytics.activity_history(start, end, tasks, contacts, trainings)

    # --- notatki -------------------------------------------------------
    def add_note(self, note: Note) -> int:
        return self._notes.insert(note)

    def update_note(self, note: Note) -> None:
        self._notes.update(note)

    def delete_note(self, note_id: int) -> None:
        self._notes.delete(note_id)

    def raw_notes(self, client_id: int) -> list[Note]:
        return self._notes.for_client(client_id)

    def client_notes(self, client_id: int) -> list[tuple[datetime, str, str]]:
        """Notatki własne + notatki z kontaktów, od najnowszej."""
        items: list[tuple[datetime, str, str]] = []
        for n in self._notes.for_client(client_id):
            items.append((n.created_at, "Notatka", n.content))
        for c in self._contacts.for_client(client_id):
            if c.note:
                label = CONTACT_TYPE_LABELS.get(c.contact_type, c.contact_type)
                items.append((c.contact_at, f"Kontakt · {label}", c.note))
        items.sort(key=lambda item: item[0], reverse=True)
        return items
