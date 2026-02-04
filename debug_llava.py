import ollama
import base64
import os
from PIL import Image
import io

# Create a simple test image
img = Image.new('RGB', (100, 100), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_bytes = img_byte_arr.getvalue()
import tempfile
with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
    f.write(img_bytes)
    img_path = f.name

print(f"Testing with image path: {img_path}")

try:
    print("\n--- Test 1: ollama.generate (path) ---")
    res1 = ollama.generate(model='llava', prompt='What color is this image?', images=[img_path])
    print(f"Result 1: {res1['response']}")
except Exception as e:
    print(f"Test 1 Error: {e}")

try:
    print("\n--- Test 2: ollama.chat (path) ---")
    res2 = ollama.chat(model='llava', messages=[{'role': 'user', 'content': 'What color is this image?', 'images': [img_path]}])
    print(f"Result 2: {res2['message']['content']}")
except Exception as e:
    print(f"Test 2 Error: {e}")

try:
    print("\n--- Test 3: ollama.generate (options: temp=0) ---")
    res3 = ollama.generate(model='llava', prompt='What color is this image?', images=[img_path], options={'temperature': 0})
    print(f"Result 3: {res3['response']}")
except Exception as e:
    print(f"Test 3 Error: {e}")

# Cleanup
if os.path.exists(img_path):
    os.remove(img_path)
