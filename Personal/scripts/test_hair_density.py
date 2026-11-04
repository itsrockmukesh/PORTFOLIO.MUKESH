import os
import cv2
import numpy as np
import trimesh

PROCESSED_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/processed"
mesh = trimesh.load(os.path.join(PROCESSED_DIR, "bust_aligned.obj"))
mesh.fix_normals()

# Identify hair faces
f_centers = mesh.triangles_center
hair_face_mask = (
    (f_centers[:, 1] < 165) |
    ((f_centers[:, 1] >= 165) & (f_centers[:, 1] < 240) & ((f_centers[:, 0] < 450) | (f_centers[:, 0] > 575))) |
    ((f_centers[:, 1] < 265) & (f_centers[:, 2] > 15))
)

print(f"Hair faces: {hair_face_mask.sum()} / {len(mesh.faces)}")

# Sample base mesh
cand_base, f_idx_base = trimesh.sample.sample_surface_even(mesh, 110000)

# Create a submesh for hair to sample dense hair points
hair_mesh = mesh.submesh([hair_face_mask], append=True)
cand_hair, f_idx_hair = trimesh.sample.sample_surface_even(hair_mesh, 35000)

print(f"Base candidate points: {len(cand_base)}")
print(f"Dense hair candidate points: {len(cand_hair)}")
