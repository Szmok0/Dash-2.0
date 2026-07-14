# BUILD.md

## Technologia
Python 3.12, PySide6, SQLite, openpyxl, reportlab/WeasyPrint, PyInstaller, Inno Setup lub WiX. Bez serwera i przeglądarki.

## Dystrybucja
Instalator EXE, bez instalowania Pythona. Dane poza katalogiem programu, preferowane `C:\ClientWorkbench\data\`.
Struktura: client_workbench.db, photos/, backups/, exports/, logs/.

## Struktura kodu
src/app.py, config.py, database/, models/, repositories/, services/, importers/, exporters/, ui/windows/, ui/pages/, ui/dialogs/, ui/widgets/, ui/styles/, resources/, tests/.

UI nie wykonuje SQL. Services = logika biznesowa. Repositories = SQLite. Models = encje/walidacja.

## Sprinty
0. Shell UI: sidebar, header, Dashboard, karta klienta, statyczne dane, dark/light, bez bazy.
1. SQLite, lista klientów, wyszukiwanie, ręczne dodawanie, karta klienta, zdjęcia.
2. Zadania i Dashboard z realnych danych.
3. Kontakty, notatki, wspólna oś czasu, brak kontaktu >30 dni.
4. Szkolenia i Kalendarz.
5. Analityka i eksport.
6. Import XLSX, backup/restore.
7. PIN, blokada, testy, EXE/instalator.

## Zasady kodu
Type hints, brak logiki biznesowej w widgetach, transakcje importu, logi do data/logs/app.log, brak telemetryki i sieci.

## Kryteria MVP
Offline, instalacja EXE, import 150 klientów bez utraty danych, ponowny import nie nadpisuje danych roboczych, działa na 1366×768 i 1920×1080, zdjęcia nie duplikują się, backup/restore przetestowane, PDF karty klienta działa, brak dodatkowych zależności po stronie użytkownika.
