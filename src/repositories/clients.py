"""Repozytorium klientów."""
from __future__ import annotations

import sqlite3
from typing import Optional

from models.entities import Client
from repositories.mappers import client_from_row, d_to_db, now_db, photo_to_db

_FIELDS = (
    "external_id, first_name, last_name, phone, email, recruitment_date, ipd_date, "
    "cv_status, ipd_status, employment_status, internship_status, client_status, "
    "dz, jc, rp, psychologist, lawyer, gender, disability_degree, disability_symbol, "
    "combined_symbols, education, certificate_valid_until, desired_job, import_comment, "
    "requires_attention, attention_note, photo_path"
)


def _values(c: Client) -> tuple:
    return (
        c.external_id, c.first_name, c.last_name, c.phone or None, c.email or None,
        d_to_db(c.recruitment_date), d_to_db(c.ipd_date),
        c.cv_status, c.ipd_status, c.employment_status, c.internship_status, c.client_status,
        c.dz or None, c.jc or None, c.rp or None, c.psychologist or None, c.lawyer or None,
        c.gender or None, c.disability_degree or None, c.disability_symbol or None,
        c.combined_symbols or None, c.education or None, d_to_db(c.certificate_valid_until),
        c.desired_job or None, c.import_comment or None,
        int(c.requires_attention), c.attention_note or None, photo_to_db(c.photo_path),
    )


class ClientRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list_all(self, search: str = "") -> list[Client]:
        sql = "SELECT * FROM clients"
        params: tuple = ()
        if search:
            sql += (
                " WHERE external_id LIKE ? OR first_name LIKE ? OR last_name LIKE ?"
                " OR (first_name || ' ' || last_name) LIKE ?"
            )
            like = f"%{search}%"
            params = (like, like, like, like)
        sql += " ORDER BY last_name, first_name"
        return [client_from_row(r) for r in self._conn.execute(sql, params)]

    def get(self, client_id: int) -> Client:
        row = self._conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        if row is None:
            raise KeyError(f"Brak klienta o id={client_id}")
        return client_from_row(row)

    def get_by_external_id(self, external_id: str) -> Optional[Client]:
        row = self._conn.execute(
            "SELECT * FROM clients WHERE external_id = ?", (external_id,)
        ).fetchone()
        return client_from_row(row) if row else None

    def insert(self, client: Client) -> int:
        now = now_db()
        placeholders = ", ".join("?" for _ in _FIELDS.split(", "))
        cur = self._conn.execute(
            f"INSERT INTO clients ({_FIELDS}, created_at, updated_at)"
            f" VALUES ({placeholders}, ?, ?)",
            _values(client) + (now, now),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def update(self, client: Client) -> None:
        assignments = ", ".join(f"{name} = ?" for name in _FIELDS.split(", "))
        self._conn.execute(
            f"UPDATE clients SET {assignments}, updated_at = ? WHERE id = ?",
            _values(client) + (now_db(), client.id),
        )
        self._conn.commit()
