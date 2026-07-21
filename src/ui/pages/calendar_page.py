"""Kalendarz — wizualizacja dat zadań, kontaktów i szkoleń (widok miesiąca i tygodnia)."""
from __future__ import annotations

import calendar as _cal
from datetime import date, timedelta
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from models.entities import CalendarEvent
from services.store import DataStore
from ui.styles.theme import Palette

WEEKDAYS = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]
MONTHS_PL = [
    "styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec",
    "lipiec", "sierpień", "wrzesień", "październik", "listopad", "grudzień",
]


def _kind_color(p: Palette, kind: str) -> str:
    return {"zadanie": p.accent, "kontakt": p.purple, "szkolenie": p.green}.get(kind, p.text_muted)


class CalendarPage(QWidget):
    def __init__(
        self,
        store: DataStore,
        palette: Palette,
        open_client: Callable[[int], None],
    ) -> None:
        super().__init__()
        self._store = store
        self._palette = palette
        self._open_client = open_client
        self._mode = "month"  # month | week
        self._anchor = date.today()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # --- pasek sterowania ---
        controls = QHBoxLayout()
        controls.setSpacing(10)

        self._prev_btn = QPushButton("‹")
        self._prev_btn.setFixedWidth(40)
        self._prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prev_btn.clicked.connect(lambda: self._shift(-1))
        self._next_btn = QPushButton("›")
        self._next_btn.setFixedWidth(40)
        self._next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_btn.clicked.connect(lambda: self._shift(1))
        self._today_btn = QPushButton("Dziś")
        self._today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._today_btn.clicked.connect(self._go_today)

        self._period_lbl = QLabel("")
        self._period_lbl.setStyleSheet("font-size: 18px; font-weight: 700;")

        controls.addWidget(self._prev_btn)
        controls.addWidget(self._next_btn)
        controls.addWidget(self._today_btn)
        controls.addSpacing(8)
        controls.addWidget(self._period_lbl)
        controls.addStretch(1)

        self._month_btn = QPushButton("Miesiąc")
        self._month_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._month_btn.clicked.connect(lambda: self._set_mode("month"))
        self._week_btn = QPushButton("Tydzień")
        self._week_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._week_btn.clicked.connect(lambda: self._set_mode("week"))
        controls.addWidget(self._month_btn)
        controls.addWidget(self._week_btn)
        root.addLayout(controls)

        # --- legenda ---
        legend = QHBoxLayout()
        legend.setSpacing(16)
        for kind, text in (("zadanie", "Zadanie"), ("kontakt", "Kontakt / spotkanie"), ("szkolenie", "Szkolenie")):
            dot = QLabel("●  " + text)
            dot.setObjectName(f"legend_{kind}")
            legend.addWidget(dot)
        legend.addStretch(1)
        self._legend = legend
        root.addLayout(legend)

        # --- obszar siatki ---
        self._area = QScrollArea()
        self._area.setWidgetResizable(True)
        self._grid_host = QWidget()
        self._grid = QGridLayout(self._grid_host)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(8)
        self._area.setWidget(self._grid_host)
        root.addWidget(self._area, 1)

        self.set_palette(palette)

    # ------------------------------------------------------------------
    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        p = palette
        for kind in ("zadanie", "kontakt", "szkolenie"):
            lbl = self.findChild(QLabel, f"legend_{kind}")
            if lbl is not None:
                lbl.setStyleSheet(f"color: {_kind_color(p, kind)}; font-size: 12px; font-weight: 600;")
        for btn in (self._month_btn, self._week_btn):
            active = (btn is self._month_btn) == (self._mode == "month")
            btn.setStyleSheet(
                f"QPushButton {{ background: {p.accent if active else p.card}; "
                f"color: {'#FFFFFF' if active else p.text}; border: 1px solid "
                f"{p.accent if active else p.line}; border-radius: 8px; padding: 7px 16px; "
                "font-weight: 600; }"
            )
        self.refresh()

    def refresh(self) -> None:
        if self._mode == "month":
            self._render_month()
        else:
            self._render_week()

    # ------------------------------------------------------------------
    def _set_mode(self, mode: str) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self.set_palette(self._palette)

    def _shift(self, direction: int) -> None:
        if self._mode == "month":
            year, month = self._anchor.year, self._anchor.month + direction
            year += (month - 1) // 12
            month = (month - 1) % 12 + 1
            day = min(self._anchor.day, _cal.monthrange(year, month)[1])
            self._anchor = date(year, month, day)
        else:
            self._anchor = self._anchor + timedelta(weeks=direction)
        self.refresh()

    def _go_today(self) -> None:
        self._anchor = date.today()
        self.refresh()

    def _events_by_day(self, start: date, end: date) -> dict[date, list[CalendarEvent]]:
        buckets: dict[date, list[CalendarEvent]] = {}
        for event in self._store.calendar_events(start, end):
            buckets.setdefault(event.event_date, []).append(event)
        return buckets

    def _clear_grid(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        # zresetuj rozciąganie i minimalne szerokości kolumn (różne między widokami)
        for i in range(8):
            self._grid.setColumnStretch(i, 0)
            self._grid.setRowStretch(i, 0)
            self._grid.setColumnMinimumWidth(i, 0)

    # ------------------------------------------------------------------
    def _render_month(self) -> None:
        self._clear_grid()
        p = self._palette
        year, month = self._anchor.year, self._anchor.month
        self._period_lbl.setText(f"{MONTHS_PL[month - 1].capitalize()} {year}")

        first_weekday, days_in_month = _cal.monthrange(year, month)  # 0 = poniedziałek
        grid_start = date(year, month, 1) - timedelta(days=first_weekday)
        events = self._events_by_day(grid_start, grid_start + timedelta(days=41))

        for col, name in enumerate(WEEKDAYS):
            head = QLabel(name)
            head.setAlignment(Qt.AlignmentFlag.AlignCenter)
            head.setStyleSheet(f"color: {p.text_muted}; font-size: 12px; font-weight: 600;")
            self._grid.addWidget(head, 0, col)

        today = date.today()
        weeks = 6
        for week in range(weeks):
            self._grid.setRowStretch(week + 1, 1)
            for col in range(7):
                cell_date = grid_start + timedelta(days=week * 7 + col)
                in_month = cell_date.month == month
                cell = self._month_cell(cell_date, events.get(cell_date, []), in_month, cell_date == today)
                self._grid.addWidget(cell, week + 1, col)
        for col in range(7):
            self._grid.setColumnStretch(col, 1)

    def _month_cell(self, day: date, events: list[CalendarEvent], in_month: bool, is_today: bool) -> QFrame:
        p = self._palette
        cell = QFrame()
        cell.setObjectName("Card")
        border = p.accent if is_today else p.line
        bg = p.card if in_month else p.panel
        cell.setStyleSheet(
            f"QFrame#Card {{ background: {bg}; border: 1px solid {border}; border-radius: 8px; }}"
        )
        cell.setMinimumHeight(96)
        # klik na dzień -> okno ze wszystkimi wydarzeniami tego dnia
        cell.setCursor(Qt.CursorShape.PointingHandCursor)
        cell.mousePressEvent = lambda _e, d=day, ev=list(events): self._open_day(d, ev)
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        num = QLabel(str(day.day))
        color = p.text if in_month else p.text_muted
        weight = "700" if is_today else "600"
        num.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: {weight}; border: none;")
        layout.addWidget(num)

        for event in events[:3]:
            layout.addWidget(self._event_chip(event, compact=True))
        if len(events) > 3:
            more = QLabel(f"+{len(events) - 3} więcej")
            more.setStyleSheet(f"color: {p.text_muted}; font-size: 10px; border: none;")
            layout.addWidget(more)
        layout.addStretch(1)
        return cell

    # ------------------------------------------------------------------
    def _render_week(self) -> None:
        self._clear_grid()
        p = self._palette
        week_start = self._anchor - timedelta(days=self._anchor.weekday())
        week_end = week_start + timedelta(days=6)
        if week_start.month == week_end.month:
            period = f"{week_start.day}–{week_end.day} {MONTHS_PL[week_start.month - 1]} {week_start.year}"
        else:
            period = (
                f"{week_start.day} {MONTHS_PL[week_start.month - 1]} – "
                f"{week_end.day} {MONTHS_PL[week_end.month - 1]} {week_end.year}"
            )
        self._period_lbl.setText(period)

        events = self._events_by_day(week_start, week_end)
        today = date.today()
        for col in range(7):
            day = week_start + timedelta(days=col)
            column = self._week_column(day, events.get(day, []), day == today)
            self._grid.addWidget(column, 0, col)
            # stała minimalna szerokość dnia -> na wąskim ekranie pojawia się poziomy pasek przewijania
            self._grid.setColumnMinimumWidth(col, 210)
        self._grid.setRowStretch(0, 1)

    def _week_column(self, day: date, events: list[CalendarEvent], is_today: bool) -> QFrame:
        p = self._palette
        col = QFrame()
        col.setObjectName("Card")
        border = p.accent if is_today else p.line
        col.setStyleSheet(
            f"QFrame#Card {{ background: {p.card}; border: 1px solid {border}; border-radius: 8px; }}"
        )
        col.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        col.setMinimumHeight(420)
        layout = QVBoxLayout(col)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        head = QLabel(f"{WEEKDAYS[day.weekday()]} {day.day}")
        head.setStyleSheet(
            f"color: {p.accent if is_today else p.text}; font-size: 13px; font-weight: 700; border: none;"
        )
        layout.addWidget(head)

        if not events:
            empty = QLabel("—")
            empty.setStyleSheet(f"color: {p.text_muted}; font-size: 11px; border: none;")
            layout.addWidget(empty)
        for event in events:
            layout.addWidget(self._event_chip(event, compact=False))
        layout.addStretch(1)
        return col

    # ------------------------------------------------------------------
    def _open_day(self, day: date, events: list[CalendarEvent]) -> None:
        """Okno ze wszystkimi wydarzeniami danego dnia (klik wydarzenia -> karta klienta)."""
        from PySide6.QtWidgets import QDialog, QPushButton as _QPushButton

        p = self._palette
        dialog = QDialog(self)
        dialog.setWindowTitle(day.strftime("%d.%m.%Y"))
        dialog.setMinimumSize(400, 440)
        dialog.setStyleSheet(f"QDialog {{ background: {p.panel}; }}")
        lay = QVBoxLayout(dialog)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        title = QLabel(f"{WEEKDAYS[day.weekday()]}, {day.day} {MONTHS_PL[day.month - 1]} {day.year}")
        title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {p.text};")
        lay.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        host = QWidget()
        v = QVBoxLayout(host)
        v.setContentsMargins(0, 0, 6, 0)
        v.setSpacing(8)
        v.setAlignment(Qt.AlignmentFlag.AlignTop)
        if not events:
            empty = QLabel("Brak wydarzeń w tym dniu.")
            empty.setStyleSheet(f"color: {p.text_muted}; font-size: 12px;")
            v.addWidget(empty)
        else:
            for event in sorted(events, key=lambda ev: ev.when):
                chip = self._event_chip(event, compact=False)
                chip.setMinimumHeight(32)
                chip.clicked.connect(dialog.accept)  # otwórz klienta i zamknij okno
                v.addWidget(chip)
        scroll.setWidget(host)
        lay.addWidget(scroll, 1)

        close = _QPushButton("Zamknij")
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.clicked.connect(dialog.reject)
        lay.addWidget(close)
        dialog.exec()

    # ------------------------------------------------------------------
    def _event_chip(self, event: CalendarEvent, compact: bool) -> QPushButton:
        p = self._palette
        color = _kind_color(p, event.kind)
        time_str = event.when.strftime("%H:%M ") if event.has_time else ""
        if compact:
            text = f"{time_str}{event.last_name}"
        else:
            text = f"{time_str}{event.last_name} · {event.label}"
        chip = QPushButton(text)
        chip.setCursor(Qt.CursorShape.PointingHandCursor)
        chip.setToolTip(f"{event.last_name} {event.first_name} — {event.label}")
        from ui.widgets.pills import with_alpha

        chip.setStyleSheet(
            f"QPushButton {{ background: {with_alpha(color, 0.15)}; color: {color}; "
            f"border: none; border-left: 3px solid {color}; border-radius: 4px; "
            "padding: 2px 6px; font-size: 11px; font-weight: 600; text-align: left; }"
            f"QPushButton:hover {{ background: {with_alpha(color, 0.28)}; }}"
        )
        chip.clicked.connect(lambda: self._open_client(event.client_id))
        return chip
