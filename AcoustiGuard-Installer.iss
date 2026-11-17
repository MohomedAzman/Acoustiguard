
#define MyAppName "AcoustiGuard"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AcoustiGuard Project"

[Setup]
AppId={{A93D1C78-2F64-4A91-9B27-6F81C04E2D35}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\AcoustiGuard
DefaultGroupName=AcoustiGuard
PrivilegesRequired=lowest
OutputDir=release_output
OutputBaseFilename=AcoustiGuard-Setup
SetupIconFile=assets\AcoustiGuard.ico
UninstallDisplayIcon={app}\AcoustiGuard.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
Uninstallable=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "dist_release\AcoustiGuard\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\AcoustiGuard"; Filename: "{app}\AcoustiGuard.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\AcoustiGuard"; Filename: "{app}\AcoustiGuard.exe"; WorkingDir: "{app}"; Tasks: desktopicon
