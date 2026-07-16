"""Monochromatyczne ikony outline rysowane QPainterem (UI.md: bez emoji).

Używane wyłącznie przy typie działania w tabeli zadań oraz w zwiniętym
sidebarze.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


def _painter(pix: QPixmap, color: str, width: float = 1.6) -> QPainter:
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    return painter


def make_icon(name: str, color: str, size: int = 18) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = _painter(pix, color)
    s = float(size)

    if name == "telefon":
        p.drawRoundedRect(QRectF(s * 0.30, s * 0.12, s * 0.40, s * 0.76), s * 0.10, s * 0.10)
        p.drawLine(QPointF(s * 0.42, s * 0.74), QPointF(s * 0.58, s * 0.74))
    elif name == "spotkanie":
        p.drawEllipse(QRectF(s * 0.16, s * 0.18, s * 0.24, s * 0.24))
        p.drawEllipse(QRectF(s * 0.60, s * 0.18, s * 0.24, s * 0.24))
        p.drawArc(QRectF(s * 0.08, s * 0.50, s * 0.40, s * 0.44), 0, 180 * 16)
        p.drawArc(QRectF(s * 0.52, s * 0.50, s * 0.40, s * 0.44), 0, 180 * 16)
    elif name == "email":
        p.drawRoundedRect(QRectF(s * 0.12, s * 0.22, s * 0.76, s * 0.56), s * 0.08, s * 0.08)
        p.drawLine(QPointF(s * 0.14, s * 0.26), QPointF(s * 0.50, s * 0.54))
        p.drawLine(QPointF(s * 0.86, s * 0.26), QPointF(s * 0.50, s * 0.54))
    elif name == "cv":
        p.drawRoundedRect(QRectF(s * 0.22, s * 0.10, s * 0.56, s * 0.80), s * 0.08, s * 0.08)
        p.drawLine(QPointF(s * 0.32, s * 0.34), QPointF(s * 0.68, s * 0.34))
        p.drawLine(QPointF(s * 0.32, s * 0.50), QPointF(s * 0.68, s * 0.50))
        p.drawLine(QPointF(s * 0.32, s * 0.66), QPointF(s * 0.56, s * 0.66))
    elif name == "szkolenie":
        p.drawPolyline(
            [
                QPointF(s * 0.10, s * 0.38),
                QPointF(s * 0.50, s * 0.18),
                QPointF(s * 0.90, s * 0.38),
                QPointF(s * 0.50, s * 0.58),
                QPointF(s * 0.10, s * 0.38),
            ]
        )
        p.drawLine(QPointF(s * 0.26, s * 0.50), QPointF(s * 0.26, s * 0.72))
        p.drawArc(QRectF(s * 0.26, s * 0.58, s * 0.48, s * 0.30), 180 * 16, 180 * 16)
    elif name == "notatka":
        p.drawRoundedRect(QRectF(s * 0.16, s * 0.14, s * 0.68, s * 0.72), s * 0.08, s * 0.08)
        p.drawLine(QPointF(s * 0.28, s * 0.36), QPointF(s * 0.72, s * 0.36))
        p.drawLine(QPointF(s * 0.28, s * 0.52), QPointF(s * 0.72, s * 0.52))
        p.drawLine(QPointF(s * 0.28, s * 0.68), QPointF(s * 0.56, s * 0.68))
    elif name == "dashboard":
        p.drawRoundedRect(QRectF(s * 0.12, s * 0.12, s * 0.32, s * 0.44), s * 0.06, s * 0.06)
        p.drawRoundedRect(QRectF(s * 0.56, s * 0.12, s * 0.32, s * 0.28), s * 0.06, s * 0.06)
        p.drawRoundedRect(QRectF(s * 0.12, s * 0.68, s * 0.32, s * 0.20), s * 0.06, s * 0.06)
        p.drawRoundedRect(QRectF(s * 0.56, s * 0.52, s * 0.32, s * 0.36), s * 0.06, s * 0.06)
    elif name == "klienci":
        p.drawEllipse(QRectF(s * 0.34, s * 0.12, s * 0.32, s * 0.32))
        p.drawArc(QRectF(s * 0.18, s * 0.52, s * 0.64, s * 0.52), 0, 180 * 16)
    elif name == "kalendarz":
        p.drawRoundedRect(QRectF(s * 0.14, s * 0.18, s * 0.72, s * 0.68), s * 0.08, s * 0.08)
        p.drawLine(QPointF(s * 0.14, s * 0.38), QPointF(s * 0.86, s * 0.38))
        p.drawLine(QPointF(s * 0.34, s * 0.10), QPointF(s * 0.34, s * 0.24))
        p.drawLine(QPointF(s * 0.66, s * 0.10), QPointF(s * 0.66, s * 0.24))
    elif name == "analityka":
        p.drawLine(QPointF(s * 0.14, s * 0.12), QPointF(s * 0.14, s * 0.86))
        p.drawLine(QPointF(s * 0.14, s * 0.86), QPointF(s * 0.88, s * 0.86))
        p.drawPolyline(
            [
                QPointF(s * 0.24, s * 0.66),
                QPointF(s * 0.44, s * 0.44),
                QPointF(s * 0.60, s * 0.56),
                QPointF(s * 0.82, s * 0.26),
            ]
        )
    elif name == "import":
        p.drawLine(QPointF(s * 0.50, s * 0.12), QPointF(s * 0.50, s * 0.60))
        p.drawPolyline(
            [QPointF(s * 0.34, s * 0.46), QPointF(s * 0.50, s * 0.62), QPointF(s * 0.66, s * 0.46)]
        )
        p.drawPolyline(
            [
                QPointF(s * 0.16, s * 0.64),
                QPointF(s * 0.16, s * 0.86),
                QPointF(s * 0.84, s * 0.86),
                QPointF(s * 0.84, s * 0.64),
            ]
        )
    elif name == "ustawienia":
        p.drawEllipse(QRectF(s * 0.36, s * 0.36, s * 0.28, s * 0.28))
        p.drawEllipse(QRectF(s * 0.18, s * 0.18, s * 0.64, s * 0.64))
    else:
        p.drawEllipse(QRectF(s * 0.25, s * 0.25, s * 0.5, s * 0.5))

    p.end()
    return QIcon(pix)
