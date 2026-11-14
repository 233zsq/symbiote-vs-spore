"""Read-only intake and reference inventory for the user's 2026-10-26 review.
Writes evidence only in docs/data and backups; never deploys or launches a game.
"""
import collections,hashlib,json,re,struct,tomllib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'backups/mods9_review_20261026';B.mkdir(parents=True,exist_ok=True)
NEW=Path('E:/mcmp_test/dl/新加入的模组9');V=Path('C:/PCL 正式版 2.8.13/.minecraft/versions')
ROOTS={'test':V/'test','mother':Path('E:/SvS_整合包_副本'),'immersive_fight':V/'Immersive Fight 4.2.9','otherworld':V/'Otherworld'}
URLS={'spawn':'https://www.curseforge.com/minecraft/mc-mods/spawn-mod','super_tier_magic':'https://www.curseforge.com/minecraft/mc-mods/super-tier-magic','hadean_breathe':'https://modrinth.com/mod/hadean-breathe/versions','quest_enhance':'https://www.curseforge.com/minecraft/mc-mods/quest-enhance','celestisynth':'https://www.curseforge.com/minecraft/mc-mods/celestisynth','celestisynth_fix':'https://www.curseforge.com/minecraft/mc-mods/celestisynth-fix','bookofdragons':'https://www.curseforge.com/minecraft/mc-mods/book-of-dragons'}
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metadata(z):
    result={}
    for n in ['META-INF/mods.toml','META-INF/neoforge.mods.toml','fabric.mod.json','META-INF/jarjar/metadata.json','META-INF/MANIFEST.MF']:
        if n not in z.namelist():continue
        raw=z.read(n).decode('utf-8-sig',errors='replace')
        try:result[n]=json.loads(raw) if n.endswith('.json') else tomllib.loads(raw) if n.endswith('.toml') else raw
        except Exception as e:result[n]={'parse_error':str(e),'raw':raw}
    return result
def declarations(meta):
    vals=[]
    for path,d in meta.items():
        if path.endswith('.toml') and isinstance(d,dict):
            for m in d.get('mods',[]):vals.append({**m,'loader':d.get('modLoader'),'loaderVersion':d.get('loaderVersion'),'license':d.get('license'),'dependencies':d.get('dependencies',{}).get(m['modId'],[])})
    if not vals and 'fabric.mod.json' in meta and meta['fabric.mod.json'].get('id'):
        f=meta['fabric.mod.json'];vals.append(dict(modId=f['id'],version=f.get('version'),displayName=f.get('name'),loader='fabric',dependencies=f.get('depends',{})))
    return vals
def strings(data):
    if data[:4]!=b'\xca\xfe\xba\xbe':return []
    count=struct.unpack_from('>H',data,8)[0];pos=10;i=1;out=[]
    while i<count:
        tag=data[pos];pos+=1
        if tag==1:
            n=struct.unpack_from('>H',data,pos)[0];pos+=2;out.append(data[pos:pos+n].decode('utf-8',errors='replace'));pos+=n
        elif tag in [3,4]:pos+=4
        elif tag in [5,6]:pos+=8;i+=1
        elif tag in [7,8,16,19,20]:pos+=2
        elif tag in [9,10,11,12,17,18]:pos+=4
        elif tag==15:pos+=3
        else:raise ValueError(tag)
        i+=1
    return out
def readjar(p,full=False):
    with zipfile.ZipFile(p) as z:
        meta=metadata(z);nms=z.namelist();result={'file':p.name,'path':str(p),'size':p.stat().st_size,'sha256':hashfile(p),'metadata':meta,'declarations':declarations(meta)}
        if full:
            assert z.testzip() is None
            resources=[n for n in nms if n.startswith(('data/','assets/')) and n.endswith('.json')]
            result['resources']=resources;result['classes']=[n for n in nms if n.endswith('.class')];result['class_versions']=dict(collections.Counter(str(int.from_bytes(z.read(n)[6:8],'big')) for n in result['classes']))
            kinds=['forge/biome_modifier','worldgen/biome','worldgen/configured_feature','worldgen/placed_feature','worldgen/structure','worldgen/structure_set','dimension_type','dimension','structures','recipes','loot_tables','advancements','epicfight_mobpatch','capabilities/weapons/types','capabilities/weapons','skills','origins','origin_layers','powers']
            result['resource_counts']=dict(collections.Counter(next((k for k in kinds if re.match(r'^data/[^/]+/'+re.escape(k)+r'/',n)),'tags' if re.match(r'^data/[^/]+/tags/',n) else 'assets' if n.startswith('assets/') else 'other_data') for n in resources))
            result['resource_count_scope']='Exact data/<namespace>/<kind>/ prefix; tags and assets separated; JSON only.'
            result['mixins']={n:json.loads(z.read(n)) for n in nms if n.endswith('.json') and ('mixins' in n or n.endswith('.mixin.json')) and not n.endswith('refmap.json')}
            result['languages']={n:json.loads(z.read(n)) for n in nms if re.match(r'assets/[^/]+/lang/(en_us|zh_cn|zh_tw)\.json$',n)}
            result['class_signals']={};result['nested']=[n for n in nms if n.endswith('.jar')]
            dest=B/'extracted'/p.stem
            for n in result['classes']:
                vals=strings(z.read(n));matches=[s for s in vals if any(k in s.lower() for k in ['config','celestisynth','epicfight','irons_spellbooks','origins','justlevel','worldgen','terrablender','quest_enhance','ftbquests','spellbook','skilltree','attribute','spawnplacement','mount','tamable','tameable','saddle'])]
                if matches:result['class_signals'][n]=matches
            for n in nms:
                if n.startswith('data/') and n.endswith('.json') or n in ['META-INF/mods.toml','fabric.mod.json'] or (n.endswith('.json') and ('mixins' in n) and 'refmap' not in n):
                    destp=dest/n;destp.parent.mkdir(parents=True,exist_ok=True);destp.write_bytes(z.read(n))
            for n in result['languages']:
                destp=dest/n;destp.parent.mkdir(parents=True,exist_ok=True);destp.write_bytes(z.read(n))
        return result
report={'date':'2026-10-26','scope':'Offline intake only; new mod and reference resources are not installed or runtime-verified','intake':[readjar(p,True) for p in sorted(NEW.glob('*.jar'))],'instances':{},'references':{}}
for role,root in ROOTS.items():
    jars=[readjar(p) for p in sorted((root/'mods').glob('*.jar'))]
    refs={p.relative_to(root).as_posix():hashfile(p) for folder in ['config','defaultconfigs','configureddefaults','kubejs','scripts','resourcepacks'] if (root/folder).exists() for p in (root/folder).rglob('*') if p.is_file()}
    section={'root':str(root),'jar_count':len(jars),'jars':jars,'config_resource_hashes':refs}
    report['instances' if role in ['test','mother'] else 'references'][role]=section
dest=R/'docs/data/模组9审查_2026-10-26.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for e in report['intake']:
    print('\nINTAKE',e['file'],e['sha256'],'Java',e['class_versions'])
    for m in e['declarations']:print(json.dumps(m,ensure_ascii=False))
    print('resources',e['resource_counts'],'langs',[(k,len(v)) for k,v in e['languages'].items()],'mixins',json.dumps(e['mixins'],ensure_ascii=False))
for role,s in {**report['instances'],**report['references']}.items():print('INSTANCE',role,s['jar_count'],'config resources',len(s['config_resource_hashes']))
print('Evidence saved',dest)
