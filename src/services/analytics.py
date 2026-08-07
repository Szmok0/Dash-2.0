"""Serwis analityki — filtrowanie klientów po danych podstawowych, statusach i działaniach."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from models.entities import ActivityRow, Client

ANY = "__any__"  # wartość „dowolny” w filtrach
DONE = "__done__"  # DM/Aneks: zrobiony
NOT_DONE = "__not_done__"  # DM/Aneks: nie ma

# wartości uznawane za „zrobiony/tak" (spójne z kartą klienta)
_DONE_VALUES = {"tak", "1", "true", "x", "jest", "zrobiony", "zrobione", "zrobiona"}


def _is_done(value) -> bool:
    return str(value or "").strip().lower() in _DONE_VALUES


@dataclass
class ClientFilter:
    text: str = ""  # ID / imię / nazwisko / poszukiwana praca
    client_status: str = ANY
    cv_status: str = ANY
    ipd_status: str = ANY
    internship_status: str = ANY
    employment_status: str = ANY
    dm: str = ANY  # ANY / DONE / NOT_DONE
    aneks: str = ANY  # ANY / DONE / NOT_DONE
    gender: str = ANY
    disability_degree: str = ANY
    # działania: wymagaj, aby klient miał wpis danego typu
    has_tasks: bool = False
    has_contacts: bool = False
    has_trainings: bool = False


@dataclass
class ClientRow:
    client: Client
    task_count: int = 0
    contact_count: int = 0
    training_count: int = 0


@dataclass
class HistoryFilter:
    start: date
    end: date
    include_tasks: bool = True
    include_contacts: bool = True
    include_trainings: bool = True


class AnalyticsService:
    """Operuje na danych z DataStore; sam nie dotyka SQLite bezpośrednio."""

    def __init__(self, store) -> None:  # store: DataStore
        self._store = store

    # ------------------------------------------------------------------
    def filter_clients(self, flt: ClientFilter) -> list[ClientRow]:
        text = flt.text.strip().lower()
        result: list[ClientRow] = []
        for client in self._store.clients:
            if not self._match_client(client, flt, text):
                continue
            tasks = self._store.client_tasks(client.id)
            contacts = self._store.client_contacts(client.id)
            trainings = self._store.client_trainings(client.id)
            if flt.has_tasks and not tasks:
                continue
            if flt.has_contacts and not contacts:
                continue
            if flt.has_trainings and not trainings:
                continue
            result.append(
                ClientRow(client, len(tasks), len(contacts), len(trainings))
            )
        result.sort(key=lambda r: (r.client.last_name, r.client.first_name))
        return result

    @staticmethod
    def _match_client(client: Client, flt: ClientFilter, text: str) -> bool:
        if text:
            hay = (
                f"{client.external_id} {client.first_name} {client.last_name} "
                f"{client.desired_job}"
            ).lower()
            if text not in hay:
                return False
        checks = [
            (flt.client_status, client.client_status),
            (flt.cv_status, client.cv_status),
            (flt.ipd_status, client.ipd_status),
            (flt.internship_status, client.internship_status),
            (flt.employment_status, client.employment_status),
            (flt.gender, client.gender),
            (flt.disability_degree, client.disability_degree),
        ]
        for wanted, actual in checks:
            if wanted != ANY and wanted != actual:
                return False
        # DM / Aneks: dwustan „zrobiony / nie ma" (wartości „Tak"/„Nie" w bazie)
        for wanted, value in ((flt.dm, client.dm), (flt.aneks, client.aneks)):
            if wanted != ANY and (wanted == DONE) != _is_done(value):
                return False
        return True

    # ------------------------------------------------------------------
    def activity_history(self, flt: HistoryFilter) -> list[ActivityRow]:
        return self._store.activity_history(
            flt.start, flt.end, flt.include_tasks, flt.include_contacts, flt.include_trainings
        )
