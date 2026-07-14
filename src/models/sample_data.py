"""Static Sprint 0 sample data used by the clickable shell."""
from __future__ import annotations

CLIENTS = [
    {
        "id": 1, "external_id": "ASII-014", "first_name": "Anna", "last_name": "Kowalska", "phone": "+48 501 230 144", "email": "anna.kowalska@example.test",
        "disability_degree": "umiarkowany", "disability_symbol": "05-R", "recruitment_date": "2026-01-12", "ipd_date": "2026-02-02", "cv_status": "aktualne", "ipd_status": "aktualne", "internship_status": "w trakcie", "employment_status": "bez pracy", "client_status": "aktywny", "requires_attention": True, "attention_note": "Oczekuje na decyzję po spotkaniu z pracodawcą.", "has_photo": True,
    },
    {
        "id": 2, "external_id": "ASII-027", "first_name": "Piotr", "last_name": "Nowak", "phone": "+48 602 441 991", "email": "piotr.nowak@example.test",
        "disability_degree": "lekki", "disability_symbol": "10-N", "recruitment_date": "2025-11-18", "ipd_date": "2025-12-01", "cv_status": "nieaktualne", "ipd_status": "aktualne", "internship_status": "brak", "employment_status": "zatrudniony", "client_status": "aktywny", "requires_attention": False, "attention_note": "", "has_photo": False,
    },
]

TASKS = [
    {"type": "telefon", "title": "Oddzwonić po dokumenty do stażu", "client_id": 1, "due": "dziś 09:30", "priority": "wysoki", "status": "do zrobienia", "done": False},
    {"type": "spotkanie", "title": "Przygotować IPD i plan działań", "client_id": 2, "due": "dziś 11:00", "priority": "sredni", "status": "w trakcie", "done": False},
    {"type": "CV", "title": "Aktualizacja CV po szkoleniu", "client_id": 1, "due": "dziś 14:00", "priority": "niski", "status": "zakonczone", "done": True},
    {"type": "szkolenie", "title": "Potwierdzić obecność na WUZ", "client_id": 2, "due": "jutro", "priority": "sredni", "status": "oczekuje_na", "done": False},
]

NO_CONTACT = ["Piotr Nowak — 42 dni", "Marta Zielińska — brak kontaktów", "Jan Wiśniewski — 36 dni"]
ATTENTION = ["Anna Kowalska — decyzja pracodawcy", "Ewa Mazur — brak kompletu dokumentów"]

LONG_NOTE = "\n".join(f"{i:02d}. Notatka robocza klienta: ustalenia, kontekst rozmowy i następny krok." for i in range(1, 23))
