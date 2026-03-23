#!/bin/bash
echo "=================================================="
echo "  Upcycle AI - Auto Setup & Launch (Portable)"
echo "=================================================="

echo ""
echo "[1/5] Checking Dependencies..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is missing! Please install Python 3.10 or higher."
    exit 1
fi
echo "✅ Python is available."

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "Ollama is missing! Attempting to install..."
    curl -fsSL https://ollama.com/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "[ERROR] Installation failed. Please manually install from https://ollama.com/download"
        exit 1
    fi
    echo "✅ Ollama installed successfully!"
fi
echo "✅ Ollama is available."

echo ""
echo "[2/5] Starting Ollama Server..."
# Start ollama serve in the background, suppressing output
ollama serve >/dev/null 2>&1 &
sleep 5

echo ""
echo "[3/5] Syncing AI Models..."
echo "Ensuring the vision model (moondream) is downloaded..."
ollama pull moondream

echo ""
echo "[4/5] Preparing Python Environment..."
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating a fresh one..."
    python3 -m venv .venv
    echo "Installing required packages (this may take a few minutes)..."
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Package installation failed."
        exit 1
    fi
    deactivate
    echo "✅ Dependencies installed successfully!"
else
    echo "✅ Python environment is ready."
fi

echo ""
echo "[5/5] Starting FastAPI Backend..."
source .venv/bin/activate
uvicorn api:app --port 8000 &
BACKEND_PID=$!

echo ""
echo "Opening Application... (12s countdown)"
sleep 12
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:8000/
elif command -v open > /dev/null; then
  open http://localhost:8000/
fi

echo ""
echo "Full system running. Press Ctrl+C to stop."
wait $BACKEND_PID
