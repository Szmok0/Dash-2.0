"""Import XLSX klientów po external_id z podglądem zmian (WORKFLOW.md).

Ponowny import aktualizuje wyłącznie dane podstawowe; zadania, kontakty,
szkolenia, notatki i zdjęcie pozostają bez zmian. Brak klienta w pliku nie
usuwa go z bazy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from models.entities import Client

# Nagłówek w pliku (po normalizacji) -> atrybut encji Client.
HEADER_MAP: dict[str, str] = {
    "id klienta": "external_id",
    "asii lp.": "external_id",
    "asii lp": "external_id",
    "external_id": "external_id",
    "id": "external_id",
    "imie": "first_name",
    "imię": "first_name",
    "nazwisko": "last_name",
    "telefon": "phone",
    "e-mail": "email",
    "email": "email",
    "data rekrutacji": "recruitment_date",
    "data ipd": "ipd_date",
    "cv": "cv_status",
    "zatrudnienie": "employment_status",
    "staz": "internship_status",
    "staż": "internship_status",
    "dz": "dz",
    "jc": "jc",
    "rp": "rp",
    "psycholog": "psychologist",
    "prawnik": "lawyer",
    "plec": "gender",
    "płeć": "gender",
    "stopien niepelnosprawnosci": "disability_degree",
    "stopień niepełnosprawności": "disability_degree",
    "symbol": "disability_symbol",
    "symbole sprzezone": "combined_symbols",
    "symbole sprzężone": "combined_symbols",
    "wyksztalcenie": "education",
    "wykształcenie": "education",
    "data waznosci orzeczenia": "certificate_valid_until",
    "data ważności orzeczenia": "certificate_valid_until",
    "poszukiwana praca": "desired_job",
    "komentarz": "import_comment",
    # długi nagłówek-instrukcja z realnych plików (symbole sprzężone)
    "jeśli niepełnosprawność sprzężona wpisać symbole ręcznie": "combined_symbols",
    "jesli niepelnosprawnosc sprzezona wpisac symbole recznie": "combined_symbols",
}

# dopasowanie po fragmencie nagłówka (gdy tekst nie jest dokładnie taki jak wyżej)
HEADER_CONTAINS = [
    ("asii", "external_id"),
    ("id klienta", "external_id"),
    ("sprzężon", "combined_symbols"),
    ("sprzezon", "combined_symbols"),
    ("stopień niepe", "disability_degree"),
    ("stopien niepe", "disability_degree"),
    ("ważności orzecz", "certificate_valid_until"),
    ("waznosci orzecz", "certificate_valid_until"),
    ("data rekrutacji", "recruitment_date"),
    ("data ipd", "ipd_date"),
    ("poszukiwana praca", "desired_job"),
    ("wykształ", "education"),
    ("wyksztal", "education"),
]

DATE_FIELDS = {"recruitment_date", "ipd_date", "certificate_valid_until"}
# pola aktualizowane przy ponownym imporcie (dane podstawowe)
UPDATABLE_FIELDS = [v for v in dict.fromkeys(HEADER_MAP.values()) if v != "external_id"]


@dataclass
class RowError:
    row_number: int
    external_id: str
    message: str


@dataclass
class ImportPreview:
    file_name: str
    new: list[Client] = field(default_factory=list)
    updated: list[tuple[Client, Client]] = field(default_factory=list)  # (istniejący, docelowy)
    unchanged: list[Client] = field(default_factory=list)
    errors: list[RowError] = field(default_factory=list)
    duplicates: list[RowError] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.new) + len(self.updated) + len(self.unchanged) + len(self.errors) + len(self.duplicates)


def _norm(value) -> str:
    """Normalizuje nagłówek: zwija białe znaki (w tym łamanie wiersza) do pojedynczej spacji."""
    if value is None:
        return ""
    return " ".join(str(value).split()).strip().lower()


def _match_header(name) -> str | None:
    """Zwraca atrybut encji dla nagłówka: dokładnie lub po fragmencie tekstu."""
    key = _norm(name)
    if not key:
        return None
    if key in HEADER_MAP:
        return HEADER_MAP[key]
    for fragment, field_name in HEADER_CONTAINS:
        if fragment in key:
            return field_name
    return None


def _parse_date(value) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"nieprawidłowa data: {text!r}")


def _norm_status(field: str, value) -> Optional[str]:
    text = _norm(value)
    if text == "":
        return None
    if field == "cv_status":
        return "aktualne" if text in ("aktualne", "aktualny", "tak", "1") else "nieaktualne"
    if field == "employment_status":
        return "zatrudniony" if text in ("zatrudniony", "zatrudniona", "tak", "1") else "bez_pracy"
    if field == "internship_status":
        return "w_trakcie" if text in ("w trakcie", "w_trakcie", "trwa") else "brak"
    return None


def parse_workbook(path: str | Path) -> tuple[list[dict], list[RowError]]:
    """Zwraca (wiersze jako słowniki pól, błędy). Wiersz zawiera _row i _values."""
    from openpyxl import load_workbook

    wb = load_workbook(filename=str(path), read_only=True, data_only=True)
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)
    try:
        header = next(rows_iter)
    except StopIteration:
        return [], [RowError(1, "", "Pusty plik.")]

    col_field: dict[int, str] = {}
    for idx, name in enumerate(header):
        field_name = _match_header(name)
        if field_name is not None and field_name not in col_field.values():
            col_field[idx] = field_name
    if "external_id" not in col_field.values():
        return [], [RowError(
            1, "",
            "Brak kolumny z ID klienta. Rozpoznawane nagłówki ID: „ASII LP.” lub „ID klienta”.",
        )]

    parsed: list[dict] = []
    errors: list[RowError] = []
    for r_idx, raw in enumerate(rows_iter, start=2):
        if raw is None or all(c is None or str(c).strip() == "" for c in raw):
            continue
        values: dict[str, object] = {}
        row_error: Optional[str] = None
        for idx, field_name in col_field.items():
            cell = raw[idx] if idx < len(raw) else None
            is_empty = cell is None or str(cell).strip() == ""
            if field_name in DATE_FIELDS:
                if is_empty:
                    continue  # pusta komórka nie nadpisuje istniejącej daty
                try:
                    values[field_name] = _parse_date(cell)
                except ValueError as exc:
                    row_error = str(exc)
            elif field_name in ("cv_status", "employment_status", "internship_status"):
                norm = _norm_status(field_name, cell)
                if norm is not None:
                    values[field_name] = norm
            else:
                if not is_empty:  # pusta komórka nie kasuje istniejącej wartości
                    values[field_name] = str(cell).strip()
        ext = str(values.get("external_id", "")).strip()
        if not ext:
            errors.append(RowError(r_idx, "", "Brak ID klienta w wierszu."))
            continue
        values["external_id"] = ext
        if row_error:
            errors.append(RowError(r_idx, ext, row_error))
            continue
        values["_row"] = r_idx
        parsed.append(values)

    wb.close()
    return parsed, errors


def build_preview(store, path: str | Path) -> ImportPreview:
    path = Path(path)
    parsed, errors = parse_workbook(path)
    preview = ImportPreview(file_name=path.name, errors=errors)

    seen: dict[str, int] = {}
    for values in parsed:
        ext = values["external_id"]
        if ext in seen:
            preview.duplicates.append(
                RowError(values["_row"], ext, f"Duplikat ID w pliku (także wiersz {seen[ext]}).")
            )
            continue
        seen[ext] = values["_row"]

        existing = store.find_by_external_id(ext)
        if existing is None:
            if not values.get("first_name") or not values.get("last_name"):
                preview.errors.append(
                    RowError(values["_row"], ext, "Nowy klient bez imienia/nazwiska.")
                )
                continue
            preview.new.append(_client_from_values(values))
        else:
            target = _apply_values(existing, values)
            if _basic_differs(existing, target):
                preview.updated.append((existing, target))
            else:
                preview.unchanged.append(existing)
    return preview


def _client_from_values(values: dict) -> Client:
    client = Client(
        id=0,
        external_id=values["external_id"],
        first_name=str(values.get("first_name", "")).strip(),
        last_name=str(values.get("last_name", "")).strip(),
    )
    return _apply_values(client, values)


def _apply_values(base: Client, values: dict) -> Client:
    from copy import copy

    target = copy(base)
    for f in UPDATABLE_FIELDS:
        if f in values:
            setattr(target, f, values[f])
    return target


def _basic_differs(a: Client, b: Client) -> bool:
    return any(getattr(a, f) != getattr(b, f) for f in UPDATABLE_FIELDS)
