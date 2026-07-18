"""Połączenie SQLite: PRAGMA foreign_keys, WAL, inicjalizacja schematu."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from config import db_path, resource_path

# schemat: w repozytorium obok modułu, w EXE bundlowany do database/schema.sql
_LOCAL_SCHEMA = Path(__file__).resolve().parent / "schema.sql"
SCHEMA_PATH = _LOCAL_SCHEMA if _LOCAL_SCHEMA.exists() else resource_path("database", "schema.sql")


def open_connection(path: Path | None = None) -> sqlite3.Connection:
    """Otwiera bazę (tworzy plik i schemat przy pierwszym uruchomieniu)."""
    conn = sqlite3.connect(str(path or db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    _migrate(conn)
    conn.commit()
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Lekkie migracje: dodaje brakujące kolumny do istniejących baz (bez utraty danych)."""
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(clients)")}
    for column in ("dm", "aneks"):
        if column not in existing:
            conn.execute(f"ALTER TABLE clients ADD COLUMN {column} TEXT")
