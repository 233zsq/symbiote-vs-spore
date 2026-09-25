# -*- coding: utf-8 -*-
"""Generate a 64x64 Minecraft (Java) skin from the reference image:
white spiky hair, pale face, black robe with white crossed straps and white obi."""
from PIL import Image

HAIR   = (240, 240, 243, 255)
HAIR_D = (212, 212, 221, 255)
HAIR_HI= (252, 252, 255, 255)
SKIN   = (243, 228, 214, 255)
SKIN_SH= (226, 203, 186, 255)
EYE    = (46, 52, 64, 255)
BROW   = (74, 74, 84, 255)
MOUTH  = (200, 160, 140, 255)
BLACK  = (26, 26, 31, 255)
BLACK_D= (15, 15, 19, 255)
BLACK_L= (42, 42, 50, 255)
WHITE  = (232, 232, 236, 255)
WHITE_D= (198, 198, 206, 255)

img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
px = img.load()

def P(x, y, c):
    px[x, y] = c

def rect(x0, y0, w, h, c):
    for yy in range(y0, y0 + h):
        for xx in range(x0, x0 + w):
            px[xx, yy] = c

# ---------------- HEAD (base) ----------------
# front face: x 8-15, y 8-15
rect(8, 8, 8, 8, SKIN)
for x in range(8, 16):            # hair rows 8-9
    P(x, 8, HAIR); P(x, 9, HAIR)
for x in (8, 9, 11, 13, 15):      # jagged bangs row 10
    P(x, 10, HAIR)
P(10, 10, HAIR_D); P(14, 10, HAIR_D)
P(10, 11, BROW); P(13, 11, BROW)  # eyebrows
P(10, 12, EYE);  P(13, 12, EYE)   # eyes
P(12, 14, MOUTH)                  # subtle mouth
for x in range(8, 16):            # chin shading
    P(x, 15, SKIN_SH)

# left side of head: x 16-23 (x=16 borders front face)
rect(16, 8, 8, 8, SKIN)
for x in range(16, 24):
    P(x, 8, HAIR); P(x, 9, HAIR); P(x, 10, HAIR)
for y in range(11, 16):           # back part stays hair
    for x in range(20, 24):
        P(x, y, HAIR)
P(19, 11, HAIR); P(19, 12, HAIR)  # sideburn strand
P(19, 13, HAIR_D)

# right side of head: x 0-7 (x=7 borders front face)
rect(0, 8, 8, 8, SKIN)
for x in range(0, 8):
    P(x, 8, HAIR); P(x, 9, HAIR); P(x, 10, HAIR)
for y in range(11, 16):
    for x in range(0, 4):
        P(x, y, HAIR)
P(4, 11, HAIR); P(4, 12, HAIR)
P(4, 13, HAIR_D)

# top of head: x 8-15, y 0-7 -- spiky white hair
rect(8, 0, 8, 8, HAIR)
for (x, y) in [(9,1),(12,1),(10,3),(13,3),(9,5),(12,5),(14,2),(11,6),(10,0),(13,0)]:
    P(x, y, HAIR_D)
for (x, y) in [(8,0),(11,1),(14,4),(9,3),(12,6)]:
    P(x, y, HAIR_HI)
# bottom of head (neck shadow)
rect(16, 0, 8, 8, SKIN_SH)

# back of head: x 24-31, y 8-15 -- all hair
rect(24, 8, 8, 8, HAIR)
for y in range(10, 15):           # vertical strand shading
    P(26, y, HAIR_D); P(29, y, HAIR_D)
for x in range(24, 32):           # tips slightly darker
    P(x, 15, HAIR_D)

# ---------------- HEAD overlay (hat layer, spiky volume) ----------------
rect(40, 0, 8, 8, HAIR)           # top
for (x, y) in [(41,1),(44,2),(42,4),(45,5),(43,6)]:
    P(x, y, HAIR_HI)
# front: x 40-47, y 8-15
for x in range(40, 48):
    P(x, 8, HAIR); P(x, 9, HAIR)
for x in (40, 42, 45, 47):
    P(x, 10, HAIR)
P(41, 9, HAIR_D); P(44, 9, HAIR_D); P(46, 10, HAIR_D)
# back: x 56-63
for x in range(56, 64):
    P(x, 8, HAIR); P(x, 9, HAIR); P(x, 10, HAIR)
for x in (57, 59, 61, 63):
    P(x, 11, HAIR)
for y in (9, 10):
    P(58, y, HAIR_D); P(60, y, HAIR_D); P(62, y, HAIR_D)
P(57, 8, HAIR_D); P(61, 8, HAIR_D)
# left: x 48-55
for x in range(48, 56):
    P(x, 8, HAIR); P(x, 9, HAIR)
for x in (49, 51, 54):
    P(x, 10, HAIR)
P(50, 9, HAIR_D); P(53, 9, HAIR_D); P(52, 8, HAIR_D)
# right: x 32-39
for x in range(32, 40):
    P(x, 8, HAIR); P(x, 9, HAIR)
for x in (33, 35, 38):
    P(x, 10, HAIR)
P(34, 9, HAIR_D); P(37, 9, HAIR_D); P(36, 8, HAIR_D)

# ---------------- BODY (base) ----------------
# front: x 20-27, y 20-31
rect(20, 20, 8, 12, BLACK)
for y in range(20, 28):           # side shading first
    P(20, y, BLACK_D); P(27, y, BLACK_D)
for i in range(8):                # white X straps (2px wide diagonals)
    for dx in (0, 1):
        if 20 + i + dx <= 27:
            P(20 + i + dx, 20 + i, WHITE)
        if 27 - i - dx >= 20:
            P(27 - i - dx, 20 + i, WHITE)
for x in range(20, 28):           # white obi belt
    P(x, 28, WHITE); P(x, 29, WHITE_D)
P(23, 29, WHITE); P(24, 29, WHITE)  # knot highlight
P(23, 30, WHITE); P(24, 30, WHITE)  # knot
P(21, 30, BLACK_L); P(24, 31, BLACK_L)

# back: x 32-39, y 20-31
rect(32, 20, 8, 12, BLACK)
for x in range(32, 40):
    P(x, 28, WHITE); P(x, 29, WHITE_D)
for y in range(22, 28):           # fold shading
    P(34, y, BLACK_D); P(37, y, BLACK_D)
P(35, 30, BLACK_L); P(36, 31, BLACK_L)

# right side: x 16-19 / left side: x 28-31
for x0 in (16, 28):
    rect(x0, 20, 4, 12, BLACK)
    for x in range(x0, x0 + 4):
        P(x, 28, WHITE); P(x, 29, WHITE_D)

# top (shoulders): x 20-27, y 16-19
rect(20, 16, 8, 4, BLACK)
for x in (20, 21, 26, 27):        # straps continue over shoulders
    P(x, 18, WHITE); P(x, 19, WHITE)
# bottom
rect(28, 16, 8, 4, BLACK_D)

# ---------------- BODY overlay (jacket: belt + hanging sash) ----------------
for x0, w in ((20, 8), (32, 8)):  # front & back belt
    for x in range(x0, x0 + w):
        P(x, 44, WHITE); P(x, 45, WHITE_D)
for x0 in (16, 28):               # sides belt
    for x in range(x0, x0 + 4):
        P(x, 44, WHITE); P(x, 45, WHITE_D)
# hanging white strips on front: x 20-27 -> overlay x 20-27, y 36-47
for y in range(45, 48):
    P(21, y, WHITE); P(22, y, WHITE)
    P(25, y, WHITE); P(26, y, WHITE)
P(22, 47, WHITE_D); P(26, 47, WHITE_D)
# back sash tail
for y in range(45, 47):
    P(35, y, WHITE); P(36, y, WHITE)
P(36, 47, WHITE_D)

# ---------------- ARMS ----------------
def arm(base_x, base_y, ov_x, ov_y):
    # faces: right(+0), front(+4), left(+8), back(+12); each 4 wide, y..y+12
    for fx in (base_x, base_x + 4, base_x + 8, base_x + 12):
        rect(fx, base_y + 4, 4, 12, BLACK)          # sleeve
        rect(fx, base_y + 13, 4, 3, SKIN)           # hand
        for x in range(fx, fx + 4):
            P(x, base_y + 12, BLACK_D)              # cuff line
            P(x, base_y + 15, SKIN_SH)              # hand shading
    rect(base_x + 4, base_y, 4, 4, BLACK)           # top
    rect(base_x + 8, base_y, 4, 4, BLACK_D)         # bottom
    # overlay: puffy sleeve upper half
    for fx in (ov_x, ov_x + 4, ov_x + 8, ov_x + 12):
        rect(fx, ov_y + 4, 4, 8, BLACK)
        for x in range(fx, fx + 4):
            P(x, ov_y + 11, BLACK_D)
    rect(ov_x + 4, ov_y, 4, 4, BLACK)

arm(40, 16, 40, 32)   # right arm
arm(32, 48, 48, 48)   # left arm

# ---------------- LEGS ----------------
def leg(base_x, base_y, ov_x, ov_y, sash):
    for fx in (base_x, base_x + 4, base_x + 8, base_x + 12):
        rect(fx, base_y + 4, 4, 12, BLACK)
        for x in range(fx, fx + 4):
            P(x, base_y + 14, BLACK_D)              # shading
            P(x, base_y + 15, BLACK_D)              # footwear
    rect(base_x + 4, base_y, 4, 4, BLACK)
    rect(base_x + 8, base_y, 4, 4, BLACK_D)
    # overlay: hakama flare, black
    for fx in (ov_x, ov_x + 4, ov_x + 8, ov_x + 12):
        rect(fx, ov_y + 4, 4, 12, BLACK)
        for x in range(fx, fx + 4):
            P(x, ov_y + 15, BLACK_D)
    rect(ov_x + 4, ov_y, 4, 4, BLACK)
    if sash:  # white hanging sash strip continuing down the front
        fx = ov_x + 4
        for y in range(ov_y + 4, ov_y + 10):
            P(fx + 1, y, WHITE); P(fx + 2, y, WHITE)
        P(fx + 2, ov_y + 10, WHITE_D)

leg(0, 16, 0, 32, True)    # right leg
leg(16, 48, 0, 48, True)   # left leg

img.save("skin_shinigami.png")

# ---------------- preview (front / back, x8) ----------------
S = 8
prev = Image.new("RGBA", (48 * S, 32 * S), (60, 60, 66, 255))
def grab(x0, y0, w, h):
    return img.crop((x0, y0, x0 + w, y0 + h)).resize((w * S, h * S), Image.NEAREST)
# front: head(8,8) body(20,20) arms(44,20 & 36,52) legs(4,20 & 20,52)
prev.paste(grab(8, 8, 8, 8),   (12 * S, 0))
prev.paste(grab(20, 20, 8, 12),(12 * S, 8 * S))
prev.paste(grab(44, 20, 4, 12),(8 * S, 8 * S))
prev.paste(grab(36, 52, 4, 12),(20 * S, 8 * S))
prev.paste(grab(4, 20, 4, 12), (12 * S, 20 * S))
prev.paste(grab(20, 52, 4, 12),(16 * S, 20 * S))
# overlay composited on top
ov = Image.new("RGBA", prev.size, (0, 0, 0, 0))
ov.paste(grab(40, 8, 8, 8),   (12 * S, 0))
ov.paste(grab(20, 36, 8, 12), (12 * S, 8 * S))
ov.paste(grab(44, 36, 4, 12), (8 * S, 8 * S))
ov.paste(grab(52, 52, 4, 12), (20 * S, 8 * S))
ov.paste(grab(4, 36, 4, 12),  (12 * S, 20 * S))
ov.paste(grab(4, 52, 4, 12),  (16 * S, 20 * S))
prev.alpha_composite(ov)
# back view at right side
bx = 24 * S
prev.paste(grab(24, 8, 8, 8),   (bx + 4 * S, 0))
prev.paste(grab(32, 20, 8, 12), (bx + 4 * S, 8 * S))
prev.paste(grab(52, 20, 4, 12), (bx + 0 * S, 8 * S))
prev.paste(grab(44, 52, 4, 12), (bx + 12 * S, 8 * S))
prev.paste(grab(12, 20, 4, 12), (bx + 4 * S, 20 * S))
prev.paste(grab(28, 52, 4, 12), (bx + 8 * S, 20 * S))
ov2 = Image.new("RGBA", prev.size, (0, 0, 0, 0))
ov2.paste(grab(56, 8, 8, 8),   (bx + 4 * S, 0))
ov2.paste(grab(32, 36, 8, 12), (bx + 4 * S, 8 * S))
ov2.paste(grab(52, 36, 4, 12), (bx + 0 * S, 8 * S))
ov2.paste(grab(60, 52, 4, 12), (bx + 12 * S, 8 * S))
ov2.paste(grab(12, 36, 4, 12), (bx + 4 * S, 20 * S))
ov2.paste(grab(12, 52, 4, 12), (bx + 8 * S, 20 * S))
prev.alpha_composite(ov2)
prev = prev.crop((8 * S, 0, 48 * S, 32 * S))
prev.save("skin_shinigami_preview.png")
print("done: skin_shinigami.png, skin_shinigami_preview.png")
