"""Repozytorium kalendarza — wydarzenia z zadań, kontaktów i szkoleń w zakresie dat."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime

from models.entities import CONTACT_TYPE_LABELS, CalendarEvent


class CalendarRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def events_between(self, start: date, end: date) -> list[CalendarEvent]:
        """Wszystkie wydarzenia w [start, end] (włącznie). end liczony do 23:59:59."""
        start_s = start.isoformat()
        end_dt = datetime.combine(end, datetime.max.time()).isoformat(timespec="seconds")
        events: list[CalendarEvent] = []

        # zadania — po terminie (due_at)
        for row in self._conn.execute(
            """
            SELECT t.title, t.due_at, c.id AS client_id, c.last_name, c.first_name
            FROM tasks t JOIN clients c ON c.id = t.client_id
            WHERE t.due_at IS NOT NULL AND t.due_at >= ? AND t.due_at <= ?
            """,
            (start_s, end_dt),
        ):
            when = datetime.fromisoformat(row["due_at"])
            events.append(
                CalendarEvent(
                    client_id=row["client_id"], last_name=row["last_name"],
                    first_name=row["first_name"], kind="zadanie",
                    label=f"Zadanie: {row['title']}", when=when, has_time=True,
                )
            )

        # kontakty (w tym spotkania)
        for row in self._conn.execute(
            """
            SELECT ct.contact_type, ct.contact_at, c.id AS client_id, c.last_name, c.first_name
            FROM contacts ct JOIN clients c ON c.id = ct.client_id
            WHERE ct.contact_at >= ? AND ct.contact_at <= ?
            """,
            (start_s, end_dt),
        ):
            when = datetime.fromisoformat(row["contact_at"])
            label = CONTACT_TYPE_LABELS.get(row["contact_type"], row["contact_type"])
            events.append(
                CalendarEvent(
                    client_id=row["client_id"], last_name=row["last_name"],
                    first_name=row["first_name"], kind="kontakt",
                    label=label, when=when, has_time=True,
                )
            )

        # szkolenia — tylko data
        for row in self._conn.execute(
            """
            SELECT tr.name, tr.training_date, c.id AS client_id, c.last_name, c.first_name
            FROM trainings tr JOIN clients c ON c.id = tr.client_id
            WHERE tr.training_date >= ? AND tr.training_date <= ?
            """,
            (start_s, end.isoformat()),
        ):
            when = datetime.combine(date.fromisoformat(row["training_date"]), datetime.min.time())
            events.append(
                CalendarEvent(
                    client_id=row["client_id"], last_name=row["last_name"],
                    first_name=row["first_name"], kind="szkolenie",
                    label=f"Szkolenie: {row['name']}", when=when, has_time=False,
                )
            )

        events.sort(key=lambda e: e.when)
        return events
