; Inno Setup 安装脚本
; 使用前请先运行 build_exe.bat 生成 dist\ChinesePaperGenerator

[Setup]
AppId={{A0D41456-59B2-4C92-A7DD-8C1F4D0D8C01}
AppName=中文论文生成器
AppVersion=1.0.0
AppPublisher=Paper Agent Team
DefaultDirName={autopf}\ChinesePaperGenerator
DefaultGroupName=中文论文生成器
DisableProgramGroupPage=yes
OutputDir=dist_installer
OutputBaseFilename=ChinesePaperGeneratorSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\ChinesePaperGenerator\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\中文论文生成器"; Filename: "{app}\ChinesePaperGenerator.exe"
Name: "{autodesktop}\中文论文生成器"; Filename: "{app}\ChinesePaperGenerator.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面图标"; GroupDescription: "附加任务:"; Flags: unchecked

[Run]
Filename: "{app}\ChinesePaperGenerator.exe"; Description: "启动中文论文生成器"; Flags: nowait postinstall skipifsilent
