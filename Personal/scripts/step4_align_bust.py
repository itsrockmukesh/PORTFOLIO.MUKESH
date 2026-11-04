import os
import cv2
import numpy as np
from scipy import ndimage
from scipy.optimize import minimize
import trimesh
import matplotlib.pyplot as plt

PROCESSED_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/processed"
ARTIFACT_DIR = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41"

print("Loading photo cutout and bust mesh...")
photo_rgba = cv2.imread(os.path.join(PROCESSED_DIR, "photo_cutout.png"), cv2.IMREAD_UNCHANGED)
photo_rgb = cv2.cvtColor(photo_rgba[:, :, :3], cv2.COLOR_BGR2RGB)
photo_alpha = photo_rgba[:, :, 3] > 64
ph_h, ph_w = photo_alpha.shape # 576 x 1024

mesh = trimesh.load(os.path.join(PROCESSED_DIR, "bust_mesh.obj"))
v_orig = mesh.vertices.copy()
faces = mesh.faces.copy()

# Step 4.1: Optimize head alignment (scale and translation) to maximize outline overlap
head_idx = np.where(v_orig[:, 1] <= 475)[0]
v_head = v_orig[head_idx]

v_hx = v_head[:, 0] - 600.5
v_hy = v_head[:, 1] - 28.7

photo_head = np.zeros_like(photo_alpha)
photo_head[:345, :] = photo_alpha[:345, :]

def eval_head_iou(params):
    sx, sy, tx, ty = params
    px = np.round(v_hx * sx + tx).astype(int)
    py = np.round(v_hy * sy + ty).astype(int)
    valid = (px >= 0) & (px < ph_w) & (py >= 0) & (py < 345)
    mask = np.zeros((345, ph_w), dtype=np.uint8)
    mask[py[valid], px[valid]] = 1
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    inter = np.logical_and(mask, photo_head[:345, :]).sum()
    union = np.logical_or(mask, photo_head[:345, :]).sum()
    return -inter / (union + 1e-6)

print("Optimizing head scale and position...")
res = minimize(eval_head_iou, [0.8056, 0.7107, 513.0, 24.5], method='Nelder-Mead', options={'maxiter': 250})
sx_opt, sy_opt, tx_opt, ty_opt = res.x
best_iou = -res.fun
print(f"Optimal Head Alignment: sx={sx_opt:.4f}, sy={sy_opt:.4f}, tx={tx_opt:.2f}, ty={ty_opt:.2f}, IoU={best_iou:.3f}")

# Step 4.2: Transform entire mesh by optimal head transformation
v_aligned = np.zeros_like(v_orig)
v_aligned[:, 0] = (v_orig[:, 0] - 600.5) * sx_opt + tx_opt
v_aligned[:, 1] = (v_orig[:, 1] - 28.7) * sy_opt + ty_opt
sz_opt = (sx_opt + sy_opt) / 2.0
cz_mesh = np.mean(v_orig[:, 2])
v_aligned[:, 2] = (v_orig[:, 2] - cz_mesh) * sz_opt

# Step 4.3: Stretch shoulders to match photo shoulder width
print("Stretching shoulders to match photo silhouette width...")
chin_y = 340.0
max_y = float(ph_h)

# Compute shoulder width stretch profile for y in [chin_y, max_y]
y_samples = np.arange(int(chin_y), ph_h + 1)
stretch_ratios = np.ones(len(y_samples), dtype=float)

for i, y_val in enumerate(y_samples):
    p_cols = np.where(photo_alpha[min(y_val, ph_h - 1)])[0]
    if len(p_cols) == 0:
        continue
    p_w = p_cols.max() - p_cols.min()
    
    # Mesh vertices near y_val
    near = np.abs(v_aligned[:, 1] - y_val) < 6.0
    if near.any():
        m_w = v_aligned[near, 0].max() - v_aligned[near, 0].min()
        if m_w > 10.0:
            stretch_ratios[i] = p_w / m_w

# Smooth stretch profile and ensure smooth transition from 1.0 at chin
stretch_ratios[0] = 1.0
stretch_s = ndimage.gaussian_filter1d(stretch_ratios, sigma=12.0)
stretch_s[0] = 1.0 # Guarantee 1.0 at chin

# Apply shoulder stretch to all vertices below chin
for iv in range(len(v_aligned)):
    vy = v_aligned[iv, 1]
    if vy > chin_y:
        idx = int(np.clip(vy - chin_y, 0, len(stretch_s) - 1))
        scale_x = stretch_s[idx]
        # Smooth ramp from 1.0 at chin
        t = np.clip((vy - chin_y) / 60.0, 0.0, 1.0)
        eff_scale = 1.0 + t * (scale_x - 1.0)
        v_aligned[iv, 0] = tx_opt + (v_aligned[iv, 0] - tx_opt) * eff_scale

# Create aligned mesh
aligned_mesh = trimesh.Trimesh(vertices=v_aligned, faces=faces, process=True)
aligned_mesh.fix_normals()

# Export aligned mesh
aligned_obj_path = os.path.join(PROCESSED_DIR, "bust_aligned.obj")
aligned_ply_path = os.path.join(PROCESSED_DIR, "bust_aligned.ply")
aligned_mesh.export(aligned_obj_path)
aligned_mesh.export(aligned_ply_path)
print(f"Exported aligned mesh: {len(aligned_mesh.vertices)} vertices")

# Render multi-panel alignment verification
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
plt.subplots_adjust(wspace=0.06, hspace=0.10)

# Panel 1: Photo Cutout
axes[0, 0].imshow(photo_rgb)
axes[0, 0].set_title("Target: Photo (1024x576)", fontsize=13, fontweight='bold')
axes[0, 0].axis('off')

# Panel 2: Mesh Silhouette over Photo
overlay = photo_rgb.copy()
# Rasterize aligned mesh outline
proj_pts = aligned_mesh.vertices[:, :2].astype(int)
valid = (proj_pts[:, 0] >= 0) & (proj_pts[:, 0] < ph_w) & (proj_pts[:, 1] >= 0) & (proj_pts[:, 1] < ph_h)
mesh_mask = np.zeros((ph_h, ph_w), dtype=np.uint8)
mesh_mask[proj_pts[valid, 1], proj_pts[valid, 0]] = 255
mesh_mask = cv2.dilate(mesh_mask, np.ones((5, 5), np.uint8))
mesh_mask = ndimage.binary_fill_holes(mesh_mask).astype(np.uint8) * 255

# Outline contour in vibrant cyan
contours, _ = cv2.findContours(mesh_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(overlay, contours, -1, (0, 255, 255), 2)

axes[0, 1].imshow(overlay)
axes[0, 1].set_title(f"Aligned Bust Outline on Photo\nHead IoU = {best_iou*100:.1f}% | Shoulders Stretched to Width", fontsize=13, fontweight='bold')
axes[0, 1].axis('off')

# Panel 3: Front Shaded Render of Aligned Bust
def render_aligned_shaded(mesh, angle_deg=0):
    theta = np.radians(angle_deg)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    
    v = mesh.vertices.copy()
    vn = mesh.vertex_normals.copy()
    
    cx = tx_opt
    cz = np.mean(v[:, 2])
    v[:, 0] -= cx
    v[:, 2] -= cz
    
    x_rot = v[:, 0] * cos_t + v[:, 2] * sin_t
    z_rot = -v[:, 0] * sin_t + v[:, 2] * cos_t
    y_rot = v[:, 1]
    
    nx_rot = vn[:, 0] * cos_t + vn[:, 2] * sin_t
    nz_rot = -vn[:, 0] * sin_t + vn[:, 2] * cos_t
    ny_rot = vn[:, 1]
    
    l_key = np.array([-0.35, -0.45, -0.80])
    l_key /= np.linalg.norm(l_key)
    
    l_fill = np.array([0.60, -0.25, -0.65])
    l_fill /= np.linalg.norm(l_fill)
    
    img = np.ones((ph_h, ph_w, 3), dtype=np.float32) * 0.94
    z_buf = np.full((ph_h, ph_w), 1e9, dtype=np.float32)
    
    sx = (x_rot + cx).astype(int)
    sy = y_rot.astype(int)
    
    rot_normals = np.column_stack([nx_rot, ny_rot, nz_rot])
    diff_key = np.maximum(0.0, np.dot(rot_normals, l_key))
    diff_fill = np.maximum(0.0, np.dot(rot_normals, l_fill))
    
    view_dir = np.array([0.0, 0.0, -1.0])
    half_vec = (l_key + view_dir)
    half_vec /= np.linalg.norm(half_vec)
    spec = np.maximum(0.0, np.dot(rot_normals, half_vec)) ** 12
    
    shading = 0.28 + 0.55 * diff_key + 0.18 * diff_fill + 0.12 * spec
    shading = np.clip(shading, 0.0, 1.0)
    
    valid = (sx >= 0) & (sx < ph_w) & (sy >= 0) & (sy < ph_h)
    
    for idx in np.where(valid)[0]:
        px, py = sx[idx], sy[idx]
        sz = z_rot[idx]
        sh = shading[idx]
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                qx, qy = px + dx, py + dy
                if 0 <= qx < ph_w and 0 <= qy < ph_h:
                    if sz < z_buf[qy, qx]:
                        z_buf[qy, qx] = sz
                        img[qy, qx] = [sh * 0.84, sh * 0.82, sh * 0.80]
                        
    img = cv2.GaussianBlur(img, (3, 3), 0.5)
    return img

img_aligned_front = render_aligned_shaded(aligned_mesh, 0)
axes[1, 0].imshow(img_aligned_front)
axes[1, 0].set_title("Aligned 3D Bust (Front View 0° Yaw)", fontsize=13, fontweight='bold')
axes[1, 0].axis('off')

# Panel 4: 30° Perspective View
img_aligned_30 = render_aligned_shaded(aligned_mesh, 30)
axes[1, 1].imshow(img_aligned_30)
axes[1, 1].set_title("Aligned 3D Bust (30° Perspective View)", fontsize=13, fontweight='bold')
axes[1, 1].axis('off')

screenshot_path = os.path.join(ARTIFACT_DIR, "step4_aligned_bust.png")
plt.tight_layout()
plt.savefig(screenshot_path, dpi=150, bbox_inches='tight')
plt.close()
print("Saved Step 4 screenshot to:", screenshot_path)
