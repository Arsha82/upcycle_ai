import streamlit as st
import io
import os
from PIL import Image
from inference import get_inference_engine
from database import init_db, save_recipe, get_history
from utils import save_image_to_disk
from rag_utils import get_rag_manager

# Init RAG Manager
rag_manager = get_rag_manager()

# Page Config
st.set_page_config(page_title="Upcycle AI", page_icon="♻️", layout="wide")

# Initialize DB
init_db()

# Initialize Session State
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'new'
if 'history_item' not in st.session_state:
    st.session_state.history_item = None

# Sidebar - Settings
st.sidebar.title("⚙️ Settings")
model_provider = st.sidebar.selectbox("Inference Engine", ["Ollama", "AirLLM"])
# Checkpoints found locally: llava, moondream (pulling)
model_name = st.sidebar.text_input("Model Name", value="moondream" if model_provider == "Ollama" else "meta-llama/Meta-Llama-3-70B-Instruct-v1")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📜 History")

# Refresh Button
if st.sidebar.button("🔄 Refresh"):
    st.rerun()

# Knowledge Bank Button
if st.sidebar.button("📚 Knowledge Bank"):
    st.session_state.view_mode = 'kb_manager'
    st.rerun()

# New Scan Button
if st.sidebar.button("➕ New Scan"):
    st.session_state.view_mode = 'new'
    st.session_state.history_item = None
    st.rerun()
    st.session_state.history_item = None
    st.rerun()

# History List
history = get_history()
for item in history:
    # item: (id, image_path, item_name, api_response, timestamp)
    # Use a unique key for each button
    label = f"{item[2]} ({item[4].split()[0]})"
    if st.sidebar.button(label, key=f"hist_{item[0]}", help=f"View {item[2]}"):
        st.session_state.view_mode = 'history'
        st.session_state.history_item = item
        st.rerun()

# Main Content
st.title("♻️ Upcycle AI")

if st.session_state.view_mode == 'history' and st.session_state.history_item:
    # View History Item
    item = st.session_state.history_item
    st.header(f"Saved: {item[2]}")
    st.subheader(f"Date: {item[4]}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if item[1] and os.path.exists(item[1]):
            st.image(item[1], caption="Original Image")
        else:
            st.warning("Image file not found.")
            
    with col2:
        st.markdown(item[3])
        
    if st.button("⬅️ Back to Scanner"):
        st.session_state.view_mode = 'new'
        st.rerun()

elif st.session_state.view_mode == 'new':
    # New Scan Mode
    st.markdown("Scan your waste and turn it into something useful!")
    
    # Input Method Mode
    input_method = st.radio("Choose Input Method", ["Camera", "Upload Image"], horizontal=True)

    image_file = None
    if input_method == "Camera":
        image_file = st.camera_input("Take a photo")
    else:
        image_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

    if image_file:
        # Display Image
        image = Image.open(image_file)
        st.image(image, caption="Uploaded Image", width=400)
        
        # Action Button
        if st.button("✨ Auto-Upcycle This!"):
            with st.spinner(f"Thinking with {model_provider} (Chain Mode)..."):
                try:
                    # Get Engine
                    engine = get_inference_engine(model_provider, model_name)
                    
                    # Run Inference
                    # Convert to bytes for inference
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    # Advanced Prompt Engineering
                    # Extract the context from the knowledge bank first.
                    # Since we don't have the object identified yet (vision runs in inference.py),
                    # we will modify inference.py to handle the RAG lookup OR we can do a quick vision here.
                    # Given the structure, let's pass an indicator to inference engine that we want RAG.
                    
                    base_prompt = """
                    You are an expert DIY and Upcycling Assistant. A user has uploaded an image of a waste item.
                    
                    1. IDENTIFY the item and its primary material (e.g., Plastic Bottle, Cardboard Box, Glass Jar).
                    2. BRAINSTORM 3 distinct, creative, and practical upcycling ideas for this item.
                       - Idea 1: Simple/Quick (5-10 mins)
                       - Idea 2: Moderate/Decorative (30-60 mins)
                       - Idea 3: Advanced/Functional (Project)
                    
                    3. DETAILED INSTRUCTIONS for ONE of the best ideas above:
                       - List materials and tools needed.
                       - Step-by-step assembly instructions.
                       - Safety tips.

                    Format your response with clear Markdown headings (##) and bullet points. Be enthusiastic and encouraging!
                    """
                    
                    response = engine.generate_response(img_bytes, base_prompt, use_rag=True)
                    
                    st.success("Analysis Complete!")
                    st.markdown(response)
                    
                    # Save to Disk and DB
                    # Reset pointer for saving
                    image_file.seek(0)
                    image_path = save_image_to_disk(image_file)
                    
                    # Use a rough naive name or "Scanned Item"
                    item_name = "Scanned Item" 
                    save_recipe(item_name, response, image_path)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

elif st.session_state.view_mode == 'kb_manager':
    # Knowledge Bank Manager UI
    st.header("📚 Manage Knowledge Bank")
    st.markdown("Populate your local Vector Database with UPcycling ideas and project instructions!")
    
    st.subheader("1. Ingest Synthetic Dataset")
    if st.button("Ingest `upcycle_knowledge_llm.csv`"):
        if os.path.exists("upcycle_knowledge_llm.csv"):
            with st.spinner("Ingesting perfectly aligned LLM RAG projects..."):
                res = rag_manager.ingest_csv("upcycle_knowledge_llm.csv")
                st.success(res)
        else:
            st.error("upcycle_knowledge_llm.csv not found. Run generate_kb_llm.py first.")
            
    st.markdown("---")
    st.subheader("2. Sync Past History")
    if st.button("Sync `upcycle.db` History"):
        if os.path.exists("upcycle.db"):
            with st.spinner("Porting past scans to Vector DB..."):
                res = rag_manager.ingest_sqlite_history("upcycle.db")
                st.success(res)
        else:
            st.warning("No upcycle.db found yet. Go scan some items!")

    st.markdown("---")
    st.subheader("3. Upload Custom Documents")
    uploaded_files = st.file_uploader("Upload PDF or TXT files", type=["pdf", "txt"], accept_multiple_files=True)
    
    if st.button("Process & Ingest Files"):
        if uploaded_files:
            for f in uploaded_files:
                with st.spinner(f"Ingesting {f.name}..."):
                    bytes_data = f.getvalue()
                    is_pdf = f.name.lower().endswith('.pdf')
                    res = rag_manager.ingest_document(f.name, bytes_data, is_pdf)
                    st.success(res)
        else:
            st.warning("Please upload at least one file.")
            
    # Show stats
    try:
        count = rag_manager.collection.count()
        st.info(f"**Knowledge Bank Size:** {count} total chunks/documents stored.")
    except Exception:
        pass
