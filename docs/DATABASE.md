# DATABASE.md

## Technologia
SQLite, plik `data/client_workbench.db`. PRAGMA foreign_keys=ON, WAL, transakcje dla importu i backupu.

## Tabele

### clients
- id INTEGER PK AUTOINCREMENT
- external_id TEXT NOT NULL UNIQUE
- first_name TEXT NOT NULL
- last_name TEXT NOT NULL
- phone TEXT
- email TEXT
- recruitment_date TEXT
- ipd_date TEXT
- cv_status TEXT NOT NULL DEFAULT 'nieaktualne'
- employment_status TEXT NOT NULL DEFAULT 'bez_pracy'
- internship_status TEXT NOT NULL DEFAULT 'brak'
- client_status TEXT NOT NULL DEFAULT 'aktywny'
- dz, jc, rp, psychologist, lawyer TEXT
- gender TEXT
- disability_degree TEXT
- disability_symbol TEXT
- combined_symbols TEXT
- education TEXT
- certificate_valid_until TEXT
- desired_job TEXT
- import_comment TEXT
- requires_attention INTEGER NOT NULL DEFAULT 0
- attention_note TEXT
- photo_path TEXT
- last_import_at TEXT
- created_at TEXT NOT NULL
- updated_at TEXT NOT NULL

### tasks
- id INTEGER PK
- client_id INTEGER NOT NULL FK clients
- title TEXT NOT NULL
- due_at TEXT
- priority TEXT NOT NULL
- status TEXT NOT NULL
- note TEXT
- completed_at TEXT
- created_at, updated_at TEXT NOT NULL

Priorytety: niski/sredni/wysoki.
Statusy: do_zrobienia/w_trakcie/zakonczone/anulowane/oczekuje_na.

### contacts
- id INTEGER PK
- client_id INTEGER NOT NULL FK clients
- contact_type TEXT NOT NULL
- contact_at TEXT NOT NULL
- status TEXT NOT NULL
- note TEXT
- created_at, updated_at TEXT NOT NULL

Typy: telefon/spotkanie/email/sms/teams/inne.

### trainings
- id INTEGER PK
- client_id INTEGER NOT NULL FK clients
- name TEXT NOT NULL
- training_date TEXT NOT NULL
- training_type TEXT NOT NULL
- status TEXT NOT NULL
- note TEXT
- created_at, updated_at TEXT NOT NULL

Rodzaje: indywidualne/grupowe/wuz/it/adaptacyjne/elearning.
Statusy: planowane/ukonczyl/nie_ukonczyl.

### notes
- id INTEGER PK
- client_id INTEGER NOT NULL FK clients
- content TEXT NOT NULL
- created_at, updated_at TEXT NOT NULL

Moduł Notatki pobiera notes oraz contacts.note.

### imports
file_name, imported_at, total_rows, inserted_rows, updated_rows, unchanged_rows, error_rows, details_json.

### settings
key TEXT PK, value TEXT.

## Zapytania
Dashboard open tasks: aktywni klienci, zadania nie zakończone i nie anulowane, sortowanie priorytet DESC, termin ASC.
Completed today: completed_at w bieżącym dniu.
Bez kontaktu >30 dni: ostatni kontakt starszy niż próg; klient bez kontaktów również trafia na listę.
Wymaga uwagi: requires_attention=1.
Notatki klienta: UNION ALL notes + contacts.note, sortowanie malejąco po dacie.

## Indeksy
clients(external_id), clients(last_name, first_name), clients(client_status), tasks(client_id,status,due_at), contacts(client_id,contact_at), trainings(client_id,training_date), notes(client_id,created_at).

## Zdjęcia
Katalog `data/photos/`. Przy dodaniu program kopiuje plik, zmienia nazwę na `client_<external_id>.<ext>`, zapisuje względną ścieżkę. Przy zmianie klienta komponent obrazu zawsze resetuje źródło. Brak zdjęcia = NULL i pusty placeholder.

## Backup
`data/backups/ClientWorkbench_backup_YYYY-MM-DD_HH-mm.zip`, zawiera bazę, photos i ustawienia. Automatycznie raz dziennie, zachowuje 10 ostatnich kopii.
