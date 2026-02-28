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
    
    # Init workflow state if needed
    if 'scan_step' not in st.session_state:
        st.session_state.scan_step = 1 # 1: Upload, 2: Refine, 3: Result
    if 'raw_vision_items' not in st.session_state:
        st.session_state.raw_vision_items = []
    if 'image_bytes' not in st.session_state:
        st.session_state.image_bytes = None
    if 'image_path' not in st.session_state:
        st.session_state.image_path = None
        
    # --- STEP 1: UPLOAD & VISION ---
    if st.session_state.scan_step == 1:
        input_method = st.radio("Choose Input Method", ["Camera", "Upload Image"], horizontal=True)

        image_file = None
        if input_method == "Camera":
            image_file = st.camera_input("Take a photo")
        else:
            image_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

        if image_file:
            image = Image.open(image_file)
            st.image(image, caption="Uploaded Image", width=400)
            
            if st.button("🔍 Analyze Image"):
                with st.spinner(f"Identifying objects with {model_provider} vision..."):
                    try:
                        engine = get_inference_engine(model_provider, model_name)
                        
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                        img_bytes = img_byte_arr.getvalue()
                        
                        # Save the image early so we have the path for later DB insertion
                        image_file.seek(0)
                        image_path = save_image_to_disk(image_file)
                        
                        st.session_state.image_bytes = img_bytes
                        st.session_state.image_path = image_path
                        
                        # If AirLLM, mock the vision step as it's text-only right now in this impl
                        if model_provider == "AirLLM":
                            # Hack fallback
                            raw_csv_response = "unknown object"
                        else:
                            raw_csv_response = engine.run_vision(img_bytes)
                        
                        # Process the comma-separated string into a list
                        items = [item.strip() for item in raw_csv_response.split(',') if item.strip()]
                        
                        st.session_state.raw_vision_items = items
                        st.session_state.scan_step = 2
                        st.rerun()
                    except Exception as e:
                        st.error(f"Vision analysis failed: {e}")

    # --- STEP 2: REFINE & SELECT ---
    elif st.session_state.scan_step == 2:
        st.info("Success! We analyzed the image. Tell us exactly what to focus on.")
        
        # Display image again for context
        if st.session_state.image_path and os.path.exists(st.session_state.image_path):
            st.image(Image.open(st.session_state.image_path), width=300)
            
        st.subheader("1. Select items to upcycle")
        st.write("Uncheck background objects or things you don't want to use.")
        
        if not st.session_state.raw_vision_items:
            st.warning("No specific objects identified. Please type what you see below.")
            st.session_state.raw_vision_items = ["Unknown object"]
            
        selected_items = []
        for i, item in enumerate(st.session_state.raw_vision_items):
            # Default to checked
            if st.checkbox(item, value=True, key=f"chk_{i}"):
                selected_items.append(item)
                
        # Optional manual override
        manual_item = st.text_input("Missed something? Type it here (optional):")
        if manual_item:
            selected_items.append(manual_item.strip())
            
        st.markdown("---")
        st.subheader("2. What equipment do you have?")
        equipment = st.text_input("Tools available (e.g., 'hot glue gun, scissors, paint')", placeholder="Leave blank for basic household items")
        
        st.markdown("---")
        col1, col2 = st.columns([1,4])
        with col1:
            if st.button("⬅️ Start Over"):
                st.session_state.scan_step = 1
                st.rerun()
        with col2:
            if st.button("✨ Generate Project Ideas"):
                if not selected_items:
                    st.error("Please select at least one item to upcycle.")
                else:
                    st.session_state.selected_items = selected_items
                    st.session_state.equipment = equipment
                    st.session_state.scan_step = 3
                    st.rerun()

    # --- STEP 3: GENERATION (REASONING) ---
    elif st.session_state.scan_step == 3:
        with st.spinner(f"Brainstorming and checking Knowledge Base with {model_provider} text reasoning..."):
            try:
                engine = get_inference_engine(model_provider, model_name)
                
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
                
                # Use the interactive reasoning flow
                if hasattr(engine, 'run_reasoning'):
                    response = engine.run_reasoning(
                        selected_items=st.session_state.selected_items,
                        equipment=st.session_state.equipment,
                        prompt=base_prompt,
                        use_rag=True
                    )
                else:
                    # Fallback for AirLLM or other engines without split logic
                    final_prompt_adj = f"The user wants to upcycle: {', '.join(st.session_state.selected_items)}. They have tools: {st.session_state.equipment.strip() if st.session_state.equipment else 'basic'}.\n\n" + base_prompt
                    response = engine.generate_response(st.session_state.image_bytes, final_prompt_adj, use_rag=True)
                
                # Save to DB
                item_name = ", ".join(st.session_state.selected_items)[:50] # Short title
                save_recipe(item_name, response, st.session_state.image_path)
                
                st.session_state.final_response = response
                st.session_state.scan_step = 4
                st.rerun()
                
            except Exception as e:
                st.error(f"Generation error: {e}")
                if st.button("⬅️ Back"):
                    st.session_state.scan_step = 2
                    st.rerun()

    # --- STEP 4: RESULT DISPLAY ---
    elif st.session_state.scan_step == 4:
        st.success("Analysis Complete!")
        
        # Display the result
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.session_state.image_path and os.path.exists(st.session_state.image_path):
                st.image(Image.open(st.session_state.image_path), caption="Original Image")
        with col2:
            st.markdown(st.session_state.final_response)
            
        if st.button("⬅️ New Scan"):
            st.session_state.scan_step = 1
            st.rerun()

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
