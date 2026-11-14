"""Pixel-authored resource-pack insignia (code-native art, no fake boss portraits).

Materials/weapons keep their original ItemStack models. These small military
symbols are for orders, chapters and tiers, not substitutes for creature faces.
"""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'kubejs/assets/svs/textures/quest'
OUTLINE='#171a22'; GOLD='#e3b766'; LIGHT='#ffe4a1'; DARK='#78543e'
designs={
'crown':[(GOLD,[(2,5,4,10),(6,3,9,10),(11,5,13,10),(3,10,12,12)]),(LIGHT,[(3,5,3,6),(7,3,8,5),(12,5,12,6)]),(DARK,[(4,13,11,13)])],
'claw':[(GOLD,[(3,4,4,10),(7,2,8,10),(11,4,12,10),(4,10,11,12)]),(LIGHT,[(3,3,3,5),(7,1,7,4),(11,3,11,5)]),(DARK,[(5,12,10,13)])],
'fortress':[(GOLD,[(1,3,3,12),(6,2,9,12),(12,3,14,12),(3,7,12,12)]),(LIGHT,[(1,2,1,4),(3,2,3,4),(6,1,6,3),(9,1,9,3),(12,2,12,4),(14,2,14,4)]),(OUTLINE,[(6,9,9,13),(3,5,3,6),(12,5,12,6)])],
'flame':[('#bc4e43',[(4,6,11,12),(6,3,10,10),(8,1,9,9)]),('#ee9e50',[(5,7,10,12),(7,4,9,11)]),(LIGHT,[(7,9,9,12),(8,7,8,11)])],
'throne':[(GOLD,[(5,2,10,11),(2,8,4,12),(11,8,13,12),(3,12,12,13)]),(DARK,[(6,4,9,9)]),(LIGHT,[(7,3,8,4),(4,11,11,11)])],
'orbital':[(GOLD,[(6,5,10,9),(1,2,5,4),(11,10,14,12)]),('#8396b5',[(2,5,4,7),(10,7,12,9)]),(LIGHT,[(7,6,8,7),(4,10,5,11),(2,12,3,13),(1,14,1,14)])],
'arsenal':[(GOLD,[(2,4,13,12),(3,2,5,4),(10,2,12,4)]),(DARK,[(4,6,11,11)]),(LIGHT,[(6,5,7,10),(9,5,10,10)]),(GOLD,[(5,9,8,9),(8,9,11,9)])],
'forge':[('#a2a9b4',[(2,7,13,9),(5,10,10,11),(3,12,12,13)]),(LIGHT,[(2,6,10,6)]),(GOLD,[(8,1,13,3),(10,3,11,6)])],
'turret':[('#8d9ba8',[(4,6,11,10),(6,11,9,12),(3,13,12,13)]),(GOLD,[(7,4,14,6),(4,5,8,8)]),(LIGHT,[(12,4,14,4)]),(DARK,[(5,8,6,9)])],
'dragon':[('#699e8b',[(6,3,10,10),(2,6,5,8),(10,6,13,8),(7,10,9,13)]),(GOLD,[(5,2,6,4),(10,2,11,4)]),(LIGHT,[(7,5,7,5),(10,5,10,5)]),(OUTLINE,[(8,8,10,8)])],
'symbiote':[('#8875ad',[(5,2,10,12),(3,5,12,9),(6,12,9,13)]),('#c2b7d8',[(5,5,6,6),(9,5,10,6)]),(OUTLINE,[(6,9,9,10)]),('#aa92bf',[(2,9,3,11),(12,9,13,11)])],
'relic':[(GOLD,[(4,3,11,4),(3,5,4,10),(11,5,12,10),(5,11,10,12)]),('#6dc5bc',[(6,5,9,10),(5,7,10,8)]),(LIGHT,[(6,5,7,6)])],
'hunt':[(DARK,[(3,2,5,13),(5,4,7,6),(5,9,7,11)]),(GOLD,[(6,3,8,4),(9,5,10,7),(9,8,10,10),(6,11,8,12)]),(LIGHT,[(7,7,14,8),(12,6,13,9)])],
'compass':[(DARK,[(4,2,11,13),(2,4,13,11)]),(GOLD,[(4,3,11,12),(3,5,12,10)]),('#303847',[(5,5,10,10)]),(LIGHT,[(7,3,8,8)]),('#a2b4c9',[(6,8,7,12)])],
'command':[(GOLD,[(2,2,13,13)]),('#303847',[(3,3,12,12)]),(LIGHT,[(5,5,10,5),(5,8,10,8),(5,11,8,11)])],
'lightning':[(GOLD,[(7,1,11,4),(5,5,9,8),(7,8,10,9),(5,10,8,12),(4,13,5,14)]),(LIGHT,[(8,2,10,3),(6,6,8,7)])]
}
for tier,color in [('t2','#98b5b1'),('t1','#9ba2dc'),('t0',GOLD)]:
    designs[tier]=[(color,[(3,3,12,4),(3,5,4,11),(11,5,12,11),(5,12,10,13)]),
                   (LIGHT,[(6,6,9,7),(7,8,8,10)])]
    if tier=='t1':designs[tier].append((color,[(7,1,8,2)]))
    if tier=='t0':designs[tier].append((color,[(4,1,5,2),(7,0,8,2),(10,1,11,2)]))

def insignia(layers):
    inner=Image.new('RGBA',(16,16));dr=ImageDraw.Draw(inner)
    for color,rects in layers:
        for rect in rects:dr.rectangle(rect,fill=color)
    mask=inner.getchannel('A');outer=Image.new('RGBA',(16,16));od=ImageDraw.Draw(outer)
    for y in range(16):
        for x in range(16):
            if mask.getpixel((x,y)):
                for dx,dy in [(0,1),(1,0),(-1,0),(0,-1)]:
                    if 0<=x+dx<16 and 0<=y+dy<16:od.point((x+dx,y+dy),OUTLINE)
    outer.alpha_composite(inner);return outer

for folder in ['emblems','banners']:(DEST/folder).mkdir(parents=True,exist_ok=True)
images={}
for name,design in designs.items():
    pic=insignia(design);pic.save(DEST/'emblems'/f'{name}.png');images[name]=pic
    banner=Image.new('RGBA',(256,48),(22,27,37,235));dr=ImageDraw.Draw(banner)
    dr.line((1,1,254,1),fill=(163,126,69,180));dr.line((1,46,254,46),fill=(101,84,60,180))
    dr.line((3,3,3,44),fill=(163,126,69,180))
    for x in range(53,246,16):
        dr.line((x,12,x+8,12,x+8,19),fill=(74,85,101,160));dr.line((x,35,x+10,35),fill=(74,85,101,140))
    banner.alpha_composite(pic.resize((32,32),Image.Resampling.NEAREST),(10,8));banner.save(DEST/'banners'/f'{name}.png')

# Override only the quest book's item surface, not editor controls or all GUI icons.
p=ROOT/'kubejs/assets/ftbquests/textures/item/book.png';p.parent.mkdir(parents=True,exist_ok=True)
book=Image.new('RGBA',(16,16));dr=ImageDraw.Draw(book)
dr.polygon([(2,2),(11,1),(14,4),(14,13),(5,15),(1,12)],fill=OUTLINE)
dr.polygon([(3,3),(10,2),(12,4),(5,6)],fill='#c7bca5')
dr.polygon([(2,5),(5,7),(5,13),(2,11)],fill='#5d493b')
dr.polygon([(6,7),(13,5),(13,12),(6,14)],fill='#343746')
dr.line([(6,7),(13,5),(13,12),(6,14),(6,7)],fill=GOLD,width=1)
dr.rectangle((8,8,10,10),fill=GOLD);dr.point((9,8),fill=LIGHT);book.save(p)
# Change the top-left book caption in both languages via the normal client pack.
lp=ROOT/'kubejs/assets/ftbquests/lang';lp.mkdir(parents=True,exist_ok=True)
for lang in ['zh_cn','en_us']:
    (lp/f'{lang}.json').write_text(json.dumps({'item.ftbquests.book':'征伐星图','ftbquests.file':'天外成王 · 征伐星图'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
preview=Image.new('RGB',(760,((len(images)+5)//6)*145),(27,31,41));pd=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
labels={'crown':'天外王途','claw':'血肉筑基','fortress':'军工疆域','flame':'掠夺劫火','throne':'诸王神权','orbital':'天基总攻','arsenal':'君王武库','forge':'军工锻造','turret':'要塞火力','dragon':'制空龙骑','symbiote':'共生战甲','relic':'远征遗珍','hunt':'独立猎场','compass':'异界远征','command':'军令备忘','lightning':'沙行雷暴','t2':'T2 基础','t1':'T1 精锐','t0':'T0 顶阶'}
for index,(name,im) in enumerate(images.items()):
    x=(index%6)*126+24;y=(index//6)*145+15
    preview.paste(im.resize((80,80),Image.Resampling.NEAREST),(x,y),im.resize((80,80),Image.Resampling.NEAREST))
    pd.text((x-5,y+91),labels[name],font=font,fill='#e7dbbc')
pp=ROOT/'backups/questbook_v6_20261017/previews';pp.mkdir(parents=True,exist_ok=True)
preview.save(pp/'chapter_insignia.png')
print('pixel insignia',len(images),'book and chapter banners written')
