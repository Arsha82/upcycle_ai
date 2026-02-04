# Upcycling AI

Local-first, offline-capable AI application to suggest upcycling ideas for waste items.

## Prerequisites

1.  **Python 3.10+**
2.  **Ollama**: Installed and running.
    - Pull the vision model: `ollama pull llama3.2-vision`
    - Pull the fallback model (optional): `ollama pull llava`
3.  **Dependencies**:
    - Run `pip install -r requirements.txt`

## Running the App

1.  Open a terminal in this directory.
2.  Run the application:
    ```bash
    streamlit run app.py
    ```
3.  The app will open in your browser (usually `http://localhost:8501`).

## Offline Usage

To use offline, ensure you have:
1.  Pulled all Ollama models while online.
2.  Downloaded any AirLLM models (via HuggingFace) while online.
3.  Installed all pip requirements.

Once these are present, the app requires no internet connection.

## Features

- **Waste Scanning**: Use your camera or upload an image.
- **AI Analysis**: Identifies items and suggests creative upcycling projects.
- **History**: Saves your past scans and ideas locally.
