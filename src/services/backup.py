"""Kopie zapasowe: ZIP z bazą, zdjęciami i ustawieniami (DATABASE.md).

Automatyczna raz dziennie, zachowuje 10 ostatnich kopii. Restore odtwarza
zawartość katalogu danych z wybranego archiwum.
"""
from __future__ import annotations

import shutil
import zipfile
from datetime import date, datetime
from pathlib import Path

from config import data_dir, db_path, photos_dir

BACKUP_PREFIX = "ClientWorkbench_backup_"
KEEP_LAST = 10


def backups_dir() -> Path:
    path = data_dir() / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_backups() -> list[Path]:
    return sorted(backups_dir().glob(f"{BACKUP_PREFIX}*.zip"), reverse=True)


def create_backup() -> Path:
    """Tworzy archiwum ZIP z bazą, katalogiem photos i plikiem ustawień."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    target = backups_dir() / f"{BACKUP_PREFIX}{stamp}.zip"
    base = data_dir()

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        db = db_path()
        if db.exists():
            zf.write(db, db.name)
        # WAL/SHM, jeśli istnieją (spójność danych po zamknięciu połączenia)
        for suffix in ("-wal", "-shm"):
            side = db.with_name(db.name + suffix)
            if side.exists():
                zf.write(side, side.name)
        photos = photos_dir()
        for photo in photos.glob("*"):
            if photo.is_file():
                zf.write(photo, f"photos/{photo.name}")
        settings = base / "settings.json"
        if settings.exists():
            zf.write(settings, settings.name)

    _prune_old()
    return target


def _prune_old() -> None:
    backups = list_backups()
    for old in backups[KEEP_LAST:]:
        old.unlink(missing_ok=True)


def auto_daily_backup() -> Path | None:
    """Tworzy kopię, jeśli dziś jeszcze żadnej nie wykonano. Zwraca ścieżkę lub None."""
    today = date.today().strftime("%Y-%m-%d")
    for backup in list_backups():
        if backup.name.startswith(f"{BACKUP_PREFIX}{today}"):
            return None
    return create_backup()


def restore_backup(archive: str | Path) -> None:
    """Odtwarza dane z archiwum. Baza musi być zamknięta przed wywołaniem."""
    archive = Path(archive)
    base = data_dir()
    with zipfile.ZipFile(archive, "r") as zf:
        names = zf.namelist()
        # usuń bieżące zdjęcia, aby odtworzenie było czyste
        if any(n.startswith("photos/") for n in names):
            for photo in photos_dir().glob("*"):
                if photo.is_file():
                    photo.unlink(missing_ok=True)
        for name in names:
            if name.startswith("photos/"):
                dest = photos_dir() / Path(name).name
            else:
                dest = base / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
