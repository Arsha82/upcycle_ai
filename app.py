import streamlit as st
import io
import os
from PIL import Image
from inference import get_inference_engine
from database import init_db, save_recipe, get_history
from utils import save_image_to_disk

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

# New Scan Button
if st.sidebar.button("➕ New Scan"):
    st.session_state.view_mode = 'new'
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

else:
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
                    
                    response = engine.generate_response(img_bytes, base_prompt)
                    
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
