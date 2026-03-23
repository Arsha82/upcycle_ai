@echo off
setlocal
echo ==================================================
echo   Upcycle AI - Safe Mode Startup
echo ==================================================
echo (If a separate window flashes a crash dump (0xc0000005), 
echo  it means your Ollama is OUTDATED. Update at https://ollama.com)
echo.

echo [1/3] Setting up Python Environment...
if not exist ".\.venv\" (
    echo [FIRST RUN ONLY] Creating virtual environment and installing packages...
    python -m venv .venv
    call .\.venv\Scripts\python -m pip install --upgrade pip
    call .\.venv\Scripts\pip install -r requirements.txt
    echo ✅ Environment ready.
)

echo [2/3] Starting AI Services (Isolated)...
:: Running both Ollama commands in a separate process that won't kill this script
start "Upcycle AI - Ollama Serve" cmd /c "echo Starting server... & ollama serve || echo [ERROR] Ollama server failed to start."
timeout /t 3 /nobreak >nul
start "Upcycle AI - Ollama Sync" cmd /c "echo Syncing models... & ollama pull moondream || echo [ERROR] Model pull failed."

echo [3/3] Launching App...
:: Running the backend in a separate window
start "Upcycle AI - FastAPI Backend" cmd /k ".\.venv\Scripts\python -m uvicorn api:app --port 8000"

echo.
echo Application is initializing...
timeout /t 6 /nobreak >nul
start http://localhost:8000/

echo ✅ Success! The server is running in its own window.
pause
