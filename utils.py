import os
import uuid

IMAGES_DIR = "images"

def save_image_to_disk(image_file):
    """Save uploaded/captured image to disk and return the path."""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    
    # Generate unique filename
    file_ext = "jpg" # Default to jpg for simplicity
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(IMAGES_DIR, filename)
    
    # Save
    with open(file_path, "wb") as f:
        f.write(image_file.getvalue())
        
    return file_path

def resize_image_for_model(image, max_size=(1024, 1024)):
    """Resize image to avoid sending too large payloads."""
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image
