PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS clients (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 external_id TEXT NOT NULL UNIQUE,
 first_name TEXT NOT NULL,
 last_name TEXT NOT NULL,
 phone TEXT, email TEXT, recruitment_date TEXT, ipd_date TEXT,
 cv_status TEXT NOT NULL DEFAULT 'nieaktualne',
 ipd_status TEXT NOT NULL DEFAULT 'nieaktualne',
 employment_status TEXT NOT NULL DEFAULT 'bez_pracy',
 internship_status TEXT NOT NULL DEFAULT 'brak',
 client_status TEXT NOT NULL DEFAULT 'aktywny',
 dm TEXT, aneks TEXT,
 dz TEXT, jc TEXT, rp TEXT, psychologist TEXT, lawyer TEXT,
 gender TEXT, disability_degree TEXT, disability_symbol TEXT,
 combined_symbols TEXT, education TEXT, certificate_valid_until TEXT,
 desired_job TEXT, import_comment TEXT,
 requires_attention INTEGER NOT NULL DEFAULT 0,
 attention_note TEXT, photo_path TEXT, last_import_at TEXT,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL,
 title TEXT NOT NULL,
 action_type TEXT NOT NULL DEFAULT 'notatka',
 due_at TEXT,
 priority TEXT NOT NULL,
 status TEXT NOT NULL,
 note TEXT,
 completed_at TEXT,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS contacts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL,
 contact_type TEXT NOT NULL,
 contact_at TEXT NOT NULL,
 status TEXT NOT NULL,
 note TEXT,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS trainings (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL,
 name TEXT NOT NULL,
 training_date TEXT NOT NULL,
 training_type TEXT NOT NULL,
 status TEXT NOT NULL,
 note TEXT,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS notes (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL,
 content TEXT NOT NULL,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS imports (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 file_name TEXT NOT NULL,
 imported_at TEXT NOT NULL,
 total_rows INTEGER NOT NULL,
 inserted_rows INTEGER NOT NULL,
 updated_rows INTEGER NOT NULL,
 unchanged_rows INTEGER NOT NULL,
 error_rows INTEGER NOT NULL,
 details_json TEXT
);

CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);

CREATE INDEX IF NOT EXISTS idx_clients_external_id ON clients(external_id);
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(client_status);
CREATE INDEX IF NOT EXISTS idx_tasks_client_status_due ON tasks(client_id, status, due_at);
CREATE INDEX IF NOT EXISTS idx_contacts_client_date ON contacts(client_id, contact_at);
CREATE INDEX IF NOT EXISTS idx_trainings_client_date ON trainings(client_id, training_date);
CREATE INDEX IF NOT EXISTS idx_notes_client_date ON notes(client_id, created_at);
