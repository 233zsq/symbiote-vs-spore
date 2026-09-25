# -*- coding: utf-8 -*-
"""Render a 64x64 MC skin onto the standard player model (base + overlay layers),
front and back 3/4 views side by side, like a NameMC-style skin render."""
import math
from PIL import Image

SKIN_PATH = "skin_shinigami.png"
OUT_PATH = "mc_character_render.png"
F = 26                       # px per model unit
SS = 8                       # texture supersample factor

skin = Image.open(SKIN_PATH).convert("RGBA")

# ---------------- perspective helpers ----------------
def solve8(M, b):
    n = 8
    A = [row[:] + [b[i]] for i, row in enumerate(M)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        d = A[col][col]
        A[col] = [v / d for v in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * c for a, c in zip(A[r], A[col])]
    return [A[i][8] for i in range(n)]

def find_coeffs(target, source):
    M, b = [], []
    for (tx, ty), (sx, sy) in zip(target, source):
        M.append([tx, ty, 1, 0, 0, 0, -sx * tx, -sx * ty]); b.append(sx)
        M.append([0, 0, 0, tx, ty, 1, -sy * tx, -sy * ty]); b.append(sy)
    return solve8(M, b)

# ---------------- model ----------------
# coords: +x = character's left, +y = up, +z = front. Units = skin pixels.
PARTS = [
    # name, box(x0,y0,z0,x1,y1,z1), region origin (ox,oy), dims (w,h,d), shade group
    ("head",   (-4, 24, -4, 4, 32, 4),  (0, 0),  (8, 8, 8)),
    ("hat",    (-4.5, 23.5, -4.5, 4.5, 32.5, 4.5), (32, 0), (8, 8, 8)),
    ("body",   (-4, 12, -2, 4, 24, 2),  (16, 16), (8, 12, 4)),
    ("jacket", (-4.5, 11.5, -2.5, 4.5, 24.5, 2.5), (16, 32), (8, 12, 4)),
    ("armR",   (-8, 12, -2, -4, 24, 2), (40, 16), (4, 12, 4)),
    ("armR_ov",(-8.5, 11.5, -2.5, -3.5, 24.5, 2.5), (40, 32), (4, 12, 4)),
    ("armL",   (4, 12, -2, 8, 24, 2),   (32, 48), (4, 12, 4)),
    ("armL_ov",(3.5, 11.5, -2.5, 8.5, 24.5, 2.5), (48, 48), (4, 12, 4)),
    ("legR",   (-4, 0, -2, 0, 12, 2),   (0, 16), (4, 12, 4)),
    ("legR_ov",(-4.5, -0.5, -2.5, 0.5, 12.5, 2.5), (0, 32), (4, 12, 4)),
    ("legL",   (0, 0, -2, 4, 12, 2),    (16, 48), (4, 12, 4)),
    ("legL_ov",(-0.5, -0.5, -2.5, 4.5, 12.5, 2.5), (0, 48), (4, 12, 4)),
]

def face_regions(ox, oy, w, h, d):
    return {
        "top":    (ox + d, oy, w, d),
        "bottom": (ox + d + w, oy, w, d),
        "right":  (ox, oy + d, d, h),          # character's right (-x)
        "front":  (ox + d, oy + d, w, h),      # +z
        "left":   (ox + d + w, oy + d, d, h),  # +x
        "back":   (ox + d + 2 * w, oy + d, w, h),
    }

def face_corners(face, x0, y0, z0, x1, y1, z1):
    # returns [TL, TR, BR, BL] matching texture orientation
    if face == "front":  return [(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)]
    if face == "back":   return [(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)]
    if face == "right":  return [(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)]
    if face == "left":   return [(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)]
    if face == "top":    return [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]
    if face == "bottom": return [(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)]

FACE_NORMAL = {
    "front": (0,0,1), "back": (0,0,-1), "right": (-1,0,0),
    "left": (1,0,0), "top": (0,1,0), "bottom": (0,-1,0),
}
SHADE = {"top": 1.0, "bottom": 0.55, "front": 0.92, "back": 0.85, "left": 0.72, "right": 0.78}

def rot(point, az, el):
    x, y, z = point
    ca, sa = math.cos(az), math.sin(az)
    x, z = x * ca + z * sa, -x * sa + z * ca     # yaw
    ce, se = math.cos(el), math.sin(el)
    y, z = y * ce - z * se, y * se + z * ce      # pitch (viewer above)
    return x, y, z

def render_figure(az_deg, el_deg=18):
    az, el = math.radians(az_deg), math.radians(el_deg)
    W, H = 22 * F, 35 * F
    cx, cy = W / 2, H - 2.5 * F    # model y=0 (feet) near bottom of canvas
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    quads = []
    for name, box, (ox, oy), (w, h, d) in PARTS:
        x0, y0, z0, x1, y1, z1 = box
        regions = face_regions(ox, oy, w, h, d)
        for face in ("top", "bottom", "front", "back", "left", "right"):
            n = rot(FACE_NORMAL[face], az, el)
            if n[2] <= 1e-6:
                continue
            pts3 = face_corners(face, x0, y0, z0, x1, y1, z1)
            pts = [rot(p, az, el) for p in pts3]
            depth = sum(p[2] for p in pts) / 4
            quad = [(cx + p[0] * F, cy - p[1] * F) for p in pts]
            rx, ry, rw, rh = regions[face]
            quads.append((depth, quad, (rx, ry, rw, rh), SHADE[face]))
    quads.sort(key=lambda q: q[0])
    for depth, quad, (rx, ry, rw, rh), shade in quads:
        tex = skin.crop((rx, ry, rx + rw, ry + rh)).resize((rw * SS, rh * SS), Image.NEAREST)
        if shade < 1.0:
            r_, g_, b_, a_ = tex.split()
            dark = Image.merge("RGB", (r_, g_, b_)).point(lambda v: int(v * shade))
            tex = Image.merge("RGBA", (*dark.split(), a_))
        src = [(0, 0), (rw * SS, 0), (rw * SS, rh * SS), (0, rh * SS)]
        coeffs = find_coeffs(quad, src)
        warped = tex.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
        canvas.alpha_composite(warped)
    return canvas

front = render_figure(-30)
back = render_figure(150)

BG = (43, 13, 16, 255)
gap = 6 * F
out = Image.new("RGBA", (front.width * 2 + gap, front.height), BG)
out.alpha_composite(front, (0, 0))
out.alpha_composite(back, (front.width + gap, 0))
out.save(OUT_PATH)
print("saved", OUT_PATH, out.size)
