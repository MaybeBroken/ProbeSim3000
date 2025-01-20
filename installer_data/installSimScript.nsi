; NSIS script for ProbeSim3000 installer

!define MUI_PRODUCT "ProbeSim3000"
RequestExecutionLevel admin
VIProductVersion "1.4.0.0"
VIAddVersionKey /LANG=1033 "ProductName" "ProbeSim3000"
VIAddVersionKey /LANG=1033 "CompanyName" "MaybeBroken"
VIAddVersionKey /LANG=1033 "LegalCopyright" "© MaybeBroken 2024. All rights reserved."
VIAddVersionKey /LANG=1033 "FileDescription" "ProbeSim3000 Installer"
VIAddVersionKey /LANG=1033 "FileVersion" "1.4.0.0"
!include "MUI2.nsh"
OutFile "ProbeSim3000-Installer.exe"
Name "ProbeSim3000"
InstallDir $PROFILE\ProbeSim3000

!insertmacro MUI_PAGE_LICENSE "C:\Users\david\git\ProbeSim3000\installer_data\LICENSE.txt"
Page custom UninstallPageCreate UninstallPageLeave
Page custom CustomInstallationPageCreate CustomInstallationPageLeave
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_LANGUAGE "English"

Var RADIOBUTTON

Section "Install"
    SetOutPath $INSTDIR
    Call installFiles
    CreateShortcut "$DESKTOP\ProbeSim3000.lnk" "$INSTDIR\ProbeSim3000.bat"
SectionEnd

Function CustomInstallationPageCreate
    nsDialogs::Create 1018
    ${NSD_CreateLabel} 0u 0u 100% 12u "How do you want the program to be installed?"
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
    SetOutPath $TEMP\ProbeSim3000
    Call installFiles
    ExecWait '"$TEMP\ProbeSim3000\ProbeSim3000.bat"'
    RMDir /r $TEMP\ProbeSim3000
    Abort
FunctionEnd

Function installFiles
    File /r /x "*.blend" /x "*.xcf" /x "*.pyc" "C:\Users\david\git\ProbeSim3000\probe-simulation\*"
FunctionEnd