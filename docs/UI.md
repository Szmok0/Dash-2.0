# UI.md

## Założenia
Dark mode jako projekt bazowy, light mode jako opcja. Interfejs ma wyglądać jak profesjonalna aplikacja desktopowa, nie strona WWW ani Excel.

Priorytety:
- najpierw widzę, potem czytam,
- wysoka gęstość informacji,
- symetria i porządek,
- mało pustych przestrzeni,
- stałe wymiary bloków,
- równe moduły,
- kolory niosą informację.

## Ekran bazowy
Laptop 15,6–16", bazowo 1920×1080, działa także przy 1366×768. Siatka 8 px. Promień kart 10–12 px. Odstępy 8/16/24/32 px.

## Sidebar
220–240 px, po zwinięciu 56–64 px. Pozycje tekstowe: Dashboard, Klienci, Kalendarz, Analityka, Import, Ustawienia. Bez ozdobnych ikon; ikony dopuszczalne tylko w wersji zwiniętej.

## Górny pasek
Wysokość 56–64 px. Tytuł, wyszukiwarka ID/nazwisko, liczba aktywnych klientów, dzisiejsze spotkania, `+ Dodaj`. Search 320–420 × 36–40 px.

## Dashboard
Układ:
- tabela zadań 70–75% szerokości,
- prawy panel 25–30% szerokości.

Prawy panel ma dwa równe moduły:
1. Bez kontaktu >30 dni
2. Wymagają uwagi

Tabela:
- wiersz 38–42 px,
- nagłówek 36–40 px,
- brak odstępów między wierszami,
- separator 1 px,
- font 13–14 px,
- statusy 11–12 px.

Kolumny:
checkbox, typ, zadanie, klient, ID, termin, priorytet, status.

Ikony tylko przy typie działania, monochromatyczne outline: telefon, spotkanie, e-mail, CV, szkolenie, notatka. Bez emoji.

Kolory priorytetu:
- wysoki czerwony,
- średni żółty/pomarańczowy,
- niski zielony lub neutralny.

Kolory statusu:
- do zrobienia niebieski,
- w trakcie fioletowy/turkusowy,
- zakończone szary,
- oczekuję na żółty,
- anulowane neutralny szary.

## Karta klienta
Osobny ekran, pełna przestrzeń robocza. Nie dzielić ekranu z Dashboardem.

Układ:
- lewa kolumna 250–290 px,
- prawa część robocza.

Lewa kolumna:
- zdjęcie 96–120 px,
- imię i nazwisko,
- ID,
- telefon,
- e-mail,
- stopień niepełnosprawności,
- symbol,
- data wejścia,
- data IPD.

Brak zdjęcia = pusty placeholder, bez inicjałów.

Prawa część:
- rząd statusów CV/IPD/Staż/Zatrudnienie/Status klienta,
- poniżej równe moduły.

Moduły:
- Dane podstawowe,
- Zadania,
- Kontakty,
- Szkolenia,
- Notatki.

Każdy moduł ma stałą i równą wysokość, nagłówek, licznik, `+ Dodaj`, 3–5 wpisów. Kliknięcie nagłówka otwiera pełny widok. Nie stosować accordionów zmieniających wysokość layoutu.

## Pełny widok modułu
Duży modal/panel nad kartą klienta, bez nowego okna Windows. Pełna lista, opcjonalne filtrowanie i wyszukiwanie. Zamknięcie wraca do karty.

## Formularze
`+ Dodaj` -> Zadanie / Kontakt / Szkolenie / Notatka. Bez ikon. Stały styl, szerokość 520–640 px. Pole notatki rośnie pionowo. Przyciski tekstowe: Zapisz / Anuluj / Usuń. Po zapisie panel zamyka się bez komunikatu.

## Typografia
Segoe UI lub Inter.
- tytuł ekranu 24–28 px,
- tytuł sekcji 16–18 px,
- tabela 13–14 px,
- metadane 11–12 px,
- przyciski 13–14 px.

Notatki: line-height 1.25–1.35, bez wielkich odstępów.

## Paleta dark
- tło #171C26
- sidebar #121722
- panel #1D2330
- karty/tabela #202737
- linie #2B3245
- tekst #F2F4F7
- tekst pomocniczy #A4ACB8
- akcent #4C8DFF
- czerwony #E85D68
- żółty #E8B44C
- zielony #4FBF78
- fioletowy #8B7CF6

## Responsywność
1920×1080: pełny sidebar i oba panele. 1366×768: sidebar zwinięty, prawy panel węższy, 8–10 wierszy widocznych, brak poziomego scrolla. Na 27" maksymalna szerokość treści; dodatkowa przestrzeń jako kontrolowany margines.
