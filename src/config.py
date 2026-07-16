"""Stałe konfiguracyjne aplikacji Client Workbench (Sprint 0)."""
from __future__ import annotations

APP_NAME = "Client Workbench"
APP_VERSION = "0.1.0-sprint0"

# Wymiary wg UI.md
SIDEBAR_WIDTH = 230
SIDEBAR_COLLAPSED_WIDTH = 60
HEADER_HEIGHT = 60
SEARCH_WIDTH = 360
SEARCH_HEIGHT = 38
TABLE_ROW_HEIGHT = 40
TABLE_HEADER_HEIGHT = 38
CARD_RADIUS = 10
FORM_WIDTH = 560

# Rozdzielczość bazowa
BASE_WINDOW_SIZE = (1920, 1080)
MIN_WINDOW_SIZE = (1366, 768)

# Maksymalna szerokość treści na dużych monitorach (UI.md: 27")
MAX_CONTENT_WIDTH = 1720

# --- katalog danych (BUILD.md: dane poza katalogiem programu) ---
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    """Katalog danych: zmienna CW_DATA_DIR lub ./data obok repozytorium."""
    path = Path(os.environ.get("CW_DATA_DIR", _ROOT / "data"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def photos_dir() -> Path:
    path = data_dir() / "photos"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "client_workbench.db"
