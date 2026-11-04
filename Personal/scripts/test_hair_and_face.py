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

# Multi-scale hair strand enhancement on clay front
blur_fine = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=1.0)
blur_mid = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=3.0)
blur_broad = cv2.GaussianBlur(clay_gray, (0, 0), sigmaX=8.0)

hair_strands_fine = np.clip((blur_fine - blur_mid) * 6.0, -1.0, 1.0)
hair_waves = np.clip((blur_mid - blur_broad) * 5.0, -1.0, 1.0)

# Sobel edges for hair lock boundaries
sx = cv2.Sobel(clay_gray, cv2.CV_32F, 1, 0, ksize=3)
sy = cv2.Sobel(clay_gray, cv2.CV_32F, 0, 1, ksize=3)
edges = np.sqrt(sx**2 + sy**2)

print("Hair strand filters computed successfully.")
print("Fine strand range:", hair_strands_fine.min(), hair_strands_fine.max())
print("Wave range:", hair_waves.min(), hair_waves.max())
print("Edges range:", edges.min(), edges.max())
