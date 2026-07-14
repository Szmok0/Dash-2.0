"""Client card page for Sprint 0."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget
from src.models.sample_data import CLIENTS, LONG_NOTE
from src.ui.widgets.common import Module, Pill, photo_placeholder

class ClientCardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._clients = {c["id"]: c for c in CLIENTS}
        self._root = QHBoxLayout(self); self._root.setContentsMargins(16,16,16,16); self._root.setSpacing(16)
        self.set_client(1)
    def set_client(self, client_id: int) -> None:
        while self._root.count():
            item = self._root.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        c = self._clients[client_id]
        left = QFrame(); left.setObjectName("Panel"); left.setFixedWidth(276)
        ll = QVBoxLayout(left); ll.setContentsMargins(16,16,16,16); ll.setSpacing(9)
        ll.addWidget(photo_placeholder(c["has_photo"]))
        name = QLabel(f"{c['first_name']} {c['last_name']}"); name.setObjectName("ScreenTitle"); name.setWordWrap(True); ll.addWidget(name)
        for label, key in [("ID", "external_id"),("Telefon", "phone"),("E-mail", "email"),("Stopień", "disability_degree"),("Symbol", "disability_symbol"),("Data wejścia", "recruitment_date"),("Data IPD", "ipd_date")]:
            v = QLabel(f"<span style='color:#A4ACB8'>{label}</span><br>{c[key]}"); v.setWordWrap(True); ll.addWidget(v)
        ll.addStretch()
        right = QVBoxLayout(); right.setSpacing(16)
        statuses = QHBoxLayout()
        for text in [f"CV: {c['cv_status']}", f"IPD: {c['ipd_status']}", f"Staż: {c['internship_status']}", f"Zatrudnienie: {c['employment_status']}", f"Klient: {c['client_status']}"]:
            statuses.addWidget(Pill(text, "#4C8DFF"))
        statuses.addStretch(); right.addLayout(statuses)
        grid = QGridLayout(); grid.setSpacing(16)
        modules = [
            Module("Dane podstawowe", 18, ["DZ: doradca zawodowy", "JC: job coach", "Poszukiwana praca: administracja biurowa", "Komentarz importu: komplet danych"]),
            Module("Zadania", 4, ["Oddzwonić po dokumenty — dziś", "Aktualizacja CV — zakończone", "Potwierdzić szkolenie — jutro"]),
            Module("Kontakty", 3, ["Telefon — dziś 09:30 — odebrany", "Spotkanie — 2026-07-14 11:00", "E-mail — wysłano dokumenty"]),
            Module("Szkolenia", 2, ["WUZ — planowane — 2026-07-20", "IT — ukończył — 2026-06-30"]),
            Module("Notatki", 6, LONG_NOTE.splitlines(), "+ Dodaj"),
        ]
        for i, module in enumerate(modules): grid.addWidget(module, i // 2, i % 2)
        right.addLayout(grid); right.addStretch()
        wrap = QWidget(); wrap.setLayout(right)
        self._root.addWidget(left); self._root.addWidget(wrap, 1)
