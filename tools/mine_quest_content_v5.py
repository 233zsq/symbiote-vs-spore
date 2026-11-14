"""Build quest authoring facts from this pack; never import another pack's mechanics."""
import collections,hashlib,json,re,shutil,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/data/quest_content_v5.json'
MODS=Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test/mods')
BACKUP=ROOT/'backups/questbook_v5_rebuild_20261017/before'
if not BACKUP.exists():
    for rel in ['docs/questbook_v2.json','tools/build_questbook_v2.py','config/ftbquests/quests',
                'kubejs/server_scripts/svs_quests_bridge.js','kubejs/server_scripts/svs_quests_v2_bindings.js',
                'kubejs/assets/svs','docs/FTB任务v4_图标清单.json']:
        src=ROOT/rel;dest=BACKUP/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if src.is_dir():shutil.copytree(src,dest)
        else:shutil.copy2(src,dest)
lang={};models=set();recipes=[];loot=collections.defaultdict(list);tags=collections.defaultdict(set);geo=[];evidence={}
def walk_items(value):
    out=set()
    if isinstance(value,dict):
        if value.get('type')=='minecraft:item' and value.get('name'):out.add(value['name'])
        for v in value.values():out.update(walk_items(v))
    elif isinstance(value,list):
        for v in value:out.update(walk_items(v))
    return out
def ingredients(data):
    out=set()
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get('item'),str):out.add(v['item'])
            if isinstance(v.get('tag'),str):out.add('#'+v['tag'])
            for vv in v.values():walk(vv)
        elif isinstance(v,list):
            for vv in v:walk(vv)
    for key in ('key','ingredient','ingredients','base','addition','template','input','inputs'):walk(data.get(key,{}))
    return sorted(out)
def consume(source,raw,jar):
    parts=source.split('/')
    if len(parts)>4 and parts[0]=='assets' and '/models/item/' in source and source.endswith('.json'):
        models.add(parts[1]+':'+source.split('/models/item/',1)[1][:-5])
    if source.endswith('/lang/zh_cn.json') or source.endswith('/lang/en_us.json'):
        try:d=json.loads(raw)
        except (ValueError,UnicodeError):return
        locale=source.rsplit('/',1)[1][:-5]
        for k,v in d.items():
            # Localized keys carry their namespace as part of the raw MC key.
            lang.setdefault(k,{})[locale]=str(v)
        return
    if source.startswith('data/') and source.endswith('.json'):
        try:d=json.loads(raw)
        except (ValueError,UnicodeError):return
        if '/recipes/' in source:
            result=d.get('result',d.get('output',{}));item=result if isinstance(result,str) else result.get('item',result.get('id','')) if isinstance(result,dict) else ''
            if item and ':' in item:recipes.append(dict(result=item,ingredients=ingredients(d),type=d.get('type',''),source=jar+'!/'+source,id=parts[1]+':'+source.split('/recipes/',1)[1][:-5]))
        elif '/loot_tables/' in source:
            for item in walk_items(d):loot[item].append(parts[1]+':'+source.split('/loot_tables/',1)[1][:-5])
        elif '/tags/items/' in source:
            key=parts[1]+':'+source.split('/tags/items/',1)[1][:-5]
            for v in d.get('values',[]):
                if isinstance(v,str):tags[key].add(v)
    if '/geo/' in source and source.endswith('.json'):geo.append(jar+'!/'+source)

for jar in sorted(MODS.glob('*.jar')):
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            if name.startswith(('assets/','data/')) and name.endswith('.json'):
                if any(s in name for s in ('/lang/','/models/item/','/recipes/','/loot_tables/','/tags/items/','/geo/')):
                    consume(name,z.read(name),jar.name)
    evidence[jar.name]=hashlib.sha256(jar.read_bytes()).hexdigest()
# Vanilla item models/names are used only for ordinary Minecraft objects.
vanilla=Path('C:/PCL 正式版 2.8.13/.minecraft/libraries/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-extra.jar')
with zipfile.ZipFile(vanilla) as z:
    for name in z.namelist():
        if name.startswith(('assets/minecraft/','data/minecraft/')) and name.endswith('.json') and any(s in name for s in ('/lang/','/models/item/','/recipes/','/loot_tables/','/tags/items/')):consume(name,z.read(name),vanilla.name)
for base in [ROOT/'config/openloader/resources',ROOT/'kubejs']:
    for p in base.rglob('*.json'):
        if '/assets/' in p.as_posix() or '/data/' in p.as_posix():
            path=p.as_posix();offset=path.find('/assets/') if '/assets/' in path else path.find('/data/')
            consume(path[offset+1:],p.read_bytes(),p.relative_to(ROOT).as_posix())

index=json.loads((ROOT/'docs/data/现版资料索引.json').read_text(encoding='utf-8'))
active_mods={decl['id'] for mod in index['mods'] for decl in mod['declarations']}|{'minecraft','silence_s_defense_tower'}
weapons=json.loads((ROOT/'docs/data/制作资料汇总.json').read_text(encoding='utf-8'))['weapons']
cap={r['id']:(r.get('data') or {}).get('type','') for r in index['resources'] if r['kind']=='weapon_capability'}
weapon_types={r['id']:r.get('data') or {} for r in index['resources'] if r['kind']=='weapon_type'}
def title(id):
    ns,path=id.split(':',1)
    for key in ['item.'+ns+'.'+path,'block.'+ns+'.'+path,'entity.'+ns+'.'+path]:
        v=lang.get(key,{})
        if v.get('zh_cn'):return re.sub('§.','',v['zh_cn'])
        if v.get('en_us'):return v['en_us']
    return path.replace('_',' ').title()
by_result=collections.defaultdict(list)
for v in recipes:by_result[v['result']].append(v)
catalog={};excluded=[]
for w in weapons:
    id=w['id']
    if id not in models or any(t in id for t in ('debug','demo','_spawn_egg')):
        excluded.append(dict(id=id,reason='无当前物品模型' if id not in models else '开发调试物品'));continue
    catalog[id]=dict(id=id,name=title(id),kind='weapon',category=cap.get(id,''),sources=by_result[id],loot=sorted(loot[id]))
# Capability-only weapons cover additions absent from the historical stat sample.
for id,typ in cap.items():
    if id in models and id not in catalog and not any(t in id for t in ('debug','demo','example')):
        catalog[id]=dict(id=id,name=title(id),kind='weapon',category=typ,sources=by_result[id],loot=sorted(loot[id]))
armor_pattern=re.compile(r'_(?:helmet|chestplate|leggings|boots|hood|robe|cuirass|greaves|sabatons|armor_head|armor_chest|armor_legs|armor_feet)$')
curio_ids=set()
def resolve_tag(key,seen=None):
    seen=set() if seen is None else seen
    if key in seen:return set()
    seen.add(key);out=set()
    for v in tags[key]:
        if v.startswith('#'):out.update(resolve_tag(v[1:],seen))
        else:out.add(v)
    return out
for tag in list(tags):
    if tag.startswith('curios:'):curio_ids.update(resolve_tag(tag))
for id in sorted(models):
    kind='armor' if armor_pattern.search(id) else 'curio' if id in curio_ids else None
    if kind and id not in catalog and not any(t in id for t in ('_spawn_egg','dummy','debug','icon_')):
        catalog[id]=dict(id=id,name=title(id),kind=kind,category='',sources=by_result[id],loot=sorted(loot[id]))
# Exact tooltip text belongs to this pack, not the reference modpacks.
for id,entry in catalog.items():
    ns,path=id.split(':',1);prefixes=(f'item.{ns}.{path}.',f'tooltip.{ns}.{path}.',f'item.{ns}.{path}_',f'item.{ns}.{path}sworditem.tooltip',f'item.{ns}.{path}item.tooltip')
    found=[(k,re.sub('§.','',v['zh_cn'])) for k,v in lang.items() if k.startswith(prefixes) and v.get('zh_cn')]
    found.sort(key=lambda kv:re.sub(r'\d+',lambda m:m.group().zfill(5),kv[0]))
    entry['tooltips']=[v for k,v in found][:24]
    typ=cap.get(id,'');tns,tname=typ.split(':',1) if ':' in typ else ['epicfight',typ]
    definition=weapon_types.get(tns+':types/'+tname,weapon_types.get(typ,{}))
    entry['combat_category']=definition.get('category','')
    entry['styles']=list(definition.get('combos',{}))
    entry['skills']=[]
    for skill in dict.fromkeys(definition.get('innate_skills',{}).values()):
        if not isinstance(skill,str) or ':' not in skill:continue
        sn,sk=skill.split(':',1);key='skill.'+sn+'.'+sk
        skill_label=lang.get(key,{}).get('zh_cn',lang.get(key,{}).get('en_us',sk.replace('_',' ')))
        desc=lang.get(key+'.tooltip',{}).get('zh_cn','')
        entry['skills'].append(dict(id=skill,name=re.sub('§.','',skill_label),description=re.sub('§.','',desc)))

# Compatibility assets do not establish registration in this pack; Geckolib demo
# armour is a library development example rather than a player acquisition route.
for id in list(catalog):
    if id.split(':')[0] not in active_mods or id.startswith('geckolib:'):
        excluded.append(dict(id=id,reason='未安装目标模组的兼容资源' if id.split(':')[0] not in active_mods else '前置库开发示例装备'))
        del catalog[id]

out=dict(as_of='2026-10-17',scope='当前安装JAR物品模型∩历史武器/EF能力；护甲部位命名与curios标签；不包含方块与调试品',
         catalog=list(catalog.values()),excluded=excluded,recipes=recipes,loot=dict(loot),
         names={id:title(id) for id in models},geo=geo,jar_sha256=evidence)
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(entries=len(catalog),kind=dict(collections.Counter(v['kind'] for v in catalog.values())),excluded=len(excluded),recipes=len(recipes)),ensure_ascii=False))
