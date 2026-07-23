"""Testy DataStore: klienci, dashboard, kontakty, zadania."""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from models.entities import Client, Contact, Task


def test_seed_counts(store):
    assert len(store.clients) == 6
    assert len(store.active_clients()) == 5


def test_search_by_id_and_name(store):
    assert len(store.search_clients("Kowal")) == 1
    assert len(store.search_clients("AS-10")) == 6
    assert store.search_clients("nieistnieje") == []


def test_unique_external_id(store):
    store.add_client(Client(id=0, external_id="X-1", first_name="A", last_name="B"))
    with pytest.raises(Exception):
        store.add_client(Client(id=0, external_id="X-1", first_name="C", last_name="D"))


def test_dashboard_open_tasks_only_active(store):
    tasks = store.dashboard_tasks()
    # zamknięty klient (AS-1060) nie pojawia się na dashboardzie
    closed = store.find_by_external_id("AS-1060")
    assert all(t.client_id != closed.id for t in tasks)


def test_task_completion_persists(store):
    cid = store.find_by_external_id("AS-1024").id
    tid = store.add_task(Task(id=0, client_id=cid, title="T", due_at=datetime.now(),
                              priority="wysoki", status="do_zrobienia"))
    task = next(t for t in store.client_tasks(cid) if t.id == tid)
    store.set_task_done(task, True)
    reloaded = next(t for t in store.client_tasks(cid) if t.id == tid)
    assert reloaded.status == "zakonczone" and reloaded.completed_at is not None


def test_no_contact_over_30_includes_clients_without_contacts(store):
    result = {c.external_id for c, _ in store.no_contact_over(30)}
    assert "AS-1052" in result      # brak kontaktów, bez pracy → obecny
    assert "AS-1031" not in result  # na stażu (w_trakcie) → wykluczony regułą


def test_follow_up_days_default_and_validation(store):
    assert store.follow_up_days() == 30  # brak ustawienia → domyślnie 30
    store.set_setting("follow_up_days", "14")
    assert store.follow_up_days() == 14
    for bad in ("0", "-5", "999", "abc", ""):
        store.set_setting("follow_up_days", bad)
        assert store.follow_up_days() == 30  # poza zakresem / nieparsowalne → 30


def test_no_contact_over_respects_threshold(store):
    cid = store.add_client(Client(id=0, external_id="THR-1", first_name="Pro", last_name="Gowy"))
    store.add_contact(Contact(id=0, client_id=cid, contact_type="telefon",
                              contact_at=datetime.now() - timedelta(days=41),
                              status="odbyty", note=""))
    ids_30 = {c.external_id for c, _ in store.no_contact_over(30)}
    ids_50 = {c.external_id for c, _ in store.no_contact_over(50)}
    assert "THR-1" in ids_30       # kontakt 41 dni temu, próg 30 → obecny
    assert "THR-1" not in ids_50   # 41 < próg 50 → nieobecny


def test_no_contact_over_excludes_employed_and_interns(store):
    store.add_client(Client(id=0, external_id="EMP-1", first_name="Za", last_name="Trudniony",
                            employment_status="zatrudniony"))
    store.add_client(Client(id=0, external_id="STA-1", first_name="Na", last_name="Stazu",
                            internship_status="w_trakcie"))
    store.add_client(Client(id=0, external_id="FREE-1", first_name="Bez", last_name="Pracy"))
    ids = {c.external_id for c, _ in store.no_contact_over(30)}
    assert "FREE-1" in ids       # kontrolny: bez pracy, bez kontaktów → obecny
    assert "EMP-1" not in ids    # zatrudniony → wykluczony
    assert "STA-1" not in ids    # na stażu → wykluczony


def test_notes_aggregate_contacts(store):
    cid = store.find_by_external_id("AS-1024").id
    before = len(store.client_notes(cid))
    store.add_contact(Contact(id=0, client_id=cid, contact_type="telefon",
                              contact_at=datetime.now(), status="odbyty", note="z kontaktu"))
    after = store.client_notes(cid)
    assert len(after) == before + 1
    assert any("z kontaktu" in content for _dt, _src, content in after)


def test_edit_and_delete_task(store):
    cid = store.find_by_external_id("AS-1024").id
    tid = store.add_task(Task(id=0, client_id=cid, title="Stary", due_at=datetime.now(),
                              priority="niski", status="do_zrobienia"))
    task = next(t for t in store.client_tasks(cid) if t.id == tid)
    task.title = "Nowy"
    store.update_task(task)
    assert next(t for t in store.client_tasks(cid) if t.id == tid).title == "Nowy"
    store.delete_task(tid)
    assert tid not in [t.id for t in store.client_tasks(cid)]
