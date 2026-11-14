"""Offline authoring preview using actual item sprites; never claims Minecraft UI acceptance."""
import io,json,math,textwrap,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'backups/questbook_v5_rebuild_20261017/previews';OUT.mkdir(parents=True,exist_ok=True)
MODS=Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test/mods')
owners={};zips=[]
for p in sorted(MODS.glob('*.jar')):
    z=zipfile.ZipFile(p);zips.append(z)
    for n in z.namelist():
        if n.startswith('assets/') and (n.endswith('.png') or '/models/' in n):owners[n]=z
vanilla=zipfile.ZipFile('C:/PCL 正式版 2.8.13/.minecraft/libraries/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-extra.jar');zips.append(vanilla)
for n in vanilla.namelist():
    if n.startswith('assets/'):owners[n]=vanilla
def raw(path):
    p=ROOT/'kubejs'/path
    return p.read_bytes() if p.exists() else owners[path].read(path) if path in owners else None
def resource(id,kind):
    ns,name=(id.split(':',1) if ':' in id else ['minecraft',id]);return f'assets/{ns}/{kind}/{name}'
def icon(id,texture=False):
    if texture:
        data=raw(resource(id,'').replace('//','/'))
        return Image.open(io.BytesIO(data)).convert('RGBA') if data else None
    path=resource(id,'models/item')+'.json';textures={};seen=set()
    while path not in seen:
        seen.add(path);data=raw(path)
        if not data:break
        model=json.loads(data)
        if model.get('loader') or model.get('elements') or model.get('parent','')=='builtin/entity':return None
        textures={**model.get('textures',{}),**textures}
        parent=model.get('parent')
        if not parent:break
        path=resource(parent,'models')+'.json'
    tex=next((textures[k] for k in ('layer0','0','all','texture') if k in textures),next(iter(textures.values()),''))
    while tex.startswith('#') and tex[1:] in textures:tex=textures[tex[1:]]
    if not tex or tex.startswith('#'):return None
    data=raw(resource(tex,'textures')+'.png')
    if not data:return None
    im=Image.open(io.BytesIO(data)).convert('RGBA')
    # Animated sprites: show the first square frame, not the whole vertical strip.
    if im.height>im.width and im.height%im.width==0:im=im.crop((0,0,im.width,im.width))
    return im
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
d=json.loads((ROOT/'docs/questbook_v2.json').read_text(encoding='utf-8'));nodes={q['key']:q for q in d['quests']}
for key in ['departure','counterattack','v5_loadouts','v5_fortress','v5_armor_monsterexpansion_1']:
    ch=next(c for c in d['chapters'] if c['key']==key);qs=[q for q in nodes.values() if q['chapter']==key]
    xs=[q['position'][0] for q in qs];ys=[q['position'][1] for q in qs];scale=66;pad=120
    width=int((max(xs)-min(xs))*scale+pad*2);height=int((max(ys)-min(ys))*scale+pad*2+50)
    im=Image.new('RGB',(max(width,760),max(height,400)),(19,25,32));draw=ImageDraw.Draw(im)
    draw.text((28,20),ch['title'].replace('&6','').replace('&b','').replace('&a','').replace('&7',''),font=font(25),fill=(240,206,136))
    draw.text((28,58),'离线排布预览 · 使用真实物品贴图，非游戏截图',font=font(17),fill=(159,176,190))
    positions={q['key']:(int((q['position'][0]-min(xs))*scale+pad),int((q['position'][1]-min(ys))*scale+pad+40)) for q in qs}
    for q in qs:
        x,y=positions[q['key']]
        for dep in q['deps']:
            if dep in positions:
                dx,dy=positions[dep];draw.line((dx,dy,x,y),fill=(81,100,115),width=3)
    for q in qs:
        x,y=positions[q['key']];pending=q['availability']=='pending'
        fill=(105,85,60) if pending else (55,99,103) if q.get('boss_slot') else (58,72,90)
        draw.rounded_rectangle((x-30,y-30,x+30,y+30),radius=10,fill=fill,outline=(186,161,116),width=2)
        sprite=icon(q['icon_texture'],True) if q.get('icon_texture') else icon(q.get('icon') or next((t['target'] for t in q['tasks'] if t['kind']=='item'),ch['icon']))
        if sprite:
            factor=min(42/sprite.width,42/sprite.height)
            sprite=sprite.resize((max(1,round(sprite.width*factor)),max(1,round(sprite.height*factor))),Image.Resampling.NEAREST)
            im.paste(sprite,(x-sprite.width//2,y-sprite.height//2),sprite)
        else:draw.text((x-14,y-12),'3D',font=font(17),fill=(195,208,213))
        title=q['title'];lines=[title[i:i+13] for i in range(0,len(title),13)][:3]
        for i,line in enumerate(lines):
            box=draw.textbbox((0,0),line,font=font(16));draw.text((x-(box[2]-box[0])/2,y+35+i*21),line,font=font(16),fill=(218,224,228))
    im.save(OUT/(key+'.png'))

portraits=sorted((q for q in nodes.values() if q.get('boss_slot')),key=lambda q:q['boss_slot'])
sheet=Image.new('RGB',(1000,math.ceil(len(portraits)/10)*125),(22,28,35));draw=ImageDraw.Draw(sheet)
for i,q in enumerate(portraits):
    x=(i%10)*100;y=(i//10)*125
    sprite=icon(q['icon_texture'],True) if q.get('icon_texture') else icon(q['icon'])
    if sprite:
        factor=min(64/sprite.width,64/sprite.height)
        sprite=sprite.resize((max(1,round(sprite.width*factor)),max(1,round(sprite.height*factor))),Image.Resampling.NEAREST)
        sheet.paste(sprite,(x+50-sprite.width//2,y+12),sprite)
    draw.text((x+30,y+82),q['boss_slot'],font=font(17),fill=(234,212,160))
    if not sprite:draw.text((x+10,y+20),'游戏3D模型',font=font(14),fill=(176,190,205))
sheet.save(OUT/'boss_icon_sheet.png')
for z in zips:z.close()
print('Saved 5 chapter layouts and the 50-target icon sheet:',OUT)
