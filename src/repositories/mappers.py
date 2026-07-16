"""Konwersje wierszy SQLite <-> encje oraz dat ISO <-> obiekty Pythona."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime
from typing import Optional

from config import data_dir
from models.entities import Client, Contact, Note, Task, Training


def dt_to_db(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat(timespec="seconds") if value else None


def dt_from_db(value: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(value) if value else None


def d_to_db(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def d_from_db(value: Optional[str]) -> Optional[date]:
    return date.fromisoformat(value) if value else None


def now_db() -> str:
    return datetime.now().isoformat(timespec="seconds")


def photo_to_db(abs_path: Optional[str]) -> Optional[str]:
    """Bezwzględna ścieżka zdjęcia -> względna wobec katalogu danych."""
    if not abs_path:
        return None
    try:
        from pathlib import Path

        return str(Path(abs_path).relative_to(data_dir()))
    except ValueError:
        return abs_path


def photo_from_db(rel_path: Optional[str]) -> Optional[str]:
    if not rel_path:
        return None
    from pathlib import Path

    p = Path(rel_path)
    return str(p if p.is_absolute() else data_dir() / p)


def client_from_row(row: sqlite3.Row) -> Client:
    return Client(
        id=row["id"],
        external_id=row["external_id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        phone=row["phone"] or "",
        email=row["email"] or "",
        recruitment_date=d_from_db(row["recruitment_date"]),
        ipd_date=d_from_db(row["ipd_date"]),
        cv_status=row["cv_status"],
        ipd_status=row["ipd_status"],
        employment_status=row["employment_status"],
        internship_status=row["internship_status"],
        client_status=row["client_status"],
        dz=row["dz"] or "",
        jc=row["jc"] or "",
        rp=row["rp"] or "",
        psychologist=row["psychologist"] or "",
        lawyer=row["lawyer"] or "",
        gender=row["gender"] or "",
        disability_degree=row["disability_degree"] or "",
        disability_symbol=row["disability_symbol"] or "",
        combined_symbols=row["combined_symbols"] or "",
        education=row["education"] or "",
        certificate_valid_until=d_from_db(row["certificate_valid_until"]),
        desired_job=row["desired_job"] or "",
        import_comment=row["import_comment"] or "",
        requires_attention=bool(row["requires_attention"]),
        attention_note=row["attention_note"] or "",
        photo_path=photo_from_db(row["photo_path"]),
    )


def task_from_row(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        client_id=row["client_id"],
        title=row["title"],
        due_at=dt_from_db(row["due_at"]),
        priority=row["priority"],
        status=row["status"],
        note=row["note"] or "",
        action_type=row["action_type"] or "notatka",
        completed_at=dt_from_db(row["completed_at"]),
    )


def contact_from_row(row: sqlite3.Row) -> Contact:
    return Contact(
        id=row["id"],
        client_id=row["client_id"],
        contact_type=row["contact_type"],
        contact_at=dt_from_db(row["contact_at"]),
        status=row["status"],
        note=row["note"] or "",
    )


def training_from_row(row: sqlite3.Row) -> Training:
    return Training(
        id=row["id"],
        client_id=row["client_id"],
        name=row["name"],
        training_date=d_from_db(row["training_date"]),
        training_type=row["training_type"],
        status=row["status"],
        note=row["note"] or "",
    )


def note_from_row(row: sqlite3.Row) -> Note:
    return Note(
        id=row["id"],
        client_id=row["client_id"],
        content=row["content"],
        created_at=dt_from_db(row["created_at"]),
    )
