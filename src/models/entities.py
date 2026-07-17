"""Encje domenowe i słowniki etykiet (models = encje/walidacja, BUILD.md)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

PRIORITIES = ["niski", "sredni", "wysoki"]
TASK_STATUSES = ["do_zrobienia", "w_trakcie", "zakonczone", "anulowane", "oczekuje_na"]
CONTACT_TYPES = ["telefon", "spotkanie", "email", "sms", "teams", "inne"]
CONTACT_STATUSES = ["planowany", "odbyty", "nieudany"]
TRAINING_TYPES = ["indywidualne", "grupowe", "wuz", "it", "adaptacyjne", "elearning"]
TRAINING_STATUSES = ["planowane", "ukonczyl", "nie_ukonczyl"]

PRIORITY_LABELS = {"niski": "Niski", "sredni": "Średni", "wysoki": "Wysoki"}
TASK_STATUS_LABELS = {
    "do_zrobienia": "Do zrobienia",
    "w_trakcie": "W trakcie",
    "zakonczone": "Zakończone",
    "anulowane": "Anulowane",
    "oczekuje_na": "Oczekuję na",
}
CONTACT_TYPE_LABELS = {
    "telefon": "Telefon",
    "spotkanie": "Spotkanie",
    "email": "E-mail",
    "sms": "SMS",
    "teams": "Teams",
    "inne": "Inne",
}
TRAINING_TYPE_LABELS = {
    "indywidualne": "Indywidualne",
    "grupowe": "Grupowe",
    "wuz": "WUZ",
    "it": "IT",
    "adaptacyjne": "Adaptacyjne",
    "elearning": "E-learning",
}
TRAINING_STATUS_LABELS = {
    "planowane": "Planowane",
    "ukonczyl": "Ukończył",
    "nie_ukonczyl": "Nie ukończył",
}
CV_STATUS_LABELS = {"aktualne": "Aktualne", "nieaktualne": "Nieaktualne"}
IPD_STATUS_LABELS = {"aktualne": "Aktualne", "nieaktualne": "Nieaktualne"}
INTERNSHIP_LABELS = {"brak": "Brak", "w_trakcie": "W trakcie"}
EMPLOYMENT_LABELS = {"bez_pracy": "Bez pracy", "zatrudniony": "Zatrudniony"}
CLIENT_STATUS_LABELS = {"aktywny": "Aktywny", "zamkniety": "Zamknięty"}


@dataclass
class Task:
    id: int
    client_id: int
    title: str
    due_at: Optional[datetime]
    priority: str
    status: str
    note: str = ""
    action_type: str = "notatka"  # typ działania na Dashboardzie
    completed_at: Optional[datetime] = None


@dataclass
class Contact:
    id: int
    client_id: int
    contact_type: str
    contact_at: datetime
    status: str
    note: str = ""


@dataclass
class Training:
    id: int
    client_id: int
    name: str
    training_date: date
    training_type: str
    status: str
    note: str = ""


@dataclass
class Note:
    id: int
    client_id: int
    content: str
    created_at: datetime


@dataclass
class CalendarEvent:
    """Wydarzenie w kalendarzu — wizualizacja daty z zadania/kontaktu/szkolenia."""

    client_id: int
    last_name: str
    first_name: str
    kind: str  # zadanie / kontakt / szkolenie
    label: str  # typ działania do wyświetlenia
    when: datetime  # data + godzina (dla szkoleń godzina 00:00)
    has_time: bool  # czy pokazywać godzinę (szkolenia mają tylko datę)

    @property
    def event_date(self) -> date:
        return self.when.date()


@dataclass
class ActivityRow:
    """Wiersz historii działań w analityce (zadanie / kontakt / szkolenie)."""

    when: datetime
    client_id: int
    external_id: str
    client_name: str
    kind: str  # zadanie / kontakt / szkolenie
    description: str
    status: str
    has_time: bool


@dataclass
class Client:
    id: int
    external_id: str
    first_name: str
    last_name: str
    phone: str = ""
    email: str = ""
    recruitment_date: Optional[date] = None
    ipd_date: Optional[date] = None
    cv_status: str = "nieaktualne"
    ipd_status: str = "nieaktualne"
    employment_status: str = "bez_pracy"
    internship_status: str = "brak"
    client_status: str = "aktywny"
    dz: str = ""
    jc: str = ""
    rp: str = ""
    psychologist: str = ""
    lawyer: str = ""
    gender: str = ""
    disability_degree: str = ""
    disability_symbol: str = ""
    combined_symbols: str = ""
    education: str = ""
    certificate_valid_until: Optional[date] = None
    desired_job: str = ""
    import_comment: str = ""
    requires_attention: bool = False
    attention_note: str = ""
    photo_path: Optional[str] = None  # ścieżka bezwzględna w pamięci, względna w bazie

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
