@echo off
title OpenManus - Local AI Agent
color 0A

echo ========================================
echo       OpenManus Local AI Agent
echo ========================================
echo.

:: Navigate to OpenManus directory
cd /d C:\Users\tialc\Documents\GitHub\OpenManus

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Set environment variables
set DAYTONA_API_KEY=disabled
set SANDBOX_ENABLED=false

:: Check if Ollama is running
echo Checking Ollama status...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama might not be running. Starting Ollama...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)

echo.
echo [OK] Environment ready
echo [OK] Using model: qwen2.5:7b
echo [OK] Cost: $0/month
echo.
echo ========================================
echo Starting OpenManus...
echo ========================================
echo.

:: Run OpenManus
python main.py

:: Keep window open if error
pause
