[Setup]
AppName=Pieces CLI
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
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "pieces"; ValueData: "{app}"; Flags: uninsdeletevalue
