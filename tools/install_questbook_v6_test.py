"""Scoped installation after explicit prior install authorization; no launch.
Refuses Java processes, unknown edits to either production bridge, or wrong paths.
Run with the external filesystem permission; no worlds/options/JARs are modified.
"""
import datetime,hashlib,json,shutil,subprocess,time,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'backups/questbook_v6_20261017'
TARGET=Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test').resolve()
assert TARGET==Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test').resolve()
def no_java():
    cmd="$ErrorActionPreference='Stop'; $a=@(Get-Process java,javaw -ErrorAction SilentlyContinue); $b=@(Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\"); [PSCustomObject]@{process=@($a | ForEach-Object {$_.Id});cim=@($b | ForEach-Object {$_.ProcessId})} | ConvertTo-Json -Compress"
    r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',cmd],capture_output=True,text=True,check=True,creationflags=0x08000000)
    x=json.loads(r.stdout.strip());assert not x['process'] and not x['cim'],('Game/Java is running; no installation',x)
    return x
no_java()
package=json.loads((B/'delivery_verification.json').read_text(encoding='utf-8'));p=Path(package['path'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==package['sha256']
with zipfile.ZipFile(p) as z:
    manifest=json.loads(z.read('SHA256.json'))
    for rel,h in manifest.items():assert hashlib.sha256(z.read('overlay/'+rel)).hexdigest()==h
base=json.loads((R/'backups/questbook_v5_rebuild_20261017/installation_final.json').read_text(encoding='utf-8'))['manifest']
for rel in ['kubejs/server_scripts/svs_quests_bridge.js','kubejs/server_scripts/svs_quests_v2_bindings.js']:
    assert hashlib.sha256((TARGET/rel).read_bytes()).hexdigest()==base[rel],('Bridge changed; merge before installation',rel)
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');backup=B/('test_before_install_'+stamp);backup.mkdir(parents=True)
questdir=(TARGET/'config/ftbquests/quests').resolve();staged=questdir.with_name('quests.__v6_staged_'+stamp);old=questdir.with_name('quests.__v5_saved_'+stamp)
for path in [questdir,staged,old]:assert path.is_relative_to(TARGET/'config/ftbquests') and path!=TARGET,path
assert not staged.exists() and not old.exists()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def world_state():
    return {p.relative_to(TARGET).as_posix():[p.stat().st_size,p.stat().st_mtime_ns] for p in (TARGET/'saves').rglob('*') if p.is_file()}
world_before=world_state();options=TARGET/'options.txt';option_before=digest(options) if options.exists() else None
shutil.copytree(questdir,backup/'config/ftbquests/quests')
existing={}
for rel in manifest:
    dst=(TARGET/rel).resolve();assert dst.is_relative_to(TARGET)
    if not rel.startswith('config/ftbquests/quests/') and dst.exists():
        dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,dest);existing[rel]=digest(dst)
test_world=TARGET/'saves/SVS_Prologue_V4_20261017'
if test_world.exists():shutil.copytree(test_world,backup/'independent_test_world/SVS_Prologue_V4_20261017')
if options.exists():shutil.copy2(options,backup/'options.txt')
with zipfile.ZipFile(p) as z:
    for rel,h in manifest.items():
        if rel.startswith('config/ftbquests/quests/'):
            dst=staged/rel.removeprefix('config/ftbquests/quests/');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read('overlay/'+rel));assert digest(dst)==h
no_java() # second independent process/CIM view immediately before mutation
swapped=False;original_renamed=False
try:
    questdir.rename(old);original_renamed=True;staged.rename(questdir);swapped=True
    with zipfile.ZipFile(p) as z:
        for rel,h in manifest.items():
            if rel.startswith('config/ftbquests/quests/'):continue
            dst=(TARGET/rel).resolve();assert dst.is_relative_to(TARGET)
            dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read('overlay/'+rel));assert digest(dst)==h
    for rel,h in manifest.items():assert digest(TARGET/rel)==h,rel
    actual={p.relative_to(TARGET).as_posix() for p in questdir.rglob('*.snbt')}
    assert actual=={rel for rel in manifest if rel.startswith('config/ftbquests/quests/')}
    assert world_state()==world_before and (digest(options) if options.exists() else None)==option_before
except Exception:
    # Preserve a failed new graph for diagnosis, restore original graph and files.
    if swapped:
        failed=questdir.with_name('quests.__v6_failed_'+stamp);assert failed.is_relative_to(TARGET/'config/ftbquests')
        questdir.rename(failed);old.rename(questdir)
    elif original_renamed and not questdir.exists():old.rename(questdir)
    for rel in manifest:
        if rel.startswith('config/ftbquests/quests/'):continue
        dst=TARGET/rel;src=backup/rel
        if src.exists():shutil.copy2(src,dst)
        elif dst.exists():
            assert dst.resolve().is_relative_to(TARGET/'kubejs');dst.unlink()
    raise
result={'time':stamp,'target':str(TARGET),'installed':True,'verified_files':len(manifest),'all_hashes_match':True,
        'package_sha256':package['sha256'],'backup':str(backup),'saved_old_graph':str(old),
        'world_file_metadata_unchanged':True,'options_sha256_unchanged':True,'game_launched':False,'mother_written':False,'manifest':manifest}
(B/'installation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='manifest'},ensure_ascii=False))
