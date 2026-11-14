"""Build a scoped, verified FTB update. Never installs into a running client."""
import hashlib,json,zipfile
from pathlib import Path
import build_questbook_v2 as b
R=Path(__file__).resolve().parents[1];B=R/'backups/questbook_v6_20261017';OUT=R/'deliverables/FTB_v6_王途与分级武库_更新包.zip'
d=json.loads(b.SOURCE.read_text(encoding='utf-8'));assert d['editorial_version']==6
assert not d.get('content_revision'),'Use package_legendary_bosses.py for the current expanded source; preserve the original v6 package'
files,bindings,entries=b.create(d);b.validate_output(files);b.validate_auxiliary(d,bindings,entries)
assert json.loads((B/'static_verification.json').read_text(encoding='utf-8'))['result']=='PASS'
paths=list((R/'config/ftbquests/quests').rglob('*.snbt'))
paths+=[R/'kubejs/server_scripts'/n for n in ['svs_quests_bridge.js','svs_quests_v2_bindings.js']]
paths+=list((R/'kubejs/assets/svs/textures/quest').rglob('*.png'))
paths+=[R/'kubejs/assets/ftbquests'/n for n in ['textures/item/book.png','lang/zh_cn.json','lang/en_us.json']]
paths=sorted(set(paths));manifest={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert all('saves' not in p.parts and p.suffix in ['.snbt','.js','.png','.json'] for p in paths)
installed=False
if (B/'installation.json').exists():
    previous=json.loads((B/'installation.json').read_text(encoding='utf-8'));target=Path(previous['target'])
    installed=previous.get('manifest')==manifest and all((target/n).exists() and hashlib.sha256((target/n).read_bytes()).hexdigest()==h for n,h in manifest.items())
policy={'replace_directories':['config/ftbquests/quests'],
        'overlay_exact_files':sorted(p for p in manifest if not p.startswith('config/ftbquests/quests/')),
        'preconditions':['Exit test client and its integrated server','Compare local task edits before replacement','Back up existing target files and independently preserve any test world'],
        'do_not_touch':['saves','options.txt','mods','world generation configuration','other scripts and assets'],
        'progress_policy':'New E6 task IDs; never silently migrate old completion or claims; use a fresh independent test world',
        'installed':installed,'game_acceptance':'user-owned; not performed'}
extras={'重写与安装说明.md':R/'docs/FTB任务v6_王途与分级武库重写.md','离线检查结果.json':B/'static_verification.json',
        '主线与奖励校样.png':B/'previews/campaign_and_rewards.png','章节徽记校样.png':B/'previews/chapter_insignia.png'}
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,'overlay/'+p.relative_to(R).as_posix())
    for name,p in extras.items():z.write(p,name)
    z.writestr('SHA256.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    z.writestr('安装范围.json',json.dumps(policy,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={'overlay/'+p for p in manifest}|set(extras)|{'SHA256.json','安装范围.json'}
    for p,h in manifest.items():assert hashlib.sha256(z.read('overlay/'+p)).hexdigest()==h,p
result={'path':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'size':OUT.stat().st_size,
        'game_files':len(paths),'archive_and_hash_validation':'PASS','installed':installed}
(B/'delivery_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
