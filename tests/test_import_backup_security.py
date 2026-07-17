"""Testy importu XLSX, kopii zapasowych i PIN."""
from __future__ import annotations

import dataclasses
import zipfile
from pathlib import Path

import pytest


def _make_xlsx(path: Path, rows: list[list]) -> None:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    wb.save(str(path))


HEADERS = ["ID klienta", "Imię", "Nazwisko", "Telefon", "CV"]


def test_import_preview_categories(store, tmp_path):
    from importers.xlsx_import import build_preview

    existing = store.find_by_external_id("AS-1031")
    xlsx = tmp_path / "imp.xlsx"
    _make_xlsx(xlsx, [
        HEADERS,
        ["AS-9000", "Jan", "Testowy", "111", "aktualne"],           # nowy
        ["AS-1024", "Anna", "Kowalska", "999888777", "aktualne"],    # aktualizacja (tel)
        ["AS-1031", existing.first_name, existing.last_name, existing.phone, "nieaktualne"],  # bez zmian
        ["AS-9000", "Jan", "Testowy", "", ""],                       # duplikat
        ["AS-9001", "", "BezImienia", "", ""],                       # błąd
    ])
    pv = build_preview(store, xlsx)
    assert [c.external_id for c in pv.new] == ["AS-9000"]
    assert [t.external_id for _e, t in pv.updated] == ["AS-1024"]
    assert [c.external_id for c in pv.unchanged] == ["AS-1031"]
    assert len(pv.duplicates) == 1
    assert len(pv.errors) == 1


def test_import_real_world_headers(store, tmp_path):
    """Nagłówki z realnego pliku: „ASII\\nLP." z łamaniem wiersza i długi nagłówek symboli."""
    from importers.xlsx_import import build_preview, parse_workbook

    real_headers = [
        "ASII\nLP.", "IMIĘ", "NAZWISKO", "DATA REKRUTACJI", "DATA IPD", "CV", "ZATRUDNIENIE",
        "DZ", "JC ", "RP", "PŁEĆ", "STOPIEŃ NIEPEŁNOSPRAWNOŚCI", "SYMBOL",
        "jeśli niepełnosprawność sprzężona wpisać symbole ręcznie", "WYKSZTAŁCENIE",
        "DATA WAŻNOŚCI ORZECZENIA", "POSZUKIWANA PRACA", "KOMENTARZ",
    ]
    xlsx = tmp_path / "real.xlsx"
    _make_xlsx(xlsx, [
        real_headers,
        ["AS-2001", "Jan", "Testowy", "2026-03-01", "", "aktualne", "bez pracy",
         "Tak", "Nie", "Nie", "Mężczyzna", "Umiarkowany", "05-R", "07-S", "Średnie",
         "2027-12-31", "Magazynier", "Uwagi"],
    ])
    parsed, errors = parse_workbook(xlsx)
    assert errors == []
    assert parsed[0]["external_id"] == "AS-2001"
    assert parsed[0]["combined_symbols"] == "07-S"
    assert parsed[0]["desired_job"] == "Magazynier"

    pv = build_preview(store, xlsx)
    assert [c.external_id for c in pv.new] == ["AS-2001"]


def test_import_dates_with_time_ranges(store, tmp_path):
    """Kolumny dat zawierające dołączony zakres godzin (realny format użytkownika)."""
    from importers.xlsx_import import _parse_date, build_preview

    from datetime import date

    assert _parse_date("01.04.2026 7:00-9:00") == date(2026, 4, 1)
    assert _parse_date("2.04.2026 7:00 -9:00") == date(2026, 4, 2)
    assert _parse_date("02.04.2026  7:00 - 10:00") == date(2026, 4, 2)
    assert _parse_date("1.04.2026 9:00-10:00") == date(2026, 4, 1)

    headers = ["ID klienta", "Imię", "Nazwisko", "DATA REKRUTACJI", "DATA IPD"]
    xlsx = tmp_path / "daty.xlsx"
    _make_xlsx(xlsx, [
        headers,
        ["AS-3001", "Jan", "Nowak", "01.04.2026 7:00-9:00", "08.04.2026 07:00-10:00"],
    ])
    pv = build_preview(store, xlsx)
    assert len(pv.errors) == 0
    assert pv.new[0].recruitment_date == date(2026, 4, 1)
    assert pv.new[0].ipd_date == date(2026, 4, 8)


def test_import_apply_does_not_touch_work_data(store, tmp_path):
    from importers.xlsx_import import build_preview

    cid = store.find_by_external_id("AS-1024").id
    tasks_before = len(store.client_tasks(cid))
    xlsx = tmp_path / "imp.xlsx"
    _make_xlsx(xlsx, [HEADERS, ["AS-1024", "Anna", "Kowalska", "555000111", "aktualne"]])
    pv = build_preview(store, xlsx)
    store.apply_import(pv)
    assert store.find_by_external_id("AS-1024").phone == "555000111"
    assert len(store.client_tasks(cid)) == tasks_before  # zadania nietknięte


def test_reimport_is_idempotent(store, tmp_path):
    from importers.xlsx_import import build_preview

    xlsx = tmp_path / "imp.xlsx"
    _make_xlsx(xlsx, [HEADERS, ["AS-9000", "Jan", "Testowy", "111", "aktualne"]])
    store.apply_import(build_preview(store, xlsx))
    pv2 = build_preview(store, xlsx)
    assert pv2.new == [] and pv2.updated == []


def test_backup_contains_db_and_restores(store, tmp_path):
    from services.backup import create_backup, restore_backup

    store.checkpoint()
    archive = create_backup()
    with zipfile.ZipFile(archive) as zf:
        assert any(n.endswith("client_workbench.db") for n in zf.namelist())

    cid = store.find_by_external_id("AS-1024").id
    original = store.client(cid).phone
    store.update_client(dataclasses.replace(store.client(cid), phone="000"))
    assert store.client(cid).phone == "000"

    store.close()
    restore_backup(archive)
    store.reopen()
    assert store.find_by_external_id("AS-1024").phone == original


def test_backup_retention(store):
    from services.backup import BACKUP_PREFIX, backups_dir, list_backups, _prune_old

    d = backups_dir()
    for i in range(15):
        (d / f"{BACKUP_PREFIX}2020-01-{i:02d}_10-00.zip").write_bytes(b"x")
    _prune_old()
    assert len(list_backups()) == 10


def test_pin_hash_and_verify(store):
    sec = store.security
    assert not sec.has_pin()
    with pytest.raises(ValueError):
        sec.set_pin("12")
    sec.set_pin("2468")
    assert sec.verify_pin("2468")
    assert not sec.verify_pin("0000")
    row = store._conn.execute("SELECT value FROM settings WHERE key='pin_hash'").fetchone()
    assert "2468" not in row["value"]  # przechowywany jest hash, nie jawny PIN


def test_idle_lock_default(store):
    assert store.security.idle_lock_minutes() == 5
    store.security.set_idle_lock_minutes(2)
    assert store.security.idle_lock_minutes() == 2
