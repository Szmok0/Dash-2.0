"""Zrzuty ekranu Dashboardu i Karty klienta w 1920x1080 oraz 1366x768.

Uruchamiane offscreen (QT_QPA_PLATFORM=offscreen) — renderuje okno do PNG.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# świeża baza tymczasowa z danymi demo — zrzuty nie ruszają danych roboczych
_tmp = tempfile.mkdtemp(prefix="cw_screens_")
os.environ["CW_DATA_DIR"] = _tmp

from PySide6.QtCore import QEvent
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from ui.windows.main_window import MainWindow

OUT_DIR = ROOT / "docs" / "screenshots"


def grab(window: MainWindow, name: str) -> None:
    # dokończ odroczone usuwanie widgetów przed renderem
    for _ in range(3):
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)
        QApplication.processEvents()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}.png"
    window.grab().save(str(path))
    print(f"Zapisano: {path}")


def main() -> None:
    app = QApplication(sys.argv)
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    sys.path.insert(0, str(ROOT / "tools"))
    from seed_demo import seed
    from services.store import DataStore

    seed(DataStore())

    window = MainWindow()
    window.show()

    for width, height, suffix, collapsed in (
        (1920, 1080, "1920x1080", False),
        (1366, 768, "1366x768", True),
    ):
        window.resize(width, height)
        window.sidebar.set_collapsed(collapsed)

        window.navigate("dashboard")
        grab(window, f"dashboard_{suffix}")

        window.open_client(1)  # klientka ze zdjęciem i długą notatką
        grab(window, f"karta_klienta_{suffix}")

    # bonus: motyw jasny na 1920x1080
    window.resize(1920, 1080)
    window.sidebar.set_collapsed(False)
    window.toggle_theme()
    window.navigate("dashboard")
    grab(window, "dashboard_1920x1080_light")


if __name__ == "__main__":
    main()
