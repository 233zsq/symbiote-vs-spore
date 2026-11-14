"""Read the three user-requested reference books. Does not touch reference files."""
import hashlib,json
from collections import Counter
from pathlib import Path
from snbt_read import loads

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('C:/PCL 正式版 2.8.13/.minecraft/versions')
NAMES=['龙之冒险：新征程v2.4a','Immersive Fight 4.2.9','DUEL OF THE END']
out=[]
for name in NAMES:
    root=BASE/name/'config/ftbquests/quests';chapters=[]
    for path in sorted((root/'chapters').glob('*.snbt')):
        d=loads(path.read_text(encoding='utf-8-sig'));qs=d.get('quests',[])
        icons=Counter();samples=[]
        for q in qs:
            icon=q.get('icon','auto')
            icons[str(icon)[:180]]+=1
        # Keep the richest player-facing examples per chapter for close reading.
        for q in sorted(qs,key=lambda q:len(str(q.get('description',''))),reverse=True)[:5]:
            samples.append({k:q[k] for k in ('id','title','subtitle','description','icon','dependencies','tasks','rewards','x','y') if k in q})
        chapters.append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            title=d.get('title',''),quests=len(qs),images=d.get('images',[]),
            icons=icons.most_common(6),samples=samples,
            task_types=dict(Counter(t.get('type') for q in qs for t in q.get('tasks',[])))))
    out.append(dict(name=name,root=str(root),chapters=chapters,quest_count=sum(c['quests'] for c in chapters)))
dest=ROOT/'backups/questbook_v5_rebuild_20261017';dest.mkdir(parents=True,exist_ok=True)
(dest/'reference_close_reading.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in out:
    print(p['name'],len(p['chapters']),p['quest_count'])
    for c in p['chapters']:print(c['file'],c['title'],c['quests'],'images',len(c['images']),c['task_types'])
