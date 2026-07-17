"""Repozytorium analityki — historia działań w okresie (zadania/kontakty/szkolenia)."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime

from models.entities import (
    ActivityRow,
    CONTACT_TYPE_LABELS,
    TASK_STATUS_LABELS,
    TRAINING_STATUS_LABELS,
    TRAINING_TYPE_LABELS,
)


class AnalyticsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def activity_history(
        self,
        start: date,
        end: date,
        include_tasks: bool = True,
        include_contacts: bool = True,
        include_trainings: bool = True,
    ) -> list[ActivityRow]:
        start_s = start.isoformat()
        end_dt = datetime.combine(end, datetime.max.time()).isoformat(timespec="seconds")
        rows: list[ActivityRow] = []

        def client_name(r: sqlite3.Row) -> str:
            return f"{r['first_name']} {r['last_name']}"

        if include_tasks:
            for r in self._conn.execute(
                """
                SELECT t.title, t.due_at, t.status,
                       c.id AS client_id, c.external_id, c.first_name, c.last_name
                FROM tasks t JOIN clients c ON c.id = t.client_id
                WHERE t.due_at IS NOT NULL AND t.due_at >= ? AND t.due_at <= ?
                """,
                (start_s, end_dt),
            ):
                rows.append(
                    ActivityRow(
                        when=datetime.fromisoformat(r["due_at"]),
                        client_id=r["client_id"], external_id=r["external_id"],
                        client_name=client_name(r), kind="zadanie",
                        description=r["title"],
                        status=TASK_STATUS_LABELS.get(r["status"], r["status"]),
                        has_time=True,
                    )
                )

        if include_contacts:
            for r in self._conn.execute(
                """
                SELECT ct.contact_type, ct.contact_at, ct.status, ct.note,
                       c.id AS client_id, c.external_id, c.first_name, c.last_name
                FROM contacts ct JOIN clients c ON c.id = ct.client_id
                WHERE ct.contact_at >= ? AND ct.contact_at <= ?
                """,
                (start_s, end_dt),
            ):
                label = CONTACT_TYPE_LABELS.get(r["contact_type"], r["contact_type"])
                desc = label + (f" — {r['note']}" if r["note"] else "")
                rows.append(
                    ActivityRow(
                        when=datetime.fromisoformat(r["contact_at"]),
                        client_id=r["client_id"], external_id=r["external_id"],
                        client_name=client_name(r), kind="kontakt",
                        description=desc, status=str(r["status"]).capitalize(),
                        has_time=True,
                    )
                )

        if include_trainings:
            for r in self._conn.execute(
                """
                SELECT tr.name, tr.training_date, tr.training_type, tr.status,
                       c.id AS client_id, c.external_id, c.first_name, c.last_name
                FROM trainings tr JOIN clients c ON c.id = tr.client_id
                WHERE tr.training_date >= ? AND tr.training_date <= ?
                """,
                (start_s, end.isoformat()),
            ):
                type_label = TRAINING_TYPE_LABELS.get(r["training_type"], r["training_type"])
                rows.append(
                    ActivityRow(
                        when=datetime.combine(
                            date.fromisoformat(r["training_date"]), datetime.min.time()
                        ),
                        client_id=r["client_id"], external_id=r["external_id"],
                        client_name=client_name(r), kind="szkolenie",
                        description=f"{r['name']} ({type_label})",
                        status=TRAINING_STATUS_LABELS.get(r["status"], r["status"]),
                        has_time=False,
                    )
                )

        rows.sort(key=lambda a: a.when, reverse=True)
        return rows
