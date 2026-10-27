# -*- coding: utf-8 -*-
"""把皮肤贴图 + 渲染合成到一张带边框的检查图上，便于核对。"""
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")

skin = Image.open(os.path.join(OUT, "贝丽儿_皮肤.png")).convert("RGBA")
prev = Image.open(os.path.join(OUT, "贝丽儿_预览.png")).convert("RGBA")

FLAT = 8
flat = skin.resize((64 * FLAT, 64 * FLAT), Image.NEAREST)

# 棋盘格底，方便看透明区
board = Image.new("RGBA", flat.size, (255, 255, 255, 255))
bd = ImageDraw.Draw(board)
for y in range(0, 64 * FLAT, FLAT * 2):
    for x in range(0, 64 * FLAT, FLAT * 2):
        bd.rectangle([x, y, x + FLAT - 1, y + FLAT - 1], fill=(214, 214, 222, 255))
        bd.rectangle([x + FLAT, y + FLAT, x + 2 * FLAT - 1, y + 2 * FLAT - 1], fill=(214, 214, 222, 255))
board.alpha_composite(flat)

PAD = 26
BORD = 8
W = max(board.width, prev.width) + PAD * 2 + BORD * 2
H = board.height + prev.height + PAD * 3 + BORD * 2 + 40
sheet = Image.new("RGBA", (W, H), (30, 32, 40, 255))
d = ImageDraw.Draw(sheet)

d.rectangle([0, 0, W - 1, H - 1], outline=(120, 130, 160, 255), width=BORD)
d.text((PAD, 12), "SKIN 64x64  (left=player's right side)", fill=(230, 232, 240, 255))

x0 = (W - board.width) // 2
sheet.alpha_composite(board, (x0, 34))
y1 = 34 + board.height + PAD
d.text((PAD, y1 - 22), "RENDER", fill=(230, 232, 240, 255))
sheet.alpha_composite(prev, ((W - prev.width) // 2, y1))

p = os.path.join(OUT, "check.jpg")
sheet.convert("RGB").save(p, quality=94)
print("report ->", p, sheet.size)
