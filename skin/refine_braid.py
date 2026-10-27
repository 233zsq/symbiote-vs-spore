# -*- coding: utf-8 -*-
"""在用户微调版 128 皮肤上细化辫子(子像素级): 每节=顶高光/本体/结影, 紫尾渐变, 红绳结收边。"""
import os
import sys
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else r"D:\mcmp\skin\skin\诺谛卡\诺谛卡_128 (1).png"
DST = sys.argv[2] if len(sys.argv) > 2 else r"D:\mcmp\skin\skin\诺谛卡\诺谛卡_128_辫子细化.png"
OUT_DIR = os.path.dirname(DST)
WORK = r"D:\mcmp\skin\out"

PAL = {
    'h': (252, 200, 192), 'H': (242, 164, 158), 'd': (206, 112, 110),
    'K': (178, 150, 205), 'V': (108, 92, 190), 'x': (180, 82, 78),
    'H2': (224, 138, 134), 'T': (44, 74, 68),
}

img = Image.open(SRC).convert("RGBA")
# 保留用户手工微调的 2 像素(肩头辫列/围巾交界)
img.putpixel((43, 40), PAL['H2'] + (255,))
img.putpixel((45, 40), PAL['T'] + (255,))


def put(x, y, ch):
    img.putpixel((x, y), PAL[ch] + (255,))


def seg4(x0, w, y0, kind='pink'):
    """一个辫节(4子行): 顶高光/本体/本体暗/结影"""
    for dx in range(w):
        edge = (dx == 0 or dx == w - 1)
        put(x0 + dx, y0,     'h' if not edge else 'H')
        put(x0 + dx, y0 + 1, 'H' if not edge else 'd')
        put(x0 + dx, y0 + 2, 'H' if not edge else 'd')
        put(x0 + dx, y0 + 3, 'd')


def violet_tip4(x0, w, y0):
    for dx in range(w):
        edge = (dx == 0 or dx == w - 1)
        put(x0 + dx, y0,     'd' if edge else 'K')
        put(x0 + dx, y0 + 1, 'K' if edge else 'V')
        put(x0 + dx, y0 + 2, 'd' if edge else 'V')
        put(x0 + dx, y0 + 3, 'd')


# 1) 头侧辫 (head/right 列4-5 => x8-11, 行3-6 => y22-29), 行7 收边
seg4(8, 4, 22)
seg4(8, 4, 26)
for dx in range(4):
    put(8 + dx, 30, 'd')
    put(8 + dx, 31, 'H' if dx in (1, 2) else 'd')

# 2) 身侧辫 (jacket/right 列2-3 => x36-39, 行0-3 => y72-79), 行4-5 紫尾
seg4(36, 4, 72)
seg4(36, 4, 76)
violet_tip4(36, 4, 80)

# 3) 胸前辫 (jacket/front 列1 => x42-43, 行1-4 => y74-81), 行5 红绳结
for y0, top, bot in ((74, 'h', 'H'), (76, 'H', 'd'), (78, 'h', 'H')):
    put(42, y0, top); put(43, y0, top)
    put(42, y0 + 1, bot); put(43, y0 + 1, bot)
put(42, 80, 'K'); put(43, 80, 'K')
put(42, 81, 'V'); put(43, 81, 'V')
put(42, 82, 'x'); put(43, 82, 'x')
put(42, 83, 'd'); put(43, 83, 'd')

os.makedirs(OUT_DIR, exist_ok=True)
img.save(DST)
img.save(os.path.join(WORK, "诺谛卡_皮肤_128_辫子细化.png"))

# 辫子区域放大对比图 (before/after)
before = Image.open(SRC).convert("RGBA")
zones = [(0, 16, 16, 32, 'head/right braid'), (32, 68, 48, 88, 'jacket/right braid'),
         (40, 70, 56, 90, 'jacket/front braid')]
S = 12
PAD = 16
W = sum((z[2] - z[0]) * S for z in zones) * 2 + PAD * (len(zones) * 2 + 1)
H = max((z[3] - z[1]) for z in zones) * S + PAD * 2 + 30
from PIL import ImageDraw
sheet = Image.new("RGBA", (W, H), (32, 34, 42, 255))
d = ImageDraw.Draw(sheet)
d.text((PAD, 8), "braid refine: each zone LEFT=before RIGHT=after", fill=(232, 234, 242, 255))
x = PAD
for x0, y0, x1, y1, name in zones:
    for im in (before, img):
        crop = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.NEAREST)
        bg = Image.new("RGBA", crop.size, (255, 255, 255, 255))
        bd = ImageDraw.Draw(bg)
        for yy in range(0, crop.height, S * 2):
            for xx in range(0, crop.width, S * 2):
                bd.rectangle([xx, yy, xx + S - 1, yy + S - 1], fill=(212, 212, 220, 255))
                bd.rectangle([xx + S, yy + S, xx + 2 * S - 1, yy + 2 * S - 1], fill=(212, 212, 220, 255))
        bg.alpha_composite(crop)
        sheet.alpha_composite(bg, (x, 30))
        x += (x1 - x0) * S + PAD
    d.text((x - 2 * ((x1 - x0) * S) - PAD + 4, H - 18), name, fill=(200, 204, 216, 255))
sheet.convert("RGB").save(os.path.join(OUT_DIR, "诺谛卡_128_辫子细化_对比.jpg"), quality=92)
print("done ->", os.path.join(OUT_DIR, "诺谛卡_128_辫子细化.png"))
