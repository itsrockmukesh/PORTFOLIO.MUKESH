import os
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
import matplotlib.pyplot as plt

PROCESSED_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/processed"
ARTIFACT_DIR = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41"

def process_clay_cutout(img_path, name):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Grey below 226
    raw_mask = (gray < 226).astype(np.uint8)
    
    # 2. Ignore floor shadow: the bust base is flat horizontally at row 855.
    # Pixels below row 855 are the floor shadow table surface.
    raw_mask[855:, :] = 0
    
    # 3. Keep largest shape (connected component)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(raw_mask)
    if num_labels > 1:
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        mask = (labels == largest_label).astype(np.uint8)
    else:
        mask = raw_mask
        
    # 4. Fill holes
    mask_filled = ndimage.binary_fill_holes(mask).astype(np.uint8)
    
    # Create RGBA cutout
    cutout = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)
    cutout[:, :, :3] = img
    cutout[:, :, 3] = mask_filled * 255
    
    out_mask_path = os.path.join(PROCESSED_DIR, f"{name}_mask.png")
    out_cutout_path = os.path.join(PROCESSED_DIR, f"{name}_cutout.png")
    cv2.imwrite(out_mask_path, mask_filled * 255)
    cv2.imwrite(out_cutout_path, cutout)
    
    return img, mask_filled, cutout

print("Processing clay-front cutout...")
front_img, front_mask, front_cutout = process_clay_cutout(
    os.path.join(PROCESSED_DIR, "clay_front_1200x896.png"), "clay_front"
)

print("Processing clay-side cutout...")
side_img, side_mask, side_cutout = process_clay_cutout(
    os.path.join(PROCESSED_DIR, "clay_side_1200x896.png"), "clay_side"
)

print("Processing photo cutout with soft alpha and collar gap closure...")
photo_bgr = cv2.imread(os.path.join(PROCESSED_DIR, "photo_input.png"))
photo_rgb = cv2.cvtColor(photo_bgr, cv2.COLOR_BGR2RGB)
h, w, _ = photo_rgb.shape

# Threshold black background (RGB max > 10)
val_max = photo_rgb.max(axis=2)
raw_fg = (val_max > 12).astype(np.uint8)

# Keep largest connected component
num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(raw_fg)
largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
fg_main = (labels == largest_label).astype(np.uint8)

# Fill interior holes (e.g. glasses reflections, dark shirt buttons)
fg_filled = ndimage.binary_fill_holes(fg_main).astype(np.uint8)

# Close background gaps between neck and collar
# In the neck/collar region (Y: 340 to 480, X: 470 to 560), fill the gap
collar_gap_region = np.zeros_like(fg_filled)
# Find convex hull or morphological close specifically in neck/collar region
neck_y1, neck_y2 = 330, 480
neck_x1, neck_x2 = 470, 560
neck_patch = fg_filled[neck_y1:neck_y2, neck_x1:neck_x2]
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
closed_patch = cv2.morphologyEx(neck_patch, cv2.MORPH_CLOSE, kernel)
# Also fill any holes in the patch
closed_patch = ndimage.binary_fill_holes(closed_patch).astype(np.uint8)
fg_filled[neck_y1:neck_y2, neck_x1:neck_x2] = closed_patch

# Now build soft alpha edge that keeps flyaway hair
# 1. Erode solid core by 4 pixels to get guaranteed solid foreground
solid_core = cv2.erode(fg_filled, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=1)

# 2. Dilate to encompass all fine hair strands
outer_boundary = cv2.dilate(fg_filled, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)), iterations=1)

# Transition zone
transition_zone = (outer_boundary > 0) & (solid_core == 0)

# In the transition zone, the background is black (0,0,0).
# Hair intensity is proportional to hair strand coverage.
# Compute normalized brightness:
luminance = 0.299 * photo_rgb[:,:,0] + 0.587 * photo_rgb[:,:,1] + 0.114 * photo_rgb[:,:,2]
max_rgb = photo_rgb.max(axis=2).astype(np.float32)

# Estimate local hair brightness in hair region (~50-100)
# Map luminance smoothly:
alpha = np.zeros((h, w), dtype=np.float32)
alpha[solid_core > 0] = 1.0

# Soft alpha in transition zone:
hair_alpha = np.clip(max_rgb / 65.0, 0.0, 1.0)
# Combine distance transform weighting with luminance
dist_inside = cv2.distanceTransform(fg_filled, cv2.DIST_L2, 5)
dist_outside = cv2.distanceTransform(1 - fg_filled, cv2.DIST_L2, 5)

# Smooth sigmoid transition modulated by hair luminance
dist_signed = dist_inside - dist_outside
edge_fade = 1.0 / (1.0 + np.exp(-dist_signed / 1.5))
combined_alpha = np.maximum(edge_fade, hair_alpha)
alpha[transition_zone] = np.clip(combined_alpha[transition_zone], 0.0, 1.0)
alpha[outer_boundary == 0] = 0.0

# Ensure collar region remains 100% solid
alpha[neck_y1:neck_y2, neck_x1:neck_x2] = np.maximum(alpha[neck_y1:neck_y2, neck_x1:neck_x2], closed_patch.astype(np.float32))

# Save photo cutout
photo_rgba = np.zeros((h, w, 4), dtype=np.uint8)
photo_rgba[:, :, :3] = photo_rgb
photo_rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

cv2.imwrite(os.path.join(PROCESSED_DIR, "photo_cutout.png"), cv2.cvtColor(photo_rgba, cv2.COLOR_RGBA2BGRA))
cv2.imwrite(os.path.join(PROCESSED_DIR, "photo_alpha.png"), (alpha * 255).astype(np.uint8))
np.save(os.path.join(PROCESSED_DIR, "photo_alpha.npy"), alpha)

# Save composite visualization
fig, axes = plt.subplots(3, 3, figsize=(18, 16))
plt.subplots_adjust(wspace=0.08, hspace=0.15)

# Clay front
axes[0, 0].imshow(cv2.cvtColor(front_img, cv2.COLOR_BGR2RGB))
axes[0, 0].set_title("Clay Front (Input)", fontsize=13, fontweight='bold')
axes[0, 0].axis('off')

axes[0, 1].imshow(front_mask, cmap='gray')
axes[0, 1].set_title("Clay Front Mask (Grey < 226, Holes Filled)", fontsize=13, fontweight='bold')
axes[0, 1].axis('off')

# Checkerboard preview for cutout
def apply_checkerboard(rgba):
    ch, cw, _ = rgba.shape
    check_size = 20
    y, x = np.ogrid[:ch, :cw]
    check = ((x // check_size) + (y // check_size)) % 2 == 0
    bg = np.where(check[:, :, None], 220, 180).astype(np.uint8)
    bg = np.repeat(bg, 3, axis=2)
    a = rgba[:, :, 3:4] / 255.0
    comp = (rgba[:, :, :3] * a + bg * (1.0 - a)).astype(np.uint8)
    return comp

axes[0, 2].imshow(apply_checkerboard(front_cutout))
axes[0, 2].set_title("Clay Front Cutout (Floor Shadow Excluded)", fontsize=13, fontweight='bold')
axes[0, 2].axis('off')

# Clay side
axes[1, 0].imshow(cv2.cvtColor(side_img, cv2.COLOR_BGR2RGB))
axes[1, 0].set_title("Clay Side (Input)", fontsize=13, fontweight='bold')
axes[1, 0].axis('off')

axes[1, 1].imshow(side_mask, cmap='gray')
axes[1, 1].set_title("Clay Side Mask (Grey < 226, Holes Filled)", fontsize=13, fontweight='bold')
axes[1, 1].axis('off')

axes[1, 2].imshow(apply_checkerboard(side_cutout))
axes[1, 2].set_title("Clay Side Cutout", fontsize=13, fontweight='bold')
axes[1, 2].axis('off')

# Photo
axes[2, 0].imshow(photo_rgb)
axes[2, 0].set_title("Photo Input (1024x576)", fontsize=13, fontweight='bold')
axes[2, 0].axis('off')

axes[2, 1].imshow(alpha, cmap='gray')
axes[2, 1].set_title("Soft Alpha Mask (Neck/Collar Gaps Closed)", fontsize=13, fontweight='bold')
axes[2, 1].axis('off')

axes[2, 2].imshow(apply_checkerboard(photo_rgba))
axes[2, 2].set_title("Photo Cutout (Flyaway Hair Preserved)", fontsize=13, fontweight='bold')
axes[2, 2].axis('off')

screenshot_path = os.path.join(ARTIFACT_DIR, "step2_cutouts.png")
plt.tight_layout()
plt.savefig(screenshot_path, dpi=150, bbox_inches='tight')
plt.close()
print("Saved Step 2 screenshot to:", screenshot_path)
