@echo off
REM Budowanie instalatora Client Workbench na Windows 11.
REM Wymagania: Python 3.12, PyInstaller, Inno Setup 6 (iscc w PATH).
REM Uruchamiać z katalogu głównego repozytorium: packaging\build_windows.bat

setlocal
cd /d "%~dp0\.."

echo === [1/4] Instalacja zaleznosci ===
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :error

echo === [2/4] Generowanie ikony ===
python tools\make_icon.py
if errorlevel 1 goto :error

echo === [3/4] PyInstaller (onedir) ===
pyinstaller --noconfirm --clean packaging\client_workbench.spec
if errorlevel 1 goto :error

REM dolacz do folderu aplikacji skrypt tworzacy skrot na pulpicie (wersja standalone)
if exist "dist\ClientWorkbench" copy /y "packaging\Utworz_skrot_na_pulpicie.bat" "dist\ClientWorkbench\" >nul

echo === [4/4] Inno Setup (instalator EXE) ===
where iscc >nul 2>nul
if errorlevel 1 (
  echo UWAGA: nie znaleziono iscc. Zainstaluj Inno Setup 6 i dodaj do PATH.
  echo Zbudowana aplikacja: dist\ClientWorkbench\ClientWorkbench.exe
  echo Skrot na pulpicie: uruchom dist\ClientWorkbench\Utworz_skrot_na_pulpicie.bat
  goto :done
)
iscc packaging\installer.iss
if errorlevel 1 goto :error

echo.
echo === GOTOWE ===
echo Instalator: dist\installer\ClientWorkbench_Setup_1.0.0.exe
goto :done

:error
echo.
echo BLAD budowania. Sprawdz komunikaty powyzej.
exit /b 1

:done
endlocal
