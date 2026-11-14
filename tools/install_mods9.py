"""Scoped, backed-up installation of the authorized mods9 overlay.
No game launch, process termination, quest replacement, or unrelated sync.
"""
import argparse,datetime,json,shutil,subprocess,time
from pathlib import Path
from prepare_mods9_install import ROOT,BACKUP,TARGETS,digest,files_snapshot,write_json

def no_java():
 cmd='$ErrorActionPreference="Stop"; $a=@(Get-Process java,javaw -ErrorAction SilentlyContinue | ForEach-Object {$_.Id}); $b=@(Get-CimInstance Win32_Process -Filter "Name=\'java.exe\' OR Name=\'javaw.exe\'" | ForEach-Object {$_.ProcessId}); [PSCustomObject]@{process=$a;cim=$b} | ConvertTo-Json -Compress'
 result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',cmd],capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=0x08000000,check=True)
 data=json.loads(result.stdout.strip());assert not data['process'] and not data['cim'],('Java is running; do not install',data)
 return data
def saves_state(root):return {p.relative_to(root).as_posix():[p.stat().st_size,p.stat().st_mtime_ns] for p in (root/'saves').rglob('*') if p.is_file()}
def options_state(root):return {p.name:digest(p) for p in root.glob('options*') if p.is_file()}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--target',choices=['test','mother','both'],default='both');parser.add_argument('--rollback',action='store_true');args=parser.parse_args()
 if args.rollback:return rollback()
 payload=json.loads((BACKUP/'payload.json').read_text(encoding='utf-8'));base=json.loads((BACKUP/'baseline.json').read_text(encoding='utf-8'))
 allowed=set(payload['overlay']);jarnames={m['file'] for m in payload['mods']}
 assert len(jarnames)==8 and not any('spawn-' in n for n in jarnames)
 for rel,h in payload['overlay'].items():
  assert rel=='config/super-tier-magic-common.toml' or rel.startswith('config/openloader/data/svs_mods9_freeze/') or rel in {'mods/'+n for n in jarnames},rel
  assert digest(BACKUP/'overlay'/rel)==h,rel
 roles=['test','mother'] if args.target=='both' else [args.target]
 no_java();time.sleep(1);no_java()
 # Validate both destinations before writing the first one.
 for role in roles:
  root=TARGETS[role].resolve();old=base['instances'][role]
  assert {p.name:digest(p) for p in (root/'mods').glob('*.jar')}==old['jars'],('Mods changed since preflight',role)
  assert files_snapshot(root,['config','defaultconfigs','configureddefaults','kubejs','scripts','resourcepacks'])==old['files'],('Configuration changed since preflight',role)
  for rel in allowed:
   p=(root/rel).resolve();assert p.is_relative_to(root) and not p.exists(),('Unexpected existing file',role,rel)
  assert saves_state(root)==old['saves_metadata'] and options_state(root)==old['options_hashes'],('World/options changed since preflight',role)
 records=[];stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
 for role in roles:
  no_java();root=TARGETS[role].resolve();backup=BACKUP/('installed_'+role+'_'+stamp);backup.mkdir(parents=True,exist_ok=False)
  oldmods={p.name:digest(p) for p in (root/'mods').glob('*.jar')}
  oldfiles=files_snapshot(root,['config','defaultconfigs','configureddefaults','kubejs','scripts','resourcepacks'])
  oldsave=saves_state(root);oldoptions=options_state(root);written=[]
  write_json(backup/'before.json',{'target':str(root),'jars':oldmods,'files':oldfiles,'saves_metadata':oldsave,'options_hashes':oldoptions,'new_paths':sorted(allowed)})
  try:
   # Config restrictions precede mod JARs; only this batch is ever copied.
   for rel in sorted(allowed,key=lambda s:(s.startswith('mods/'),s)):
    p=(root/rel).resolve();assert p.is_relative_to(root) and not p.exists()
    p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BACKUP/'overlay'/rel,p);written.append(rel)
   assert all(digest(root/rel)==h for rel,h in payload['overlay'].items())
   nowmods={p.name:digest(p) for p in (root/'mods').glob('*.jar')}
   assert set(nowmods)==set(oldmods)|jarnames
   assert all(nowmods[k]==h for k,h in oldmods.items())
   nowfiles=files_snapshot(root,['config','defaultconfigs','configureddefaults','kubejs','scripts','resourcepacks'])
   assert {k:v for k,v in nowfiles.items() if k not in allowed}==oldfiles
   assert set(nowfiles)-set(oldfiles)=={r for r in allowed if r.startswith('config/')}
   assert saves_state(root)==oldsave and options_state(root)==oldoptions
  except Exception:
   # Remove only newly introduced, verified paths. Preserve any unexpected edit.
   for rel in reversed(written):
    p=(root/rel).resolve();assert p.is_relative_to(root) and rel in allowed
    if p.exists() and digest(p)==payload['overlay'][rel]:p.unlink()
   raise
  record={'date':'2026-10-31','role':role,'target':str(root),'backup':str(backup),'installed':True,'new_jars':len(jarnames),'jar_count_before':len(oldmods),'jar_count_after':len(nowmods),'manifest':payload['overlay'],'all_payload_hashes_match':True,'existing_jars_unchanged':True,'unrelated_config_resources_unchanged':True,'saves_metadata_unchanged':True,'options_hashes_unchanged':True,'game_launched':False,'evidence':'E0 file installation; loading and gameplay unverified'}
  write_json(backup/'installation.json',record);records.append(record)
  write_json(BACKUP/'installation.json',records);write_json(ROOT/'docs/data/模组9安装核对_2026-10-31.json',records)
  print(role,'installed',len(allowed),'files; jars',len(oldmods),'->',len(nowmods),flush=True)

def rollback():
 records=json.loads((BACKUP/'installation.json').read_text(encoding='utf-8'));no_java();time.sleep(1);no_java()
 # Refuse partial rollback if a new config/JAR was modified by the player/game.
 for row in records:
  root=Path(row['target']).resolve();assert root in {p.resolve() for p in TARGETS.values()}
  for rel,h in row['manifest'].items():
   p=(root/rel).resolve();assert p.is_relative_to(root) and p.exists() and digest(p)==h,('Changed installed file; preserve and merge before rollback',rel)
 for row in reversed(records):
  no_java();root=Path(row['target']).resolve()
  for rel in row['manifest']:
   p=(root/rel).resolve();assert p.is_relative_to(root);p.unlink()
  row['rolled_back']=True
 write_json(BACKUP/'rollback.json',records);print('Rolled back only this batch; empty directories retained')

if __name__=='__main__':main()
