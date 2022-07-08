; �ű��� Inno Setup �ű��� ���ɣ�
; �йش��� Inno Setup �ű��ļ�����ϸ��������İ����ĵ���

#define MyAppName "2048��Ƶ��"
#define MyAppVersion "1.8"
#define MyAppPublisher "2651688427@qq.com"
#define MyAppURL "https://www.example.com/"
#define MyAppExeName "2048_audio.exe"

[Setup]
; ע: AppId��ֵΪ������ʶ��Ӧ�ó���
; ��ҪΪ������װ����ʹ����ͬ��AppIdֵ��
; (��Ҫ�����µ� GUID�����ڲ˵��е�� "����|���� GUID"��)
AppId={{BF5EE9E5-9402-4C15-AFE3-4DB82CDD3A67}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\game_2048_audio
DisableProgramGroupPage=yes
LicenseFile=D:\Src\python\Game\2048\v1.8\dist\license.txt
; ������ȡ��ע�ͣ����ڷǹ���װģʽ�����У���Ϊ��ǰ�û���װ����
;PrivilegesRequired=lowest
OutputDir=d:\src\python\game\2048\v1.8\
OutputBaseFilename=2048_audio-1.8_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Files]
Source: "D:\Src\python\Game\2048\v1.8\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Src\python\Game\2048\v1.8\dist\sounds\*"; DestDir: "{app}\sounds"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\setting.json"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\zdsrapi.dll"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\zdsrapi.ini"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\readMe.html"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\license.txt"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\src.zip"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\nvdaControllerClient32.dll"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Src\python\Game\2048\v1.8\dist\AISound.dll"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ע��: ��Ҫ���κι���ϵͳ�ļ���ʹ�á�Flags: ignoreversion��

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

