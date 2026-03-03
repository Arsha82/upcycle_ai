from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import io
import datetime
from database import init_db, save_recipe, get_history as get_all_recipes
from inference import get_inference_engine
from typing import List, Optional

app = FastAPI(title="Upcycle AI API")

# Enable CORS so the Svelte frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. Restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the db on startup
init_db()

# Serve images statically for the frontend Explore page
base_dir = os.path.dirname(os.path.abspath(__file__))
uploads_dir = os.path.join(base_dir, "uploads")
images_dir = os.path.join(base_dir, "images")

if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
if os.path.exists(images_dir):
    app.mount("/images", StaticFiles(directory=images_dir), name="images")

# --- Configurations ---
MODEL_PROVIDER = "Ollama" # Hardcoded for now, can be dynamic
MODEL_NAME = "moondream:latest" # Default vision model

class GenerationRequest(BaseModel):
    selected_items: List[str]
    equipment: str
    image_path: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Upcycle AI API is running."}

@app.post("/api/vision")
async def extract_items_from_image(file: UploadFile = File(...)):
    """
    Accepts an image, runs Moondream vision inference, and returns a list of items.
    """
    try:
        engine = get_inference_engine(MODEL_PROVIDER, MODEL_NAME)
        image_bytes = await file.read()
        
        # Save image temporarily for inference if needed, or pass bytes
        # Save permanently to disk if we want to show it in the results later
        from app import save_image_to_disk # Reuse existing logic or replicate it
        # Actually, let's replicate the simple saving to avoid circular imports.
        
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        saved_path = os.path.join(upload_dir, f"img_{timestamp}.{ext}")
        
        with open(saved_path, "wb") as f:
            f.write(image_bytes)

        # Run Vision
        raw_csv_response = engine.run_vision(image_bytes)
        
        # Parse into list
        items = [item.strip() for item in raw_csv_response.split(',') if item.strip()]
        
        return {
            "status": "success",
            "items": items,
            "image_path": saved_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_project(req: GenerationRequest):
    """
    Accepts an array of items and equipment, runs Qwen Reasoning RAG, and returns project text.
    """
    try:
        engine = get_inference_engine(MODEL_PROVIDER, MODEL_NAME) # Provider handles model routing internally
        
        base_prompt = """
        You are an expert DIY and Upcycling Assistant. A user wants to upcycle the provided items.
        
        1. BRAINSTORM 3 distinct, creative, and practical upcycling ideas for these items.
           - Idea 1: Simple/Quick (5-10 mins)
           - Idea 2: Moderate/Decorative (30-60 mins)
           - Idea 3: Advanced/Functional (Project)
        
        2. DETAILED INSTRUCTIONS for ONE of the best ideas above:
           - List materials and tools needed.
           - Step-by-step assembly instructions.
           - Safety tips.

        Format your response with clear Markdown headings (##) and bullet points. Be enthusiastic and encouraging!
        """
        
        # Note: reasoning_model is internally hardcoded to qwen2.5:1.5b in inference.py
        response = engine.run_reasoning(
            selected_items=req.selected_items,
            equipment=req.equipment,
            prompt=base_prompt,
            use_rag=True
        )
        
        # Save to DB
        item_name = ", ".join(req.selected_items)[:50]
        if req.image_path and os.path.exists(req.image_path):
            save_recipe(item_name, response, req.image_path)
            
        return {
            "status": "success",
            "project_markdown": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def get_history():
    """Returns saved projects from the SQLite DB"""
    try:
        recipes = get_all_recipes()
        # Convert tuples to dict for json serialization
        result = []
        for r in recipes:
            result.append({
                "id": r[0],
                "item_name": r[1],
                "recipe_text": r[2],
                "image_path": r[3],
                "created_at": r[4]
            })
        return {"status": "success", "history": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/explore")
def get_explore():
    """Returns saved projects from the SQLite DB for the Explore Feed"""
    try:
        recipes = get_all_recipes() # Currently using history, can add pagination/randomization here later
        
        result = []
        for r in recipes:
            result.append({
                "id": r[0],
                "item_name": r[1],
                "recipe_text": r[2],
                "image_path": r[3],
                "created_at": r[4]
            })
        return {"status": "success", "explore_feed": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
