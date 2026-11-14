"""Render real mod geometry/UVs from the front, then produce 16px FTB portraits.
This is a geometry renderer, not an invented face or a UV-atlas thumbnail.
"""
import io,json,math,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
R=Path(__file__).resolve().parents[1];B=R/'backups/legendary_bosses_20261018'
z=zipfile.ZipFile(B/'legendarybosses-0.6.1-beta.jar');out=R/'kubejs/assets/svs/textures/quest/boss';out.mkdir(parents=True,exist_ok=True)
preview=B/'previews';preview.mkdir(exist_ok=True);manifest=[]
def transform(rotation,pivot):
    rx,ry,rz=np.deg2rad(rotation);cx,sx=math.cos(rx),math.sin(rx);cy,sy=math.cos(ry),math.sin(ry);cz,sz=math.cos(rz),math.sin(rz)
    rot=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    m=np.eye(4);m[:3,:3]=rot;m[:3,3]=np.array(pivot)-rot@np.array(pivot);return m
def render(boss):
    geo=json.loads(z.read(f'assets/legendarybosses/geo/{boss}.geo.json'))['minecraft:geometry'][0]
    tex=Image.open(io.BytesIO(z.read(f'assets/legendarybosses/textures/entity/{boss}.png'))).convert('RGBA')
    # The mod's AutoGlowingGeoLayer supplies the canonical luminous eyes.
    # Include its real pixels rather than drawing invented facial details.
    tex.alpha_composite(Image.open(io.BytesIO(z.read(f'assets/legendarybosses/textures/entity/{boss}_glowmask.png'))).convert('RGBA'))
    bones={b['name']:b for b in geo['bones']};mat={}
    def matrix(name):
        if name not in mat:
            b=bones[name];m=transform(b.get('rotation',[0,0,0]),b.get('pivot',[0,0,0]));mat[name]=(matrix(b['parent'])@m) if b.get('parent') else m
        return mat[name]
    # Human bosses use a close frontal head crop so the eyes and beard remain
    # legible at 16px. Null keeps the original halo silhouette around the head.
    size=224;top=37 if boss=='null' else 33;bottom=16 if boss=='null' else 23;span=top-bottom;left=-span/2
    rgba=np.zeros((size,size,4),dtype=np.uint8);depth=np.full((size,size),np.inf)
    for name,bone in bones.items():
        if name.startswith('armor_') or any(p in name for p in ['leg','pants','boot','slot','hotbar','pickaxe','item','chunk_']):continue
        for cube in bone.get('cubes',[]):
            origin=np.array(cube['origin'],float);dx,dy,dz=cube['size'];uv=cube.get('uv');inflate=cube.get('inflate',0)
            if not isinstance(uv,list):continue
            u,v=uv
            # North face of the box: Minecraft skins face toward negative Z.
            vertices=np.array([[origin[0]-inflate,origin[1]+dy+inflate,origin[2]-inflate,1],
                               [origin[0]+dx+inflate,origin[1]+dy+inflate,origin[2]-inflate,1],
                               [origin[0]+dx+inflate,origin[1]-inflate,origin[2]-inflate,1],
                               [origin[0]-inflate,origin[1]-inflate,origin[2]-inflate,1]])
            m=matrix(name)@transform(cube.get('rotation',[0,0,0]),cube.get('pivot',[0,0,0]));world=(m@vertices.T).T[:,:3]
            points=np.column_stack(((world[:,0]-left)/span*size,(top-world[:,1])/span*size,world[:,2]))
            tuv=np.array([[u+dz,v+dz],[u+dz+dx,v+dz],[u+dz+dx,v+dz+dy],[u+dz,v+dz+dy]],float)
            if cube.get('mirror',bone.get('mirror',False)):tuv[:,0]=(u+dz)*2+dx-tuv[:,0]
            for ids in [[0,1,2],[0,2,3]]:
                a,b,c=points[ids];ta,tb,tc=tuv[ids]
                lo=np.maximum(np.floor(np.min([a[:2],b[:2],c[:2]],axis=0)).astype(int),0)
                hi=np.minimum(np.ceil(np.max([a[:2],b[:2],c[:2]],axis=0)).astype(int),size-1)
                denom=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
                if abs(denom)<1e-9:continue
                for yy in range(lo[1],hi[1]+1):
                    for xx in range(lo[0],hi[0]+1):
                        x,y=xx+.5,yy+.5;w1=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/denom;w2=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/denom;w3=1-w1-w2
                        if min(w1,w2,w3)<-1e-7:continue
                        zz=w1*a[2]+w2*b[2]+w3*c[2]
                        if zz>=depth[yy,xx]:continue
                        t=w1*ta+w2*tb+w3*tc;tx=min(max(int(t[0]),0),tex.width-1);ty=min(max(int(t[1]),0),tex.height-1);pixel=tex.getpixel((tx,ty))
                        if pixel[3]<128:continue
                        rgba[yy,xx]=pixel;depth[yy,xx]=zz
    return Image.fromarray(rgba)
sheet=Image.new('RGB',(720,240),'#242b36');dr=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for index,boss in enumerate(['herobrine','entity_303','null','notch']):
    source=render(boss);source.save(preview/(boss+'_front_render.png'))
    pic=source.resize((14,14),Image.Resampling.LANCZOS);pic.putalpha(pic.getchannel('A').point(lambda x:255 if x>=110 else 0))
    face=Image.new('RGBA',(16,16));face.alpha_composite(pic,(1,1));alpha=face.getchannel('A').filter(ImageFilter.MaxFilter(3));result=Image.new('RGBA',(16,16),(25,20,24,0));result.putalpha(alpha);result.alpha_composite(face)
    result.save(out/('lb_'+boss+'.png'));up=result.resize((128,128),Image.Resampling.NEAREST);sheet.paste(up,(index*180+26,24),up);dr.text((index*180+18,170),boss,font=font,fill='#ebd399')
    manifest.append(dict(boss=boss,source='legendarybosses-0.6.1-beta.jar!/assets/legendarybosses/geo/'+boss+'.geo.json',texture='assets/legendarybosses/textures/entity/'+boss+'.png',render=str(preview/(boss+'_front_render.png')),output=str(out/('lb_'+boss+'.png')),size=[16,16],kind='original-model-front-projection'))
sheet.save(preview/'four_boss_portraits.png');(B/'portrait_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Rendered four original-model front portraits, 16px with dark outline')
