import ollama
import os
from PIL import Image
import io
import tempfile

# Create a simple test image
img = Image.new('RGB', (100, 100), color = 'blue')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_bytes = img_byte_arr.getvalue()

with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
    f.write(img_bytes)
    img_path = f.name

print(f"Testing Moondream with image path: {img_path}")

try:
    print("\n--- Test 1: Simple Context ---")
    res1 = ollama.generate(model='moondream', prompt='Describe this image.', images=[img_path])
    print(f"Result 1: {res1['response']}")
except Exception as e:
    print(f"Test 1 Error: {e}")

try:
    print("\n--- Test 2: Complex Prompt ---")
    complex_prompt = """
    You are an expert DIY assistant.
    1. Identify the item.
    2. Suggest 3 upcycling ideas.
    """
    res2 = ollama.generate(model='moondream', prompt=complex_prompt, images=[img_path])
    print(f"Result 2: {res2['response']}")
except Exception as e:
    print(f"Test 2 Error: {e}")

# Cleanup
if os.path.exists(img_path):
    os.remove(img_path)
