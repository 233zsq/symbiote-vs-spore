"""Rebuild the questbook after the user's rejection of the shallow 234-node draft.

Authored routes + complete optional equipment catalogue. Frozen collector tags,
existing mechanics and reference modpacks are never modified.
"""
import ast,collections,hashlib,json,math,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FACTS=json.loads((ROOT/'docs/data/quest_content_v5.json').read_text(encoding='utf-8'))
DOSSIERS=json.loads((ROOT/'docs/questbook_v5_boss_dossiers.json').read_text(encoding='utf-8'))
BASE=ROOT/'backups/questbook_v5_rebuild_20261017/before/docs/questbook_v2.json'
d=json.loads(BASE.read_text(encoding='utf-8'))
old={q['key']:q for q in d['quests']};q=json.loads(json.dumps(old));names=FACTS['names']
catalog={e['id']:e for e in FACTS['catalog']}
frozen_tags={tag:ast.literal_eval(items) for tag,items in re.findall(r"event\.add\('([^']+)', (\[.*?\])\)",(ROOT/'kubejs/server_scripts/svs_collect_tags.js').read_text(encoding='utf-8'))}
collection_names=['初识','见闻','珍藏','奇兵','传世']
source='用户2026-10-17完整重写要求；本包制作资料与quest_content_v5.json静态取得证据；剧情v4'

def name(id):
    if id.startswith('#'):
        path=id.split(':',1)[-1];parts=path.split('/')
        if len(parts)==1:return {'planks':'木板','logs':'原木','logs_that_burn':'可燃原木','coals':'煤或木炭','wool':'羊毛'}.get(path,'JEI所列同类材料')
        forms={'ingots':'锭','nuggets':'粒','gems':'宝石','plates':'板','dusts':'粉','storage_blocks':'块','ores':'矿石'}
        metals={'iron':'铁','gold':'金','netherite':'下界合金','copper':'铜','steel':'钢','bronze':'青铜','silver':'银','cobalt':'钴','tin':'锡','lead':'铅','aluminum':'铝','zinc':'锌'}
        if parts[0] in forms and parts[-1] in metals:return metals[parts[-1]]+forms[parts[0]]+'（同类材料）'
        if parts[-1] in ('diamond','emerald','lapis','quartz','amethyst'):return {'diamond':'钻石','emerald':'绿宝石','lapis':'青金石','quartz':'石英','amethyst':'紫水晶'}[parts[-1]]+'（同类材料）'
        return 'JEI所列同类材料'
    return names.get(id,id.split(':',1)[-1].replace('_',' ').title())
def sec(title,*lines):return dict(title=title,lines=list(lines))
def add(key,ch,title,deps,tasks,text,icon=None,**extra):
    assert key not in q,key
    q[key]=dict(key=key,chapter=ch,title=title,deps=deps,tasks=tasks,text=text,
                optional=True,availability='pending' if any(t['kind']=='pending' for t in tasks) else 'wired',
                xp=0,items=[],writing_style='v5',source=source,**extra)
    if icon:q[key]['icon']=icon
    return q[key]
def item(id,count=1):return dict(kind='item',target=id,count=count,consume=False)
def read(key,ch,title,text,icon='minecraft:book',deps=None,**extra):
    return add(key,ch,title,deps or [],[dict(kind='checkmark',target='',count=1)],text,icon,**extra)
def chapter(key,title,group,icon):
    assert key not in {c['key'] for c in d['chapters']},key
    d['chapters'].append(dict(key=key,title=title,group=group,icon=icon))
def link(key,label):return dict(key=key,label=label)
def catkey(id):return 'V5_ITEM_'+hashlib.sha256(id.encode()).hexdigest()[:16]

modtitles={'minecraft':'原版军械','magistuarmory':'史诗骑士','dungeons_and_combat':'地牢与战斗','slu':'魂系军械',
 'jerotesvillage':'村民与二轮','jerotes':'杰罗特兵工','simplyswords':'简易刀剑','epicfight_dd':'史诗多样兵器',
 'epicfight':'史诗战斗','efn':'夜幕兵器','cdmoveset':'多变武技','wom':'奇迹武器','cataclysm':'灾变军械',
 'spore':'真菌武装','legendary_monsters':'传奇怪物','monsterexpansion':'巨兽猎装','bloodandmadness':'血源兵器',
 'irons_spellbooks':'铁魔法装备','saintsdragons':'圣龙军备','mowziesmobs':'荒野奇观','tconstruct':'匠魂工具',
 'eeeabsmobs':'无名遗迹','silence_s_defense_tower':'静默军工','artifacts':'遗物','relics':'遗珍',
 'w_o_w_armors_and_weapons':'魔兽兵装','woc_remastered':'混沌战具','epicfight_awaken':'觉醒兵器',
 'sword_soaring':'御剑','alexsmobs':'动物生态','aquamirae':'冰海遗物','souls_like_armors':'魂系甲胄',
 '_misc':'地域遗珍与特色装备','farmersdelight':'农夫军需','nethersdelight':'下界军需','refm':'远征兵器',
 'epicfightx':'史诗扩展','wukong':'齐天兵器','bonfires':'篝火兵器','cloudertinker':'云匠工艺',
 'ringsofascension':'升华戒指','iss_elden_ring':'艾尔登法术装备','tinkers_ingenuity':'匠心饰品',
 'sophisticatedbackpacks':'精妙背包'}
types={'sword':'剑','longsword':'长剑','greatsword':'大剑','tachi':'大太刀','katana':'刀','spear':'长矛','dagger':'匕首',
 'axe':'斧','shield':'盾','bow':'弓','crossbow':'弩','trident':'三叉戟','staff':'法杖','fist':'拳套','uchigatana':'打刀',
 'glaive':'长柄刃','rapier':'刺剑','twinblade':'双头刃','scythe':'镰','hammer':'锤','sickle':'短镰','pickaxe':'矿镐','shovel':'铲'}
def form(e):
    typ=(e.get('combat_category') or e.get('category','').split(':')[-1]).lower()
    if typ in types:return types[typ]
    path=e['id'].split(':')[1]
    for word,label in sorted(types.items(),key=lambda x:-len(x[0])):
        if word in path:return label
    return '特色兵器'
def acquisition(e):
    lines=[]
    for recipe in e['sources'][:2]:
        station={'minecraft:crafting_shaped':'工作台','minecraft:crafting_shapeless':'工作台',
                 'minecraft:smithing_transform':'锻造台','minecraft:smelting':'熔炉','minecraft:blasting':'高炉'}.get(recipe['type'],'专用工艺')
        ingredients='、'.join(name(id) for id in recipe['ingredients'][:7])
        lines.append(station+'路线'+('：'+ingredients if ingredients else '：查看JEI的当前配方')+'。')
    entities=[s for s in e['loot'] if ':entities/' in s]
    chest=[s for s in e['loot'] if ':chests/' in s]
    if entities:
        matches=[]
        for s in entities[:4]:
            target=s.replace(':entities/',':')
            boss=next((v for v in old.values() if v.get('boss_entity')==target),None)
            matches.append(boss['title'].split(' · ')[-1] if boss else target.split(':')[-1].replace('_',' '))
        lines.append('战利品线索：'+ '、'.join(matches)+'。掉落可能受条件或随机性影响。')
    if chest:lines.append('另见'+modtitles.get(e['id'].split(':')[0],e['id'].split(':')[0])+'的探索宝箱战利品；不保证每个箱子都有。')
    if not lines:lines=['特殊取得路线：查看本物品的JEI页面、原生说明与相关挑战。任务不额外复制这件装备。']
    return lines

def equipment_notes(e,purpose):
    sections=[sec('选择与试用',purpose)]
    if e.get('styles'):
        labels={'one_hand':'单持','two_hand':'双持','mount':'骑乘','common':'通用','ranged':'远程','sheath':'收刀','dual_wield':'双持兵器'}
        sections.append(sec('战技装配','当前动作配置包含：'+'、'.join(dict.fromkeys(labels.get(s,'专用架势') for s in e['styles']))+'。先在安全区域确认切换条件与收招。'))
    if e.get('skills'):
        lines=[]
        for skill in e['skills']:
            lines.append('固有战技：'+skill['name']+'。')
            if skill['description']:
                description=re.sub(r'%[\d$.]*[sdf]','相应数值',skill['description']).replace('\\n','\n')
                lines.extend(description.splitlines())
        sections.append(sec('当前固有战技',*lines,'触发、充能与可用数值以当前游戏内技能提示为准；本页不额外发放技能书。'))
    tips=e.get('tooltips',[])
    if tips:
        lines=[];paragraph=''
        for text in tips:
            text=re.sub(r'%[\d$.]*[sdf]','相应数值',text).replace('\\n','\n')
            if not text:
                if paragraph:lines.append(paragraph);paragraph=''
            elif '\n' in text:
                if paragraph:lines.append(paragraph);paragraph=''
                lines.extend(text.splitlines())
            elif not paragraph and ('效果：' in text or '被动：' in text):lines.append(text)
            else:paragraph+=text
        if paragraph:lines.append(paragraph)
        sections.append(sec('原生物品说明',*lines,'上述为本包原生说明；效果是否受当前配置调整，以实际物品提示为准。'))
    return sections

# Catalogue groups stay separate from the four career routes and main progress.
d['groups'] += [['arsenal','军械全鉴 · 武器与工具'],['armory','军械全鉴 · 护甲套装'],['curios','军械全鉴 · 饰品与遗珍']]
for v in q.values():
    if v['chapter'] not in ('start','prologue'):v['writing_style']='v5'

# Boss chapters become reconnaissance -> combat -> equipment-use maps, with dossiers inside combat nodes.
bosses=[v for v in q.values() if v.get('boss_slot')]
boss_icon_report=[]
structure_index=json.loads((ROOT/'docs/data/现版资料索引.json').read_text(encoding='utf-8'))
structures={r['id'] for r in structure_index['resources'] if r['kind']=='structure'}
for v in bosses:
    slot=v['boss_slot'];facts=DOSSIERS[slot];entity=v.get('boss_entity','spore:proto')
    loot=[id for id,sources in FACTS['loot'].items() if entity.replace(':',':entities/',1) in sources and id not in ('minecraft:air','epicfight:skillbook') and 'music_disc' not in id]
    candidate=facts['icon_candidate']
    if candidate not in names:
        candidate=next((id for id in loot if not id.startswith('minecraft:') and id in names),None)
    if not candidate:
        matching=[id for id in names if id.startswith(entity.split(':')[0]+':') and entity.split(':')[1].replace('boss_','') in id and ('egg' in id or 'sword' in id)]
        candidate=next(iter(matching),None)
    assert candidate in names,(slot,candidate)
    v['icon']=candidate
    if slot!='M26':v.pop('icon_texture',None)
    v['subtitle']=facts['location']
    v['text'][0]=facts['lore']
    v['text'][2]=facts['tactics']
    v['sections']=[sec('远征情报',facts['location']+'。',
        '主线征伐目标；按本阶段连线推进。' if slot.startswith('M') else '独立挑战；不作为主线或四职业的毕业门槛。'),
        sec('战前整备',facts['tactics']),
        sec('战利品与后续用途',('原生战利品线索：'+ '、'.join(name(id) for id in loot[:8])+'。' if loot else '这场胜利与装备持有分别记录。战利品按原生挑战结算，不以猜测填入必掉清单。'),
            '在物品页查看配方与用途；原生掉落由战场拾取，本任务的补给单独列在奖励区。')]
    v['links']=[]
    s=facts['structure']
    if s:
        assert s in structures,(slot,s)
        key='V5_SCOUT_'+slot
        add(key,v['chapter'],'侦察 · '+facts['location'],[],[dict(kind='structure',target=s,count=1)],
            ['标记'+facts['location']+'，为'+v['title'].split(' · ')[-1]+'的挑战准备往返路线。',
             '抵达对应结构范围。','结构到访只证明位置，不等于首领已出现、已起战或已经获胜。',
             '场地已记入星图；带好实际起战物，再选择战斗时机。'],'minecraft:filled_map',
             subtitle='自然探索线索 · 到访不算胜利')
        v['links'].append(link(key,'侦察'+facts['location']))
    boss_icon_report.append(dict(slot=slot,entity=entity,icon=candidate,mode='真实正面16像素图' if v.get('icon_texture') else '对应原生战利品/武装徽记',fallback_spawn_egg='egg' in candidate))

# Conquest produces useful, modest supplies, with new claim IDs so a previously
# claimed tellraw can never masquerade as a newly added material reward.
supplies=[('minecraft:copper_ingot',4),('kubejs:refined_iron_ingot',3),('tconstruct:cobalt_ingot',2),
 ('minecraft:cooked_beef',8),('minecraft:gold_ingot',4),('tconstruct:cobalt_ingot',4),('tconstruct:slimesteel_ingot',4),
 ('minecraft:gold_ingot',8),('kubejs:spore_coin',8),('tconstruct:hepatizon_ingot',2),('minecraft:blaze_rod',4),
 ('tconstruct:manyullyn_ingot',2),('tconstruct:rose_gold_ingot',4),('kubejs:spore_coin',10),('minecraft:gold_ingot',8),
 ('tconstruct:manyullyn_ingot',2),('minecraft:netherite_scrap',2),('minecraft:redstone',16),('minecraft:ender_pearl',4),
 ('minecraft:quartz',16),('tconstruct:manyullyn_ingot',2),('minecraft:golden_carrot',8),('kubejs:spore_coin',10),
 ('minecraft:netherite_scrap',2)]
for index,(id,count) in enumerate(supplies,1):
    v=q[f'V4_M{index:02}'];v['items']=[[id,count]]
    v['reward_id_keys']={'1':'v5_supply','2':'1'}
    v['text'][3]='原生掉落在战场拾取；本项另给'+name(id)+'×'+str(count)+'作为下一段远征的军需。'

# Full weapon catalogue; recipe ancestry is navigable without imposing collection on combat.
weapon_pages=[];equipment_map={};set_groups=collections.defaultdict(list)
for e in catalog.values():
    if e['kind']=='armor':
        base=re.sub(r'_(helmet|chestplate|leggings|boots|hood|robe|cuirass|greaves|sabatons|armor_head|armor_chest|armor_legs|armor_feet)$','',e['id'])
        set_groups[base].append(e)
for kind,group,prefix in [('weapon','arsenal','兵器'),('curio','curios','饰品')]:
    by_mod=collections.defaultdict(list)
    for e in catalog.values():
        if e['kind']==kind:by_mod[e['id'].split(':')[0]].append(e)
    small=[ns for ns,es in by_mod.items() if len(es)<12]
    if len(small)>2:
        by_mod['_misc']=[e for ns in small for e in by_mod.pop(ns)]
    for ns,entries in sorted(by_mod.items()):
        entries.sort(key=lambda e:(form(e) if kind=='weapon' else '',e['id']))
        for page in range(math.ceil(len(entries)/35)):
            ch=f'v5_{kind}_{ns}_{page+1}';subset=entries[page*35:(page+1)*35];root=ch+'_INDEX'
            title=prefix+' · '+modtitles.get(ns,ns)+(f' {page+1}/{math.ceil(len(entries)/35)}' if len(entries)>35 else '')
            chapter(ch,title,group,subset[0]['id'])
            read(root,ch,title,['完整军械档案：本页收录'+str(len(subset))+'件'+('兵器与战斗工具。' if kind=='weapon' else '饰品。'),
                '取得任意感兴趣的装备，记录实际持有；所有物品检测均不扣除。',
                '这是独立收藏页。无需集齐全页，也不需要按历史面板排序换装；成长路线在收藏家与锻造师章节。',
                '查取得路径、试用手感，再决定它在你行装中的位置。'],subset[0]['id'])
            q[root]['position']=[6,-3.5]
            for index,e in enumerate(subset):
                id=e['id'];key=catkey(id);equipment_map[id]=key
                purpose=('形态：'+form(e)+'。先在安全地带试单持、双持或技能连段，再决定它适合突进、周旋还是另一种战术。' if kind=='weapon' else '装备前阅读槽位与原生效果；与其他饰品一起使用时，先检查槽位冲突和触发条件。')
                v=add(key,ch,e['name'],[root],[item(id)],
                    ['把'+e['name']+'收入'+modtitles.get(id.split(':')[0],id.split(':')[0])+'的'+('军械档案。' if kind=='weapon' else '遗珍档案。'),
                     '持有'+e['name']+'1件，不消耗；不限耐久、附魔或已有自定义名称。',purpose,
                     '留下收藏记录；任务不返还一份复制品，也不要求你放弃已经趁手的装备。'],id,
                    subtitle=(form(e)+' · ' if kind=='weapon' else '')+('制作路线' if e['sources'] else '探索/特殊取得'),catalog_items=[id],
                    sections=[sec('取得路线',*acquisition(e))]+equipment_notes(e,purpose))
                v['position']=[(index%7)*2.7,(index//7)*3.0]
                if kind=='weapon':weapon_pages.append(key)

by_mod=collections.defaultdict(list)
for base,entries in set_groups.items():by_mod[base.split(':')[0]].append((base,entries))
small=[ns for ns,sets in by_mod.items() if len(sets)<7]
if len(small)>2:by_mod['_misc']=[e for ns in small for e in by_mod.pop(ns)]
for ns,sets in sorted(by_mod.items()):
    sets.sort()
    for page in range(math.ceil(len(sets)/30)):
        ch=f'v5_armor_{ns}_{page+1}';subset=sets[page*30:(page+1)*30];root=ch+'_INDEX'
        title='护甲 · '+modtitles.get(ns,ns)+(f' {page+1}/{math.ceil(len(sets)/30)}' if len(sets)>30 else '')
        chapter(ch,title,'armory',subset[0][1][0]['id'])
        read(root,ch,title,['把护甲按实际部件和系列整理，比较取得成本与用途。','选择一套行装，收齐本项所列部件；单件特色装备单独记录。',
             '同一系列在此合并展示，不据四件外形推定套装加成。穿戴效果、饰品槽位和材料需求以本包物品说明为准。',
             '主线不要求全套图鉴毕业，按自己的打法逐步替换。'],subset[0][1][0]['id'])
        q[root]['position']=[6,-3.5]
        for index,(base,parts) in enumerate(subset):
            parts.sort(key=lambda e:next((i for i,s in enumerate(['helmet','hood','chestplate','robe','leggings','boots']) if e['id'].endswith('_'+s)),20))
            id=parts[0]['id'];key='V5_SET_'+hashlib.sha256(base.encode()).hexdigest()[:16]
            nm=parts[0]['name'];nm=re.sub(r'(头盔|兜帽|胸甲|胸铠|护腿|靴子|战靴|之靴|Helmet|Hood|Chestplate|Leggings|Boots)$','',nm).strip()
            title=nm+('行装' if len(parts)>1 else ' · 单件护甲')
            lines=[]
            for e in parts:
                equipment_map[e['id']]=key
                lines += [e['name']+'：'+acquisition(e)[0]]
            v=add(key,ch,title,[root],[item(e['id']) for e in parts],
                ['建立'+title+'的装备档案；用实际部件构成一套可携行的远征选择。',
                 '按部件记录：'+'、'.join(e['name'] for e in parts)+'，各1件；可以分次持有，不消耗。',
                 '套装收集记录不等于已穿戴或已触发套装效果。先看属性、耐久、修理途径与机动代价，再决定实际搭配。',
                 '行装已归档；无需全套图鉴毕业才能挑战主线。'],id,catalog_items=[e['id'] for e in parts],
                 subtitle=str(len(parts))+'部件 · '+('单件特色装备' if len(parts)==1 else '同系列收集'),
                 sections=[sec('部件与取得路线',*lines),sec('整备检查','出征前检查耐久与修理材料；展示同系列不表示自动获得隐藏套装增益。',
                 '特色单件可以和其他行装混搭。若原生说明要求整套生效，再按说明选择。')])
            v['position']=[(index%6)*3.2,(index//6)*3.3]

# Real recipe links and source-to-use links, rather than a mandatory all-items chain.
for e in catalog.values():
    key=equipment_map.get(e['id'])
    if not key:continue
    links=q[key].setdefault('links',[])
    for recipe in e['sources'][:2]:
        for ingredient in recipe['ingredients']:
            target=equipment_map.get(ingredient)
            if target and target!=key and target not in [l['key'] for l in links]:links.append(link(target,'前置装备：'+name(ingredient)))
    q[key]['links']=links[:5]
future=collections.defaultdict(set)
for e in catalog.values():
    for recipe in e['sources']:
        for ingredient in recipe['ingredients']:
            if ingredient in equipment_map and ingredient!=e['id']:future[ingredient].add(e['id'])
for id,targets in future.items():
    key=equipment_map[id];lines=[]
    for target in sorted(targets)[:4]:
        lines.append(name(target)+'：该装备是其配方中的已有兵器／部件之一，升级前检查材料与耐久条件。')
        dest=equipment_map[target]
        if dest!=key and dest not in [l['key'] for l in q[key].get('links',[])]:q[key].setdefault('links',[]).append(link(dest,'后续制作：'+name(target)))
    if lines:q[key]['sections'].append(sec('下一件有用的装备',*lines))
for index,label in enumerate(collection_names,1):
    members=frozen_tags['svs:collect_t'+str(index)];core=q['L'+str(index+1).zfill(2)]
    core['text'][1]='同时持有「'+label+'」名单中的武器'+str(core['tasks'][0]['count'])+'件；允许重复计件，不扣除。'
    core['text'][2]='单件装备档案会标明所属收藏名单。这是收藏分册，不代表当前战斗强弱排名。'
    for id in members:
        if id in equipment_map:
            entry=q[equipment_map[id]]
            entry['sections'].append(sec('收藏家计件归属','本装备属于「'+label+'」名单；持有时计入对应收藏目标。'))
            entry.setdefault('links',[]).append(link(core['key'],'查看「'+label+'」计件目标'))
    examples=[id for id in members if id in equipment_map][:5]
    core.setdefault('sections',[]).append(sec('本册例项',*['可选：'+name(id)+'。' for id in examples]))
    core.setdefault('links',[]).extend(link(equipment_map[id],name(id)+'的完整档案') for id in examples)
for v in bosses:
    entity=v.get('boss_entity','spore:proto');drops=[e for e in catalog.values() if entity.replace(':',':entities/',1) in e['loot']]
    # Include derived equipment crafted from the boss's real loot.
    materials={id for id,s in FACTS['loot'].items() if entity.replace(':',':entities/',1) in s}
    derived=[e for e in catalog.values() if any(materials & set(recipe['ingredients']) for recipe in e['sources'])]
    for e in (drops+derived)[:6]:
        target=equipment_map[e['id']]
        if target not in [l['key'] for l in v['links']]:v['links'].append(link(target,'战果用途：'+e['name']))

# Expand all four careers with practical routes that have real, separate outcomes.
chapter('v5_loadouts','收藏家 · 从兵器到成套行装','career','minecraft:armor_stand')
read('V5_LOADOUT_INDEX','v5_loadouts','军械需要组合，而不只是数量',[
 '为不同远征准备主武器、护甲和功能饰品，完整收藏图鉴与实战配装各有作用。',
 '阅读三种整备路线，再选择适合自己的行装。',
 '收藏家聚合目标沿用原标签与既定数量；全图鉴新增的单件记录均为可选，不增加毕业门槛。',
 '一把熟练的兵器、一套可修的护甲和明确的撤退手段，比盲目追逐面板更有价值。'])
q['V5_LOADOUT_INDEX']['position']=[6.,-3.5]
loadouts=[
 ('V5_LOADOUT_LIGHT','轻兵周旋','simplyswords:iron_rapier','用恢复快、自己熟悉的短连段保持进退，不因武器名叫刺剑就假定一切突刺都能破甲。','准备一把铁刺剑，试两轮短连段后检查耐力余量。'),
 ('V5_LOADOUT_REACH','长柄控制','simplyswords:iron_spear','长柄路线的价值在于你能否维持合适距离。贴身挤压和狭窄通道需要另有预案。','准备一把铁矛，练习进攻后退回可观察距离。'),
 ('V5_LOADOUT_HEAVY','重兵窗口','simplyswords:iron_glaive','重兵器需要与你能稳定抓住的输出窗口相配。不要为了打一整套把撤离耐力全部耗尽。','准备一把铁战刃，试清起手、收招与防御切换。'),
 ('V5_LOADOUT_RUNIC','符文升级','simplyswords:runic_longsword','先保留同型底材，再查符文升级材料。升级前检查配方是否接受现有耐久与附魔状态，避免误耗惯用装备。','持有符文长剑，检查其实际技能与修理方案。'),
 ('V5_LOADOUT_HUNT','把首猎制成行装','monsterexpansion:rhyza_helmet','把巨兽素材变成可穿的猎装。先看本包现有配方，缺哪个部件就向对应素材安排下一次狩猎。','持有锐爪兽头盔，再到护甲图鉴查看同系列部件。'),
 ('V5_LOADOUT_BOSS','直接战利品与材料锻造','cataclysm:gauntlet_of_guard','守卫拳套是直接战利品的例子；焰魔与咒魂等材料则需要继续合成。两条取得路径应分别安排，不必为证明收藏重复交出唯一掉落。','持有守卫拳套，查对这一件兵器的取得路径。'),
 ('V5_LOADOUT_SOUL','筹魂锻造','slu:gundyr_axespear','古战场击杀与魂武制作分别记账。基础魂、进阶魂和同名不同级材料不能混用，按JEI逐项筹备。','持有古达斧枪，查找下一把感兴趣的魂武。')]
for index,(key,title,id,advice,work) in enumerate(loadouts):
    assert id in names,id
    v=add(key,'v5_loadouts',title,['V5_LOADOUT_INDEX'],[item(id)],
        ['为下一次远征建立一套可解释的武装选择。',work,advice,'这条路线提供选择，不要求全做，也不自动提高装备属性。'],id,
        sections=[sec('配装思路',advice),sec('取得路线',*acquisition(catalog[id]) if id in catalog else ['在JEI查看当前配方与模组原生说明。'])])
    v['links']=[link(equipment_map[id],'打开装备档案')] if id in equipment_map else []
    v['position']=[(index%4)*4.0,(index//4)*4.0]

# Smith: separate furnace size, alloy temperature, components, tool shapes and maintenance.
chapter('v5_smithcraft','锻造师 · 部件、合金与维修','career','tconstruct:tinkers_anvil')
smith_rows=[
 ('CAST','浇铸与模具','tconstruct:ingot_cast','模具决定金属会变成什么。先在小熔化炉中准备金属，再用排液口浇入放好模具的浇铸台。','持有锭模具；实际完成一次浇铸后，再推进合金与部件。'),
 ('PART','部件制造台','tconstruct:part_builder','先看成品需要哪些部件，再在部件台选相应形状。不同部件位置影响工具的材料与特性，不用一堆原料代替成品。','持有部件制造台，按目标工具配方制作所需部件。'),
 ('STATION','组装与维护','tconstruct:tinker_station','工具站用于起步组装与维修。把材料、部件和实际工具放进对应操作界面，阅读预览后再确认。','持有工匠站，完成一次原生组装或维修练习。'),
 ('SMELTERY','扩大熔铸','tconstruct:smeltery_controller','小熔化炉可以完成起步浇铸；多种熔融金属的合金要核对设备、容量和温度。升级炉体服务于目标合金，而不是为了堆一座空壳。','持有冶炼炉控制器，按匠魂手册准备完整炉体与排液路径。'),
 ('ALLOY','第一种合金','tconstruct:slimesteel_ingot','黏液钢让你开始比较材料特性。准备比例与足够空槽，先少量合金，再决定是否为整把工具投入材料。','持有黏液钢锭4个。'),
 ('COBALT','钴与速度','tconstruct:cobalt_ingot','钴的选择要和工具用途相配。对照当前配方的温度与材料路线，不因矿物来自下界就给整个维度增加任务门禁。','持有钴锭4个。'),
 ('ANVIL','高阶工位','tconstruct:tinkers_anvil','更大的工具与后段工艺需要相应工位。先查看目标工具需要什么，再安排工匠砧与部件材料。','持有工匠砧1个。'),
 ('FUEL','高温燃料','tconstruct:blazing_blood_bucket','高熔点材料要匹配实际燃料温度。先保证容器和供给路径，再提高炉温，避免拿到金属却无法熔化。','持有烈焰血桶1个。'),
 ('MANYULLYN','玛玉灵战备','tconstruct:manyullyn_ingot','后段材料的价值在于特性与使用条件。把它和自己的输出节奏、维修成本一起考虑，不用历史面板把它标成唯一答案。','持有玛玉灵锭4个。'),
 ('HEPATIZON','黑色合金选择','tconstruct:hepatizon_ingot','同阶段的另一种工艺给工具不同的选择。先查配方，再看特性适不适合长途采集或战斗节奏。','持有黑色合金锭4个。'),
 ('QUEEN','王后史莱姆','tconstruct:queens_slime_ingot','把最后一种合金作为选材作业。它不是任务自动赋予工具的额外属性，仍需在对应部件或工艺中实际使用。','持有王后史莱姆锭2个。'),
 ('CLEAVER','重兵器与工作工具','tconstruct:cleaver','劈刀与采集工具承担不同职责。重武器的收招要练，工具则要考虑采集范围、耐久和维修材料。','持有劈刀1把，不限材料。'),
 ('MATTOCK','远征工作工具','tconstruct:mattock','为建设前线带一把合适工具，可以减少来回搬运。按说明确认它能处理的方块，不把工具名当作万能采集保证。','持有鹤嘴锄1把，不限材料。')]
previous='F01'
for index,(suffix,title,id,advice,work) in enumerate(smith_rows):
    assert id in names,id
    count=4 if suffix in ('ALLOY','COBALT','MANYULLYN','HEPATIZON') else 2 if suffix=='QUEEN' else 1
    key='V5_SMITH_'+suffix
    dep=previous if suffix in ('PART','STATION','SMELTERY','ANVIL','FUEL','MANYULLYN') else 'F01'
    v=add(key,'v5_smithcraft',title,[dep],[item(id,count)],
        ['把工艺变成能用于下一次远征的工具与材料。',work,advice,'只记录持有；亲手熔铸、组装和维修属于实操练习，不伪装成自动检测。'],id,
        sections=[sec('操作要点',advice),sec('工艺与取得',*acquisition(catalog[id]) if id in catalog else ['用本包JEI和匠魂手册核对原料、工位与温度。'])])
    v['position']=[(index%5)*3.4,(index//5)*4]
    previous=key

# Dragon species dossier rows use actual egg/scale models; no invented universal taming food.
dragon_rows=[('raevyx','雷翼','雷电巨龙的接近、驯养和骑乘需要分别准备。先看雷翼的原生指南，再选择靠近时机。'),
 ('cindervane','烬羽','烬羽的养成路线和战斗形态各有作用。先为自己的龙准备合适食物与安置空间，再带它进入危险区域。'),
 ('atroxiia','蚀影','蚀影不是其他龙换色后的同一份驯养作业。阅读对应指南，区分接近条件、交互与战斗用途。'),
 ('stegonaut','甲背','地面与厚重形体的龙也可进入远征计划。先确认可用交互和移动条件，再决定伴行或侦察。'),
 ('varasuchus','巨鳄','水边活动的龙需要你先理解接近与撤退路线；饲养、回收和战斗各有准备。'),
 ('ignivorus','噬焰龙','你可以选择收服战争伙伴，也可以独立狩猎取得龙材。不要为了职业任务杀掉自己养成的龙。'),
 ('volitans','蓑鲉龙','面对飞行生态的龙，观察环境和原生交互比照抄一种通用食物更可靠。驯养与狩猎不是强制组合。'),
 ('nulljaw','虚颚','虚颚的养成条件以自己的原生指南为准。本包没有据文件名承诺虚颚蛋，因此不安排找一枚未确认的蛋。')]
chapter('v5_dragon_species','狩龙人 · 八种龙的远征档案','career','minecraft:dragon_egg')
for index,(species,label,advice) in enumerate(dragon_rows):
    suffix=chr(ord('a')+index);key='V5_DRAGON_'+species;target='H04'+suffix
    icon=next((id for id in names if id.startswith('saintsdragons:') and species in id and 'scale' in id),None)
    icon=icon or next(id for id in names if id.startswith('saintsdragons:') and species in id and 'egg' in id)
    v=read(key,'v5_dragon_species',label+' · 接近与养成',
        ['为'+label+'建立独立的养成与战备档案。','阅读对应龙种指南，准备原生食物、接近方式与安全安置点。',advice,
         '本页是阅读与准备记录；真实驯服以对应原生进度记录，任务不会赠送或复制一条龙。'],icon,sections=[sec('出发清单',
         '查对应龙种的原生指南，不把任意生肉当成八种龙的通用条件。','确认接近、驯服、喂食和可骑乘条件，给失败后的撤离留出空间。'),
         sec('养成后的用途',advice,'是否骑乘、伴行或参与战斗，以该龙种实际能力与原生设置为准。')],links=[link(target,'记录'+label+'的真实驯服')])
    v['position']=[(index%4)*4,(index//4)*4]

chapter('v5_symbiote_field','共生使 · 狩猎、压力与远征','career','minecraft:amethyst_shard')
sym_rows=[
 ('STAGES','四阶战甲','附着、整合、合作、主导是共生结合的四个阶段。先看自己的实际档案，阶段任务可以认可已经达到的更高阶段。','观察当前结合阶段与可用能力，不要求退化后重练。'),
 ('TRUST','信赖与成长','信赖数值、愿望、压力与进化阶段相关却不是同一个目标。不要把一次信赖上涨当成直接进入下一阶。','查看一次自己的实际状态与愿望，再选择可完成的交互。'),
 ('FEED','喂食与补给','准备食物和真正喂入是两种行为。按当前可用交互进行喂食，出征前留出自己与共生体各自的补给。','完成一次原生喂食后手动确认；仅持有食物不算交互。'),
 ('HUNT','狩猎红利','在狩猎状态亲手有效击杀真菌，才进入当前已实现的红利路线。炮塔与环境代杀不能冒充这项个人作业。','确认狩猎状态，再到共生使主页面完成一次有效狩猎。'),
 ('STRESS','压力不是勋章','压力管理是保障持续作战的手段。没有必要故意受击、失控或把状态推到危险阈值来证明自己会使用共生体。','查看压力，并按原生可用方式处理；无压力时也可练习查看。'),
 ('SIEGE','围城中的天敌','真菌优先仇恨与围城压力提醒意味着更高收益也有额外风险。开战前看撤退路线，不把伙伴的存在当成无敌保证。','检查围城前的个人状态与补给后手动确认。'),
 ('STRAIN','菌株属于自己','菌株随机、个人进化可退化；队伍共享任务不会复制另一个人的菌株或档案。选择围绕自己现有能力展开。','阅读个人档案与共享任务的区别。'),
 ('ABILITIES','只练已经掌握的能力','键位以自己的控制设置为准，先看能力是否已经可用，再进行安全试用。触手辅助战的后续开发不等于当前已经解锁。','在安全处选择一项当前可用能力进行试用，再手动确认。')]
for index,(suffix,title,advice,work) in enumerate(sym_rows):
    key='V5_SYM_'+suffix
    v=read(key,'v5_symbiote_field',title,['让共生体成为可以持续驾驭的战甲，而不是只追一个阶段数字。',work,advice,
        '这是一项操作说明与自报练习；四阶和狩猎的真实检测仍在共生使主页面。'],'minecraft:amethyst_shard',
        sections=[sec('实操说明',advice)],links=[link('J05' if suffix=='HUNT' else 'J01','回到共生使成长路线')])
    v['position']=[(index%4)*4,(index//4)*4]

q['V5_SYM_STAGES']['sections'].append(sec('当前已实现的真菌克制',
    '附着：对真菌伤害×1.10，受到真菌伤害减少10%。',
    '整合：对真菌伤害×1.20，受到真菌伤害减少15%。',
    '合作：对真菌伤害×1.35，受到真菌伤害减少22%。',
    '主导：对真菌伤害×1.50，受到真菌伤害减少30%。',
    '按当前个人结合阶段生效；历史任务完成记录不把退化后的能力永久保持在最高阶。'))

# A dedicated, compact military production route uses real turret objects and recipes.
chapter('v5_fortress','要塞军工 · 核心、炮塔与后勤','career','silence_s_defense_tower:driving_core_1')
military=[
 ('CORE','第一枚驱动核心','silence_s_defense_tower:driving_core_1','铁锭3、石头4、活塞1、中继器1，是基础驱动核心的原生工作台路线。先造核心，再考虑炮塔；没有预设电网长链。'),
 ('TURRET','第一座箭塔','silence_s_defense_tower:arrow_turret_leavl1_p','基础核心、弩、木桶、石台阶与原木构成入门箭塔便携物品。持有只算备料，实际部署、供给、攻击和回收在军工演练另行确认。'),
 ('COUNTER','为升级记录战果','silence_s_defense_tower:counter_1','计数器由中继器、铁锭与红石合成。计数和核心升级的实际扣除按原生操作核对，不把物品栏里的数字当成已经成功升级。'),
 ('GLOVES','回收工具','silence_s_defense_tower:gloves','手套由皮革、箱子与铁锭合成。远征前准备回收工具，先在安全处熟悉交互，避免把唯一炮塔留在无法回收的位置。'),
 ('UPGRADE','核心升级台','silence_s_defense_tower:core_upgrade_table','石砖6、铁锭2与工作台1构成核心升级台。升级前准备原生材料和计数条件；JEI的单张材料图标不代表实际扣除只需一个。'),
 ('MAINTAIN','战地维修站','silence_s_defense_tower:maintenance_station0','石砖8与高炉1构成维修站便携物品。把修复与再部署纳入前线后勤，实际可修对象和消耗按原生说明检查。'),
 ('CORE3','三级驱动','silence_s_defense_tower:driving_core_3','按升级台界面逐级准备材料。研究台会消耗一枚三级核心，不能把同一枚核心同时算成研究台原料和已装入炮塔的动力。'),
 ('RESEARCH','研究台与世界科技','silence_s_defense_tower:research_table','木板、绿色羊毛、书架和三级核心进入研究台路线。研究可能作用于世界范围；不要把原生全局科技当成队伍独占能力。')]
for index,(suffix,title,id,advice) in enumerate(military):
    assert id in names,id
    key='V5_FACTORY_'+suffix
    dep=['A12'] if index==0 else ['V5_FACTORY_CORE' if index<4 else 'V5_FACTORY_UPGRADE' if index>4 else 'V5_FACTORY_COUNTER']
    v=add(key,'v5_fortress',title,dep,[item(id)],['把现有军工模组转成可供给、可维修、能随远征推进的防线。',
        '持有'+name(id)+'1个，不消耗。',advice,'完成备料记录；炮塔实战与攻击归因仍以独立军工演练的实际结果结算。'],id,
        sections=[sec('制作与使用',advice)],links=[link('V4_TOWER1','查看首次炮塔实战的开放状态')])
    v['position']=[(index%4)*4,(index//4)*4]

# Navigation hub: optional encyclopedia pages are discoverable without entering every chapter.
chapter('v5_catalog_index','军械导航 · 系列与取得路线','manual','minecraft:item_frame')
for index,(group,label) in enumerate([('arsenal','武器与战斗工具'),('armory','护甲套装与单件'),('curios','饰品与遗珍')]):
    pages=[c for c in d['chapters'] if c['group']==group]
    chunks=[pages[i:i+16] for i in range(0,len(pages),16)]
    for part,subset in enumerate(chunks):
        key=f'V5_NAV_{group}_{part}'
        v=read(key,'v5_catalog_index',label+' · '+str(part+1),[
           '按模组系列查看完整装备，不把全部收藏变成主线清单。','选择下面的系列链接，查看真实物品图标、取得线索和前置装备。',
           '护甲按实际部件合并；武器配方能跳转到已有前置装备；饰品先检查槽位与触发条件。',
           '只有感兴趣的行装需要投入材料；本页是导航，不发稀有装备复制奖励。'],
           'minecraft:item_frame',links=[link(c['key']+'_INDEX',re.sub('&.','',c['title'])) for c in subset])
        v['position']=[index*5,part*3.5]

# Main phase preparation and consequence nodes make the war a journey rather than a bare boss list.
prep=[
 ('departure','V5_WAR1','荒野开猎','A12','minecraft:cooked_beef','先让据点能够补充食物、修理与回程，再选择第一只巨兽。血肉筑基的三场狩猎可以自行安排顺序。','monsterexpansion:rhyza_helmet'),
 ('journey','V5_WAR2','吞并边疆','V4_PHASE1','minecraft:iron_ingot','将矿路、古族、魔像、遗迹和冰海视作不同远征，不必为了开下一页反复回村交付。海洋战额外解决呼吸与返程。','simplyswords:runic_longsword'),
 ('front','V5_WAR3','猎手之后，诸王之前','V4_PHASE2','minecraft:shield','本段分为猎手、夺火、夺权和咒翼压轴。先稳定一套近战与辅助能力，再选择神权远征的次序。','tconstruct:manyullyn_ingot'),
 ('counterattack','V5_WAR4','将军工推到前线','V4_PHASE3','minecraft:ender_chest','机械三战负责夺械，守界四战负责开路。炮塔供给与真实打击、母巢战役和大圣传承各有独立结算，读完计划不会替代实战。','cataclysm:cursium_ingot')]
for index,(ch,key,title,dep,id,advice,gear) in enumerate(prep):
    v=add(key,ch,title,[dep],[item(id,8 if id.endswith('cooked_beef') else 1)],
       ['把本阶段的兵器、补给与远征目标安排在同一张星图上。','准备'+name(id)+('8个。' if id.endswith('cooked_beef') else '1个。'),advice,
        '补给只检测持有，不扣除；出发顺序由本段的实际依赖决定。'],id,subtitle='本段战前整备',
        sections=[sec('本段远征目标',advice),sec('出征前检查','检查武器熟练度、护甲耐久、口粮与返程点。','受控入口尚未开放时，先进行其他可达远征与职业成长。')],
        links=[link('V5_LOADOUT_INDEX','整备武装组合'),link('V5_SMITH_STATION','工具维护'),
               link(equipment_map.get(gear,'F10' if gear.startswith('tconstruct:') else 'V4_M17'),'本段军械线索')])
    v['position']=[-5,-3]

# Link legacy career spotlights into the full archive; replace placeholder-only conclusions.
for v in list(q.values()):
    if v['chapter'] in ('collector','smith','dragon','symbiote','recon','expedition','manual','atlas'):
        if v['chapter']=='collector':v.setdefault('sections',[]).append(sec('收藏与实战','聚合任务按既定件数计数，不要求不同种；名品节点和全军械图鉴提供实际取得与升级导航。','全图鉴均为独立收藏，不成为收藏家毕业或主线的额外条件。'))
        for t in v['tasks']:
            if t['kind']=='item' and t['target'] in equipment_map:
                v.setdefault('links',[]).append(link(equipment_map[t['target']],'查看'+name(t['target'])+'的完整档案'))
        if v['chapter']=='smith':v.setdefault('links',[]).append(link('V5_SMITH_CAST','查看熔铸、部件与维护路线'))
        if v['chapter']=='dragon':v.setdefault('links',[]).append(link('V5_DRAGON_raevyx','查看八种龙的独立档案'))
        if v['chapter']=='symbiote':v.setdefault('links',[]).append(link('V5_SYM_STAGES','查看共生野战手册'))

# Layout: clear field/background panels, a dossier spine, and equipment cards; never generic skulls.
for ch in d['chapters']:
    nodes=[v for v in q.values() if v['chapter']==ch['key']]
    for index,v in enumerate(nodes):
        if 'position' not in v:
            row,col=divmod(index,6);v['position']=[(col if row%2==0 else 5-col)*2.5,row*3.5]
    if ch['key'] in ('departure','journey','front','counterattack','hunts','souls'):
        central=[v for v in nodes if v.get('boss_slot')]
        for index,v in enumerate(central):
            x=(index%3)*7.;y=(index//3)*6.
            if ch['key'] in ('counterattack',):
                x=(index%3)*7.;y=(index//3)*7.
            v['position']=[x,y]
            scout=q.get('V5_SCOUT_'+v['boss_slot'])
            if scout:scout['position']=[x-2.2,y-1.6]
        used={tuple(v.get('position',[])) for v in central}
        others=[v for v in nodes if not v.get('boss_slot') and not v['key'].startswith(('V5_SCOUT_','V5_WAR'))]
        for index,v in enumerate(others):v['position']=[(index%4)*4.5,-7.-(index//4)*3.5]
        # Read top to bottom: field intelligence, fights, then the phase outcome.
        milestone={'departure':'V4_PHASE1','journey':'V4_PHASE2','front':'V4_PHASE3'}.get(ch['key'])
        if milestone:
            bottom=max(v['position'][1] for v in central)+5.
            q[milestone]['position']=[7.,bottom]
            for v in others:
                if v['key']!=milestone:v['position']=[19.+3.5*others.index(v),bottom]
        if ch['key']=='counterattack':
            placements={'V4_M18':[-7.,0.],'V4_M19':[0.,0.],'V4_M20':[7.,0.],
                        'V4_STRIKE':[14.,0.],'V4_M21':[-7.,6.],'V4_M22':[0.,6.],
                        'V4_M23':[7.,6.],'V4_M24':[14.,6.],'V4_M25':[3.5,12.],
                        'V4_M26':[3.5,18.],'V4_CROWN':[3.5,23.],'V5_WAR4':[-12.,-3.]}
            for k,p in placements.items():q[k]['position']=p
            for v in central:
                scout=q.get('V5_SCOUT_'+v['boss_slot'])
                if scout:scout['position']=[v['position'][0]-2.2,v['position'][1]-1.6]
        if ch['key']=='front':
            placements={'V4_M09':[-7.,0.],'V4_M10':[-7.,5.],'V4_M11':[-7.,10.],
                        'V4_M12':[-7.,15.],'V4_M13':[0.,0.],'V4_M14':[7.,0.],
                        'V4_M15':[0.,6.],'V4_M16':[7.,6.],'V4_M17':[3.5,15.],
                        'V4_PHASE3':[3.5,20.],'V4_FIRE':[-7.,20.],'V5_WAR3':[-12.,-3.]}
            for k,p in placements.items():q[k]['position']=p
            for v in central:
                scout=q.get('V5_SCOUT_'+v['boss_slot'])
                if scout:scout['position']=[v['position'][0]-2.2,v['position'][1]-1.6]
    # Background panels are existing vanilla resources with verified FTB image fields.
    points=[v.get('position',[0,0]) for v in nodes]
    if points:
        xmin=min(p[0] for p in points)-1.3;xmax=max(p[0] for p in points)+1.3
        ymin=min(p[1] for p in points)-1.3;ymax=max(p[1] for p in points)+1.3
        ch['images']=[dict(x=(xmin+xmax)/2,y=(ymin+ymax)/2,width=xmax-xmin,height=ymax-ymin,
           rotation=0.0,image='minecraft:textures/block/deepslate_tiles.png',alpha=34,order=-100,
           hover=[ch['title']],click='',dev=False,corner=False)]
    ch['title']=('&6' if ch['group']=='main' else '&b' if ch['group']=='career' else '&a' if ch['group'] in ('arsenal','armory','curios') else '&7')+re.sub('&.','',ch['title'])

for v in q.values():
    if 'sections' in v:
        # Deduplicate navigation entries while preserving deliberate display order.
        seen=set();v['links']=[l for l in v.get('links',[]) if not (l['key'] in seen or seen.add(l['key']))]
    assert len(v['text'])==4 and all(v['text']),v['key']
    assert v['tasks'],v['key']
d.update(schema=3,story_version=4,editorial_version=5,
    authority='用户2026-10-17指出旧版粗糙，要求研究三个参考包后完全重写FTB；本轮覆盖主线、Boss情报、四职业与全军械图鉴')
d['quests']=list(q.values())
(ROOT/'docs/questbook_v2.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=dict(catalog_counts=dict(collections.Counter(e['kind'] for e in catalog.values())),
    covered_item_ids=sorted(equipment_map),armor_sets=len(set_groups),boss_icons=boss_icon_report,
    chapters=len(d['chapters']),quests=len(q),source_scope=FACTS['scope'],excluded=FACTS['excluded'])
(ROOT/'docs/data/questbook_v5_coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('covered_item_ids','boss_icons','excluded')},ensure_ascii=False))
