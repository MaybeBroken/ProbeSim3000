; NSIS script for ProbeSim3000-Server installer

!define MUI_PRODUCT "ProbeSim3000-Server"
!include "MUI2.nsh"
OutFile "ProbeSim3000-Server-Installer.exe"
Name "ProbeSim3000-Server"
InstallDir $PROFILE\ProbeSim3000-Server
RequestExecutionLevel admin

!insertmacro MUI_PAGE_LICENSE "C:\Users\david\git\ProbeSim3000\installer_data\LICENSE.txt"
Page custom CustomInstallationPageCreate CustomInstallationPageLeave
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Var RADIOBUTTON

Section "Install"
    SetOutPath $INSTDIR
    ; File "C:\Users\david\git\ProbeSim3000\installer_data\python-3.13.0.exe"
    ; ExecWait '"$INSTDIR\python-3.13.0.exe" InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=0 TargetDir="$INSTDIR\python\"'
    File /r /x "*.blend" /x "*.xcf" /x "*.pyc" "C:\Users\david\git\ProbeSim3000\probe-simulation_server\*"
    CreateShortcut "$DESKTOP\ProbeSim-Server.lnk" "$INSTDIR\ProbeSim-Server.bat"
SectionEnd

Function CustomInstallationPageCreate
    nsDialogs::Create 1018
    ${NSD_CreateLabel} 0u 0u 100% 12u "How do you want the server to be installed?"
    Pop $0
    ${NSD_CreateRadioButton} 0u 15u 100% 12u "Single time launch" 1018
    Pop $0
    StrCpy $RADIOBUTTON $0
    ${NSD_CreateRadioButton} 0u 30u 100% 12u "Install as an application" 1018
    Pop $0
    nsDialogs::Show
FunctionEnd

Function CustomInstallationPageLeave
    ${NSD_GetState} $RADIOBUTTON $0
    StrCmp $0 1 SingleTimeLaunch
    Return

SingleTimeLaunch:
    SetOutPath $TEMP\ProbeSim3000-Server
    File /r /x "*.blend" /x "*.xcf" /x "*.pyc" "C:\Users\david\git\ProbeSim3000\probe-simulation_server\*"
    ExecWait '"$TEMP\ProbeSim3000-Server\ProbeSim-Server.bat"'
    RMDir /r $TEMP\ProbeSim3000-Server
    Abort
FunctionEnd
