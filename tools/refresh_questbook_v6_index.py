"""Refresh only the task/theme subtree in packwiz; retain unrelated entries."""
import hashlib,re,tomllib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=R/'index.toml';s=P.read_text(encoding='utf-8');parts=re.split(r'(?=\[\[files\]\])',s)
def scoped(path):
    return path.startswith(('config/ftbquests/quests/','kubejs/assets/svs/textures/quest/','kubejs/assets/ftbquests/')) or path in ['kubejs/server_scripts/svs_quests_bridge.js','kubejs/server_scripts/svs_quests_v2_bindings.js']
keep=[]
for block in parts[1:]:
    entry=tomllib.loads(block)['files'][0]
    if not scoped(entry['file']):keep.append(block.strip())
paths=list((R/'config/ftbquests/quests').rglob('*.snbt'))+list((R/'kubejs/assets/svs/textures/quest').rglob('*.png'))+list((R/'kubejs/assets/ftbquests').rglob('*'))
paths+=[R/'kubejs/server_scripts'/n for n in ['svs_quests_bridge.js','svs_quests_v2_bindings.js']]
for p in sorted(p for p in paths if p.is_file()):
    rel=p.relative_to(R).as_posix();assert scoped(rel)
    keep.append('[[files]]\nfile = "'+rel+'"\nhash = "'+hashlib.sha256(p.read_bytes()).hexdigest()+'"')
new=parts[0].rstrip()+'\n\n'+'\n\n'.join(keep)+'\n';P.write_text(new,encoding='utf-8')
p=R/'pack.toml';pack=p.read_text(encoding='utf-8');digest=hashlib.sha256(P.read_bytes()).hexdigest()
# Match the line without assuming a trailing space.
pack=re.sub(r'(\[index\][\s\S]*?\nhash = ")[^"]+("\s*\n)',lambda m:m[1]+digest+m[2],pack,count=1)
p.write_text(pack,encoding='utf-8')
assert tomllib.loads(pack)['index']['hash']==digest
for e in tomllib.loads(new)['files']:
    if scoped(e['file']):assert hashlib.sha256((R/e['file']).read_bytes()).hexdigest()==e['hash']
print('Refreshed scoped quest assets and pack index digest; other entries retained')
