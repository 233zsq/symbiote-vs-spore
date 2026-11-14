"""Checks the reported failures: visibility, campaign continuity, real icons,
ranked collection, achievable milestones and actual skill book reward NBT.
These checks do not claim Minecraft UI/gameplay acceptance.
"""
import collections,hashlib,json,re
from pathlib import Path
from PIL import Image
import build_questbook_v2 as b
from snbt_read import loads
R=Path(__file__).resolve().parents[1];B=R/'backups/questbook_v6_20261017'
d=json.loads(b.SOURCE.read_text(encoding='utf-8'));q={v['key']:v for v in d['quests']}
assert d['editorial_version']==6
files,bindings,entries=b.create(d);b.validate_output(files);b.validate_auxiliary(d,bindings,entries)
for name,obj in files.items():assert loads((b.OUT/name).read_text(encoding='utf-8'))==obj,name
missing={x.removeprefix('item:') for x in json.loads((B/'runtime_missing_v5.json').read_text(encoding='utf-8'))}
facts=json.loads((R/'docs/data/quest_content_v5.json').read_text(encoding='utf-8'))
expected={e['id'] for e in facts['catalog']}-missing
if d.get('content_revision','').startswith('6.1-legendarybosses'):
    extension=json.loads((R/'docs/data/legendary_bosses_20261018.json').read_text(encoding='utf-8'))
    expected.update('legendarybosses:'+s for s in extension['obtained_items'])
covered=[i for v in q.values() for i in v.get('catalog_items',[])]
assert set(covered)==expected
assert len(covered)==len(set(covered)),'an item must only earn one registration reward'
assert {v['key'] for v in q.values() if not v['deps']}=={'E6_S00'}
assert len(d['chapters'])<=24

main={v['boss_slot']:v for v in q.values() if v.get('boss_slot','').startswith('M')}
side={v['boss_slot']:v for v in q.values() if v.get('boss_slot','').startswith('S')}
assert set(main)=={f'M{i:02}' for i in range(1,27)}
assert set(side)=={f'S{i:02}' for i in range(1,25)}
cache={}
def ancestors(k):
    if k not in cache:
        cache[k]=set(q[k]['deps'])
        for p in q[k]['deps']:cache[k].update(ancestors(p))
    return cache[k]
for n in range(2,25):assert f'E6_V4_M{n-1:02}' in ancestors(main[f'M{n:02}']['key'])
for v in main.values():
    assert not any(q[k]['optional'] for k in ancestors(v['key'])),v['key']
    if v['boss_slot'] not in ['M25','M26']:
        assert len(v['text'][0])>=65,v['key']
        assert len(v['sections'])==3
        after=q['E6_V6_AFTER_'+v['boss_slot']]
        assert after['items'] or after.get('select_rewards'),after['key']
for k in ['V4_M25','V4_M26','V4_CROWN','V4_FIRE','V4_STRIKE']:
    assert q['E6_'+k]['availability']=='pending'
    assert any(t['kind']=='pending' for t in q['E6_'+k]['tasks'])
assert main['M23']['boss_entity']=='nightfall_invade:arterius'
assert side['S21']['boss_entity']=='slu:boss_artorias'
assert sum(k.startswith('E6_AID_') for k in q)==5

all_item_refs=set()
for ch in d['chapters']:
    assert ch.get('icon_texture'),ch['key']
    p=R/'kubejs/assets/svs'/ch['icon_texture'].split(':',1)[1]
    with Image.open(p) as im:assert im.size==(16,16) and im.getbbox(),p
    points=[tuple(v['position']) for v in q.values() if v['chapter']==ch['key']]
    assert len(points)==len(set(points)),('node overlap',ch['key'])
for v in q.values():
    for t in v['tasks']:
        if t['kind']=='item':all_item_refs.add(t['target'])
        if t['kind']=='bridge' and t['target']=='catalog_count':
            assert len(set(t['quest_keys']))==len(t['quest_keys'])>=t['count'],v['key']
            assert all(q[k].get('catalog_items') for k in t['quest_keys']),v['key']
            assert not any(t2.get('consume') for k in t['quest_keys'] for t2 in q[k]['tasks'])
    for i in v['items']:all_item_refs.add(i[0]['id'] if isinstance(i[0],dict) else i[0])
    if v.get('icon'):all_item_refs.add(v['icon'])
    if v.get('catalog_items'):
        assert v['tier'] in ['T0','T1','T2'] and v['optional']
        assert v['items']==[['kubejs:spore_coin',{'T2':1,'T1':4,'T0':12}[v['tier']]*(2 if v['ledger_kind']=='armor' and len(v['catalog_items'])>1 else 1)]]
        assert all(t['kind']=='item' and not t['consume'] for t in v['tasks'])
        assert v['icon'] in v['catalog_items']
    for l in v.get('links',[]):assert l['key'] in q
    assert v['key'].startswith('E6_'),'old progress may not silently finish a rewritten task'

skills=set()
for table in d['reward_tables'].values():
    for e in table['entries']:
        i=e['item'];all_item_refs.add(i['id'] if isinstance(i,dict) else i)
        if isinstance(i,dict) and i['id']=='epicfight:skillbook':
            assert set(i['tag'])=={'skill'} and i['tag']['skill'].startswith('epicfight:')
            skills.add(i['tag']['skill'].split(':')[1])
registration=(B/'EpicFightSkills.javap').read_text(encoding='utf-8-sig')
assert all(re.search(r'// String '+re.escape(s)+r'\s',registration) for s in skills)
assert not (all_item_refs & missing),all_item_refs & missing
for v in files.values():
    for g in v.get('quests',[]):
        assert g['hide_until_deps_complete'] and g['hide_until_deps_visible'] and g['hide_details_until_startable']
        if any(qe['quest_id']==g['id'] and q[qe['key']].get('catalog_items') for qe in entries):
            assert all(r['type']!='command' for r in g['rewards']),'claim all must not spam tellraw'

# Normal-player visibility model: completed dependencies reveal the next task;
# editor mode intentionally ignores this policy in the real FTB GUI.
def visible(completed):
    return {k for k,v in q.items() if k in completed or (any(p in completed for p in v['deps']) if v.get('dependency')=='any' else all(p in completed for p in v['deps']))}
assert visible(set())=={'E6_S00'}
assert visible({'E6_S00'})=={'E6_S00','E6_S01'}
completed=set(ancestors('E6_A12'))|{'E6_A12'}
assert 'E6_V6_BRIEF1' in visible(completed)
assert 'E6_V4_M02' not in visible(completed)
assert not any(k.startswith('E6_GEAR_') for k in visible(completed))
# Opening one catalogue batch reveals at most six acquisitions, never the whole tier.
for tier in ['T2','T1','T0']:
    root=f'E6_LEDGER_{tier}_weapon_0';done=set(ancestors(root))|{root}
    open_gear=[k for k in visible(done) if q[k].get('catalog_items')]
    assert len(open_gear)==6,(tier,len(open_gear))

ref=json.loads((R/'backups/questbook_v5_rebuild_20261017/reference_close_reading.json').read_text(encoding='utf-8'))
for pack in ref:
    for ch in pack['chapters']:
        p=Path(pack['root'])/'chapters'/ch['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==ch['sha256'],p
report={'result':'PASS','fresh_start_visible':['天外四客'],'reference_chapters_unchanged':sum(len(p['chapters']) for p in ref),
        'invalid_v5_items_removed':len(missing),'ranked_equipment':len(covered),'skills_with_verified_registration':sorted(skills),
        'catalogue_rewards':'one-time, non-consuming, distinct completed acquisitions','support_returns':5,
        'limitations':['No Minecraft UI or gameplay acceptance performed','Three main-boss controlled entrances not open','Eight unfinished event goals remain closed','Tiers are editorial utility bands, not measured DPS rankings']}
report_path=(R/'backups/legendary_bosses_20261018/questbook_regression.json') if d.get('content_revision','').startswith('6.1-legendarybosses') else B/'static_verification.json'
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
