@echo off
title OpenManus Setup
color 0E

echo ========================================
echo       OpenManus UI Setup
echo ========================================
echo.

:: Navigate to OpenManus directory
cd /d C:\Users\tialc\Documents\GitHub\OpenManus

:: Activate virtual environment
call venv\Scripts\activate.bat

echo Installing required packages for Web UI...
pip install gradio

echo.
echo [OK] Setup complete!
echo.
echo Files created:
echo   - OpenManus_Launcher.bat (Command Line)
echo   - OpenManus_WebUI.bat (Web Interface)
echo   - openmanus_advanced_ui.py (Advanced UI)
echo.
echo Place these files in: C:\Users\tialc\Documents\GitHub\OpenManus
echo.
echo To run:
echo   1. Double-click OpenManus_Launcher.bat for command line
echo   2. Double-click OpenManus_WebUI.bat for web interface
echo.
pause
