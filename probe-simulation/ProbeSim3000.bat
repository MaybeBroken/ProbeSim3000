@echo off
echo launching from %cd%
echo Checking paths...
if not exist "_req.txt" (
  echo Requirements file not found at "_req.txt"
  pause
)
if not exist "Main.py" (
  echo Main script not found at "Main.py"
  pause
)
python3 --version >nul 2>&1
if %errorlevel% neq 0 (
  echo Python3 is not installed. Installing from Microsoft Store...
  start ms-windows-store://pdp/?productid=9PJPW5LDXLZ5
  echo Waiting for Python3 installation to complete...
  :wait_for_python
  timeout /t 1 >nul
  python3 --version >nul 2>&1
  if %errorlevel% neq 0 (
    goto wait_for_python
  )
)
echo Paths are correct.
python3 -m pip install -r "_req.txt" > base-output.dat
python3 "Main.py" > base-output.dat
echo Python output has been saved to %cd%\base-output.dat
echo Engine output has been saved to %cd%\engine-debug.dat
pause
