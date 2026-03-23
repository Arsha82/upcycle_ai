@echo off
setlocal
echo ==================================================
echo   Upcycle AI - Auto Setup ^& Launch (Portable)
echo ==================================================

echo.
echo [1/4] Checking Ollama Installation...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Ollama is missing! Attempting to install via Windows Package Manager (winget)...
    winget install Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo Winget installation failed. 
        echo Please download and install Ollama manually from: https://ollama.com/download
        start https://ollama.com/download
        pause
        exit /b 1
    )
    echo ✅ Ollama installed successfully! Please restart this script to continue.
    pause
    exit /b 0
)

echo.
echo [2/4] Starting Ollama Server...
:: Launching the Ollama background engine in a hidden/minimized window
start "Ollama Engine" /MIN ollama serve >nul 2>nul
:: Give the engine a couple seconds to boot
timeout /t 3 /nobreak >nul

echo Pulling the required AI vision model (moondream)...
call ollama pull moondream

echo.
echo [3/4] Checking Python Environment...
if not exist ".\.venv\" (
    echo Python environment not found. Creating a fresh virtual environment...
    python -m venv .venv
    echo Installing required packages (this may take a few minutes)...
    call .\.venv\Scripts\python -m pip install --upgrade pip
    call .\.venv\Scripts\pip install -r requirements.txt
    echo ✅ Dependencies installed successfully!
) else (
    echo ✅ Python environment is ready.
)

echo.
echo [4/4] Starting FastAPI Backend...
echo (The backend serves the pre-built React frontend entirely locally)
start "FastAPI Backend" cmd /k ".\.venv\Scripts\python -m uvicorn api:app --port 8000"

echo.
echo Opening Application...
:: Giving the Python server 6 seconds to boot up to prevent browser connection errors
timeout /t 6 /nobreak >nul
start http://localhost:8000/

echo.
echo Application started successfully!
pause
