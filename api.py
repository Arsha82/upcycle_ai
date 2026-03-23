from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
import io
import traceback
from PIL import Image
import shutil

from starlette.concurrency import run_in_threadpool
from database import init_db, get_history, save_recipe
from inference import get_inference_engine
from utils import save_image_to_disk
from rag_utils import get_rag_manager

app = FastAPI(title="Upcycle API React Backend")

# Determine the absolute path to the frontend dist folder
# Works regardless of where you launch the server from
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIST = os.path.join(_BASE_DIR, "frontend", "dist")

# Enable CORS for the local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In dev, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/status")
def api_status():
    """Health check — confirm the backend is alive."""
    return {"status": "Upcycle API is running smoothly."}

@app.get("/")
def read_root():
    """Serve the React SPA entry point."""
    index = os.path.join(_FRONTEND_DIST, "index.html")
    if os.path.isfile(index):
        return FileResponse(
            index,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Pragma": "no-cache",
            },
        )
    return {"status": "Upcycle API is running smoothly. (Frontend not built yet)"}

@app.get("/api/history")
def read_history():
    """Fetch all Database History items formatted for React Home page."""
    rows = get_history()
    results = []
    import string
    for row in rows:
        # row: (id, image_path, item_name, api_response, timestamp)
        image_path = row[1]
        image_url = f"http://localhost:8000/api/media?path={image_path}" if image_path else None
        
        # We try to extract a brief summary from the markdown response
        response_text = row[3] or ""
        lines = [line.strip() for line in response_text.split('\n') if line.strip() and not line.startswith('#')]
        desc = lines[0] if lines else "AI-generated upcycling project instructions."
        if len(desc) > 150:
            desc = desc[:147] + "..."

        results.append({
            "id": row[0],
            "title": row[2] or "Unknown Item",
            "desc": desc,
            "bgImage": image_url,
            "details": f"Scan Date: {row[4]}\nAI Model: Local Device Pipeline\nStatus: Processed",
            "raw_response": response_text
        })
    return results

@app.get("/api/history/{item_id}")
def read_history_item(item_id: int):
    """Fetch a single exact history item by ID for the ItemDetail layout."""
    rows = get_history()
    for row in rows:
        if row[0] == item_id:
            image_path = row[1]
            image_url = f"http://localhost:8000/api/media?path={image_path}" if image_path else None
            return {
                "id": row[0],
                "title": row[2],
                "image_url": image_url,
                "response": row[3],
                "timestamp": row[4]
            }
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/api/media")
def serve_media(path: str):
    """Serve local uploaded images securely."""
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Media file not found")
    return FileResponse(path)

class ScanRequest(BaseModel):
    items: list[str]
    equipment: str

# Real Inference Endpoints
@app.post("/api/scan")
async def scan_image(file: UploadFile = File(...)):
    engine = get_inference_engine("Ollama", "moondream")
    raw_bytes = await file.read()
    try:
        # CRITICAL FIX: The frontend might send PNG/WebP.
        # Saving raw bytes directly to a .jpg temp file causes Ollama's vision encoder
        # to catastrophically fail and hallucinate <unk> gibberish.
        # We must explicitly convert it to a clean RGB JPEG stream first.
        image = Image.open(io.BytesIO(raw_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        clean_jpeg_bytes = img_byte_arr.getvalue()
        
        # Offload the massively blocking CPU/GPU vision model iteration away from the 
        # Uvicorn main async event loop. Otherwise /api/history requests will freeze endlessly!
        items_str = await run_in_threadpool(engine.run_vision, clean_jpeg_bytes)
        # Parse the comma-separated or newline-separated items
        items_list = [i.strip() for i in items_str.replace('\n', ',').split(',') if i.strip()]
        return {"items": items_list[:6]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_project(req: ScanRequest):
    engine = get_inference_engine("Ollama", "moondream")
    try:
        generator = engine.run_reasoning(req.items, req.equipment, "", use_rag=False)
        return StreamingResponse(generator, media_type="text/plain")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history_data():
    try:
        from database import get_history
        rows = get_history()
        history = []
        for row in rows:
            img_url = f"http://localhost:8000/api/media/{os.path.basename(row[1])}" if row[1] else ""
            history.append({
                "id": row[0],
                "bgImage": img_url,
                "title": row[2],
                "details": row[3],
                "timestamp": row[4]
            })
        return history
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge Bank Endpoints
@app.post("/api/kb/ingest-csv")
async def ingest_csv():
    try:
        if not os.path.exists("upcycle_knowledge_llm.csv"):
            raise HTTPException(status_code=404, detail="upcycle_knowledge_llm.csv not found")
        rm = get_rag_manager()
        res = rm.ingest_csv("upcycle_knowledge_llm.csv")
        return {"status": "success", "message": res}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/kb/sync-history")
async def sync_history():
    try:
        if not os.path.exists("upcycle.db"):
            raise HTTPException(status_code=404, detail="upcycle.db not found")
        rm = get_rag_manager()
        res = rm.ingest_sqlite_history("upcycle.db")
        return {"status": "success", "message": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/kb/upload")
async def upload_document(files: list[UploadFile] = File(...)):
    try:
        rm = get_rag_manager()
        results = []
        for file_obj in files:
            bytes_data = await file_obj.read()
            is_pdf = file_obj.filename.lower().endswith('.pdf')
            res = rm.ingest_document(file_obj.filename, bytes_data, is_pdf)
            results.append(res)
        return {"status": "success", "messages": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/kb/stats")
async def kb_stats():
    try:
        rm = get_rag_manager()
        count = rm.collection.count()
        return {"count": count}
    except Exception:
        return {"count": 0}

# ─── Serve the built React frontend ────────────────────────────────────────────
# Smart catch-all: serve real files directly (fonts, assets, SVGs, etc.)
# Only fall back to index.html for paths that don't exist as files (React routes)
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Check if the requested path is an actual file in dist/
    # Normalise separators so Windows handles URL forward slashes correctly
    safe_path = full_path.replace("/", os.sep)
    candidate = os.path.join(_FRONTEND_DIST, safe_path)
    print(f"DEBUG SPA: full_path={full_path!r}  candidate={candidate!r}  exists={os.path.isfile(candidate)}")
    if os.path.isfile(candidate):
        return FileResponse(candidate)
    # Fall back to index.html for React Router client-side routes
    # No-cache so browsers always refetch the latest index.html
    index = os.path.join(_FRONTEND_DIST, "index.html")
    if os.path.isfile(index):
        return FileResponse(
            index,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Pragma": "no-cache",
            },
        )
    return {"error": "Frontend not built. Run: cd frontend && npm run build"}

