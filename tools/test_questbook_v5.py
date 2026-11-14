"""Independent coverage, icon, migration and navigation checks for the rebuilt book."""
import hashlib,json,re
from collections import Counter
from pathlib import Path
import build_questbook_v2 as b
from snbt_read import loads

ROOT=Path(__file__).resolve().parents[1]
d=json.loads(b.SOURCE.read_text(encoding='utf-8'));q={v['key']:v for v in d['quests']}
facts=json.loads((ROOT/'docs/data/quest_content_v5.json').read_text(encoding='utf-8'))
files,bindings,entries=b.create(d);b.validate_output(files);b.validate_auxiliary(d,bindings,entries)
assert d['editorial_version']==5
assert len(q)==len(d['quests'])
main={v['boss_slot']:v for v in q.values() if v.get('boss_slot','').startswith('M')}
side={v['boss_slot']:v for v in q.values() if v.get('boss_slot','').startswith('S')}
assert set(main)=={f'M{i:02}' for i in range(1,27)}
assert set(side)=={f'S{i:02}' for i in range(1,25)}
def ancestors(key):
    out=set(q[key]['deps'])
    for dep in q[key]['deps']:out.update(ancestors(dep))
    return out
for v in main.values():
    assert not any(q[k]['optional'] or q[k]['chapter'].startswith('v5_') or q[k]['chapter'] in ('collector','smith','dragon','symbiote') for k in ancestors(v['key'])),v['key']
assert len({v['text'][0] for v in list(main.values())+list(side.values())})==50
for v in list(main.values())+list(side.values()):
    assert len(v['text'][0])>=35,('missing individual introduction',v['key'])
    assert len(''.join(v['text']))+sum(len(''.join(s['lines'])) for s in v.get('sections',[]))>=200,v['key']
    assert len(v.get('sections',[]))>=3,v['key']
    assert v['subtitle'],v['key']
    assert v['icon'] not in ('minecraft:wither_skeleton_skull','minecraft:skeleton_skull','minecraft:book'),v['key']
    assert 'spawn_egg' not in v['icon'],v['key']
    assert v['icon'] in facts['names'],v['key']
    assert v['sections'][2]['title']=='战利品与后续用途'
assert main['M23']['boss_entity']=='nightfall_invade:arterius'
assert side['S21']['boss_entity']=='slu:boss_artorias'
for key in ('V4_STRIKE','V4_M25','V4_M26','V4_CROWN','V4_S02'):
    assert key in q,key
    assert q[key]['availability']=='pending' and any(t['kind']=='pending' for t in q[key]['tasks']),key
assert q['V4_M26']['icon_texture']=='svs:textures/quest/boss/m26.png'
assert all(q[k]['tasks']==[dict(kind='bridge',target='milestone',count=1)] for k in ('A12','H05','C07','V4_PHASE1','V4_PHASE2','V4_PHASE3'))
assert q['H05']['dependency']=='any' and q['C07']['dependency']=='any'

catalog={e['id']:e for e in facts['catalog']}
covered={id for v in q.values() for id in v.get('catalog_items',[])}
assert covered==set(catalog),('catalogue missing or extra',set(catalog)^covered)
assert not any(id.startswith(('geckolib:','dungeons_gear:')) or 'debug' in id for id in covered)
storm=next(v for v in q.values() if v.get('catalog_items')==['simplyswords:stormbringer'])
assert any('冲震' in '\n'.join(s['lines']) for s in storm['sections']), 'missing real unique-weapon description'
netherite=next(v for v in q.values() if v.get('catalog_items')==['simplyswords:netherite_longsword'])
assert any('符文长剑' in '\n'.join(s['lines']) for s in netherite['sections']), 'missing actual next upgrade'
assert any(s['title']=='收藏家计件归属' for s in storm['sections']), 'catalogue must explain counted collection groups'
for v in q.values():
    assert v['tasks'],('empty task cannot complete',v['key'])
    assert not any(s in '\n'.join(v['text']) for s in ('冒险者，','战地手册','待重写','查看源码'))
    for l in v.get('links',[]):assert l['key'] in q,(v['key'],l)
    for t in v['tasks']:
        if t['kind']=='item':
            assert not t['target'].startswith('#'),v['key']
            assert t['target'] in facts['names'] or t['target'].startswith('kubejs:'),(v['key'],t['target'])
    if v.get('catalog_items'):
        assert v['optional'] and not v['items'] and not v.get('stage'),v['key']
        assert v.get('sections') and v['sections'][0]['title'] in ('取得路线','部件与取得路线')
        assert {t['target'] for t in v['tasks']}==set(v['catalog_items']),v['key']
        assert all(not t.get('consume') for t in v['tasks']),v['key']
        assert v['icon']==v['tasks'][0]['target'],v['key']
        if len(v['tasks'])>1:assert '同时持有' not in v['text'][1], 'native per-item completion remembers pieces separately'
        for e in v['catalog_items']:
            # If evidence exists, at least one real ingredient or source must appear.
            entry=catalog[e]
            prose='\n'.join(s for section in v['sections'] for s in section['lines'])
            if entry['sources']:assert '工作台' in prose or '锻造台' in prose or '专用工艺' in prose or '熔炉' in prose or '高炉' in prose,v['key']

before=json.loads((ROOT/'backups/questbook_v5_rebuild_20261017/before/docs/questbook_v2.json').read_text(encoding='utf-8'))
old={v['key']:v for v in before['quests']}
for key,v in old.items():
    if v['chapter'] in ('start','prologue'):
        for field in ('tasks','deps','items','xp','reward_id_keys','stage'):assert q[key].get(field)==v.get(field),(key,field)
    if key in q:assert q[key]['tasks']==v['tasks'],('changed legacy proof',key)
for n in range(1,25):
    key=f'V4_M{n:02}';v=q[key]
    assert len(v['items'])==1 and v['reward_id_keys']=={'1':'v5_supply','2':'1'},key
    assert b.uid('reward/'+key+'/v5_supply')!=b.uid('reward/'+key+'/1')
for ch in d['chapters']:
    nodes=[v for v in q.values() if v['chapter']==ch['key']]
    assert 0<len(nodes)<=40,ch['key']
    assert ch.get('images') and ch['images'][0]['order']<0,ch['key']
    positions=[tuple(v['position']) for v in nodes if 'position' in v]
    assert len(positions)==len(set(positions)),('overlapping nodes',ch['key'])
    generated=files['chapters/'+ch['key']+'.snbt']['quests']
    points=[(v['x'],v['y']) for v in generated]
    assert len(points)==len(set(points)),('generated node overlap',ch['key'])
# Independent SNBT parser validates actual on-disk output, not just builder's JSON subset.
for name,obj in files.items():assert loads((b.OUT/name).read_text(encoding='utf-8'))==obj,name
# Reference books remain read-only, checked against hashes taken before close reading.
research=json.loads((ROOT/'backups/questbook_v5_rebuild_20261017/reference_close_reading.json').read_text(encoding='utf-8'))
for pack in research:
    for chapter in pack['chapters']:
        p=Path(pack['root'])/'chapters'/chapter['file']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==chapter['sha256'],p
result=dict(result='PASS',chapters=len(d['chapters']),quests=len(q),main_bosses=24,main_events=2,
            independent_bosses=24,equipment_items=len(covered),catalog_kind=dict(Counter(e['kind'] for e in catalog.values())),
            armor_entries=sum(bool(v.get('catalog_items')) and all(catalog[i]['kind']=='armor' for i in v['catalog_items']) for v in q.values()),
            linked_navigation=sum(len(v.get('links',[])) for v in q.values()),
            reference_chapters_unchanged=sum(len(p['chapters']) for p in research),runtime_acceptance='user-owned; not claimed')
(ROOT/'backups/questbook_v5_rebuild_20261017/static_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
