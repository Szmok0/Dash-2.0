# Client Workbench

Lokalna aplikacja desktopowa (Windows 11, offline, jeden użytkownik) do pracy z klientami.
Działa bez chmury, sieci i AI. Wszystkie sprinty z `docs/BUILD.md` zrealizowane:

- **Sprint 0** — shell UI (dark/light, Dashboard, karta klienta),
- **Sprint 1** — baza SQLite (WAL, foreign keys), lista i wyszukiwanie klientów,
  ręczne dodawanie klienta (ID wymagane i unikalne), zdjęcia w `data/photos/`,
- **Sprint 2–3** — Dashboard, zadania, kontakty, notatki, „bez kontaktu >30 dni",
- **Sprint 4** — Szkolenia oraz Kalendarz (widok miesiąca i tygodnia),
- **Sprint 5** — Analityka (filtry, historia działań, klikalne wyniki) i eksport
  CSV/XLSX/PDF oraz eksport karty klienta do PDF,
- **Sprint 6** — Import XLSX po ID z podglądem (nowi/aktualizowani/bez zmian/błędy/
  duplikaty) w jednej transakcji; kopie zapasowe ZIP (auto raz dziennie, 10 ostatnich) i przywracanie,
- **Sprint 7** — PIN (4 cyfry, hash PBKDF2) i blokada po bezczynności, edycja/usuwanie
  wpisów, testy (pytest), pakiet instalacyjny EXE z ikoną na pulpicie.

Architektura wg BUILD.md: UI nie wykonuje SQL — strony rozmawiają z fasadą
`services.DataStore`, która używa repozytoriów (`repositories/`) nad SQLite
(`database/connection.py` + `database/schema.sql`); encje w `models/`.

## Co zawiera Sprint 0

- stały sidebar (Dashboard, Klienci, Kalendarz, Analityka, Import, Ustawienia), zwijany do listwy z ikonami,
- górny pasek: tytuł, wyszukiwarka ID/nazwisko, licznik aktywnych klientów, dzisiejsze spotkania, `+ Dodaj`,
- Dashboard: tabela zadań (checkbox, typ z ikoną, zadanie, klient, ID, termin, priorytet, status) + prawe moduły „Bez kontaktu >30 dni" i „Wymagają uwagi",
- kartę klienta: osobny ekran, lewa kolumna (zdjęcie/placeholder, dane), rząd statusów CV/IPD/Staż/Zatrudnienie/Klient (zmiana jednym kliknięciem) i równe moduły: Dane podstawowe, Zadania, Kontakty, Szkolenia, Notatki,
- pełny widok modułu (modal z filtrowaniem) po kliknięciu nagłówka,
- formularze `+ Dodaj` (Zadanie / Kontakt / Szkolenie / Notatka) — zapis do pamięci,
- motyw ciemny (bazowy) i jasny (Ustawienia → przełącznik),
- dane testowe: różne priorytety i statusy, zakończone zadanie przekreślone, długa notatka 20+ wierszy, klient ze zdjęciem (Anna Kowalska) i bez zdjęcia.

## Uruchomienie

```bash
python -m pip install -r requirements.txt
python src/app.py
```

Wymagany Python 3.11+ oraz PySide6. Baza tworzy się automatycznie w `./data/`
(katalog można zmienić zmienną środowiskową `CW_DATA_DIR`). Aplikacja startuje
pusta; dane demonstracyjne można zasiać:

```bash
python tools/seed_demo.py
```

## Instalator Windows (EXE + ikona na pulpicie)

Budowanie instalatora opisano w `packaging/README.md`. W skrócie, na Windows:

```bat
packaging\build_windows.bat
```

Powstaje `dist/installer/ClientWorkbench_Setup_1.0.0.exe` — instaluje aplikację bez
potrzeby Pythona, tworzy skrót w menu Start i ikonę na pulpicie, a dane użytkownika
trzyma w `%LOCALAPPDATA%\ClientWorkbench\data`.

## Testy

```bash
python -m pytest tests/ -q
```

## Zrzuty ekranu

Generowanie (działa też headless):

```bash
QT_QPA_PLATFORM=offscreen python tools/screenshot.py
```

Wyniki w `docs/screenshots/` (Dashboard i Karta klienta w 1920×1080 i 1366×768 + wariant jasny).

## Struktura

```
docs/            dokumentacja produktu (PRODUCT, UI, DATABASE, WORKFLOW, BUILD, schema.sql)
src/app.py       punkt wejścia
src/config.py    stałe wymiarów + ścieżki katalogu danych
src/database/    połączenie SQLite + schema.sql
src/models/      encje domenowe i słowniki etykiet
src/repositories/ dostęp do tabel (clients, tasks, contacts, trainings, notes)
src/services/    DataStore + AnalyticsService (fasady danych dla UI)
src/exporters/   eksport CSV/XLSX/PDF tabel i karty klienta (openpyxl, reportlab)
src/data/        zestaw danych demonstracyjnych (seed)
src/ui/windows/  okno główne
src/ui/pages/    Dashboard, Klienci, Karta klienta, Kalendarz, Analityka, Ustawienia
src/ui/dialogs/  formularze (zadanie/kontakt/szkolenie/notatka, klient) + pełny widok modułu
src/ui/widgets/  sidebar, header, pigułki statusów, ikony
src/ui/styles/   palety dark/light + QSS
tools/           seed_demo, generator zdjęcia testowego i zrzutów ekranu
resources/       zasoby (zdjęcie testowe, czcionka DejaVu do PDF)
data/            baza, zdjęcia, backupy (poza repozytorium)
```

## Kolejne sprinty (wg BUILD.md)

6. Import XLSX, backup/restore
7. PIN, blokada, testy, EXE/instalator
