@echo off
setlocal
echo ==================================================
echo   Upcycle AI - Auto Setup ^& Launch (Portable)
echo ==================================================

echo.
echo [1/5] Checking Dependencies...

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is missing! Please install Python 3.10 or higher.
    echo Opening download page...
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python is available.

:: Check for Ollama
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Ollama is missing! Checking for winget...
    where winget >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Both Ollama and winget are missing.
        echo Please install Ollama manually from: https://ollama.com/download
        start https://ollama.com/download
        pause
        exit /b 1
    )
    echo Attempting to install Ollama via winget...
    winget install Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [ERROR] Winget installation failed. 
        echo Please install Ollama manually from: https://ollama.com/download
        pause
        exit /b 1
    )
    echo ✅ Ollama installed successfully! 
    echo Please RESTART this script to refresh your system PATH and start.
    pause
    exit /b 0
)
echo ✅ Ollama is available.

echo.
echo [2/5] Starting Ollama Server...
:: Using 'start' to launch the background engine separately
start "Ollama Engine" /MIN cmd /c "ollama serve"
:: Give the engine some time to boot
timeout /t 5 /nobreak >nul

echo.
echo [3/5] Syncing AI Models...
:: CRITICAL: We NO LONGER use '/WAIT' or 'call' for the pull because if your
:: Ollama version is buggy (mlx platform error), it will segfault (0xc0000005)
:: and kill this script. We now launch pull in its own window so the script survives.
echo Ensuring the vision model (moondream) is downloaded...
echo (If a separate window flashes a crash dump, please UPDATE Ollama at https://ollama.com)
start "Ollama Model Sync" cmd /c "ollama pull moondream"

echo.
echo [4/5] Preparing Python Environment...
if not exist ".\.venv\" (
    echo Virtual environment not found. Creating a fresh one...
    python -m venv .venv
    echo Installing required packages (this may take a few minutes)...
    call .\.venv\Scripts\python -m pip install --upgrade pip
    call .\.venv\Scripts\pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Package installation failed. Check your internet and requirements.txt
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully!
) else (
    echo ✅ Python environment is ready.
)

echo.
echo [5/5] Starting FastAPI Backend...
start "FastAPI Backend" cmd /k ".\.venv\Scripts\python -m uvicorn api:app --port 8000"

echo.
echo Opening Application...
timeout /t 6 /nobreak >nul
start http://localhost:8000/

echo.
echo Application started successfully!
pause
