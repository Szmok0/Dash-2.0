# PRODUCT.md

## Cel
Client Workbench to lokalna aplikacja desktopowa Windows 11 dla jednego użytkownika. Ma działać jak rozbudowany notatnik i osobiste centrum pracy z klientami. Działa offline, bez chmury i AI.

## Główna zasada
Karta klienta jest jedynym miejscem tworzenia i edycji danych. Dashboard, Klienci, Kalendarz i Analityka są widokami danych.

## Menu
Dashboard, Klienci, Kalendarz, Analityka, Import, Ustawienia. Menu stale dostępne po lewej i opcjonalnie zwijane.

## Dashboard
Dashboard niczego nie zapisuje. Pokazuje:
- tabelę zadań,
- aktywnych klientów — liczba w górnym pasku,
- dzisiejsze spotkania — krótka informacja w górnym pasku,
- klientów bez kontaktu dłużej niż 30 dni,
- klientów ręcznie oznaczonych jako „Wymaga uwagi”.

Tabela zadań:
- typ działania,
- zadanie,
- klient,
- ID klienta,
- termin,
- priorytet,
- status,
- checkbox zakończenia.

Wykonane zadanie jest przekreślone i wyszarzone, ma status „Zakończone”, pozostaje widoczne do końca dnia, później znika z Dashboardu, lecz zostaje na karcie klienta.

## Klient
Klient ma unikalny ID z wewnętrznej bazy, status Aktywny/Zamknięty, zdjęcie, dane podstawowe, statusy CV/IPD/Staż/Zatrudnienie, zadania, kontakty, szkolenia i notatki.

Klient zamknięty nie pojawia się w bieżącym Dashboardzie, ale pozostaje w bazie, wyszukiwaniu i analityce.

## Dane podstawowe
Stały zestaw pól:
- ASII LP./ID klienta,
- Imię, Nazwisko,
- Telefon, E-mail,
- Data rekrutacji, Data IPD,
- CV, Zatrudnienie, Staż,
- DZ, JC, RP, Psycholog, Prawnik,
- Płeć,
- Stopień niepełnosprawności,
- Symbol,
- Symbole sprzężone,
- Wykształcenie,
- Data ważności orzeczenia,
- Poszukiwana praca,
- Komentarz.

Dane można zaimportować z XLSX lub dodać ręcznie w identycznym formularzu. Ponowny import aktualizuje wyłącznie dane podstawowe; zadania, kontakty, szkolenia, notatki i zdjęcie pozostają bez zmian.

## Statusy szybkiego podglądu
- CV: aktualne / nieaktualne,
- IPD: aktualne / nieaktualne,
- Staż: brak / w trakcie,
- Zatrudnienie: bez pracy / zatrudniony,
- Klient: aktywny / zamknięty.

Zmiana jednym kliknięciem lub krótkim menu wyboru.

## Zadania
Pola:
- nazwa,
- termin,
- priorytet: niski / średni / wysoki,
- status: do zrobienia / w trakcie / zakończone / anulowane / oczekuję na,
- notatka.

## Kontakty
Typy: telefon, spotkanie, e-mail, SMS, Teams, inne.
Pola: typ, data, opcjonalna godzina, status, notatka.

## Szkolenia
Pola: nazwa, data, rodzaj, status, notatka.
Rodzaje: indywidualne, grupowe, WUZ, IT, adaptacyjne, e-learning.
Statusy: planowane, ukończył, nie ukończył.

## Notatki
Moduł Notatki agreguje notatki własne i notatki z kontaktów. Sortowanie od najnowszej.

## Kalendarz
Tylko wizualizacja dat z zadań, kontaktów/spotkań i szkoleń. Widok miesiąca i tygodnia. Wpis pokazuje nazwisko, typ działania i godzinę. Kliknięcie prowadzi do klienta.

## Analityka
Bez wykresów. Filtry po danych podstawowych, statusach, szkoleniach, kontaktach i zadaniach. Historia działań w okresie. Eksport PDF/CSV/XLSX. Każdy wynik klikalny.

## Import i eksport
Import XLSX po ID klienta. Podgląd: nowi, aktualizowani, bez zmian, błędy, duplikaty. Brak klienta w pliku nie usuwa go.
Eksport: karta klienta do PDF, analityka do PDF/CSV/XLSX.

## Bezpieczeństwo
Windows 11, offline, jeden użytkownik, PIN 4 znaki, automatyczna blokada po bezczynności, SQLite, lokalny backup, bez szyfrowania aplikacyjnego w MVP.

## Poza MVP
Wielu użytkowników, role, synchronizacja MS365/SharePoint, AI, chmura, załączniki inne niż zdjęcie, rozbudowana historia zmian.
