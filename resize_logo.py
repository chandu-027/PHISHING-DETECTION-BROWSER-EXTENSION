import os
import subprocess
import sys

# Ensure Pillow is installed
try:
    from PIL import Image
except ImportError:
    print("Pillow not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image

def resize_image():
    # Source image path
    src_path = r"C:\Users\91994\.gemini\antigravity\brain\94df044c-1195-43a7-a524-3ad7c57f94a7\phishguard_logo_1786199728955.jpg"
    
    # Destination directory
    dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extension")
    os.makedirs(dest_dir, exist_ok=True)
    
    if not os.path.exists(src_path):
        print(f"Error: Source image not found at {src_path}")
        return
        
    print(f"Loading logo from {src_path}...")
    img = Image.open(src_path)
    
    sizes = [16, 48, 128]
    for size in sizes:
        dest_path = os.path.join(dest_dir, f"icon{size}.png")
        print(f"Resizing to {size}x{size} and saving to {dest_path}...")
        resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
        resized_img.save(dest_path, "PNG")
        
    print("Resizing complete!")

if __name__ == "__main__":
    resize_image()
