"""Story-v4 graph, migration, completion and icon regression checks (no game)."""
import json
from collections import Counter
from pathlib import Path
import build_questbook_v2 as b

ROOT=Path(__file__).resolve().parents[1]
d=json.loads(b.SOURCE.read_text(encoding='utf-8'));q={v['key']:v for v in d['quests']}
files,bindings,entries=b.create(d)
b.validate_output(files);b.validate_auxiliary(d,bindings,entries)
def ancestors(key):
    result=set(q[key]['deps'])
    for dep in q[key]['deps']:result.update(ancestors(dep))
    return result

assert all(v.get('writing_style')=='v4' for v in q.values())
assert not any(s in '\n'.join(v['text']) for v in q.values() for s in ('冒险者，','战地手册','终局候选','待重写'))
main={v['boss_slot']:v for v in q.values() if v.get('boss_slot','').startswith('M')}
side={v['boss_slot']:v for v in q.values() if v.get('boss_slot','').startswith('S')}
assert set(main)=={f'M{i:02}' for i in range(1,27)}
assert set(side)=={f'S{i:02}' for i in range(1,25)}
assert len({v['boss_entity'] for k,v in main.items() if k not in ('M25','M26')})==24
assert not ({v.get('boss_entity') for v in main.values()} & {v['boss_entity'] for v in side.values()})
for i in range(1,25):
    v=main[f'M{i:02}']
    assert v['tasks']==[dict(kind='kill',target=v['boss_entity'],count=1)],v['key']
    assert not any(q[k]['optional'] or q[k]['chapter'] in ('collector','smith','dragon','symbiote') for k in ancestors(v['key'])),v['key']
assert all(v['optional'] for v in side.values())
assert main['M23']['boss_entity']=='nightfall_invade:arterius'
assert side['S24']['boss_entity']=='slu:boss_dragon_slayer_armour'
assert q['H05']['dependency']=='any' and q['C07']['dependency']=='any'
for key in ('V4_PHASE1','V4_PHASE2','V4_PHASE3','H05','C07','F14','J12','H14','L08'):
    assert q[key]['tasks']==[dict(kind='bridge',target='milestone',count=1)],key
for key in ('V4_M25','V4_M26','V4_STRIKE','V4_FIRE','V4_CROWN','V4_S02'):
    assert q[key]['availability']=='pending'
    assert all(t['kind']=='pending' for t in q[key]['tasks'])
    assert not q[key]['items'] and not q[key].get('stage'),key
assert 'V4_M25' in ancestors('V4_M26')
assert {'V4_STRIKE','V4_FIRE','V4_TOWER2'}<=ancestors('V4_M25')
assert not any(not v['tasks'] for v in q.values()),'empty quests cannot auto-complete'
assert [q[k]['stage'] for k in ('V4_PHASE1','V4_PHASE2','V4_PHASE3')]==['svs_stage2_arena','svs_stage3_calamity','svs_stage4_endgame']
assert not {'B11','C22','D29','E18'} & q.keys()
for ch in d['chapters']:
    for v in (v for v in q.values() if v['chapter']==ch['key']):
        targets=[t['target'] for t in v['tasks'] if t['kind']=='item']
        if targets:assert b.quest_icon(v,ch)==targets[0],v['key']
assert b.quest_icon(q['V4_M26'],{})['tag']['Icon']=='svs:textures/quest/boss/m26.png'
# Legacy quest identity is retained only where the proof still means the same thing.
before=ROOT/'backups/questbook_v4_20261017/before/docs/questbook_v2.json'
if before.exists():
    old={v['key']:v for v in json.loads(before.read_text(encoding='utf-8'))['quests']}
    for key,v in old.items():
        if v['chapter'] in ('start','prologue'):
            assert q[key]['tasks']==v['tasks'],key
            for prop in ('items','xp','stage','reward_id_keys','deps'):assert q[key].get(prop)==v.get(prop),(key,prop)
    for key in ('C19','D20'):
        assert key not in q and q[key+'_V4']['tasks'][0]['kind']=='item'
        assert b.uid('quest/'+key)!=b.uid('quest/'+key+'_V4')
    for key in ('C15','HUNT_ignis','HUNT_scylla','SOUL_boss_gundyr'):
        assert old[key]['tasks']==q[key]['tasks'],key
print(json.dumps({'result':'PASS','quests':len(q),'chapters':len(d['chapters']),
                  'main_bosses':24,'main_events':2,'side_slots':24,
                  'item_icon_nodes':sum(any(t['kind']=='item' for t in v['tasks']) for v in q.values()),
                  'note':'static checks only; user owns in-game acceptance'},ensure_ascii=False))
