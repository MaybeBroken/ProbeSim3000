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
where python3 >nul 2>&1
if %errorlevel% neq 0 (
    echo Python3 is not installed. Installing from Microsoft Store...
    start /wait ms-windows-store://pdp/?productid=9PJPW5LDXLZ5
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo Failed to install Python3. Please install it manually.
        pause
        exit /b
    )
)
echo Paths are correct.
python3 -m pip install -r _req.txt > base-output.log
python3 Main.py > base-output.log
pause
