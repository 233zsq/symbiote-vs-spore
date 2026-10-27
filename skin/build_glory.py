# -*- coding: utf-8 -*-
"""诺谛卡_名以光辉 (From Darkness, Light) 64x64 双层 + 128x128 HD。
设计依据 crt/诺谛卡/衣着 的 Q版小人 + Live2D + 立绘：
  头: 粉发(品红挑染+焰红发梢) / 金环冠+红心宝石+金币垂饰 / 黑羽角 / 后白羽簇 / 侧绺焰尖
  身: 黑毛领 / 绛红胸衣+白心版+火焰纹 / 金币腰链 / 白毛裙+紫流苏+金羽饰 / 焰红裙摆
  臂: 裸臂+金臂环 / 红手套 / 肩白羽(外层)
  腿: 人腿=白毛大腿+金腿环+炭黑小腿+白绒口+蹄尖(参照 Live2D 马前腿)
  背: 外层白翼(品红翼尖) + 凤凰焰舌下摆
类人马形态按用户要求做人腿。复用 mc-skin-crafter skill 的 skin_lib。
"""
import os
import sys
sys.path.insert(0, r"C:\Users\zhens\.qoder-cn\skills\mc-skin-crafter\scripts")
import skin_lib as sl

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

PAL = {
    # 粉发 + 焰梢
    'H': (242, 164, 158), 'h': (252, 200, 192), 'd': (206, 112, 110),
    # 绛红/火焰
    'X': (140, 26, 48), 'x': (190, 45, 70), 'v': (230, 80, 100), 'O': (240, 140, 70),
    # 雪白羽毛
    'F': (250, 248, 244), 'f': (226, 220, 210), 'e': (200, 192, 180),
    # 金
    'Y': (185, 154, 91), 'N': (214, 184, 122), 'o': (168, 130, 58), 'U': (238, 214, 150),
    # 皮肤/眼(同原皮)
    'S': (247, 228, 218), 's': (230, 200, 187), 'b': (238, 186, 178), 'm': (214, 150, 140),
    'E': (58, 62, 69), 'W': (252, 252, 250), 'I': (94, 156, 148), 'i': (171, 216, 206),
    # 炭黑(角/小腿/毛领) + 紫流苏
    'k': (48, 46, 58), 'c': (82, 78, 92),
    'K': (178, 150, 205), 'V': (108, 92, 190),
    # HD 中间调
    'H2': (224, 138, 134),
}

G = {}
# ---------------- 头(内层): 脸沿用原皮验收结构(深睫+青绿虹膜+无嘴无鼻+腮红)
G['head/front'] = [
    "dHHHHHHd",   # 顶角暗发破方体
    "hHHHHHHh",
    "HHHHHHHH",
    "dxxHHxxd",   # 中分锯齿刘海(焰尖)
    "dEEhhEEd",   # 深炭睫毛+镜间碎发
    "dWISSIWd",   # 侧绺框脸+眼白+虹膜
    "dWiSSiWd",
    "HbSSSSbH",   # 无嘴+腮红
]
G['head/right'] = [   # col7=前缘(侧绺)
    "hhhhhhhh",
    "HHHHHHHH",
    "HHHHHHHH",
    "HHhHHHHd",
    "HHxHHHHd",   # 品红挑染缕
    "HHxHHHHd",
    "HHxHHxHd",
    "HxxHHxxd",   # 焰红发梢
]
G['head/left'] = [    # col0=前缘
    "hhhhhhhh",
    "HHHHHHHH",
    "HHHHHHHH",
    "dHHHHhHH",
    "dHHHHHxH",
    "dHHHHHxH",
    "dHxHHxHH",
    "dxxHHxxH",
]
G['head/back'] = [
    "hhhhhhhh",
    "HHHHHHHH",
    "HHHHHHHH",
    "dHHHHHHd",
    "dHHHHHHd",
    "dHxHHxHd",
    "dxxHHxxd",
    "dxxxxxxd",   # 发尾整排焰红(凤凰)
]
G['head/top'] = [
    "hhhhhhhh", "hHHHHHHh", "HHHHHHHH", "HHxHHxHH",
    "HHxHHxHH", "HHHHHHHH", "hHHHHHHh", "hhhhhhhh",
]
G['head/bottom'] = ["dddddddd"] * 4 + ["ddssssdd"] * 4

# ---------------- 头(外层): 黑羽角+金环冠+心宝石+金币垂+侧绺焰尖
G['hat/front'] = [
    "kk....kk",   # 黑羽角尖
    "kNNNNNNk",   # 金环冠+角根
    ".NUxxUN.",   # 冠心红宝
    ".Y....Y.",   # 金币垂饰
    "........",
    "x......x",   # 侧绺焰尖
    "x......x",
    "........",
]
G['hat/top'] = [
    "........", "........", "kk....kk", "kNNNNNNk",
    "........", "........", "........", "........",
]
G['hat/right'] = [    # col7=前缘
    "k......k",    # 黑羽角(顶角柱)
    "NNNNNNNN",    # 冠带
    "FF.UU...",    # 后白羽+金翼饰
    "Ff..YY..",    # 金币耳坠
    "f...YY..",
    ".......x",
    ".......x",
    "........",
]
G['hat/left'] = [     # col0=前缘
    "k......k",
    "NNNNNNNN",
    "...UU.FF",
    "..YY..fF",
    "..YY...f",
    "x.......",
    "x.......",
    "........",
]
G['hat/back'] = [
    "kk....kk",
    "NNNNNNNN",
    "FF....FF",   # 白羽后簇
    "Ff....fF",
    "f......f",
    "x......x",   # 发梢焰尖
    "x......x",
    "........",
]

# ---------------- 身体(内层): 黑毛领/绛红胸衣/金币链/白毛裙+紫流苏/焰摆
G['body/front'] = [
    "kkkkkkkk",   # 黑毛领
    "XxxFFxxX",   # 绛红胸衣+白心版
    "XxxvvxxX",   # 心版下火焰纹
    "XoYooYoX",   # 金币腰链
    "FffffffF",   # 白毛裙
    "FFFFFFFF",
    "FKFFFFKF",   # 紫流苏
    "FKFNNFKF",   # 金羽坠+流苏
    "FVFooFVF",
    "FVffffVF",   # 流苏梢
    "xFffffFx",   # 焰摆
    "xxffffxx",
]
G['body/back'] = [
    "kkkkkkkk",
    "XXxxxxXX",
    "XxxxxxxX",
    "XoYooYoX",
    "FffffffF",
    "FFFFFFFF",
    "FKFFFFKF",
    "FKFFFFKF",
    "FVFffFVF",
    "FVffffVF",
    "xFffffFx",
    "xxffffxx",
]
_side_body = [
    "kkkk", "XxxX", "XvvX", "oYYo", "FffF", "FFFF",
    "FKKF", "FKKF", "FVVF", "FffF", "xFFx", "xxxx",
]
G['body/right'] = _side_body
G['body/left'] = _side_body
G['body/top'] = ["HHHHHHHH", "kkkkkkkk", "kkkkkkkk", "kkkSSkkk"]
G['body/bottom'] = ["ffffffff"] * 4

# ---------------- 身体(外层): 肩白羽 / 背翼(品红翼尖) / 凤凰焰舌
_jk_front = ["........"] * 12
_jk_front[0] = "FF....FF"
_jk_front[1] = "Ff....fF"
_jk_front[9] = "v......v"    # 前摆焰尖
_jk_front[10] = "v......v"
G['jacket/front'] = _jk_front
G['jacket/back'] = [
    "FFFFFFFF",   # 白翼(整片)
    "FfFFFFfF",
    "FeFFFFeF",   # 羽脉
    "FFFFFFFF",
    "FFfFFfFF",
    "FFFFFFFF",
    "Fx.xx.xF",   # 羽缘锯齿+品红
    ".x....x.",
    "........",
    "..vxxv..",    # 焰舌
    "..vxxv..",
    "...xx...",
]
_jk_side = ["...."] * 12
_jk_side[0] = "FFFF"
_jk_side[1] = "fFFf"
_jk_side[2] = "FeeF"
_jk_side[10] = ".xx."
_jk_side[11] = ".xx."
G['jacket/right'] = _jk_side
G['jacket/left'] = _jk_side

# ---------------- 臂(内层): 裸臂+金臂环+红手套
_arm = [
    "SSSS", "SssS", "YYYY", "oooo", "SSSS", "SssS",
    "SSSS", "SssS", "SSSS", "xxxx", "xvxx", "XXXX",
]
for p in ('rarm', 'larm'):
    for f in ('front', 'back', 'right', 'left'):
        G[p + '/' + f] = _arm
    G[p + '/top'] = ["SSSS", "SssS", "SSSS", "SssS"]
    G[p + '/bottom'] = ["XXXX"] * 4
# 臂(外层): 肩白羽 + 金镯
_a2 = ["...."] * 12
_a2[0] = "FFFF"
_a2[1] = "fFFf"
_a2[8] = "NYYN"
for p in ('rarm2', 'larm2'):
    for f in ('front', 'back', 'right', 'left'):
        G[p + '/' + f] = _a2
    G[p + '/top'] = ["FFFF", "fFFf", "fFFf", "FFFF"]

# ---------------- 腿(内层): 人腿=白毛大腿/金腿环/炭黑小腿/白绒口/蹄尖
_leg = [
    "FFFF", "FffF", "FFFF", "YYYY", "kcck", "kcck",
    "kcck", "kcck", "FFFF", "FffF", "FFFF", "kkkk",
]
for p in ('rleg', 'lleg'):
    for f in ('front', 'back', 'right', 'left'):
        G[p + '/' + f] = _leg
    G[p + '/top'] = ["FFFF"] * 4
    G[p + '/bottom'] = ["kkkk"] * 4
# 腿(外层): 腿环亮面 + 绒口蓬松
_l2 = ["...."] * 12
_l2[3] = "NYYN"
_l2[8] = "fFFf"
_l2[9] = "FFFF"
_l2[10] = "fFFf"
for p in ('rleg2', 'lleg2'):
    for f in ('front', 'back', 'right', 'left'):
        G[p + '/' + f] = _l2

# ---------------- HD 脸 16x16(沿用原皮验收脸结构 + 金冠行 + 品红刘海梢)
HD = {'head/front': [
    "HHHHHHHHHHHHHHHH",
    "HhHHHHHHHHHHHHhH",
    "NNNNNNNNNNNNNNNN",   # 金环冠
    "YYYYYYYxxYYYYYYY",   # 冠心红宝
    "YoYYYYYxxYYYYYoY",
    "dHHhHHHHHHHHhHHd",
    "dHxHHhHHHHhHHxHd",   # 品红刘海梢
    "ddEEEEhhhhEEEEdd",   # 双层睫毛
    "ddEEEEhhhhEEEEdd",
    "ddWWIISSSSIIWWdd",
    "ddWWIISSSSIIWWdd",
    "ddWWiiSSSSiiWWdd",
    "ddddddSSSSdddddd",
    "dHbbSSSSSSSSbbHd",   # 腮红
    "dHHSSSSSSSSSSHHd",   # 嘴位(mouth='two' 注入)
    "dHHSSSSSSSSSSHHd",
]}

# ---------------- HD 细节坐标表(128 子像素)
HD_DETAIL = {
    'hat/front': [   # 冠上金币纹 + 宝石高光
        (3, 3, 'U'), (6, 3, 'U'), (9, 3, 'U'), (12, 3, 'U'),
        (7, 4, 'v'), (8, 4, 'v'),
    ],
    'hat/right': [(4, 3, 'U'), (10, 3, 'U'), (8, 7, 'U')],
    'hat/left': [(11, 3, 'U'), (5, 3, 'U'), (7, 7, 'U')],
    'body/front': [   # 金币链扣心 + 心版宝石 + 焰摆亮尖
        (5, 7, 'o'), (10, 7, 'o'),
        (7, 5, 'x'), (8, 5, 'x'),
        (1, 21, 'v'), (14, 21, 'v'),
    ],
    'body/back': [(5, 7, 'o'), (10, 7, 'o'), (1, 21, 'v'), (14, 21, 'v')],
    'jacket/back': [   # 翼羽脉 + 焰舌橙心
        (3, 3, 'f'), (12, 3, 'f'), (3, 6, 'f'), (12, 6, 'f'),
        (7, 19, 'O'), (8, 19, 'O'), (7, 21, 'O'), (8, 21, 'O'),
    ],
    'head/back': [   # 余烬天使环(火焰版)
        (3, 4, 'v'), (4, 4, 'v'), (5, 4, 'v'), (6, 4, 'v'), (7, 4, 'v'),
        (8, 4, 'v'), (9, 4, 'v'), (10, 4, 'v'), (11, 4, 'v'), (12, 4, 'v'),
        (6, 3, 'O'), (9, 3, 'O'),
    ],
    'rleg/front': [(2, 7, 'U'), (5, 7, 'U')],   # 腿环铆钉
    'lleg/front': [(2, 7, 'U'), (5, 7, 'U')],
}

if __name__ == '__main__':
    errs = sl.check_grids(G)
    assert not errs, errs
    img = sl.build(PAL, G)
    holes = sl.validate_base(img, G)
    assert not holes, holes[:5]
    img.save(os.path.join(OUT, "诺谛卡_名以光辉.png"))
    sl.make_sheet(img, os.path.join(OUT, "诺谛卡_名以光辉_检查图.jpg"), title="NORDICA-GLORY 64")
    hd = sl.build_hd(PAL, G, HD, HD_DETAIL, mouth='two', hair_chars='hHdxXv')
    hd.save(os.path.join(OUT, "诺谛卡_名以光辉_128.png"))
    sl.make_hd_sheet(hd, os.path.join(OUT, "诺谛卡_名以光辉_128_检查图.jpg"), title="NORDICA-GLORY HD")
    print("glory 64/128 done, holes:", len(holes))
