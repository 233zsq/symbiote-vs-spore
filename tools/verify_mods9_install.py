"""Meaningful static acceptance and scope audit; never launches Minecraft."""
import ast,collections,hashlib,json,re,struct,subprocess,sys,tomllib,zipfile
from pathlib import Path
from urllib.parse import unquote
from prepare_mods9_install import ROOT,BACKUP,digest,files_snapshot,write_json

D=ROOT/'docs';OUT=D/'data/模组9收尾校验_2026-10-31.json'
def links(body):return set(re.findall(r'\]\(([^)\n]+)\)',body))
def verify():
 write_json(OUT,{'date':'2026-10-31','status':'checking'})
 payload=json.loads((BACKUP/'payload.json').read_text(encoding='utf-8'))
 baseline=json.loads((BACKUP/'baseline.json').read_text(encoding='utf-8'))
 installed=json.loads((BACKUP/'installation.json').read_text(encoding='utf-8'))
 result={'date':'2026-10-31','evidence':'E0 only','game_launched':False,'instances':{},'repo_protected_changes':[]}
 allowed=set(payload['overlay']);newjars={m['file']:m['sha256'] for m in payload['mods']}
 for row in installed:
  root=Path(row['target']);before=baseline['instances'][row['role']]
  for rel,h in payload['overlay'].items():assert digest(root/rel)==h,(row['role'],rel)
  jars={p.name:digest(p) for p in (root/'mods').glob('*.jar')}
  assert jars=={**before['jars'],**newjars}
  files=files_snapshot(root,['config','defaultconfigs','configureddefaults','kubejs','scripts','resourcepacks'])
  assert {k:v for k,v in files.items() if k not in allowed}==before['files']
  assert {p.name:digest(p) for p in root.glob('options*') if p.is_file()}==before['options_hashes']
  saves={p.relative_to(root).as_posix():[p.stat().st_size,p.stat().st_mtime_ns] for p in (root/'saves').rglob('*') if p.is_file()}
  assert saves==before['saves_metadata']
  assert not any(n.startswith('spawn-') for n in jars)
  result['instances'][row['role']]={'jar_count':len(jars),'payload_files_match':len(allowed),'old_jar_count_preserved':len(before['jars']),'unrelated_config_resource_hashes_preserved':len(before['files']),'options_unchanged':True,'saves_metadata_unchanged':True}
 for rel,h in baseline['repo_protected'].items():
  if rel in ['index.toml','pack.toml']:continue
  if digest(ROOT/rel)!=h:result['repo_protected_changes'].append(rel)
 assert not result['repo_protected_changes'],result['repo_protected_changes']
 result['repo_protected_files_checked']=len(baseline['repo_protected'])-2
 # Verify only this batch changed shared pack metadata.
 old=tomllib.loads((BACKUP/'repo_before/index.toml').read_text(encoding='utf-8'))
 current=tomllib.loads((ROOT/'index.toml').read_text(encoding='utf-8'))
 current_map={e['file']:e for e in current['files']};assert len(current_map)==len(current['files'])
 for row in old['files']:
  if row['file'] not in payload['root_paths']:assert current_map[row['file']]==row
 for rel in payload['root_paths']:assert current_map[rel]['hash']==digest(ROOT/rel)
 assert tomllib.loads((ROOT/'pack.toml').read_text(encoding='utf-8'))['index']['hash']==digest(ROOT/'index.toml')
 result['packwiz_batch_entries_verified']=8
 result['other_index_entries_preserved']=sum(e['file'] not in payload['root_paths'] for e in old['files'])
 # Complete source-byte and dependency class checks.
 namespaces={};declarations={};major={}
 for m in payload['mods']:
  p=BACKUP/'overlay/mods'/m['file'];assert digest(p)==m['sha256']
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   data=tomllib.loads(z.read('META-INF/mods.toml').decode('utf-8-sig'));assert data['modLoader']=='javafml'
   mod=data['mods'][0];assert mod['modId'] not in declarations
   declarations[mod['modId']]=data;namespaces[m['file']]=set(z.namelist())
   major[m['file']]=dict(collections.Counter(str(int.from_bytes(z.read(n)[6:8],'big')) for n in z.namelist() if n.endswith('.class')))
   assert set(major[m['file']])=={'61'}
 for item in baseline['intake']:
  assert digest(Path(item['path']))==item['sha256']
  if item['enabled']:assert newjars[item['file']]==item['sha256']
  else:assert digest(BACKUP/'candidates_disabled'/item['file'])==item['sha256']
 available={'forge','minecraft'}
 root=Path(installed[0]['target'])
 for p in (root/'mods').glob('*.jar'):
  with zipfile.ZipFile(p) as z:
   if 'META-INF/mods.toml' not in z.namelist():continue
   data=tomllib.loads(z.read('META-INF/mods.toml').decode('utf-8-sig'));available.update(m['modId'] for m in data['mods'])
 requirements=[]
 for mod,data in declarations.items():
  for dep in data.get('dependencies',{}).get(mod,[]):
   if dep['mandatory']:
    assert dep['modId'] in available,(mod,dep)
    requirements.append({'mod':mod,'dependency':dep['modId'],'range':dep['versionRange'],'present':True})
 result['mandatory_dependency_presence']=requirements
 tree=ast.parse((ROOT/'tools/audit_mods9.py').read_text(encoding='utf-8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='strings')
 parser_scope={'struct':struct};exec(compile(ast.Module(body=[fn],type_ignores=[]),'constant_pool','exec'),parser_scope)
 result['dependency_class_checks']=[]
 for file,prefix,lib in [('bookofdragons-1.31-1.20.1.jar','mod/azure/azurelib/','azurelib-neo-1.20.1-3.1.3.jar'),('hadean_breathe-0.25.7-1.20.1-forge.jar','vzling/','vzling-0.98.8-1.20.1-forge.jar')]:
  refs=set()
  with zipfile.ZipFile(BACKUP/'overlay/mods'/file) as z:
   for n in z.namelist():
    if n.endswith('.class'):refs.update(s for s in parser_scope['strings'](z.read(n)) if s.startswith(prefix) and not any(c in s for c in ';(<') and s+'.class' not in namespaces[file])
  missing=sorted(s for s in refs if s+'.class' not in namespaces[lib]);assert not missing
  result['dependency_class_checks'].append({'file':file,'library':lib,'references':len(refs),'missing':missing,'method_abi_and_gameplay_verified':False})
 cfg=tomllib.loads((ROOT/'config/super-tier-magic-common.toml').read_text(encoding='utf-8'))
 for group,keys in {'skills':['thunderAbyss','thunderStormTerrainDamage'],'air':['flightCheat','survivalCloudFlight'],'lightning':['boltTerrainDamage'],'ancientZombie':['naturalSpawns','reinforcementsEnabled'],'lordOfSwords':['naturalSpawns']}.items():
  assert all(cfg[group][k] is False for k in keys)
 assert cfg['swordPercentage']=={'minimum':0.0,'maximum':0.0}
 frozen=ROOT/'config/openloader/data/svs_mods9_freeze'
 assert json.loads((frozen/'pack.mcmeta').read_text(encoding='utf-8'))['pack']['pack_format']==15
 tag=json.loads((frozen/'data/svs_mods9/tags/worldgen/biome/disabled_generation.json').read_text(encoding='utf-8'));assert tag=={'replace':True,'values':[]}
 feature_files=list(frozen.rglob('forge/biome_modifier/*.json'));assert len(feature_files)==6
 for p in feature_files:assert json.loads(p.read_text(encoding='utf-8'))=={'type':'forge:none'}
 structure_files=list(frozen.rglob('worldgen/structure/*.json'));assert len(structure_files)==8
 for p in structure_files:assert json.loads(p.read_text(encoding='utf-8'))['biomes']=='#svs_mods9:disabled_generation'
 result['freeze_static_checks']={'structure_biomes':8,'feature_modifiers':6,'empty_tag':True,'super_tier_policy':True,'runtime_generation_unverified':True}
 delivery=json.loads((BACKUP/'delivery.json').read_text(encoding='utf-8'));assert digest(Path(delivery['path']))==delivery['sha256']
 with zipfile.ZipFile(delivery['path']) as z:
  assert z.testzip() is None
  for rel,h in payload['overlay'].items():assert hashlib.sha256(z.read('overlay/'+rel)).hexdigest()==h
  assert not any('spawn-4.0.8' in n for n in z.namelist())
 result['delivery_crc_hashes_match']=True
 # Current source check is a read-only generator mode, not a rewrite.
 q=subprocess.run([sys.executable,str(ROOT/'tools/build_questbook_v2.py'),'--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',check=True)
 result['quest_source_check']=json.loads(q.stdout.strip());assert result['quest_source_check']['check']=='PASS'
 # Verify new links only; do not rewrite unrelated broken historical references.
 changed=[p for p in (BACKUP/'docs_before').rglob('*.md')]
 checked_names={p.relative_to(BACKUP/'docs_before').as_posix() for p in changed}
 checked_names|={'模组9_入包与回退记录_2026-10-31.md','剧情与FTB施工计划_2026-10-31.md','DeepSeek建议_采纳对照_2026-10-31.md','资料库更新记录_2026-10-31.md','archive/2026-10-31_入口整理前/_归档说明.md'}
 checked=0;broken=[]
 for name in sorted(checked_names):
  p=D/name;assert b'\r\r\n' not in p.read_bytes(),('Double CRLF',name)
  prior=BACKUP/'docs_before'/name;oldlinks=links(prior.read_text(encoding='utf-8-sig')) if prior.exists() else set()
  for href in links(p.read_text(encoding='utf-8-sig'))-oldlinks:
   if '://' in href or href.startswith('#'):continue
   clean=href.strip('<>').split('#')[0];dest=p.parent/unquote(clean);checked+=1
   if not dest.exists():broken.append({'file':name,'href':href})
 assert not broken,broken
 result['new_local_links_checked']=checked;result['broken_new_links']=broken
 guide=json.loads((D/'data/DeepSeek建议来源_2026-10-31.json').read_text(encoding='utf-8'))
 assert digest(Path(guide['copy']))==guide['sha256']==digest(Path(guide['source']))
 result['reference_copy_identical']=True
 result['archived_originals_verified']=0;ledger=[]
 for p in changed:
  name=p.relative_to(BACKUP/'docs_before');current=D/name;archived=D/'archive/2026-10-31_入口整理前'/name
  if archived.exists():assert archived.read_bytes()==p.read_bytes();result['archived_originals_verified']+=1
  ledger.append({'path':str(current),'before_sha256':digest(p),'after_sha256':digest(current)})
 write_json(BACKUP/'docs_changes.json',ledger)
 for name in ['prepare_mods9_install.py','build_mods9_overlay.py','install_mods9.py','update_mods9_install_docs.py','finish_mods9_navigation.py','verify_mods9_install.py']:
  p=ROOT/'tools'/name;compile(p.read_text(encoding='utf-8'),str(p),'exec')
 result['python_source_checks']=6;result['status']='PASS'
 result['not_verified']=['game loading','dedicated server loading','generation in new chunks','combat and riding','Quest Enhance save/network','multiplayer']
 write_json(OUT,result)
 print(json.dumps({'status':result['status'],'instance_jars':{k:v['jar_count'] for k,v in result['instances'].items()},'repo_protected_files':result['repo_protected_files_checked'],'new_links':checked,'archived_originals':result['archived_originals_verified'],'evidence':'E0; no game launch'},ensure_ascii=False))

if __name__=='__main__':verify()
