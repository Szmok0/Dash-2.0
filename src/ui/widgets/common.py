"""Reusable Sprint 0 widgets."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget

PRIORITY_COLORS = {"wysoki": "#E85D68", "sredni": "#E8B44C", "niski": "#4FBF78"}
STATUS_COLORS = {"do zrobienia": "#4C8DFF", "w trakcie": "#8B7CF6", "zakonczone": "#7B8492", "oczekuje_na": "#E8B44C", "anulowane": "#7B8492"}

class Pill(QLabel):
    def __init__(self, text: str, color: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background:{color}; color:#121722; border-radius:9px; padding:3px 8px; font-weight:700; font-size:11px;")

class Module(QFrame):
    clicked = Signal()
    def __init__(self, title: str, count: int, lines: list[str], add_text: str = "+ Dodaj") -> None:
        super().__init__()
        self.setObjectName("Module")
        self.setMinimumHeight(160)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        header = QHBoxLayout()
        title_label = QLabel(f"{title}  {count}")
        title_label.setObjectName("SectionTitle")
        add = QPushButton(add_text)
        add.setFixedWidth(76)
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(add)
        layout.addLayout(header)
        for line in lines[:5]:
            label = QLabel(line)
            label.setWordWrap(True)
            label.setStyleSheet("border-top:1px solid #2B3245; padding-top:5px;")
            layout.addWidget(label)
        layout.addStretch()

    def mousePressEvent(self, event):  # type: ignore[override]
        self.clicked.emit()
        super().mousePressEvent(event)

def photo_placeholder(has_photo: bool) -> QLabel:
    label = QLabel()
    label.setFixedSize(112, 112)
    pixmap = QPixmap(112, 112)
    pixmap.fill(QColor("#202737"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QColor("#2B3245"))
    painter.setBrush(QColor("#2B3245" if not has_photo else "#4C8DFF"))
    painter.drawRoundedRect(8, 8, 96, 96, 12, 12)
    if has_photo:
        painter.setPen(QColor("#F2F4F7")); painter.setFont(QFont("Segoe UI", 28, QFont.Bold)); painter.drawText(pixmap.rect(), Qt.AlignCenter, "foto")
    painter.end()
    label.setPixmap(pixmap)
    return label
