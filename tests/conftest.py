"""Konfiguracja testów — izolowany katalog danych na każdy test."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Świeży DataStore na tymczasowej bazie, zasiany danymi demo."""
    monkeypatch.setenv("CW_DATA_DIR", str(tmp_path))
    # config cache'uje ścieżki przez zmienną środowiskową — importujemy po ustawieniu
    from services.store import DataStore
    from seed_demo import seed

    ds = DataStore()
    seed(ds)
    yield ds
    ds.close()
