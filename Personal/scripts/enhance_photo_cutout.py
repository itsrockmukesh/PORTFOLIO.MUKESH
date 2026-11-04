import os
import cv2
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

ROOT_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal"
PROCESSED_DIR = os.path.join(ROOT_DIR, "processed")
ARTIFACT_DIR = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41"

print("Loading original photo...")
photo = cv2.imread(os.path.join(ROOT_DIR, "inputs/photo.png"))
h, w, _ = photo.shape
gray = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)

# ==============================================================================
# 1. DENSE HAIR & CLEAN MASK GENERATION
# ==============================================================================
print("1. Generating dense, solid hair alpha mask...")
# Studio background is pure black (< 4)
fg_mask = (photo.max(axis=2) >= 5).astype(np.uint8)

# Close neck gaps between neck and collar
neck_y1, neck_y2 = 320, 480
neck_x1, neck_x2 = 420, 610
neck_patch = fg_mask[neck_y1:neck_y2, neck_x1:neck_x2]
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
closed_neck = cv2.morphologyEx(neck_patch, cv2.MORPH_CLOSE, kernel)
fg_mask[neck_y1:neck_y2, neck_x1:neck_x2] = closed_neck

# Fill all interior holes so body, face and hair core are 100% solid
fg_filled = ndimage.binary_fill_holes(fg_mask).astype(np.uint8)

# Hair region mask:
hair_zone = np.zeros((h, w), dtype=bool)
hair_zone[:175, :] = True
hair_zone[140:240, :448] = True
hair_zone[140:240, 576:] = True

# Volumize hair: slightly dilate hair perimeter by 2 pixels to recover fine hair edge volume
hair_core = (fg_filled > 0) & hair_zone
hair_dilated = cv2.dilate(hair_core.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

# Combine body core with dense hair core
dense_fg = fg_filled.copy()
dense_fg[hair_dilated > 0] = 1

# Outer boundary for soft antialiased edges
outer_boundary = cv2.dilate(dense_fg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
transition = (outer_boundary > 0) & (dense_fg == 0)

# Build high-precision alpha channel:
# Solid 1.0 inside dense_fg
alpha = dense_fg.astype(np.float32)

# High-fidelity antialiasing at the boundary
dist_in = cv2.distanceTransform(dense_fg, cv2.DIST_L2, 5)
dist_out = cv2.distanceTransform(1 - dense_fg, cv2.DIST_L2, 5)
dist_signed = dist_in - dist_out
edge_alpha = 1.0 / (1.0 + np.exp(-dist_signed / 1.1))

# Modulate edge by subtle luminance of hair flyaways
flyaway_lum = np.clip(photo.max(axis=2).astype(np.float32) / 28.0, 0.0, 1.0)
edge_alpha = np.maximum(edge_alpha, flyaway_lum * 0.95)

alpha[transition] = np.clip(edge_alpha[transition], 0.0, 1.0)
alpha[outer_boundary == 0] = 0.0

# Bottom feathering: smoothly fade the bottom 30 rows of polo shirt into the dark background
y_coords = np.arange(h)[:, None]
bottom_fade = np.clip(1.0 - (y_coords - 542) / 34.0, 0.0, 1.0)
alpha *= bottom_fade

# ==============================================================================
# 2. FACIAL BEAUTIFICATION & SILKY SKIN SMOOTHING
# ==============================================================================
print("2. Performing high-end facial skin smoothing...")
# YCrCb skin detection tuned for Mukesh's natural skin tone
ycrcb = cv2.cvtColor(photo, cv2.COLOR_BGR2YCrCb)
Y, Cr, Cb = ycrcb[:,:,0], ycrcb[:,:,1], ycrcb[:,:,2]

skin_color = (Cr >= 132) & (Cr <= 172) & (Cb >= 98) & (Cb <= 138) & (Y >= 65)

face_y1, face_y2 = 140, 345
face_x1, face_x2 = 415, 610
face_zone = np.zeros((h, w), dtype=bool)
face_zone[face_y1:face_y2, face_x1:face_x2] = True

skin_mask = skin_color & face_zone

# Feature protection: preserve eyes, glasses frames, catchlights, beard, mustache, and lips
# 1. High-frequency edges (metallic glasses frames, eyelids, iris rims)
sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
edge_mag = np.sqrt(sobel_x**2 + sobel_y**2)
is_edge = (edge_mag > 28) & face_zone

# 2. Glasses & eyes zone:
glasses_eyes_zone = np.zeros((h, w), dtype=bool)
glasses_eyes_zone[175:240, 435:585] = True
protect_glasses_eyes = glasses_eyes_zone & ((edge_mag > 16) | (Y < 85) | (Y > 235))

# 3. Facial hair zone (mustache, stubble, beard, chin):
mustache_zone = np.zeros((h, w), dtype=bool)
mustache_zone[240:270, 465:555] = True
beard_zone = np.zeros((h, w), dtype=bool)
beard_zone[265:345, 430:590] = True
protect_facial_hair = (mustache_zone | beard_zone) & ((Y < 100) | (edge_mag > 18))

# 4. Eyebrows:
eyebrow_zone = np.zeros((h, w), dtype=bool)
eyebrow_zone[145:180, 435:585] = True
protect_eyebrows = eyebrow_zone & (Y < 95)

# Clean skin mask (pure skin on forehead, cheeks, nose bridge, temples)
skin_smooth_mask = skin_mask & ~is_edge & ~protect_glasses_eyes & ~protect_facial_hair & ~protect_eyebrows
skin_smooth_mask_f = cv2.GaussianBlur(skin_smooth_mask.astype(np.float32), (9, 9), 3.0)

# Edge-preserving surface blur / bilateral filter
smooth_p1 = cv2.bilateralFilter(photo, d=11, sigmaColor=45, sigmaSpace=45)
smooth_p2 = cv2.bilateralFilter(smooth_p1, d=7, sigmaColor=32, sigmaSpace=32)

# Blend smoothed skin into photo
photo_beautified = photo.copy().astype(np.float32)
for c in range(3):
    photo_beautified[:,:,c] = (
        (1.0 - skin_smooth_mask_f) * photo[:,:,c] +
        skin_smooth_mask_f * smooth_p2[:,:,c]
    )

# ==============================================================================
# 3. DENSE, RICH HAIR ENHANCEMENT
# ==============================================================================
print("3. Enriching hair density, dark espresso depth, and wavy curl definition...")
# In the hair region, deepen hair blacks, reduce washed-out glare, and boost strand contrast
hair_enh_mask = (hair_zone & (fg_filled > 0) & (Y < 135)).astype(np.float32)
hair_enh_mask = cv2.GaussianBlur(hair_enh_mask, (15, 15), 5.0)

# High-frequency strand unsharp mask
hair_strands = cv2.addWeighted(photo_beautified, 1.25, cv2.GaussianBlur(photo_beautified, (0, 0), 2.0), -0.25, 0)
for c in range(3):
    # Deepen dark tones for thick, dense hair appearance
    deepened = np.clip(hair_strands[:,:,c] * 0.93, 0, 255)
    photo_beautified[:,:,c] = (1.0 - hair_enh_mask) * photo_beautified[:,:,c] + hair_enh_mask * deepened

# ==============================================================================
# 4. EXPOSURE & BRIGHTNESS HARMONIZATION WITH DARK HERO BACKGROUND
# ==============================================================================
print("4. Harmonizing photo exposure, highlight roll-off, and cinematic color grade...")
# A. Highlight Compression (roll off harsh flash glare on forehead and nose)
x_norm = photo_beautified / 255.0

# Filmic highlight tone-mapping: soft S-curve knee above 0.65 (retains facial contrast without blown highlights)
tone_mapped = np.where(x_norm > 0.62, 0.62 + (x_norm - 0.62) * 0.62, x_norm)

# Exposure matching: gentle 0.94 multiplier so photo seamlessly matches the dark moody hero background
exposure_matched = tone_mapped * 255.0 * 0.95

# B. Ambient Color Grading (harmonizing with the portfolio's crimson/dark obsidian palette)
# Subtle warm crimson undertone in ambient shadows and midtones:
crimson_tint = np.array([8.0, 4.0, 18.0], dtype=np.float32) # BGR
shadow_ambient = np.clip(1.0 - (exposure_matched / 175.0), 0.0, 1.0)
exposure_matched += shadow_ambient * crimson_tint * 0.22

# Ensure valid range
photo_final_bgr = np.clip(exposure_matched, 0, 255).astype(np.uint8)

# Construct final 4-channel RGBA cutout
photo_final_rgba = np.zeros((h, w, 4), dtype=np.uint8)
photo_final_rgba[:, :, :3] = photo_final_bgr
photo_final_rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

# Save photo cutout in processed and workspace root
cutout_path_proc = os.path.join(PROCESSED_DIR, "photo_cutout.png")
cutout_path_root = os.path.join(ROOT_DIR, "photo_cutout.png")
cv2.imwrite(cutout_path_proc, photo_final_rgba)
cv2.imwrite(cutout_path_root, photo_final_rgba)
cv2.imwrite(os.path.join(PROCESSED_DIR, "photo_alpha.png"), (alpha * 255).astype(np.uint8))
print(f"Saved enhanced photo_cutout.png to {cutout_path_root} ({os.path.getsize(cutout_path_root)/(1024):.1f} KB)")

# ==============================================================================
# 5. VISUAL ARTIFACT GENERATION (HIGH-RES COMPARISONS)
# ==============================================================================
print("5. Generating high-resolution comparison figure...")
fig = plt.figure(figsize=(20, 14), facecolor='#060408')
gs = fig.add_gridspec(2, 3, wspace=0.08, hspace=0.14)

# Panel 1: Full-Screen Harmonized Photo on Dark Portfolio Background
ax1 = fig.add_subplot(gs[:, 0])
ax1.set_facecolor('#070508')

# Render on dark portfolio background (#060408)
bg_hero = np.full((h, w, 3), [8, 4, 6], dtype=np.uint8) # Dark crimson-tinted obsidian
a_comp = alpha[:, :, None]
comp_rgb = (cv2.cvtColor(photo_final_bgr, cv2.COLOR_BGR2RGB) * a_comp + bg_hero * (1.0 - a_comp)).astype(np.uint8)
ax1.imshow(comp_rgb)
ax1.set_title("Harmonized Photo on Dark Portfolio Hero Background\nDense Hair, Smooth Skin & Seamless Exposure", color='white', fontsize=12, fontweight='bold', pad=12)
ax1.axis('off')

# Panel 2: Hair Density & Volume Zoom
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#070508')
hair_crop = comp_rgb[20:180, 380:640]
ax2.imshow(hair_crop)
ax2.set_title("Dense Volumetric Hair: Opaque Strands & Enhanced Curls", color='#ff5065', fontsize=12, fontweight='bold', pad=10)
ax2.axis('off')

# Panel 3: Face Beautification & Skin Smoothing Zoom
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor('#070508')
face_crop = comp_rgb[140:340, 420:605]
ax3.imshow(face_crop)
ax3.set_title("Silky Smooth Skin: Zero Glare, Sharp Eyes & Beard", color='#ff7080', fontsize=12, fontweight='bold', pad=10)
ax3.axis('off')

# Panel 4: Alpha Channel Heatmap (Hair & Silhouette Fullness)
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#070508')
ax4.imshow(alpha, cmap='magma')
ax4.set_title("Alpha Matte: 100% Solid Hair Volume & Soft Flyaway Edge", color='white', fontsize=12, fontweight='bold', pad=10)
ax4.axis('off')

# Panel 5: Split Comparison (Before vs After Exposure & Beautification)
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor('#070508')
orig_rgb = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
split_img = np.zeros_like(comp_rgb)
split_img[:, :w//2] = orig_rgb[:, :w//2]
split_img[:, w//2:] = comp_rgb[:, w//2:]
# Draw dividing line
split_img[:, w//2-1:w//2+1] = [220, 30, 50]
ax5.imshow(split_img[100:380, 360:660])
ax5.set_title("Left: Original Raw Flash | Right: Beautified & Matched", color='white', fontsize=12, fontweight='bold', pad=10)
ax5.axis('off')

screenshot_path = os.path.join(ARTIFACT_DIR, "photo_cutout_enhanced_comparison.png")
plt.subplots_adjust(left=0.03, right=0.97, top=0.94, bottom=0.04, wspace=0.12, hspace=0.16)
plt.savefig(screenshot_path, dpi=150, facecolor='#060408')
plt.close()
print("Saved comparison screenshot to:", screenshot_path)
