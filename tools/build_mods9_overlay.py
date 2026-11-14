"""Build and statically check the six-mod overlay; never launches Minecraft.
Writes only this batch's repo metadata/config and ignored backup/delivery files.
"""
import argparse,collections,hashlib,json,re,shutil,tomllib,zipfile
from pathlib import Path
from prepare_mods9_install import ROOT,BACKUP,INTAKE,digest,write_json

FREEZE='config/openloader/data/svs_mods9_freeze'
CONFIG='config/super-tier-magic-common.toml'
CONFIG_TEXT='''# SvS mods9: approved conservative integration, 2026-10-31.
# Other values are supplied by the original mod defaults on first load.
[skills]
thunderAbyss = false
thunderStormTerrainDamage = false

[air]
flightCheat = false
survivalCloudFlight = false

[swordPercentage]
minimum = 0.0
maximum = 0.0

[lightning]
boltTerrainDamage = false

[ancientZombie]
naturalSpawns = false
reinforcementsEnabled = false

[lordOfSwords]
naturalSpawns = false
'''
SLUGS={
 'bookofdragons-1.31-1.20.1.jar':('book-of-dragons','Book of Dragons'),
 'celestisynth-1.20.1-1.3.4-all.jar':('celestisynth','Celestisynth'),
 'celestisynth_fix-0.1.jar':('celestisynth-fix','Celestisynth Fix'),
 'hadean_breathe-0.25.7-1.20.1-forge.jar':('hadean-breathe','Hadean Breathe'),
 'quest_enhance-1.20.1-forge-3.13.jar':('quest-enhance','FTB Quest Enhance'),
 'super-tier-magic-3.6.3.jar':('super-tier-magic','Super-Tier Magic'),
 'azurelib-neo-1.20.1-3.1.3.jar':('azurelib','AzureLib'),
 'vzling-0.98.8-1.20.1-forge.jar':('vzlinglib','VzlingLib'),
}
def jbytes(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def build():
 baseline=json.loads((BACKUP/'baseline.json').read_text(encoding='utf-8'))
 sources=json.loads((BACKUP/'download_sources.json').read_text(encoding='utf-8'))
 overlay=BACKUP/'overlay';overlay.mkdir(parents=True,exist_ok=True)
 paths={};blocked=[];jars={};mods=[]
 def put(rel,raw):
  p=overlay/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);paths[rel]=p
 for row in baseline['intake']:
  p=Path(row['path']);assert digest(p)==row['sha256']
  if not row['enabled']:
   held=BACKUP/'candidates_disabled'/p.name;held.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,held)
   blocked.append({'file':p.name,'sha256':row['sha256'],'reason':'Worldgen remains frozen; no complete native switch for Spawn biome injection','enabled':False});continue
  assert p.name in sources['intake'] and sources['intake'][p.name]['provider']!='unresolved'
  jars[p.name]=(p,sources['intake'][p.name])
 for name,src in sources['dependencies'].items():jars[name]=(Path(src['path']),{'provider':'curseforge',**src})
 assert set(jars)==set(SLUGS)
 put(FREEZE+'/pack.mcmeta',jbytes({'pack':{'pack_format':15,'description':'SvS mods9: freeze natural structures and mineral/surface features; preserve manual placement resources'}}))
 put(FREEZE+'/data/svs_mods9/tags/worldgen/biome/disabled_generation.json',jbytes({'replace':True,'values':[]}))
 structure_count=feature_count=0
 for name,(p,src) in jars.items():
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   meta=tomllib.loads(z.read('META-INF/mods.toml').decode('utf-8-sig'))
   assert meta['modLoader']=='javafml'
   versions=dict(collections.Counter(str(int.from_bytes(z.read(n)[6:8],'big')) for n in z.namelist() if n.endswith('.class')))
   assert set(versions)=={'61'},(name,versions)
   declarations=meta['mods'];assert len(declarations)==1
   mods.append({'file':name,'mod_id':declarations[0]['modId'],'version':declarations[0]['version'],'sha256':digest(p),'sha512':digest(p,'sha512'),'dependencies':meta.get('dependencies',{}),'source':src,'java_class_versions':versions})
   for n in z.namelist():
    if re.match(r'^data/(celestisynth|hadean_breathe)/forge/biome_modifier/[^/]+\.json$',n):
     native=json.loads(z.read(n));assert native['type']=='forge:add_features',(name,n,native)
     put(FREEZE+'/'+n,jbytes({'type':'forge:none'}));feature_count+=1
    if re.match(r'^data/(hadean_breathe|bookofdragons)/worldgen/structure/[^/]+\.json$',n):
     native=json.loads(z.read(n));native['biomes']='#svs_mods9:disabled_generation'
     put(FREEZE+'/'+n,jbytes(native));structure_count+=1
  put('mods/'+name,p.read_bytes())
 assert feature_count==6 and structure_count==8,(feature_count,structure_count)
 put(CONFIG,CONFIG_TEXT.encode('utf-8'))
 root_changes={}
 for rel,p in paths.items():
  if not rel.startswith('config/'):continue
  root_changes[rel]=p.read_bytes()
 for name,(p,src) in jars.items():
  slug,title=SLUGS[name]
  text=f'name = {json.dumps(title)}\nfilename = {json.dumps(name)}\nside = "both"\n\n[download]\nurl = {json.dumps(src["url"])}\nhash-format = "sha512"\nhash = "{digest(p,"sha512")}"\n'
  if src['provider']=='curseforge':text+=f'\n[update]\n[update.curseforge]\nfile-id = {src["file_id"]}\nproject-id = {src["project_id"]}\n'
  else:text+=f'\n[update]\n[update.modrinth]\nmod-id = {json.dumps(src["project_id"])}\nversion = {json.dumps(src["version_id"])}\n'
  tomllib.loads(text);root_changes['mods/'+slug+'.pw.toml']=text.encode('utf-8')
 # Compare before writing: never absorb an unknown concurrent edit.
 repo_before={}
 for rel,raw in root_changes.items():
  p=ROOT/rel
  if p.exists():
   assert p.read_bytes()==raw,('Unexpected existing batch path',rel)
   repo_before[rel]=digest(p)
  else:repo_before[rel]=None
 index=ROOT/'index.toml';pack=ROOT/'pack.toml'
 old_index=index.read_text(encoding='utf-8');old_pack=pack.read_text(encoding='utf-8')
 for p in [index,pack]:
  dest=BACKUP/'repo_before'/p.name
  dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(p,dest)
 for rel,raw in root_changes.items():
  p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 parts=re.split(r'(?=\[\[files\]\])',old_index)
 old_entries=[tomllib.loads(s)['files'][0] for s in parts[1:]]
 untouched=[s.strip() for s in parts[1:] if tomllib.loads(s)['files'][0]['file'] not in root_changes]
 for rel,raw in sorted(root_changes.items()):
  chunk=f'[[files]]\nfile = {json.dumps(rel)}\nhash = "{hashlib.sha256(raw).hexdigest()}"'
  if rel.endswith('.pw.toml'):chunk+='\nmetafile = true'
  untouched.append(chunk)
 new_index=parts[0].rstrip()+'\n\n'+'\n\n'.join(untouched)+'\n'
 # Concurrency guard immediately before the two shared index mutations.
 assert index.read_text(encoding='utf-8')==old_index and pack.read_text(encoding='utf-8')==old_pack,'Shared pack metadata changed concurrently'
 index.write_text(new_index,encoding='utf-8')
 new_pack=re.sub(r'(\[index\][\s\S]*?\nhash = ")[^"]+("\s*\n)',lambda m:m[1]+digest(index)+m[2],old_pack,count=1)
 pack.write_text(new_pack,encoding='utf-8')
 data=tomllib.loads(new_index);actual={e['file']:e for e in data['files']}
 assert len(actual)==len(data['files'])
 for e in old_entries:
  if e['file'] not in root_changes:assert actual[e['file']]==e
 assert tomllib.loads(new_pack)['index']['hash']==digest(index)
 for rel,raw in root_changes.items():assert actual[rel]['hash']==hashlib.sha256(raw).hexdigest()
 payload={'date':'2026-10-31','scope':'Six content/fix mods plus two dependencies; Spawn excluded; no quest, EF or map implementation','overlay':{rel:digest(p) for rel,p in sorted(paths.items())},'mods':mods,'held':blocked,'root_paths':sorted(root_changes),'root_before':repo_before,'freeze':{'disabled_biome_modifiers':feature_count,'disabled_structure_biomes':structure_count,'empty_biome_tag':'svs_mods9:disabled_generation'},'game_launched':False,'evidence':'E0 static only'}
 write_json(BACKUP/'payload.json',payload)
 out=ROOT/'deliverables/模组9_六模组与前置_2026-10-31.zip';out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for rel,p in sorted(paths.items()):z.write(p,'overlay/'+rel)
  for rel in root_changes:
   if rel.startswith('mods/'):z.write(ROOT/rel,'packwiz/'+Path(rel).name)
  z.writestr('SHA256.json',jbytes(payload['overlay']))
  z.writestr('安装清单.json',jbytes(payload))
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  for rel,h in payload['overlay'].items():assert hashlib.sha256(z.read('overlay/'+rel)).hexdigest()==h
 write_json(BACKUP/'delivery.json',{'path':str(out),'sha256':digest(out),'files':len(paths),'active_jars':len(jars),'spawn_excluded':True,'crc_and_hashes':'PASS'})
 write_json(ROOT/'docs/data/模组9入包清单_2026-10-31.json',payload)
 print(json.dumps({'overlay_files':len(paths),'active_jars':len(jars),'disabled_structures':structure_count,'disabled_features':feature_count,'packwiz_entries':len(jars),'delivery':str(out),'static_result':'PASS'},ensure_ascii=False))

if __name__=='__main__':build()
