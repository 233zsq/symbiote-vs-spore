"""Package authorized local mod + task/language integration; does not install.
Original ARR JAR remains byte-for-byte intact. Author permits packs with backlink.
"""
import hashlib,json,re,tomllib,zipfile
from pathlib import Path
import build_questbook_v2 as b
R=Path(__file__).resolve().parents[1];B=R/'backups/legendary_bosses_20261018'
O=R/'deliverables/LegendaryBosses_0.6.1_SvS_剧情任务汉化更新包.zip'
d=json.loads(b.SOURCE.read_text(encoding='utf-8'));assert d['content_revision']=='6.1-legendarybosses-20261018'
files,bindings,entries=b.create(d);b.validate_output(files);b.validate_auxiliary(d,bindings,entries)
assert json.loads((B/'static_verification.json').read_text(encoding='utf-8'))['result']=='PASS'
paths=list((R/'config/ftbquests/quests').rglob('*.snbt'))
paths+=[R/'kubejs/server_scripts'/s for s in ['svs_quests_bridge.js','svs_quests_v2_bindings.js']]
paths+=list((R/'kubejs/assets/svs/textures/quest').rglob('*.png'))
paths+=list((R/'kubejs/assets/ftbquests').rglob('*.png'))+list((R/'kubejs/assets/ftbquests/lang').glob('*.json'))
paths+=[R/'kubejs/assets/legendarybosses/lang/zh_cn.json',R/'config/Legendary Bosses/legendarybosses.toml']
paths+=list((R/'config/openloader/data/svs/data/legendarybosses').rglob('*.json'))
overlay={p.relative_to(R).as_posix():p for p in sorted(set(paths))}
jar=B/'legendarybosses-0.6.1-beta.jar';overlay['mods/'+jar.name]=jar
manifest={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in overlay.items()}
assert manifest['mods/'+jar.name]=='86834189f19c693b6059e8fe76bb5fe95cf61e263dd52350409c967c8e9431d7'
policy={'installed':False,'reason':'User is playing; files first, no hot replacement',
        'replace_directory':'config/ftbquests/quests','overlay_files':sorted(n for n in manifest if not n.startswith('config/ftbquests/quests/')),
        'target_test':'C:/PCL 正式版 2.8.13/.minecraft/versions/test','target_mother':'E:/SvS_整合包_副本',
        'do_not_touch':['saves','options.txt','other mod JARs','worldgen','unrelated scripts'],
        'preserved_existing_E6_progress':True,'new_native_advancements_may_recognize_prior_wins':True,
        'launch_game':False,'acceptance':'user-owned; not performed'}
extras={'审查与安装说明.md':R/'docs/Legendary_Bosses_审查与入包_2026-10-18.md','剧情v5增补.md':R/'docs/剧情重写_v5_旧世四传说与造界者.md',
        '静态检查.json':B/'static_verification.json','四Boss头像校样.png':B/'previews/four_boss_portraits.png',
        'packwiz/legendary-bosses.pw.toml':R/'mods/legendary-bosses.pw.toml'}
O.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(O,'w',zipfile.ZIP_DEFLATED) as z:
    for n,p in overlay.items():z.write(p,'overlay/'+n)
    for n,p in extras.items():z.write(p,n)
    z.writestr('SHA256.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    z.writestr('安装范围.json',json.dumps(policy,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(O) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={'overlay/'+n for n in overlay}|set(extras)|{'SHA256.json','安装范围.json'}
    for n,h in manifest.items():assert hashlib.sha256(z.read('overlay/'+n)).hexdigest()==h,n
result=dict(path=str(O),sha256=hashlib.sha256(O.read_bytes()).hexdigest(),size=O.stat().st_size,game_files=len(manifest),installed=False,
            crc_and_hash_validation='PASS',jar_unmodified=True)
(B/'delivery_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Refresh the new mod's scoped packwiz files. Leave all unrelated entries intact.
p=R/'index.toml';parts=re.split(r'(?=\[\[files\]\])',p.read_text(encoding='utf-8'))
newpaths={n:path for n,path in overlay.items() if n.startswith(('kubejs/assets/legendarybosses/','config/Legendary Bosses/','config/openloader/data/svs/data/legendarybosses/'))}
newpaths['mods/legendary-bosses.pw.toml']=R/'mods/legendary-bosses.pw.toml'
keep=[block.strip() for block in parts[1:] if tomllib.loads(block)['files'][0]['file'] not in newpaths]
for name,path in sorted(newpaths.items()):
    block='[[files]]\nfile = '+json.dumps(name)+'\nhash = "'+hashlib.sha256(path.read_bytes()).hexdigest()+'"'
    if name.endswith('.pw.toml'):block+='\nmetafile = true'
    keep.append(block)
p.write_text(parts[0].rstrip()+'\n\n'+'\n\n'.join(keep)+'\n',encoding='utf-8')
p=R/'pack.toml';s=p.read_text(encoding='utf-8');digest=hashlib.sha256((R/'index.toml').read_bytes()).hexdigest()
s=re.sub(r'(\[index\][\s\S]*?\nhash = ")[^"]+("\s*\n)',lambda m:m[1]+digest+m[2],s,count=1);p.write_text(s,encoding='utf-8')
assert tomllib.loads(s)['index']['hash']==digest
print(json.dumps(result,ensure_ascii=False))
