; Script for Hotel and Event Management System Installer
#define MyAppName "Hotel and Event Management App"
#define MyAppVersion "2.0"
#define MyAppPublisher "School of Accounting Package"
#define MyAppURL "https://www.example.com/"
#define MyAppExeName "python.exe"

[Setup]
PrivilegesRequired=admin
AppId={{7C26CBC0-0FD9-4943-9A21-2204ED49422F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=C:\Users\KLOUNGE\Documents\HEMS-main\license.txt
OutputDir=C:\Users\KLOUNGE\Desktop
OutputBaseFilename=hems-app-installerE1
SetupIconFile=C:\Users\KLOUNGE\Documents\HEMS-main\hems-inst.ico
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked  

[Files]
; Copy application files
Source: "C:\Users\KLOUNGE\Documents\HEMS-main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Copy embedded Python
Source: "C:\Users\KLOUNGE\Documents\HEMS-main\python-embed\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\python\{#MyAppExeName}"; Parameters: """{app}\start.py"""; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\python\{#MyAppExeName}"; Parameters: """{app}\start.py"""; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Open firewall for the application
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""HEMS"" dir=in action=allow protocol=TCP localport=8000"; Flags: runhidden

; Run the application using embedded Python
Filename: "{app}\python\{#MyAppExeName}"; Parameters: """{app}\start.py"""; WorkingDir: "{app}"; Flags: nowait runminimized