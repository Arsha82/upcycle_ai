<div align="center">

# Upcycling AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![Offline](https://img.shields.io/badge/Connectivity-Offline%20Capable-2ea44f?style=for-the-badge)](https://github.com/ollama/ollama)

<br />

[![Watch the Demo](demo.png)](https://youtu.be/dUZK9wBlSqQ)

<br />

**Local-first, offline-capable AI application to suggest upcycling ideas for waste items.**

This application empowers users to turn waste into wealth by identifying objects and suggesting creative upcycling projects. Built with privacy and accessibility in mind, it runs entirely on your local machine.

</div>

---

## Table of Contents

- [Key Features & Advantages](#key-features--advantages)
- [Tech Stack](#tech-stack)
- [Workflow](#workflow)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [Usage Guide](#usage-guide)

---

## Key Features & Advantages

### Works Completely Offline
Perfect for rural areas or locations with unstable internet. Once the models are downloaded, **no internet connection is required** to use the app. It brings the power of advanced AI to the edge.

### Zero Cost - No APIs
Say goodbye to monthly subscriptions and per-token costs. This app does **not** rely on paid APIs like OpenAI or Anthropic. It uses open-source models (Llama 3.2 Vision, Llava) running locally on your hardware.

### Privacy First
Your photos and data never leave your device. Everything is processed locally, ensuring complete privacy and security for your personal data.

### Smart Waste Analysis
- **Instant Recognition**: Identify waste items using your webcam or uploaded images.
- **Creative Ideas**: Get step-by-step DIY upcycling guides tailored to the specific item.
- **History Tracking**: Automatically saves your scans and ideas for future reference.

---

## Tech Stack

This project leverages a modern, open-source stack designed for local inference and performance:

- **Frontend**: [Streamlit](https://streamlit.io/) - Provides the interactive web interface for image capture and display.
- **AI Backend**: [Ollama](https://ollama.com/) - Manages local LLM inference.
- **Models**:
    - **Vision**: `llama3.2-vision` (Primary) or `llava` (Fallback) for image understanding.
    - **Logic**: `llama3` family for reasoning and text generation.
- **Database**: **SQLite** - A lightweight, file-based database to store user history and saved upcycling ideas locally.
- **Language**: **Python 3.10+**

---

## Workflow

The application follows a streamlined local processing pipeline:

1.  **Input Acquisition**: The user captures an image via the webcam or uploads a file through the Streamlit interface.
2.  **Preprocessing**: The image is converted to bytes and prepared for the inference engine.
3.  **Local Inference**:
    - **Standard Strategy**: The image and prompt are sent directly to a vision-capable model (like Llama 3.2 Vision).
    - **Chain Strategy**: For smaller hardware, the app splits the task:
        1.  *Vision Step*: A specialized small model (e.g., Moondream) describes the image.
        2.  *Reasoning Step*: A text-only model (e.g., Llama 3) takes that description and generates the creative project ideas.
4.  **Response Generation**: The AI generates a structured markdown response with project titles, difficulty levels, and instructions.
5.  **Persistence**: The image is saved to disk, and the metadata (timestamp, item name, response) is committed to the local SQLite database.

---

## Installation & Setup

Follow these steps to get up and running in minutes.

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.10** or higher ([Download Here](https://www.python.org/downloads/))
- **Ollama**: This creates the local AI server. ([Download Ollama](https://ollama.com/download))

### 2. Download Models
Open your terminal or command prompt and run the following commands to download the necessary AI brains. You need internet for this step only.

```bash
# Pull the main vision model (Recommended)
ollama pull llama3.2-vision

# (Optional) Pull a fallback model
ollama pull llava
```

### 3. Install Dependencies
Navigate to the project folder and install the Python requirements:

```bash
pip install -r requirements.txt
```

---

## How to Run

1.  Open a terminal in the project directory.
2.  Start the application with:
    ```bash
    streamlit run app.py
    ```
3.  The app will open automatically in your browser (usually at `http://localhost:8501`).

---

## Usage Guide

1.  **Select Input Method**: Choose between "Camera" to snap a photo or "Upload" to use an existing image.
2.  **Analyze**: Click the button to let the AI scan the item.
3.  **Get Inspired**: Read through the suggested upcycling projects, materials needed, and step-by-step instructions.
4.  **Save/History**: Your results are saved automatically. Check the sidebar to revisit past ideas!

---

<div align="center">
    <i>Built for a sustainable future.</i>
</div>
