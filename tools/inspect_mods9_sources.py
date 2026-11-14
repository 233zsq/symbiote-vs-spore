"""Extract selected reference resources and decompile local review targets only.
No reference archive or instance file is changed.
"""
import hashlib,json,subprocess,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'backups/mods9_review_20261026';V=Path('C:/PCL 正式版 2.8.13/.minecraft/versions')
CFR=R/'backups/legendary_bosses_20261018/cfr-0.152.jar';JAVA='C:/Program Files/Java/jdk-17/bin/java.exe'
targets=[]
for p in Path('E:/mcmp_test/dl/新加入的模组9').glob('*.jar'):
    if not p.name.startswith('spawn-'):targets.append(('intake',p))
for name,patterns in [('Immersive Fight 4.2.9',['celepic-*','superdupertamer-*','class_enhancement-*']),('Otherworld',['otherworldorigins-*','otherworld-0*','justlevelingfork-*','AutoLeveling-*'])]:
    for pat in patterns:
        for p in (V/name/'mods').glob(pat+'.jar'):targets.append(('reference',p))
report=[]
for kind,p in targets:
    out=B/'decompiled'/p.stem;out.mkdir(parents=True,exist_ok=True)
    if not (out/'summary.txt').exists():
        s=subprocess.run([JAVA,'-Xmx512m','-jar',str(CFR),str(p),'--outputdir',str(out),'--silent','true'],capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=0x08000000)
        (out/'decompiler.log').write_text(s.stderr,encoding='utf-8')
    resources={}
    if kind=='reference':
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n.endswith(('.json','.toml')) and (n.startswith(('data/','assets/','META-INF/')) or 'mixin' in n):
                    body=z.read(n);resources[n]=hashlib.sha256(body).hexdigest()
                    if not n.endswith('refmap.json'):
                        dest=B/'reference_resources'/p.stem/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(body)
    report.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sources=str(out),source_files=len(list(out.rglob('*.java'))),resources=resources))
    print(p.name,'java',report[-1]['source_files'],'json/toml',len(resources),flush=True)
# Spawn review focuses on generation + config rather than hundreds of render classes.
p=next(Path('E:/mcmp_test/dl/新加入的模组9').glob('spawn-*.jar'));dest=B/'spawn_review_classes'
with zipfile.ZipFile(p) as z:
    selected=[n for n in z.namelist() if n.endswith('.class') and any(s in n for s in ['/config/','/worldgen/','/mixin/ChunkGenerator','/mixin/MultiNoise','/mixin/OverworldBiomeBuilder','Spawn.class','/registry/SpawnEntities','/registry/SpawnBiomes'])]
    for n in selected:
        f=dest/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n))
        out=B/'decompiled'/p.stem
        if not(out/n.replace('.class','.java')).exists():
            subprocess.run([JAVA,'-Xmx512m','-jar',str(CFR),str(f),'--outputdir',str(out),'--silent','true'],capture_output=True,creationflags=0x08000000)
print('spawn generation classes',len(selected),flush=True)
(B/'source_inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
