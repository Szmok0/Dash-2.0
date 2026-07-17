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
    assert "AS-1052" in result  # brak kontaktów
    assert "AS-1031" in result  # ostatni kontakt 41 dni temu


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
