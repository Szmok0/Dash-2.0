"""Wypełnia bazę danymi demonstracyjnymi (do testów i zrzutów ekranu).

Użycie:  python tools/seed_demo.py   (opcjonalnie CW_DATA_DIR=/ścieżka)
Odmawia działania, jeśli baza zawiera już klientów.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data.sample_data import RESOURCES_DIR, build_demo_data
from services.store import DataStore


def seed(store: DataStore) -> None:
    if store.clients:
        print("Baza zawiera już klientów — seed pominięty.")
        return

    data = build_demo_data()
    id_map: dict[int, int] = {}
    for client in data.clients:
        old_id = client.id
        id_map[old_id] = store.add_client(client)

    for task in data.tasks:
        task.client_id = id_map[task.client_id]
        store.add_task(task)
    for contact in data.contacts:
        contact.client_id = id_map[contact.client_id]
        store.add_contact(contact)
    for training in data.trainings:
        training.client_id = id_map[training.client_id]
        store.add_training(training)
    for note in data.notes:
        note.client_id = id_map[note.client_id]
        store.add_note(note)

    # zdjęcie demonstracyjne dla Anny Kowalskiej
    photo = RESOURCES_DIR / "photos" / "client_AS-1024.png"
    if photo.exists():
        anna = store.find_by_external_id("AS-1024")
        if anna is not None:
            store.set_client_photo(anna, str(photo))

    print(f"Zasiano {len(data.clients)} klientów z danymi powiązanymi.")


if __name__ == "__main__":
    seed(DataStore())
