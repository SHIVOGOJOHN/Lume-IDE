[Setup]
AppName=Lume
AppVersion=0.9.0
AppPublisher=John Shivogo
DefaultDirName={autopf}\Lume
DefaultGroupName=Lume
OutputBaseFilename=Lume_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=logo.ico

[Files]
; Onefile Nuitka build
Source: "Lume.exe"; DestDir: "{app}"; Flags: ignoreversion

; If you switch away from --onefile, use the standalone folder instead:
; Source: "luau_ide.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lume"; Filename: "{app}\Lume.exe"
Name: "{commondesktop}\Lume"; Filename: "{app}\Lume.exe"

[Run]
Filename: "{app}\Lume.exe"; Description: "Launch Lume"; Flags: nowait postinstall skipifsilent
