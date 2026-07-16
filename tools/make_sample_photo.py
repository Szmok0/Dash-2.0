"""Generuje neutralne przykładowe zdjęcie klienta do danych testowych Sprintu 0."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QLinearGradient, QPainter, QPixmap


def main() -> None:
    app = QGuiApplication(sys.argv)
    size = 240
    pix = QPixmap(size, size)

    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor("#3A4A6B"))
    gradient.setColorAt(1.0, QColor("#22304C"))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.fillRect(0, 0, size, size, QBrush(gradient))

    # sylwetka portretowa (neutralna, bez rysów twarzy)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#8FA3C8"))
    painter.drawEllipse(QPointF(size / 2, size * 0.38), size * 0.17, size * 0.17)
    painter.drawEllipse(QRectF(size * 0.22, size * 0.62, size * 0.56, size * 0.55))
    painter.end()

    out = Path(__file__).resolve().parent.parent / "resources" / "photos" / "client_AS-1024.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out))
    print(f"Zapisano: {out}")


if __name__ == "__main__":
    main()
