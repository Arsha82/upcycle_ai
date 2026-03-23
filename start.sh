#!/bin/bash
echo "=================================================="
echo "  Upcycle AI - Auto Setup & Launch (Portable)"
echo "=================================================="

echo ""
echo "[1/4] Checking Ollama Installation..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama is missing! Attempting to install..."
    curl -fsSL https://ollama.com/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "Installation failed. Please manually install from https://ollama.com/download"
        exit 1
    fi
    echo "✅ Ollama installed successfully!"
fi

echo ""
echo "[2/4] Starting Ollama Server..."
# Start ollama serve in the background, suppressing output
ollama serve >/dev/null 2>&1 &
OLLAMA_PID=$!
sleep 3

echo "Pulling the required AI vision model (moondream)..."
ollama pull moondream

echo ""
echo "[3/4] Checking Python Environment..."
if [ ! -d ".venv" ]; then
    echo "Python environment not found. Creating a fresh virtual environment..."
    python3 -m venv .venv
    echo "Installing required packages (this may take a few minutes)..."
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo "✅ Dependencies installed successfully!"
else
    echo "✅ Python environment is ready."
fi

echo ""
echo "[4/4] Starting FastAPI Backend..."
echo "(The backend serves the pre-built React frontend entirely locally)"
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
uvicorn api:app --port 8000 &
BACKEND_PID=$!

echo ""
echo "Opening Application..."
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
