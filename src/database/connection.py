"""Połączenie SQLite: PRAGMA foreign_keys, WAL, inicjalizacja schematu."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from config import db_path

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def open_connection(path: Path | None = None) -> sqlite3.Connection:
    """Otwiera bazę (tworzy plik i schemat przy pierwszym uruchomieniu)."""
    conn = sqlite3.connect(str(path or db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    return conn
