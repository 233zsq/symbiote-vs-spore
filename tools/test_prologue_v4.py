"""Focused content/graph regression checks for the authored v4 prologue."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('quest_builder', ROOT/'tools/build_questbook_v2.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
d = json.loads((ROOT/'docs/questbook_v2.json').read_text(encoding='utf-8'))
q = {v['key']: v for v in d['quests']}
files, bindings, entries = builder.create(d)
builder.validate_output(files)

def ancestors(key):
    result = set(q[key]['deps'])
    for dep in q[key]['deps']:
        result |= ancestors(dep)
    return result

assert ancestors('A07') == {'S00'}, 'village must be reachable before combat/fusion'
assert ancestors('A10') == {'S00'}, 'fusion must be reachable before village'
assert ancestors('A02') == {'S00'}, 'weapon cannot wait for combat practice'
assert ancestors('V4A_FORGE') == {'S00'}, 'working furnace kit must be available early'
assert {'A06','A11','A09','B03','V4A_CAST','V4A_DEFENSE'} <= ancestors('A12')
assert not any(q[k]['availability']=='pending' for k in ancestors('A12'))
assert all(q[k]['chapter']=='prologue' for k in ['B02','B03','V4A_FORGE'])
assert q['B02']['tasks'] == [dict(kind='bridge',target='fireseed_ready',count=1)]
assert q['B03']['tasks'][0]['target']=='fireseed'
assert q['A10']['tasks'][0]['stage']=='ATTACHED'
assert q['A06']['tasks'][0]['target']=='hostile_kills'
assert q['A06']['tasks'][0]['count']==5
assert q['A12']['stage']=='svs_stage1_prologue'
assert q['A12']['tasks']==[dict(kind='bridge',target='milestone',count=1)], 'FTB empty-task quests do not auto-complete'
assert q['M14']['items']==[], 'old reference page must not duplicate the furnace gift'
kit = dict(q['V4A_FORGE']['items'])
assert kit == {'tconstruct:seared_melter':1,'tconstruct:seared_heater':1,
    'tconstruct:seared_faucet':1,'tconstruct:seared_table':1,'tconstruct:ingot_cast':1,
    'minecraft:coal':16,'minecraft:raw_copper':3,'tconstruct:part_builder':1,
    'tconstruct:tinker_station':1}
assert all(v.get('writing_style')=='v4' for v in q.values() if v['chapter'] in ('start','prologue'))
assert builder.text_labels(q['A01'])[0]=='【战略目标】'
assert builder.text_labels(q['F04'])[0]=='【战略目标】', 'whole book now follows story v4'
# Previously authored IDs must remain stable when moved between chapters.
old_ids = {'A12':'000D7BD903B53355', 'B02':'00069FEB67BAFE21', 'B03':'000C5A8BEF0C98DE'}
assert all(old_ids[v['key']]==v['quest_id'] for v in entries if v['key'] in old_ids)
prologue=files['chapters/prologue.snbt']['quests']
generated={v['id']:v for v in prologue}
for key, suffix in [('A07','v4_fireseed'),('A06','v4_coins')]:
    rewards=generated[builder.uid('quest/'+key)]['rewards']
    assert rewards[1]['id']==builder.uid('reward/'+key+'/'+suffix)
    assert rewards[-1]['id']==builder.uid('reward/'+key+'/1'), 'retain old tellraw claim ID'
print('PASS: parallel routes, early equipment, graduation gates, kit completeness, stable quest IDs; static checks only')
