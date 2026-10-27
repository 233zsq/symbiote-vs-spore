# -*- coding: utf-8 -*-
"""诺谛卡(原皮) MC 皮肤生成器。
分层: 基础层 = 脸/发/身体/衣袖/腿袜靴; 第二层(overlay) = 飞行帽+护目镜/毛边/腰包粉绳/护膝红标/靴扣。
进化形态借鉴: 发丝蓝紫挑染(v/V)。
脸型风格参考 D:/mcmp/skin/exam 内皮肤。
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

PAL = {
    # 头发(提饱和粉) + 进化借鉴薰衣草/紫罗兰渐变
    'H': (242, 164, 158), 'h': (252, 200, 192), 'd': (206, 112, 110),
    # 进化借鉴: 低饱和薰衣草挑染(融入粉发)
    'v': (122, 123, 224), 'V': (108, 92, 190), 'K': (178, 150, 205),
    # 皮肤
    'S': (247, 228, 218), 's': (230, 200, 187), 'b': (238, 186, 178), 'm': (214, 150, 140),
    # 眼
    'E': (58, 62, 69), 'D': (140, 124, 130), 'W': (252, 252, 250), 'I': (94, 156, 148), 'i': (171, 216, 206),
    # 围巾(墨绿)
    'T': (44, 74, 68), 't': (30, 55, 50),
    # 外套(蓝紫)
    'C': (98, 110, 158), 'c': (84, 96, 142), 'e': (66, 78, 124),
    # 手套(黑)
    'G': (38, 42, 48), 'g': (60, 66, 74),
    # 护目镜(镜片与眼睛同系青灰, 避免与粉发撞色)
    'L': (122, 150, 142), 'l': (176, 208, 198), 'Y': (185, 154, 91),  # Y=黄铜框
    # 毛皮(奶油)
    'F': (239, 230, 214), 'f': (211, 198, 172),
    # 睡袋卷 / 米色 trim
    'R': (220, 205, 174), 'r': (185, 169, 138), 'A': (207, 195, 168), 'a': (179, 167, 140),
    # 皮革
    'P': (107, 74, 46), 'p': (82, 56, 35), 'B': (126, 84, 51), 'y': (92, 61, 38),
    'U': (198, 203, 210),  # 银扣
    # 流苏 / 绳
    'x': (180, 82, 78), 'q': (78, 142, 134), 'Q': (176, 86, 122), 'u': (142, 66, 98),
    # 腿袜 / 护膝 / 靴
    'w': (237, 239, 240), 'n': (211, 216, 219),
    'J': (217, 205, 180), 'j': (190, 177, 152),
    'O': (59, 74, 51), 'o': (44, 56, 38), 'z': (26, 32, 26),
    # 裙(黑)
    'Z': (42, 45, 51),
    # HD(128)专用中间调
    'H1': (247, 182, 175), 'H2': (224, 138, 134), 'N': (214, 184, 122), 'X': (14, 18, 14),
}

# ---------------------------------------------------------------- 面片布局
FACES = {
    'head':   {'top': (8, 0, 8, 8), 'bottom': (16, 0, 8, 8), 'right': (0, 8, 8, 8),
               'front': (8, 8, 8, 8), 'left': (16, 8, 8, 8), 'back': (24, 8, 8, 8)},
    'hat':    {'top': (40, 0, 8, 8), 'bottom': (48, 0, 8, 8), 'right': (32, 8, 8, 8),
               'front': (40, 8, 8, 8), 'left': (48, 8, 8, 8), 'back': (56, 8, 8, 8)},
    'body':   {'top': (20, 16, 8, 4), 'bottom': (28, 16, 8, 4), 'right': (16, 20, 4, 12),
               'front': (20, 20, 8, 12), 'left': (28, 20, 4, 12), 'back': (32, 20, 8, 12)},
    'jacket': {'top': (20, 32, 8, 4), 'bottom': (28, 32, 8, 4), 'right': (16, 36, 4, 12),
               'front': (20, 36, 8, 12), 'left': (28, 36, 4, 12), 'back': (32, 36, 8, 12)},
    'rarm':   {'top': (44, 16, 4, 4), 'bottom': (48, 16, 4, 4), 'right': (40, 20, 4, 12),
               'front': (44, 20, 4, 12), 'left': (48, 20, 4, 12), 'back': (52, 20, 4, 12)},
    'rarm2':  {'top': (44, 32, 4, 4), 'bottom': (48, 32, 4, 4), 'right': (40, 36, 4, 12),
               'front': (44, 36, 4, 12), 'left': (48, 36, 4, 12), 'back': (52, 36, 4, 12)},
    'larm':   {'top': (36, 48, 4, 4), 'bottom': (40, 48, 4, 4), 'right': (32, 52, 4, 12),
               'front': (36, 52, 4, 12), 'left': (40, 52, 4, 12), 'back': (44, 52, 4, 12)},
    'larm2':  {'top': (52, 48, 4, 4), 'bottom': (56, 48, 4, 4), 'right': (48, 52, 4, 12),
               'front': (52, 52, 4, 12), 'left': (56, 52, 4, 12), 'back': (60, 52, 4, 12)},
    'rleg':   {'top': (4, 16, 4, 4), 'bottom': (8, 16, 4, 4), 'right': (0, 20, 4, 12),
               'front': (4, 20, 4, 12), 'left': (8, 20, 4, 12), 'back': (12, 20, 4, 12)},
    'rleg2':  {'top': (4, 32, 4, 4), 'bottom': (8, 32, 4, 4), 'right': (0, 36, 4, 12),
               'front': (4, 36, 4, 12), 'left': (8, 36, 4, 12), 'back': (12, 36, 4, 12)},
    'lleg':   {'top': (20, 48, 4, 4), 'bottom': (24, 48, 4, 4), 'right': (16, 52, 4, 12),
               'front': (20, 52, 4, 12), 'left': (24, 52, 4, 12), 'back': (28, 52, 4, 12)},
    'lleg2':  {'top': (4, 48, 4, 4), 'bottom': (8, 48, 4, 4), 'right': (0, 52, 4, 12),
               'front': (4, 52, 4, 12), 'left': (8, 52, 4, 12), 'back': (12, 52, 4, 12)},
}

# ---------------------------------------------------------------- 像素图
G = {}

G['head/front'] = [
    "HHHHHHHH",
    "llllllll",   # 内层只留镜片
    "LLLLLLLL",
    "dHhHHhKd",   # 刘海(亮尖+暗边+单侧紫尖)
    "dEEhhEEd",   # 深色睫毛+镜间碎发
    "dWISSIWd",   # 深色侧绺框脸
    "dWiSSiWd",
    "HbSSSSbH",   # 无嘴(二次元皮肤惯例)+腮红
]
G['head/right'] = [   # col7 = 前缘; 镜片包边行1-2 + 侧辫
    "hhhhhhhh",
    "HHHHHHHl",
    "dHHHHHHL",
    "dHHdhhHH",
    "dHHdhhHH",
    "dHHdHHHH",
    "dHHdhhHH",
    "dHHdHHHH",   # 辫子粉色到底(接缝连续), 紫尾移到身体段
]
G['head/left'] = [    # col0 = 前缘; 镜片包边行1-2 + 发绺
    "hhhhhhhh",
    "lHHHHHHH",
    "LHHHHHHd",
    "HHhHHHHd",
    "HHhHHHHd",
    "HHhHHHHd",
    "HHKHHHdd",   # 发绺尾渐变紫
    "HHhHHHHd",
]
G['head/back'] = [
    "hhhhhhhh",
    "HHHHHHHH",
    "HHHHHHHH",
    "dHKHHhHd",
    "dHKHHhHd",
    "dHKHHKHd",
    "dKVVVVKd",   # 后颈紫罗兰 undercolor(进化渐变)
    "ddVVVVdd",
]
G['head/top'] = [
    "hhhhhhhh",
    "hhhhhhhh",
    "HHHHHHHH",
    "HHdHHdHH",
    "HHdHHdHH",
    "HHHHHHHH",
    "HHHHHHHH",
    "HHHHHHHH",
]
G['head/bottom'] = [
    "dddddddd",
    "dddddddd",
    "dddddddd",
    "dddddddd",
    "ddssssdd",
    "ddssssdd",
    "ddssssdd",
    "ddssssdd",
]

# ---- 帽子 overlay: 奶油毛帽轮廓(外层) + 镜片高光/框点 + 发丝
G['hat/front'] = [
    "FFFFFFFF",   # 毛帽眉带(轮廓对比)
    "YW.YY.WY",   # 镜框: 外rim+桥接+高光(外层)
    "Y..YY..Y",
    ".d....d.",   # 刘海侧尖(不遮基础层亮尖)
    ".d....d.",
    ".d....d.",
    "d......d",   # 框脸发丝
    "........",
]
G['hat/top'] = [
    "FFFFFFFF",
    "FfFFFFfF",
    "FFFFFFFF",
    "FFfFFfFF",
    "FFFFFFFF",
    "FfFFFFfF",
    "FFFFFFFF",
    "FFfFFfFF",
]
G['hat/right'] = [
    "FFFFFFFF",   # 毛帽侧量
    "FFF....Y",   # 镜框包边
    "FF.....d",
    "Hd..xxxd",   # 蝴蝶结(外层)
    "....x.xd",
    "d......d",
    "H......d",
    "........",
]
G['hat/left'] = [
    "FFFFFFFF",
    "Y....FFF",
    "d.....FF",
    "dxxx..dH",
    "dx.x....",
    "d......d",
    "d......H",
    "........",
]
G['hat/back'] = [
    "FFFFFFFF",   # 毛帽后量
    "FFF..FFF",
    "FF....FF",
    "HH....HH",
    ".H....H.",
    "dH....Hd",
    ".d....d.",
    "..dHHd..",
]

# ---- 身体 base
G['body/front'] = [
    "dhdTTTTF",   # 辫子列在基础层即发色(接缝连续)
    "dHdTTTTc",
    "CCCYYCCC",
    "cCBCCCCc",
    "CCCBCCCC",
    "CCCCBCCC",
    "BBBBBBBB",
    "yyyUUyyy",
    "CCeCCeCC",
    "cCCeeCCc",
    "cCCCCCCc",
    "ZZZZZZZZ",
]
G['body/back'] = [   # 内层: 外套+腰带(书包移外层)
    "cCCCCCCc",
    "cCCCCCCc",
    "CCCCCCCC",
    "CCeCCeCC",
    "CCeCCeCC",
    "cCCCCCCc",
    "BBBBBBBB",
    "yyyUUyyy",
    "CCCCCCCC",
    "cCCCCCCc",
    "cCCCCCCc",
    "ZZZZZZZZ",
]
_side_body = [
    "TTTT", "tTTt", "CCCC", "cCCc", "CCCC", "CeeC",
    "BBBB", "yBBy", "CCCC", "cCCc", "cCCc", "ZZZZ",
]
G['body/right'] = [   # 她右侧: 基础层辫子列发色(接缝连续)
    "TThh",
    "tTHH",
    "CCCC", "cCCc", "CCCC", "CeeC",
    "BBBB", "yBBy", "CCCC", "cCCc", "cCCc", "ZZZZ",
]
G['body/left'] = _side_body
G['body/top'] = ["TTTTTTTT", "tTTTTTTt", "TTTTTTTT", "tTTTTTTt"]
G['body/bottom'] = ["ZZZZZZZZ"] * 4

# ---- 外套 overlay: 毛边下摆 + 腰包 + 粉绳
_jk_front = ["........"] * 12
_jk_front[1] = "dhd....."   # 单侧辫(她右胸), 对侧不连
_jk_front[2] = "dHd....."
_jk_front[3] = "dhd....."
_jk_front[4] = "dKd....."   # 辫尾渐变紫
_jk_front[5] = "dxd....."
_jk_front[6] = ".....PPP"
_jk_front[7] = ".....PpP"
_jk_front[8] = ".....PPP"
_jk_front[9] = "FFFFFFFF"
_jk_front[10] = "fFfFFfFf"
G['jacket/front'] = _jk_front
_jk_back = ["........"] * 12
_jk_back[0] = "HHRRRRHH"   # 书包+睡袋卷(外层), 垂发覆其上
_jk_back[1] = "dHrRRrHd"
_jk_back[2] = "HdBPPBdH"
_jk_back[3] = ".dBppBd."
_jk_back[4] = "PBPPPPBP"
_jk_back[5] = "PPPPPPPP"
_jk_back[6] = "pPPPPPPp"
_jk_back[7] = "PPpPPpPP"
_jk_back[8] = "pPPPPPPp"
_jk_back[9] = "FFFFFFFF"
_jk_back[10] = "fFfFFfFf"
G['jacket/back'] = _jk_back
_jk_r = ["...."] * 12
_jk_r[0] = "..hh"      # 她右侧: 辫子从头连到身
_jk_r[1] = "..HH"
_jk_r[2] = "..hh"
_jk_r[3] = "..HH"
_jk_r[4] = "..KV"      # 辫尾渐变紫
_jk_r[5] = "..dd"
_jk_r[9] = "FFFF"
_jk_r[10] = "fFfF"
G['jacket/right'] = _jk_r
_jk_l = ["...."] * 12
_jk_l[9] = "FFFF"       # 她左侧: 不连发
_jk_l[10] = "fFfF"
G['jacket/left'] = _jk_l

# ---- 手臂 base
_arm = [
    "CCCC", "CeeC", "eCCe", "CeeC", "CCCC", "CCCC",
    "cCCc", "CCCC", "CccC", "GGGG", "GggG", "GGGG",
]
G['rarm/front'] = _arm
G['rarm/back'] = _arm
G['rarm/right'] = _arm
G['rarm/left'] = _arm
G['larm/front'] = _arm
G['larm/back'] = _arm
G['larm/right'] = _arm
G['larm/left'] = _arm
G['rarm/top'] = ["CCCC", "CccC", "CCCC", "CccC"]
G['larm/top'] = ["CCCC", "CccC", "CCCC", "CccC"]
G['rarm/bottom'] = ["GGGG"] * 4
G['larm/bottom'] = ["GGGG"] * 4

# ---- 手臂 overlay: 流苏带 + 毛袖口
_a2 = ["...."] * 12
_a2[0] = "FFFF"       # 肩头毛领(消除硬边+立绘配色)
_a2[5] = "cccc"
_a2[6] = "xxxx"
_a2[7] = "FFFF"
_a2[8] = "fFfF"
for k in ('rarm2/front', 'rarm2/back', 'rarm2/right', 'rarm2/left',
          'larm2/front', 'larm2/back', 'larm2/right', 'larm2/left'):
    G[k] = _a2
G['rarm2/top'] = ["FFFF", "FffF", "FffF", "FFFF"]
G['larm2/top'] = ["FFFF", "FffF", "FffF", "FFFF"]

# ---- 腿 base: 白腿袜 + 护膝 + 墨绿长靴
_leg = [
    "ZggZ", "ZZZZ", "wwww", "wnww", "JJJJ", "JJJJ",
    "AAAA", "OOOO", "OooO", "OOOO", "OooO", "zzzz",
]
for k in ('rleg/front', 'rleg/back', 'rleg/right', 'rleg/left',
          'lleg/front', 'lleg/back', 'lleg/right', 'lleg/left'):
    G[k] = _leg
G['rleg/top'] = ["ZZZZ"] * 4
G['lleg/top'] = ["ZZZZ"] * 4
G['rleg/bottom'] = ["zzzz"] * 4
G['lleg/bottom'] = ["zzzz"] * 4

# ---- 腿 overlay: 护膝红标 + 靴口米色 + 靴带银扣
_l2 = ["...."] * 12
_l2[5] = "JxxJ"
_l2[6] = "aAAa"
_l2[8] = "OUUO"
_l2[10] = "OUUO"
for k in ('rleg2/front', 'rleg2/back', 'rleg2/right', 'rleg2/left',
          'lleg2/front', 'lleg2/back', 'lleg2/right', 'lleg2/left'):
    G[k] = _l2


def build():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for key, rows in G.items():
        part, face = key.split('/')
        x0, y0, w, h = FACES[part][face]
        assert len(rows) == h, (key, len(rows), h)
        for y, row in enumerate(rows):
            assert len(row) == w, (key, y, len(row), w)
            for x, ch in enumerate(row):
                if ch == '.':
                    continue
                r, g, b = PAL[ch]
                img.putpixel((x0 + x, y0 + y), (r, g, b, 255))
    return img


# ---------------------------------------------------------------- 多视图渲染
def face_img(img, part, face):
    x0, y0, w, h = FACES[part][face]
    base = img.crop((x0, y0, x0 + w, y0 + h))
    ov = {
        'head': 'hat', 'body': 'jacket', 'rarm': 'rarm2', 'larm': 'larm2',
        'rleg': 'rleg2', 'lleg': 'lleg2',
    }.get(part)
    if ov:
        ox, oy, ow, oh = FACES[ov][face]
        base = base.copy()
        base.alpha_composite(img.crop((ox, oy, ox + ow, oy + oh)))
    return base


def render_view(img, view, scale=10):
    """view: front/back/right/left -> 24x32 画布"""
    canvas = Image.new("RGBA", (24, 32), (0, 0, 0, 0))
    if view == 'front':
        hf, bf, af, lf = 'front', 'front', 'front', 'front'
        canvas.paste(face_img(img, 'head', hf), (8, 0))
        canvas.paste(face_img(img, 'rarm', af), (4, 8))
        canvas.paste(face_img(img, 'larm', af), (16, 8))
        canvas.paste(face_img(img, 'body', bf), (8, 8))
        canvas.paste(face_img(img, 'rleg', lf), (8, 20))
        canvas.paste(face_img(img, 'lleg', lf), (12, 20))
    elif view == 'back':
        canvas.paste(face_img(img, 'head', 'back'), (8, 0))
        canvas.paste(face_img(img, 'rarm', 'back'), (4, 8))
        canvas.paste(face_img(img, 'larm', 'back'), (16, 8))
        canvas.paste(face_img(img, 'body', 'back'), (8, 8))
        canvas.paste(face_img(img, 'rleg', 'back'), (8, 20))
        canvas.paste(face_img(img, 'lleg', 'back'), (12, 20))
    elif view == 'right':   # 看玩家右侧: 头右面 col7=前
        canvas.paste(face_img(img, 'larm', 'right'), (10, 8))   # 远侧臂
        canvas.paste(face_img(img, 'lleg', 'right'), (10, 20))
        canvas.paste(face_img(img, 'body', 'right'), (10, 8))
        canvas.paste(face_img(img, 'rleg', 'right'), (10, 20))
        canvas.paste(face_img(img, 'rarm', 'right'), (10, 8))
        canvas.paste(face_img(img, 'head', 'right'), (8, 0))
    elif view == 'left':
        canvas.paste(face_img(img, 'rarm', 'left'), (10, 8))
        canvas.paste(face_img(img, 'rleg', 'left'), (10, 20))
        canvas.paste(face_img(img, 'body', 'left'), (10, 8))
        canvas.paste(face_img(img, 'lleg', 'left'), (10, 20))
        canvas.paste(face_img(img, 'larm', 'left'), (10, 8))
        canvas.paste(face_img(img, 'head', 'left'), (8, 0))
    return canvas.resize((24 * scale, 32 * scale), Image.NEAREST)


def checker(im, cell):
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    from PIL import ImageDraw
    d = ImageDraw.Draw(bg)
    for y in range(0, im.height, cell * 2):
        for x in range(0, im.width, cell * 2):
            d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(212, 212, 220, 255))
            d.rectangle([x + cell, y + cell, x + 2 * cell - 1, y + 2 * cell - 1], fill=(212, 212, 220, 255))
    bg.alpha_composite(im)
    return bg


def make_sheet(img, path, scale=10):
    from PIL import ImageDraw
    views = ['front', 'right', 'back', 'left']
    renders = [render_view(img, v, scale) for v in views]
    head = face_img(img, 'head', 'front').resize((8 * scale * 2, 8 * scale * 2), Image.NEAREST)
    flat = checker(img.resize((64 * 8, 64 * 8), Image.NEAREST), 8)
    PAD = 24
    vw = renders[0].width
    top_w = vw * 4 + PAD * 5
    bot_h = max(head.height, 0)
    W = max(top_w, flat.width + PAD * 2)
    H = PAD * 4 + renders[0].height + head.height + flat.height + 60
    sheet = Image.new("RGBA", (W, H), (32, 34, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W - 1, H - 1], outline=(120, 130, 160, 255), width=6)
    d.text((PAD, 10), "NORDICA  multi-view  (front / right / back / left)", fill=(232, 234, 242, 255))
    x = PAD
    for v, r in zip(views, renders):
        sheet.alpha_composite(checker(r, scale), (x, 34))
        d.text((x + 4, 34 + r.height + 6), v, fill=(200, 204, 216, 255))
        x += vw + PAD
    y1 = 34 + renders[0].height + PAD + 16
    d.text((PAD, y1 - 18), "HEAD FRONT x2", fill=(232, 234, 242, 255))
    sheet.alpha_composite(checker(head, scale * 2), (PAD, y1))
    y2 = y1 + head.height + PAD
    d.text((PAD, y2 - 18), "TEXTURE 64x64 x8", fill=(232, 234, 242, 255))
    sheet.alpha_composite(flat, ((W - flat.width) // 2, y2))
    sheet.convert("RGB").save(path, quality=94)
    return path


# ---------------------------------------------------------------- 128x128 HD
# 脸部正面手工重画(16x16): 三档虹膜+瞳孔+高光+双层睫毛+发丝尖
HD = {}
HD['head/front'] = [
    "HHHHHHHHHHHHHHHH",
    "HhHHHHHHHHHHHHhH",
    "llllllllllllllll",   # 镜片(内层), 镜框由外层承担
    "llllllllllllllll",
    "LLLWLLLLLLLWLLLL",
    "LLLLLLLLLLLLLLLL",
    "dHHhHHHHHHHHhHHd",
    "dHhHHhHHHHhHHhHd",
    "ddEEEEhhhhEEEEdd",
    "ddEEEEhhhhEEEEdd",
    "ddWWIISSSSIIWWdd",
    "ddWWIISSSSIIWWdd",
    "ddWWiiSSSSiiWWdd",
    "ddddddSSSSdddddd",
    "dHbbSSSSSSSSbbHd",   # 无嘴(默认); 嘴由 build_hd(mouth=...) 叠加
    "dHHSSSSSSSSSSHHd",
]
# 前身手工子像素细节: (face本地x, y, 字符)
HD_DETAIL = {
    'body/front': [
        (7, 14, 'y'), (8, 15, 'y'),          # 银扣内芯
        (6, 14, 'U'), (9, 15, 'U'),          # 扣环高光
        (5, 5, 'y'), (7, 7, 'y'), (9, 9, 'y'), (11, 11, 'y'),   # 斜挎带缝线
        (8, 4, 'N'), (9, 4, 'Y'),           # 金铃高光
        (11, 13, 'p'), (13, 13, 'p'), (12, 16, 'p'),            # 腰包缝线
    ],
    'rleg/front': [
        (2, 17, 'U'), (5, 21, 'U'),          # 靴带扣高光
        (2, 17, 'A'), (5, 17, 'A'), (3, 18, 'A'), (4, 18, 'A'), (2, 19, 'A'), (5, 19, 'A'),  # 靴带交叉
        (1, 9, 'j'), (6, 9, 'j'),          # 护膝缝线
    ],
    'lleg/front': [
        (2, 17, 'U'), (5, 21, 'U'),
        (2, 17, 'A'), (5, 17, 'A'), (3, 18, 'A'), (4, 18, 'A'), (2, 19, 'A'), (5, 19, 'A'),
        (1, 9, 'j'), (6, 9, 'j'),
    ],
    # ---- HD 创意细画 ----
    'head/back': [   # 天使环高光
        (3, 4, 'h'), (4, 4, 'h'), (5, 4, 'h'), (6, 4, 'h'), (7, 4, 'h'),
        (8, 4, 'h'), (9, 4, 'h'), (10, 4, 'h'), (11, 4, 'h'), (12, 4, 'h'),
        (2, 5, 'h'), (13, 5, 'h'),
    ],
    'hat/right': [  # 蝴蝶结(外层, 辫根)
        (8, 6, 'x'), (9, 6, 'x'), (12, 6, 'x'), (13, 6, 'x'),
        (8, 7, 'x'), (10, 7, 'x'), (11, 7, 'x'), (13, 7, 'x'),
        (9, 8, 'x'), (12, 8, 'x'),
        (9, 9, 'd'), (12, 9, 'd'),
    ],
    'body/front': [
        (7, 0, 't'), (9, 0, 't'), (11, 0, 't'), (7, 2, 't'), (9, 2, 't'), (11, 2, 't'),  # 围巾针织rib
        (8, 5, 'y'), (9, 5, 'y'),          # 铃底
        (2, 13, 'y'), (6, 13, 'y'), (10, 13, 'y'), (14, 13, 'y'),   # 皮带粒纹
        (6, 14, 'N'), (9, 14, 'N'),        # 扣环高光
        (5, 7, 'y'), (7, 9, 'y'), (9, 11, 'y'),   # 斜挎带缝线
        (2, 16, 'e'), (3, 16, 'e'), (4, 16, 'e'), (5, 16, 'e'),     # 口袋盖
        (10, 16, 'e'), (11, 16, 'e'), (12, 16, 'e'), (13, 16, 'e'),
        (3, 17, 'U'), (12, 17, 'U'),       # 口袋扣
    ],
    'jacket/front': [
        (10, 13, 'p'), (11, 13, 'p'), (12, 13, 'p'), (13, 13, 'p'), (14, 13, 'p'), (15, 13, 'p'),  # 腰包盖
        (12, 14, 'U'),                     # 包扣
        (12, 10, 'Q'), (13, 10, 'u'), (14, 10, 'Q'), (15, 10, 'u'),  # 粉绳圈
        (12, 11, 'u'), (13, 11, 'Q'), (14, 11, 'u'), (15, 11, 'Q'),
    ],
    'jacket/back': [
        (3, 1, 'r'), (7, 1, 'r'), (11, 1, 'r'),   # 睡袋卷螺旋
        (4, 7, 'U'), (10, 7, 'U'),         # 绑带扣
    ],
    'rarm/front': [
        (1, 19, 'g'), (2, 19, 'g'), (5, 19, 'g'), (6, 19, 'g'),   # 指节线
    ],
    'larm/front': [
        (1, 19, 'g'), (2, 19, 'g'), (5, 19, 'g'), (6, 19, 'g'),
    ],
}
HAIR_CHARS = set('hHdKVv')


def build_hd(mouth='none'):
    S = 2
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    grid_at = {}   # (part,face) -> 原字符网格
    for key, rows in G.items():
        part, face = key.split('/')
        grid_at[(part, face)] = rows
    # 1) 64 版面 x2 打底
    for key, rows in G.items():
        part, face = key.split('/')
        x0, y0, w, h = FACES[part][face]
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch == '.':
                    continue
                px = PAL[ch] + (255,)
                for dy in range(S):
                    for dx in range(S):
                        img.putpixel(((x0 + rx) * S + dx, (y0 + ry) * S + dy), px)
    # 2) 手工 HD 脸覆盖
    for key, rows in HD.items():
        part, face = key.split('/')
        x0, y0, w, h = FACES[part][face]
        for ry in range(h * S):
            for rx in range(w * S):
                img.putpixel((x0 * S + rx, y0 * S + ry), (0, 0, 0, 0))
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch == '.':
                    continue
                img.putpixel((x0 * S + rx, y0 * S + ry), PAL[ch] + (255,))
    # 2.5) 嘴型开关: none / dot(单点) / two(双像素)
    x0, y0, w, h = FACES['head']['front']
    if mouth == 'dot':
        img.putpixel((x0 * S + 7, y0 * S + 14), PAL['m'] + (255,))
    elif mouth == 'two':
        img.putpixel((x0 * S + 7, y0 * S + 14), PAL['m'] + (255,))
        img.putpixel((x0 * S + 8, y0 * S + 14), PAL['m'] + (255,))
    # 3) 手工子像素细节
    for key, pts in HD_DETAIL.items():
        part, face = key.split('/')
        x0, y0, w, h = FACES[part][face]
        for lx, ly, ch in pts:
            img.putpixel((x0 * S + lx, y0 * S + ly), PAL[ch] + (255,))
    # 4) 程序化细节 pass
    for key, rows in G.items():
        part, face = key.split('/')
        if key in HD:
            continue
        x0, y0, w, h = FACES[part][face]
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch == '.':
                    continue
                left = row[rx - 1] if rx > 0 else '.'
                up = rows[ry - 1][rx] if ry > 0 else '.'
                down = rows[ry + 1][rx] if ry + 1 < len(rows) else '.'
                X, Y = (x0 + rx) * S, (y0 + ry) * S
                # 外套织纹: 隔块单子像素暗点
                if ch == 'C' and (rx + ry) % 2 == 0:
                    img.putpixel((X + 1, Y + 1), PAL['c'] + (255,))
                # 发丝分绺: 每2字符一条竖向中间调线
                if ch in HAIR_CHARS and left == ch and up == ch and rx % 2 == 1:
                    img.putpixel((X + 1, Y), PAL['H2'] + (255,))
                    img.putpixel((X + 1, Y + 1), PAL['H2'] + (255,))
                # 毛皮绒边: 底边交替缺口
                if ch == 'F' and down != 'F':
                    if rx % 2 == 0:
                        img.putpixel((X, Y + 1), PAL['f'] + (255,))
                        img.putpixel((X + 1, Y + 1), PAL['f'] + (255,))
                # 金属: 黄铜顶高光 / 银扣内芯
                if ch == 'Y' and up != 'Y':
                    img.putpixel((X, Y), PAL['N'] + (255,))
                    img.putpixel((X + 1, Y), PAL['N'] + (255,))
                if ch == 'U':
                    img.putpixel((X + 1, Y + 1), PAL['y'] + (255,))
                # 靴底齿纹
                if ch == 'z' and rx % 2 == 0:
                    img.putpixel((X, Y + 1), PAL['X'] + (255,))
                    img.putpixel((X + 1, Y + 1), PAL['X'] + (255,))
    return img


def make_hd_sheet(img, path):
    from PIL import ImageDraw
    flat = checker(img.resize((128 * 4, 128 * 4), Image.NEAREST), 4)
    head = img.crop((16, 16, 32, 32)).resize((16 * 10, 16 * 10), Image.NEAREST)
    PAD = 24
    W = max(flat.width, head.width) + PAD * 2
    H = flat.height + head.height + PAD * 3 + 40
    sheet = Image.new("RGBA", (W, H), (32, 34, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W - 1, H - 1], outline=(120, 130, 160, 255), width=6)
    d.text((PAD, 10), "NORDICA HD 128x128  (texture x4 / head x10)", fill=(232, 234, 242, 255))
    sheet.alpha_composite(checker(head, 10), (PAD, 34))
    sheet.alpha_composite(flat, (PAD, 34 + head.height + PAD))
    sheet.convert("RGB").save(path, quality=92)
    return path


def make_mouth_cmp(img_none, img_dot, path):
    from PIL import ImageDraw
    a = img_none.crop((16, 16, 32, 32)).resize((16 * 12, 16 * 12), Image.NEAREST)
    b = img_dot.crop((16, 16, 32, 32)).resize((16 * 12, 16 * 12), Image.NEAREST)
    PAD = 20
    W = a.width * 2 + PAD * 3
    H = a.height + PAD * 2 + 30
    sheet = Image.new("RGBA", (W, H), (32, 34, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 8), "LEFT: no mouth   RIGHT: 1px mouth", fill=(232, 234, 242, 255))
    sheet.alpha_composite(checker(a, 12), (PAD, 30))
    sheet.alpha_composite(checker(b, 12), (PAD * 2 + a.width, 30))
    sheet.convert("RGB").save(path, quality=92)
    return path


if __name__ == '__main__':
    img = build()
    img.save(os.path.join(OUT, "诺谛卡_皮肤.png"))
    p = make_sheet(img, os.path.join(OUT, "诺谛卡_检查图.jpg"))
    hd = build_hd('none')
    hd.save(os.path.join(OUT, "诺谛卡_皮肤_128.png"))
    ph = make_hd_sheet(hd, os.path.join(OUT, "诺谛卡_128_检查图.jpg"))
    hd_dot = build_hd('dot')
    hd_dot.save(os.path.join(OUT, "诺谛卡_皮肤_128_单点嘴.png"))
    pc = make_mouth_cmp(hd, hd_dot, os.path.join(OUT, "诺谛卡_128_嘴型对比.jpg"))
    print("skin ->", os.path.join(OUT, "诺谛卡_皮肤.png"))
    print("sheet ->", p)
    print("hd ->", os.path.join(OUT, "诺谛卡_皮肤_128.png"))
    print("hd sheet ->", ph)
    print("hd dot ->", os.path.join(OUT, "诺谛卡_皮肤_128_单点嘴.png"))
    print("mouth cmp ->", pc)
