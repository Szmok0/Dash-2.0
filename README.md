# Client Workbench Sprint 0

Lokalna makieta desktopowa Windows dla jednego użytkownika, zgodna z pakietem zasad w `ClientWorkbench_Coding_Pack/`.

## Uruchomienie

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.app
```

Sprint 0 zawiera klikalny shell UI z ciemnym motywem, stałym sidebarem, Dashboardem i osobną kartą klienta na danych testowych. Nie używa SQLite.
