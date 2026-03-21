import streamlit as st
import io
import os
from PIL import Image
from inference import get_inference_engine
from database import init_db, save_recipe, get_history, delete_recipe, rename_recipe
from utils import save_image_to_disk
from rag_utils import get_rag_manager

# Init RAG Manager
rag_manager = get_rag_manager()

# Page Config
st.set_page_config(page_title="Upcycle AI", page_icon="♻️", layout="wide")

st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #F8F7F3;
}

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #1a2035 !important;
    border-right: none;
}

/* Safe sidebar text colors avoiding wildcard overrides */
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #f8f9fa !important;
}

/* Sidebar Input fields/SelectBoxes */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="popover"] > div,
section[data-testid="stSidebar"] input {
    background-color: #272f4d !important;
    border: 1px solid #3b4255 !important;
    color: white !important;
}

/* Global Sidebar Buttons (including internal column buttons) */
section[data-testid="stSidebar"] button {
    background-color: transparent !important;
    border: 1px solid #4a5568 !important;
    color: #e2e8f0 !important;
    border-radius: 6px;
    padding: 0.25rem 0.75rem;
    transition: all 0.3s;
}
section[data-testid="stSidebar"] button:hover {
    border-color: #cca677 !important;
    color: #cca677 !important;
}

/* Remove main padding for custom header */
.block-container {
    padding-top: 2.5rem !important;
}

/* Typography Customizations */
.main-header {
    text-align: center;
    font-family: 'Georgia', serif;
    color: #1a203f;
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}
.sub-header {
    text-align: center;
    font-family: 'Courier New', monospace;
    font-style: italic;
    color: #4a5568;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

.accent-line {
    width: 60px;
    height: 2px;
    background-color: #cca677;
    margin: 0 auto 3rem auto;
}

.feature-card {
    background-color: white;
    padding: 2.5rem 1.5rem;
    border-radius: 4px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    text-align: center;
    height: 100%;
    border-top: 3px solid transparent;
    transition: transform 0.3s, border-top 0.3s;
}
.feature-card:hover {
    transform: translateY(-5px);
    border-top: 3px solid #cca677;
}
.feature-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
}
.feature-title {
    font-weight: 700;
    letter-spacing: 1px;
    font-size: 0.85rem;
    margin-bottom: 1rem;
    color: #1a203f !important;
}
.feature-text {
    color: #718096 !important;
    font-size: 0.85rem;
    line-height: 1.6;
}

.sub-footer {
    text-align: center;
    font-size: 0.75rem;
    letter-spacing: 2px;
    color: #a0aec0;
    margin: 4rem 0 3rem 0;
    font-weight: 600;
}

.section-label {
    color: #cca677;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 1rem;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# Initialize DB
init_db()

# Initialize Session State
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'new'
if 'history_item' not in st.session_state:
    st.session_state.history_item = None
if 'rename_item_id' not in st.session_state:
    st.session_state.rename_item_id = None
if 'global_chat' not in st.session_state:
    st.session_state.global_chat = [{"role": "assistant", "content": "Hi! I'm your Upcycle AI assistant. How can I help you today?"}]
if 'last_scan_result' not in st.session_state:
    st.session_state.last_scan_result = None

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
    
    if st.session_state.get('rename_item_id') == item[0]:
        new_name = st.sidebar.text_input("New name", value=item[2], key=f"ren_txt_{item[0]}")
        col_s1, col_s2 = st.sidebar.columns(2)
        if col_s1.button("Save", key=f"save_ren_{item[0]}"):
            if new_name and new_name.strip():
                rename_recipe(item[0], new_name.strip())
                if st.session_state.history_item and st.session_state.history_item[0] == item[0]:
                    old_item = st.session_state.history_item
                    st.session_state.history_item = (old_item[0], old_item[1], new_name.strip(), old_item[3], old_item[4])
            st.session_state.rename_item_id = None
            st.rerun()
        if col_s2.button("Cancel", key=f"cnc_ren_{item[0]}"):
            st.session_state.rename_item_id = None
            st.rerun()
    else:
        col1, col2, col3 = st.sidebar.columns([4, 1, 1])
        if col1.button(label, key=f"hist_{item[0]}", help=f"View {item[2]}"):
            st.session_state.view_mode = 'history'
            st.session_state.history_item = item
            st.rerun()
        if col2.button("✏️", key=f"ren_{item[0]}", help="Rename this item"):
            st.session_state.rename_item_id = item[0]
            st.rerun()
        if col3.button("❌", key=f"del_{item[0]}", help="Delete this item"):
            delete_recipe(item[0])
            if st.session_state.history_item and st.session_state.history_item[0] == item[0]:
                st.session_state.view_mode = 'new'
                st.session_state.history_item = None
            st.rerun()

# Main Content

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
    
    st.markdown("<div class='main-header'>Upcycle AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Elevating waste into sustainable creations.</div>", unsafe_allow_html=True)
    st.markdown("<div class='accent-line'></div>", unsafe_allow_html=True)
    
    feat1, feat2, feat3 = st.columns(3)
    with feat1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">FULLY OFFLINE</div>
            <div class="feature-text">Runs entirely on your local machine with no external calls.</div>
        </div>
        """, unsafe_allow_html=True)
    with feat2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">RAG-GROUNDED</div>
            <div class="feature-text">Context-aware responses backed by an internal knowledge base.</div>
        </div>
        """, unsafe_allow_html=True)
    with feat3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <div class="feature-title">ZERO COST</div>
            <div class="feature-text">Open-source models without ongoing subscription or API fees.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='sub-footer'>VISION SEES · RAG KNOWS · LLM REASONS · SQLITE REMEMBERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>NEW SCAN</div>", unsafe_allow_html=True)
    
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
        st.markdown("### Brainstorming & Searching Knowledge Base...")
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
                response_gen = engine.run_reasoning(
                    selected_items=st.session_state.selected_items,
                    equipment=st.session_state.equipment,
                    prompt=base_prompt,
                    use_rag=True
                )
            else:
                final_prompt_adj = f"The user wants to upcycle: {', '.join(st.session_state.selected_items)}. They have tools: {st.session_state.equipment.strip() if st.session_state.equipment else 'basic'}.\n\n" + base_prompt
                response_gen = engine.generate_response(st.session_state.image_bytes, final_prompt_adj, use_rag=True)
            
            # Consume stream or display string
            if isinstance(response_gen, str):
                st.markdown(response_gen)
                response = response_gen
            else:
                response = st.write_stream(response_gen)
            
            # Save to DB
            item_name = str(", ".join(st.session_state.selected_items))[:50]
            inserted_id = save_recipe(item_name, response, st.session_state.image_path)
            
            st.session_state.final_response = response
            st.session_state.last_scan_result = response
            
            import datetime
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.history_item = (inserted_id, st.session_state.image_path, item_name, response, now_str)
            st.session_state.view_mode = 'history'
            st.session_state.scan_step = 1
            st.rerun()
            
        except Exception as e:
            st.error(f"Generation error: {e}")
            if st.button("⬅️ Back"):
                st.session_state.scan_step = 2
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

# --- Floating Chatbot ---
st.markdown(
    """
    <style>
    /* Position the popover container */
    div[data-testid="stPopover"], div:has(> div[data-testid="stPopover"]) {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 999999 !important;
    }
    
    /* Make the button look like a circle emoji button */
    div[data-testid="stPopover"] button {
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        background-color: #4CAF50 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
        font-size: 24px !important;
        transition: transform 0.2s;
    }
    div[data-testid="stPopover"] button:hover {
        transform: scale(1.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.popover("🤖"):
    st.markdown("### 🤖 Assistant")
    chat_container = st.container(height=350)
    for msg in st.session_state.global_chat:
        with chat_container.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about history, projects..."):
        st.session_state.global_chat.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        with chat_container.chat_message("assistant"):
            try:
                engine = get_inference_engine(model_provider, model_name)
                
                app_context = ""
                if st.session_state.view_mode == 'history' and st.session_state.history_item:
                    app_context = f"APP CONTEXT: The user is currently viewing a past upcycle scan of '{st.session_state.history_item[2]}'. The generated instructions were:\n{st.session_state.history_item[3]}\n\n"
                elif st.session_state.view_mode == 'new' and st.session_state.last_scan_result:
                    app_context = f"APP CONTEXT: The user recently scanned an item and generated the following instructions:\n{st.session_state.last_scan_result}\n\n"

                chat_context = "CONVERSATION HISTORY:\n"
                for msg in st.session_state.global_chat[1:]:
                    chat_context += f"{msg['role'].capitalize()}: {msg['content']}\n\n"
                
                chat_prompt = f"You are the Upcycling AI Assistant.\n{app_context}\n{chat_context}\nAnswer the user's latest question directly and concisely."
                
                reply_gen = engine.generate_response(b"", chat_prompt, use_rag=False, chat_only=True)
                
                if isinstance(reply_gen, str):
                    reply = reply_gen
                    st.markdown(reply)
                else:
                    reply = st.write_stream(reply_gen)
                    
                st.session_state.global_chat.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error communicating with AI: {e}")
