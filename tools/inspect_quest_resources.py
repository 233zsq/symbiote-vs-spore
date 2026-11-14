"""Read installed resource identifiers without launching Minecraft."""
import json, zipfile
from pathlib import Path

mods=Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test/mods')
out=Path(__file__).resolve().parents[1]/'backups/questbook_v4_20261017'
out.mkdir(parents=True,exist_ok=True)
entities={}; items={}; advancements=set()
for p in mods.glob('*.jar'):
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if n.startswith('assets/') and n.endswith('/lang/en_us.json'):
                try: lang=json.loads(z.read(n))
                except (ValueError,UnicodeError): continue
                for k,v in lang.items():
                    parts=k.split('.',2)
                    if len(parts)==3 and parts[0] in ('entity','item','block'):
                        target=entities if parts[0]=='entity' else items
                        target[parts[1]+':'+parts[2]]={'label':v,'jar':p.name}
            if n.startswith('data/') and '/advancements/' in n and n.endswith('.json'):
                namespace,tail=n[5:].split('/advancements/',1)
                advancements.add(namespace+':'+tail[:-5])
(out/'resource_identifiers.json').write_text(json.dumps({'entities':entities,'items':items,'advancements':sorted(advancements)},ensure_ascii=False,indent=2),encoding='utf-8')
for k,v in entities.items():
    if k.split(':')[0] in ('mowziesmobs','bosses_of_mass_destruction','slu'):
        print(k,v['label'])
