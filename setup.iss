[Setup]
AppName=PiecesCLI
AppVersion=1.0
DefaultDirName={pf}\PiecesCLI
DefaultGroupName=PiecesCLI
OutputDir=.
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist/pieces.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PiecesCLI"; Filename: "{app}\PiecesCLI.exe"
Name: "{group}\{cm:UninstallProgram,PiecesCLI}"; Filename: "{uninstallexe}"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandstring; ValueName: "pieces"; ValueData: "{app}"; Flags: uninsdeletevalue

