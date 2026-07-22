@echo off
TITLE NINCore System Launcher

echo ========================================================
echo   Starting NINCore Identity Risk Engine
echo ========================================================
echo.

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found! 
    echo Please run setup.bat first.
    pause
    exit /b
)

echo - Activating Virtual Environment...
call venv\Scripts\activate.bat

echo - Starting FastAPI Backend (Port 8000)...
start "NINCore Backend API" cmd /k "venv\Scripts\uvicorn.exe api.main:app --host 0.0.0.0 --port 8000 --reload"

echo - Waiting for API to initialize...
timeout /t 3 /nobreak > NUL

echo - Starting Streamlit Dashboard (Port 8501)...
start "NINCore Dashboard" cmd /k "venv\Scripts\streamlit.exe run dashboard\app.py"

echo.
echo [OK] All systems are starting up!
echo Close this master window to exit. The API and Dashboard will run in separate windows.
