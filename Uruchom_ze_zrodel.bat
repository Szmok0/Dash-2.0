@echo off
REM Uruchamia Client Workbench ze zrodel (python) z baza w STALYM miejscu poza kodem.
REM Dzieki temu podmiana / aktualizacja kodu NIE rusza bazy, zadan ani zdjec.
REM Baza laduje w: %LOCALAPPDATA%\ClientWorkbench\data  (to samo miejsce, co gotowy .exe)

setlocal
set "CW_DATA_DIR=%LOCALAPPDATA%\ClientWorkbench\data"
cd /d "%~dp0"

echo Baza danych: %CW_DATA_DIR%
python src\app.py
if errorlevel 1 pause
endlocal
