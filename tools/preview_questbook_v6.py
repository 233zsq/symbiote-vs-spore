"""Readable content proof, not a screenshot or claimed in-game verification."""
import io,json,textwrap,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'backups/questbook_v6_20261017/previews';O.mkdir(parents=True,exist_ok=True)
d=json.loads((R/'docs/questbook_v2.json').read_text(encoding='utf-8'));qs={q['key']:q for q in d['quests']}
fonts={s:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',s) for s in [15,17,19,23,30]}
zips=[];owners={}
for p in Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test/mods').glob('*.jar'):
    z=zipfile.ZipFile(p);zips.append(z)
    for n in z.namelist():
        if n.startswith('assets/') and n.endswith(('.png','.json')):owners[n]=z
p=Path('C:/PCL 正式版 2.8.13/.minecraft/libraries/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-extra.jar')
z=zipfile.ZipFile(p);zips.append(z)
for n in z.namelist():
    if n.startswith('assets/'):owners[n]=z
def raw(path):
    p=R/'kubejs'/path
    return p.read_bytes() if p.exists() else owners[path].read(path) if path in owners else None
def icon(id,texture=False):
    ns,name=id.split(':',1)
    if texture:
        data=raw('assets/'+ns+'/'+name)
        return Image.open(io.BytesIO(data)).convert('RGBA') if data else None
    data=raw(f'assets/{ns}/models/item/{name}.json')
    if not data:return None
    m=json.loads(data)
    if m.get('loader') or m.get('elements'):return None
    tex=m.get('textures',{}).get('layer0')
    if not tex or tex.startswith('#'):return None
    ns,name=tex.split(':',1) if ':' in tex else ('minecraft',tex)
    data=raw(f'assets/{ns}/textures/{name}.png')
    if not data:return None
    im=Image.open(io.BytesIO(data)).convert('RGBA')
    if im.height>im.width and im.height%im.width==0:im=im.crop((0,0,im.width,im.width))
    return im
im=Image.new('RGB',(1240,1540),'#171d27');dr=ImageDraw.Draw(im)
def text(x,y,s,size=19,color='#d6dce5',width=55):
    for line in textwrap.wrap(s,width=width):
        dr.text((x,y),line,font=fonts[size],fill=color);y+=size+10
    return y
dr.text((40,24),'天外成王 · 主线与武库内容校样',font=fonts[30],fill='#edc778')
text(40,75,'离线内容预览，展示实际任务文本和原生物品平面图；并非游戏截图。',17,width=70)
examples=[('E6_V4_M02','E6_V6_AFTER_M02'),('E6_V4_M06','E6_V6_AFTER_M06'),('E6_V4_M12','E6_V6_AFTER_M12')]
for row,(key,afterkey) in enumerate(examples):
    q=qs[key];a=qs[afterkey];y=130+row*342
    dr.rounded_rectangle((30,y,1208,y+320),radius=12,fill='#242e3c',outline='#816843',width=2)
    sprite=icon(q['icon_texture'],True) if q.get('icon_texture') else icon(q['icon'])
    if sprite:
        sprite.thumbnail((55,55));spr=sprite.resize((56,56),Image.Resampling.NEAREST);im.paste(spr,(48,y+20),spr)
    text(122,y+22,q['title'],23,'#edc778',width=44)
    text(50,y+91,q['text'][0],19,width=56)
    text(50,y+191,'战后：'+a['title'],19,'#84d4cd',width=56)
    text(50,y+225,a['text'][2],17,width=65)
    names={'silence_s_defense_tower:driving_core_1':'核心1级','silence_s_defense_tower:counter_1':'计数器','silence_s_defense_tower:gloves':'回收手套','silence_s_defense_tower:driving_core_3':'核心3级','kubejs:spore_coin':'真菌残魂','tconstruct:hepatizon_ingot':'黑色合金锭'}
    text(50,y+277,'实际拨付：'+'　'.join(names.get(i[0],i[0])+'×'+str(i[1]) for i in a['items']),17,'#d8caa7',width=75)
y=1170
dr.rounded_rectangle((30,y,1208,1495),radius=12,fill='#242e3c',outline='#816843',width=2)
text(50,y+18,'收藏家与全鉴合并 · 不同装备，分档累计',23,'#edc778',width=46)
for col,(tier,label,r,sett) in enumerate([('T2','基础',1,'3 / 8 / 16种兵器；1 / 3 / 6套甲胄'),('T1','精锐',4,'3 / 8 / 16种兵器；1 / 3 / 6套甲胄'),('T0','顶阶',12,'3 / 8 / 16种兵器；1 / 2 / 3套甲胄')]):
    x=50+col*385
    spr=icon('svs:textures/quest/emblems/'+tier.lower()+'.png',True).resize((48,48),Image.Resampling.NEAREST);im.paste(spr,(x,y+69),spr)
    text(x+65,y+76,tier+' · '+label,23,'#edc778',width=14)
    text(x,y+135,'单件鉴定：残魂×'+str(r),17,width=20)
    text(x,y+173,'成组甲胄：按完整登记结算',17,width=20)
    text(x,y+211,sett,15,width=22)
text(50,y+275,'每批六件，按需展开；翻页不要求集齐上一批。奖励只领一次，已取得记录保留。',17,width=78)
im.save(O/'campaign_and_rewards.png')
for z in zips:z.close()
print(O/'campaign_and_rewards.png')
