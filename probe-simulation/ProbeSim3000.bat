@echo off
python --version 2>nul | findstr /r /c:"Python 3\.[1-9][2-9]" >nul
if %errorlevel% neq 0 (
    echo Python 3.12 or greater is not installed.
    echo Installing Python 3.12...
    powershell -Command "Start-Process msiexec.exe -ArgumentList '/i https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1' -NoNewWindow -Wait"
)

pip list --outdated 2>nul | findstr /r /c:"pip" >nul
if %errorlevel% equ 0 (
    echo Updating package manager...
    python -m pip install --upgrade pip
)
python Main.py
pause