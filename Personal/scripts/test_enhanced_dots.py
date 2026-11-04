import os
import cv2
import numpy as np
from scipy import ndimage
import trimesh
import matplotlib.pyplot as plt

PROCESSED_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/processed"
mesh = trimesh.load(os.path.join(PROCESSED_DIR, "bust_aligned.obj"))
mesh.fix_normals()

# Load clay front
clay_front = cv2.imread(os.path.join(PROCESSED_DIR, "clay_front_1200x896.png"))
clay_gray = cv2.cvtColor(clay_front, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
cf_h, cf_w = clay_gray.shape

# Alignment transform:
sx_opt, sy_opt, tx_opt, ty_opt = 0.8089, 0.7106, 513.0, 24.59

# Precompute hair strand and wave maps
blur_fine = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=0.9)
blur_mid = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=2.5)
blur_broad = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=7.0)

hair_strands = np.clip((blur_fine - blur_mid) * 7.5, -1.0, 1.0)
hair_waves = np.clip((blur_mid - blur_broad) * 5.0, -1.0, 1.0)

sx = cv2.Sobel(clay_gray, cv2.CV_32F, 1, 0, ksize=3)
sy = cv2.Sobel(clay_gray, cv2.CV_32F, 0, 1, ksize=3)
edges = np.sqrt(sx**2 + sy**2)

# Base clay detail for shirt / neck / ears
local_contrast = blur_fine - blur_broad
clay_base = (
    0.35 * (1.0 - clay_gray) +
    0.45 * np.clip(local_contrast * 4.0 + 0.4, 0.0, 1.0) +
    0.30 * np.clip(edges * 5.0, 0.0, 1.0)
)
clay_base = 0.15 + 0.80 * ((clay_base - clay_base.min()) / (clay_base.max() - clay_base.min() + 1e-6))

# Sample candidate points:
# We sample 150,000 points over the entire mesh
print("Sampling candidate points...")
candidates, face_indices = trimesh.sample.sample_surface_even(mesh, 150000)
n_cand = len(candidates)
print(f"Sampled {n_cand} candidate points")

# Barycentric normal interpolation
f_verts = mesh.vertices[mesh.faces[face_indices]]
f_norms = mesh.vertex_normals[mesh.faces[face_indices]]

v0, v1, v2 = f_verts[:, 0], f_verts[:, 1], f_verts[:, 2]
v0v1 = v1 - v0
v0v2 = v2 - v0
pv0 = candidates - v0

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

cand_normals = (
    u[:, None] * f_norms[:, 0] +
    v[:, None] * f_norms[:, 1] +
    w[:, None] * f_norms[:, 2]
)
cand_normals /= (np.linalg.norm(cand_normals, axis=1, keepdims=True) + 1e-8)

# Map to clay space
clay_x = np.clip(np.round(600.5 + (candidates[:, 0] - tx_opt) / sx_opt).astype(int), 0, cf_w - 1)
clay_y = np.clip(np.round(28.7 + (candidates[:, 1] - ty_opt) / sy_opt).astype(int), 0, cf_h - 1)

# Base brightness
cand_bright = clay_base[clay_y, clay_x]

# Hair region identification:
# In photo coordinates:
# Cranium/crown/top: y < 165
# Temples/fade/sides: y in [135, 240] and x not in [455, 570]
# Back of head: y < 265 and z > 15
is_top_hair = candidates[:, 1] < 160
is_side_hair = (candidates[:, 1] >= 140) & (candidates[:, 1] < 240) & ((candidates[:, 0] < 452) | (candidates[:, 0] > 574))
is_back_hair = (candidates[:, 1] < 265) & (candidates[:, 2] > 15)
is_hair = is_top_hair | is_side_hair | is_back_hair

print(f"Candidate dots in hair region: {is_hair.sum()} ({is_hair.sum()/n_cand*100:.1f}%)")

# HAIR ENHANCEMENT:
# In hair region, sample strand textures & wave height
c_strands = hair_strands[clay_y, clay_x]
c_waves = hair_waves[clay_y, clay_x]
c_edges = edges[clay_y, clay_x]

# Hair brightness: rich contrast between hair locks and strand highlights
hair_val = (
    0.42 + 
    0.32 * np.clip(c_strands * 1.5, -0.4, 1.0) +
    0.22 * np.clip(c_waves * 1.2, -0.4, 0.8) +
    0.20 * np.clip(c_edges * 1.8, 0.0, 1.0)
)
hair_val = np.clip(hair_val, 0.28, 0.98)

# Apply hair brightness to hair region with soft blend at hairline
hair_blend = np.where(is_hair, 1.0, 0.0)
cand_bright = np.where(is_hair, hair_val, cand_bright)

# Volumetric hair loft / strand displacement along normal:
# Add 3D wave loft to hair dots
hair_loft = np.zeros_like(candidates)
hair_loft_dist = np.clip(0.8 + 2.4 * c_waves + 1.6 * c_strands, -1.0, 4.5)
hair_loft[is_hair] = cand_normals[is_hair] * hair_loft_dist[is_hair, None]
candidates_adj = candidates + hair_loft

# FACE BEAUTIFICATION:
# Face oval:
x0, y0 = 512.8, 232.0
ry_face = 95.0
y_rel = (candidates[:, 1] - y0) / ry_face
rx_eff = 72.0 * np.where(y_rel > 0, 1.0 - 0.28 * y_rel, 1.0)
x_rel = (candidates[:, 0] - x0) / rx_eff
dist_face = np.sqrt(x_rel**2 + y_rel**2)

is_front = (cand_normals[:, 2] < -0.15) & (candidates[:, 2] < -15)
face_mask = (dist_face <= 1.0) & is_front

# Soft cubic feather for seamless face transition
t_face = np.clip((1.0 - dist_face) / 0.30, 0.0, 1.0)
w_face = t_face * t_face * (3.0 - 2.0 * t_face)
w_face[~is_front] = 0.0

# 1. Silky porcelain luminance gradient on face:
face_smooth_val = 0.52 + 0.12 * np.clip(1.0 - dist_face**2, 0.0, 1.0)
cand_bright = (1.0 - w_face) * cand_bright + w_face * face_smooth_val

# 2. Perfect analytic smooth dome normals on face:
dx = (candidates[:, 0] - x0) / (72.0**2)
dy = (candidates[:, 1] - y0) / (95.0**2)
dz = (candidates[:, 2] - (-65.0)) / (45.0**2)
smooth_norm = np.stack([dx, dy, dz], axis=-1)
smooth_norm /= (np.linalg.norm(smooth_norm, axis=1, keepdims=True) + 1e-8)
# Ensure smooth_norm points forward (nz < 0)
smooth_norm[:, 2] = -np.abs(smooth_norm[:, 2])

# Blend normals on face
cand_normals_adj = (1.0 - w_face[:, None]) * cand_normals + w_face[:, None] * smooth_norm
cand_normals_adj /= (np.linalg.norm(cand_normals_adj, axis=1, keepdims=True) + 1e-8)

# Ledge dimming: apply ONLY to shoulders and base (y > 380), NOT hair!
upward_component = -cand_normals_adj[:, 1]
dim_factor = np.ones(n_cand, dtype=float)
is_shoulder_ledge = (candidates[:, 1] > 380) & (upward_component > 0.35)
dim_factor[is_shoulder_ledge] = np.clip(1.0 - 1.8 * (upward_component[is_shoulder_ledge] - 0.35), 0.15, 1.0)
cand_bright *= dim_factor

print("Face beautification and hair enhancement computed.")
print(f"Face dots in candidates: {face_mask.sum()} ({face_mask.sum()/n_cand*100:.1f}%)")
