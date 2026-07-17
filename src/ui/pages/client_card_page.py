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

from models.entities import (
    CLIENT_STATUS_LABELS,
    CONTACT_TYPE_LABELS,
    CV_STATUS_LABELS,
    CV_STATUSES,
    Client,
    EMPLOYMENT_LABELS,
    INTERNSHIP_LABELS,
    IPD_STATUS_LABELS,
    PRIORITY_LABELS,
    TASK_STATUS_LABELS,
    TRAINING_STATUS_LABELS,
    TRAINING_TYPE_LABELS,
    normalize_cv_status,
)
from services.store import DataStore
from ui.dialogs.entry_dialogs import DIALOGS
from ui.dialogs.module_view import ModuleViewDialog
from ui.styles.theme import Palette
from ui.widgets.flow_layout import FlowLayout
from ui.widgets.pills import MenuPill, QuickStatusPill, YesNoFlag

LEFT_COLUMN_WIDTH = 300
PHOTO_SIZE = 180
MODULE_HEIGHT = 330
STATUS_DIVIDER_HEIGHT = 40


def _fmt_date(value) -> str:
    return value.strftime("%d.%m.%Y") if value else "—"


class ClientCardPage(QWidget):
    def __init__(
        self,
        store: DataStore,
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
        self._pdf_btn = QPushButton("Eksport PDF")
        self._pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pdf_btn.clicked.connect(self._export_pdf)
        top.addWidget(self._pdf_btn)
        self._attention_btn = QPushButton("Wymaga uwagi")
        self._attention_btn.setCheckable(True)
        self._attention_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._attention_btn.toggled.connect(self._toggle_attention)
        top.addWidget(self._attention_btn)
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

        self._photo_btn = QPushButton("Zmień zdjęcie")
        self._photo_btn.setObjectName("Ghost")
        self._photo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._photo_btn.clicked.connect(self._pick_photo)
        photo_btn_row = QHBoxLayout()
        photo_btn_row.addStretch(1)
        photo_btn_row.addWidget(self._photo_btn)
        photo_btn_row.addStretch(1)
        left_layout.addLayout(photo_btn_row)

        self._name_lbl = QLabel()
        self._name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_lbl.setWordWrap(True)
        self._name_lbl.setStyleSheet("font-size: 17px; font-weight: 700; padding-top: 4px;")
        left_layout.addWidget(self._name_lbl)

        self._id_lbl = QLabel()
        self._id_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self._id_lbl)
        left_layout.addSpacing(10)

        # komplet danych podstawowych (import XLSX / ręczne) — przewijalna lista
        info_scroll = QScrollArea()
        info_scroll.setWidgetResizable(True)
        info_scroll.setFrameShape(QFrame.Shape.NoFrame)
        info_scroll.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }")
        info_host = QWidget()
        self._info_layout = QVBoxLayout(info_host)
        self._info_layout.setContentsMargins(0, 0, 8, 0)
        self._info_layout.setSpacing(2)
        self._info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_scroll.setWidget(info_host)
        left_layout.addWidget(info_scroll, 1)
        self._style_left_labels()

        body.addWidget(self._left)

        # --- prawa część robocza ---
        right = QVBoxLayout()
        right.setSpacing(14)

        # rząd statusów: wszystkie kontrolki w jednej linii (zawijanej gdy brak miejsca)
        status_wrap = QWidget()
        self._status_flow = FlowLayout(status_wrap, margin=0, spacing=7)
        right.addWidget(status_wrap)

        # panel Komentarz (osobne, obramowane pole — treść od razu widoczna)
        self._comment_frame = QFrame()
        self._comment_frame.setObjectName("Panel")
        cf = QVBoxLayout(self._comment_frame)
        cf.setContentsMargins(16, 10, 16, 12)
        cf.setSpacing(4)
        chead = QHBoxLayout()
        ctitle = QLabel("Komentarz")
        ctitle.setStyleSheet("font-size: 14px; font-weight: 700;")
        chead.addWidget(ctitle)
        chead.addStretch(1)
        self._comment_edit_btn = QPushButton("Edytuj")
        self._comment_edit_btn.setObjectName("Ghost")
        self._comment_edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._comment_edit_btn.clicked.connect(self._edit_comment)
        chead.addWidget(self._comment_edit_btn)
        cf.addLayout(chead)
        self._comment_lbl = QLabel("—")
        self._comment_lbl.setWordWrap(True)
        self._comment_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cf.addWidget(self._comment_lbl)
        right.addWidget(self._comment_frame)

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

    def _fill_left_info(self) -> None:
        """Wypełnia lewą kolumnę kompletem danych podstawowych klienta."""
        c = self._client
        assert c is not None
        p = self._palette
        _clear_layout(self._info_layout)
        # każdy zestaw (etykieta + wartość) w osobnej, subtelnej ramce (#6)
        for label, value in self._basic_data_pairs():
            box = QFrame()
            box.setStyleSheet(
                f"QFrame {{ background: {p.card}; border: 1px solid {p.line}; border-radius: 8px; }}"
            )
            bl = QVBoxLayout(box)
            bl.setContentsMargins(11, 7, 11, 8)
            bl.setSpacing(2)
            caption = QLabel(label)
            caption.setStyleSheet(
                f"color: {p.text_muted}; font-size: 10px; text-transform: uppercase; border: none;"
            )
            value_lbl = QLabel(value)
            value_lbl.setWordWrap(True)
            value_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value_lbl.setStyleSheet(f"font-size: 13px; color: {p.text}; border: none;")
            bl.addWidget(caption)
            bl.addWidget(value_lbl)
            self._info_layout.addWidget(box)
        self._info_layout.setSpacing(8)

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
                    f"border-radius: 12px; border: 2px solid {self._palette.line};"
                    f"background: {self._palette.card};"
                )
        if self._photo.pixmap().isNull():
            # brak zdjęcia = pusty placeholder, bez inicjałów (spójna ramka jak pola danych)
            self._photo.setStyleSheet(
                f"background: {self._palette.card}; border: 2px solid {self._palette.line};"
                "border-radius: 12px;"
            )

        self._photo_btn.setText("Zmień zdjęcie" if client.photo_path else "Dodaj zdjęcie")
        self._name_lbl.setText(client.full_name)
        self._id_lbl.setText(f"ID: {client.external_id}")
        self._fill_left_info()

        # panel Komentarz — pełny gdy jest treść, kompaktowy gdy pusty (#4)
        comment = client.import_comment.strip() if client.import_comment else ""
        self._comment_lbl.setText(comment or "Brak komentarza — kliknij „Edytuj”, aby dodać.")
        self._comment_lbl.setStyleSheet(
            f"font-size: {'13px' if comment else '12px'}; line-height: 135%; color: "
            f"{self._palette.text if comment else self._palette.text_muted};"
        )

        self._attention_btn.blockSignals(True)
        self._attention_btn.setChecked(client.requires_attention)
        self._attention_btn.blockSignals(False)
        self._style_attention(client.requires_attention)

        self._build_status_row()
        self._build_modules()

    # ------------------------------------------------------------------
    def _build_status_row(self) -> None:
        client = self._client
        assert client is not None
        p = self._palette

        _clear_layout(self._status_flow)

        def save() -> None:
            self._store.update_client(client)
            self._on_data_changed()

        def caption(text: str) -> None:
            lbl = QLabel(text)
            lbl.setFixedHeight(50)
            lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            lbl.setStyleSheet(
                f"color: {p.text_muted}; font-size: 10px; font-weight: 700;"
                "letter-spacing: 1px; padding: 0 2px;"
            )
            self._status_flow.addWidget(lbl)

        caption("STATUSY")

        # CV — pill z rozwijanym menu (3 stany), identyczny kształt jak pozostałe statusy
        def cv_changed(v: str) -> None:
            client.cv_status = v
            save()

        self._status_flow.addWidget(
            MenuPill(
                "CV", CV_STATUSES, CV_STATUS_LABELS, normalize_cv_status(client.cv_status),
                {"brak": p.red, "do_poprawy": p.yellow, "aktualne": p.green},
                cv_changed, p,
            )
        )

        def add_pill(title, values, labels, current, colors, attr):
            def color_for(v: str) -> str:
                return colors.get(v, p.text_muted)

            def on_change(v: str) -> None:
                setattr(client, attr, v)
                save()

            self._status_flow.addWidget(
                QuickStatusPill(title, values, labels, current, color_for, on_change)
            )

        add_pill("IPD", ["aktualne", "nieaktualne"], IPD_STATUS_LABELS, client.ipd_status,
                 {"aktualne": p.green, "nieaktualne": p.red}, "ipd_status")
        add_pill("Staż", ["brak", "w_trakcie"], INTERNSHIP_LABELS, client.internship_status,
                 {"brak": p.text_muted, "w_trakcie": p.purple}, "internship_status")
        add_pill("Zatrudnienie", ["bez_pracy", "zatrudniony"], EMPLOYMENT_LABELS,
                 client.employment_status,
                 {"bez_pracy": p.yellow, "zatrudniony": p.green}, "employment_status")
        add_pill("Klient", ["aktywny", "zamkniety"], CLIENT_STATUS_LABELS, client.client_status,
                 {"aktywny": p.accent, "zamkniety": p.text_muted}, "client_status")

        # nagłówek grupy cech tak/nie
        caption("SPECJALIŚCI")

        # toggle zielony/czerwony: DZ / JC / RP / Psycholog / Prawnik (ma / nie ma)
        def add_flag(title: str, attr: str) -> None:
            def on_toggle(has: bool) -> None:
                setattr(client, attr, "Tak" if has else "Nie")
                save()

            has = str(getattr(client, attr)).strip().lower() in ("tak", "1", "true", "x", "jest")
            self._status_flow.addWidget(YesNoFlag(title, has, on_toggle, p))

        for title, attr in (("DZ", "dz"), ("JC", "jc"), ("RP", "rp"),
                            ("Psycholog", "psychologist"), ("Prawnik", "lawyer")):
            add_flag(title, attr)

    # ------------------------------------------------------------------
    def _build_modules(self) -> None:
        client = self._client
        assert client is not None

        _clear_layout(self._grid)

        # 4 symetryczne moduły w siatce 2x2 (dane podstawowe są w lewej kolumnie)
        modules = [
            ("Zadania", self._task_entries(), "Zadanie"),
            ("Kontakty", self._contact_entries(), "Kontakt"),
            ("Szkolenia", self._training_entries(), "Szkolenie"),
            ("Notatki", self._note_entries(), "Notatka"),
        ]
        for index, (title, entries, add_kind) in enumerate(modules):
            row, col = divmod(index, 2)
            self._grid.addWidget(self._module_card(title, entries, add_kind), row, col)
        for col in range(2):
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
        layout.setSpacing(10)

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
            add_btn = QPushButton(f"+ {add_kind}")
            add_btn.setObjectName("Ghost")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.clicked.connect(lambda: self._open_add_dialog(add_kind))
            head.addWidget(add_btn)
        layout.addLayout(head)

        shown = entries[:4]
        for entry in shown:
            header, meta, content = entry[0], entry[1], entry[2]
            edit_ref = entry[3] if len(entry) > 3 else None
            layout.addWidget(self._entry_row(header, meta, content, edit_ref))
        if not entries:
            empty = QLabel(
                f"Brak wpisów.\nKliknij „+ {add_kind}”, aby dodać." if add_kind else "Brak wpisów."
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                f"color: {p.text_muted}; font-size: 12px; line-height: 145%;"
                f"border: 1px dashed {p.line}; border-radius: 8px; padding: 18px;"
            )
            layout.addWidget(empty)
        layout.addStretch(1)

        if len(entries) > len(shown):
            more = QPushButton(f"Pokaż wszystkie ({len(entries)})")
            more.setObjectName("Ghost")
            more.setCursor(Qt.CursorShape.PointingHandCursor)
            more.clicked.connect(lambda: self._open_full_view(title, entries))
            layout.addWidget(more)
        return frame

    def _entry_row(self, header: str, meta: str, content: str, edit_ref=None) -> QFrame:
        p = self._palette
        row = QFrame()
        if edit_ref is not None:
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.setToolTip("Kliknij, aby edytować")
            row.setStyleSheet(
                "QFrame { border: none; border-bottom: 1px solid " + p.line + "; background: transparent; }"
                "QFrame:hover { background: " + p.hover + "; border-radius: 6px; }"
            )
            row.mousePressEvent = lambda _e, ref=edit_ref: self._open_edit_dialog(ref)
        else:
            row.setStyleSheet(f"border: none; border-bottom: 1px solid {p.line}; background: transparent;")
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 9)
        layout.setSpacing(5)

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
    def _basic_data_pairs(self) -> list[tuple[str, str]]:
        c = self._client
        assert c is not None
        # imię, nazwisko, ID są przy zdjęciu; DZ/JC/RP/Psycholog/Prawnik jako toggle w rzędzie statusów;
        # komentarz w osobnym panelu — tutaj zostają właściwe dane podstawowe
        return [
            ("Telefon", c.phone or "—"),
            ("E-mail", c.email or "—"),
            ("Data rekrutacji", _fmt_date(c.recruitment_date)),
            ("Data IPD", _fmt_date(c.ipd_date)),
            ("Płeć", c.gender or "—"),
            ("Stopień niepełnosprawności", c.disability_degree or "—"),
            ("Symbol", c.disability_symbol or "—"),
            ("Symbole sprzężone", c.combined_symbols or "—"),
            ("Wykształcenie", c.education or "—"),
            ("Data ważności orzeczenia", _fmt_date(c.certificate_valid_until)),
            ("Poszukiwana praca", c.desired_job or "—"),
        ]

    def _task_entries(self) -> list[tuple[str, str, str]]:
        c = self._client
        assert c is not None
        entries = []
        from datetime import datetime as _dt

        for t in sorted(self._store.client_tasks(c.id), key=lambda t: t.due_at or _dt.max):
            due = t.due_at.strftime("%d.%m.%Y %H:%M") if t.due_at else "—"
            meta = f"{due} · {PRIORITY_LABELS[t.priority]} · {TASK_STATUS_LABELS[t.status]}"
            entries.append((t.title, meta, t.note, ("Zadanie", t)))
        return entries

    def _contact_entries(self) -> list[tuple]:
        c = self._client
        assert c is not None
        return [
            (
                CONTACT_TYPE_LABELS.get(ct.contact_type, ct.contact_type),
                f"{ct.contact_at.strftime('%d.%m.%Y %H:%M')} · {ct.status}",
                ct.note,
                ("Kontakt", ct),
            )
            for ct in self._store.client_contacts(c.id)
        ]

    def _training_entries(self) -> list[tuple]:
        c = self._client
        assert c is not None
        return [
            (
                t.name,
                f"{t.training_date.strftime('%d.%m.%Y')} · "
                f"{TRAINING_TYPE_LABELS[t.training_type]} · {TRAINING_STATUS_LABELS[t.status]}",
                t.note,
                ("Szkolenie", t),
            )
            for t in self._store.client_trainings(c.id)
        ]

    def _note_entries(self) -> list[tuple]:
        c = self._client
        assert c is not None
        items: list[tuple] = []
        for note in self._store.raw_notes(c.id):
            items.append((note.created_at, "Notatka", note.content, ("Notatka", note)))
        for ct in self._store.client_contacts(c.id):
            if ct.note:
                label = CONTACT_TYPE_LABELS.get(ct.contact_type, ct.contact_type)
                items.append((ct.contact_at, f"Kontakt · {label}", ct.note, ("Kontakt", ct)))
        items.sort(key=lambda it: it[0], reverse=True)
        return [
            (source, created.strftime("%d.%m.%Y %H:%M"), content, ref)
            for created, source, content, ref in items
        ]

    # ------------------------------------------------------------------
    def _open_full_view(self, title: str, entries: list[tuple]) -> None:
        stripped = [(e[0], e[1], e[2]) for e in entries]
        ModuleViewDialog(self, self._palette, title, stripped).exec()

    def _open_edit_dialog(self, edit_ref) -> None:
        if edit_ref is None or self._client is None:
            return
        kind, entity = edit_ref
        dialog = DIALOGS[kind](self, self._store, self._client.id, entity)
        if dialog.exec():
            self.show_client(self._client.id)
            self._on_data_changed()

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

    def _export_pdf(self) -> None:
        if self._client is None:
            return
        from PySide6.QtWidgets import QMessageBox

        from exporters.client_pdf import export_client_card_pdf

        try:
            path = export_client_card_pdf(self._store, self._client.id)
        except Exception as exc:  # pragma: no cover - komunikat dla użytkownika
            QMessageBox.critical(self, "Eksport PDF", f"Nie udało się wyeksportować:\n{exc}")
            return
        QMessageBox.information(self, "Eksport PDF", f"Zapisano kartę klienta:\n{path}")

    def _edit_comment(self) -> None:
        if self._client is None:
            return
        from PySide6.QtWidgets import QInputDialog

        text, ok = QInputDialog.getMultiLineText(
            self, "Komentarz", "Treść komentarza:", self._client.import_comment or ""
        )
        if ok:
            self._client.import_comment = text.strip()
            self._store.update_client(self._client)
            self.show_client(self._client.id)

    def _pick_photo(self) -> None:
        if self._client is None:
            return
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz zdjęcie", "", "Obrazy (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return
        self._store.set_client_photo(self._client, path)
        self.show_client(self._client.id)

    def _style_attention(self, active: bool) -> None:
        p = self._palette
        from ui.widgets.pills import with_alpha

        if active:
            self._attention_btn.setText("● Wymaga uwagi")
            self._attention_btn.setStyleSheet(
                f"QPushButton {{ background: {with_alpha(p.yellow, 0.18)}; color: {p.yellow};"
                f"border: 1px solid {with_alpha(p.yellow, 0.5)}; border-radius: 8px;"
                "padding: 7px 14px; font-weight: 700; }}"
            )
        else:
            self._attention_btn.setText("Oznacz „Wymaga uwagi”")
            self._attention_btn.setStyleSheet(
                f"QPushButton {{ background: {p.card}; color: {p.text_muted};"
                f"border: 1px solid {p.line}; border-radius: 8px; padding: 7px 14px; }}"
                f"QPushButton:hover {{ color: {p.yellow}; border-color: {with_alpha(p.yellow, 0.5)}; }}"
            )

    def _toggle_attention(self, checked: bool) -> None:
        if self._client is None:
            return
        self._client.requires_attention = checked
        if not checked:
            self._client.attention_note = ""
        self._store.update_client(self._client)
        self._style_attention(checked)
        self._on_data_changed()


def _clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
