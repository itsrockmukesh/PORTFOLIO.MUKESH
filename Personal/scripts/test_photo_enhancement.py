import cv2
import numpy as np
import matplotlib.pyplot as plt

photo = cv2.imread("/Users/mukeshkumar/PORTFOLIO/Personal/inputs/photo.png")
h, w, _ = photo.shape

# 1. Inspect alpha and hair region in original cutout
cutout = cv2.imread("/Users/mukeshkumar/PORTFOLIO/Personal/processed/photo_cutout.png", cv2.IMREAD_UNCHANGED)
cur_alpha = cutout[:, :, 3]

# Check hair alpha distribution
hair_y1, hair_y2 = 20, 160
hair_x1, hair_x2 = 380, 640
hair_alpha_crop = cur_alpha[hair_y1:hair_y2, hair_x1:hair_x2]
print(f"Hair alpha min: {hair_alpha_crop.min()}, mean: {hair_alpha_crop.mean():.1f}, max: {hair_alpha_crop.max()}")
print(f"Pixels with alpha < 240 in hair: {(hair_alpha_crop < 240).sum()} / {hair_alpha_crop.size} ({(hair_alpha_crop < 240).mean()*100:.1f}%)")

# Face skin color distribution
face_crop = photo[140:340, 420:600]
hsv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2HSV)
ycrcb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2YCrCb)
print("Face YCrCb Y range:", ycrcb[:,:,0].min(), ycrcb[:,:,0].max())
print("Face YCrCb Cr range:", ycrcb[:,:,1].min(), ycrcb[:,:,1].max())
print("Face YCrCb Cb range:", ycrcb[:,:,2].min(), ycrcb[:,:,2].max())
