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
from repositories.calendar import CalendarRepository
from repositories.clients import ClientRepository


class DataStore:
    def __init__(self, conn: Optional[sqlite3.Connection] = None) -> None:
        self._conn = conn or open_connection()
        self._clients = ClientRepository(self._conn)
        self._tasks = TaskRepository(self._conn)
        self._contacts = ContactRepository(self._conn)
        self._trainings = TrainingRepository(self._conn)
        self._notes = NoteRepository(self._conn)
        self._calendar = CalendarRepository(self._conn)

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

    # --- szkolenia -----------------------------------------------------
    def client_trainings(self, client_id: int) -> list[Training]:
        return self._trainings.for_client(client_id)

    def add_training(self, training: Training) -> int:
        return self._trainings.insert(training)

    # --- kalendarz -----------------------------------------------------
    def calendar_events(self, start: date, end: date):
        return self._calendar.events_between(start, end)

    # --- notatki -------------------------------------------------------
    def add_note(self, note: Note) -> int:
        return self._notes.insert(note)

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
