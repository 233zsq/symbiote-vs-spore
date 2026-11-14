"""Prepared installer; run only after the user exits the game.
No automatic launch, no process termination, no save edits, no unrelated sync.
"""
import argparse,datetime,hashlib,json,shutil,subprocess,time,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'backups/legendary_bosses_20261018'
TARGETS={'test':Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test').resolve(),'mother':Path('E:/SvS_整合包_副本').resolve()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def no_java():
    cmd="$ErrorActionPreference='Stop'; $p=@(Get-Process java,javaw -ErrorAction SilentlyContinue); $c=@(Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\"); [PSCustomObject]@{process=@($p | ForEach-Object {$_.Id});cim=@($c | ForEach-Object {$_.ProcessId})} | ConvertTo-Json -Compress"
    out=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',cmd],capture_output=True,text=True,check=True,creationflags=0x08000000)
    state=json.loads(out.stdout.strip());assert not state['process'] and not state['cim'],('Java is running; no installation',state)
    for name in ['java.exe','javaw.exe']:
        r=subprocess.run(['tasklist.exe','/FI','IMAGENAME eq '+name],capture_output=True,text=True,check=True,creationflags=0x08000000)
        assert name not in r.stdout.lower(),('Java visible in tasklist; no installation',name)
    return state
def state(base):
    return {p.relative_to(base).as_posix():[p.stat().st_size,p.stat().st_mtime_ns] for p in (base/'saves').rglob('*') if p.is_file()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--target',choices=['test','mother','both'],default='test');args=parser.parse_args()
    no_java();time.sleep(1);no_java()
    delivery=json.loads((B/'delivery_verification.json').read_text(encoding='utf-8'));package=Path(delivery['path']);assert sha(package)==delivery['sha256']
    baseline=json.loads((B/'installation_baseline.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None;manifest=json.loads(z.read('SHA256.json'))
        for rel,h in manifest.items():assert hashlib.sha256(z.read('overlay/'+rel)).hexdigest()==h
        roles=['test','mother'] if args.target=='both' else [args.target];records=[]
        # Validate every target before touching either one.
        for role in roles:
            base=TARGETS[role]
            for rel in manifest:
                dst=(base/rel).resolve();assert dst.is_relative_to(base)
                assert not rel.startswith(('saves/','options','scripts/')),rel
            before=baseline[role]
            actual={p.relative_to(base).as_posix():sha(p) for p in (base/'config/ftbquests/quests').rglob('*') if p.is_file()}
            assert actual==before['quest_files'],('Task source changed; merge before install',role)
            for rel,h in before['existing_overlay'].items():
                assert (base/rel).is_file() and sha(base/rel)==h,('User edit; merge before install',role,rel)
            for rel in manifest:
                if rel not in before['existing_overlay'] and not rel.startswith('config/ftbquests/quests/'):
                    assert not (base/rel).exists(),('Unexpected new user file',role,rel)
        for role in roles:
            no_java();base=TARGETS[role];stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');backup=B/('installed_'+role+'_'+stamp)
            backup.mkdir(parents=True);questdir=(base/'config/ftbquests/quests').resolve();stage=questdir.with_name('quests.__lb_staged_'+stamp);old=questdir.with_name('quests.__before_lb_'+stamp)
            for p in [questdir,stage,old]:assert p.is_relative_to(base/'config/ftbquests') and p!=base
            assert not stage.exists() and not old.exists()
            saves=state(base);options=base/'options.txt';option_sha=sha(options) if options.exists() else None
            jars={p.name:sha(p) for p in (base/'mods').glob('*.jar')}
            shutil.copytree(questdir,backup/'config/ftbquests/quests')
            for rel in manifest:
                dst=base/rel
                if not rel.startswith('config/ftbquests/quests/') and dst.exists():
                    p=backup/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,p)
                if rel.startswith('config/ftbquests/quests/'):
                    p=stage/rel.removeprefix('config/ftbquests/quests/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read('overlay/'+rel))
            no_java();renamed=False;swapped=False;written=[]
            try:
                questdir.rename(old);renamed=True;stage.rename(questdir);swapped=True
                for rel,h in manifest.items():
                    if rel.startswith('config/ftbquests/quests/'):continue
                    dst=base/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read('overlay/'+rel));written.append(rel)
                for rel,h in manifest.items():assert sha(base/rel)==h,rel
                assert {p.relative_to(base).as_posix() for p in questdir.rglob('*.snbt')}=={r for r in manifest if r.startswith('config/ftbquests/quests/')}
                assert state(base)==saves and (sha(options) if options.exists() else None)==option_sha
                assert all(sha(base/'mods'/name)==h for name,h in jars.items()),'Existing mods changed'
            except Exception:
                if swapped:
                    failed=questdir.with_name('quests.__lb_failed_'+stamp);assert failed.is_relative_to(base/'config/ftbquests');questdir.rename(failed);old.rename(questdir)
                elif renamed and not questdir.exists():old.rename(questdir)
                for rel in written:
                    dst=base/rel;src=backup/rel
                    if src.exists():shutil.copy2(src,dst)
                    elif dst.exists():
                        assert dst.resolve().is_relative_to(base) and rel in manifest;dst.unlink()
                raise
            record=dict(role=role,time=stamp,target=str(base),backup=str(backup),old_task_directory=str(old),game_files=len(manifest),
                        package_sha256=delivery['sha256'],all_hashes_match=True,save_file_metadata_unchanged=True,options_unchanged=True,
                        previous_jar_hashes_unchanged=True,new_jar_sha256=manifest['mods/legendarybosses-0.6.1-beta.jar'],game_launched=False)
            (backup/'installation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');records.append(record)
            # Persist successful targets even if a later independent target cannot install.
            (B/'installation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(records,ensure_ascii=False))
if __name__=='__main__':main()
