@echo off
title OpenManus Web UI
color 0B

echo ========================================
echo       OpenManus Web Interface
echo ========================================
echo.

cd /d C:\Users\tialc\Documents\GitHub\OpenManus
call venv\Scripts\activate.bat

set DAYTONA_API_KEY=disabled
set SANDBOX_ENABLED=false

echo Checking Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)

echo.
echo [OK] Ready - Opening http://localhost:7860
echo.

python openmanus_webui.py

pause
