"""Main window for the Sprint 0 shell."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget
from src.config import APP_NAME
from src.models.sample_data import CLIENTS
from src.ui.pages.client_card import ClientCardPage
from src.ui.pages.dashboard import DashboardPage
from src.ui.styles.theme import DARK_QSS

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__(); self.setWindowTitle(APP_NAME); self.resize(1366, 768); self.setStyleSheet(DARK_QSS)
        shell = QWidget(); root = QHBoxLayout(shell); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(232)
        nav = QVBoxLayout(sidebar); nav.setContentsMargins(12,16,12,16); nav.setSpacing(8)
        logo = QLabel("Client\nWorkbench"); logo.setObjectName("SectionTitle"); nav.addWidget(logo)
        self.buttons = []
        for text in ["Dashboard", "Klienci", "Kalendarz", "Analityka", "Import", "Ustawienia"]:
            b = QPushButton(text); b.setProperty("nav", True); b.setCheckable(True); nav.addWidget(b); self.buttons.append(b)
        nav.addStretch()
        main = QVBoxLayout(); main.setContentsMargins(0,0,0,0); main.setSpacing(0)
        top = QFrame(); top.setObjectName("TopBar"); top.setFixedHeight(64)
        tl = QHBoxLayout(top); tl.setContentsMargins(16,10,16,10); tl.setSpacing(16)
        self.title = QLabel("Dashboard"); self.title.setObjectName("ScreenTitle"); tl.addWidget(self.title)
        search = QLineEdit(); search.setPlaceholderText("Szukaj: ID, imię, nazwisko"); search.setFixedWidth(380); tl.addWidget(search)
        active = sum(1 for c in CLIENTS if c["client_status"] == "aktywny")
        tl.addWidget(QLabel(f"Aktywni klienci: {active}")); tl.addWidget(QLabel("Dzisiejsze spotkania: 2")); tl.addStretch()
        add = QPushButton("+ Dodaj"); add.setProperty("primary", True); add.setFixedWidth(100); tl.addWidget(add)
        self.stack = QStackedWidget(); self.dashboard = DashboardPage(); self.client = ClientCardPage(); self.stack.addWidget(self.dashboard); self.stack.addWidget(self.client)
        main.addWidget(top); main.addWidget(self.stack)
        root.addWidget(sidebar); root.addLayout(main, 1); self.setCentralWidget(shell)
        self.buttons[0].setChecked(True); self.buttons[0].clicked.connect(self.show_dashboard); self.buttons[1].clicked.connect(lambda: self.show_client(1)); self.dashboard.open_client.connect(self.show_client)
    def show_dashboard(self) -> None:
        self.stack.setCurrentWidget(self.dashboard); self.title.setText("Dashboard"); self.buttons[0].setChecked(True); self.buttons[1].setChecked(False)
    def show_client(self, client_id: int) -> None:
        self.client.set_client(client_id); self.stack.setCurrentWidget(self.client); self.title.setText("Karta klienta"); self.buttons[0].setChecked(False); self.buttons[1].setChecked(True)
