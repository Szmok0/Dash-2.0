"""Model zdarzenia kalendarza.

Kalendarz jest tylko wizualizacją dat pochodzących z zadań, kontaktów/spotkań
i szkoleń (patrz PRODUCT.md -> Kalendarz). Ten model to lekki, wspólny format,
do którego repozytorium/serwis mapuje wiersze z tabel `tasks`, `contacts`
i `trainings`. Widok kalendarza nie wykonuje SQL.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from enum import Enum
from typing import Optional


class EventKind(str, Enum):
    """Typ działania stojący za wpisem w kalendarzu."""

    TASK = "zadanie"
    CONTACT = "kontakt"
    MEETING = "spotkanie"
    TRAINING = "szkolenie"


@dataclass(frozen=True)
class CalendarEvent:
    """Pojedynczy wpis widoczny w kalendarzu.

    Wpis pokazuje nazwisko, typ działania i godzinę (PRODUCT.md). Kliknięcie
    prowadzi do klienta, dlatego trzymamy `client_id`.
    """

    client_id: int
    client_name: str
    kind: EventKind
    when: datetime
    title: str = ""
    all_day: bool = False

    @property
    def day(self) -> date:
        return self.when.date()

    @property
    def start_time(self) -> Optional[time]:
        return None if self.all_day else self.when.time()

    def time_label(self) -> str:
        """Godzina do wyświetlenia, np. '09:30' albo '' dla całodniowych."""
        if self.all_day:
            return ""
        return self.when.strftime("%H:%M")
