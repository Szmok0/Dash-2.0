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
        ["AS-9000", "Jan", "Testowy", "", ""],                       # duplikat ID w pliku
        ["AS-9001", "", "BezImienia", "", ""],                       # nowy (samo nazwisko — też wchodzi)
        ["", "Ktoś", "BezID", "", ""],                               # błąd: brak ID
    ])
    pv = build_preview(store, xlsx)
    assert [c.external_id for c in pv.new] == ["AS-9000", "AS-9001"]
    assert [t.external_id for _e, t in pv.updated] == ["AS-1024"]
    assert [c.external_id for c in pv.unchanged] == ["AS-1031"]
    assert len(pv.duplicates) == 1
    assert len(pv.errors) == 1  # tylko wiersz bez ID


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


def test_import_cv_three_states(store, tmp_path):
    """CV: brak CV / CV do poprawy / CV aktualne oraz numeryczne ID."""
    from importers.xlsx_import import _clean_id, build_preview

    assert _clean_id(1.0) == "1"
    assert _clean_id("12.0") == "12"
    assert _clean_id(7) == "7"

    xlsx = tmp_path / "cv.xlsx"
    _make_xlsx(xlsx, [
        ["ID klienta", "Imię", "Nazwisko", "CV"],
        ["CV-1", "A", "B", "brak CV"],
        ["CV-2", "C", "D", "CV do poprawy"],
        ["CV-3", "E", "F", "CV aktualne"],
    ])
    pv = build_preview(store, xlsx)
    cvs = {c.external_id: c.cv_status for c in pv.new}
    assert cvs == {"CV-1": "brak", "CV-2": "do_poprawy", "CV-3": "aktualne"}


def test_import_bad_date_does_not_drop_client(store, tmp_path):
    """Błędna data w wierszu NIE może wyrzucać całego klienta (brak dziur w numeracji)."""
    from importers.xlsx_import import build_preview

    headers = ["ASII LP.", "IMIĘ", "NAZWISKO", "DATA REKRUTACJI", "DATA IPD"]
    rows = [headers]
    for i in range(1, 21):
        rec = "b.d." if i in (3, 10, 17) else "01.04.2026 7:00-9:00"  # 3 błędne daty
        rows.append([i, f"Imie{i}", f"Nazwisko{i}", rec, ""])
    xlsx = tmp_path / "bez_dziur.xlsx"
    _make_xlsx(xlsx, rows)

    pv = build_preview(store, xlsx)
    assert len(pv.new) == 20  # wszystkie 20 wchodzi mimo błędnych dat
    assert len(pv.errors) == 0
    store.apply_import(pv)
    ids = sorted(int(c.external_id) for c in store.clients if c.external_id.isdigit())
    assert ids == list(range(1, 21))  # brak dziur
    assert store.find_by_external_id("3").recruitment_date is None  # tylko data pominięta


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


def test_import_skips_phantom_id_only_rows(store, tmp_path):
    """Wiersze z samym numerem LP (bez nazwiska i danych) nie tworzą klientów-widm."""
    from importers.xlsx_import import build_preview

    xlsx = tmp_path / "widma.xlsx"
    _make_xlsx(xlsx, [
        ["ASII LP.", "IMIĘ", "NAZWISKO", "TELEFON"],
        ["101", "Jan", "Nowak", "111"],
        ["102", "Anna", "Kowalska", "222"],
        ["103", "", "", ""],   # sam numer LP — widmo, pomijamy
        ["104", "", "", ""],   # sam numer LP — widmo, pomijamy
        ["105", "", "", "500600700"],  # bez nazwiska, ale z telefonem — zostaje
    ])
    pv = build_preview(store, xlsx)
    assert [c.external_id for c in pv.new] == ["101", "102", "105"]
    assert pv.new[-1].last_name == "(bez nazwiska)"


def test_blank_clients_excluded_from_list_and_count(store):
    """Klienci-widma (bez nazwiska i danych) nie liczą się na liście ani w liczniku aktywnych."""
    from models.entities import Client

    before = len(store.clients)
    before_active = len(store.active_clients())

    store.add_client(Client(id=0, external_id="Z-999", first_name="", last_name=""))  # widmo
    assert len(store.clients) == before
    assert len(store.active_clients()) == before_active

    # realny klient bez nazwiska, ale z telefonem — widoczny i liczony
    store.add_client(Client(id=0, external_id="Z-1000", first_name="", last_name="", phone="500"))
    assert len(store.clients) == before + 1
    assert len(store.active_clients()) == before_active + 1


def test_dm_aneks_roundtrip(store):
    """Nowe pola DM/Aneks zapisują się i odczytują z bazy."""
    from models.entities import Client

    cid = store.add_client(
        Client(id=0, external_id="DA-1", first_name="Test", last_name="Aneksowy",
               dm="Tak", aneks="Nie")
    )
    got = store.client(cid)
    assert got.dm == "Tak"
    assert got.aneks == "Nie"


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
