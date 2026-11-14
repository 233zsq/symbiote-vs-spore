"""User-requested front portrait -> 16px + dark outline; no generated fake faces.

Manifest sources must be real front pictures. A crop/mask can isolate the subject;
UV atlases are not portraits. Outputs only declared resources inside the repo.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'docs/FTB任务v4_图标清单.json'

def render(entry):
    src=(ROOT/entry['source']).resolve()
    assert src.is_relative_to(ROOT),src
    pic=Image.open(src).convert('RGBA')
    if entry.get('mask_polygon'):
        alpha=Image.new('L',pic.size,0)
        ImageDraw.Draw(alpha).polygon([tuple(p) for p in entry['mask_polygon']],fill=255)
        pic.putalpha(alpha)
    if entry.get('remove_blue_sky'):
        pixels=list(pic.get_flattened_data()) if hasattr(pic,'get_flattened_data') else list(pic.getdata())
        pic.putdata([(r,g,b,0 if b>r*1.15 and b>g*1.05 and r>100 else a)
                     for r,g,b,a in pixels])
    if entry.get('crop'):pic=pic.crop(tuple(entry['crop']))
    bounds=pic.getbbox(); assert bounds,'empty subject'
    pic=pic.crop(bounds)
    # 14px inner silhouette reserves one pixel for the requested dark outline.
    pic=ImageOps.contain(pic,(14,14),Image.Resampling.LANCZOS)
    alpha=pic.getchannel('A').point(lambda a:255 if a>=100 else 0)
    pic.putalpha(alpha)
    face=Image.new('RGBA',(16,16));face.alpha_composite(pic,((16-pic.width)//2,(16-pic.height)//2))
    mask=face.getchannel('A').filter(ImageFilter.MaxFilter(3))
    result=Image.new('RGBA',(16,16),(35,27,24,0));result.putalpha(mask);result.alpha_composite(face)
    for x,y,color in entry.get('pixel_edits',[]):result.putpixel((x,y),tuple(color))
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    entries=json.loads(MANIFEST.read_text(encoding='utf-8'))['portraits'];ready=0
    for e in entries:
        if not e.get('source'):continue
        actual=render(e)
        assert actual.size==(16,16)
        target=(ROOT/e['output']).resolve()
        assert target.is_relative_to(ROOT/'kubejs/assets/svs/textures/quest/boss'),target
        if args.check:
            with Image.open(target) as saved:assert saved.convert('RGBA').tobytes()==actual.tobytes(),target
        else:target.parent.mkdir(parents=True,exist_ok=True);actual.save(target)
        ready+=1
    print(json.dumps({'ready':ready,'missing_front_sources':len(entries)-ready,'check':args.check}))

if __name__=='__main__':main()
