"""Wspólne widgety kalendarza: klikalne wpisy i panel szczegółów dnia."""
from __future__ import annotations

from datetime import date
from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...models.calendar_event import CalendarEvent
from ..styles import palette

PL_WEEKDAYS = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
PL_MONTHS = [
    "styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec",
    "lipiec", "sierpień", "wrzesień", "październik", "listopad", "grudzień",
]


class EventChip(QFrame):
    """Pojedynczy wpis w kalendarzu. Kliknięcie prowadzi do klienta.

    Pokazuje godzinę, nazwisko i typ działania (PRODUCT.md). Lewa krawędź
    koloruje się wg typu (kolory niosą informację, UI.md).
    """

    clicked = Signal(int)  # client_id

    def __init__(self, event: CalendarEvent, compact: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._client_id = event.client_id
        self.setObjectName("EventChip")
        self.setCursor(Qt.PointingHandCursor)
        color = palette.KIND_COLORS.get(event.kind.value, palette.ACCENT)
        self.setStyleSheet(
            f"""
            QFrame#EventChip {{
                background: {palette.CARD};
                border-left: 3px solid {color};
                border-radius: 4px;
            }}
            QFrame#EventChip:hover {{ background: {palette.LINE}; }}
            QLabel {{ background: transparent; color: {palette.TEXT}; }}
            QLabel#meta {{ color: {palette.TEXT_MUTED}; }}
            """
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 3, 6, 3)
        lay.setSpacing(6)

        time_label = event.time_label()
        if compact:
            text = f"{time_label + '  ' if time_label else ''}{event.client_name}"
            lbl = QLabel(text)
            lbl.setToolTip(f"{event.client_name} — {event.kind.value}"
                           + (f" — {time_label}" if time_label else ""))
            lbl.setStyleSheet(f"color: {palette.TEXT}; font-size: 11px;")
            lay.addWidget(lbl, 1)
        else:
            if time_label:
                t = QLabel(time_label)
                t.setFixedWidth(42)
                t.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 13px;")
                lay.addWidget(t)
            name = QLabel(event.client_name)
            name.setStyleSheet(f"color: {palette.TEXT}; font-size: 13px; font-weight: 600;")
            lay.addWidget(name)
            kind = QLabel(event.kind.value + (f" · {event.title}" if event.title else ""))
            kind.setObjectName("meta")
            kind.setStyleSheet(f"color: {palette.TEXT_MUTED}; font-size: 12px;")
            lay.addWidget(kind, 1)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 (Qt override)
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._client_id)
        super().mousePressEvent(event)


class DayDetailDialog(QDialog):
    """Panel pełnej listy wpisów dla jednego dnia.

    Otwiera się po kliknięciu dnia w widoku miesiąca (naprawa: dotąd nie dało
    się kliknąć dnia, żeby zobaczyć jego zawartość). Każdy wpis klikalny
    prowadzi do klienta.
    """

    client_selected = Signal(int)

    def __init__(self, day: date, events: List[CalendarEvent], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        weekday = PL_WEEKDAYS[day.weekday()]
        self.setWindowTitle(f"{weekday}, {day.day} {PL_MONTHS[day.month - 1]} {day.year}")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"QDialog {{ background: {palette.PANEL}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        header = QLabel(f"{weekday}, {day.day} {PL_MONTHS[day.month - 1]} {day.year}")
        header.setStyleSheet(f"color: {palette.TEXT}; font-size: 18px; font-weight: 700;")
        root.addWidget(header)

        count = QLabel(f"{len(events)} " + _pl_entries(len(events)))
        count.setStyleSheet(f"color: {palette.TEXT_MUTED}; font-size: 12px;")
        root.addWidget(count)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        inner = QWidget()
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(0, 0, 6, 0)
        inner_lay.setSpacing(6)

        if not events:
            empty = QLabel("Brak wpisów w tym dniu.")
            empty.setStyleSheet(f"color: {palette.TEXT_MUTED}; font-size: 13px; padding: 12px 0;")
            inner_lay.addWidget(empty)
        else:
            for ev in sorted(events, key=lambda e: (e.all_day is False, e.when)):
                chip = EventChip(ev, compact=False)
                chip.clicked.connect(self._on_event_clicked)
                inner_lay.addWidget(chip)
        inner_lay.addStretch(1)
        scroll.setWidget(inner)
        scroll.setMinimumHeight(240)
        root.addWidget(scroll, 1)

        close_btn = QPushButton("Zamknij")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {palette.CARD}; color: {palette.TEXT};
                border: 1px solid {palette.LINE}; border-radius: 8px;
                padding: 8px 18px; font-size: 13px;
            }}
            QPushButton:hover {{ background: {palette.LINE}; }}
            """
        )
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    def _on_event_clicked(self, client_id: int) -> None:
        self.client_selected.emit(client_id)
        self.accept()


def _pl_entries(n: int) -> str:
    """Poprawna forma słowa 'wpis' po polsku."""
    if n == 1:
        return "wpis"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return "wpisy"
    return "wpisów"


def make_vscroll(widget: QWidget) -> QScrollArea:
    """Zawija widget w pionowo przewijalny obszar bez ramki."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setStyleSheet("QScrollArea { background: transparent; }")
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    scroll.setWidget(widget)
    return scroll
