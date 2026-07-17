"""Okno główne: sidebar + header + przełączane strony (QStackedWidget)."""
from __future__ import annotations

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
from ui.pages.calendar_page import CalendarPage
from ui.pages.client_card_page import ClientCardPage
from ui.pages.clients_page import ClientsPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.placeholder_page import PlaceholderPage
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
        self.analytics_page = PlaceholderPage(
            self.palette_theme, "Analityka", "Filtry, historia działań i eksport — Sprint 5."
        )
        self.import_page = PlaceholderPage(
            self.palette_theme, "Import", "Import XLSX z podglądem zmian — Sprint 6."
        )
        self.settings_page = SettingsPage(self.palette_theme, self.toggle_theme)
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
