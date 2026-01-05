@echo off
title OpenManus - First Time Setup
color 0E

echo.
echo ============================================================
echo         OpenManus - First Time Installation
echo ============================================================
echo.
echo This will set up everything needed to run OpenManus locally.
echo.

:: Get the directory where this script is located
cd /d "%~dp0"
set "OPENMANUS_DIR=%CD%"

echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11 or 3.12 from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo       Python found.

echo.
echo [2/7] Checking for Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Ollama not found. 
    echo Please install Ollama from https://ollama.com
    echo Then run: ollama pull qwen2.5:7b
    echo.
    echo Press any key to continue anyway...
    pause >nul
) else (
    echo       Ollama found.
)

echo.
echo [3/7] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo       Virtual environment created.
) else (
    echo       Virtual environment already exists.
)

echo.
echo [4/7] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install fastapi uvicorn --quiet
echo       Dependencies installed.

echo.
echo [5/7] Installing Playwright browsers...
pip install playwright --quiet
playwright install chromium
echo       Playwright browsers installed.

echo.
echo [6/7] Setting up configuration...
if not exist "config\config.toml" (
    echo       Creating config.toml for local Ollama...
    (
        echo # OpenManus Configuration - Local Ollama Setup
        echo.
        echo [llm]
        echo api_type = "ollama"
        echo model = "qwen2.5:7b"
        echo base_url = "http://localhost:11434/v1"
        echo api_key = "ollama"
        echo max_tokens = 4096
        echo temperature = 0.0
        echo.
        echo [llm.vision]
        echo api_type = "ollama"
        echo model = "qwen2.5:7b"
        echo base_url = "http://localhost:11434/v1"
        echo api_key = "ollama"
        echo max_tokens = 4096
        echo temperature = 0.0
        echo.
        echo [browser]
        echo headless = false
        echo.
        echo [search]
        echo engine = "duckduckgo"
        echo.
        echo [sandbox]
        echo use_sandbox = false
    ) > config\config.toml
    echo       Configuration created.
) else (
    echo       Configuration already exists.
)

echo.
echo [7/7] Verifying installation...
call venv\Scripts\activate.bat
python -c "import fastapi; import playwright; print('All packages OK')" 2>nul
if %errorlevel% neq 0 (
    echo       WARNING: Some packages may not be installed correctly.
) else (
    echo       All packages verified.
)

echo.
echo ============================================================
echo         Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Make sure Ollama is running: ollama serve
echo   2. Pull a model if needed: ollama pull qwen2.5:7b
echo   3. Run start.bat to launch OpenManus
echo.
pause