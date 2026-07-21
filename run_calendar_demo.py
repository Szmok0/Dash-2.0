"""Samodzielny podgląd modułu Kalendarz z danymi testowymi.

Uruchomienie:
    python run_calendar_demo.py

Pokazuje widok Miesiąca (klik dnia otwiera panel z pełną listą wpisów) oraz
widok Tygodnia (poziomy scroll przez wszystkie 7 dni). Klik wpisu wypisuje w
konsoli, do którego klienta prowadziłby w pełnej aplikacji.
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from typing import List

from PySide6.QtWidgets import QApplication

from src.models.calendar_event import CalendarEvent, EventKind
from src.ui.pages.calendar_page import CalendarPage


def _sample_events() -> List[CalendarEvent]:
    """Dane testowe rozłożone wokół dzisiejszej daty."""
    base = date.today()
    monday = base - timedelta(days=base.weekday())
    names = [
        (101, "Kowalski Jan"), (102, "Nowak Anna"), (103, "Wiśniewski Piotr"),
        (104, "Wójcik Maria"), (105, "Kamiński Tomasz"), (106, "Lewandowska Ewa"),
        (107, "Zieliński Marek"), (108, "Szymańska Kinga"),
    ]

    def ev(day_offset: int, hour: int, minute: int, kind: EventKind,
           who: int, title: str = "", all_day: bool = False) -> CalendarEvent:
        cid, cname = names[who % len(names)]
        when = datetime.combine(monday + timedelta(days=day_offset), datetime.min.time())
        when = when.replace(hour=hour, minute=minute)
        return CalendarEvent(cid, cname, kind, when, title, all_day)

    events = [
        ev(0, 9, 0, EventKind.MEETING, 0, "Spotkanie wstępne"),
        ev(0, 11, 30, EventKind.CONTACT, 1, "Telefon"),
        ev(0, 14, 0, EventKind.TASK, 2, "Przygotować IPD"),
        ev(1, 8, 30, EventKind.TRAINING, 3, "Szkolenie IT"),
        ev(1, 10, 0, EventKind.MEETING, 4, "Spotkanie"),
        ev(1, 13, 15, EventKind.CONTACT, 5, "E-mail follow-up"),
        ev(1, 15, 0, EventKind.TASK, 6, "Aktualizacja CV"),
        ev(2, 9, 45, EventKind.MEETING, 7, "Spotkanie z pracodawcą"),
        ev(2, 12, 0, EventKind.TASK, 0, "Zamknięcie stażu"),
        ev(3, 0, 0, EventKind.TASK, 2, "Termin dokumentów", all_day=True),
        ev(3, 10, 30, EventKind.TRAINING, 4, "Szkolenie grupowe WUZ"),
        ev(3, 13, 0, EventKind.CONTACT, 5, "Teams"),
        ev(3, 16, 0, EventKind.MEETING, 6, "Spotkanie"),
        ev(4, 9, 0, EventKind.CONTACT, 1, "Telefon"),
        ev(4, 11, 0, EventKind.TASK, 3, "Skierowanie na staż"),
        ev(5, 10, 0, EventKind.TRAINING, 7, "Szkolenie adaptacyjne"),
        ev(6, 12, 0, EventKind.TASK, 0, "Podsumowanie tygodnia"),
        # kilka wpisów w innych tygodniach miesiąca
        ev(-4, 9, 0, EventKind.MEETING, 2, "Spotkanie"),
        ev(9, 14, 0, EventKind.TASK, 5, "Kontrola postępów"),
    ]
    return events


def make_provider(events: List[CalendarEvent]):
    def provider(start: date, end: date) -> List[CalendarEvent]:
        return [e for e in events if start <= e.day <= end]
    return provider


def main() -> int:
    app = QApplication(sys.argv)
    page = CalendarPage(make_provider(_sample_events()))
    page.client_selected.connect(lambda cid: print(f"[demo] otwórz kartę klienta ID={cid}"))
    page.resize(1280, 820)
    page.setWindowTitle("Client Workbench — Kalendarz (podgląd)")
    page.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
