"""Package the rebuilt questbook only; no automatic instance write or game launch."""
import hashlib,json,zipfile
from pathlib import Path
import build_questbook_v2 as builder

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/FTB_v5_完整重建_待用户测试.zip'
REPORT=ROOT/'docs/FTB任务v5_三包精读与完整重建_2026-10-17.md'
data=json.loads(builder.SOURCE.read_text(encoding='utf-8'))
assert data['editorial_version']==5
files,bindings,entries=builder.create(data)
builder.validate_output(files);builder.validate_auxiliary(data,bindings,entries)
paths=sorted((ROOT/'config/ftbquests/quests').rglob('*.snbt'))
paths += [ROOT/'kubejs/server_scripts'/n for n in ('svs_quests_bridge.js','svs_quests_v2_bindings.js')]
textures={v['icon_texture'] for v in data['quests'] if v.get('icon_texture')}
paths += sorted(ROOT/'kubejs/assets/svs'/n.split(':',1)[1] for n in textures)
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert len(manifest)==len(paths)
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,'overlay/'+p.relative_to(ROOT).as_posix())
    z.write(REPORT,'重建与安装说明.md')
    z.writestr('SHA256.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    z.write(ROOT/'backups/questbook_v5_rebuild_20261017/static_verification.json','离线检查结果.json')
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    for name,digest in manifest.items():assert hashlib.sha256(z.read('overlay/'+name)).hexdigest()==digest,name
    assert set(z.namelist())=={'overlay/'+name for name in manifest}|{'SHA256.json','重建与安装说明.md','离线检查结果.json'}
result=dict(path=str(OUT),sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),size=OUT.stat().st_size,
            game_files=len(paths),chapters=len(data['chapters']),quests=len(data['quests']),
            archive_and_hash_validation='PASS',installed=False)
(ROOT/'backups/questbook_v5_rebuild_20261017/delivery_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
