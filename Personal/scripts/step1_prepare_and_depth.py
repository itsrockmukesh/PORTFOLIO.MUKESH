import os
import cv2
import numpy as np
from PIL import Image
import onnxruntime as ort
import matplotlib.pyplot as plt

INPUT_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/inputs"
PROCESSED_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/processed"
ARTIFACT_DIR = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41"
MODEL_PATH = "/Users/mukeshkumar/PORTFOLIO/Personal/models/onnx/model_quantized.onnx"

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# 1. Scale clay images to 1200x896
print("Scaling clay images to 1200x896...")
clay_front = Image.open(os.path.join(INPUT_DIR, "clay-front.png")).convert("RGB")
clay_side = Image.open(os.path.join(INPUT_DIR, "clay-side.png")).convert("RGB")
photo = Image.open(os.path.join(INPUT_DIR, "photo.png")).convert("RGB")

clay_front_scaled = clay_front.resize((1200, 896), Image.Resampling.LANCZOS)
clay_side_scaled = clay_side.resize((1200, 896), Image.Resampling.LANCZOS)

clay_front_scaled.save(os.path.join(PROCESSED_DIR, "clay_front_1200x896.png"))
clay_side_scaled.save(os.path.join(PROCESSED_DIR, "clay_side_1200x896.png"))
photo.save(os.path.join(PROCESSED_DIR, "photo_input.png"))

# 2. Setup Depth Anything V2 session
print("Loading Depth Anything V2 ONNX session...")
session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])

mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)

def run_depth(pil_img):
    orig_w, orig_h = pil_img.size
    # Round to nearest multiple of 14
    target_h = int(round(orig_h / 14.0) * 14)
    target_w = int(round(orig_w / 14.0) * 14)
    
    resized = pil_img.resize((target_w, target_h), Image.Resampling.BILINEAR)
    img_np = np.array(resized).astype(np.float32) / 255.0
    img_np = np.transpose(img_np, (2, 0, 1))[np.newaxis, ...] # (1, 3, H, W)
    img_np = (img_np - mean) / std
    
    depth_out = session.run(None, {'pixel_values': img_np})[0]
    depth_map = depth_out[0] # (H, W)
    
    # Resize back to original dimensions
    depth_resized = cv2.resize(depth_map, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
    
    # Normalize 0..1
    d_min, d_max = depth_resized.min(), depth_resized.max()
    depth_norm = (depth_resized - d_min) / (d_max - d_min + 1e-8)
    return depth_norm, depth_resized

print("Running depth inference on clay-front...")
front_depth_norm, front_depth_raw = run_depth(clay_front_scaled)
np.save(os.path.join(PROCESSED_DIR, "clay_front_depth.npy"), front_depth_norm)

print("Running depth inference on clay-side...")
side_depth_norm, side_depth_raw = run_depth(clay_side_scaled)
np.save(os.path.join(PROCESSED_DIR, "clay_side_depth.npy"), side_depth_norm)

print("Running depth inference on photo...")
photo_depth_norm, photo_depth_raw = run_depth(photo)
np.save(os.path.join(PROCESSED_DIR, "photo_depth.npy"), photo_depth_norm)

# Generate composite screenshot
fig, axes = plt.subplots(3, 2, figsize=(14, 15))
plt.subplots_adjust(wspace=0.05, hspace=0.15)

axes[0, 0].imshow(clay_front_scaled)
axes[0, 0].set_title("Clay Front (1200x896)", fontsize=14, fontweight='bold')
axes[0, 0].axis('off')

axes[0, 1].imshow(front_depth_norm, cmap='inferno')
axes[0, 1].set_title("Depth Anything V2: Clay Front", fontsize=14, fontweight='bold')
axes[0, 1].axis('off')

axes[1, 0].imshow(clay_side_scaled)
axes[1, 0].set_title("Clay Side (1200x896)", fontsize=14, fontweight='bold')
axes[1, 0].axis('off')

axes[1, 1].imshow(side_depth_norm, cmap='inferno')
axes[1, 1].set_title("Depth Anything V2: Clay Side", fontsize=14, fontweight='bold')
axes[1, 1].axis('off')

axes[2, 0].imshow(photo)
axes[2, 0].set_title("Photo Input (1024x576)", fontsize=14, fontweight='bold')
axes[2, 0].axis('off')

axes[2, 1].imshow(photo_depth_norm, cmap='inferno')
axes[2, 1].set_title("Depth Anything V2: Photo", fontsize=14, fontweight='bold')
axes[2, 1].axis('off')

screenshot_path = os.path.join(ARTIFACT_DIR, "step1_depth_maps.png")
plt.tight_layout()
plt.savefig(screenshot_path, dpi=150, bbox_inches='tight')
plt.close()
print("Saved screenshot to:", screenshot_path)
