; Inno Setup — instalator Client Workbench (Windows 11)
; Wymaga: Inno Setup 6+ (https://jrsoftware.org/isdl.php)
; Budowanie: iscc packaging\installer.iss  (po wcześniejszym pyinstaller)

#define AppName "Client Workbench"
#define AppVersion "1.0.0"
#define AppPublisher "Client Workbench"
#define AppExeName "ClientWorkbench.exe"

[Setup]
AppId={{7E2C1A94-3B6D-4F0E-9C2A-CW2026DASH20}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\ClientWorkbench
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=ClientWorkbench_Setup_{#AppVersion}
SetupIconFile=..\resources\app_icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
; Ikona na pulpicie — domyślnie zaznaczona
Name: "desktopicon"; Description: "Utwórz ikonę na pulpicie"; GroupDescription: "Dodatkowe skróty:"; Flags: checkedonce

[Files]
; Cała zawartość folderu zbudowanego przez PyInstaller (onedir)
Source: "..\dist\ClientWorkbench\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
; Menu Start
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\resources\app_icon.ico"
; Pulpit (dedykowana ikona)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\resources\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Uruchom {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Dane użytkownika (baza, zdjęcia, kopie) pozostają w %LOCALAPPDATA%\ClientWorkbench
Type: filesandordirs; Name: "{app}\_internal"
