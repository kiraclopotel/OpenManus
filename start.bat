@echo off
title OpenManus AI
color 0A

:: Get the directory where this script is located
cd /d "%~dp0"

echo.
echo ============================================================
echo                    OpenManus AI Agent
echo ============================================================
echo.

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run install.bat first.
    echo.
    pause
    exit /b 1
)

:: Activate venv
call venv\Scripts\activate.bat

:: Set environment variables
set DAYTONA_API_KEY=disabled
set SANDBOX_ENABLED=false

:: Check Ollama
echo Checking Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Ollama doesn't seem to be running.
    echo Starting Ollama...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)
echo Ollama OK.

:: Check if server.py exists
if not exist "server.py" (
    echo ERROR: server.py not found.
    echo Please make sure all files are in place.
    pause
    exit /b 1
)

:: Check if ui.html exists
if not exist "ui.html" (
    echo ERROR: ui.html not found.
    echo Please make sure all files are in place.
    pause
    exit /b 1
)

echo.
echo Starting OpenManus...
echo.
echo ============================================================
echo   Web UI: http://localhost:8000
echo   Press Ctrl+C to stop
echo ============================================================
echo.

:: Open browser
start http://localhost:8000

:: Start server
python server.py

echo.
echo Server stopped.
pause