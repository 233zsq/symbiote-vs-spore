"""Produce a verified quest-only overlay; never writes to a Minecraft instance."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT='docs/FTB任务v4_全书重写与图标_2026-10-17.md'
OUT=ROOT/'deliverables/FTB_v4_任务重写_待用户测试.zip'

def main():
    import build_questbook_v2 as builder
    data=json.loads(builder.SOURCE.read_text(encoding='utf-8'))
    files,bindings,entries=builder.create(data)
    builder.validate_output(files)
    builder.validate_auxiliary(data,bindings,entries)
    paths=sorted((ROOT/'config/ftbquests/quests').rglob('*.snbt'))
    paths += [ROOT/'kubejs/server_scripts'/name for name in
              ('svs_quests_bridge.js','svs_quests_v2_bindings.js')]
    textures={v['icon_texture'] for v in data['quests'] if v.get('icon_texture')}
    paths += sorted(ROOT/'kubejs/assets/svs'/name.split(':',1)[1] for name in textures)
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert len(manifest)==len(paths)
    assert not any('probe' in k or '/saves/' in k or k.endswith('options.txt') for k in manifest)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:z.write(p,'overlay/'+p.relative_to(ROOT).as_posix())
        z.write(ROOT/REPORT,'安装与未验说明.md')
        z.writestr('SHA256.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={'overlay/'+k for k in manifest}|{'安装与未验说明.md','SHA256.json'}
        for name,digest in manifest.items():
            assert hashlib.sha256(z.read('overlay/'+name)).hexdigest()==digest,name
    result=dict(artifact=OUT.relative_to(ROOT).as_posix(),game_files=len(manifest),
                size=OUT.stat().st_size,sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),
                quests=len(data['quests']),chapters=len(data['chapters']),
                validation='ZIP CRC, exact inventory and all overlay SHA256 match repo',
                deployed=False,runtime_acceptance='user-owned; not performed this turn')
    dest=ROOT/'backups/questbook_v4_20261017/delivery_verification.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
