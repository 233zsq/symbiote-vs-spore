"""Build/validate FTB Quests 2001.4.22 data. Python stdlib only.

Default writes only the repo's generated task directory and bridge bindings.
--check validates without mutating. External deployment is a separate operation.
"""
import argparse
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

ROOT = Path(os.path.abspath(__file__)).parents[1]
SOURCE = ROOT / 'docs/questbook_v2.json'
OUT = ROOT / 'config/ftbquests/quests'


class Long(int):
    pass


def uid(key):
    # 52-bit positive IDs survive Rhino's JS-number boundary exactly.
    return '000' + hashlib.sha256(('svs.questbook.v2/'+key).encode()).hexdigest()[:13].upper()


def snbt(value, depth=0):
    pad='  '*depth
    if isinstance(value, bool):return 'true' if value else 'false'
    if isinstance(value, Long):return str(value)+'L'
    if isinstance(value, (int,float)):return str(value)
    if isinstance(value, str):return json.dumps(value,ensure_ascii=False)
    if isinstance(value,list):
        return '[\n'+',\n'.join('  '*(depth+1)+snbt(v,depth+1) for v in value)+'\n'+pad+']' if value else '[]'
    if isinstance(value,dict):
        return '{\n'+',\n'.join('  '*(depth+1)+json.dumps(k)+': '+snbt(v,depth+1) for k,v in value.items())+'\n'+pad+'}'
    raise TypeError(type(value))


def parse_generated(text):
    # Our output is a strict JSON subset with only NBT long numeric suffixes.
    # Do not strip suffixes inside prose/string literals.
    return json.loads(re.sub(r'("(?:[^"\\]|\\.)*")|(-?\d+)L',
        lambda m:m.group(1) if m.group(1) else m.group(2),text))


def stack(item,count=1,name=''):
    if item.startswith('#'):
        raise ValueError('Current pack has no itemfilters:tag; use tag_count bridge: '+item)
    if name:
        return {'id':item,'Count':1,'tag':{'display':{'Name':json.dumps({'text':name,'italic':False},ensure_ascii=False),
            'Lore':[json.dumps({'text':'职业纪念；沿用原物品属性与槽位','italic':False,'color':'gray'},ensure_ascii=False)]}}}
    return item


def command(cmd, title='', auto='enabled'):
    return {'type':'command','command':cmd,'elevate_perms':True,'silent':True,
            'team_reward':False,'auto':auto,'title':title or '完成讲评'}


def create(data):
    nodes={q['key']:q for q in data['quests']}
    assert len(nodes)==len(data['quests']),'duplicate logical quest'
    ids=[]
    bindings=[]
    files={}
    tables=[]
    entries=[]
    groups=[{'id':uid('group/'+k),'title':title} for k,title in data['groups']]
    files['chapter_groups.snbt']={'chapter_groups':groups}
    files['data.snbt']={'version':13,'default_autoclaim_rewards':'disabled','default_consume_items':False,
        'default_reward_team':False,'default_quest_shape':'circle','detection_delay':20,'disable_gui':False,
        'drop_book_on_death':False,'drop_loot_crates':False,'pause_game':False,'progression_mode':'linear',
        'show_lock_icons':True,'hide_excluded_quests':False,'grid_scale':0.5}
    diff_table=uid('table/difficulty')
    files['reward_tables/difficulty.snbt']={'id':diff_table,'title':'个人难度·只选一次','loot_size':1,'order_index':0,
        'rewards':[dict(command('svs difficulty '+level,title,auto='disabled'),icon=icon) for level,title,icon in
        [('easy','轻松','minecraft:leather_helmet'),('normal','标准','minecraft:iron_helmet'),('hard','硬核','minecraft:diamond_helmet')]]}
    ids.extend([g['id'] for g in groups]+[diff_table])
    for ci,ch in enumerate(data['chapters']):
        quests=[]
        chapter_nodes=[q for q in data['quests'] if q['chapter']==ch['key']]
        assert 0<len(chapter_nodes)<=40,(ch['key'],len(chapter_nodes))
        # Serpentine fallback avoids long return arrows at row boundaries.
        # Forks and joins can use authored positions in the content source.
        for i,q in enumerate(chapter_nodes):
            assert len(q['text'])==4 and all(q['text']),q['key']
            assert q['source'],q['key']
            assert not (q.get('stage') and q.get('optional')),q['key']
            quest_id=uid('quest/'+q['key']);ids.append(quest_id)
            deps=q.get('deps',[])
            assert all(d in nodes for d in deps),(q['key'],deps)
            description=[label+t for label,t in zip(['【教学目标】','【作业】','【提示】','【讲评】'],q['text'])]
            tasks=[]
            for ti,t in enumerate(q['tasks']):
                task_id=uid('task/'+q['key']+'/'+str(ti));ids.append(task_id)
                kind=t['kind'];target=t.get('target','');count=t.get('count',1)
                built={'id':task_id,'type':'custom' if kind in ('bridge','pending') else kind}
                if kind=='item':built.update(item=stack(target),count=Long(count),consume_items=t.get('consume',False),match_nbt=False)
                elif kind=='kill':built.update(entity=target,value=Long(count))
                elif kind=='structure':built.update(structure=target)
                elif kind=='advancement':built.update(advancement=target)
                elif kind in ('bridge','pending'):
                    built.update(title=('尚未开放·' if kind=='pending' else '')+q['text'][1])
                    bindings.append(dict(key=q['key'],quest_id=quest_id,task_id=task_id,**t))
                elif kind!='checkmark':raise ValueError(kind)
                tasks.append(built)
            rewards=[]
            if q.get('xp'):rewards.append({'type':'xp','xp':q['xp'],'team_reward':False})
            for item in q.get('items',[]):
                rewards.append({'type':'item','item':stack(item[0],name=item[2] if len(item)>2 else ''),
                                'count':item[1],'team_reward':False})
            if q.get('choice'):
                rewards.append({'type':'choice','table_id':Long(int(diff_table,16)),'team_reward':False,'auto':'disabled',
                                'exclude_from_claim_all':True})
            if q.get('stage'):rewards.append(command('gamestage add {p} '+q['stage'],'阶段授予'))
            rewards.append(command('tellraw {p} '+json.dumps({'text':q['text'][3],'color':'gray'},ensure_ascii=False)))
            for ri,r in enumerate(rewards):r['id']=uid('reward/'+q['key']+'/'+str(ri));ids.append(r['id'])
            row,col=divmod(i,6)
            position=q.get('position',[(col if row%2==0 else 5-col)*2.5,row*3.5])
            icon=q.get('icon') or next((t['target'] for t in q['tasks'] if t['kind']=='item'),ch['icon'])
            built={'id':quest_id,'title':q['title'],'description':description,'icon':stack(icon),
                'subtitle':'尚未开放' if q['availability']=='pending' else '可选作业' if q['optional'] else '',
                'x':float(position[0]),'y':float(position[1]),'size':1.15 if q.get('stage') else 1.0,'shape':'diamond' if q.get('stage') else 'circle',
                'dependencies':[uid('quest/'+d) for d in deps],'tasks':tasks,'rewards':rewards,
                'optional':q['optional'],'hide_until_deps_complete':False,'hide_until_deps_visible':False,
                'hide_details_until_startable':False,'ignore_reward_blocking':False}
            if q.get('dependency')=='any':built['dependency_requirement']='one_completed'
            quests.append(built)
            entries.append({'key':q['key'],'chapter':ch['key'],'quest_id':quest_id,
                'task_ids':[t['id'] for t in tasks],'availability':q['availability'],'source':q['source']})
        chapter_id=uid('chapter/'+ch['key']);ids.append(chapter_id)
        files['chapters/'+ch['key']+'.snbt']={'id':chapter_id,'filename':ch['key'],'title':ch['title'],
            'group':uid('group/'+ch['group']),'order_index':ci,'icon':ch['icon'],
            'default_hide_dependency_lines':False,'default_quest_shape':'circle','quest_links':[],'quests':quests}
    assert len(ids)==len(set(ids)),'ID collision'
    # Check cycles across chapters too.
    visiting=set();done=set()
    def visit(key):
        assert key not in visiting,'dependency cycle: '+key
        if key in done:return
        visiting.add(key)
        for dep in nodes[key].get('deps',[]):visit(dep)
        visiting.remove(key);done.add(key)
    for key in nodes:visit(key)
    for name,obj in files.items():assert parse_generated(snbt(obj))==obj,name
    return files,bindings,entries


def validate_output(files):
    actual={p.relative_to(OUT).as_posix() for p in OUT.rglob('*.snbt')}
    assert actual==set(files),('unexpected/missing SNBT',actual ^ set(files))
    for name,obj in files.items():
        assert parse_generated((OUT/name).read_text(encoding='utf-8'))==obj,('stale generated file',name)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=json.loads(SOURCE.read_text(encoding='utf-8'));files,bindings,entries=create(data)
    if not args.check:
        # Constrain removal to this explicit repository output subtree, only .snbt files.
        assert OUT==ROOT/'config/ftbquests/quests'
        OUT.mkdir(parents=True,exist_ok=True)
        for p in OUT.rglob('*.snbt'):
            if p.relative_to(OUT).as_posix() not in files:p.unlink()
        for name,obj in files.items():
            p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(snbt(obj)+'\n',encoding='utf-8')
        (ROOT/'docs/FTB任务v2_ID映射.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (ROOT/'kubejs/server_scripts/svs_quests_v2_bindings.js').write_text(
            '// GENERATED by tools/build_questbook_v2.py; edit docs/questbook_v2.json.\n'
            +'global.svsQuestV2Bindings = '+json.dumps(bindings,ensure_ascii=False,indent=2)+'\n'
            +'global.svsQuestV2Stages = '+json.dumps([
                {'quest_id':uid('quest/'+q['key']),'stage':q['stage']} for q in data['quests'] if q.get('stage')])+'\n'
            +'global.svsQuestV2Audit = '+json.dumps({
                'quests':[uid('quest/'+q['key']) for q in data['quests']],
                'items':sorted({t['target'] for q in data['quests'] for t in q['tasks'] if t['kind']=='item' and not t['target'].startswith('#')} | {i[0] for q in data['quests'] for i in q.get('items',[]) } | {ch['icon'] for ch in data['chapters']} | {q['icon'] for q in data['quests'] if q.get('icon')}),
                'entities':sorted({t['target'] for q in data['quests'] for t in q['tasks'] if t['kind']=='kill'})
            },ensure_ascii=False)+'\n',encoding='utf-8')
        lines=['# FTB任务 v2 节点与验收目录','','> 自动从 questbook_v2.json 生成；wired 表示检测已绑定，**不表示游戏验收通过**。pending 不可手动完成。','']
        for ch in data['chapters']:
            qs=[q for q in data['quests'] if q['chapter']==ch['key']]
            lines+=['## '+ch['title']+'（'+str(len(qs))+'）','']
            for q in qs:
                lines+=['### '+q['key']+' '+q['title'],'',
                    '状态：'+q['availability']+'；依赖：'+(' ∨ ' if q.get('dependency')=='any' else ' ∧ ').join(q['deps'] or ['无'])+'。',
                    '']+[label+t for label,t in zip(['- 【教学目标】','- 【作业】','- 【提示】','- 【讲评】'],q['text'])]+[
                    '', '检测：`'+json.dumps(q['tasks'],ensure_ascii=False)+'`。',
                    '验收：依赖满足后按作业完成；未满足时不得推进。持有类不扣物品，提交类只扣指定数；击杀类排除错误目标及环境死亡；到访不判清场；桥类与 pending 不能点击跳过。',
                    '奖励：xp '+str(q.get('xp',0))+'；物品 '+json.dumps(q.get('items',[]),ensure_ascii=False)+'。',
                    '依据：'+q['source']+'。','']
        (ROOT/'docs/FTB任务v2_节点与验收目录.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    validate_output(files)
    print(json.dumps({'chapters':len(data['chapters']),'quests':len(data['quests']),
        'counts':dict(Counter(q['chapter'] for q in data['quests'])),
        'pending':sum(q['availability']=='pending' for q in data['quests']),
        'custom_tasks':len(bindings),'files':len(files),'check':'PASS'},ensure_ascii=False))


if __name__=='__main__':main()
