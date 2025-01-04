; Basic NSIS Installer Script

; Name of the installer
OutFile "ProbeSim3000_Installer.exe"

; Default installation directory
InstallDir $PROFILE\ProbeSim3000

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
    File /r "C:\Users\david\git\ProbeSim3000\probe-simulation\*"

    ; Create a shortcut on the desktop
    CreateShortcut "$DESKTOP\ProbeSim3000.lnk" "$INSTDIR\ProbeSim3000.bat"

SectionEnd