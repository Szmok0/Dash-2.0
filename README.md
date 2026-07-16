# Client Workbench — Sprint 0 (shell UI)

Lokalna aplikacja desktopowa (Windows 11, offline) do pracy z klientami.
Ten etap to **Sprint 0** wg `docs/BUILD.md`: klikalny shell UI z danymi
testowymi w pamięci — **bez SQLite** (baza wchodzi w Sprintcie 1).

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

Wymagany Python 3.11+ oraz PySide6.

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
src/config.py    stałe wymiarów/rozmiarów
src/data/        dane testowe Sprintu 0 (w pamięci)
src/ui/windows/  okno główne
src/ui/pages/    Dashboard, Klienci, Karta klienta, Ustawienia, zaślepki
src/ui/dialogs/  formularze + pełny widok modułu
src/ui/widgets/  sidebar, header, pigułki statusów, ikony
src/ui/styles/   palety dark/light + QSS
tools/           generator zdjęcia testowego i zrzutów ekranu
resources/       zasoby (zdjęcie testowe)
```

## Kolejne sprinty (wg BUILD.md)

1. SQLite, lista klientów, ręczne dodawanie, zdjęcia
2. Zadania i Dashboard z realnych danych
3. Kontakty, notatki, oś czasu, brak kontaktu >30 dni
4. Szkolenia i Kalendarz
5. Analityka i eksport
6. Import XLSX, backup/restore
7. PIN, blokada, testy, EXE/instalator
