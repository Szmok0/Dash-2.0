# Pakowanie i instalator (Windows 11)

Client Workbench dystrybuowany jest jako instalator EXE, który nie wymaga
instalacji Pythona u użytkownika (BUILD.md). Budowanie odbywa się na Windows.

## Wymagania (maszyna budująca)
- Windows 10/11 64-bit
- Python 3.12 (zalecany; działa też 3.11)
- [Inno Setup 6+](https://jrsoftware.org/isdl.php) — narzędzie `iscc` w PATH
- (opcjonalnie) UPX do kompresji binariów

## Budowanie jednym poleceniem
Z katalogu głównego repozytorium:

```bat
packaging\build_windows.bat
```

Skrypt kolejno:
1. instaluje zależności + PyInstaller,
2. generuje ikonę (`resources/app_icon.ico` / `.png`),
3. buduje aplikację (`pyinstaller packaging/client_workbench.spec`) → `dist/ClientWorkbench/`,
4. buduje instalator (`iscc packaging/installer.iss`) → `dist/installer/ClientWorkbench_Setup_1.0.0.exe`.

## Kroki ręczne (alternatywa)
```bat
python -m pip install -r requirements.txt pyinstaller
python tools\make_icon.py
pyinstaller --noconfirm --clean packaging\client_workbench.spec
iscc packaging\installer.iss
```

## Co robi instalator
- instaluje aplikację w `C:\Program Files\ClientWorkbench`,
- tworzy skrót w menu Start oraz **ikonę na pulpicie** (zadanie „Utwórz ikonę na pulpicie”, domyślnie zaznaczone) z dedykowaną ikoną `app_icon.ico`,
- oferuje uruchomienie po instalacji,
- dane użytkownika (baza, zdjęcia, kopie zapasowe, logi) trzymane są poza katalogiem programu, w `%LOCALAPPDATA%\ClientWorkbench\data`, dzięki czemu odinstalowanie/aktualizacja nie kasuje danych.

## Ikona
`tools/make_icon.py` generuje ikonę z jednego źródła do PNG oraz wielorozmiarowego
ICO (16–256 px). Ikona jest osadzona w EXE (PyInstaller `icon=`) oraz używana przez
skróty instalatora.

## Uwaga o platformie
`.spec` i `.iss` są przeznaczone dla Windows. Ten sam `.spec` można uruchomić na
innych systemach do walidacji pakowania (powstaje binarka natywna dla danego OS),
ale dystrybuowany instalator `.exe` z ikoną na pulpicie budujemy na Windows.
