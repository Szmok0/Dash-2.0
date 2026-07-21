"""Strona Kalendarz.

Kalendarz to wyłącznie wizualizacja dat z zadań, kontaktów/spotkań i szkoleń
(PRODUCT.md). Dostępne widoki: Miesiąc i Tydzień. Wpis pokazuje nazwisko, typ
działania i godzinę; kliknięcie prowadzi do klienta (sygnał `client_selected`).

Naprawione w tej wersji:
1. Widok miesiąca — kliknięcie dnia otwiera panel z pełną listą wpisów tego
   dnia (wcześniej dnia nie dało się kliknąć, by zobaczyć zawartość).
2. Widok tygodnia — 7 kolumn dni w poziomo przewijalnym obszarze, więc na
   węższym ekranie da się przewinąć w bok do wszystkich dni (wcześniej widać
   było tylko 2–3 dni).
"""
from __future__ import annotations

import calendar as _calendar
from datetime import date, timedelta
from typing import Callable, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ...models.calendar_event import CalendarEvent
from ..styles import palette
from ..widgets.calendar_widgets import (
    PL_MONTHS,
    DayDetailDialog,
    EventChip,
    make_vscroll,
)

# (start, end) -> wpisy w tym zakresie dni (włącznie).
EventProvider = Callable[[date, date], List[CalendarEvent]]

WEEKDAY_ABBR = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nie"]
MAX_CHIPS_IN_CELL = 3
WEEK_COLUMN_WIDTH = 210  # stała szerokość kolumny dnia w widoku tygodnia


def _group_by_day(events: List[CalendarEvent]) -> Dict[date, List[CalendarEvent]]:
    grouped: Dict[date, List[CalendarEvent]] = {}
    for ev in events:
        grouped.setdefault(ev.day, []).append(ev)
    for day_events in grouped.values():
        day_events.sort(key=lambda e: (e.all_day is False, e.when))
    return grouped


# --------------------------------------------------------------------------- #
# Widok miesiąca
# --------------------------------------------------------------------------- #
class _DayCell(QFrame):
    """Komórka dnia w siatce miesiąca. Klik w tło otwiera szczegóły dnia."""

    day_clicked = Signal(date)
    client_selected = Signal(int)

    def __init__(self, day: date, in_month: bool, is_today: bool,
                 events: List[CalendarEvent], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._day = day
        self.setObjectName("DayCell")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        border = palette.ACCENT if is_today else palette.LINE
        bg = palette.CARD if in_month else palette.PANEL
        num_color = palette.TEXT if in_month else palette.TEXT_MUTED
        self.setStyleSheet(
            f"""
            QFrame#DayCell {{
                background: {bg};
                border: 1px solid {palette.LINE};
                {'border: 1px solid ' + palette.ACCENT + ';' if is_today else ''}
            }}
            QFrame#DayCell:hover {{ background: {palette.LINE}; }}
            """
        )
        _ = border

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 6)
        lay.setSpacing(3)

        head = QHBoxLayout()
        num = QLabel(str(day.day))
        weight = "700" if is_today else "600"
        num.setStyleSheet(
            f"color: {palette.ACCENT if is_today else num_color};"
            f"font-size: 13px; font-weight: {weight}; background: transparent;"
        )
        head.addWidget(num)
        head.addStretch(1)
        if events:
            badge = QLabel(str(len(events)))
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(18, 18)
            badge.setStyleSheet(
                f"color: {palette.TEXT}; background: {palette.PANEL};"
                f"border-radius: 9px; font-size: 10px; font-weight: 600;"
            )
            head.addWidget(badge)
        lay.addLayout(head)

        for ev in events[:MAX_CHIPS_IN_CELL]:
            chip = EventChip(ev, compact=True)
            chip.clicked.connect(self.client_selected.emit)
            lay.addWidget(chip)

        hidden = len(events) - MAX_CHIPS_IN_CELL
        if hidden > 0:
            more = QLabel(f"+{hidden} więcej")
            more.setStyleSheet(
                f"color: {palette.TEXT_MUTED}; font-size: 11px; background: transparent;"
            )
            lay.addWidget(more)
        lay.addStretch(1)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.day_clicked.emit(self._day)
        super().mousePressEvent(event)


class MonthView(QWidget):
    """Siatka 7×6 dni. Klik dnia -> panel szczegółów (`DayDetailDialog`)."""

    client_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(1)
        for col, name in enumerate(WEEKDAY_ABBR):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            weekend = col >= 5
            lbl.setStyleSheet(
                f"color: {palette.TEXT_MUTED if not weekend else palette.RED};"
                f"font-size: 12px; font-weight: 600; padding: 6px 0;"
                f"background: {palette.PANEL};"
            )
            self._grid.addWidget(lbl, 0, col)
        for col in range(7):
            self._grid.setColumnStretch(col, 1)
        for row in range(1, 7):
            self._grid.setRowStretch(row, 1)

    def render_month(self, anchor: date, events: List[CalendarEvent]) -> None:
        # Usuń stare komórki dni (zachowaj nagłówek w wierszu 0).
        for i in reversed(range(self._grid.count())):
            item = self._grid.itemAt(i)
            widget = item.widget()
            if widget is not None:
                pos = self._grid.getItemPosition(i)
                if pos[0] >= 1:  # row >= 1
                    widget.setParent(None)

        grouped = _group_by_day(events)
        today = date.today()
        first_of_month = anchor.replace(day=1)
        # Poniedziałek jako pierwszy dzień tygodnia.
        start = first_of_month - timedelta(days=first_of_month.weekday())

        for week in range(6):
            for dow in range(7):
                day = start + timedelta(days=week * 7 + dow)
                cell = _DayCell(
                    day=day,
                    in_month=(day.month == anchor.month),
                    is_today=(day == today),
                    events=grouped.get(day, []),
                )
                cell.day_clicked.connect(self._open_day)
                cell.client_selected.connect(self.client_selected.emit)
                self._grid.addWidget(cell, week + 1, dow)
        self._events_by_day = grouped

    def _open_day(self, day: date) -> None:
        events = self._events_by_day.get(day, [])
        dlg = DayDetailDialog(day, events, parent=self)
        dlg.client_selected.connect(self.client_selected.emit)
        dlg.exec()


# --------------------------------------------------------------------------- #
# Widok tygodnia (poziomo przewijalny)
# --------------------------------------------------------------------------- #
class _DayColumn(QFrame):
    """Jedna kolumna dnia o stałej szerokości w widoku tygodnia."""

    client_selected = Signal(int)

    def __init__(self, day: date, is_today: bool, events: List[CalendarEvent],
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DayColumn")
        self.setFixedWidth(WEEK_COLUMN_WIDTH)  # stała szerokość -> wymusza scroll w poziomie
        self.setStyleSheet(
            f"QFrame#DayColumn {{ background: {palette.CARD};"
            f"border: 1px solid {palette.LINE}; border-radius: 8px; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        weekend = day.weekday() >= 5
        name = QLabel(WEEKDAY_ABBR[day.weekday()])
        name.setStyleSheet(
            f"color: {palette.RED if weekend else palette.TEXT_MUTED};"
            f"font-size: 12px; font-weight: 600; background: transparent;"
        )
        num = QLabel(str(day.day))
        num.setStyleSheet(
            f"color: {palette.ACCENT if is_today else palette.TEXT};"
            f"font-size: 20px; font-weight: 700; background: transparent;"
        )
        header = QVBoxLayout()
        header.setSpacing(0)
        header.addWidget(name)
        header.addWidget(num)
        head_wrap = QFrame()
        head_wrap.setStyleSheet(
            f"background: transparent; border-bottom: 2px solid "
            f"{palette.ACCENT if is_today else palette.LINE};"
        )
        head_wrap.setLayout(header)
        head_inner = header
        head_inner.setContentsMargins(2, 0, 2, 6)
        lay.addWidget(head_wrap)

        events_box = QWidget()
        events_lay = QVBoxLayout(events_box)
        events_lay.setContentsMargins(0, 0, 4, 0)
        events_lay.setSpacing(6)
        if not events:
            empty = QLabel("—")
            empty.setAlignment(Qt.AlignHCenter)
            empty.setStyleSheet(f"color: {palette.TEXT_MUTED}; background: transparent;")
            events_lay.addWidget(empty)
        else:
            for ev in events:
                chip = EventChip(ev, compact=False)
                chip.clicked.connect(self.client_selected.emit)
                events_lay.addWidget(chip)
        events_lay.addStretch(1)
        lay.addWidget(make_vscroll(events_box), 1)


class WeekView(QWidget):
    """Tydzień jako 7 kolumn w poziomo przewijalnym obszarze.

    Naprawa: kolumny mają stałą szerokość i leżą w `QScrollArea`, dzięki czemu
    na węższym ekranie pokazuje się poziomy pasek przewijania i dostęp jest do
    wszystkich 7 dni (a nie tylko do 2–3 widocznych).
    """

    client_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            f"""
            QScrollArea {{ background: transparent; }}
            QScrollBar:horizontal {{
                background: {palette.PANEL}; height: 12px; margin: 0; border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {palette.LINE}; border-radius: 6px; min-width: 60px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: {palette.ACCENT}; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
            """
        )
        root.addWidget(self._scroll)

    def render_week(self, anchor: date, events: List[CalendarEvent]) -> None:
        grouped = _group_by_day(events)
        today = date.today()
        start = anchor - timedelta(days=anchor.weekday())  # poniedziałek

        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(4, 4, 4, 8)
        row.setSpacing(8)
        for i in range(7):
            day = start + timedelta(days=i)
            col = _DayColumn(day, is_today=(day == today), events=grouped.get(day, []))
            col.client_selected.connect(self.client_selected.emit)
            row.addWidget(col)
        row.addStretch(0)
        # Wymuś minimalną szerokość = suma kolumn, by pojawił się scroll poziomy.
        container.setMinimumWidth(7 * WEEK_COLUMN_WIDTH + 8 * 8)
        self._scroll.setWidget(container)


# --------------------------------------------------------------------------- #
# Strona kalendarza
# --------------------------------------------------------------------------- #
class CalendarPage(QWidget):
    """Pełna strona Kalendarz z przełącznikiem Miesiąc / Tydzień i nawigacją."""

    client_selected = Signal(int)  # emitowany po kliknięciu wpisu -> otwórz kartę klienta

    def __init__(self, event_provider: EventProvider, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._provider = event_provider
        self._anchor = date.today()
        self._mode = "month"

        self.setStyleSheet(f"background: {palette.BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        root.addLayout(self._build_toolbar())

        self._stack = QStackedWidget()
        self._month = MonthView()
        self._week = WeekView()
        self._month.client_selected.connect(self.client_selected.emit)
        self._week.client_selected.connect(self.client_selected.emit)
        self._stack.addWidget(self._month)
        self._stack.addWidget(self._week)
        root.addWidget(self._stack, 1)

        self.refresh()

    # -- toolbar ---------------------------------------------------------- #
    def _build_toolbar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(12)

        title = QLabel("Kalendarz")
        title.setStyleSheet(f"color: {palette.TEXT}; font-size: 24px; font-weight: 700;")
        bar.addWidget(title)

        bar.addSpacing(8)
        prev_btn = self._nav_button("‹")
        today_btn = self._nav_button("Dziś", wide=True)
        next_btn = self._nav_button("›")
        prev_btn.clicked.connect(lambda: self._shift(-1))
        next_btn.clicked.connect(lambda: self._shift(1))
        today_btn.clicked.connect(self._go_today)
        bar.addWidget(prev_btn)
        bar.addWidget(today_btn)
        bar.addWidget(next_btn)

        self._period_label = QLabel()
        self._period_label.setStyleSheet(
            f"color: {palette.TEXT}; font-size: 16px; font-weight: 600;"
        )
        bar.addWidget(self._period_label)

        bar.addStretch(1)

        self._month_btn = self._toggle_button("Miesiąc")
        self._week_btn = self._toggle_button("Tydzień")
        self._month_btn.clicked.connect(lambda: self._set_mode("month"))
        self._week_btn.clicked.connect(lambda: self._set_mode("week"))
        seg = QHBoxLayout()
        seg.setSpacing(0)
        seg.addWidget(self._month_btn)
        seg.addWidget(self._week_btn)
        wrap = QFrame()
        wrap.setStyleSheet(
            f"background: {palette.PANEL}; border: 1px solid {palette.LINE}; border-radius: 8px;"
        )
        wrap.setLayout(seg)
        seg.setContentsMargins(3, 3, 3, 3)
        bar.addWidget(wrap)
        return bar

    def _nav_button(self, text: str, wide: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(34)
        btn.setFixedWidth(64 if wide else 34)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {palette.PANEL}; color: {palette.TEXT};
                border: 1px solid {palette.LINE}; border-radius: 8px;
                font-size: 15px;
            }}
            QPushButton:hover {{ background: {palette.LINE}; }}
            """
        )
        return btn

    def _toggle_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(28)
        btn.setMinimumWidth(84)
        self._style_toggle(btn, active=False)
        return btn

    def _style_toggle(self, btn: QPushButton, active: bool) -> None:
        if active:
            btn.setStyleSheet(
                f"QPushButton {{ background: {palette.ACCENT}; color: white;"
                f"border: none; border-radius: 6px; font-size: 13px; font-weight: 600; }}"
            )
        else:
            btn.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {palette.TEXT_MUTED};"
                f"border: none; border-radius: 6px; font-size: 13px; }}"
                f"QPushButton:hover {{ color: {palette.TEXT}; }}"
            )

    # -- state ------------------------------------------------------------ #
    def _set_mode(self, mode: str) -> None:
        self._mode = mode
        self._stack.setCurrentWidget(self._month if mode == "month" else self._week)
        self._style_toggle(self._month_btn, active=(mode == "month"))
        self._style_toggle(self._week_btn, active=(mode == "week"))
        self._month_btn.setChecked(mode == "month")
        self._week_btn.setChecked(mode == "week")
        self.refresh()

    def _shift(self, direction: int) -> None:
        if self._mode == "month":
            self._anchor = _add_months(self._anchor, direction)
        else:
            self._anchor = self._anchor + timedelta(days=7 * direction)
        self.refresh()

    def _go_today(self) -> None:
        self._anchor = date.today()
        self.refresh()

    def refresh(self) -> None:
        if self._mode == "month":
            first = self._anchor.replace(day=1)
            start = first - timedelta(days=first.weekday())
            end = start + timedelta(days=41)
            events = self._provider(start, end)
            self._month.render_month(self._anchor, events)
            self._period_label.setText(f"{PL_MONTHS[self._anchor.month - 1].capitalize()} {self._anchor.year}")
        else:
            start = self._anchor - timedelta(days=self._anchor.weekday())
            end = start + timedelta(days=6)
            events = self._provider(start, end)
            self._week.render_week(self._anchor, events)
            self._period_label.setText(_week_label(start, end))


def _add_months(d: date, delta: int) -> date:
    month_index = d.month - 1 + delta
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    last_day = _calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last_day))


def _week_label(start: date, end: date) -> str:
    if start.month == end.month:
        return f"{start.day}–{end.day} {PL_MONTHS[start.month - 1]} {start.year}"
    if start.year == end.year:
        return (f"{start.day} {PL_MONTHS[start.month - 1]} – "
                f"{end.day} {PL_MONTHS[end.month - 1]} {start.year}")
    return (f"{start.day} {PL_MONTHS[start.month - 1]} {start.year} – "
            f"{end.day} {PL_MONTHS[end.month - 1]} {end.year}")
