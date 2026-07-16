"""Karta klienta: osobny ekran, lewa kolumna danych + rząd statusów + równe moduły."""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from data.sample_data import (
    CLIENT_STATUS_LABELS,
    CONTACT_TYPE_LABELS,
    CV_STATUS_LABELS,
    Client,
    EMPLOYMENT_LABELS,
    INTERNSHIP_LABELS,
    IPD_STATUS_LABELS,
    PRIORITY_LABELS,
    SampleStore,
    TASK_STATUS_LABELS,
    TRAINING_STATUS_LABELS,
    TRAINING_TYPE_LABELS,
)
from ui.dialogs.entry_dialogs import DIALOGS
from ui.dialogs.module_view import ModuleViewDialog
from ui.styles.theme import Palette
from ui.widgets.pills import QuickStatusPill

LEFT_COLUMN_WIDTH = 270
PHOTO_SIZE = 110
MODULE_HEIGHT = 300


def _fmt_date(value) -> str:
    return value.strftime("%d.%m.%Y") if value else "—"


class ClientCardPage(QWidget):
    def __init__(
        self,
        store: SampleStore,
        palette: Palette,
        on_back: Callable[[], None],
        on_data_changed: Callable[[], None],
    ) -> None:
        super().__init__()
        self._store = store
        self._palette = palette
        self._on_back = on_back
        self._on_data_changed = on_data_changed
        self._client: Optional[Client] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 20)
        root.setSpacing(16)

        # pasek powrotu
        top = QHBoxLayout()
        back = QPushButton("‹ Wróć")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(self._on_back)
        top.addWidget(back)
        top.addStretch(1)
        self._attention_check = QCheckBox("Wymaga uwagi")
        self._attention_check.toggled.connect(self._toggle_attention)
        top.addWidget(self._attention_check)
        root.addLayout(top)

        body = QHBoxLayout()
        body.setSpacing(16)

        # --- lewa kolumna ---
        self._left = QFrame()
        self._left.setObjectName("Panel")
        self._left.setFixedWidth(LEFT_COLUMN_WIDTH)
        left_layout = QVBoxLayout(self._left)
        left_layout.setContentsMargins(20, 24, 20, 20)
        left_layout.setSpacing(6)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._photo = QLabel()
        self._photo.setFixedSize(PHOTO_SIZE, PHOTO_SIZE)
        self._photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_row = QHBoxLayout()
        photo_row.addStretch(1)
        photo_row.addWidget(self._photo)
        photo_row.addStretch(1)
        left_layout.addLayout(photo_row)

        self._name_lbl = QLabel()
        self._name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_lbl.setWordWrap(True)
        self._name_lbl.setStyleSheet("font-size: 17px; font-weight: 700; padding-top: 8px;")
        left_layout.addWidget(self._name_lbl)

        self._id_lbl = QLabel()
        self._id_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self._id_lbl)
        left_layout.addSpacing(12)

        self._info_rows: dict[str, QLabel] = {}
        for key in (
            "Telefon",
            "E-mail",
            "Stopień niepełnospr.",
            "Symbol",
            "Data wejścia",
            "Data IPD",
        ):
            caption = QLabel(key)
            value = QLabel("—")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            left_layout.addWidget(caption)
            left_layout.addWidget(value)
            left_layout.addSpacing(6)
            self._info_rows[key] = value
        self._style_left_labels()

        body.addWidget(self._left)

        # --- prawa część robocza ---
        right = QVBoxLayout()
        right.setSpacing(16)

        self._status_row = QHBoxLayout()
        self._status_row.setSpacing(12)
        status_wrap = QWidget()
        status_wrap.setLayout(self._status_row)
        right.addWidget(status_wrap)

        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)
        grid_host = QWidget()
        self._grid = QGridLayout(grid_host)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(16)
        grid_scroll.setWidget(grid_host)
        right.addWidget(grid_scroll, 1)

        body.addLayout(right, 1)
        root.addLayout(body, 1)

    # ------------------------------------------------------------------
    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self._style_left_labels()
        if self._client is not None:
            self.show_client(self._client.id)

    def _style_left_labels(self) -> None:
        p = self._palette
        self._id_lbl.setStyleSheet(f"color: {p.text_muted}; font-size: 12px;")
        for key, value_lbl in self._info_rows.items():
            value_lbl.setStyleSheet(f"font-size: 13px; color: {p.text};")
        for caption in self._left.findChildren(QLabel):
            if caption.text() in self._info_rows:
                caption.setStyleSheet(
                    f"color: {p.text_muted}; font-size: 11px; text-transform: uppercase;"
                )

    # ------------------------------------------------------------------
    def show_client(self, client_id: int) -> None:
        self._client = self._store.client(client_id)
        client = self._client

        # zdjęcie: zawsze reset źródła przy zmianie klienta (DATABASE.md)
        self._photo.setPixmap(QPixmap())
        if client.photo_path:
            pix = QPixmap(client.photo_path)
            if not pix.isNull():
                self._photo.setPixmap(
                    pix.scaled(
                        PHOTO_SIZE,
                        PHOTO_SIZE,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                self._photo.setStyleSheet(
                    f"border-radius: 10px; border: 1px solid {self._palette.line};"
                )
        if self._photo.pixmap().isNull():
            # brak zdjęcia = pusty placeholder, bez inicjałów
            self._photo.setStyleSheet(
                f"background: {self._palette.card}; border: 1px dashed {self._palette.line};"
                "border-radius: 10px;"
            )

        self._name_lbl.setText(client.full_name)
        self._id_lbl.setText(f"ID: {client.external_id}")
        self._info_rows["Telefon"].setText(client.phone or "—")
        self._info_rows["E-mail"].setText(client.email or "—")
        self._info_rows["Stopień niepełnospr."].setText(client.disability_degree or "—")
        self._info_rows["Symbol"].setText(client.disability_symbol or "—")
        self._info_rows["Data wejścia"].setText(_fmt_date(client.recruitment_date))
        self._info_rows["Data IPD"].setText(_fmt_date(client.ipd_date))

        self._attention_check.blockSignals(True)
        self._attention_check.setChecked(client.requires_attention)
        self._attention_check.blockSignals(False)

        self._build_status_row()
        self._build_modules()

    # ------------------------------------------------------------------
    def _build_status_row(self) -> None:
        client = self._client
        assert client is not None
        p = self._palette

        _clear_layout(self._status_row)

        def add_pill(title, values, labels, current, colors, attr):
            def color_for(v: str) -> str:
                return colors.get(v, p.text_muted)

            def on_change(v: str) -> None:
                setattr(client, attr, v)
                self._on_data_changed()

            self._status_row.addWidget(
                QuickStatusPill(title, values, labels, current, color_for, on_change)
            )

        add_pill("CV", ["aktualne", "nieaktualne"], CV_STATUS_LABELS, client.cv_status,
                 {"aktualne": p.green, "nieaktualne": p.red}, "cv_status")
        add_pill("IPD", ["aktualne", "nieaktualne"], IPD_STATUS_LABELS, client.ipd_status,
                 {"aktualne": p.green, "nieaktualne": p.red}, "ipd_status")
        add_pill("Staż", ["brak", "w_trakcie"], INTERNSHIP_LABELS, client.internship_status,
                 {"brak": p.text_muted, "w_trakcie": p.purple}, "internship_status")
        add_pill("Zatrudnienie", ["bez_pracy", "zatrudniony"], EMPLOYMENT_LABELS,
                 client.employment_status,
                 {"bez_pracy": p.yellow, "zatrudniony": p.green}, "employment_status")
        add_pill("Klient", ["aktywny", "zamkniety"], CLIENT_STATUS_LABELS, client.client_status,
                 {"aktywny": p.accent, "zamkniety": p.text_muted}, "client_status")
        self._status_row.addStretch(1)

    # ------------------------------------------------------------------
    def _build_modules(self) -> None:
        client = self._client
        assert client is not None

        _clear_layout(self._grid)

        modules = [
            ("Dane podstawowe", self._basic_data_entries(), None),
            ("Zadania", self._task_entries(), "Zadanie"),
            ("Kontakty", self._contact_entries(), "Kontakt"),
            ("Szkolenia", self._training_entries(), "Szkolenie"),
            ("Notatki", self._note_entries(), "Notatka"),
        ]
        for index, (title, entries, add_kind) in enumerate(modules):
            row, col = divmod(index, 3)
            self._grid.addWidget(self._module_card(title, entries, add_kind), row, col)
        # wyrównanie: pusta komórka w drugim rzędzie zachowuje równe szerokości
        filler = QWidget()
        self._grid.addWidget(filler, 1, 2)
        for col in range(3):
            self._grid.setColumnStretch(col, 1)

    def _module_card(
        self,
        title: str,
        entries: list[tuple[str, str, str]],
        add_kind: Optional[str],
    ) -> QFrame:
        p = self._palette
        frame = QFrame()
        frame.setObjectName("Panel")
        frame.setFixedHeight(MODULE_HEIGHT)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        head = QHBoxLayout()
        title_btn = QPushButton(title)
        title_btn.setObjectName("Ghost")
        title_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        title_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: {p.text};"
            "font-size: 15px; font-weight: 700; padding: 0; text-align: left; }"
            f"QPushButton:hover {{ color: {p.accent}; }}"
        )
        title_btn.setToolTip("Otwórz pełny widok")
        title_btn.clicked.connect(lambda: self._open_full_view(title, entries))
        head.addWidget(title_btn)

        counter = QLabel(str(len(entries)))
        counter.setStyleSheet(
            f"background: {p.card}; border: 1px solid {p.line}; border-radius: 9px;"
            f"padding: 1px 9px; font-size: 11px; color: {p.text_muted};"
        )
        head.addWidget(counter)
        head.addStretch(1)

        if add_kind is not None:
            add_btn = QPushButton("+ Dodaj")
            add_btn.setObjectName("Ghost")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.clicked.connect(lambda: self._open_add_dialog(add_kind))
            head.addWidget(add_btn)
        layout.addLayout(head)

        shown = entries[:4]
        for header, meta, content in shown:
            layout.addWidget(self._entry_row(header, meta, content))
        if not entries:
            empty = QLabel("Brak wpisów")
            empty.setStyleSheet(f"color: {p.text_muted}; font-size: 12px;")
            layout.addWidget(empty)
        layout.addStretch(1)

        if len(entries) > len(shown):
            more = QPushButton(f"Pokaż wszystkie ({len(entries)})")
            more.setObjectName("Ghost")
            more.setCursor(Qt.CursorShape.PointingHandCursor)
            more.clicked.connect(lambda: self._open_full_view(title, entries))
            layout.addWidget(more)
        return frame

    def _entry_row(self, header: str, meta: str, content: str) -> QFrame:
        p = self._palette
        row = QFrame()
        row.setStyleSheet(f"border: none; border-bottom: 1px solid {p.line}; background: transparent;")
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 2, 0, 6)
        layout.setSpacing(1)

        top = QHBoxLayout()
        header_lbl = QLabel(header)
        header_lbl.setStyleSheet("font-size: 13px; font-weight: 600; border: none;")
        # pozwól layoutowi przycinać długie tytuły zamiast rozpychać moduł
        header_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        top.addWidget(header_lbl, 1)
        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet(f"color: {p.text_muted}; font-size: 11px; border: none;")
        top.addWidget(meta_lbl)
        layout.addLayout(top)

        if content:
            preview = content.splitlines()[0]
            if len(preview) > 70:
                preview = preview[:67] + "…"
            content_lbl = QLabel(preview)
            content_lbl.setStyleSheet(f"color: {p.text_muted}; font-size: 12px; border: none;")
            content_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            layout.addWidget(content_lbl)
        return row

    # ------------------------------------------------------------------
    def _basic_data_entries(self) -> list[tuple[str, str, str]]:
        c = self._client
        assert c is not None
        pairs = [
            ("ASII LP. / ID", c.external_id),
            ("Imię i nazwisko", c.full_name),
            ("Telefon", c.phone or "—"),
            ("E-mail", c.email or "—"),
            ("Data rekrutacji", _fmt_date(c.recruitment_date)),
            ("Data IPD", _fmt_date(c.ipd_date)),
            ("DZ", c.dz or "—"),
            ("JC", c.jc or "—"),
            ("RP", c.rp or "—"),
            ("Psycholog", c.psychologist or "—"),
            ("Prawnik", c.lawyer or "—"),
            ("Płeć", c.gender or "—"),
            ("Stopień niepełnosprawności", c.disability_degree or "—"),
            ("Symbol", c.disability_symbol or "—"),
            ("Symbole sprzężone", c.combined_symbols or "—"),
            ("Wykształcenie", c.education or "—"),
            ("Data ważności orzeczenia", _fmt_date(c.certificate_valid_until)),
            ("Poszukiwana praca", c.desired_job or "—"),
            ("Komentarz", c.import_comment or "—"),
        ]
        return [(label, "", value) for label, value in pairs]

    def _task_entries(self) -> list[tuple[str, str, str]]:
        c = self._client
        assert c is not None
        entries = []
        from datetime import datetime as _dt

        for t in sorted(self._store.client_tasks(c.id), key=lambda t: t.due_at or _dt.max):
            due = t.due_at.strftime("%d.%m.%Y %H:%M") if t.due_at else "—"
            meta = f"{due} · {PRIORITY_LABELS[t.priority]} · {TASK_STATUS_LABELS[t.status]}"
            entries.append((t.title, meta, t.note))
        return entries

    def _contact_entries(self) -> list[tuple[str, str, str]]:
        c = self._client
        assert c is not None
        return [
            (
                CONTACT_TYPE_LABELS.get(ct.contact_type, ct.contact_type),
                f"{ct.contact_at.strftime('%d.%m.%Y %H:%M')} · {ct.status}",
                ct.note,
            )
            for ct in self._store.client_contacts(c.id)
        ]

    def _training_entries(self) -> list[tuple[str, str, str]]:
        c = self._client
        assert c is not None
        return [
            (
                t.name,
                f"{t.training_date.strftime('%d.%m.%Y')} · "
                f"{TRAINING_TYPE_LABELS[t.training_type]} · {TRAINING_STATUS_LABELS[t.status]}",
                t.note,
            )
            for t in self._store.client_trainings(c.id)
        ]

    def _note_entries(self) -> list[tuple[str, str, str]]:
        c = self._client
        assert c is not None
        return [
            (source, created.strftime("%d.%m.%Y %H:%M"), content)
            for created, source, content in self._store.client_notes(c.id)
        ]

    # ------------------------------------------------------------------
    def _open_full_view(self, title: str, entries: list[tuple[str, str, str]]) -> None:
        ModuleViewDialog(self, self._palette, title, entries).exec()

    def _open_add_dialog(self, kind: str) -> None:
        assert self._client is not None
        dialog = DIALOGS[kind](self, self._store, self._client.id)
        if dialog.exec():
            self.show_client(self._client.id)
            self._on_data_changed()

    def open_add_menu(self, anchor: QWidget) -> None:
        """Menu + Dodaj z górnego paska, gdy otwarta jest karta klienta."""
        menu = QMenu(self)
        for kind in ("Zadanie", "Kontakt", "Szkolenie", "Notatka"):
            menu.addAction(kind, lambda k=kind: self._open_add_dialog(k))
        menu.exec(anchor.mapToGlobal(anchor.rect().bottomLeft()))

    def _toggle_attention(self, checked: bool) -> None:
        if self._client is None:
            return
        self._client.requires_attention = checked
        if not checked:
            self._client.attention_note = ""
        self._on_data_changed()


def _clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
