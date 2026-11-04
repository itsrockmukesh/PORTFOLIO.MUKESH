import cv2
import numpy as np
import matplotlib.pyplot as plt

photo = cv2.imread("/Users/mukeshkumar/PORTFOLIO/Personal/inputs/photo.png")
h, w, c = photo.shape

# 1. Precise Hair Mask with Dense Volumetric Coverage
# Any pixel in upper region with brightness > 4 is part of head/hair
gray = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
luminance = 0.299 * photo[:,:,2] + 0.587 * photo[:,:,1] + 0.114 * photo[:,:,0] # BGR to RGB lum

# Background is pure black (< 4)
fg_mask = (photo.max(axis=2) >= 5).astype(np.uint8)

# Close neck gaps between neck and collar
neck_y1, neck_y2 = 320, 480
neck_x1, neck_x2 = 420, 610
neck_patch = fg_mask[neck_y1:neck_y2, neck_x1:neck_x2]
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
closed_neck = cv2.morphologyEx(neck_patch, cv2.MORPH_CLOSE, kernel)
fg_mask[neck_y1:neck_y2, neck_x1:neck_x2] = closed_neck

# Fill interior holes
from scipy import ndimage
fg_filled = ndimage.binary_fill_holes(fg_mask).astype(np.uint8)

# In the hair region (y <= 175, or sides y in [140, 240] and x outside [445, 580]),
# make hair alpha solid and dense:
# Create dense hair mask
hair_zone = np.zeros((h, w), dtype=bool)
hair_zone[:175, :] = True
hair_zone[140:240, :448] = True
hair_zone[140:240, 576:] = True

# Inside the hair zone, any pixel with max_rgb >= 8 is 100% solid hair!
# And soft antialiased edge for outer flyaways:
dense_hair_alpha = np.zeros((h, w), dtype=np.float32)
dense_hair_alpha[fg_filled > 0] = 1.0

# Refine hair perimeter with high-quality soft antialiasing
# Dilate foreground slightly to capture all delicate flyaway strands
flyaways = (photo.max(axis=2) >= 5) & (fg_filled == 0) & hair_zone
dense_hair_alpha[flyaways] = np.clip(photo.max(axis=2)[flyaways] / 35.0, 0.0, 1.0)

# Smooth the boundary of alpha with gentle 1.2px gaussian blur along transition
alpha_smooth = cv2.GaussianBlur(dense_hair_alpha, (3, 3), 0.8)
# Keep solid core fully 1.0
core = cv2.erode(fg_filled, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
final_alpha = np.where(core > 0, 1.0, alpha_smooth)
final_alpha = np.clip(final_alpha, 0.0, 1.0)

# Check hair alpha now:
hair_crop_alpha = final_alpha[20:160, 380:640]
print(f"Enhanced Hair Alpha: min={hair_crop_alpha.min():.2f}, mean={hair_crop_alpha.mean():.2f}, max={hair_crop_alpha.max():.2f}")
print(f"Hair pixels with alpha < 0.95: {(hair_crop_alpha < 0.95).sum()} / {hair_crop_alpha.size} ({(hair_crop_alpha < 0.95).mean()*100:.1f}%)")

# 2. Skin Smoothing & Facial Beautification
# Detect skin pixels in face area
ycrcb = cv2.cvtColor(photo, cv2.COLOR_BGR2YCrCb)
Y, Cr, Cb = ycrcb[:,:,0], ycrcb[:,:,1], ycrcb[:,:,2]

# Skin color rule for Mukesh:
skin_color = (Cr >= 132) & (Cr <= 172) & (Cb >= 98) & (Cb <= 138) & (Y >= 65)

# Restrict to face bounds
face_y1, face_y2 = 145, 345
face_x1, face_x2 = 420, 605
face_mask = np.zeros((h, w), dtype=bool)
face_mask[face_y1:face_y2, face_x1:face_x2] = True

skin_mask = skin_color & face_mask

# Exclude facial hair (beard, mustache), eyebrows, eyes, glasses
# Dark features:
is_dark = (Y < 75) & face_mask
# High-contrast edges (glasses frames, eyes, pupils):
sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
edge_mag = np.sqrt(sobel_x**2 + sobel_y**2)
is_edge = (edge_mag > 32) & face_mask

# Eyes and glasses box protection:
# Glasses/eyes are around y in [180, 235], x in [440, 580]
glasses_eyes_zone = np.zeros((h, w), dtype=bool)
glasses_eyes_zone[180:235, 440:580] = True
protect_glasses_eyes = glasses_eyes_zone & ((edge_mag > 20) | (Y < 85) | (Y > 230))

# Mustache & beard protection:
mustache_zone = np.zeros((h, w), dtype=bool)
mustache_zone[240:270, 465:555] = True
beard_zone = np.zeros((h, w), dtype=bool)
beard_zone[265:345, 430:590] = True
protect_facial_hair = (mustache_zone | beard_zone) & ((Y < 95) | (edge_mag > 18))

# Final clean skin mask
skin_smooth_mask = skin_mask & ~is_dark & ~is_edge & ~protect_glasses_eyes & ~protect_facial_hair
skin_smooth_mask_f = cv2.GaussianBlur(skin_smooth_mask.astype(np.float32), (9, 9), 3.0)

# Edge-preserving skin smoothing via Bilateral Filter
smoothed_photo = cv2.bilateralFilter(photo, d=11, sigmaColor=45, sigmaSpace=45)
# Second pass for silky skin finish
smoothed_photo = cv2.bilateralFilter(smoothed_photo, d=7, sigmaColor=30, sigmaSpace=30)

# Blend smoothed skin into original photo
photo_beautified = photo.copy().astype(np.float32)
for c in range(3):
    photo_beautified[:,:,c] = (
        (1.0 - skin_smooth_mask_f) * photo[:,:,c] +
        skin_smooth_mask_f * smoothed_photo[:,:,c]
    )

# 3. Enhance Hair Density & Rich Tones in photo:
# In the hair region, boost rich dark espresso tones and curly strand contrast
hair_enh_mask = (hair_zone & (fg_filled > 0) & (Y < 125)).astype(np.float32)
hair_enh_mask = cv2.GaussianBlur(hair_enh_mask, (15, 15), 5.0)

# Rich hair grading: deepen blacks slightly, enhance strand definition
hair_strands_unsharp = cv2.addWeighted(photo_beautified, 1.25, cv2.GaussianBlur(photo_beautified, (0, 0), 2.0), -0.25, 0)
for c in range(3):
    # Deepen dark hair slightly to look thick and full
    deepened = np.clip(hair_strands_unsharp[:,:,c] * 0.94, 0, 255)
    photo_beautified[:,:,c] = (1.0 - hair_enh_mask) * photo_beautified[:,:,c] + hair_enh_mask * deepened

# 4. Exposure & Brightness Matching with Dark WebGL Background:
# A. Highlight tone-mapping (compress blown-out highlights from flash)
# Soft roll-off above 180:
# Map [0..255] through a filmic curve
x_norm = photo_beautified / 255.0

# Filmic highlight compression:
# S-curve: x / (1.0 + 0.25 * x^2)
tone_mapped = np.where(x_norm > 0.65, 0.65 + (x_norm - 0.65) * 0.60, x_norm)
# Exposure harmonization factor:
exposure_matched = tone_mapped * 255.0

# B. Subtle ambient color grading matching the hero crimson/dark obsidian palette:
# Dark hero ambiance: rgb(0.64, 0.035, 0.055)
# Infuse very subtle warm ambient grade into shadows/midtones:
crimson_tint = np.array([12, 6, 22], dtype=np.float32) # BGR
shadow_weight = np.clip(1.0 - (exposure_matched / 180.0), 0.0, 1.0)
exposure_matched += shadow_weight * crimson_tint * 0.25

# C. Soft vignette at the bottom of the polo shirt to feather into the dark background:
y_coords = np.arange(h)[:, None]
bottom_fade = np.clip(1.0 - (y_coords - 480) / 96.0, 0.0, 1.0)
final_alpha *= bottom_fade

photo_final_bgr = np.clip(exposure_matched, 0, 255).astype(np.uint8)

print("Beautification, hair densification, and exposure harmonization complete!")
