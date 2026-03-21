#!/bin/bash
echo "Starting FastAPI Backend..."
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
uvicorn api:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting React Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Both servers are running. Press Ctrl+C to stop."
wait $BACKEND_PID $FRONTEND_PID
