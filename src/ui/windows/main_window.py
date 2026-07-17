"""Okno główne: sidebar + header + przełączane strony (QStackedWidget)."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME, BASE_WINDOW_SIZE, MIN_WINDOW_SIZE
from services.store import DataStore
from ui.pages.analytics_page import AnalyticsPage
from ui.pages.calendar_page import CalendarPage
from ui.pages.client_card_page import ClientCardPage
from ui.pages.clients_page import ClientsPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.import_page import ImportPage
from ui.pages.settings_page import SettingsPage
from ui.styles.theme import DARK, LIGHT, Palette, build_qss
from ui.widgets.header import Header
from ui.widgets.sidebar import Sidebar

PAGE_TITLES = {
    "dashboard": "Dashboard",
    "klienci": "Klienci",
    "kalendarz": "Kalendarz",
    "analityka": "Analityka",
    "import": "Import",
    "ustawienia": "Ustawienia",
    "karta": "Karta klienta",
}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(*BASE_WINDOW_SIZE)
        self.setMinimumSize(*MIN_WINDOW_SIZE)

        self.store: DataStore = DataStore()
        self.palette_theme: Palette = DARK
        self._dark = True
        self._current_page = "dashboard"

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.palette_theme, self.navigate)
        root.addWidget(self.sidebar)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.header = Header(self.palette_theme, self._on_search, self._on_add)
        right_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        self.dashboard = DashboardPage(self.store, self.palette_theme, self.open_client)
        self.clients_page = ClientsPage(self.store, self.palette_theme, self.open_client)
        self.calendar_page = CalendarPage(self.store, self.palette_theme, self.open_client)
        self.analytics_page = AnalyticsPage(self.store, self.palette_theme, self.open_client)
        self.import_page = ImportPage(self.store, self.palette_theme, self._data_changed)
        self.settings_page = SettingsPage(
            self.palette_theme, self.store, self.toggle_theme, self._change_pin
        )
        self.client_card = ClientCardPage(
            self.store, self.palette_theme, self._back_from_card, self._data_changed
        )

        self._pages = {
            "dashboard": self.dashboard,
            "klienci": self.clients_page,
            "kalendarz": self.calendar_page,
            "analityka": self.analytics_page,
            "import": self.import_page,
            "ustawienia": self.settings_page,
            "karta": self.client_card,
        }
        for page in self._pages.values():
            self.stack.addWidget(page)
        right_layout.addWidget(self.stack, 1)

        root.addWidget(right, 1)
        self.setCentralWidget(central)

        self.apply_theme()
        self.navigate("dashboard")

        # --- blokada po bezczynności ---
        self._locked = False
        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(30_000)  # sprawdzaj co 30 s
        self._idle_timer.timeout.connect(self._check_idle)
        self._idle_ms = 0
        self._idle_timer.start()

    # ------------------------------------------------------------------
    def start_security(self) -> None:
        """Wywoływane po pokazaniu okna: ustaw PIN lub poproś o odblokowanie."""
        from ui.dialogs.pin_dialog import PinDialog

        if not self.store.security.has_pin():
            dialog = PinDialog(self, self.store.security, self.palette_theme, mode="set")
            dialog.exec()
        else:
            self._lock()

    def _lock(self) -> None:
        from ui.dialogs.pin_dialog import PinDialog

        if self._locked or not self.store.security.has_pin():
            return
        self._locked = True
        dialog = PinDialog(self, self.store.security, self.palette_theme, mode="verify")
        dialog.exec()
        self._locked = False
        self._idle_ms = 0

    def _check_idle(self) -> None:
        if self._locked or not self.store.security.has_pin():
            return
        self._idle_ms += self._idle_timer.interval()
        limit = self.store.security.idle_lock_minutes() * 60_000
        if self._idle_ms >= limit:
            self._lock()

    def eventFilter(self, obj, event):  # noqa: N802 (Qt API)
        if event.type() in (
            QEvent.Type.MouseMove, QEvent.Type.KeyPress,
            QEvent.Type.MouseButtonPress, QEvent.Type.Wheel,
        ):
            self._idle_ms = 0
        return super().eventFilter(obj, event)

    def _change_pin(self) -> None:
        from ui.dialogs.pin_dialog import PinDialog

        mode = "change" if self.store.security.has_pin() else "set"
        PinDialog(self, self.store.security, self.palette_theme, mode=mode).exec()

    # ------------------------------------------------------------------
    def navigate(self, key: str) -> None:
        self._current_page = key
        self.stack.setCurrentWidget(self._pages[key])
        self.header.set_title(PAGE_TITLES[key])
        if key in self.sidebar._buttons:
            self.sidebar.set_active(key)
        self._refresh_counters()
        if key == "dashboard":
            self.dashboard.refresh()
        elif key == "klienci":
            self.clients_page.refresh()
        elif key == "kalendarz":
            self.calendar_page.refresh()
        elif key == "analityka":
            self.analytics_page.refresh()
        elif key == "ustawienia":
            self.settings_page.refresh()

    def open_client(self, client_id: int) -> None:
        self.client_card.show_client(client_id)
        self._current_page = "karta"
        self.stack.setCurrentWidget(self.client_card)
        client = self.store.client(client_id)
        self.header.set_title(f"Karta klienta — {client.full_name}")
        self._refresh_counters()

    def _back_from_card(self) -> None:
        self.navigate("dashboard")

    def _data_changed(self) -> None:
        self.dashboard.refresh()
        self.clients_page.refresh()
        self._refresh_counters()

    def _refresh_counters(self) -> None:
        meetings = self.store.todays_meetings()
        if meetings:
            first = meetings[0]
            name = self.store.client(first.client_id).last_name
            info = f"{len(meetings)} (najbliższe {first.contact_at.strftime('%H:%M')} · {name})"
        else:
            info = "brak"
        self.header.set_counters(len(self.store.active_clients()), info)

    # ------------------------------------------------------------------
    def _on_search(self, text: str) -> None:
        self.dashboard.set_filter(text)
        self.clients_page.set_filter(text)

    def _on_add(self) -> None:
        if self._current_page == "karta":
            self.client_card.open_add_menu(self.header.add_button)
            return
        # poza kartą klienta: wybór klienta, potem formularz (karta = jedyne miejsce edycji)
        menu = QMenu(self)
        for client in sorted(self.store.active_clients(), key=lambda c: c.last_name):
            menu.addAction(
                f"{client.last_name} {client.first_name} ({client.external_id})",
                lambda cid=client.id: self.open_client(cid),
            )
        menu.exec(
            self.header.add_button.mapToGlobal(self.header.add_button.rect().bottomLeft())
        )

    # ------------------------------------------------------------------
    def toggle_theme(self) -> None:
        self._dark = not self._dark
        self.palette_theme = DARK if self._dark else LIGHT
        self.apply_theme()

    def apply_theme(self) -> None:
        self.setStyleSheet(build_qss(self.palette_theme))
        self.sidebar.set_palette(self.palette_theme)
        self.header.set_palette(self.palette_theme)
        self.dashboard.set_palette(self.palette_theme)
        self.clients_page.set_palette(self.palette_theme)
        self.calendar_page.set_palette(self.palette_theme)
        self.analytics_page.set_palette(self.palette_theme)
        self.import_page.set_palette(self.palette_theme)
        self.settings_page.set_palette(self.palette_theme)
        self.client_card.set_palette(self.palette_theme)
        self._refresh_counters()
