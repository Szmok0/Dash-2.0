"""Punkt wejścia aplikacji Client Workbench."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from config import APP_NAME, data_dir
from ui.windows.main_window import MainWindow

RESOURCES = Path(__file__).resolve().parent.parent / "resources"


def _setup_logging() -> None:
    log_dir = data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_dir / "app.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> int:
    _setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    icon_path = RESOURCES / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))

    # automatyczna kopia zapasowa raz dziennie
    try:
        from services.backup import auto_daily_backup

        window.store.checkpoint()
        auto_daily_backup()
    except Exception:  # pragma: no cover
        logging.getLogger(__name__).exception("Automatyczna kopia zapasowa nie powiodła się")

    # wykrywanie bezczynności dla blokady PIN
    app.installEventFilter(window)

    window.show()
    window.start_security()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
