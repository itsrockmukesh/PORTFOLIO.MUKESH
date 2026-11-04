import os
import cv2
import numpy as np
from scipy import ndimage
from skimage import measure
import trimesh
import matplotlib.pyplot as plt

PROCESSED_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal/processed"
ARTIFACT_DIR = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41"
VOXEL_SIZE = 2.5 # px

print("Loading front and side masks for sculpted 3D bust...")
front_mask = cv2.imread(os.path.join(PROCESSED_DIR, "clay_front_mask.png"), cv2.IMREAD_GRAYSCALE) > 0
side_mask = cv2.imread(os.path.join(PROCESSED_DIR, "clay_side_mask.png"), cv2.IMREAD_GRAYSCALE) > 0

f_ys = np.where(front_mask)[0]
s_ys = np.where(side_mask)[0]
y_min = max(f_ys.min(), s_ys.min())
y_max = 854 # Flat base cut

all_y = np.arange(y_min, y_max + 1)
n_rows = len(all_y)

fx_min = np.zeros(n_rows, dtype=float)
fx_max = np.zeros(n_rows, dtype=float)
sz_front = np.zeros(n_rows, dtype=float)
sz_back = np.zeros(n_rows, dtype=float)

for i, y in enumerate(all_y):
    f_cols = np.where(front_mask[y])[0]
    if len(f_cols) > 0:
        fx_min[i] = f_cols.min()
        fx_max[i] = f_cols.max()
    else:
        fx_min[i] = fx_min[i-1] if i > 0 else 600
        fx_max[i] = fx_max[i-1] if i > 0 else 600
        
    s_cols = np.where(side_mask[y])[0]
    if len(s_cols) > 0:
        sz_front[i] = s_cols.min()
        sz_back[i] = s_cols.max()
    else:
        sz_front[i] = sz_front[i-1] if i > 0 else 600
        sz_back[i] = sz_back[i-1] if i > 0 else 600

# 1. Brow to chin: smooth featureless face profile
brow_idx = np.where(all_y == 160)[0][0]
chin_idx = np.where(all_y == 475)[0][0]
face_ys = all_y[brow_idx:chin_idx+1]
poly_face = np.polyfit(face_ys - face_ys[0], sz_front[brow_idx:chin_idx+1], 2)
sz_front[brow_idx:chin_idx+1] = np.polyval(poly_face, face_ys - face_ys[0])

# 2. Chin to collar: smooth monotonic throat slope without notch
collar_idx = np.where(all_y == 610)[0][0]
n_throat = collar_idx - chin_idx
t_throat = np.linspace(0.0, 1.0, n_throat + 1)
z_chin = sz_front[chin_idx]
z_collar = 500.0
sz_front[chin_idx:collar_idx+1] = z_chin + (t_throat**1.5) * (z_collar - z_chin)

# 3. Smooth the head width Rx from cranium to chin using a clean convex head oval
head_ys = np.array([40, 80, 140, 200, 260, 320, 380, 440, 475])
head_ws = np.array([120, 195, 265, 288, 296, 290, 275, 240, 220])
poly_head_w = np.polyfit(head_ys, head_ws, 3)

for i, y in enumerate(all_y):
    if y <= 475:
        w_fit = np.polyval(poly_head_w, y)
        fx_min[i] = 600.5 - w_fit / 2.0
        fx_max[i] = 600.5 + w_fit / 2.0

# 4. Smooth back of head & neck
head_depth_poly = np.polyfit(all_y[:chin_idx+1], sz_back[:chin_idx+1], 3)
sz_back[:chin_idx+1] = np.polyval(head_depth_poly, all_y[:chin_idx+1])

# Smooth all curves along Y with Gaussian filter
sigma_y = 6.0
fx_min_s = ndimage.gaussian_filter1d(fx_min, sigma_y)
fx_max_s = ndimage.gaussian_filter1d(fx_max, sigma_y)
sz_front_s = ndimage.gaussian_filter1d(sz_front, sigma_y)
sz_back_s = ndimage.gaussian_filter1d(sz_back, sigma_y)

xc_arr = (fx_min_s + fx_max_s) / 2.0
rx_arr = (fx_max_s - fx_min_s) / 2.0
zc_arr = (sz_front_s + sz_back_s) / 2.0
rz_arr = (sz_back_s - sz_front_s) / 2.0

rx_arr = np.maximum(rx_arr, 4.0)
rz_arr = np.maximum(rz_arr, 4.0)

# Build voxel grid
x_grid_min = int(np.floor(fx_min_s.min() - 15))
x_grid_max = int(np.ceil(fx_max_s.max() + 15))
z_grid_min = int(np.floor(sz_front_s.min() - 15))
z_grid_max = int(np.ceil(sz_back_s.max() + 15))

y_coords = np.arange(y_min - 5, y_max + 6, VOXEL_SIZE)
x_coords = np.arange(x_grid_min, x_grid_max, VOXEL_SIZE)
z_coords = np.arange(z_grid_min, z_grid_max, VOXEL_SIZE)

ny = len(y_coords)
nx = len(x_coords)
nz = len(z_coords)

print(f"Carving voxel grid: {ny}x{nx}x{nz} voxels ({ny*nx*nz/1e6:.2f}M)")
vol = np.full((ny, nx, nz), -1.0, dtype=np.float32)

XX, ZZ = np.meshgrid(x_coords, z_coords, indexing='ij')

for iy, y_val in enumerate(y_coords):
    if y_val < y_min or y_val > y_max:
        vol[iy, :, :] = -1.0
        continue
    
    idx = np.clip(np.searchsorted(all_y, y_val), 0, n_rows - 1)
    xc, rx = xc_arr[idx], rx_arr[idx]
    zc, rz = zc_arr[idx], rz_arr[idx]
    
    dx = (XX - xc) / rx
    dz = (ZZ - zc) / rz
    val = 1.0 - (dx**2 + dz**2)
    
    if y_val > y_max - VOXEL_SIZE:
        base_fade = (y_max - y_val) / VOXEL_SIZE
        val = np.minimum(val, base_fade)
        
    vol[iy, :, :] = val

print("Smoothing 3D voxel volume with Gaussian filter (sigma=1.2)...")
vol_smoothed = ndimage.gaussian_filter(vol, sigma=1.2)

print("Extracting surface mesh with Marching Cubes...")
verts_vox, faces, normals, _ = measure.marching_cubes(vol_smoothed, level=0.0)

# Convert to world coordinates
verts_world = np.zeros_like(verts_vox)
verts_world[:, 0] = x_coords[0] + verts_vox[:, 1] * VOXEL_SIZE # X
verts_world[:, 1] = y_coords[0] + verts_vox[:, 0] * VOXEL_SIZE # Y
verts_world[:, 2] = z_coords[0] + verts_vox[:, 2] * VOXEL_SIZE # Z

mesh = trimesh.Trimesh(vertices=verts_world, faces=faces, process=True)
mesh.fix_normals()

# Export OBJ and PLY
mesh.export(os.path.join(PROCESSED_DIR, "bust_mesh.obj"))
mesh.export(os.path.join(PROCESSED_DIR, "bust_mesh.ply"))
print(f"Exported refined mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

# Software renderer for shaded views
def render_shaded_mesh(mesh, angle_deg, img_size=(750, 650)):
    theta = np.radians(angle_deg)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    
    v = mesh.vertices.copy()
    vn = mesh.vertex_normals.copy()
    
    cx = 600.0
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
    
    l_rim = np.array([0.0, -0.70, 0.70])
    l_rim /= np.linalg.norm(l_rim)
    
    h, w = img_size
    img = np.ones((h, w, 3), dtype=np.float32) * 0.94
    z_buf = np.full((h, w), 1e9, dtype=np.float32)
    
    scale = (h - 70) / (y_max - y_min)
    screen_x = (x_rot * scale + w / 2.0).astype(int)
    screen_y = ((y_rot - y_min) * scale + 35).astype(int)
    
    rot_normals = np.column_stack([nx_rot, ny_rot, nz_rot])
    diff_key = np.maximum(0.0, np.dot(rot_normals, l_key))
    diff_fill = np.maximum(0.0, np.dot(rot_normals, l_fill))
    diff_rim = np.maximum(0.0, np.dot(rot_normals, l_rim))
    
    view_dir = np.array([0.0, 0.0, -1.0])
    half_vec = (l_key + view_dir)
    half_vec /= np.linalg.norm(half_vec)
    spec = np.maximum(0.0, np.dot(rot_normals, half_vec)) ** 12
    
    ambient = 0.28
    shading = ambient + 0.55 * diff_key + 0.18 * diff_fill + 0.12 * diff_rim + 0.12 * spec
    shading = np.clip(shading, 0.0, 1.0)
    
    valid = (screen_x >= 0) & (screen_x < w) & (screen_y >= 0) & (screen_y < h)
    
    for idx in np.where(valid)[0]:
        sx, sy = screen_x[idx], screen_y[idx]
        sz = z_rot[idx]
        sh = shading[idx]
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                px, py = sx + dx, sy + dy
                if 0 <= px < w and 0 <= py < h:
                    if sz < z_buf[py, px]:
                        z_buf[py, px] = sz
                        img[py, px] = [sh * 0.84, sh * 0.82, sh * 0.80]
                        
    img = cv2.GaussianBlur(img, (3, 3), 0.5)
    return img

print("Rendering shaded views (front 0°, perspective 30°, side profile 90°)...")
img_front = render_shaded_mesh(mesh, 0)
img_30deg = render_shaded_mesh(mesh, 30)
img_side = render_shaded_mesh(mesh, 90)

fig, axes = plt.subplots(1, 3, figsize=(18, 8))
axes[0].imshow(img_front)
axes[0].set_title("Front View (0° Yaw)\nSmooth Oval Face, No Ledges", fontsize=14, fontweight='bold')
axes[0].axis('off')

axes[1].imshow(img_30deg)
axes[1].set_title("30° Perspective View\nContinuous Curvature & Sculpted Trapezius", fontsize=14, fontweight='bold')
axes[1].axis('off')

axes[2].imshow(img_side)
axes[2].set_title("Side Profile View (90° Yaw)\nSmooth Brow-to-Chin & Sloped Submental Neck", fontsize=14, fontweight='bold')
axes[2].axis('off')

screenshot_path = os.path.join(ARTIFACT_DIR, "step3_mesh_views.png")
plt.tight_layout()
plt.savefig(screenshot_path, dpi=150, bbox_inches='tight')
plt.close()
print("Saved Step 3 mesh screenshot to:", screenshot_path)
