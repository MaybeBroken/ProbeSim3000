; Basic NSIS Installer Script

; Name of the installer
OutFile "ProbeSim3000-Server_Installer.exe"

; Default installation directory
InstallDir $PROFILE\ProbeSim3000-Server

; Request application privileges for Windows Vista and higher
RequestExecutionLevel user

; Pages to be displayed
Page license
Page directory
Page instfiles

; License file to be displayed
LicenseData "C:\Users\david\git\ProbeSim3000\installer_data\LICENSE.txt"

; Section to install files
Section "Install"

    ; Set output path to the installation directory
    SetOutPath $INSTDIR

    ; Add files to be installed
    File /r "C:\Users\david\git\ProbeSim3000\probe-simulation_server\*"

    ; Create a shortcut on the desktop
    CreateShortcut "$DESKTOP\ProbeSim-Server.lnk" "$INSTDIR\ProbeSim-Server.bat"

SectionEnd