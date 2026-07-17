"""Eksport karty klienta do PDF (reportlab)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from exporters.table_export import exports_dir
from models.entities import (
    CLIENT_STATUS_LABELS,
    CV_STATUS_LABELS,
    EMPLOYMENT_LABELS,
    INTERNSHIP_LABELS,
    IPD_STATUS_LABELS,
    PRIORITY_LABELS,
    TASK_STATUS_LABELS,
    TRAINING_STATUS_LABELS,
    TRAINING_TYPE_LABELS,
    CONTACT_TYPE_LABELS,
)


def _d(value) -> str:
    return value.strftime("%d.%m.%Y") if value else "—"


def export_client_card_pdf(store, client_id: int) -> Path:  # store: DataStore
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    from exporters.fonts import FONT_BOLD, register_pdf_fonts

    font = register_pdf_fonts()
    bold = FONT_BOLD if font != "Helvetica" else "Helvetica-Bold"
    client = store.client(client_id)
    path = exports_dir() / f"karta_{client.external_id}_{datetime.now():%Y-%m-%d_%H-%M-%S}.pdf"

    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    for name in ("Title", "Normal", "BodyText", "Heading3"):
        styles[name].fontName = font
    styles["Title"].fontName = bold
    styles["Heading3"].fontName = bold
    small = styles["BodyText"]
    small.fontSize = 9
    small.leading = 12

    story = [
        Paragraph(f"Karta klienta — {client.full_name}", styles["Title"]),
        Paragraph(f"ID: {client.external_id}", styles["Normal"]),
        Paragraph("Wygenerowano: " + datetime.now().strftime("%d.%m.%Y %H:%M"), styles["Normal"]),
        Spacer(1, 0.4 * cm),
    ]

    def section(title: str) -> None:
        story.append(Spacer(1, 0.35 * cm))
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))

    def render_table(headers: list[str], rows: list[list[str]]) -> None:
        if not rows:
            story.append(Paragraph("Brak wpisów.", small))
            return
        data = [[Paragraph(f"<b>{h}</b>", small) for h in headers]]
        data += [[Paragraph(str(c), small) for c in r] for r in rows]
        table = Table(data, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D2330")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B0B6C0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F2F6")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.append(table)

    # Dane podstawowe
    section("Dane podstawowe")
    basic = [
        ("Telefon", client.phone or "—"), ("E-mail", client.email or "—"),
        ("Data rekrutacji", _d(client.recruitment_date)), ("Data IPD", _d(client.ipd_date)),
        ("Płeć", client.gender or "—"),
        ("Stopień niepełnosprawności", client.disability_degree or "—"),
        ("Symbol", client.disability_symbol or "—"),
        ("Symbole sprzężone", client.combined_symbols or "—"),
        ("Wykształcenie", client.education or "—"),
        ("Data ważności orzeczenia", _d(client.certificate_valid_until)),
        ("Poszukiwana praca", client.desired_job or "—"),
        ("DZ", client.dz or "—"), ("JC", client.jc or "—"), ("RP", client.rp or "—"),
        ("Psycholog", client.psychologist or "—"), ("Prawnik", client.lawyer or "—"),
        ("Komentarz", client.import_comment or "—"),
    ]
    render_table(["Pole", "Wartość"], [[k, v] for k, v in basic])

    # Statusy
    section("Statusy")
    render_table(
        ["Status", "Wartość"],
        [
            ["CV", CV_STATUS_LABELS.get(client.cv_status, client.cv_status)],
            ["IPD", IPD_STATUS_LABELS.get(client.ipd_status, client.ipd_status)],
            ["Staż", INTERNSHIP_LABELS.get(client.internship_status, client.internship_status)],
            ["Zatrudnienie", EMPLOYMENT_LABELS.get(client.employment_status, client.employment_status)],
            ["Klient", CLIENT_STATUS_LABELS.get(client.client_status, client.client_status)],
        ],
    )

    # Zadania
    section("Zadania")
    render_table(
        ["Termin", "Zadanie", "Priorytet", "Status"],
        [
            [
                t.due_at.strftime("%d.%m.%Y %H:%M") if t.due_at else "—",
                t.title, PRIORITY_LABELS.get(t.priority, t.priority),
                TASK_STATUS_LABELS.get(t.status, t.status),
            ]
            for t in store.client_tasks(client_id)
        ],
    )

    # Kontakty
    section("Kontakty")
    render_table(
        ["Data", "Typ", "Status", "Notatka"],
        [
            [
                c.contact_at.strftime("%d.%m.%Y %H:%M"),
                CONTACT_TYPE_LABELS.get(c.contact_type, c.contact_type),
                str(c.status).capitalize(), c.note or "—",
            ]
            for c in store.client_contacts(client_id)
        ],
    )

    # Szkolenia
    section("Szkolenia")
    render_table(
        ["Data", "Nazwa", "Rodzaj", "Status"],
        [
            [
                t.training_date.strftime("%d.%m.%Y"), t.name,
                TRAINING_TYPE_LABELS.get(t.training_type, t.training_type),
                TRAINING_STATUS_LABELS.get(t.status, t.status),
            ]
            for t in store.client_trainings(client_id)
        ],
    )

    # Notatki
    section("Notatki")
    render_table(
        ["Data", "Źródło", "Treść"],
        [
            [created.strftime("%d.%m.%Y %H:%M"), source, content]
            for created, source, content in store.client_notes(client_id)
        ],
    )

    doc.build(story)
    return path
