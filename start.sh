#!/bin/bash
echo "========================================="
echo "Starting Upcycle AI"
echo "========================================="

echo ""
echo "[1/3] Checking Ollama Models..."
# The ollama pull command is currently commented out because it causes 
# an internal crash (0xc0000005) on some Windows Ollama versions.
# If your Ollama is updated and working, you can manually run: ollama pull moondream
# ollama pull moondream

echo ""
echo "[2/3] Starting FastAPI Backend..."
echo "(The backend serves the pre-built React frontend)"
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
uvicorn api:app --port 8000 &
BACKEND_PID=$!

echo ""
echo "[3/3] Opening Application..."
# Giving the server a little more time to boot up to prevent browser connection errors
sleep 6
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:8000/
elif command -v open > /dev/null; then
  open http://localhost:8000/
fi

echo ""
echo "Full system running. Press Ctrl+C to stop."
wait $BACKEND_PID
