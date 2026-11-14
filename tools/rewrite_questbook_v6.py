"""Author the conquest campaign and a single ranked, rewarded arsenal.

Uses the v5 snapshot as input only. Reference packs and live saves are read-only.
T0 is the highest editorial combat band; it is not a measured DPS leaderboard.
"""
import collections,copy,hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'docs/questbook_v2.json').exists():
    current=json.loads((ROOT/'docs/questbook_v2.json').read_text(encoding='utf-8'))
    if current.get('content_revision'):
        raise SystemExit('Current source includes a later extension; do not overwrite it with the v5-to-v6 historical rewrite. Edit the current source or use the documented extension snapshot.')
B=ROOT/'backups/questbook_v6_20261017'
old=json.loads((B/'before/docs/questbook_v2.json').read_text(encoding='utf-8'))
oldq={q['key']:copy.deepcopy(q) for q in old['quests']}
F=json.loads((ROOT/'docs/data/quest_content_v5.json').read_text(encoding='utf-8'))
D=json.loads((ROOT/'docs/questbook_v5_boss_dossiers.json').read_text(encoding='utf-8'))
missing={x.removeprefix('item:') for x in json.loads((B/'runtime_missing_v5.json').read_text(encoding='utf-8')) if x.startswith('item:')}
cat={e['id']:e for e in F['catalog'] if e['id'] not in missing}
names=F['names']
d={'schema':4,'story_version':4,'editorial_version':6,'title':'天外成王 · 征伐星图',
   'authority':'用户本轮改定：充实成王主线、主支线回流、收藏与全鉴合并、T2/T1/T0分档奖励、逐步可见；取代旧分离/禁排名/禁技能书口径',
   'groups':[['main','王途 · 征伐与夺权'],['career','军团 · 四艺与军工'],['arsenal','君王武库 · 分级鉴定'],['optional','远征 · 独立猎场'],['reference','星图 · 备忘与循环']],
   'chapters':[],'quests':[],'reward_tables':{}}
Q={}
SOURCE='剧情v4《天外成王篇》；用户本轮改定；三包主线近读；当前实例资源与2026-10-17运行时失效项审计'

def sec(t,*lines):return {'title':t,'lines':list(lines)}
def link(k,t):return {'key':k,'label':t}
def it(id,n=1):return {'kind':'item','target':id,'count':n,'consume':False}
def bridge(target='milestone',**kw):return {'kind':'bridge','target':target,'count':kw.pop('count',1),**kw}
def chapter(k,t,g,emblem,icon='ftbquests:book'):
    d['chapters'].append(dict(key=k,title=t,group=g,icon=icon,icon_texture='svs:textures/quest/emblems/'+emblem+'.png'))
def add(k,ch,t,deps,tasks,goal,work,hint,result,icon=None,**kw):
    assert k not in Q,k
    q=dict(key=k,chapter=ch,title=t,deps=deps,tasks=tasks,text=[goal,work,hint,result],optional=kw.pop('optional',False),
           availability='pending' if any(t['kind']=='pending' for t in tasks) else 'wired',xp=kw.pop('xp',20),
           items=kw.pop('items',[]),source=SOURCE,writing_style='v6',**kw)
    if icon:q['icon']=icon
    elif not q.get('icon_texture'):q['icon_texture']='svs:textures/quest/emblems/'+('crown' if ch=='start' else 'command')+'.png'
    Q[k]=q;return q
def read(k,ch,t,deps,goal,hint,result,**kw):
    return add(k,ch,t,deps,[{'kind':'checkmark','target':'','count':1}],goal,'阅读本次行动命令，确认后展开下一步。',hint,result,**kw)
def coins(q,n):q['items'].append(['kubejs:spore_coin',n]);return q
def table(k,t,entries):d['reward_tables'][k]={'title':t,'entries':[{'item':x[0],'count':x[1]} for x in entries]}
def book(s):return {'id':'epicfight:skillbook','Count':1,'tag':{'skill':'epicfight:'+s}}

table('v6_mobility','身法军资 · 二选一',[(book('roll'),1),(book('step'),1)])
table('v6_guard','格挡军资 · 二选一',[(book('guard'),1),(book('impact_guard'),1)])
table('v6_veteran','精锐技法 · 三选一',[(book('parrying'),1),(book('stamina_pillager'),1),(book('endurance'),1)])
table('v6_master','王权技法 · 三选一',[(book('swordmaster'),1),(book('technician'),1),(book('hypervitality'),1)])
table('v6_fieldgear','远征行装 · 三选一',[('artifacts:running_shoes',1),('artifacts:umbrella',1),('artifacts:night_vision_goggles',1)])
table('v6_firegear','夺火整备 · 二选一',[('artifacts:obsidian_skull',1),('minecraft:golden_apple',4)])
table('v6_elitegear','精锐军需 · 三选一',[('artifacts:feral_claws',1),('artifacts:steadfast_spikes',1),('artifacts:panic_necklace',1)])
table('v6_t2gear','T2鉴定赏 · 武装任选一',[('simplyswords:iron_longsword',1),('simplyswords:iron_spear',1),('minecraft:iron_chestplate',1)])
table('v6_t1gear','T1鉴定赏 · 军械任选一',[('simplyswords:runic_katana',1),('simplyswords:runic_glaive',1),('minecraft:diamond_chestplate',1)])
table('v6_t0gear','T0鉴定赏 · 君王军资任选一',[('cataclysm:ignitium_ingot',2),('tconstruct:manyullyn_ingot',12),('minecraft:netherite_ingot',2)])
table('v6_crownweapon','武库毕业赏 · 王权兵器任选一',[('wom:ruine',1),('cataclysm:the_incinerator',1),('slu:moonlight_sword',1)])
for key,n in [('v6_mobility',4),('v6_guard',4),('v6_veteran',12),('v6_master',24)]:
    d['reward_tables'][key]['entries'].append({'item':'kubejs:spore_coin','count':n})
    d['reward_tables'][key]['title']=d['reward_tables'][key]['title'].split(' · ')[0]+' · 任选一'

for a in [('start','序章 · 天外来客','main','crown'),('departure','Ⅰ · 血肉筑基','main','claw'),
          ('journey','Ⅱ · 疆域与军工','main','fortress'),('fire','Ⅲ甲 · 掠夺焚世劫火','main','flame'),
          ('front','Ⅲ乙 · 诸王神权','main','throne'),('counterattack','Ⅳ · 天基总攻','main','orbital'),
          ('finale','终章 · 齐天遗蜕','main','crown'),('collector','收藏家 · 君王武库','career','arsenal'),
          ('smith','锻造师 · 军工总造','career','forge'),('military','要塞 · 火力与远征','career','turret'),
          ('dragon','狩龙人 · 制空龙骑','career','dragon'),('symbiote','共生使 · 噬神战甲','career','symbiote'),
          ('arsenal_t2','T2 · 基础军械鉴定','arsenal','t2'),('arsenal_t1','T1 · 精锐军械鉴定','arsenal','t1'),
          ('arsenal_t0','T0 · 王权军械鉴定','arsenal','t0'),('curios','遗珍 · 远征与战斗','arsenal','relic'),
          ('hunts','猎场 · 荒野与古国','optional','hunt'),('souls','猎场 · 旧王回响','optional','throne'),
          ('expedition','远征 · 另一轮天空','optional','compass'),('manual','星图 · 作战备忘','reference','command'),
          ('cycles','星图 · 竞技与军令','reference','hunt')]:chapter(*a)

# One visible entry, then one objective at a time. Read tasks are briefings only.
q=read('S00','start','天外四客',[''],'真菌要吞食这颗星球，共生体要吞食强者。你要的比它们更多：一座要塞、诸王的武库，以及此界的王座。',
       '你与共生体一同降临；另一位更早到来的异界强者只留下不灭残躯。那是征伐终点，不是开局救援者。',
       '先取兵刃，再融合天外生命。立旗之前，先让自己有资格活着走进村庄。',items=[['kubejs:refined_iron_ingot',3],['minecraft:cooked_beef',8]],xp=0)
q['deps']=[]
q=read('S01','start','定下征途',['S00'],'选定个人难度，开始这场征伐。','难度选项只影响自己的规则；同队任务共享与个人领奖分开处理。','难度奖励需手动选择；有疑问可在作战备忘查阅。',choice=True,xp=0)
sequence=['A01','A02','A03','A04','A05','A06','A10','A11','A07','B02','B03','A08','A09','V4A_FORGE','V4A_CAST','V4A_DEFENSE','A12']
prev='S01'
for key in sequence:
    v=copy.deepcopy(oldq[key]);v.update(chapter='start',deps=[prev],writing_style='v6',source=SOURCE)
    for f in ['position','links','reward_id_keys','icon_texture']:v.pop(f,None)
    if key not in ('A02','A06','A07','V4A_FORGE'):v['items']=[]
    if key=='A01':v['text']=['先把刀从生存工具变成能夺权的兵器。','阅读史诗战斗姿态与攻击说明后确认。','进入战斗模式；先试短连段和收招，不把按键存在误认为已经学习技能。','下一步取得第一把实用兵刃。']
    if key=='A02':v['text'][3]='铁剑与盾牌已拨付。完成下一段实战，可从翻滚或跨步中领取一本身法书。'
    if key=='A05':v['title']='身法与耐力';v['text']=['不依赖站桩换血，把耐力留给决定生死的那一次动作。','阅读身法书的学习与装备规则后确认。','技能书将在下一项实战后领取；学过的技能不需要反复吃书。','完成初试锋芒，领取身法军资。']
    if key=='A06':v['select_rewards']=['v6_mobility'];v['text'][3]='首批猎物倒下。领取一本身法书，再向另一颗流星进发。'
    if key=='A10':v['text'][3]='异星生命已与你融合。后续猎杀与喂食让它成长；任务不会凭空提升共生阶位。'
    if key=='A09':v['title']='军需官的第一张清单';v['text']=['把村庄变成能支撑远征的后方。','阅读补给与贸易安排后确认。','真菌残魂用于现有军需渠道；留出食物、修理和技能整备预算，装备奖励在后续征伐与鉴定中逐步拨付。','村民负责原生交易，你负责把可用物资带上前线。']
    if key=='V4A_CAST':v['text'][1]='完成浇铸练习后自行确认；本项为教学记录。';v['text'][3]='下一次猎杀所得可以投入炉中；实操熟练度由你掌握，任务不伪造自动验证。'
    if key=='A12':v['text']=['降临、融合、立旗已经完成。你不再是路过废土的流亡者，接下来让荒野承认新的领主。','序章前置完成后自动结算。','主线逐项展开；支线由相应战果引出。全武库无需集齐，职业毕业也不拦截征伐。','发布第一道猎令：锐爪兽。'];v['select_rewards']=['v6_guard'];coins(v,12)
    Q[key]=v;prev=key

# Campaign. Each theatre has a strategic transition, distinct boss dossier,
# useful provisioning, a verified field objective, and a route back to support.
briefings={
1:('departure','荒野要先学会畏惧你','村庄献出火种，但城墙还挡不住强敌。先猎取荒野霸主的血肉，再用骨材、铁与红石铺出第一道火力网。','共生使展开血肉成长，锻造师处理猎获，收藏家把战利品登记为可反复使用的战备资产。'),
2:('journey','矿道、古塔与海路','第一道防线能守住后方，你才有余力吞并更远的疆域。山王封着矿道，古族扼住道路，旧魔像和幽灵舰队守着下一轮军工遗产。','本章战果依次引出精锐武库、重型核心、守军整备与远征维修；不用把全部支线做完才能继续。'),
3:('fire','普通火药烧不完菌潮','感染已经爬进军营、医院和实验室。你要取走的不是又一把普通火剑，而是旧防线一直没能守住的原初火种。','先反杀追来的猎手，再连续突破狱火骑士、炼狱飞龙与原初受火者；劫火的战斗运用单列，不用阅读假装赋能所有炮塔。'),
4:('front','王权必须握在新王手里','火种能焚巢，诸王的法则却仍阻碍总攻。圣堂、死亡、永昼和时间各自闭锁一块疆土，把它们逐一撕开。','王魂属于本包叙事；实际回报是残魂、技能书、材料与装备。共生进化仍须喂食、狩猎和原生条件。'),
5:('counterattack','把准星移向天外','你的火力能压住地面，却还缺一次从天而降的裁决。机械三巨头分别扼住导航、火控与武库权限，先让钢铁军团熄火。','三段战果接到天基整备；在总攻前清除争王者和守界者。发射与母巢是独立事件，未开放的目标会明确标识。')}
for n,(ch,title,goal,hint) in briefings.items():
    deps=[{1:'A12',2:'V4_PHASE1',3:'V4_PHASE2',4:'V6_FIRE_END',5:'V4_PHASE3'}[n]]
    read('V6_BRIEF'+str(n),ch,title,deps,goal,hint,'下一项就是本战区的第一步行动。',xp=0)

# Field orders are actual actions, not a ring of unconnected read-and-confirm nodes.
add('V6_P1_SUPPLY','departure','远征要有归路',['V6_BRIEF1'],[it('minecraft:bread',8)],
    '在挑战荒野巨兽前，准备一份不依赖临时狩猎的粮食。','持有面包8个，不消耗。','原生种植、工作台制作或村民交易均可；已领的牛排留作应急。','补给线开始运转。先找到锐爪兽的栖地。','minecraft:bread',items=[['minecraft:torch',16]])

plans=[
('M01','departure','V6_P1_SUPPLY','爪与鳞，都是军资','锐爪兽控制着村外的狩猎区。要塞的第一条补给路，不能向一头掠食者交税。','拿它的利爪开刃，用甲壳与骨材扩展猎装；战后打开君王武库与共生使。'),
('M02','departure','V6_AFTER_M01','把移动山岳拆成城墙','第一场胜利让共生体尝到强者的血肉，但火种周围还没有可靠的外层防线。岩壳巨兽正好带着你需要的重装骨材。','战后拨付基础驱动核心、计数器与回收手套；进入要塞支线制作第一座箭塔。'),
('M03','departure','V6_AFTER_M02','截断荒漠雷暴','重装底盘已经到手，下一步让远征越过荒漠。雷虫盘踞的沙路将成为要塞的外延运输线。','雷电核心是战略叙事；实际军工沿原生核心升级台推进，不把青金石写成万能电池。'),
('M04','journey','V6_BORDER','山岭从此归旗','矿石要从山里运回炉边。镇山大王把山岭视为自己的王土，你要让这条矿道换一面旗。','山岭战果支持高炉与精锐军械鉴定，为旧纪元设备的拆解准备钢铁。'),
('M05','journey','V6_AFTER_M04','古族的封锁到此为止','夺下矿道还不够，蛇龙执战者控制着通往旧遗迹的边疆要道。绕路只会让补给线越拉越长。','正面打通封锁，将格挡与耐力技法带入后续重卫决斗。'),
('M06','journey','V6_AFTER_M05','从云端拆下一座动力炉','要塞仍在消耗初级核心，旧文明的魔像却把动力封在高处。拆开云筑魔像，让古老工艺为你服务。','拨付一枚3级核心：可投入防线，也可作为研究台配方的一部分；第二枚仍需原生取得。'),
('M07','journey','V6_AFTER_M06','让遗迹重卫为新王开门','动力只是要塞的骨架，守军也需要更可靠的武装。无名守卫者仍在替一个死去的时代把门。','胜利后给出守军装备与武库方向；任务不承诺村民自动换装或新兵种AI。'),
('M08','journey','V6_AFTER_M07','冰海军火库易主','你的旗帜已经越过山岭与古迹，海路却被幽灵舰队截住。船长科妮莉亚掌握着下一次远洋整备的钥匙。','夺取舰队遗物，补齐携行维修。当前冰海自然生成关闭，正式受控入口仍待开放，不为此偷偷改世界生成。'),
('M09','fire','V6_CAMP','猎人也能成为猎物','重火力要塞引来了旧时代的猎魔人。布莱德将你与共生体当成异端；你要用他的失败宣布新的狩猎秩序。','这场人形交锋检验身法与收招，奖励接续格挡、耐力与战斗饰品整备。'),
('M10','fire','V6_AFTER_M09','撕开焦土第一道防线','原初火种不在凡俗的熔炉里。通往它的焦土入口，由一位狱火重甲骑士把守。','准备自己的火焰防护。战后赏赐提供下一战补给，原生抗火机制仍以物品效果为准。'),
('M11','fire','V6_AFTER_M10','把狱火龙心装进军资箱','骑士之后，是失控的炼狱飞龙。它堵住了最后一段夺火道路，只有击落它，才能直面控火半神。','不必为主线杀死自己养成的圣龙：这里是独立首领，狩龙支线继续尊重驯养与狩猎两种路线。'),
('M12','fire','V6_AFTER_M11','原初之火不再属于旧神','你已经跨过重甲与龙焰。现在握住这场远征真正的目标，把旧纪元没能守住的火种从受火者掌中夺走。','劫火是后续母巢攻略的战略核心；实际炮塔附魔与菌毯净化没有被阅读任务代办。'),
('M13','front','V6_HOSPITAL','圣堂的盾牌换一位主人','夺火之后，圣堂遗产成为进军实验设施的阻碍。堕落圣骑仍握着旧秩序的盾，却已经守不住自己的领地。','战后展开顶阶武库的入口，以高阶甲胄与饰品强化自己的承伤方案。'),
('M14','front','V6_AFTER_M13','亡骸王座不该继续空耗军资','卡玛斯靠死亡维持王权。你要夺走他的统御遗产，让共生体的进化面对更高层次的能量。','王魂不会变成一个免费复活按钮；胜利赏赐兑现为技能、残魂与可投入制作的材料。'),
('M15','front','V6_AFTER_M14','折翼，便能打破永昼王权','永昼的辉光笼罩着苏蕾娅的疆域。新王不需要向一位旧神请求通行，把她的权柄从天空拉下来。','辉光是故事中的权柄；任务不会改变昼夜规则，真正的回报会列在奖励区。'),
('M16','front','V6_AFTER_M15','时间也不能庇护旧王','Melkor试图让战败的时代继续停留在时间夹缝里。你要让他的力量成为下一轮远征的战果。','名字与称号合计一场；其自然生成关闭，受控入口待开放。任务不把一次阅读算作时空能力解锁。'),
('M17','front','V6_AFTER_M16','把旧世战魂一并吞下','圣堂、死亡、永昼与时间已经次第失守。咒翼灵骸汇聚的旧日战魂，是共生体迈向主导前最后一场重考。','冰牢压轴后转入机械战区。先盘点武器、护甲、技能和携行维修，避免带着半套战备进入总攻。'),
('M18','counterattack','V6_LOGISTICS','夺取导航链','天基武库的第一道权限在前锋机甲手里。拆毁MechX-12，先让轨道兵器知道你要它瞄准哪里。','导航模块是战果职责，当前原生掉落是实际军工材料；不捏造已经注册的发射信标。'),
('M19','counterattack','V6_AFTER_M18','夺取索敌链','导航之后是高速火控。湮灭猎影仍在废墟之间清除接近武库的人，把它的索敌权也抢过来。','机动、收招与维修要一起准备；不要把快速机械战打成漫无目的的追逐。'),
('M20','counterattack','V6_AFTER_M19','让终极战争机器熄火','导航与火控已经归你，发射密钥却仍在终极构造体背后。拆开它，拿走旧纪元最后的武库。','正式接到天基打击整备；尚未实现的发射事件不会被“已获密钥”这句剧情自动完成。'),
('M21','counterattack','V6_AFTER_M20','争王者只留一个','武库失守的消息引来了同样觊觎最高权柄的泽尔塔。总攻之前，必须确立唯一的征伐统帅。','这是一场巅峰武艺决斗，战后军资回补主武器维修与下一轮王座战。'),
('M22','counterattack','V6_AFTER_M21','攻破永夜封锁','暗夜领主把通往核心疆域的道路封进永夜。你不必为他的旧秩序留一座边境堡垒。','该模组自然生成关闭，入口单独待开放；斩下旧王仍须有效胜利，不能领书代替战斗。'),
('M23','counterattack','V6_AFTER_M22','跨过旧纪元的最后剑圣','亚尔特硫斯仍守着时代的尽头。拿出一路掠夺并练熟的兵刃，让旧世最锋利的剑见证后来者。','这里是Nightfall正式普通版最后守望者，和支线SLU狼骑分别记账。'),
('M24','counterattack','V6_AFTER_M23','把前线推进母巢边界','最后一道界域封锁横在军团与母巢之间。砸碎戍卫，让火力阵地和后勤线路真正到达总攻出发线。','守界胜利之后进行战前盘点，再等待有限母巢事件；普通野外proto击杀不能替代战役。')]

after={
'M01':('第一份猎获，三条成长线','你把第一头霸主变成军资。收藏家接收兵器与护甲，锻造师加工素材，共生使继续吞噬和喂食。','三条支线现在各自展开第一步；可以先选一条，主线仍继续追猎岩壳巨兽。',['C_ROOT','F01','J01']),
'M02':('第一套火力网的账单','重装骨材已经夺回。要塞拨付基础核心、计数器与手套，把它们投入原生箭塔配方。','要塞支线从核心到升级、维修逐步展开。主线只核对这笔军工资产已到手，不假装验证炮塔已经开火。',['G01']),
'M03':('荒野归旗，扫清试探者','荒漠运输线已打通，真菌前哨开始试探你的防线。现在把新兵刃带去清理外围感染者。','清除之后结算阶段Ⅰ；巨龙生态与独立猎场作为高收益远征逐步加入星图。',['H01','V6_HUNT_ROOT']),
'M04':('矿道战果转入炉边','山岭矿道已不再替暴君输送财富。把下一批金属投入精锐兵装和军工工位。','收藏家T1赏格开放；锻造师沿钴、合金与高阶工位发展。',['C_T1','F05']),
'M05':('破封锁，补齐防守技法','古族封锁线已经被你撕开，下一战将面对旧文明的厚重构造体。','任选一本精锐技法，按自己的武器与技能槽搭配；不要求学习重复技能。',['V6_TRAIN_VETERAN']),
'M06':('动力炉归你，支出由你决定','旧世动力已经入库。新增一枚3级核心，你可以把它交给研究台配方，也可以先投资现有防线。','要塞研究与精锐军工扩展；一枚核心只能支出一次，不把两条分支都标成已经完成。',['G05','F08']),
'M07':('从领主行装到守军军备','重卫倒下后，遗迹通道和守军武装有了新的主人。','领取一套铁甲作为现有守军或备用行装，自行通过原生交互装备；任务不接管村民AI。',['C_ARMOR2']),
'M08':('远洋战果装入远征箱','舰队遗留武装已经从旧日船长手中易主。下一段战争不会只发生在村外。','维修站与便携物资支持远征；沿要塞支线完善回收与补给，再进入夺火战区。',['G04','V6_EXP_ROOT']),
'M09':('把猎人的技法编入新军','追杀者已经倒下，猎杀与被猎杀的身份由你重写。','先核对防护与技能，再连续突破三道夺火战位。',['J07','V6_TRAIN_VETERAN']),
'M10':('穿过狱火门槛','焦土第一道防线崩塌。你还要面对火龙与受火者，先领取防火方向的军需。','黑曜石头骨的实际触发与抗性以原生说明为准；它不等于所有火焰永久免疫。',['G06']),
'M11':('龙焰之后，直取原初','火龙已经被击落，原初受火者不再有第二道屏障。','补充战斗口粮与高温材料，下一项直面火种掌控者。',['F09','H01']),
'M12':('火种入库，进入夺权战','原初火种已成为你的战略战果。把它与现有军工防线结合，是另一项需要实战验证的作业。','劫火军工目标保留真实未开放状态；本章征伐先结算，不拿虚假阅读按钮代办净化。',['V4_FIRE','C_T1']),
'M13':('不破之盾也会易主','圣堂旧卫的失败证明，王权武装并非不可夺取。','T0武库开放；从顶阶护甲、神兵与饰品中选自己的方向，不要求把整本全鉴清空。',['C_T0']),
'M14':('王魂化作下一场的底气','死灵君王已经无法继续消耗这片疆域。你要把收益投入下一场，而不是留下一枚无用的收藏勋章。','领取王权技法或推进共生主导；技能学习与共生阶位仍由原生机制决定。',['J10']),
'M15':('永昼权柄落入武库','辉光已经被你从高处折下。接下来的敌人不能再靠一段无法触及的历史保住王座。','高阶材料用于原生制作，残魂用于现有军需；本次没有改变世界时间。',['C_T0']),
'M16':('夹缝中的旧王也已倒下','时间没能保住Melkor。现在只剩冰牢中的旧世战魂仍足以阻挡机械战区的开启。','检查装备、饰品与身法，准备阶段压轴。',['V6_SOUL_ROOT']),
'M17':('旧世已服，轮到钢铁','咒翼灵骸化为战果，旧世武道不再挡在你的军团前。','领取精锐饰品与总攻军资，进入机械导航、索敌和发射权限三段攻势。',['C_FINAL','G07']),
'M18':('导航战果归档','前锋机甲已经报废，导航职责记录在星图。','真正发射还需完整武器链与事件接入；下一步猎取火控。',['G07']),
'M19':('索敌战果归档','高速猎影停止运转。你已具备进攻终极构造体的战果条件。','补充维修材料，继续向武库权限推进。',['G07']),
'M20':('武库权限转交新王','终极战争机器熄火，天基发射的战略条件已经齐备。','天基实战任务仍锁定，等待真实发射接口。总攻之前先扫清争王者与最后守界者。',['V4_STRIKE','G07']),
'M21':('唯一的征伐统帅','另一位争王者已经倒下，前线不再容纳第二道命令。','军团继续向永夜封锁区推进，奖励支持下一场王座战。',['C_T0']),
'M22':('永夜堡垒失守','暗夜领主无法继续封锁疆域。你和母巢之间，只剩剑圣与界域戍卫。','准备一套练熟的主武器、可靠护甲与技能组合，再跨过最后两战。',['V6_TRAIN_MASTER']),
'M23':('旧剑已折，新王向前','你已经正面跨过旧纪元最强剑士。接下来要砸碎的是疆域本身的最后一道边界。','用军资补齐出发线，不把支线全收集设成守界挑战的门槛。',['C_FINAL']),
'M24':('总攻出发线','界域封锁被打穿，军团已经到达母巢边界。','下面分开列出火力盘点、劫火实战、天基实战和有限母巢事件；只有真实战役成功才能通向齐天终章。',['G07','V4_FIRE','V4_STRIKE'])}
support={
'M01':[['kubejs:spore_coin',12],['minecraft:iron_ingot',4]],
'M02':[['silence_s_defense_tower:driving_core_1',1],['silence_s_defense_tower:counter_1',1],['silence_s_defense_tower:gloves',1]],
'M03':[['kubejs:spore_coin',18],['minecraft:redstone',16]],
'M04':[['minecraft:blast_furnace',1],['kubejs:spore_coin',20]],
'M05':[['kubejs:spore_coin',22]],
'M06':[['silence_s_defense_tower:driving_core_3',1],['kubejs:spore_coin',24]],
'M07':[['minecraft:iron_helmet',1],['minecraft:iron_chestplate',1],['minecraft:iron_leggings',1],['minecraft:iron_boots',1]],
'M08':[['silence_s_defense_tower:maintenance_station0',1],['kubejs:spore_coin',28]],
'M09':[['kubejs:spore_coin',30]],'M10':[['minecraft:golden_carrot',12]],
'M11':[['tconstruct:manyullyn_ingot',4],['kubejs:spore_coin',32]],
'M12':[['kubejs:spore_coin',40],['tconstruct:hepatizon_ingot',4]],
'M13':[['kubejs:spore_coin',36]],'M14':[['kubejs:spore_coin',40]],
'M15':[['tconstruct:rose_gold_ingot',8],['kubejs:spore_coin',40]],
'M16':[['kubejs:spore_coin',44],['minecraft:ender_pearl',8]],
'M17':[['kubejs:spore_coin',64],['minecraft:netherite_scrap',4]],
'M18':[['minecraft:redstone_block',8],['kubejs:spore_coin',48]],
'M19':[['minecraft:quartz',32],['kubejs:spore_coin',48]],
'M20':[['kubejs:spore_coin',80],['minecraft:netherite_ingot',1]],
'M21':[['kubejs:spore_coin',56],['minecraft:golden_carrot',16]],
'M22':[['kubejs:spore_coin',60]],'M23':[['kubejs:spore_coin',72]],
'M24':[['kubejs:spore_coin',96],['minecraft:golden_apple',4]]}
for slot,ch,dep,title,goal,benefit in plans:
    n=int(slot[1:]);brief='V6_ORDER_'+slot
    z=read(brief,ch,title,[dep],goal,benefit,'情报已展开。按下一项目标找到并战胜'+oldq['V4_'+slot]['title'].split(' · ')[-1]+'。',xp=0)
    z['icon_texture']='svs:textures/quest/emblems/'+('claw' if n<=3 else 'fortress' if n<=8 else 'flame' if n<=12 else 'throne' if n<=17 else 'orbital')+'.png'
    v=copy.deepcopy(oldq['V4_'+slot]);v.update(chapter=ch,deps=[brief],writing_style='v6',source=SOURCE,items=[],xp=60+n*8)
    v.pop('position',None);v.pop('reward_id_keys',None)
    v['text']=[goal+' '+D[slot]['lore'],'击败'+v['title'].split(' · ')[-1]+'的正式本体1次。',D[slot]['tactics'],benefit]
    v['sections']=[sec('目标与入口',D[slot]['location']+'。',
        '使用正式本体与原生起战方式；展示实体、部位实体不计为本项胜利。',
        '当前自然生成关闭，受控入口未开放；此任务保留实际击杀检测，不虚构可达入口。' if slot in ['M08','M16','M22'] else '到访场地不等于胜利；准备返程与补给后再起战。'),
        sec('作战情报',D[slot]['tactics']),sec('战果转用',benefit,'战后下一项自动结算的军需与原生战场掉落分开领取。')]
    if slot=='M03':v.pop('icon',None);v['icon_texture']='svs:textures/quest/emblems/lightning.png'
    Q[v['key']]=v
    title,g,h,links=after[slot]
    a=add('V6_AFTER_'+slot,ch,title,[v['key']],[bridge()],g,'上一场正式胜利完成后自动结算本次战果。',h,
          '军资已拨付；下一项继续征伐，相关支线可自行选择。',items=support[slot],xp=40,
          links=[link(k, Q.get(k,oldq.get(k,{})).get('title',k)) for k in links])
    a['icon_texture']=z['icon_texture']
    if slot in ['M05','M09']:a['select_rewards']=['v6_veteran']
    if slot=='M10':a['select_rewards']=['v6_firegear']
    if slot in ['M14','M22']:a['select_rewards']=['v6_master']
    if slot in ['M08','M17']:a['select_rewards']=['v6_fieldgear' if slot=='M08' else 'v6_elitegear']
    # Useful fieldwork occupies the next step; no mass of simultaneous boss nodes.

add('V6_SWEEP','departure','把新刀带向菌潮',['V6_AFTER_M03'],[bridge('spore_kills',count=12)],
    '三头霸主已成为战果，真菌却仍在据点外围伸展。以新武装清除十二个真菌系目标，检验自己的短连段与撤离节奏。','任务开放后，由玩家有效击杀真菌系敌人12只。','炮塔或环境代杀不冒充个人狩猎。要塞支线可以同时准备核心、箭塔与维修工具。','试探者已经被扫清，荒野归旗。','kubejs:spore_coin',items=[['kubejs:spore_coin',16]])
add('V4_PHASE1','departure','血肉筑基 · 荒野归旗',['V6_SWEEP'],[bridge()],
    '霸主的基因、重装骨材与荒漠通路都已归你，接下来夺取真正能扩大领地的军工遗产。','阶段Ⅰ主线完成后自动结算。','收藏家、锻造师、狩龙人与共生使继续独立成长；不要求全职业毕业。','阶段Ⅱ开放：矿道、古塔与冰海。',stage='svs_stage2_arena',items=[['kubejs:spore_coin',24]])
add('V6_BORDER','journey','让矿道接上要塞',['V6_BRIEF2'],[it('minecraft:iron_ingot',16)],
    '下一片疆土首先要能变成军工产能。为扩张准备一批铁料，而不是只在地图上插旗。','持有铁锭16个，不消耗。','原生采矿、冶炼、贸易均可。铁料随后可用于箭塔底盘、升级台或护甲。','军工储备就绪，先夺山岭矿道。','minecraft:iron_ingot',items=[['minecraft:coal',16]])
add('V4_PHASE2','journey','疆域割据 · 旧世军工归库',['V6_AFTER_M08'],[bridge()],
    '山岭、边境、古塔、遗迹与冰海已接成一条远征线。要塞有了扩张的底盘，你要开始向诸王索取火种。','阶段Ⅱ战果结算后自动完成。','维修与核心研发沿要塞支线扩展；主线不要求穷尽军工科技。','夺火战区开放。',stage='svs_stage3_calamity',items=[['kubejs:spore_coin',40]])
add('V6_CAMP','fire','感染已爬进旧军营',['V6_BRIEF3'],[{'kind':'structure','target':'spore:military_camp','count':1}],
    '侦察感染军营，找出普通守备火力已经失守的证据。这将成为你夺取原初之火的出发点。','抵达真菌军营结构范围。','到访只记录侦察，不表示清场；真菌设施支线继续扩展到监狱、医院与实验室。','旧防线的火力不足，你将去拿足以焚巢的火种。','kubejs:spore_coin',links=[link('RECON_ROOT','感染设施远征')],items=[['kubejs:spore_coin',12]])
add('V6_FIRE_END','fire','劫火入库 · 王权仍待征服',['V6_AFTER_M12'],[bridge()],
    '原初火种已经夺得，但诸王还各自锁住疆域。你要把圣堂、死亡、永昼与时间一并纳入新王的战果。','夺火战三位首领完成并结算后自动完成。','劫火实战另见要塞支线；本项只结算征伐战果。','进入诸王神权战区。',items=[['kubejs:spore_coin',32]])
add('V6_HOSPITAL','front','圣堂之前，先看失守的庇护所',['V6_BRIEF4'],[{'kind':'structure','target':'spore:hospital','count':1}],
    '真菌已占据旧时代的救治设施。圣堂还在宣称秩序，却没能守住它要保护的人。你要直接夺取能够继续作战的武装。','抵达真菌医院结构范围。','不用把一次到访写成解救全部幸存者；设施搜刮与感染清剿在远征支线展开。','下一道命令：击溃堕落圣骑。','kubejs:spore_coin',items=[['minecraft:golden_carrot',8]])
add('V4_PHASE3','front','诸王已服 · 开启机械总攻',['V6_AFTER_M17'],[bridge()],
    '原初火种与旧世诸王的遗产都已归库。真正的灭巢战还缺一次从天空降下的毁灭。','阶段Ⅲ压轴胜利及战果结算后自动完成。','共生主导、顶阶鉴定和技能整备是可选增援；不会用全鉴毕业卡住机械战区。','机械三巨头的导航、火控与武库权限，依次成为新的征伐目标。',stage='svs_stage4_endgame',items=[['kubejs:spore_coin',64]])
add('V6_LOGISTICS','counterattack','给总攻留一份维修物资',['V6_BRIEF5'],[it('silence_s_defense_tower:maintenance_station0'),it('minecraft:iron_ingot',16)],
    '把火力阵地推向母巢前，先准备能带走的维修资产与金属。没有后勤的炮群只能打出第一轮。','持有维修站便携物品1个及铁锭16个；分项记录，不消耗。','科妮莉亚战后已拨付一座维修站；用手套收回与重新部署的实操沿要塞支线进行。','总攻后勤就绪，先拆导航机甲。','silence_s_defense_tower:maintenance_station0',links=[link('G04','维修与携行支线')],items=[['kubejs:spore_coin',20]])
add('V6_MUSTER','counterattack','总攻盘点 · 粮、铁与火力',['V6_AFTER_M24'],[it('minecraft:golden_carrot',16),it('silence_s_defense_tower:driving_core_3')],
    '在母巢边界汇集最后一批战备，准备同时投入个人武装与军工火力。','持有金胡萝卜16个、驱动核心3级1个；不消耗。','这是持有盘点，不表示炮塔已经部署、已经击杀或已经完成天基发射。研究台若用掉之前的核心，需另行原生取得一枚。','军资已集结，等待真实劫火、天基与有限战役全部就绪。','silence_s_defense_tower:driving_core_3',items=[['kubejs:spore_coin',64]])
for key in ['V4_FIRE','V4_STRIKE','V4_M25','V4_M26','V4_CROWN']:
    v=copy.deepcopy(oldq[key]);v.update(chapter='military' if key in ['V4_FIRE','V4_STRIKE'] else 'finale',source=SOURCE,writing_style='v6');v.pop('position',None);v.pop('links',None)
    if key=='V4_FIRE':v['deps']=['V6_AFTER_M12'];v['icon_texture']='svs:textures/quest/emblems/flame.png'
    elif key=='V4_STRIKE':v['deps']=['V6_AFTER_M20'];v['icon_texture']='svs:textures/quest/emblems/orbital.png'
    elif key=='V4_M25':v['deps']=['V6_MUSTER','V4_FIRE','V4_STRIKE'];v['icon_texture']='svs:textures/quest/emblems/fortress.png';v['items']=[['kubejs:spore_coin',160]];v['select_rewards']=['v6_master']
    elif key=='V4_M26':v['deps']=['V6_SAGE_ORDER'];v['items']=[['kubejs:spore_coin',240]]
    else:v['icon_texture']='svs:textures/quest/emblems/crown.png';v['items']=[['kubejs:spore_coin',320]]
    Q[key]=v
read('V6_SAGE_ORDER','finale','此界已平，向异界传奇请战',['V4_M25'],
     '母巢焦土之后，本土已没有值得你继续争夺的王座。你走向那具真魂早已远去的不灭残躯，以君王之姿请求赐教。',
     '大圣的神魂不知所踪。你将面对残躯的武道本能，赢下正式两阶段连战，承接金身本源；一阶段倒地不算最终胜利。',
     '下一项是双阶段终极试炼。当前正式事件未开放，不允许手动勾过。',xp=0,icon_texture='svs:textures/quest/emblems/crown.png')

# Crafting / evolution: preserve real task semantics, remove duplicate tutorial pages.
for ch,prefix,rootgate in [('smith','F','V6_AFTER_M01'),('symbiote','J','V6_AFTER_M01'),('dragon','H','V6_AFTER_M03')]:
    subset=[v for v in oldq.values() if v['chapter']==ch]
    for v in subset:
        if ch=='dragon' and v['key']=='H01':pass
        v['source']=SOURCE;v['writing_style']='v6';v['optional']=True
        for f in ['position','links','reward_id_keys']:v.pop(f,None)
        v['deps']=[rootgate if dep=='A12' else dep for dep in v['deps']]
        if not v['deps']:v['deps']=[rootgate]
        # Low-impact instructional choices stay clearly manual.
        if all(t['kind']=='checkmark' for t in v['tasks']):
            v['text'][1]='阅读本项原生操作说明，完成练习后自行确认；不作为自动实操证明。'
        Q[v['key']]=v
    # Small progression rewards buy the next useful action.
for key,n in [('F04',12),('F06',20),('F08',24),('F10',36),('F12',40),('J04',20),('J05',24),('J07',36),('J10',64),('H05',30)]:
    if key in Q:coins(Q[key],n)
if 'F14' in Q:Q['F14']['select_rewards']=['v6_firegear'];coins(Q['F14'],64)
if 'J12' in Q:Q['J12']['select_rewards']=['v6_master'];coins(Q['J12'],96)
if 'H14' in Q:Q['H14']['select_rewards']=['v6_fieldgear'];coins(Q['H14'],64)
for v in Q.values():
    if v['chapter'] in ['smith','symbiote','dragon'] and not any(t['kind'] in ['item','kill','advancement'] for t in v['tasks']):
        v.pop('icon',None);v['icon_texture']='svs:textures/quest/emblems/'+{'smith':'forge','symbiote':'symbiote','dragon':'dragon'}[v['chapter']]+'.png'
# Species dossiers unfold one at a time. Opening the next dossier never requires
# taming every species; the actual tame milestone still accepts any one species.
prev='H03'
for index,v in enumerate(v for v in oldq.values() if v['key'].startswith('V5_DRAGON_')):
    v.update(chapter='dragon',deps=[prev],source=SOURCE,writing_style='v6',items=[],xp=0,optional=True)
    v.pop('position',None);Q[v['key']]=v
    native='H04'+chr(ord('a')+index)
    if native in Q:Q[native]['deps']=[v['key'],'V4_PHASE1']
    prev=v['key']

# Real military progression; deployment success remains unclaimed.
grows=[
('G01','第一枚驱动核心',['V6_AFTER_M02'],'silence_s_defense_tower:driving_core_1','M02战果提供核心、计数器与手套。先认清核心是原生炮塔配方材料，不是一项自动开启的城防技能。','持有驱动核心1级。',[['minecraft:crossbow',1],['minecraft:barrel',1],['minecraft:stone_slab',2]]),
('G02','第一座便携箭塔',['G01'],'silence_s_defense_tower:arrow_turret_leavl1_p','把核心和上一步配给的材料投入原生箭塔配方，再带到据点外试用。放置、归属、索敌与回收请分别观察。','持有箭塔1级便携物品。',[['kubejs:spore_coin',12],['minecraft:arrow',32]]),
('G03','核心升级工位',['G02'],'silence_s_defense_tower:core_upgrade_table','要塞成长从工位开始。升级成本与计数条件使用当前JEI及配置，不把展示配方当作实际扣料日志。','持有核心升级台。',[['minecraft:iron_ingot',8],['minecraft:redstone',8]]),
('G04','维修与携行',['G03'],'silence_s_defense_tower:maintenance_station0','维修站与回收手套支持远征火力网。先练收回与再次部署，记录归属和已有数据是否保留。','持有维修站便携物品。',[['kubejs:spore_coin',20],['minecraft:iron_ingot',8]]),
('G05','研究台的两笔核心预算',['G04','V6_AFTER_M06'],'silence_s_defense_tower:research_table','研究台配方要消耗一枚3级核心。如果你先用它升级炮塔，就要重新取得研究用核心；同一枚不能同时交两次账。','持有研究台。',[['kubejs:spore_coin',36]]),
('G06','把研发变成可用资产',['G05'],'silence_s_defense_tower:driving_core_3','研究后的火力成长仍走原生系统。本项核对备用核心，真实研发与部署效果由游戏实操确认。','再取得驱动核心3级1枚，作为防线或研究的下一笔独立投入。',[['minecraft:golden_carrot',12],['kubejs:spore_coin',32]]),
('G07','为远征留一套回收工具',['G04','V6_AFTER_M17'],'silence_s_defense_tower:gloves','母巢战区需要可携行的火力资产。带好手套与维修物资，避免把全部炮塔留在后方。','持有回收手套。',[['kubejs:spore_coin',40]])]
for k,t,deps,id,g,w,items in grows:
    v=add(k,'military',t,deps,[it(id)],g,w+' 不消耗。','持有检测只证明物资到手；不伪造有效炮塔击杀、维修次数或研究完成。','下一笔军需用于后续工位与远征。',id,optional=True,items=items)
    if k=='G05':v['select_rewards']=['v6_fieldgear']

# Training rewards are attached to real combat records, never free checkmark farms.
add('V6_TRAIN_VETERAN','military','精锐操练 · 为下一场多留一口耐力',['V6_AFTER_M05'],[bridge('hostile_kills',count=16)],
    '新技法要用在实际战斗里。选一把愿意练的兵刃，在远征途中完成十六次有效击杀。','目标开放后由玩家有效击杀敌对目标16只。','不宣称脚本检测了格挡成功或特定连段；只记录实际击杀。','精锐技法补充一次，可按已有学习情况换另一条方向。','epicfight:skillbook',optional=True,select_rewards=['v6_veteran'],items=[['kubejs:spore_coin',20]])
add('V6_TRAIN_MASTER','military','终战操练 · 把军资变成胜算',['V6_AFTER_M17'],[bridge('spore_kills',count=30)],
    '总攻前再练一次穿过菌潮的节奏。用自己的主武器清除三十只真菌系敌人，为王座决战校准手感。','目标开放后由玩家有效击杀真菌系敌人30只。','此操练不替代有限母巢事件，也不把炮塔代杀算进个人技法记录。','可选一本王权技法，回到后续主线继续征伐。','epicfight:skillbook',optional=True,select_rewards=['v6_master'],items=[['kubejs:spore_coin',48]])

# Optional hunts are introduced by the campaign, then open one encounter at a time.
read('V6_HUNT_ROOT','hunts','把额外战利品带回主战场',['V6_AFTER_M03'],
     '荒野之外还有不守主线道路的强者。它们提供独立武装与额外军资，适合在下一段远征之前补强。',
     '每个猎场沿上一场胜利继续展开；不要求猎场全通才能推进主线。','首个独立猎场开放。',optional=True,xp=0,links=[link('C_ROOT','所有战利品统一进入君王武库')])
side=[v for v in oldq.values() if v.get('boss_slot','').startswith('S') and v['boss_slot'] not in ['S01','S20','S21','S22','S23','S24']]
side.sort(key=lambda v:int(v['boss_slot'][1:]))
prev='V6_HUNT_ROOT'
for v in side:
    slot=v['boss_slot'];v.update(chapter='hunts',deps=[prev],writing_style='v6',source=SOURCE,items=[['kubejs:spore_coin',16+int(slot[1:])*2]],xp=80,optional=True)
    for f in ['position','reward_id_keys']:v.pop(f,None)
    v['links']=[link('C_ROOT','把战利品计入分级鉴定'),link('V6_TRAIN_VETERAN','继续精锐操练')]
    if slot in ['S04','S08','S12','S16']:v['select_rewards']=['v6_fieldgear' if slot in ['S04','S08'] else 'v6_elitegear']
    Q[v['key']]=v
    # The unavailable Gascoigne full encounter must not block other independent hunts.
    if v['availability']!='pending':prev=v['key']
read('V6_SOUL_ROOT','souls','旧王回响，名器与技法',['V6_AFTER_M16'],'旧纪元英雄不在野外游荡。它们的回响属于独立召唤挑战，将王魂与武装带回主战场。',
     '封印石自然投放关闭，召唤入口未开放。这里不赠召唤物、不恢复野刷。','后续挑战保留真实胜利条件；入口开放后逐场进行。',optional=True,xp=0)
prev='V6_SOUL_ROOT'
for slot in ['S20','S21','S22','S23','S24']:
    v=next(copy.deepcopy(v) for v in oldq.values() if v.get('boss_slot')==slot)
    v.update(chapter='souls',deps=[prev],source=SOURCE,writing_style='v6',optional=True,items=[['kubejs:spore_coin',48]],select_rewards=['v6_veteran'])
    for f in ['position','reward_id_keys']:v.pop(f,None)
    v['links']=[link('C_T0','回到王权军械鉴定')];Q[v['key']]=v;prev=v['key']

read('V6_EXP_ROOT','expedition','海路之后还有另一轮天空',['V6_AFTER_M08'],
     '把一支远征队的补给装进背包。另一轮天空中的墓穴与金属，可以作为主战区之外的高收益战果。',
     '沉降领主属于支线，不会卡住诸王与机械主线。','先准备背包，再取得异界钥匙。',optional=True,xp=0)
prev='V6_EXP_ROOT'
for key in ['C08','C09','C10','C11','C13','C14','C15','C16']:
    v=copy.deepcopy(oldq[key]);v.update(chapter='expedition',deps=[prev],source=SOURCE,writing_style='v6',optional=True)
    for f in ['position','reward_id_keys','links']:v.pop(f,None)
    if key=='C15':v['items']=[['kubejs:spore_coin',64]];v['select_rewards']=['v6_elitegear']
    if key=='C16':v['items']=[['kubejs:spore_coin',24]];v['links']=[link('V6_BRIEF3','把战果带回夺火主线'),link('C_ROOT','鉴定远征所得')]
    Q[key]=v;prev=key
read('RECON_ROOT','expedition','失守设施，仍有军资可取',['V6_CAMP'],'军营只是真菌占据旧设施的开端。沿监狱、医院、实验室和大教堂继续掠夺物资。',
     '结构侦察只算抵达，清剿任务独立记录；不把一张地图当作已经夺回整座设施。','设施远征按路段展开，收益供给主战场。',optional=True,xp=0)
prev='RECON_ROOT'
for key in ['D03','D04','D05','D07','D08','D21']:
    v=copy.deepcopy(oldq[key]);v.update(chapter='expedition',deps=[prev],source=SOURCE,writing_style='v6',optional=True,items=[['kubejs:spore_coin',12]],xp=40)
    for f in ['position','links','reward_id_keys']:v.pop(f,None)
    Q[key]=v;prev=key
Q['D21']['links']=[link('V6_BRIEF5','返回天基总攻'),link('C_ROOT','补强军械与饰品')]

# Support returns are concrete optional supply settlements within the campaign.
# They never become mandatory campaign prerequisites.
for key,ch,title,deps,goal,items,pool,nextkey in [
 ('AID_FORGE','journey','军工增援 · 新合金投入扩张',['F06','V4_PHASE1'],'工坊已能处理进阶合金。把这笔配套材料用于边疆远征与核心升级。',[['minecraft:iron_ingot',16],['minecraft:redstone',16]],None,'V6_BORDER'),
 ('AID_ARMORY','fire','武库增援 · 精锐兵装支援夺火',['C_T1_weapon_3','C_T1_armor_1','V4_PHASE2'],'兵器与护甲的鉴定已经形成精锐储备。军需官为夺火远征增拨一份防护方案。',[['kubejs:spore_coin',32]],'v6_firegear','V6_BRIEF3'),
 ('AID_DRAGON','front','龙骑增援 · 远征补给入库',['H05','V6_FIRE_END'],'制空伙伴已经通过真实驯服进入你的军团。额外补给支持诸王远征，不要求牺牲自己的龙。',[['minecraft:golden_carrot',16],['kubejs:spore_coin',32]],'v6_fieldgear','V6_BRIEF4'),
 ('AID_SYMBIOTE','counterattack','共生增援 · 主导战甲支援总攻',['J10','V4_PHASE3'],'你已在原生进化中驾驭共生体。把补给和技法投入机械总攻，继续练熟自己的主武器。',[['kubejs:spore_coin',64]],'v6_master','V6_BRIEF5'),
 ('AID_TURRET','counterattack','要塞增援 · 研究后勤推向前线',['G06','V6_AFTER_M20'],'研究与备用核心已形成独立军工资产，为母巢出发线补上一批维修金属。',[['minecraft:iron_ingot',32],['kubejs:spore_coin',48]],None,'V6_MUSTER')]:
    v=add(key,ch,title,deps,[bridge()],goal,'对应支线成果与主线战区均已开放后自动结算。',
          '增援为可选收益；下一场主线不要求等齐所有增援。','领取军资后继续本战区征伐。',
          optional=True,items=items,links=[link(nextkey,'返回本战区主线')],icon_texture='svs:textures/quest/emblems/fortress.png')
    if pool:v['select_rewards']=[pool]

# One collector, one ledger. Distinct quests, not stack quantity, earn milestones.
read('C_ROOT','collector','君王武库 · 收录即有军资',['V6_AFTER_M01'],
     '收藏不是把武器锁进箱子。每一件鉴定过的兵器和每一套甲胄，都应成为下一次征伐的资本。',
     'T2基础、T1精锐、T0顶阶；这是按取得成本、战技与用途编排的实用分档，尚未经统一条件下的伤害实测。材料、附魔与打法可改变表现。',
     '先打开T2鉴定。每个物品只奖一次；全鉴、分档赏格与收藏家毕业都集中在这里。',optional=True,xp=0,icon_texture='svs:textures/quest/emblems/arsenal.png')
for tier,gate in [('T2','C_ROOT'),('T1','V6_AFTER_M04'),('T0','V6_AFTER_M13')]:
    deps=['C_ROOT'] if tier=='T2' else ['C_T2' if tier=='T1' else 'C_T1',gate]
    read('C_'+tier,'collector',tier+'赏格 · '+{'T2':'基础兵装','T1':'精锐武装','T0':'王权名器'}[tier],deps,
         '征伐军资按武库档次结算。'+tier+'物品可以在对应全鉴逐件登记，武器、护甲套装分别累计。',
         '全鉴按六件一批展开；“下一批”只切换查阅范围，不要求先把上一批全收齐。持有记录不扣除物品；护甲部件可分次取得。',
         '对应档次全鉴开放，收藏里程碑随真实鉴定累积。',optional=True,xp=0,icon_texture='svs:textures/quest/emblems/'+tier.lower()+'.png')
read('C_RELIC','collector','遗珍赏格 · 让饰品服务战术',['C_T2'],
     '武器决定出手方式，护甲与饰品决定一场远征能走多远。把遗珍纳入同一本武库。',
     '槽位与效果使用原生说明；随机探索不要求指定唯一掉落。收录奖励与原生物品分开，不复制刚取得的遗珍。',
     '遗珍鉴定按批展开；达到里程碑再领取一次功能饰品选择。',optional=True,xp=0,icon_texture='svs:textures/quest/emblems/relic.png')

# Explicit reviewed exceptions override cost bands. No obsolete historical DPS is used.
TOP={
'cataclysm:the_incinerator','cataclysm:soul_render','cataclysm:tidal_claws','cataclysm:astrape','cataclysm:gauntlet_of_bulwark',
'cataclysm:annihilator','cataclysm:the_immolator','cataclysm:the_annihilator',
'slu:soul_of_cinder_sword','slu:cinder_king_greatsword','slu:grand_trial_sword','slu:moonlight_sword',
'wom:gesetz','wom:antitheus','wom:agony','wom:tormented_mind','wom:ruine','wom:herrscher',
'souls_like_bosses:spear_of_melkor','souls_like_bosses:dark_moon_greatsword','wukong:jingubang',
'simplyswords:stormbringer','simplyswords:emberblade','simplyswords:thunderbrand','simplyswords:molten_edge',
'simplyswords:livyatan','simplyswords:bramblethorn','simplyswords:watcher','simplyswords:hearthflame',
'simplyswords:soulkeeper','simplyswords:twisted_blade','simplyswords:soulstealer','simplyswords:soulrender',
'simplyswords:whisperwind','simplyswords:caelestis','simplyswords:icewhisper','simplyswords:arcanethyst',
'simplyswords:stars_edge','simplyswords:wickpiercer','simplyswords:tempest','simplyswords:waxweaver',
'simplyswords:hardclaymore','simplyswords:righteous_relic','simplyswords:tainted_relic'}
LATE_BOSSES={q.get('boss_entity') for q in oldq.values() if q.get('boss_slot') in ['M12','M14','M15','M16','M17','M20','M21','M22','M23','M24','S09','S10','S11','S13']}
rank_report=[]
def rank(e):
    id=e['id'];path=id.split(':',1)[1]
    loot_entities={s.replace(':entities/',':') for s in e['loot'] if ':entities/' in s}
    ingredients={i for r in e['sources'] for i in r['ingredients']}
    if id in TOP:return 'T0','人工标记：顶阶独有战技/多阶段终盘制作路线'
    if e['kind']=='armor' and any(s in path for s in ['ignitium','cursium','monstrous','dragonlord','gundyr','soul_of_cinder','cinder_king']):return 'T0','顶阶甲材或终盘首领甲胄系列'
    if loot_entities & LATE_BOSSES:return 'T0','高阶/终盘首领原生战利品：'+','.join(sorted(loot_entities & LATE_BOSSES))
    if any('ignitium' in i or 'cursium' in i for i in ingredients):return 'T0','配方含顶阶首领金属'
    if path.startswith(('wooden_','stone_','leather_','golden_','iron_','copper_','chainmail_')) and e['kind']=='weapon':return 'T2','基础材料兵装，承担入门与过渡'
    if id.startswith('minecraft:'):
        return ('T1','下界合金/钻石级标准兵装') if path.startswith(('netherite_','diamond_')) else ('T2','原版基础军备')
    if any(s in path for s in ['netherite','runic','diamond','manyullyn','hepatizon','queen','witherite','abyssal','soul','dragon','paladin','obsidian','ruby','amethyst']):return 'T1','进阶材质、专属系列或魂系军械；未列顶阶例外'
    if e.get('skills') or any(':entities/' in s for s in e['loot']):return 'T1','独有战技或首领/精英战利品路线'
    if e['id'].split(':')[0] in ['slu','wom','bloodandmadness','epicfight_awaken','woc_remastered','w_o_w_armors_and_weapons','souls_like_armors']:return 'T1','特色武技/甲胄系列，作为精锐档起点；需随实测调档'
    return 'T2','基础/通用装备或资料不足，保守编入入门档；不据旧面板猜测顶阶'
for e in cat.values():
    tier,why=rank(e);e['tier']=tier;e['rank_reason']=why
    rank_report.append(dict(id=e['id'],name=e['name'],kind=e['kind'],tier=tier,reason=why,recipes=[r['id'] for r in e['sources']],loot=e['loot']))

# Reuse the well-sourced item descriptions, but replace every obsolete policy.
catalog_old={id:q for q in old['quests'] for id in q.get('catalog_items',[])}
def clean_sections(v):
    result=[]
    for s in v.get('sections',[]):
        if s['title'] in ['收藏家计件归属','关联军械','派生与用途']:continue
        lines=[]
        for line in s['lines']:
            line=line.replace('本页不额外发放技能书','技能书可从征伐与鉴定赏格另行领取').replace('任务不额外复制这件装备。','')
            if any(s in line for s in ['独立收藏页','不返还一份复制品','完整军械','不参与收藏家']):continue
            lines.append(line)
        if lines:result.append(dict(title=s['title'],lines=lines))
    return result
sets=collections.defaultdict(list)
for e in cat.values():
    if e['kind']=='armor':
        oldnode=catalog_old[e['id']]
        sets[oldnode['key']].append(e)
for es in sets.values():
    tier=min((e['tier'] for e in es),key=lambda t:int(t[1:]))
    for e in es:
        if e['tier']!=tier:
            e['rank_reason']='同系列甲胄统一分档；'+e['rank_reason'];e['tier']=tier
            report=next(r for r in rank_report if r['id']==e['id']);report.update(tier=tier,reason=e['rank_reason'])
entries=[]
for e in cat.values():
    if e['kind']!='armor':entries.append([e])
entries+=list(sets.values())
def entry_sort(es):
    e=es[0];return (e['id'].split(':')[0],e.get('combat_category') or '',e['id'])
milestone_lists=collections.defaultdict(list)
lookup={}
for tier in ['T2','T1','T0','RELIC']:
    ch='curios' if tier=='RELIC' else 'arsenal_'+tier.lower()
    candidates=[es for es in entries if (es[0]['kind']=='curio')==(tier=='RELIC') and (tier=='RELIC' or min((e['tier'] for e in es),key=lambda t:int(t[1:]))==tier)]
    # Three branches, each reveals six real targets at a time, never a fan of 30.
    groups=collections.defaultdict(list)
    for es in candidates:groups[es[0]['kind']].append(es)
    for branch,(kind,group) in enumerate(sorted(groups.items())):
        group.sort(key=entry_sort)
        parent='C_RELIC' if tier=='RELIC' else 'C_'+tier
        for page in range((len(group)+5)//6):
            gate=f'LEDGER_{tier}_{kind}_{page}'
            deps=[parent] if page==0 else [f'LEDGER_{tier}_{kind}_{page-1}']
            portion=group[page*6:(page+1)*6]
            label={'weapon':'兵器','armor':'甲胄','curio':'遗珍'}[kind]
            head='展开'+label if page==0 else '下一批'+label
            g=read(gate,ch,head+' · '+str(page+1),deps,
                   '本批可鉴定：'+'、'.join(es[0]['name'] for es in portion)+'。',
                   '按需要逐批展开。翻页不要求先集齐上一批；不感兴趣的武器可以跳过。',
                   '本批物品持有检测开启，已拥有的物品放入随身物品栏即可登记。',optional=True,xp=0,
                   icon_texture='svs:textures/quest/emblems/'+('relic' if tier=='RELIC' else tier.lower())+'.png')
            g['position']=[branch*23,page*5.8]
            for index,es in enumerate(portion):
                ids=[e['id'] for e in es];key='GEAR_'+hashlib.sha256('|'.join(sorted(ids)).encode()).hexdigest()[:16]
                if tier=='RELIC':display_tier=es[0]['tier']
                else:display_tier=tier
                reward={'T2':1,'T1':4,'T0':12}[display_tier]*(2 if kind=='armor' and len(ids)>1 else 1)
                # Chestpieces are readable representatives; never old nonexistent boots.
                icon=next((i for i in ids if any(t in i for t in ['chestplate','cuirass','brigandine']) and 'boots' not in i),ids[0])
                title=es[0]['name'] if len(ids)==1 else re.sub(r'(头盔|胸甲|护腿|靴子|靴|战靴)$','',es[0]['name'])+' · 系列'
                v=add(key,ch,display_tier+' · '+title,[gate],[it(i) for i in ids],
                    '把这'+('组甲胄' if len(ids)>1 else '件'+label)+'纳入同一本君王武库。',
                    '取得'+('本项所列部件各1件，可分次取得。' if len(ids)>1 else es[0]['name']+'1件。')+' 不消耗；不限耐久、附魔和名称。',
                    display_tier+'分档依据：'+es[0]['rank_reason'].replace('人工标记：','')+'。实际表现还取决于技能、强化与配装。',
                    '首次鉴定奖励真菌残魂×'+str(reward)+'；计入收藏家对应档次的'+label+'里程碑。',icon,
                    optional=True,xp=0,items=[['kubejs:spore_coin',reward]],catalog_items=ids,tier=display_tier,ledger_kind=kind,
                    sections=clean_sections(catalog_old[ids[0]]),hide_dependency_lines=True,
                    links=[link('C_RELIC' if tier=='RELIC' else 'C_'+tier,'回到对应赏格与阶段奖励')])
                v['position']=[branch*23+(index%3)*3.2+3.2,page*5.8+(index//3)*2.5]
                if kind=='armor':
                    acquire=[]
                    for e in es:
                        recipe=e['sources'][0] if e['sources'] else None
                        desc=('材料线索：'+'、'.join(names.get(i,i) for i in recipe['ingredients'][:6])+'；按JEI核对工位与数量。') if recipe else '从本系列原生探索、制作或挑战路线取得，具体查看JEI与物品说明。'
                        acquire.append(e['name']+'：'+desc)
                    v['sections']=[sec('本项部件与取得路线',*acquire),sec('出征检查','部件可以分次取得；本项所有列出部件均已登记时才计为一项鉴定。','检查耐久、维修材料与原生套装说明，再决定整套使用或与特色单件混搭。')]
                milestone_lists[(display_tier,kind)].append(key)
                for id in ids:lookup[id]=key

for tier in ['T2','T1','T0']:
    for kind,label,thresholds in [('weapon','兵器',[3,8,16]),('armor','甲胄',[1,3,6])]:
        if tier=='T0' and kind=='armor':thresholds=[1,2,3]
        prev='C_'+tier
        for ix,num in enumerate(thresholds):
            k='C_'+tier+'_'+kind+'_'+str(num)
            # A ranked ledger reward must count unique completed acquisitions, not duplicates.
            q=add(k,'collector',tier+' · '+label+'鉴定'+str(num)+'项',[prev],
                  [bridge('catalog_count',count=num,quest_keys=milestone_lists[(tier,kind)])],
                  '在'+tier+'全鉴中完成'+str(num)+'项不同'+label+'的实际取得，形成一套有深度的战备资产。',
                  '累计完成'+str(num)+'项'+tier+label+'鉴定；同一物品多把不会重复计数。',
                  '护甲系列按本项全部列出部件计1项，可分次取得；不强迫同时穿戴，也不要求同时装满背包。',
                  '领取该档赏格，继续补强下一段主线。',optional=True,xp={'T2':60,'T1':120,'T0':240}[tier],
                  items=[['kubejs:spore_coin',{'T2':8,'T1':24,'T0':64}[tier]*(ix+1)]],
                  icon_texture='svs:textures/quest/emblems/'+tier.lower()+'.png')
            if ix==0:q['select_rewards']=['v6_'+tier.lower()+'gear']
            elif ix==1:q['select_rewards']=['v6_guard' if tier=='T2' else 'v6_veteran' if tier=='T1' else 'v6_master']
            else:q['select_rewards']=['v6_fieldgear' if tier=='T2' else 'v6_elitegear' if tier=='T1' else 'v6_t0gear']
            prev=k
Q['C_ARMOR2']=Q.pop('C_T2_armor_1');Q['C_ARMOR2']['key']='C_ARMOR2'
for q in Q.values():
    q['deps']=['C_ARMOR2' if k=='C_T2_armor_1' else k for k in q['deps']]
for ix,num in enumerate([3,8,16]):
    keys=[k for (t,kind),ks in milestone_lists.items() if kind=='curio' for k in ks]
    add('C_RELIC_'+str(num),'collector','遗珍鉴定 · '+str(num)+'种',['C_RELIC' if ix==0 else 'C_RELIC_'+str([3,8,16][ix-1])],
        [bridge('catalog_count',count=num,quest_keys=keys)],'让功能饰品覆盖不同远征需求，而不是重复堆同一种。','完成'+str(num)+'种不同遗珍的持有鉴定。',
        '重复取得同一件不叠加计数；奖励为功能选择，原生效果和槽位不变。','奖励支援远征或下一次首领挑战。',optional=True,
        items=[['kubejs:spore_coin',16*(ix+1)]],select_rewards=['v6_fieldgear' if ix<2 else 'v6_elitegear'],icon_texture='svs:textures/quest/emblems/relic.png')
add('C_FINAL','collector','收藏家毕业 · 武库服务王座',['C_T0_weapon_8','C_T0_armor_3','C_RELIC_8'],[bridge()],
    '武库已经覆盖神兵、甲胄与功能遗珍。它的价值在于让你能够应对不同敌人，而不是逼你清空所有名录。','完成顶阶兵器8项、顶阶甲胄3项、不同遗珍8种的鉴定里程碑。',
    '毕业不要求全收集；主线也不会反过来以本项毕业为门槛。','君王武库成形。领取高阶军资，回到总攻与齐天终章。',optional=True,
    items=[['kubejs:spore_coin',160]],select_rewards=['v6_crownweapon','v6_master'],
    links=[link('V6_BRIEF5','把武库投入机械总攻')],icon_texture='svs:textures/quest/emblems/crown.png')

# Compact reference chapters, gated behind the tutorial. No sea of open books.
prev='A12'
for key in ['M01','M02','M03','M04','M05','M06','M07','M08','M09','M10','M11','M12','M13','M14']:
    v=copy.deepcopy(oldq[key]);v.update(chapter='manual',deps=[prev],source=SOURCE,writing_style='v6',optional=True,xp=0,items=[])
    for f in ['position','links','reward_id_keys']:v.pop(f,None)
    v.pop('icon',None);v['icon_texture']='svs:textures/quest/emblems/command.png'
    Q[key]=v;prev=key
prev='V4_PHASE1'
for key in ['B05','B06','B07','B08','R01','R02','R03']:
    if key not in oldq:continue
    v=copy.deepcopy(oldq[key]);v.update(chapter='cycles',deps=[prev],source=SOURCE,writing_style='v6',optional=True)
    for f in ['position','links','reward_id_keys']:v.pop(f,None)
    Q[key]=v
    if v['availability']!='pending':prev=key

# Narrative links now name concrete routes; clean stale pointers and old non-reward policy.
# The player-facing campaign is written as orders, not an implementation report.
boss_lore=[
 '它靠利爪和追击统治荒野，你要从它的狩猎本能里取走第一份进化养料。',
 '厚甲是它横行荒野的本钱，击碎甲壳，骨材就能进入你的熔炉与要塞。',
 '沙下的雷暴截断远征路线。把荒漠重新交给车队与猎人，新领地便能向外延伸。',
 '暴君把每一条矿路都当成王权的延伸。山岭的新主人，只能由正面一战决定。',
 '古族以武技守住要道。用身法、格挡与短连段撕开防线，把运输线路接向遗迹。',
 '旧文明的巨像仍在云端运转。拆解它，就能把古老动力投入你的军工事业。',
 '沉默重卫守着一扇早已失去主人的门。门后的武装与遗产，不该继续埋在尘土里。',
 '冰海埋葬了舰队，却没能埋葬船长的执念。击败亡灵，接收她留下的钥匙与远洋遗物。',
 '猎魔人向天外生命举刀，你要让他明白，这片疆土已经有了新的猎人。',
 '狱火骑士守着夺火远征的第一道门。先拆开重甲，再追向门后的龙焰。',
 '失控的飞龙把焦土当作自己的猎场。夺下龙心，原初火种就不再有屏障。',
 '旧纪元曾借他的火对抗天灾，却没能留下胜利。你会把火种与军团一同带到母巢面前。',
 '圣堂重装仍在宣告旧日誓言，但它的主人已经堕落。让盾牌与遗产进入新王的武库。',
 '亡骸之主用死亡维系秩序，你要以更强的征伐终结这份王权。',
 '辉光女神将权柄铺向天空。折断永昼之翼，把这份耀眼的遗产带回王座。',
 '旧王藏在时间的夹缝中，试图逃过时代更替。你要让这场征伐抵达他面前。',
 '无数旧日战魂汇成一具巨君。正面击溃它，共生体便能向更高的战甲形态迈进。',
 '前锋机甲守着轨道武库的导航链。拆掉它，向天外延伸你的征伐意志。',
 '自律猎影高速游荡在废墟之间。收走索敌核心，让旧军团失去追猎新王的能力。',
 '空间站中的终极兵器锁着武库权限。机械三段攻势的终点，就是它彻底熄火的时刻。',
 '另一位巅峰武者向统帅之位伸手。总攻的号令，只能来自一个人。',
 '旧领主把疆域藏进永夜。斩落他，让前线旗帜跨过最后的暗夜堡垒。',
 '最后守望者守着旧时代的荣光。用练熟的刀剑交锋，让他承认新王已经到来。',
 '戍卫横在界域边界，你的军团在它身后就能直面母巢。击溃它，把火力与补给推进核心腹地。']
benefit_overrides={
 'M03':'荒漠战果投入红石与核心升级储备；战后清除据点外的真菌前哨，完成第一阶段立旗。',
 'M08':'冰海远征带来维修站与远洋补给；受控挑战入口当前未开放。',
 'M12':'火种战果结算后进入诸王战区；劫火实战将在要塞支线开放。',
 'M14':'死灵王魂纳入共生体的进化目标，同时拨付王权技法与下一场军资。',
 'M15':'烈阳权柄纳入王座战果，高阶金属与残魂支持后续征伐。',
 'M16':'时间王魂纳入战果，接着直取冰牢压轴；受控挑战入口当前未开放。',
 'M18':'导航链战果已记录，维修与军工材料拨入前线；下一步直取索敌核心。',
 'M20':'机械武库易主，接到天基整备；发射战役当前未开放。先清除总攻前的最后强敌。',
 'M22':'暗夜王权战果接向最后剑圣与界域戍卫；受控挑战入口当前未开放。',
 'M23':'剑圣的失败确立新王的武道地位，军资支持最后一场守界大战。',
 'M24':'边界已打通，开始总攻盘点。有限母巢战役当前未开放。'}
tactics_overrides={
 'M03':'在开阔沙地留下返程线，拉开足以看清巨虫的距离，再尝试短连段与侧向撤离。',
 'M08':'把返程点留在安全岸线。进入战场前补齐耐久与食物，不在陌生水域耗尽最后一份补给。',
 'M12':'先留出横向移动与撤离的空间，再寻找法术间隙切入；不要把全部耐力消耗在第一轮进攻。',
 'M16':'这是一场独立王座挑战。使用练熟的武器与防御方案，先看清动作，再决定追击。',
 'M18':'在机械竞技场先找回收与补给位置。面对重型机械，保持能看全动作的距离。',
 'M20':'携带完整维修物资进入空间站，先观察火力与移动窗口，不在狭窄角落连续贪刀。',
 'M22':'保留足以辨认对手和返程的视野，先确认安全距离，再用短连段建立节奏。',
 'M23':'控制锁定、收招与耐力，用练熟的兵器迎接剑戟交锋。上一场的军资可以先用于维修。',
 'M24':'先在巨型目标面前找到能看全动作的距离。返程点与补给留在战场外缘，再向前压进。'}
for n in range(1,25):
    slot=f'M{n:02}';v=Q['V4_'+slot]
    v['text'][0]=plans[n-1][4]+' '+boss_lore[n-1]
    v['text'][1]='击败'+v['title'].split(' · ')[-1]+'1次。'
    if slot in tactics_overrides:v['text'][2]=tactics_overrides[slot]
    if slot in benefit_overrides:
        v['text'][3]=benefit_overrides[slot];Q['V6_ORDER_'+slot]['text'][2]=benefit_overrides[slot]
    v['sections']=[sec('远征入口',D[slot]['location']+'。',
        '受控挑战入口当前未开放。' if slot in ['M08','M16','M22'] else '先准备往返路线、食物与维修物资，再接近首领。'),
        sec('作战情报',v['text'][2]),sec('战果转用',v['text'][3],'战场原生掉落自行拾取；下一项军需结算另行领取。')]
    if slot in ['M08','M16','M22']:v['subtitle']='受控入口尚未开放 · '+D[slot]['location']
Q['V6_AFTER_M20']['text'][2]='天基实战当前未开放。总攻之前先扫清争王者与最后守界者。'
Q['V6_AFTER_M24']['text'][2]='接着盘点火力与军资。劫火、天基与有限母巢战役将按实际开放进度接入。'
after_hints={
 'M01':'选一条支线先投入战果：开炉打造新武器、鉴定已得兵装，或继续喂食共生体。下一场主线追猎岩壳巨兽。',
 'M02':'沿要塞支线合成箭塔，再用手套练习收放。把火力留在据点外围，同时准备穿过荒漠的补给。',
 'M03':'把新兵刃带去清理外围真菌。想进一步扩大战果，可以前往独立猎场或开始观察龙族。',
 'M04':'先查看T1武库的兵器与甲胄赏格；缺材料时，锻造师的合金路线提供另一种补强方式。',
 'M05':'任选一本适合自己的精锐技法，检查技能槽与兵器搭配，再向云端旧塔进发。',
 'M06':'这枚核心既能投入防线，也能用于研究台配方。先选眼下最需要的一项，另一份核心随后自行制造。',
 'M07':'整套铁甲可留作备用，也可通过原生交互交给现有守军。检查耐久，再准备冰海远征。',
 'M08':'把维修站装进远征箱，带上手套与食物。下一段夺火战争发生在更远的旧防线上。',
 'M09':'先补齐防护和技能，再连续突破骑士、飞龙与受火者三道夺火战位。',
 'M10':'根据现有配装选择黑曜石头骨或消耗补给，读清原生效果，再迎接炼狱飞龙。',
 'M11':'领取高温材料和军资，修好主武器，下一项直面火种掌控者。',
 'M12':'劫火实战目标当前未开放。先收好这笔战果，再向圣堂、死亡、永昼与时间的王座推进。',
 'M13':'打开T0武库查看顶阶方向。挑一套适合自己的护甲与饰品，继续逼近死亡王座。',
 'M14':'任选王权技法，把原生共生进化与个人武技一起投入下一场远征。',
 'M15':'把高阶金属用于原生制作，残魂留作军需。下一场将面对时间夹缝中的旧王。',
 'M16':'检查主武器、护甲、饰品与身法，再深入冰牢迎接本阶段压轴。',
 'M17':'领取精锐饰品与总攻军资。后方准备便携维修，前线开始夺取机械三段权限。',
 'M18':'下一步猎取索敌核心。沿军工支线把回收工具和维修物资带上前线。',
 'M19':'补齐维修材料，检查武器耐久，继续向空间站中的终极武库推进。',
 'M21':'补充战斗口粮与军资，继续向永夜封锁区推进。',
 'M22':'带一套练熟的武器、可靠护甲与技能组合，跨过最后的剑圣与守界大战。',
 'M23':'将军资用于出发前维修，再前往核心熔铸遗迹。武库与职业增援可按需要领取。'}
for slot,hint in after_hints.items():Q['V6_AFTER_'+slot]['text'][2]=hint
Q['V4_M25']['text']=['真菌把星球当作粮仓，你把军团炮口对准它们的母巢。铺开火力阵地，以劫火与天基支援推进，最后亲手捏碎本场战役的核心。',
    '完成同一场有限母巢攻坚，赢下必要波次与最终核心战。','本战役当前未开放；开放后按场次规则结算。野外同类首领击杀不计为战役胜利。',
    '核心陷落之后，才会开启异界大圣残躯的终极试炼。']
Q['C_ROOT']['sections']=[sec('如何使用分档',
    'T0最高，T1精锐，T2基础。分档同时考虑取得链、独有战技、用途与稀有材料，实战体验后可调整。',
    '匠魂等可换部件装备按形制的基础档收录，实际材料、强化与技能会改变强度。',
    '武器不是只比一击面板；同档也可能分别擅长破防、机动、持续作战或远程。')]
for q in Q.values():
    if q.get('links'):
        q['links']=[{**l,'label':Q[l['key']]['title']} for l in q['links'] if l['key'] in Q]
    for t in q['tasks']:
        if t.get('target') in missing:raise ValueError(('invalid target',q['key'],t))
    if q.get('icon') in missing:q.pop('icon');q['icon_texture']='svs:textures/quest/emblems/arsenal.png'
    q['text']=[s.replace('本页不额外发放技能书','技能书由征伐与鉴定赏格补充') for s in q['text']]
    assert all(dep in Q for dep in q['deps']),(q['key'],q['deps'])

# Compact authored campaign lanes and per-chapter themed stage banners.
colors={'main':'&6','career':'&b','arsenal':'&a','optional':'&d','reference':'&7'}
for ch in d['chapters']:
    ch['title']=colors[ch['group']]+ch['title']+'&r'
    qs=[q for q in Q.values() if q['chapter']==ch['key']]
    if ch['key'].startswith('arsenal_') or ch['key']=='curios':
        # Gated batches are positioned within the same book page.
        ch['images']=[]
    else:
        # Topological order keeps campaign lines short even when authored out of order.
        done=set();ordered=[]
        while len(ordered)<len(qs):
            ready=[q for q in qs if q['key'] not in done and all(dep in done or Q[dep]['chapter']!=ch['key'] for dep in q['deps'])]
            assert ready,('layout cycle',ch['key'])
            for q in ready:
                ordered.append(q);done.add(q['key'])
        for i,q in enumerate(ordered):
            row,col=divmod(i,5);q['position']=[(col if row%2==0 else 4-col)*3.4,row*4.2]
        ch['images']=[{'x':6.8,'y':-3.4,'width':17.6,'height':3.0,'image':'svs:textures/quest/banners/'+ch['icon_texture'].rsplit('/',1)[1],
                      'alpha':180,'order':-100,'hover':[re.sub('&.','',ch['title'])],'click':'','dev':False,'corner':False}]

# Edition-specific IDs deliberately do not reinterpret old claimed/completed tasks.
# Existing save records are left untouched. Acceptance should use a fresh test world.
mapping={k:'E6_'+k for k in Q}
for q in Q.values():
    q['key']=mapping[q['key']];q['deps']=[mapping[k] for k in q['deps']]
    for l in q.get('links',[]):l['key']=mapping[l['key']]
    for t in q['tasks']:
        if 'quest_keys' in t:t['quest_keys']=[mapping[k] for k in t['quest_keys']]
d['quests']=list(Q.values())
(ROOT/'docs/questbook_v2.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'docs/data/questbook_v6_rankings.json').write_text(json.dumps({'method':'实用战备分档，T0最高；现版配方、战利品、战技与人工例外；不使用旧DPS作为现版排名','entries':rank_report,'excluded_runtime_missing':sorted(missing)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(B/'migration.json').write_text(json.dumps({'policy':'全新E6任务ID，不转写旧完成与领奖记录；不操作任何世界存档','old_to_new':mapping},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'chapters':len(d['chapters']),'quests':len(d['quests']),'main_objectives':sum(not q['optional'] for q in d['quests']),'ranked_items':len(cat),'tier_counts':dict(collections.Counter(e['tier'] for e in cat.values()))},ensure_ascii=False))
