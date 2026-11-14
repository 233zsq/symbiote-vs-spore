"""One-time, reviewable v2 -> story-v4 migration. Normal edits use questbook_v2.json.

Never writes an instance or save. Refuses to migrate an already migrated source.
"""
import copy, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/questbook_v2.json'
BACKUP=ROOT/'backups/questbook_v4_20261017/before'
d=json.loads(SOURCE.read_text(encoding='utf-8'))
assert not any(q['key']=='V4_M01' for q in d['quests']), 'already migrated'
assert not BACKUP.exists(), 'backup exists; review rather than overwrite'
for rel in ['docs/questbook_v2.json','tools/build_questbook_v2.py',
            'docs/FTB任务v2_ID映射.json','docs/FTB任务v2_节点与验收目录.md',
            'kubejs/server_scripts/svs_quests_v2_bindings.js','config/ftbquests/quests']:
    src=ROOT/rel; dst=BACKUP/rel; dst.parent.mkdir(parents=True,exist_ok=True)
    if src.is_dir(): shutil.copytree(src,dst)
    else: shutil.copy2(src,dst)
old={q['key']:copy.deepcopy(q) for q in d['quests']}
q={k:copy.deepcopy(v) for k,v in old.items()}
source='剧情重写_v4_天外成王篇.md；天外成王篇_玩法与落地方案_v1.md；2026-10-17用户授权全书重写'

def text(key,title,goal,work,hint,result):
    q[key].update(title=title,text=[goal,work,hint,result],writing_style='v4',source=source)

def add(key,ch,title,deps,tasks,goal,work,hint,result,optional=False,**extra):
    q[key]=dict(key=key,chapter=ch,title=title,deps=deps,tasks=tasks,
                text=[goal,work,hint,result],writing_style='v4',source=source,
                optional=optional,availability='pending' if any(t['kind']=='pending' for t in tasks) else 'wired',
                xp=0,items=[],**extra)

def milestone(key,ch,title,deps,stage=None):
    add(key,ch,title,deps,[dict(kind='bridge',target='milestone',count=1)],
        '汇合本阶段征伐成果，向下一片战场进军。','完成连线所示的全部主线讨伐。',
        '四职业、独立猎场与竞技场均可自行安排，不必完成才能进军。',
        '本阶段战绩已记入征伐星图。',**({'stage':stage} if stage else {}))

# Relocate the real scouting/arena routes; retired milestones cannot grant new victories.
retire={'B11','C22','D12','D16','D19','D23','D25','D29',
        'E02','E03','E04','E05','E09','E10','E11','E12','E14','E16','E17','E18',
        'C23','HUNT_maledictus','HUNT_BB_father_gascoigne','HUNT_BB_gascoigne_beast',
        'HUNT_BB_micolash','SOUL_boss_soul_of_cinder'}
for k in retire: q.pop(k)
for v in q.values():
    if v['chapter'] in ('departure','journey','front'):
        v['chapter']='recon' if v['key'] in {'B01','B04','B05','B06','B07','B08','B09','B10','C02','C03','C04','C05','C06','C07','D02','D03','D04','D05','D07','D08','D11','D18','D21'} else 'expedition'
        v['optional']=True
    v['writing_style']='v4'
    # Replace the obsolete narrator, retaining factual tasks and useful craft instructions.
    if v['chapter'] not in ('start','prologue'):
        v['source']=source+'；原任务已核检测与奖励沿用'
        v['text'][3]={
            'collector':'兵器已收入你的军械库；是否带上战场，由你选择。',
            'smith':'将这道工艺用于下一次出征，军械供给由你掌握。',
            'dragon':'将龙族的力量纳入你的远征计划。',
            'symbiote':'掌控天外血肉，让进化为征伐效力。',
            'commissions':'整备军资，等待下一次出征。',
            'manual':'据此整备装备、能力与军需。',
            'atlas':'标记目标与退路，再向下一处战场推进。',
        }.get(v['chapter'],'本次远征记录已归入星图，战果可用于下一次整备。')
    if not v['tasks']:
        v['tasks']=[dict(kind='bridge',target='milestone',count=1)]

depmap={'B11':'V4_PHASE1','C22':'V4_PHASE2','D29':'V4_PHASE3',
        'D12':'HUNT_harbinger','D16':'V4_S02','D19':'HUNT_ignis',
        'E12':'V4_M25','E14':'V4_M25'}
for v in q.values():v['deps']=[depmap.get(k,k) for k in v['deps']]
q['C09']['deps']=['A12']; q['D11']['deps']=['V4_PHASE2']; q['D18']['deps']=['V4_PHASE2']
q['D21']['deps']=['D08']

rows='''锐爪兽|monsterexpansion:rhyza|猎食者的利爪|猎取荒野霸主，将高敏掠食者的战利品带回军械库。
岩壳巨兽|monsterexpansion:rakoth|击碎移动山岳|打穿重装岩壳，为据点扩建争得立足之地。
沙行雷虫|jerotesvillage:duneshockler|荒漠雷心|深入荒漠，夺取雷暴巨虫守住的猎场。
镇山大王|jerotesvillage:tyrant_of_the_mountain_realm|山岭归旗|推翻山岭暴君，将远征锋线推进矿脉腹地。
蛇龙执战者|jerotesvillage:serpon_combat_executer|撕开古族封锁|正面击溃执战者，越过古族封锁的边疆要道。
云筑魔像|legendary_monsters:cloud_golem|拆解旧世动力|攻破旧文明构造体，将魔像遗产列入军工回收目标。
无名守卫者|eeeabsmobs:nameless_guardian|重卫之后|击倒古迹重卫，夺取旧时代门户后的资源。
船长科妮莉亚|aquamirae:captain_cornelia|冰海军火库|征服亡灵舰长，将远洋遗产纳入你的版图。
赤色猎手·布莱德|nightfall_invade:scarlet_hunter|猎人与猎物|反杀追猎天外来客的旧世猎手，确立这片猎场的新主人。
下界骑士·赫尔瓦|block_factorys_bosses:underworld_knight|撕开焦土防线|击穿狱火重甲，开启夺火征途。
炼狱飞龙·阿什洛德|block_factorys_bosses:infernal_dragon|狱火龙心|斩落烈焰巨龙，向原初火种继续进军。
原初受火者|irons_spellbooks:fire_boss|夺取原初之火|击败控火半神，完成夺火三战的最后一击。
堕落圣骑|legendary_monsters:posessed_paladin|圣堂易主|清除失控圣骑，回收旧圣堂的武装遗产。
冥骸之主·卡玛斯|dungeons_and_combat:kamath|死亡王座|击败死灵君王，让亡骸军势的统御者败在你的刀下。
永昼之翼·苏蕾娅|dungeons_and_combat:sunleia|折断永昼之翼|跨越辉光女神的防线，将永昼王权写入征服名册。
Melkor·抹消时间者|souls_like_bosses:melkor|时之狭间|猎杀藏身时之狭间的旧日存在，夺取这场王权决斗的胜利。
咒翼灵骸|cataclysm:maledictus|吞噬旧世战魂|击溃汇聚众魂与诅咒的灵骸，为机械总攻扫清最后的旧世强敌。
MechX-12|woc_remastered:mechx_12|拆毁前锋机甲|摧毁机械阵列的前锋，向天基武器的控制核心推进。
湮灭猎影|legendary_monsters:annihilation_pursuer|猎影停机|终结废墟间的自律猎杀，夺取高阶火控研究所需的战绩。
湮灭构造体|legendary_monsters:the_obliterator|攻破天基武库|轰碎终极战争机器，为接管天基发射系统扫清守军。
泽尔塔|woc_remastered:zertar|王座只容一人|击败争夺最高统帅权的强者，确立总攻军团的旗帜。
暗夜领主|souls_like_bosses:nightlord|破开永夜|斩落永夜王座上的旧主，推进母巢方向的征伐。
最后守望者·亚尔特硫斯|nightfall_invade:arterius|跨越旧世剑圣|以刀剑越过最后守望者，让旧纪元见证新王的武艺。
界域戍卫|eeeabsmobs:realm_warden|打穿界域边界|击溃巨型戍卫，为母巢攻坚扫清最后一场常规讨伐。'''
for i,line in enumerate(rows.splitlines(),1):
    name,entity,title,goal=line.split('|'); key=f'V4_M{i:02}'
    phase=1 if i<=3 else 2 if i<=8 else 3 if i<=17 else 4
    ch=['departure','journey','front','counterattack'][phase-1]
    deps=[['A12','V4_PHASE1','V4_PHASE2','V4_PHASE3'][phase-1]]
    if i==11: deps=['V4_M10']
    if i==12: deps=['V4_M11']
    if i==17: deps=[f'V4_M{n:02}' for n in range(9,17)]
    if i==20: deps=['V4_M18','V4_M19']
    if 21<=i<=24: deps=['V4_M20']
    hint='可按本段连线选择出征顺序；备好补给与返程点，击杀仅认目标本体。战利品沿用模组原生掉落。'
    if i in (8,16,22):hint='本包未开放该模组自然生成；受控挑战入口尚待开放，请勿按原版攻略在野外无限寻找。'
    if i==23:hint='目标为最后守望者正式形态；高难试作形态与魂系支线的狼骑不计入本场战绩。'
    if i==17:hint='完成本段猎手、夺火与夺权战后，挑战咒翼灵骸。它是本段压轴，大圣残躯才是最终试炼。'
    result=f'{name}的讨伐战绩已归档。领取本项经验补给，原生掉落由战场拾取。'
    if i in (6,12,14,15,16,18,19,20):result+='军工、劫火、天基与金身能力另见对应目标的开放状态。'
    add(key,ch,f'M{i:02} · {title} · {name}',deps,[dict(kind='kill',target=entity,count=1)],goal,
        f'本任务开放后，击败{name}一次。',hint,result,boss_entity=entity,boss_slot=f'M{i:02}')
    q[key]['xp']=[30,50,75,100][phase-1]
    local=i-[1,4,9,18][phase-1]
    q[key]['position']=[(local%3)*3.5,(local//3)*3.5]
milestone('V4_PHASE1','departure','Ⅰ · 血肉筑基',[f'V4_M{i:02}' for i in range(1,4)],'svs_stage2_arena')
milestone('V4_PHASE2','journey','Ⅱ · 疆域割据',[f'V4_M{i:02}' for i in range(4,9)],'svs_stage3_calamity')
milestone('V4_PHASE3','front','Ⅲ · 劫火与神权',['V4_M17'],'svs_stage4_endgame')
for key,pos in [('V4_PHASE1',[3.5,4]),('V4_PHASE2',[3.5,7]),('V4_PHASE3',[3.5,11])]:q[key]['position']=pos

features=[
 ('V4_TOWER1','departure','军工 · 初代哨戒',['V4_PHASE1'],'部署并供给一座能实际攻击真菌的初级防御塔。','Silence’s Turrets已入包。炮塔部署与战斗目标尚未开放，先按配方筹备，不以持有炮塔当作防线建成。',[10.5,0]),
 ('V4_TOWER2','journey','军工 · 重火力要塞',['V4_PHASE2'],'完成重火力塔的供给、攻击与回收演练。','军工升级目标尚未开放；不要求安装其他塔防模组，不赠送尚不存在的动力核心。',[10.5,0]),
 ('V4_FIRE','front','军工 · 将劫火用于实战',['V4_M12'],'用已开放的劫火武装完成一次对真菌的有效攻击。','劫火能力尚未开放。夺火战绩不会自动使刀剑、法术与炮塔获得全局增伤。',[10.5,3.5]),
 ('V4_STRIKE','counterattack','军工 · 第一次天基打击',['V4_M20'],'取得发射装备与弹药，完成一次有效的天基打击。','天基武器尚未开放。摧毁构造体记录讨伐胜利，发射装备与实际打击仍需在此完成。',[10.5,3.5]),
 ('V4_M25','counterattack','M25 · 母巢总攻',[f'V4_M{i:02}' for i in range(21,25)]+['V4_STRIKE','V4_FIRE','V4_TOWER2'],'完成同一场有限母巢攻坚，赢下所有必要波次与最终核心战。','母巢战役尚未开放。野外消灭同类核心、守村围城结束或目标消失均不能替代本场胜利。',[3.5,11]),
 ('V4_M26','counterattack','M26 · 大圣残躯',['V4_M25'],'唤醒不灭残躯，堂堂正正赢下同一场两阶段试炼。','最终试炼尚未开放。大圣真魂早已远去，此战承接的是残躯留下的战意；第一阶段结束不算通关。',[3.5,14.5]),
 ('V4_CROWN','counterattack','终章 · 承接不灭金身',['V4_M26'],'领取齐天根器与不灭金身的正式传承奖励。','传承奖励尚未开放；现阶段不授予不死、复活、时间操纵或触手新能力。',[3.5,18]),
]
for key,ch,title,deps,work,hint,pos in features:
    add(key,ch,title,deps,[dict(kind='pending',target=key.lower(),count=1)],
        {'V4_M25':'将军团火力推进真菌腹地，粉碎这座母巢的吞噬核心。','V4_M26':'以平定一界的君王之姿，请教异界至强者留下的武道本能。','V4_CROWN':'承接不灭金身，完成天外成王之路。'}.get(key,'把征伐成果转化为可以实际使用的要塞力量。'),
        work,hint,'本项目开放并完成后，才能结算这里的战果。',position=pos)
q['V4_M25']['boss_slot']='M25';q['V4_M26'].update(boss_slot='M26',boss_entity='mod_cf2f7f04:great_sage')

# Exactly 24 optional encounters; multi-form fights stay one encounter.
side=[
 ('C15','沉降领主','jerotesvillage:sediment_lord',None),
 ('V4_S02','加斯科因·猎人与兽','bloodandmadness:father_gascoigne','gascoigne_full_encounter'),
 ('V4_S03','钢铁守护者','mowziesmobs:ferrous_wroughtnaut',None),
 ('V4_S04','霜冻巨兽','mowziesmobs:frostmaw',None),
 ('V4_S05','雕刻家·通臂大师','mowziesmobs:sculptor',None),
 ('V4_S06','太阳鸟·乌姆武提','mowziesmobs:umvuthi',None),
 ('V4_S07','荒古守卫者','legendary_monsters:ancient_guardian',None),
 ('V4_S08','海妖内拉基斯','block_factorys_bosses:kraken',None),
 ('HUNT_ignis','伊格尼斯','cataclysm:ignis',None),
 ('HUNT_scylla','斯库拉','cataclysm:scylla',None),
 ('HUNT_leviathan','利维坦','cataclysm:the_leviathan',None),
 ('HUNT_harbinger','先驱者','cataclysm:the_harbinger',None),
 ('HUNT_remnant','远古遗骸','cataclysm:ancient_remnant',None),
 ('HUNT_monstrosity','下界合金巨兽','cataclysm:netherite_monstrosity',None),
 ('HUNT_ender_guardian','末影守卫','cataclysm:ender_guardian',None),
 ('V4_S16','暗夜巫妖','bosses_of_mass_destruction:lich',None),
 ('V4_S17','下界铁掌','bosses_of_mass_destruction:gauntlet',None),
 ('V4_S18','黑曜巨石柱','bosses_of_mass_destruction:obsidilith',None),
 ('V4_S19','虚空之花','bosses_of_mass_destruction:void_blossom',None),
 ('SOUL_boss_gundyr','古达','slu:boss_gundyr',None),
 ('SOUL_boss_artorias','狼骑亚尔特留斯','slu:boss_artorias',None),
 ('SOUL_boss_gael','盖尔','slu:boss_gael',None),
 ('V4_S23','远古战士','slu:boss_ancient_warrior',None),
 ('V4_S24','猎龙铠甲','slu:boss_dragon_slayer_armour',None)]
for i,(key,name,entity,pending) in enumerate(side,1):
    ch='expedition' if i==1 else 'souls' if i>=20 else 'hunts'
    if key not in q:
        add(key,ch,'', ['A12' if i<9 else 'V4_PHASE2' if i<20 else 'V4_PHASE3'],
            [dict(kind='pending' if pending else 'kill',target=pending or entity,count=1)],'','','','',True)
        q[key]['xp']=30
    q[key].update(boss_slot=f'S{i:02}',boss_entity=entity,optional=True)
    hint='独立猎场，可自行安排挑战；沿原生线索准备起战材料和退路，战利品按原生掉落取得。'
    if i==2:hint='完整变身战尚未开放。从人形开战并确认最终胜利；单独召出的兽形不算完整战斗。'
    if i>=20:hint='魂系定点与随机券挑战入口尚待开放；本包禁用封印石与自然野刷，无需在野外寻找。'
    if i==5:hint='这是独立讨伐记录；雕刻家的原生登顶试炼属于另一玩法，不用登顶成功冒充击杀。'
    text(key,f'S{i:02} · {name}',f'向{name}发起独立挑战，为军械库收取另一条战线的战利品。',
        '完成从人形开始的完整加斯科因战斗。' if i==2 else ('取得沉降领主原生胜利进度。' if i==1 else f'完成{name}的讨伐目标。'),hint,
        '收取原生战利品与本项所列补给。这场独立挑战不影响主线阶段晋升。')
    if i!=1:q[key]['position']=[((i-2)%5)*3,((i-2)//5)*3.5] if i<20 else [(i-20)*3,0]

# Carryover route pages rewritten for the conquest setting and actual detection semantics.
edits={
'B01':('要塞与猎场','把据点作为征伐后方。','阅读防务、独立竞技场与清剿路线。','这些路线提供准备与挑战，不作为阶段Ⅰ的毕业门槛。'),
'B04':('防务轮值','掌握据点的围城节奏。','阅读共享计时、预警与离村规则。','在村走表，离村冻结；回村预警回拨。自然围城无须等待七天才能推进主线。'),
'B05':('地面竞技场','为武技寻找独立试炼场。','到访地面斗兽场。','到访只记录场地；起战、冷却和重试按竞技场原生提示。'),
'B06':('斗兽场首胜','赢下一次完整的单体挑战。','完成一次地面竞技场有效场次并获胜。','此胜利目标尚未开放；入场、启动祭坛与场外同种击杀均不算。'),
'B07':('天空竞技场','把群战训练纳入备战。','取得普通天空竞技场首次抵达进度。','本项记录到访，完整波次胜利另列；冰场可自行探索。'),
'B08':('天空终波','用完整波次检验续战能力。','完整赢下一次天空竞技场挑战。','此胜利目标尚未开放。任务所列钴锭为一次性补给，原生竞技场奖励另计。'),
'B09':('扫清真菌前哨','削弱据点周边的感染势力。','本项开放后，由队员有效击杀真菌怪物共15只。','不要求15种；环境死亡、非怪物与任务开放前的击杀不计。'),
'B10':('军械之外的本领','为当前兵刃补足战斗技能。','查看技能树与技能编辑器，确认可用技能。','技能树按实际节点条件解锁；技能书渠道另查军需手册。任务不额外赠送技能书。'),
'C02':('远征口粮','准备长途征伐的基础补给。','持有熟牛肉8个。','只检测持有，不扣除，不要求食用；其他料理可以自行搭配。'),
'C03':('侦察真菌高塔','将敌方地面据点标入星图。','到访一座真菌高塔。','按自然探索线索寻找；指南针受白名单与黑名单限制，不保证可定位。'),
'C04':('前哨接敌','清理首次侦察遇到的感染者。','本项开放后击败感染人类3只。','野外同种目标亦可，不把三次击杀当成高塔清场。'),
'C05':('地下据点','追踪地下感染战线。','到访真菌地下据点。','与地表入口侦察二选一即可汇合。'),
'C06':('地表缺口','从地表寻找感染据点的入口。','到访真菌入口结构。','与地下据点侦察二选一即可汇合。'),
'C07':('据点已标记','汇合地下战线的侦察情报。','完成地下据点或地表入口任一到访。','无需两处都跑；到访并不代表全歼守军。'),
'C09':('二轮远征钥匙','打开一条独立异界远征路线。','持有二轮世界钥匙。','配方查本包JEI，备好回程工具；沉降远征不影响主线晋升。'),
'C10':('踏入二轮','亲身抵达异界猎场。','取得进入二轮世界的原生进度。','持有钥匙与实际入境分别记录，出发前确认返程办法。'),
'C11':('异界立足','在二轮击败当地基础敌人。','取得二轮三圣原生进度。','按该进度要求击败僵尸、骷髅与蜘蛛；这不是三场首领战。'),
'C13':('追索墓穴','取得沉降墓穴定位线索。','持有沉降墓穴地图。','配方用二轮基础地图与腐肉；基础地图商人不保证在任一村庄出现。'),
'C14':('沉降墓穴','抵达异界领主的猎场。','到访沉降墓穴。','沿原生地图寻找，领主棺的激活与再战按原生交互。'),
'C16':('携战果返航','把异界远征战果带回主世界。','击败沉降领主后，本次远征者返回主世界。','本项开放后才检测返程；一直留在家的队友不能代交。'),
'D02':('占领军营情报点','将感染军营纳入反攻地图。','到访真菌军营。','先记回程点；到访不等于占领或消灭全部守军。'),
'D03':('斩落蛮兵','检验对重型真菌的应对。','本项开放后击败蛮兵1只。','自然遭遇与围城中的同种目标均可，无须等指定围城日。'),
'D04':('监狱侦察','查明感染监狱的位置。','到访真菌监狱。','与医院二选一即可继续调查实验室。'),
'D05':('医院侦察','查明感染医院的位置。','到访真菌医院。','与监狱二选一；不要求搜出虚构档案。'),
'D07':('深入实验室','抵达感染设施腹地。','到访真菌实验室。','先完成监狱或医院任一侦察；本项仅检测结构到访。'),
'D08':('拔除肉丘','处理一个可见的增殖威胁。','本项开放后击败肉丘1只。','自然遭遇即可；实验室不保证有肉丘，击杀也不会清除全球感染。'),
'D11':('古代工厂侦察','寻找先驱者的独立战场。','到访古代工厂。','先驱者属于独立猎场，不是机械主线的替代目标。'),
'D18':('燃烧竞技场侦察','寻找伊格尼斯的独立战场。','到访燃烧竞技场。','沿原生点火与再战机制准备；此支线不代替主线夺火三战。'),
'D21':('大教堂侦察','标出真菌大型设施。','到访真菌大教堂。','大教堂不是母巢事件入口的保证，抵达也不会启动总攻。'),
'C17':('整备据点守军','将后勤、守军和撤退路线连起来。','实际检查卫兵、火种与撤退路线后手动确认。','这是操作自报，不自动授予文明等级或刷新围城。'),
'C19':('补齐钴料','为进阶锻造预备材料。','持有钴锭2个。','不扣除材料；具体升级方案查JEI与锻造师路线。'),
'C20':('补齐战技','检查下次远征需要的战斗能力。','查看技能树、已装备技能与饰品。','按当前界面条件解锁技能；不要求刷出指定随机技能书才能继续。'),
'D06':('军团口粮','补充中段远征的基础食物。','持有熟牛肉8个。','只检测持有，不扣除；其他料理可自由准备。'),
'D15':('猎人战前准备','为完整变身战留出观察与补给空间。','检查武器、口粮与返程点后手动确认。','加斯科因完整挑战尚未开放；勿把米科拉什的召唤物当成它的入口。'),
'D17':('战后整备','将猎人战的损耗补回来。','检查装备耐久、食物、技能与回程点后手动确认。','任务不会修理装备或补满资源，按实际损耗补充。'),
'D20':('焰铸之材','把伊格尼斯战果转成装备选择。','持有焰魔锭1个。','不扣除材料；用途查JEI，无须再杀一次或收集随机唱片。'),
'E13':('终战整备','为大圣残躯试炼准备完整行装。','检查补给、装备、技能与再战路线后手动确认。','不自动补满资源；原有匠魂武器与其他合规打法仍可使用。'),
'E15':('请教不灭残躯','认清终章的挑战对象。','阅读大圣残躯与两阶段胜利的说明。','真魂已远去，此战回应残躯的武道本能；完整两阶段结束才算试炼成功。'),
'F02':('点燃军械炉','建立能够实际熔铸的生产链。','用燃料、熔化设备、排液口与浇铸台完成一次熔铸后确认。','这是实操自报。起步炉具在序章“第一座炉火”领取一次，此处不重复赠送。'),
'J01':('附着 · 天外血肉','确认初次融合的成果。','队内至少一人达到附着或更高阶段。','任务共享推进，个人融合档案分别保存。'),
'J04':('整合 · 血肉成甲','把共生体推向第二阶。','队内至少一人达到整合或更高阶段。','更高阶段亦认可，无须退化后重练。'),
'J05':('吞噬真菌','以狩猎状态取得当前共生红利。','在狩猎状态下亲手有效击杀一只真菌怪物。','必须由玩家造成有效致命伤害；炮塔或环境代杀不算亲手狩猎。'),
'J07':('合作 · 驾驭异星之力','让共生成长达到第三阶。','队内至少一人达到合作或更高阶段。','共享任务不复制个人成长与菌株，已达更高阶段者可直接认可。'),
'J10':('主导 · 成神战甲','掌握当前最高阶共生形态。','队内至少一人达到主导阶段。','不限定菌株，不要求所有队员一起进化；职业毕业不锁主线。'),
'H05':('第一位战争伙伴','以一次真实驯服开启龙骑路线。','完成八种驯服记录中的任意一项。','龙的所有权属于实际驯服者；共享任务不会复制宠物。'),
'H08':('孵化后备龙骑','尝试原生龙蛋孵化路线。','按对应龙种指南孵化自己的龙蛋一次并确认。','此项为可选实操自报，温度与环境按具体龙种要求准备。'),
'M02':('技能树与军需书店','掌握已有战技的取得途径。','先查看技能树，再查技能书交易与竞技场来源。','技能树按节点条件解锁。职业村民技能书与竞技场奖池以实际开放内容为准；本任务不发技能书。'),
'T02':('感染据点索引','为可选侦察安排路线。','查看真菌高塔、地下据点与地表入口线索。','它们位于侦察与备战页；到访不等于清场，不作为主线阶段门槛。'),
'T07':('灾变古国索引','区分主线压轴与独立猎场。','查看冰牢、卫城、古代工厂、燃烧竞技场等原生线索。','咒翼灵骸位于主线Ⅲ；其余七场灾变挑战为独立猎场，大圣残躯位于终章。'),
'T10':('母巢总攻索引','为有限攻坚事件预留军工准备。','阅读母巢与守村围城的区别。','母巢事件尚未开放；包含核心战的有限波次须完整获胜，守村成功与野外核心击杀不能替代。'),
}
for key,(title,goal,work,hint) in edits.items():text(key,title,goal,work,hint,q[key]['text'][3])
q['C19']['tasks']=[dict(kind='item',target='tconstruct:cobalt_ingot',count=2,consume=False)]
q['D20']['tasks']=[dict(kind='item',target='cataclysm:ignitium_ingot',count=1,consume=False)]
# Changed proof gets a new identity, rather than trusting a legacy reading checkmark.
for key in ('C19','D20'):
    new=key+'_V4';q[new]=q.pop(key);q[new]['key']=new
    for v in q.values():v['deps']=[new if dep==key else dep for dep in v['deps']]
q['L26']['text'][2]='咒翼灵骸为主线Ⅲ压轴；战后按本包配方筹备材料，收藏节点不要求再次讨伐。'
q['L31']['text'][2]='此处记录普通配方成品；大圣终章的传承奖励单独结算。'
q['H10']['text'][2]='先按龙种指南确认可骑乘；不要求固定坐标，此项为手动确认的实操记录。'
q['S04']['title']='征伐星图的开放范围'
q['S04']['text']=['以四阶段征伐统合这片世界，最终请教大圣残躯。','阅读主线、军工与独立猎场的开放状态。','主线讨伐已按新世界观排列；标记“尚未开放”的能力或战役暂不能完成。','测试反馈请附任务标题、实际操作与看到的结果。']
q['S02']['text']=['从天外来客走向终焉王座。','阅读血肉筑基、疆域割据、劫火与神权、天基总攻四阶段路线。','收藏家、锻造师、狩龙人、共生使并行成长；独立猎场与职业毕业均不作为主线前置。','把四艺的成果用于征伐，主线战绩由你亲手夺取。']
# Remove technical bookkeeping and obsolete future claims from visible copy.
for v in q.values():
    v['text']=[s.replace('教学自报','实操自报').replace('数量待批；','').replace('；数量待批','') for s in v['text']]
    if v['key'].startswith('H04'):
        v['text'][2]='八种任选一种即可继续，驯服方法按对应龙种指南；任务不赠龙，不改变所有权。'
    if v['key']=='J12':v['text'][1]='完成四阶成长、一次有效狩猎与压力管理练习。'
    # Item goals use real item artwork, never a generic sword or book override.
    items=[t['target'] for t in v['tasks'] if t['kind']=='item']
    if items:v['icon']=items[0]

titles={'departure':'Ⅰ · 血肉筑基','journey':'Ⅱ · 疆域割据','front':'Ⅲ · 劫火与神权',
        'counterattack':'Ⅳ · 天基总攻与齐天终章','collector':'收藏家 · 君王军械库',
        'smith':'锻造师 · 要塞军工','dragon':'狩龙人 · 战争龙骑','symbiote':'共生使 · 天外战甲',
        'expedition':'独立远征 · 异界与战备','hunts':'独立猎场 · 巨兽与古国','souls':'独立猎场 · 古战场回响',
        'commissions':'军需 · 悬赏与日课','manual':'军需手册 · 战技与装备','atlas':'征伐地标 · 入口与退路'}
for ch in d['chapters']:ch['title']=titles.get(ch['key'],ch['title'])
d['chapters'].insert(10,dict(key='recon',title='独立侦察 · 防务与竞技场',group='optional',icon='minecraft:compass'))
d['authority']='2026-10-17用户：测试交给用户，先按新世界观重写FTB任务；武器材料用实物图标，Boss正面像素图标'
d['story_version']=4
d['quests']=list(q.values())
# Authored coordinates for retained routes are regenerated to avoid collisions after relocation.
for ch in d['chapters']:
    vs=[v for v in d['quests'] if v['chapter']==ch['key']]
    if ch['key'] not in ('start','prologue','departure','journey','front','counterattack','hunts','souls'):
        for i,v in enumerate(vs):v['position']=[(i%6)*3.0,(i//6)*3.5]
SOURCE.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=[]
for key,v in old.items():
    newkey={'C19':'C19_V4','D20':'D20_V4'}.get(key,key)
    new=q.get(newkey)
    manifest.append(dict(old_key=key,new_key=newkey if new else None,
                         action='retired' if new is None else 'new_proof_new_id' if newkey!=key else 'retained',
                         old_chapter=v['chapter'],new_chapter=new['chapter'] if new else None))
(ROOT/'docs/FTB任务v4_迁移映射.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Migrated',len(old),'->',len(q),'quests; backups:',BACKUP)
