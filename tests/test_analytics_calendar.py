"""Testy serwisu analityki, kalendarza i eksporterów."""
from __future__ import annotations

from datetime import date, timedelta


def test_filter_clients_by_status(store):
    from services.analytics import AnalyticsService, ClientFilter

    svc = AnalyticsService(store)
    assert len(svc.filter_clients(ClientFilter())) == 6
    assert len(svc.filter_clients(ClientFilter(client_status="aktywny"))) == 5
    cv = svc.filter_clients(ClientFilter(cv_status="aktualne"))
    assert all(r.client.cv_status == "aktualne" for r in cv)


def test_filter_clients_requires_activity(store):
    from services.analytics import AnalyticsService, ClientFilter

    svc = AnalyticsService(store)
    with_tr = svc.filter_clients(ClientFilter(has_trainings=True))
    assert all(r.training_count > 0 for r in with_tr)


def test_activity_history_sorted_desc(store):
    from services.analytics import AnalyticsService, HistoryFilter

    svc = AnalyticsService(store)
    flt = HistoryFilter(start=date.today() - timedelta(days=60), end=date.today() + timedelta(days=60))
    rows = svc.activity_history(flt)
    assert rows
    assert rows == sorted(rows, key=lambda a: a.when, reverse=True)
    assert {"zadanie", "kontakt", "szkolenie"} == {a.kind for a in rows}


def test_calendar_events_trainings_have_no_time(store):
    today = date.today()
    events = store.calendar_events(today - timedelta(days=40), today + timedelta(days=40))
    trainings = [e for e in events if e.kind == "szkolenie"]
    assert trainings and all(not e.has_time for e in trainings)


def test_exporters_create_files(store, tmp_path, monkeypatch):
    monkeypatch.setenv("CW_DATA_DIR", str(tmp_path))
    from exporters.table_export import TableData, export_csv, export_pdf, export_xlsx

    table = TableData("Test", ["A", "B"], [["1", "Ćma"], ["2", "Żółw"]])
    for fn in (export_csv, export_xlsx, export_pdf):
        path = fn(table)
        assert path.exists() and path.stat().st_size > 0


def test_client_card_pdf(store, tmp_path, monkeypatch):
    monkeypatch.setenv("CW_DATA_DIR", str(tmp_path))
    from exporters.client_pdf import export_client_card_pdf

    cid = store.find_by_external_id("AS-1024").id
    path = export_client_card_pdf(store, cid)
    assert path.exists() and path.stat().st_size > 1000
