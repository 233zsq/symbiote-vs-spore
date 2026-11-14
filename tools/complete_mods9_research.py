"""Additional static evidence for the 2026-10-26 intake; no instance writes."""
import ast,json,re,struct,subprocess,zipfile
from pathlib import Path

R=Path(__file__).resolve().parents[1]
B=R/'backups/mods9_review_20261026'
D=B/'decompiled'; RR=B/'reference_resources'
V=Path('C:/PCL 正式版 2.8.13/.minecraft/versions')
JAVA='C:/Program Files/Java/jdk-17/bin/java.exe'
CFR=R/'backups/legendary_bosses_20261018/cfr-0.152.jar'
# Reuse the constant-pool parser without executing the inventory's top level.
tree=ast.parse((R/'tools/audit_mods9.py').read_text(encoding='utf-8'))
parser=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='strings')
exec(compile(ast.Module(body=[parser],type_ignores=[]),'<constant_pool_parser>','exec'))
out={}
for key,root,pat,terms in [
 ('spawn',Path('E:/mcmp_test/dl/新加入的模组9'),'spawn-*.jar',['SpawnServerConfig.class','SpawnClientConfig.class','SpawnOverworldBiomes.class']),
 ('findme',V/'Immersive Fight 4.2.9/mods','Find me*.jar',None),
 ('fight_more',V/'Immersive Fight 4.2.9/mods','fight_more-*.jar',['MyTamedCommand.class']),
]:
    p=next(root.glob(pat));out[key]={'file':str(p),'selected':[]}
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if n.endswith('.class') and (terms is None or any(n.endswith(t) for t in terms)):
                out[key]['selected'].append(n)
                dest=B/'extra_classes'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(n))
                if terms is not None and not (D/p.stem/n.replace('.class','.java')).exists():
                    subprocess.run([JAVA,'-Xmx384m','-jar',str(CFR),str(dest),'--outputdir',str(D/p.stem),'--silent','true'],capture_output=True,creationflags=0x08000000)
            elif key in ['findme','fight_more'] and n.endswith(('.json','.toml')):
                dest=RR/p.stem/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(n))
    if terms is None and not (D/p.stem/'summary.txt').exists():
        subprocess.run([JAVA,'-Xmx512m','-jar',str(CFR),str(p),'--outputdir',str(D/p.stem),'--silent','true'],capture_output=True,creationflags=0x08000000)
    print(key,p.name,len(out[key]['selected']),flush=True)

cs=next(Path('E:/mcmp_test/dl/新加入的模组9').glob('celestisynth-*.jar'))
ce=next((V/'Immersive Fight 4.2.9/mods').glob('celepic-*.jar'))
old=next((V/'Immersive Fight 4.2.9/mods').glob('celestisynth-*.jar'))
with zipfile.ZipFile(cs) as znew,zipfile.ZipFile(ce) as zce,zipfile.ZipFile(old) as zold:
    new=set(znew.namelist());older=set(zold.namelist())
    refs=set()
    for n in zce.namelist():
        if n.endswith('.class'):
            refs.update(s for s in strings(zce.read(n)) if s.startswith(('com/aqutheseal/celestisynth/','org/thecelestialworkshop/celestisynth/')) and '(' not in s and ';' not in s and '<' not in s)
    out['celepic_class_references']=[{'class':s,'in_reference_1_3_1':s+'.class' in older,'in_candidate_1_3_4':s+'.class' in new} for s in sorted(refs)]
    out['celepic_old_namespace_class_count_in_1_3_4']=sum(n.startswith('com/aqutheseal/celestisynth/') and n.endswith('.class') for n in new)
print('CELEpic CS refs',len(out['celepic_class_references']),'missing in new',sum(not x['in_candidate_1_3_4'] for x in out['celepic_class_references']),flush=True)

oroot=RR/'otherworldorigins-2.0.1/data/otherworldorigins'
out['classes']={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in sorted((oroot/'origins/class').glob('*.json'))}
out['layers']={}
for p in sorted((oroot/'origin_layers').glob('*.json')):
    data=json.loads(p.read_text(encoding='utf-8'))
    out['layers'][p.stem]={'order':data.get('order'),'enabled':data.get('enabled',True),'origins':data.get('origins',[])}
out['subclasses']={p.relative_to(oroot/'origins').as_posix():json.loads(p.read_text(encoding='utf-8')) for p in sorted((oroot/'origins').rglob('*.json')) if 'subclass' in str(p)}
out['class_powers']={p.relative_to(oroot/'powers').as_posix():json.loads(p.read_text(encoding='utf-8')) for p in sorted((oroot/'powers/class').rglob('*.json'))}
(R/'docs/data/模组9专项研究_2026-10-26.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Otherworld classes',len(out['classes']),'subclasses',len(out['subclasses']),'layers',len(out['layers']),flush=True)
