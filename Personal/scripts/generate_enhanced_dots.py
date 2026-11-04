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

print("Loading aligned bust mesh...")
mesh = trimesh.load(os.path.join(PROCESSED_DIR, "bust_aligned.obj"))
mesh.fix_normals()

# 1. Precompute multi-scale clay textures for hair strands and face smoothness
print("Computing multi-frequency hair strand filters and clay textures...")
clay_front = cv2.imread(os.path.join(PROCESSED_DIR, "clay_front_1200x896.png"))
clay_gray = cv2.cvtColor(clay_front, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
cf_h, cf_w = clay_gray.shape

# Difference of Gaussians (DoG) for hair curls and fine strand details
blur_micro = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=0.9)
blur_fine = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=1.8)
blur_mid = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=3.8)
blur_broad = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=8.5)

hair_micro_strands = np.clip((blur_micro - blur_fine) * 9.0, -1.0, 1.0)
hair_strands = np.clip((blur_fine - blur_mid) * 7.0, -1.0, 1.0)
hair_waves = np.clip((blur_mid - blur_broad) * 5.0, -1.0, 1.0)

# Sobel edge gradients for lock boundaries & hairline
sx = cv2.Sobel(clay_gray, cv2.CV_32F, 1, 0, ksize=3)
sy = cv2.Sobel(clay_gray, cv2.CV_32F, 0, 1, ksize=3)
edges = np.sqrt(sx**2 + sy**2)

# Base clay detail for shirt / collar / chest
local_contrast = blur_fine - blur_broad
clay_base = (
    0.35 * (1.0 - clay_gray) +
    0.45 * np.clip(local_contrast * 4.0 + 0.4, 0.0, 1.0) +
    0.30 * np.clip(edges * 5.0, 0.0, 1.0)
)
clay_base = 0.15 + 0.80 * ((clay_base - clay_base.min()) / (clay_base.max() - clay_base.min() + 1e-6))

# Alignment transform:
sx_opt, sy_opt, tx_opt, ty_opt = 0.8089, 0.7106, 513.0, 24.59

# Helper to interpolate barycentric normals for sampled points
def get_surface_normals(sub_mesh, pts, f_indices):
    f_verts = sub_mesh.vertices[sub_mesh.faces[f_indices]]
    f_norms = sub_mesh.vertex_normals[sub_mesh.faces[f_indices]]
    v0, v1, v2 = f_verts[:, 0], f_verts[:, 1], f_verts[:, 2]
    v0v1 = v1 - v0
    v0v2 = v2 - v0
    pv0 = pts - v0
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
    u = np.clip(u, 0.0, 1.0)
    v = np.clip(v, 0.0, 1.0)
    w = np.clip(w, 0.0, 1.0)
    sum_uvw = u + v + w
    u /= sum_uvw
    v /= sum_uvw
    w /= sum_uvw
    norms = u[:, None] * f_norms[:, 0] + v[:, None] * f_norms[:, 1] + w[:, None] * f_norms[:, 2]
    return norms / (np.linalg.norm(norms, axis=1, keepdims=True) + 1e-8)

print("Sampling base surface dots with Poisson-disk spacing...")
cand_base, f_base = trimesh.sample.sample_surface_even(mesh, 115000)
norm_base = get_surface_normals(mesh, cand_base, f_base)

# Identify hair faces to sample extra dense hair dots
f_centers = mesh.triangles_center
hair_face_mask = (
    (f_centers[:, 1] < 165) |
    ((f_centers[:, 1] >= 165) & (f_centers[:, 1] < 240) & ((f_centers[:, 0] < 452) | (f_centers[:, 0] > 574))) |
    ((f_centers[:, 1] < 265) & (f_centers[:, 2] > 15))
)
hair_submesh = mesh.submesh([hair_face_mask], append=True)

# Sample extra 22,000 hair points specifically to enrich hair density
print("Sampling extra hair candidate dots (22,000 dots)...")
cand_hair, f_hair = trimesh.sample.sample_surface_even(hair_submesh, 22000)
norm_hair = get_surface_normals(hair_submesh, cand_hair, f_hair)

# Combine candidate sets
all_pts = np.vstack([cand_base, cand_hair])
all_norms = np.vstack([norm_base, norm_hair])
n_total_cand = len(all_pts)
print(f"Total candidate dots: {n_total_cand}")

# Map all points to clay space
clay_x = np.clip(np.round(600.5 + (all_pts[:, 0] - tx_opt) / sx_opt).astype(int), 0, cf_w - 1)
clay_y = np.clip(np.round(28.7 + (all_pts[:, 1] - ty_opt) / sy_opt).astype(int), 0, cf_h - 1)

# Base brightness from clay texture
all_bright = clay_base[clay_y, clay_x]

# Hair region identification:
is_top_hair = all_pts[:, 1] < 162
is_side_hair = (all_pts[:, 1] >= 140) & (all_pts[:, 1] < 240) & ((all_pts[:, 0] < 452) | (all_pts[:, 0] > 574))
is_back_hair = (all_pts[:, 1] < 265) & (all_pts[:, 2] > 15)
is_hair = is_top_hair | is_side_hair | is_back_hair

print(f"Total candidates in hair region: {is_hair.sum()} ({is_hair.sum()/n_total_cand*100:.1f}%)")

# HAIR ENHANCEMENT:
# 1. Rich multi-scale hair strand contrast & lock highlights
c_micro = hair_micro_strands[clay_y, clay_x]
c_strands = hair_strands[clay_y, clay_x]
c_waves = hair_waves[clay_y, clay_x]
c_edges = edges[clay_y, clay_x]

hair_val = (
    0.46 + 
    0.28 * np.clip(c_micro * 1.5, -0.4, 0.9) +
    0.25 * np.clip(c_strands * 1.5, -0.4, 0.9) +
    0.18 * np.clip(c_waves * 1.2, -0.4, 0.8) +
    0.16 * np.clip(c_edges * 1.8, 0.0, 1.0)
)
hair_val = np.clip(hair_val, 0.28, 0.98)
all_bright = np.where(is_hair, hair_val, all_bright)

# 2. 3D Volumetric hair loft / strand wave offset along normal
hair_loft = np.zeros_like(all_pts)
hair_loft_dist = np.clip(0.8 + 2.5 * c_waves + 1.8 * c_strands + 1.0 * c_micro, -0.8, 4.5)
hair_loft[is_hair] = all_norms[is_hair] * hair_loft_dist[is_hair, None]
all_pts_adj = all_pts + hair_loft

# FACE BEAUTIFICATION:
# Accurate face oval centered in photo space
x0, y0 = 512.8, 232.0
ry_face = 95.0
y_rel = (all_pts_adj[:, 1] - y0) / ry_face
# Taper width towards chin
rx_eff = 72.0 * np.where(y_rel > 0, 1.0 - 0.28 * y_rel, 1.0)
x_rel = (all_pts_adj[:, 0] - x0) / rx_eff
dist_face = np.sqrt(x_rel**2 + y_rel**2)

is_front = (all_norms[:, 2] < -0.15) & (all_pts_adj[:, 2] < 30)
face_mask = (dist_face <= 1.0) & is_front

# Soft C^2 feathering at face perimeter
t_face = np.clip((1.0 - dist_face) / 0.32, 0.0, 1.0)
w_face = t_face * t_face * (3.0 - 2.0 * t_face)
w_face[~is_front] = 0.0

# 1. Silky porcelain luminance gradient on face:
# Soft studio cheekbone/forehead highlight with silky smooth falloff
face_smooth_val = 0.52 + 0.12 * np.clip(1.0 - dist_face**2, 0.0, 1.0)
all_bright = (1.0 - w_face) * all_bright + w_face * face_smooth_val

# 2. Mathematical C^inf dome normals on face for flawless specular sheen:
dx = (all_pts_adj[:, 0] - x0) / (72.0**2)
dy = (all_pts_adj[:, 1] - y0) / (95.0**2)
dz = (all_pts_adj[:, 2] - (-65.0)) / (45.0**2)
smooth_norm = np.stack([dx, dy, dz], axis=-1)
smooth_norm /= (np.linalg.norm(smooth_norm, axis=1, keepdims=True) + 1e-8)
smooth_norm[:, 2] = -np.abs(smooth_norm[:, 2])

# Blend normals on face
all_norms_adj = (1.0 - w_face[:, None]) * all_norms + w_face[:, None] * smooth_norm
all_norms_adj /= (np.linalg.norm(all_norms_adj, axis=1, keepdims=True) + 1e-8)

# Ledge dimming: apply ONLY to shoulders and base (y > 380), NOT hair!
upward_component = -all_norms_adj[:, 1]
dim_factor = np.ones(n_total_cand, dtype=float)
is_shoulder_ledge = (all_pts_adj[:, 1] > 380) & (upward_component > 0.35)
dim_factor[is_shoulder_ledge] = np.clip(1.0 - 1.8 * (upward_component[is_shoulder_ledge] - 0.35), 0.15, 1.0)
all_bright *= dim_factor

# Balanced dot selection:
# We want:
# ~24,000 hair dots (~31%)
# ~4,500 face dots (~6%)
# ~49,500 body/collar/shirt dots (~63%)
keep_prob = np.zeros(n_total_cand, dtype=float)
for i in range(n_total_cand):
    if is_hair[i]:
        keep_prob[i] = 0.58 + 0.30 * all_bright[i]
    elif face_mask[i]:
        keep_prob[i] = 0.75 + 0.20 * all_bright[i]
    else:
        keep_prob[i] = 0.52 + 0.35 * all_bright[i]

rng = np.random.default_rng(42)
rand_vals = rng.random(n_total_cand)
accepted = rand_vals < keep_prob

if accepted.sum() < TARGET_DOTS:
    chosen_indices = np.argsort(-keep_prob)[:TARGET_DOTS]
else:
    # Weighted choice among accepted
    accepted_indices = np.where(accepted)[0]
    sub_probs = keep_prob[accepted_indices]
    sub_probs /= sub_probs.sum()
    chosen_indices = rng.choice(accepted_indices, size=TARGET_DOTS, replace=False, p=sub_probs)

dots_pos = all_pts_adj[chosen_indices].astype(np.float32)
dots_norm = all_norms_adj[chosen_indices].astype(np.float32)
dots_bright = all_bright[chosen_indices].astype(np.float32)
dots_rand = rng.random(TARGET_DOTS).astype(np.float32)

hair_final = is_hair[chosen_indices]
face_final = face_mask[chosen_indices]
body_final = ~hair_final & ~face_final

print(f"\n--- Final Dot Statistics ---")
print(f"Total dots: {len(dots_pos):,}")
print(f"Hair dots: {hair_final.sum():,} ({hair_final.sum()/TARGET_DOTS*100:.1f}%) [Was 9,506]")
print(f"Face dots: {face_final.sum():,} ({face_final.sum()/TARGET_DOTS*100:.1f}%) [Beautified porcelain smooth]")
print(f"Body/Shirt dots: {body_final.sum():,} ({body_final.sum()/TARGET_DOTS*100:.1f}%)")
print(f"Hair brightness range: [{dots_bright[hair_final].min():.3f}, {dots_bright[hair_final].max():.3f}], mean: {dots_bright[hair_final].mean():.3f}")
print(f"Face brightness range: [{dots_bright[face_final].min():.3f}, {dots_bright[face_final].max():.3f}], mean: {dots_bright[face_final].mean():.3f}")

# Save enhanced binary dots file
bin_path = os.path.join(OUTPUT_DIR, "dots.bin")
dot_buffer = np.zeros((TARGET_DOTS, 8), dtype=np.float32)
dot_buffer[:, 0:3] = dots_pos
dot_buffer[:, 3:6] = dots_norm
dot_buffer[:, 6] = dots_rand
dot_buffer[:, 7] = dots_bright
dot_buffer.tofile(bin_path)

# Also save directly in workspace root for WebGL server
dot_buffer.tofile("/Users/mukeshkumar/PORTFOLIO/Personal/dots.bin")
dot_buffer.tofile(os.path.join(PROCESSED_DIR, "dots.bin"))
print(f"Saved enhanced dots.bin ({os.path.getsize(bin_path)/(1024*1024):.2f} MB)")

# Generate visual figure showing Hair Enhancement and Face Beautification
fig = plt.figure(figsize=(20, 14), facecolor='#060406')
gs = fig.add_gridspec(2, 3, wspace=0.06, hspace=0.12)

crimson_base = np.array([0.64, 0.035, 0.055])
colors = np.zeros((TARGET_DOTS, 4), dtype=float)
colors[:, 0] = np.clip(crimson_base[0] * (0.35 + 0.90 * dots_bright), 0, 1)
colors[:, 1] = np.clip(crimson_base[1] * (0.30 + 0.85 * dots_bright), 0, 1)
colors[:, 2] = np.clip(crimson_base[2] * (0.30 + 0.85 * dots_bright), 0, 1)
colors[:, 3] = np.clip(0.35 + 0.65 * dots_bright, 0, 1)

order = np.argsort(dots_pos[:, 2])

# Panel 1: Full Front Bust with Enhanced Hair & Smooth Porcelain Face
ax1 = fig.add_subplot(gs[:, 0])
ax1.set_facecolor('#070508')
ax1.scatter(dots_pos[order, 0], dots_pos[order, 1], c=colors[order], s=1.3, edgecolors='none')
ax1.set_aspect('equal')
ax1.set_xlim(120, 904)
ax1.set_ylim(580, 15)
ax1.set_title("Full Bust Hero (78,000 Dots)\nEnhanced Hair Volume & Silky Smooth Face", color='white', fontsize=13, fontweight='bold', pad=12)
ax1.axis('off')

# Panel 2: Zoom on Enhanced Hair Strands, Volume & Curls
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#070508')
h_idx = np.where(hair_final)[0]
ax2.scatter(dots_pos[h_idx, 0], dots_pos[h_idx, 1], c=colors[h_idx], s=3.2, edgecolors='none')
ax2.set_aspect('equal')
ax2.set_xlim(370, 655)
ax2.set_ylim(170, 20)
ax2.set_title(f"Enhanced Hair: {hair_final.sum():,} Dots (Dense Locks & 3D Loft)", color='#ff5065', fontsize=12, fontweight='bold', pad=10)
ax2.axis('off')

# Panel 3: Zoom on Beautified Porcelain Face Smoothness
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor('#070508')
f_idx = np.where(face_final)[0]
ax3.scatter(dots_pos[f_idx, 0], dots_pos[f_idx, 1], c=colors[f_idx], s=3.8, edgecolors='none')
ax3.set_aspect('equal')
ax3.set_xlim(420, 605)
ax3.set_ylim(350, 130)
ax3.set_title(f"Beautified Face: {face_final.sum():,} Dots (Silky Smooth Porcelain)", color='#ff7080', fontsize=12, fontweight='bold', pad=10)
ax3.axis('off')

# Panel 4: Shaded 3D Angle (30 Degrees) showing 3D Hair Depth & Pure Facial Curvature
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#070508')
theta = np.radians(30)
cos_t, sin_t = np.cos(theta), np.sin(theta)
x_rot = (dots_pos[:, 0] - 512.8) * cos_t - dots_pos[:, 2] * sin_t + 512.8
z_rot = (dots_pos[:, 0] - 512.8) * sin_t + dots_pos[:, 2] * cos_t
order_rot = np.argsort(z_rot)
ax4.scatter(x_rot[order_rot], dots_pos[order_rot, 1], c=colors[order_rot], s=1.4, edgecolors='none')
ax4.set_aspect('equal')
ax4.set_xlim(220, 804)
ax4.set_ylim(580, 15)
ax4.set_title("30° Perspective: Volumetric Hair Parallax & Facial Curvature", color='white', fontsize=12, fontweight='bold', pad=10)
ax4.axis('off')

# Panel 5: Detail of Hairline Transition into Porcelain Forehead
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor('#070508')
trans_mask = (dots_pos[:, 1] >= 110) & (dots_pos[:, 1] <= 210) & (dots_pos[:, 0] >= 420) & (dots_pos[:, 0] <= 605)
ax5.scatter(dots_pos[trans_mask, 0], dots_pos[trans_mask, 1], c=colors[trans_mask], s=3.5, edgecolors='none')
ax5.set_aspect('equal')
ax5.set_xlim(420, 605)
ax5.set_ylim(210, 110)
ax5.set_title("Seamless Hairline-to-Face Blend (Zero Facet Creases)", color='white', fontsize=12, fontweight='bold', pad=10)
ax5.axis('off')

screenshot_path = os.path.join(ARTIFACT_DIR, "step5_enhanced_hair_and_face.png")
plt.subplots_adjust(left=0.04, right=0.96, top=0.94, bottom=0.04, wspace=0.15, hspace=0.18)
plt.savefig(screenshot_path, dpi=150, facecolor='#060406')
plt.close()
print("Saved comparison screenshot to:", screenshot_path)
