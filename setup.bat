@echo off
TITLE NINCore Setup Wizard

echo ========================================================
echo   NINCore Full Setup Utility
echo ========================================================
echo.

echo [1/5] Checking Python Installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your system PATH!
    pause
    exit /b
)
python --version

echo.
echo [2/5] Creating Python Virtual Environment (venv)...
python -m venv venv

echo.
echo [3/5] Installing Dependencies from requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/5] Initializing SQLite Database Schema...
python scripts\setup_database.py

echo.
echo [5/5] Generating Synthetic Dataset (This may take a minute)...
python scripts\generate_dataset.py

echo.
echo ========================================================
echo   Setup Successfully Completed!
echo   You can now start the entire system by double-clicking:
echo   run.bat
echo ========================================================
pause
