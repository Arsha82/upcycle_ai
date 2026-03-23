@echo off
echo =========================================
echo Starting Upcycle AI
echo =========================================

echo.
echo [1/3] Checking Ollama Models...
:: The ollama pull command is currently commented out because it causes 
:: an internal crash (0xc0000005) on some Windows Ollama versions.
:: If your Ollama is updated and working, you can manually run: ollama pull moondream
:: call ollama pull moondream

echo.
echo [2/3] Starting FastAPI Backend...
echo (The backend serves the pre-built React frontend)
start "FastAPI Backend" cmd /k ".\.venv\Scripts\python -m uvicorn api:app --port 8000"

echo.
echo [3/3] Opening Application...
:: Giving the server a little more time to boot up to prevent browser connection errors
timeout /t 6 /nobreak >nul
start http://localhost:8000/

echo.
echo Application started successfully!
pause
