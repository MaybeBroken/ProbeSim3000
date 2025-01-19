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
echo Paths are correct.
python3 -m pip install -r "_req.txt"
python3 "Main.py"
pause
