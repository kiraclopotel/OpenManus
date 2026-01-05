@echo off
title OpenManus AI
color 0A

echo.
echo ========================================
echo       OpenManus AI - Starting...
echo ========================================
echo.

cd /d C:\Users\tialc\Documents\GitHub\OpenManus
call venv\Scripts\activate.bat

set DAYTONA_API_KEY=disabled
set SANDBOX_ENABLED=false

echo Checking dependencies...

pip show uvicorn >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing FastAPI and Uvicorn...
    pip install fastapi uvicorn
)

pip show playwright >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Playwright...
    pip install playwright
)

:: Check if Chromium browser exists
if not exist "%LOCALAPPDATA%\ms-playwright" (
    echo.
    echo Installing Playwright browsers - please wait...
    playwright install chromium
    echo.
)

:: Double check chromium folder
dir "%LOCALAPPDATA%\ms-playwright\chromium*" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Chromium not found. Installing browsers...
    playwright install chromium
    echo.
)

echo.
echo [OK] All dependencies ready
echo [OK] Starting server at http://localhost:8000
echo.

start http://localhost:8000
python server.py

echo.
echo Server stopped.
pause