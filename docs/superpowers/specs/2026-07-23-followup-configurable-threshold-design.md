# Follow-up: konfigurowalny próg „bez kontaktu" (+ wykluczenie zatrudnionych/stażystów)

- **Data:** 2026-07-23
- **Status:** do przeglądu (spec przed implementacją)
- **Autor:** brainstorming (superpowers) + użytkownik

## Kontekst

Client Workbench pokazuje na Dashboardzie panel **„Bez kontaktu >30 dni"** —
lista aktywnych klientów, dla których ostatni wpisany kontakt jest starszy niż
30 dni. Lista jest w pełni **wyliczana** z historii kontaktów; klient „wypada"
z niej automatycznie, gdy pojawi się nowy wpis w panelu Kontakt.

Obecna logika: `ContactsRepository.no_contact_over(days)`
(`src/repositories/activities.py:112`) → `DataStore.no_contact_over(days=30)`
(`src/services/store.py:211`) → Dashboard woła `no_contact_over(30)` na sztywno
(`src/ui/pages/dashboard_page.py:243`).

## Problem

1. Próg **30 dni jest zaszyty** w kodzie UI — nie da się go dostosować bez zmiany kodu.
2. **Reguła wykluczenia nie jest zaimplementowana.** Oczekiwane zachowanie: na
   liście NIE powinni pojawiać się klienci oznaczeni jako *zatrudnieni* lub
   *na stażu*. Obecne zapytanie filtruje jedynie `client_status = 'aktywny'`
   (czyli odsiewa tylko klientów *zamkniętych*), a `employment_status` i
   `internship_status` to osobne pola, których zapytanie nie sprawdza.

> ⚠️ **Rozbieżność wykryta podczas projektowania:** użytkownik opisał wykluczenie
> zatrudnionych/stażystów jako regułę „już działającą", ale w kodzie jej nie ma.
> Ta specyfikacja traktuje wykluczenie jako **wymaganie do wdrożenia** (dogonienie
> oczekiwania). Jeśli intencją było zachowanie obecnego zachowania — patrz sekcja
> *Decyzja do potwierdzenia*.

## Cel

Zastąpić zaszyty próg 30 **jednym, globalnym, konfigurowalnym progiem N** oraz
uzupełnić zapytanie o **regułę wykluczenia** zatrudnionych i stażystów. Bez
nowych tabel, bez stanu „załatwione", bez snooze — stan „załatwienia" wynika
wyłącznie z pojawienia się nowego wpisu kontaktu (YAGNI).

## Poza zakresem (świadomie)

- Osobna tabela reminderów / persystencja stanu „done".
- Snooze / odkładanie przypomnień.
- Różne progi zależne od typu wsparcia.
- Powiadomienia systemowe / e-mail.

## Stan obecny (fakty z kodu)

| Element | Stan |
|---|---|
| Tabela ustawień | `settings(key TEXT PRIMARY KEY, value TEXT)` — `schema.sql:86` |
| API ustawień | `DataStore.get_setting(key, default)` / `set_setting(key, value)` — `store.py:49-55` |
| Zapytanie listy | `no_contact_over(days)` filtruje `WHERE c.client_status = 'aktywny'` — `activities.py:121` |
| Wywołanie w UI | `self._store.no_contact_over(30)` — `dashboard_page.py:243` |
| Tytuł panelu | literał `"Bez kontaktu >30 dni"` — `dashboard_page.py:106` |
| Pola statusów | `client_status` ∈ {aktywny, zamkniety}; `employment_status` ∈ {bez_pracy, zatrudniony}; `internship_status` ∈ {brak, w_trakcie} — `entities.py:59-61` |

## Projekt

### 1. Ustawienie progu

- Klucz w tabeli `settings`: **`follow_up_days`**, wartość tekstowa liczby całkowitej.
- Domyślnie **`"30"`** (zachowanie kompatybilne — brak wpisu = 30).
- Walidacja przy odczycie i zapisie: liczba całkowita w zakresie **1–365**;
  wartość spoza zakresu lub nieparsowalna → fallback do 30.
- Odczyt pomocniczy w `DataStore`, np. `follow_up_days() -> int`, opakowujący
  `get_setting("follow_up_days", "30")` z walidacją, żeby UI nie parsowało samo.

### 2. Zapytanie (reguła wykluczenia)

Rozszerzyć `WHERE` w `ContactsRepository.no_contact_over`:

```sql
WHERE c.client_status = 'aktywny'
  AND c.employment_status <> 'zatrudniony'
  AND c.internship_status <> 'w_trakcie'
```

Reszta zapytania (LEFT JOIN kontaktów, `MAX(contact_at)`, `HAVING last_at IS NULL
OR last_at < ?`) bez zmian. Sygnatura metody bez zmian — nadal przyjmuje `days`.

### 3. UI

- **Ustawienia** (`settings_page.py`): nowe pole liczbowe
  „Przypominaj po ilu dniach bez kontaktu" (spinbox 1–365, domyślnie bieżąca
  wartość ustawienia). Zapis przez `set_setting("follow_up_days", …)`.
- **Dashboard** (`dashboard_page.py`):
  - próg pobierany z ustawień: `n = self._store.follow_up_days()`,
    wywołanie `self._store.no_contact_over(n)`;
  - tytuł panelu dynamiczny: `f"Bez kontaktu >{n} dni"` (ustawiany przy
    tworzeniu/odświeżeniu panelu, nie jako literał);
  - licznik (`counter`) bez zmian — pokazuje `len(no_contact)`.

## Przepływ danych

```
Ustawienia → set_setting("follow_up_days", N)
                        │
Dashboard.refresh() → n = follow_up_days()
                    → no_contact_over(n)
                    → [(client, days), …]  (aktywni, nie-zatrudnieni, nie-staż)
                        │
nowy wpis w panelu Kontakt → last_at rośnie → klient znika przy kolejnym refresh
```

## Przypadki brzegowe

- Brak wpisu `follow_up_days` w bazie → traktuj jak 30.
- Wartość „0"/ujemna/tekst → fallback 30 (walidacja).
- Klient bez żadnego kontaktu → nadal na liście (`last_at IS NULL`), o ile
  aktywny i nie zatrudniony/na stażu.
- Zmiana N w Ustawieniach → widoczna po odświeżeniu Dashboardu.
- Klient zatrudniony ORAZ na stażu → wykluczony (dowolny z warunków wystarcza).

## Testy (pytest)

Rozszerzyć testy repozytorium/DataStore:

1. `no_contact_over(N)` z różnym N — granice: ostatni kontakt dokładnie N dni,
   N-1 (nieobecny), N+1 (obecny).
2. Klient `employment_status='zatrudniony'` — **nieobecny** na liście.
3. Klient `internship_status='w_trakcie'` — **nieobecny** na liście.
4. Klient `bez_pracy` + `internship_status='brak'`, kontakt >N dni — **obecny**.
5. Nowy wpis kontaktu z datą < N dni → klient znika z wyniku.
6. `follow_up_days()` — brak ustawienia → 30; wartość spoza zakresu → 30;
   poprawna wartość → zwraca int.

## Pliki do zmiany

- `src/repositories/activities.py` — warunek wykluczenia w `no_contact_over`.
- `src/services/store.py` — helper `follow_up_days()` (odczyt + walidacja).
- `src/ui/pages/settings_page.py` — pole progu + zapis.
- `src/ui/pages/dashboard_page.py` — próg z ustawień + dynamiczny tytuł.
- `tests/` — nowe/rozszerzone przypadki.

## Decyzja do potwierdzenia (review gate)

Czy specyfikacja ma obejmować **wykluczenie zatrudnionych/stażystów** (sekcja 2)?
- **TAK** (domyślnie w tym spec-u): rzeczywistość dogoni opisaną regułę.
- **NIE**: usuwamy sekcję 2, zostaje sam konfigurowalny próg N; zmienia się tylko
  `dashboard_page.py` + `settings_page.py` + helper w `store.py`.
