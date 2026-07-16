"""Pełny widok modułu karty klienta: duży modal nad kartą, bez nowego okna."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Palette


class ModuleViewDialog(QDialog):
    """Pełna lista wpisów modułu z prostym filtrowaniem tekstowym."""

    def __init__(
        self,
        parent: QWidget,
        palette: Palette,
        title: str,
        entries: list[tuple[str, str, str]],  # (nagłówek, metadane, treść)
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._palette = palette
        self._entries = entries

        parent_window = parent.window()
        self.resize(
            max(720, int(parent_window.width() * 0.62)),
            max(520, int(parent_window.height() * 0.72)),
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        head = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        head.addWidget(title_lbl)
        self._counter = QLabel(str(len(entries)))
        self._counter.setStyleSheet(
            f"background: {palette.card}; border: 1px solid {palette.line};"
            f"border-radius: 9px; padding: 1px 9px; font-size: 11px; color: {palette.text_muted};"
        )
        head.addWidget(self._counter)
        head.addStretch(1)
        close_btn = QPushButton("Zamknij")
        close_btn.clicked.connect(self.accept)
        head.addWidget(close_btn)
        root.addLayout(head)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filtruj wpisy…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._apply_filter)
        root.addWidget(self._search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        self._list_layout = QVBoxLayout(body)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch(1)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        self._apply_filter("")

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().lower()
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        visible = 0
        for header, meta, content in self._entries:
            if needle and needle not in f"{header} {meta} {content}".lower():
                continue
            self._list_layout.insertWidget(visible, self._entry_widget(header, meta, content))
            visible += 1
        self._counter.setText(str(visible))

    def _entry_widget(self, header: str, meta: str, content: str) -> QFrame:
        p = self._palette
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(7)

        top = QHBoxLayout()
        header_lbl = QLabel(header)
        header_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
        top.addWidget(header_lbl)
        top.addStretch(1)
        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet(f"color: {p.text_muted}; font-size: 11px;")
        top.addWidget(meta_lbl)
        layout.addLayout(top)

        if content:
            content_lbl = QLabel(content)
            content_lbl.setWordWrap(True)
            content_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            content_lbl.setStyleSheet(
                f"color: {p.text}; font-size: 13px; line-height: 130%;"
            )
            layout.addWidget(content_lbl)
        return frame
