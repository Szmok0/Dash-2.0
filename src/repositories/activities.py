"""Repozytoria zadań, kontaktów, szkoleń i notatek."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from typing import Optional

from models.entities import Contact, Note, Task, Training
from repositories.mappers import (
    contact_from_row,
    d_to_db,
    dt_to_db,
    note_from_row,
    now_db,
    task_from_row,
    training_from_row,
)


class TaskRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def for_client(self, client_id: int) -> list[Task]:
        rows = self._conn.execute(
            "SELECT * FROM tasks WHERE client_id = ? ORDER BY due_at IS NULL, due_at",
            (client_id,),
        )
        return [task_from_row(r) for r in rows]

    def dashboard(self) -> list[Task]:
        """Otwarte zadania aktywnych klientów + zakończone/anulowane z dzisiaj."""
        today = date.today().isoformat()
        rows = self._conn.execute(
            """
            SELECT t.* FROM tasks t
            JOIN clients c ON c.id = t.client_id
            WHERE c.client_status = 'aktywny'
              AND (
                    t.status NOT IN ('zakonczone', 'anulowane')
                 OR (t.completed_at IS NOT NULL AND date(t.completed_at) = ?)
              )
            ORDER BY (t.status = 'zakonczone'),
                     CASE t.priority WHEN 'wysoki' THEN 0 WHEN 'sredni' THEN 1 ELSE 2 END,
                     t.due_at IS NULL, t.due_at
            """,
            (today,),
        )
        return [task_from_row(r) for r in rows]

    def insert(self, task: Task) -> int:
        now = now_db()
        cur = self._conn.execute(
            "INSERT INTO tasks (client_id, title, action_type, due_at, priority, status,"
            " note, completed_at, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                task.client_id, task.title, task.action_type, dt_to_db(task.due_at),
                task.priority, task.status, task.note or None,
                dt_to_db(task.completed_at), now, now,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def set_status(self, task_id: int, status: str, completed_at: Optional[datetime]) -> None:
        self._conn.execute(
            "UPDATE tasks SET status = ?, completed_at = ?, updated_at = ? WHERE id = ?",
            (status, dt_to_db(completed_at), now_db(), task_id),
        )
        self._conn.commit()

    def update(self, task: Task) -> None:
        self._conn.execute(
            "UPDATE tasks SET title=?, action_type=?, due_at=?, priority=?, status=?,"
            " note=?, completed_at=?, updated_at=? WHERE id=?",
            (
                task.title, task.action_type, dt_to_db(task.due_at), task.priority,
                task.status, task.note or None, dt_to_db(task.completed_at), now_db(), task.id,
            ),
        )
        self._conn.commit()

    def delete(self, task_id: int) -> None:
        self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()


class ContactRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def for_client(self, client_id: int) -> list[Contact]:
        rows = self._conn.execute(
            "SELECT * FROM contacts WHERE client_id = ? ORDER BY contact_at DESC",
            (client_id,),
        )
        return [contact_from_row(r) for r in rows]

    def meetings_on(self, day: date) -> list[Contact]:
        rows = self._conn.execute(
            """
            SELECT ct.* FROM contacts ct
            JOIN clients c ON c.id = ct.client_id
            WHERE ct.contact_type = 'spotkanie' AND date(ct.contact_at) = ?
              AND c.client_status = 'aktywny'
            ORDER BY ct.contact_at
            """,
            (day.isoformat(),),
        )
        return [contact_from_row(r) for r in rows]

    def no_contact_over(self, days: int) -> list[tuple[int, Optional[int]]]:
        """(client_id, dni od ostatniego kontaktu | None gdy brak kontaktów)."""
        now = datetime.now()
        threshold = dt_to_db(now - timedelta(days=days))
        rows = self._conn.execute(
            """
            SELECT c.id AS client_id, MAX(ct.contact_at) AS last_at
            FROM clients c
            LEFT JOIN contacts ct ON ct.client_id = c.id AND ct.contact_at <= ?
            WHERE c.client_status = 'aktywny'
              AND c.employment_status <> 'zatrudniony'
              AND c.internship_status <> 'w_trakcie'
            GROUP BY c.id
            HAVING last_at IS NULL OR last_at < ?
            """,
            (dt_to_db(now), threshold),
        )
        result: list[tuple[int, Optional[int]]] = []
        for row in rows:
            if row["last_at"] is None:
                result.append((row["client_id"], None))
            else:
                last = datetime.fromisoformat(row["last_at"])
                result.append((row["client_id"], (now - last).days))
        result.sort(key=lambda item: -(item[1] if item[1] is not None else 9999))
        return result

    def insert(self, contact: Contact) -> int:
        now = now_db()
        cur = self._conn.execute(
            "INSERT INTO contacts (client_id, contact_type, contact_at, status, note,"
            " created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (
                contact.client_id, contact.contact_type, dt_to_db(contact.contact_at),
                contact.status, contact.note or None, now, now,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def update(self, contact: Contact) -> None:
        self._conn.execute(
            "UPDATE contacts SET contact_type=?, contact_at=?, status=?, note=?, updated_at=?"
            " WHERE id=?",
            (
                contact.contact_type, dt_to_db(contact.contact_at), contact.status,
                contact.note or None, now_db(), contact.id,
            ),
        )
        self._conn.commit()

    def delete(self, contact_id: int) -> None:
        self._conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self._conn.commit()


class TrainingRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def for_client(self, client_id: int) -> list[Training]:
        rows = self._conn.execute(
            "SELECT * FROM trainings WHERE client_id = ? ORDER BY training_date DESC",
            (client_id,),
        )
        return [training_from_row(r) for r in rows]

    def insert(self, training: Training) -> int:
        now = now_db()
        cur = self._conn.execute(
            "INSERT INTO trainings (client_id, name, training_date, training_type, status,"
            " note, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                training.client_id, training.name, d_to_db(training.training_date),
                training.training_type, training.status, training.note or None, now, now,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def update(self, training: Training) -> None:
        self._conn.execute(
            "UPDATE trainings SET name=?, training_date=?, training_type=?, status=?, note=?,"
            " updated_at=? WHERE id=?",
            (
                training.name, d_to_db(training.training_date), training.training_type,
                training.status, training.note or None, now_db(), training.id,
            ),
        )
        self._conn.commit()

    def delete(self, training_id: int) -> None:
        self._conn.execute("DELETE FROM trainings WHERE id = ?", (training_id,))
        self._conn.commit()


class NoteRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def for_client(self, client_id: int) -> list[Note]:
        rows = self._conn.execute(
            "SELECT * FROM notes WHERE client_id = ? ORDER BY created_at DESC",
            (client_id,),
        )
        return [note_from_row(r) for r in rows]

    def insert(self, note: Note) -> int:
        now = now_db()
        cur = self._conn.execute(
            "INSERT INTO notes (client_id, content, created_at, updated_at) VALUES (?,?,?,?)",
            (note.client_id, note.content, dt_to_db(note.created_at) or now, now),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def update(self, note: Note) -> None:
        self._conn.execute(
            "UPDATE notes SET content=?, updated_at=? WHERE id=?",
            (note.content, now_db(), note.id),
        )
        self._conn.commit()

    def delete(self, note_id: int) -> None:
        self._conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self._conn.commit()
