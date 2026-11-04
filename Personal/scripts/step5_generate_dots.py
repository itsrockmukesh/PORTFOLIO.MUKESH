import os
import cv2
import numpy as np
from scipy import ndimage
import trimesh
import matplotlib.pyplot as plt

PROCESSED_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/processed"
OUTPUT_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/output"
ARTIFACT_DIR = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41"
TARGET_DOTS = 78000

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading aligned mesh...")
mesh = trimesh.load(os.path.join(PROCESSED_DIR, "bust_aligned.obj"))
mesh.fix_normals()

# Precompute clay shading maps for local contrast and edges
print("Computing clay shading texture maps (local contrast + edges)...")
clay_front_bgr = cv2.imread(os.path.join(PROCESSED_DIR, "clay_front_1200x896.png"))
clay_front_gray = cv2.cvtColor(clay_front_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

# 1. Local contrast via Difference of Gaussians (DoG)
blur_fine = cv2.GaussianBlur(clay_front_gray, (0, 0), sigmaX=1.5)
blur_broad = cv2.GaussianBlur(clay_front_gray, (0, 0), sigmaX=8.0)
local_contrast = blur_fine - blur_broad

# 2. Sobel edge magnitude
sobel_x = cv2.Sobel(clay_front_gray, cv2.CV_32F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(clay_front_gray, cv2.CV_32F, 0, 1, ksize=3)
edges = np.sqrt(sobel_x**2 + sobel_y**2)

# Combine: base luminance + enhanced local contrast + crisp edge lines
clay_detail = (
    0.35 * (1.0 - clay_front_gray) + # Darker clay features (hair strands, shirt folds) become brighter dots
    0.45 * np.clip(local_contrast * 4.0 + 0.4, 0.0, 1.0) +
    0.30 * np.clip(edges * 5.0, 0.0, 1.0)
)
# Normalize to [0.15, 0.95]
clay_detail = (clay_detail - clay_detail.min()) / (clay_detail.max() - clay_detail.min() + 1e-6)
clay_detail = 0.15 + 0.80 * clay_detail
cf_h, cf_w = clay_detail.shape # 896 x 1200

# Sample candidate surface points with Poisson disk (blue noise) even spacing
print(f"Sampling surface dots with Poisson-disk spacing...")
candidates, face_indices = trimesh.sample.sample_surface_even(mesh, 115000)
n_cand = len(candidates)
print(f"Sampled {n_cand} candidate points")

# Interpolate smooth surface normals for each sampled point
# Get face vertices and normals
f_verts = mesh.vertices[mesh.faces[face_indices]] # (N, 3, 3)
f_norms = mesh.vertex_normals[mesh.faces[face_indices]] # (N, 3, 3)

# Compute barycentric coordinates for exact normal interpolation
v0 = f_verts[:, 0]
v1 = f_verts[:, 1]
v2 = f_verts[:, 2]

p = candidates
v0v1 = v1 - v0
v0v2 = v2 - v0
pv0 = p - v0

d00 = np.einsum('ij,ij->i', v0v1, v0v1)
d01 = np.einsum('ij,ij->i', v0v1, v0v2)
d11 = np.einsum('ij,ij->i', v0v2, v0v2)
d20 = np.einsum('ij,ij->i', pv0, v0v1)
d21 = np.einsum('ij,ij->i', pv0, v0v2)

denom = d00 * d11 - d01 * d01
denom = np.where(np.abs(denom) < 1e-8, 1e-8, denom)
v = (d11 * d20 - d01 * d21) / denom
w = (d00 * d21 - d01 * d20) / denom
u = 1.0 - v - w

# Clamp barycentric coords to [0, 1]
u = np.clip(u, 0.0, 1.0)
v = np.clip(v, 0.0, 1.0)
w = np.clip(w, 0.0, 1.0)
sum_uvw = u + v + w
u /= sum_uvw
v /= sum_uvw
w /= sum_uvw

cand_normals = (
    u[:, None] * f_norms[:, 0] +
    v[:, None] * f_norms[:, 1] +
    w[:, None] * f_norms[:, 2]
)
cand_normals /= (np.linalg.norm(cand_normals, axis=1, keepdims=True) + 1e-8)

# Map dots to clay image coordinate space to sample brightness
# Recall alignment transform:
# x_aligned = tx + (x_clay - 600.5) * sx => x_clay = 600.5 + (x_aligned - tx) / sx
# y_aligned = ty + (y_clay - 28.7) * sy => y_clay = 28.7 + (y_aligned - ty) / sy
sx_opt, sy_opt, tx_opt, ty_opt = 0.8089, 0.7106, 513.0, 24.59

clay_x = 600.5 + (candidates[:, 0] - tx_opt) / sx_opt
clay_y = 28.7 + (candidates[:, 1] - ty_opt) / sy_opt

clay_ix = np.clip(np.round(clay_x).astype(int), 0, cf_w - 1)
clay_iy = np.clip(np.round(clay_y).astype(int), 0, cf_h - 1)

# Sample brightness
cand_bright = clay_detail[clay_iy, clay_ix]

# 1. Featureless smooth face oval:
# Face oval centered at (513, 215) in photo space
dx_face = (candidates[:, 0] - 513.0) / 95.0
dy_face = (candidates[:, 1] - 215.0) / 115.0
dist_face = np.sqrt(dx_face**2 + dy_face**2)

# Only apply to front-facing surface (nz < -0.3)
front_facing = cand_normals[:, 2] < -0.2
in_face = (dist_face < 1.0) & front_facing

# Soft feathering transition at hairline and jaw
feather = np.clip((1.0 - dist_face) / 0.25, 0.0, 1.0)
feather[~front_facing] = 0.0

smooth_face_val = 0.48
cand_bright = (1.0 - feather) * cand_bright + feather * smooth_face_val

# 2. Dim flat upward-facing ledges (normals pointing up: ny < -0.3)
upward_component = -cand_normals[:, 1] # Positive when pointing UP
dim_factor = np.clip(1.0 - 1.8 * np.maximum(0.0, upward_component - 0.35), 0.12, 1.0)
cand_bright *= dim_factor

# 3. Density weighting: slightly tighter in bright areas
# Acceptance probability proportional to brightness
keep_prob = 0.65 + 0.45 * cand_bright
rng = np.random.default_rng(42)
rand_vals = rng.random(n_cand)
accepted = rand_vals < keep_prob

if accepted.sum() < TARGET_DOTS:
    # If slightly below, take top TARGET_DOTS by prob
    chosen_indices = np.argsort(-keep_prob)[:TARGET_DOTS]
else:
    accepted_indices = np.where(accepted)[0]
    chosen_indices = rng.choice(accepted_indices, size=TARGET_DOTS, replace=False)

# Extract exactly 78,000 dots
dots_pos = candidates[chosen_indices].astype(np.float32)
dots_norm = cand_normals[chosen_indices].astype(np.float32)
dots_bright = cand_bright[chosen_indices].astype(np.float32)
dots_rand = rng.random(TARGET_DOTS).astype(np.float32)

print(f"Final dots count: {len(dots_pos)} (Target: {TARGET_DOTS})")
print(f"Position X range: [{dots_pos[:,0].min():.1f}, {dots_pos[:,0].max():.1f}]")
print(f"Position Y range: [{dots_pos[:,1].min():.1f}, {dots_pos[:,1].max():.1f}]")
print(f"Position Z range: [{dots_pos[:,2].min():.1f}, {dots_pos[:,2].max():.1f}]")
print(f"Brightness range: [{dots_bright.min():.3f}, {dots_bright.max():.3f}], mean: {dots_bright.mean():.3f}")

# Pack into single interleaved binary file:
# [x, y, z, nx, ny, nz, rand, bright] per dot = 8 float32 (32 bytes per dot)
dot_buffer = np.zeros((TARGET_DOTS, 8), dtype=np.float32)
dot_buffer[:, 0:3] = dots_pos
dot_buffer[:, 3:6] = dots_norm
dot_buffer[:, 6] = dots_rand
dot_buffer[:, 7] = dots_bright

bin_path = os.path.join(OUTPUT_DIR, "dots.bin")
dot_buffer.tofile(bin_path)
file_size_mb = os.path.getsize(bin_path) / (1024 * 1024)
print(f"Saved binary dot file to: {bin_path} ({file_size_mb:.2f} MB)")

# Also save copy in processed dir
dot_buffer.tofile(os.path.join(PROCESSED_DIR, "dots.bin"))

# Generate high-resolution visual figure of the dots
fig = plt.figure(figsize=(18, 14), facecolor='#060406')
gs = fig.add_gridspec(2, 2, wspace=0.05, hspace=0.10)

# Crimson color palette: RGB [0.64, 0.035, 0.055]
crimson_base = np.array([0.64, 0.035, 0.055])

# Panel 1: Full-screen orthographic front scatter
ax1 = fig.add_subplot(gs[:, 0])
ax1.set_facecolor('#070508')

# Color dots by brightness in dark crimson
colors = np.zeros((TARGET_DOTS, 4), dtype=float)
# Dark crimson scaled by brightness with slight glow
colors[:, 0] = np.clip(crimson_base[0] * (0.4 + 0.8 * dots_bright), 0, 1)
colors[:, 1] = np.clip(crimson_base[1] * (0.3 + 0.7 * dots_bright), 0, 1)
colors[:, 2] = np.clip(crimson_base[2] * (0.3 + 0.7 * dots_bright), 0, 1)
colors[:, 3] = np.clip(0.35 + 0.60 * dots_bright, 0, 1)

# Sort back-to-front by Z for proper alpha blending
order = np.argsort(dots_pos[:, 2])
ax1.scatter(dots_pos[order, 0], dots_pos[order, 1], c=colors[order], s=1.2, edgecolors='none')
ax1.set_aspect('equal')
ax1.set_xlim(100, 924)
ax1.set_ylim(580, 10) # Inverted Y for image space
ax1.set_title("78,000 Surface Dots in Dark Crimson\nPoisson-Disk Spacing & Clay Detail Shading", color='white', fontsize=14, fontweight='bold', pad=12)
ax1.axis('off')

# Panel 2: Zoom on Hair Strands & Hairline
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#070508')
hair_mask = (dots_pos[:, 1] >= 20) & (dots_pos[:, 1] <= 180) & (dots_pos[:, 0] >= 380) & (dots_pos[:, 0] <= 640)
ax2.scatter(dots_pos[hair_mask, 0], dots_pos[hair_mask, 1], c=colors[hair_mask], s=3.5, edgecolors='none')
ax2.set_aspect('equal')
ax2.set_xlim(380, 640)
ax2.set_ylim(180, 20)
ax2.set_title("Hair Strands, Hairline & Crown Curl Detail", color='white', fontsize=13, fontweight='bold', pad=10)
ax2.axis('off')

# Panel 3: Zoom on Collar, Buttons & Shirt Folds
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor('#070508')
shirt_mask = (dots_pos[:, 1] >= 340) & (dots_pos[:, 1] <= 560) & (dots_pos[:, 0] >= 300) & (dots_pos[:, 0] <= 720)
ax3.scatter(dots_pos[shirt_mask, 0], dots_pos[shirt_mask, 1], c=colors[shirt_mask], s=2.5, edgecolors='none')
ax3.set_aspect('equal')
ax3.set_xlim(300, 720)
ax3.set_ylim(560, 340)
ax3.set_title("Polo Collar Creases & Fabric Fold Contrast", color='white', fontsize=13, fontweight='bold', pad=10)
ax3.axis('off')

screenshot_path = os.path.join(ARTIFACT_DIR, "step5_surface_dots.png")
plt.tight_layout()
plt.savefig(screenshot_path, dpi=150, facecolor='#060406')
plt.close()
print("Saved Step 5 screenshot to:", screenshot_path)
