@echo off
REM Tworzy skrot "Client Workbench" na pulpicie z wbudowana ikona aplikacji.
REM Umiesc ten plik w folderze obok ClientWorkbench.exe i uruchom (podwojny klik).
REM Nie wymaga uprawnien administratora.

setlocal
set "TARGET=%~dp0ClientWorkbench.exe"
set "WORKDIR=%~dp0"
set "SHORTCUT=%USERPROFILE%\Desktop\Client Workbench.lnk"

if not exist "%TARGET%" (
  echo BLAD: nie znaleziono ClientWorkbench.exe obok tego pliku.
  echo Umiesc ten skrypt w folderze z aplikacja.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('%SHORTCUT%'); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%WORKDIR%'; $s.IconLocation='%TARGET%,0'; $s.Description='Client Workbench'; $s.Save()"

echo.
echo Gotowe — skrot "Client Workbench" jest na pulpicie.
pause
endlocal
