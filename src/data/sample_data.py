"""Dane demonstracyjne (seed) — używane przez tools/seed_demo.py.

Encje pochodzą z models.entities; ten moduł tylko buduje przykładowy zestaw.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from models.entities import Client, Contact, Note, Task, Training

RESOURCES_DIR = Path(__file__).resolve().parent.parent.parent / "resources"


@dataclass
class DemoData:
    clients: list[Client] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    contacts: list[Contact] = field(default_factory=list)
    trainings: list[Training] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)


def _long_note() -> str:
    lines = [
        "Rozmowa podsumowująca pierwszy miesiąc współpracy.",
        "Klientka zgłasza dużą motywację do zmiany zawodu.",
        "Dotychczasowe doświadczenie: 6 lat w handlu detalicznym.",
        "Ograniczenia zdrowotne: praca siedząca, bez dźwigania.",
        "Preferowany wymiar: pełny etat, ewentualnie 3/4.",
        "Możliwość dojazdu do 40 minut komunikacją miejską.",
        "CV wymaga aktualizacji o kurs obsługi kasy fiskalnej.",
        "Umówiono konsultację z doradcą zawodowym na przyszły tydzień.",
        "Klientka prosi o kontakt telefoniczny po godzinie 14:00.",
        "Rozważa szkolenie z podstaw obsługi komputera (pakiet biurowy).",
        "W poprzedniej pracy najlepiej czuła się w kontakcie z klientem.",
        "Zgłasza obawy dotyczące rozmów kwalifikacyjnych — stres.",
        "Zaplanowano symulację rozmowy rekrutacyjnej na kolejne spotkanie.",
        "Dokumenty orzeczenia dostarczone, ważne do końca 2026 roku.",
        "Wskazane sprawdzenie ofert pracy w sektorze administracji.",
        "Klientka nie posiada prawa jazdy, nie planuje kursu.",
        "Ustalono, że kontakt SMS jest preferowany przy przypomnieniach.",
        "Omówiono zasady udziału w projekcie i harmonogram wsparcia.",
        "Klientka wyraziła zgodę na udział w szkoleniu grupowym WUZ.",
        "Następny kontakt: po otrzymaniu wyników konsultacji doradczej.",
        "Notatka sporządzona po spotkaniu w biurze projektu.",
        "Do weryfikacji: możliwość refundacji dojazdów na szkolenia.",
    ]
    return "\n".join(lines)


def build_demo_data() -> DemoData:
    now = datetime.now()
    today = date.today()
    data = DemoData()

    data.clients = [
        Client(
            id=1, external_id="AS-1024", first_name="Anna", last_name="Kowalska",
            phone="601 234 567", email="anna.kowalska@example.com",
            recruitment_date=today - timedelta(days=95), ipd_date=today - timedelta(days=80),
            cv_status="aktualne", ipd_status="aktualne", employment_status="bez_pracy",
            internship_status="brak", client_status="aktywny",
            dz="Tak", jc="Tak", rp="Nie", psychologist="Tak", lawyer="Nie",
            gender="Kobieta", disability_degree="Umiarkowany", disability_symbol="05-R",
            combined_symbols="07-S", education="Średnie",
            certificate_valid_until=date(2026, 12, 31),
            desired_job="Pracownik administracyjno-biurowy",
        ),
        Client(
            id=2, external_id="AS-1031", first_name="Marek", last_name="Nowak",
            phone="512 908 445", email="marek.nowak@example.com",
            recruitment_date=today - timedelta(days=210), ipd_date=today - timedelta(days=190),
            cv_status="do_poprawy", ipd_status="aktualne", employment_status="bez_pracy",
            internship_status="w_trakcie", client_status="aktywny",
            gender="Mężczyzna", disability_degree="Lekki", disability_symbol="02-P",
            education="Zawodowe", desired_job="Magazynier",
            requires_attention=True, attention_note="Brak dokumentów do stażu — pilne.",
        ),
        Client(
            id=3, external_id="AS-1044", first_name="Ewa", last_name="Wiśniewska",
            phone="698 112 004", email="ewa.wisniewska@example.com",
            recruitment_date=today - timedelta(days=150), ipd_date=today - timedelta(days=140),
            cv_status="aktualne", ipd_status="nieaktualne", employment_status="zatrudniony",
            internship_status="brak", client_status="aktywny",
            gender="Kobieta", disability_degree="Znaczny", disability_symbol="04-O",
            education="Wyższe", desired_job="Księgowość",
        ),
        Client(
            id=4, external_id="AS-1052", first_name="Tomasz", last_name="Zieliński",
            phone="781 340 220", email="tomasz.zielinski@example.com",
            recruitment_date=today - timedelta(days=60), ipd_date=None,
            cv_status="do_poprawy", ipd_status="nieaktualne", employment_status="bez_pracy",
            internship_status="brak", client_status="aktywny",
            gender="Mężczyzna", disability_degree="Umiarkowany", disability_symbol="03-L",
            education="Średnie", desired_job="Ochrona mienia",
        ),
        Client(
            id=5, external_id="AS-1057", first_name="Katarzyna", last_name="Mazur",
            phone="530 774 981", email="k.mazur@example.com",
            recruitment_date=today - timedelta(days=45), ipd_date=today - timedelta(days=30),
            cv_status="aktualne", ipd_status="aktualne", employment_status="bez_pracy",
            internship_status="brak", client_status="aktywny",
            gender="Kobieta", disability_degree="Lekki", disability_symbol="10-N",
            education="Wyższe", desired_job="Grafik komputerowy",
            requires_attention=True, attention_note="Prośba o zmianę doradcy.",
        ),
        Client(
            id=6, external_id="AS-1060", first_name="Piotr", last_name="Krawczyk",
            phone="604 220 118", email="piotr.krawczyk@example.com",
            recruitment_date=today - timedelta(days=320), ipd_date=today - timedelta(days=300),
            cv_status="aktualne", ipd_status="aktualne", employment_status="zatrudniony",
            internship_status="brak", client_status="zamkniety",
            gender="Mężczyzna", disability_degree="Lekki", disability_symbol="05-R",
            education="Zawodowe", desired_job="Kierowca kat. B",
        ),
    ]

    data.tasks = [
        Task(id=1, client_id=2, title="Skompletować dokumenty stażowe", action_type="cv",
             due_at=now.replace(hour=12, minute=0), priority="wysoki", status="do_zrobienia",
             note="Umowa + orzeczenie + skierowanie."),
        Task(id=2, client_id=1, title="Telefon w sprawie oferty pracy", action_type="telefon",
             due_at=now.replace(hour=14, minute=30), priority="wysoki", status="w_trakcie",
             note="Oferta: recepcja, pełny etat."),
        Task(id=3, client_id=4, title="Aktualizacja CV po szkoleniu", action_type="cv",
             due_at=now + timedelta(days=1), priority="sredni", status="do_zrobienia"),
        Task(id=4, client_id=5, title="Spotkanie — plan działania IPD", action_type="spotkanie",
             due_at=now + timedelta(days=2), priority="sredni", status="oczekuje_na",
             note="Czekam na potwierdzenie terminu."),
        Task(id=5, client_id=3, title="Wysłać zaświadczenie e-mailem", action_type="email",
             due_at=now + timedelta(days=3), priority="niski", status="do_zrobienia"),
        Task(id=6, client_id=1, title="Zapisy na szkolenie WUZ", action_type="szkolenie",
             due_at=now + timedelta(days=5), priority="niski", status="w_trakcie"),
        Task(id=7, client_id=3, title="Przygotować notatkę z monitoringu", action_type="notatka",
             due_at=now.replace(hour=10, minute=0), priority="sredni", status="zakonczone",
             completed_at=now.replace(hour=9, minute=40)),
        Task(id=8, client_id=4, title="SMS z przypomnieniem o wizycie", action_type="telefon",
             due_at=now + timedelta(days=4), priority="niski", status="anulowane"),
    ]

    data.contacts = [
        Contact(id=1, client_id=1, contact_type="spotkanie",
                contact_at=now.replace(hour=9, minute=0), status="odbyty",
                note="Omówiono aktualizację CV i plan szkoleń na najbliższy kwartał."),
        Contact(id=2, client_id=5, contact_type="spotkanie",
                contact_at=now.replace(hour=13, minute=30), status="planowany",
                note="Plan działania IPD — sala 2."),
        Contact(id=3, client_id=1, contact_type="telefon",
                contact_at=now - timedelta(days=6), status="odbyty",
                note="Klientka potwierdza udział w szkoleniu grupowym."),
        Contact(id=4, client_id=2, contact_type="telefon",
                contact_at=now - timedelta(days=41), status="odbyty",
                note="Prośba o przesunięcie terminu dostarczenia dokumentów."),
        Contact(id=5, client_id=3, contact_type="email",
                contact_at=now - timedelta(days=12), status="odbyty",
                note="Przesłano listę ofert pracy w księgowości."),
        Contact(id=6, client_id=1, contact_type="sms",
                contact_at=now - timedelta(days=2), status="odbyty",
                note="Przypomnienie o spotkaniu."),
        Contact(id=7, client_id=1, contact_type="teams",
                contact_at=now - timedelta(days=20), status="odbyty",
                note="Konsultacja online z doradcą zawodowym."),
    ]

    data.trainings = [
        Training(id=1, client_id=1, name="Warsztat umiejętności zawodowych",
                 training_date=today + timedelta(days=9), training_type="wuz",
                 status="planowane", note="Grupa poranna."),
        Training(id=2, client_id=1, name="Podstawy obsługi komputera",
                 training_date=today - timedelta(days=30), training_type="it",
                 status="ukonczyl", note="Wynik bardzo dobry."),
        Training(id=3, client_id=2, name="Szkolenie adaptacyjne — magazyn",
                 training_date=today - timedelta(days=15), training_type="adaptacyjne",
                 status="nie_ukonczyl", note="Przerwane z przyczyn zdrowotnych."),
        Training(id=4, client_id=5, name="Kurs grafiki — moduł e-learning",
                 training_date=today + timedelta(days=20), training_type="elearning",
                 status="planowane"),
    ]

    data.notes = [
        Note(id=1, client_id=1, content=_long_note(), created_at=now - timedelta(days=1)),
        Note(id=2, client_id=1,
             content="Klientka dostarczyła zaktualizowane orzeczenie o niepełnosprawności.",
             created_at=now - timedelta(days=8)),
        Note(id=3, client_id=2,
             content="Pilne: skompletować dokumenty stażowe przed końcem miesiąca.",
             created_at=now - timedelta(days=3)),
        Note(id=4, client_id=5,
             content="Klientka prosi o kontakt wyłącznie mailowy w godzinach pracy.",
             created_at=now - timedelta(days=5)),
    ]

    return data
