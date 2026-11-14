"""Append reviewed Legendary Bosses encounters to the installed v6 campaign.

Stable E6 IDs and rewards are preserved. Input is a scoped pre-change snapshot;
do not rerun the v6-from-v5 full rewrite to remove this extension accidentally.
"""
import copy,ctypes,hashlib,json,re,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'backups/legendary_bosses_20261018'
d=json.loads((B/'before/docs/questbook_v2.json').read_text(encoding='utf-8'));Q={q['key']:q for q in d['quests']}
z=zipfile.ZipFile(B/'legendarybosses-0.6.1-beta.jar')
en=json.loads(z.read('assets/legendarybosses/lang/en_us.json'));tw=json.loads(z.read('assets/legendarybosses/lang/zh_tw.json'))
mapper=ctypes.windll.kernel32.LCMapStringW
mapper.argtypes=[ctypes.c_ulong,ctypes.c_ulong,ctypes.c_wchar_p,ctypes.c_int,ctypes.c_wchar_p,ctypes.c_int]
mapper.restype=ctypes.c_int
def simplified(s):
    size=mapper(0x0804,0x02000000,s,len(s),None,0);assert size>0
    out=ctypes.create_unicode_buffer(size+1);assert mapper(0x0804,0x02000000,s,len(s),out,size)>0
    return out.value
replacements={'伺服器':'服务器','存档档案':'存档文件','档案':'文件','程式':'程序','程序码':'代码','快捷列':'快捷栏','介面':'界面','狱髓':'下界合金','地狱石':'下界岩','凋零骷髅':'凋灵骷髅','萤幕':'屏幕','於':'于','後':'后','麽':'么','303实体':'实体303','Entity 303':'实体303','资料':'数据','储存':'保存','侦测':'检测','连线':'连接','覆写':'覆盖','空指标':'空指针','十字镐':'镐','世界重生':'世界再生'}
zh={}
for k in en:
    s=simplified(tw[k])
    for a,b in replacements.items():s=s.replace(a,b)
    zh[k]=s
zh.update({
 'entity.legendarybosses.herobrine':'Herobrine', 'entity.legendarybosses.entity_303':'实体303',
 'entity.legendarybosses.entity_303_clone':'实体303（分身）','entity.legendarybosses.entity_303_mini':'微型303',
 'entity.legendarybosses.null':'Null','entity.legendarybosses.notch':'Notch',
 'item.legendarybosses.herobrine_greatsword':'Herobrine之刃',
 'item.legendarybosses.entity_303_scythe':'实体303之镰','item.legendarybosses.entity_303_hood':'实体303兜帽',
 'item.legendarybosses.creation_pickaxe':'创世之镐',
 'message.legendarybosses.entity_303.delete_world_hint':'在引导期间命中他%s次，打断删除！',
 'message.legendarybosses.entity_303.delete_progress':'删除世界 %s｜打断 %s/%s',
 'message.legendarybosses.null.no_totems_subtitle':'kill -9：每枚图腾都会被逐个击碎',
 'message.legendarybosses.null.no_totems_title':'不死图腾禁用',
 'message.legendarybosses.null.no_totems_done':'图腾已经耗尽，你可以行动了。',
 'message.legendarybosses.null.sigkill':'进程终止。剩余图腾：%s',
 'advancements.legendarybosses.herobrine_slayer.title':'白瞳传说陨落',
 'advancements.legendarybosses.entity_303_slayer.title':'入侵已终止',
 'advancements.legendarybosses.null_slayer.title':'虚无亦可击溃',
 'advancements.legendarybosses.notch_slayer.title':'造界者的认可'})
assert set(zh)==set(en)
for k in en:assert re.findall(r'%(?:\d+\$)?[sdf]',en[k])==re.findall(r'%(?:\d+\$)?[sdf]',zh[k]),k
lp=R/'kubejs/assets/legendarybosses/lang/zh_cn.json';lp.parent.mkdir(parents=True,exist_ok=True);lp.write_text(json.dumps(zh,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

download=json.loads((B/'download.json').read_text(encoding='utf-8'))
(R/'mods/legendary-bosses.pw.toml').write_text('name = "Legendary Bosses"\nfilename = "legendarybosses-0.6.1-beta.jar"\nside = "both"\n\n[download]\nurl = "'+download['url']+'"\nhash-format = "sha512"\nhash = "'+download['sha512']+'"\n\n[update]\n[update.curseforge]\nfile-id = 9234898\nproject-id = 1716327\n',encoding='utf-8')
# Same effective default as AUTO in this pack (TConstruct is installed), now explicit.
# Preserve original moves, damage, item erasure, terrain restoration and flight rules.
cfg='''# SvS: 原生MODDED档；AUTO在本包也会因匠魂而选择此档。
# 保留作者倍率与招式；实际EF战斗质量和最终数值仍由独立测试验收。
[difficulty]
mode = "MODDED"
strongModList = ["avaritia", "draconicevolution", "mekanism", "apotheosis", "tconstruct"]
[difficulty.vanilla]
healthMultiplier = 0.3
damageMultiplier = 0.45
armorOverride = 18.0
armorToughnessOverride = 0.0
[difficulty.modded]
healthMultiplier = 1.0
damageMultiplier = 1.0
armorOverride = -1.0
armorToughnessOverride = -1.0
[difficulty.custom]
healthMultiplier = 1.0
damageMultiplier = 1.0
armorOverride = -1.0
armorToughnessOverride = -1.0
[multiplayer]
healthPerExtraPlayer = 0.0
playerScanRadius = 32.0
[bosses.herobrine]
enabled = true
healthMultiplier = 1.0
damageMultiplier = 1.0
[bosses.entity303]
enabled = true
healthMultiplier = 1.0
damageMultiplier = 1.0
[bosses.null]
enabled = true
healthMultiplier = 1.0
damageMultiplier = 1.0
[bosses.notch]
enabled = true
healthMultiplier = 1.0
damageMultiplier = 1.0
[mechanics]
antiInfinityCounter = true
nullDeletesItems = true
flightLock = true
[griefing]
nullErasesBlocks = true
notchCreationBlocks = true
'''
p=R/'config/Legendary Bosses/legendarybosses.toml';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(cfg,encoding='utf-8')

def sec(t,*lines):return {'title':t,'lines':list(lines)}
def it(id,n=1):return {'kind':'item','target':id,'count':n,'consume':False}
def link(k,t):return {'key':k,'label':t}
def add(k,ch,title,deps,tasks,text,**kw):
    assert k not in Q
    q=dict(key=k,chapter=ch,title=title,deps=deps,tasks=tasks,text=text,
           optional=kw.pop('optional',False),availability='wired',xp=kw.pop('xp',0),items=kw.pop('items',[]),
           writing_style='v6',source='用户2026-10-18新增Legendary Bosses要求；0.6.1-beta Forge JAR注册、招式与终场结算代码；剧情v5增补',**kw)
    Q[k]=q;return q
def img(boss):return 'svs:textures/quest/boss/lb_'+boss+'.png'

bosses=[
 dict(key='herobrine',label='白瞳君王·Herobrine',slot='LB01',chapter='front',before='E6_V6_AFTER_M17',next='E6_V4_PHASE3',
      hp=3200,armor=75,damage=20,icon='legendarybosses:herobrine_greatsword',
      title='诸王之上，还有白瞳之王',
      goal='你已击溃咒翼灵骸，却还不能宣布旧世诸王尽数伏诛。白瞳君王Herobrine握着黑曜符文与雷暴，他将成为诸王篇真正的终点。',
      strategy='在本包叙事中，他是旧纪元最深处的武道王者，并非真菌造物，也不是另一位天外来客。夺取他的符文兵刃，才能把诸王篇的战果带入机械总攻。',
      phases=['开场：白瞳剑士使用瞬身与反击。看到蓄势再决定短连段，不以长时间锁定站桩硬换。','生命降至66%：转为符文战士，出现凋灵骷髅弹幕与黑曜攻势；转阶段演出期间无法正常伤害。','生命降至33%：狂暴形态带来陨石雨与黑曜审判。吸引与红圈出现时优先撤出，再把握出招后的窗口。'],
      ritual=['底层铺3×3金块，上层中央下界岩，东南西北四个相邻格放红石火把。','用打火石或火焰弹点燃中央下界岩。仪式会消耗祭坛材料；中途破坏可中断。','在远离基地的开阔独立场地召唤。二阶段凋灵骷髅在mobGriefing开启时可能破坏地形。'],
      offer=[it('minecraft:gold_block',9),it('minecraft:netherrack'),it('minecraft:redstone_torch',4)],
      payout=[['kubejs:spore_coin',96],['tconstruct:manyullyn_ingot',8]],select=['v6_master'],
      outcome='诸王战果正式收束。Herobrine之刃从原生战利品中取得，星图另拨军资与技法，接下来夺取钢铁军团的天基武库。'),
 dict(key='entity_303',label='赤码入侵者·实体303',slot='LB02',chapter='counterattack',before='E6_V6_AFTER_M20',next='E6_V6_ORDER_M21',
      hp=2800,armor=60,damage=18,icon='legendarybosses:entity_303_scythe',
      title='武库易主，终端却传来第二道命令',
      goal='机械三巨头已经熄火，你的命令却仍被另一个存在篡改。实体303侵占了旧世终端；先斩断这名赤码入侵者，军工系统才只听新王号令。',
      strategy='将原生的“病毒入侵”融入旧纪元武库争夺。他的假聊天和删除进度属于战斗演出；你要夺取的是原生镰刀、兜帽与终端战果。',
      phases=['开场：悬浮镰手以火球、追踪光束和雷标骚扰。火球可反弹；长光束应利用视线阻挡或贴近寻找窗口。','生命降至66%：分身、微型303与代码裂隙加入。观察发光红眼寻找本体，分身不计为胜利。','生命降至33%：烈焰飞镰与删除引导加入。按屏幕要求在引导期间命中本体，打断大招；回旋镰去程与返程均有判定。'],
      ritual=['底层铺3×3黑曜石，上层中央红石块，四角放灵魂火把。','在书与笔的页面写入303，用书右击中央红石块；已成书中包含303也可被原生检测识别。','仪式消耗终端并改写书页。战斗假消息不是系统报错；真正的加载错误应查看日志。'],
      offer=[it('minecraft:obsidian',9),it('minecraft:redstone_block'),it('minecraft:soul_torch',4),it('minecraft:writable_book')],
      payout=[['kubejs:spore_coin',112],['minecraft:netherite_scrap',4]],select=['v6_elitegear'],
      outcome='赤码命令已被截断。原生战利品提供实体303之镰与兜帽，新的军资支援最后的争王者与守界战。'),
 dict(key='null',label='虚无抹消者·Null',slot='LB03',chapter='counterattack',before='E6_V6_AFTER_M24',next='E6_V6_MUSTER',
      hp=3000,armor=60,damage=22,icon=None,
      title='打穿边界，还要击溃边界中的虚无',
      goal='界域戍卫倒下后，母巢出发线却被一片无法命名的空白吞没。Null抹除地面、武装与视野。你必须让虚无也承认自己可以被击败。',
      strategy='他是旧世界“抹除法则”的关口，与其后的造界者形成破坏与创造的对照。击溃Null后才汇集总攻军资；不将他写成真菌的主脑。',
      phases=['开场：掌击、虚空弹与抹除线加入，部分弹射物会穿过它。沿白色预兆侧移，不在脚下失去立足点时贪刀。','生命降至66%：坍缩、格式化、撤销与复制地面加入。离开标记地面；看清撤销留下的位置，避免被回送进危险区。','生命降至33%：黑雾压缩视野，return null倒计时结束前靠近其身边安全圈。首次进入此阶段时，携带的不死图腾可能触发定身并被逐个消耗。'],
      ritual=['在铁砧把命名牌改名为小写null，然后用玩家丢弃操作将它抛出。','命名牌会在仪式中消失，随后Null出现。不要在武器库或村庄旁随意抛出这个名字。','战前将不死图腾存回后方，检查随身物品栏与饰品槽。原生第三阶段会定身并消耗检测到的图腾，不只是击落副手的一枚。','主手和护甲会暂时移除并由模组安排返还；进入独立测试世界先验恢复，不携带唯一珍藏品试战。'],
      offer=[it('minecraft:name_tag'),it('minecraft:anvil')],
      payout=[['kubejs:spore_coin',128],['minecraft:golden_carrot',24]],select=['v6_master'],
      outcome='虚无消散，总攻出发线重新出现。回收自己的行装与场地，再汇集劫火、天基和火力军资，继续有限母巢战役。'),
 dict(key='notch',label='造界者·Notch',slot='LB04',chapter='finale',before='E6_V4_M25',next='E6_V6_SAGE_ORDER',
      hp=4000,armor=60,damage=24,icon='legendarybosses:creation_pickaxe',
      title='天灾已平，造界者亲自考验新王',
      goal='母巢已经陷落，旧世界却还没有将最高权柄交给你。Notch以创造之镐重构战场；胜过这位本土造界者，你才算真正跨过此界的最终门槛。',
      strategy='本包将“创造者”定位为本土旧纪元造界权柄的持有者，不宣称现实作者身份，也不改写天外四客。Notch是本土终极大Boss，大圣残躯仍是随后更高一层的异界武道传承。',
      phases=['创造者：近身镐击、地柱、地浪与囚笼交替。先离开重砸预兆，囚笼成形前撤离或尽快突破。','生命降至66%：建筑师用活塞、TNT、发射器和铁巨像扩张火力。多看地面与两侧，避免被夹在连续攻击中。','生命降至33%：创造形态悬空，/fill倒计时要求进入白色安全格；铁砧雨、创世纪与世界再生继续改造战场，按各自标记移动。'],
      ritual=['在平地铺3×3底座，中央草方块，周围八格金块。','手持附魔金苹果右击中央草方块。仪式中途破坏祭坛可中断并返还苹果。','保留地面视野与足够空场，远离核心建筑。暂时建造方块的恢复逻辑存在，跨模组设施仍应在独立世界先验证。'],
      offer=[it('minecraft:gold_block',8),it('minecraft:grass_block'),it('minecraft:enchanted_golden_apple')],
      payout=[['kubejs:spore_coin',192],['minecraft:netherite_ingot',2]],select=['v6_master','v6_t0gear'],
      outcome='造界者收起万物，承认新王已经跨过本土的最后门槛。带上创世之镐与全部战果，向真魂远去的大圣残躯请求赐教。')]

changed={}
for info in bosses:
    boss=info['key'];stem='E6_LB_'+boss.upper();ch=info['chapter'];order=stem+'_ORDER';prep=stem+'_RITUAL';fight=stem+'_VICTORY';after=stem+'_AFTER'
    add(order,ch,info['title'],[info['before']],[{'kind':'checkmark','target':'','count':1}],
        [info['goal'],'阅读本次压轴征伐命令，确认后准备原生召唤仪式。',info['strategy'],'压轴挑战就绪；战绩以原生最终胜利进度为准。'],
        icon_texture=img(boss),boss_campaign_role=info['slot'])
    add(prep,ch,'仪式整备 · '+info['label'],[order],info['offer'],
        ['用旧世界留下的仪式把对手唤到你选定的战场。','持有本项所列材料；任务不扣除，仪式消耗由模组原生处理。',info['ritual'][0],
         '材料已备，按下面步骤起战；取得材料不代表已经召出或战胜首领。'],
        icon=info['offer'][0]['target'],sections=[sec('召唤步骤',*info['ritual'])])
    adv='legendarybosses:'+boss+'_slayer'
    v=add(fight,ch,info['slot']+' · '+info['label'],[prep],[{'kind':'advancement','target':adv,'count':1}],
        [info['goal'],'完成'+info['label']+'的原生最终胜利进度。',
         '三阶段战斗与终场演出完成后结算。转阶段、分身消失和演出开始都不算最终胜利。',info['outcome']],
        icon_texture=img(boss),boss_slot=info['slot'],boss_entity='legendarybosses:'+boss,
        subtitle='主线压轴候选 · 实际EF交互待独立测试',
        sections=[sec('三阶段情报',*info['phases']),sec('原生召唤',*info['ritual']),
                  sec('当前战斗设置','本包使用作者MODDED档，保留原生招式与伤害。纸面基础生命'+str(info['hp'])+'、护甲'+str(info['armor'])+'，并非本包运行时测量结果。',
                      '战斗附近会限制飞行。地面移动、技能与原生攻击的实际配合由你在独立测试世界验收。'),
                  sec('战果与后续',info['outcome'],'原生进度由模组终场授予当时仍追踪首领条的玩家；不以最终一刀限定全队奖励。')],
        links=[link('E6_C_T0','T0君王武库'),link('E6_G07','总攻携行军工')])
    add(after,ch,'战果结算 · '+info['label'],[fight],[{'kind':'bridge','target':'milestone','count':1}],
        [info['outcome'],'原生最终胜利完成后自动结算。','首领原生装备在战场拾取；本项只拨付下一段军需，不再复制一份同样的Boss武器。',
         '军资到账，继续下一段王途。'],icon_texture=img(boss),items=info['payout'],select_rewards=info['select'],xp=240)
    old=Q[info['next']]['deps'];assert old==[info['before']],(info['next'],old)
    Q[info['next']]['deps']=[after];changed[info['next']]={'before':old,'after':[after]}
    info.update(order_key=order,prep_key=prep,fight_key=fight,after_key=after,advancement=adv)

# Old milestones now describe the new last opponent; no E6 claimed reward is reset.
Q['E6_V4_PHASE3']['text'][0]='咒翼灵骸与白瞳君王已经倒下，旧世诸王的武道与符文遗产正式归库。接下来让钢铁军团交出天基武库。'
Q['E6_V4_PHASE3']['text'][3]='诸王篇压轴已过，机械三巨头的导航、索敌与武库权限成为下一组目标。'
Q['E6_V6_AFTER_M17']['text'][2]='先领取压轴前的军资与饰品，再向白瞳君王Herobrine发出挑战。它才是诸王篇的最后一场。'
Q['E6_V6_AFTER_M17']['links'].append(link('E6_LB_HEROBRINE_ORDER','诸王篇最终压轴'))
Q['E6_V6_AFTER_M20']['text'][2]='武库易主，实体303却仍在篡改旧世终端。先清除这名入侵者，再扫清争王者与最后守界者。'
Q['E6_V6_AFTER_M20']['links'].append(link('E6_LB_ENTITY_303_ORDER','终端入侵者'))
Q['E6_V6_AFTER_M24']['text'][2]='边界之后还有Null留下的虚无封锁。击溃它，再汇集总攻军资；有限母巢战役仍按实际开放状态接入。'
Q['E6_V6_AFTER_M24']['links'].append(link('E6_LB_NULL_ORDER','总攻前最后关口'))
Q['E6_V4_M25']['text'][3]='母巢核心陷落后，旧世界的造界者Notch将亲自考验你。本土最终门槛之后，才是大圣残躯的异界试炼。'
Q['E6_V6_SAGE_ORDER']['text'][0]='母巢已平，造界者Notch也已认可你的胜利。本土再无必须争夺的王座，你走向那具真魂远去的不灭残躯，以君王之姿请求赐教。'
Q['E6_V6_SAGE_ORDER']['text'][3]='本土造界者的考验已过。下一项是大圣双阶段终极试炼，正式事件尚未开放。'

# Four obtainable pieces join the current ledger; boss-only prop weapons do not.
newitems=[
 ('herobrine_greatsword','Herobrine之刃','weapon','herobrine',
  '白瞳君王的原生玩家击杀战利品。三阶段战斗结束并等待终场演出后拾取。',
  '11点总基础攻击伤害、2600耐久是该版本构造值；右击发射弧月剑气，冷却3秒，耗2点耐久。',
  '这是可用的战利品兵刃；虚空之刃、符文大剑、猩红大剑则是Boss演出道具，不加入生存收集门槛。'),
 ('entity_303_scythe','实体303之镰','weapon','entity_303',
  '实体303的原生玩家击杀战利品，与兜帽分别结算。分身和微型303不掉落本体的胜利装备。',
  '12点总基础攻击伤害、2400耐久为原生构造值；右击回旋飞镰，去返程都有攻击，冷却4秒并消耗耐久。',
  '战斗模式下原生右击技能与EF按键的实际冲突待试；先在安全场地确认，不把它自动改成另一套Boss招式。'),
 ('entity_303_hood','实体303兜帽','armor','entity_303',
  '实体303的原生玩家击杀战利品。此处为特色单件，不虚构三件缺失的同名甲胄。',
  '头部装备：穿戴时提供原生火焰免疫，潜行时获得隐身；具体伤害类型交互与其他装备兼容须以游戏表现为准。',
  'T0功能甲位，不代表它的护甲面板一定高于所有重甲。可搭配现有行装。'),
 ('creation_pickaxe','创世之镐','weapon','notch',
  '造界者Notch的原生玩家击杀战利品。等待造界战最终胜利结算后拾取。',
  '9点总基础攻击伤害、3000耐久为原生构造值；3×3挖掘，潜行改为单格；右击建造8秒临时墙，冷却12秒。',
  'T0工程工具位，代表终盘取得与实用能力，不是最高近战DPS。原生采掘与临时墙不会授予玩家创造模式。')]
gate='E6_LB_LOOT_LEDGER'
add(gate,'arsenal_t0','传说战果 · 四件王权军械',['E6_C_T0'],[{'kind':'checkmark','target':'','count':1}],
    ['白瞳君王、赤码入侵者与造界者的可用战利品，统一收入君王武库。','阅读后展开四件装备的首次鉴定。','每件只记录一次；原生Boss道具、分身武器与刷怪蛋不占生存收藏格。','武器与兜帽的鉴定分别计入T0兵器、甲胄里程碑。'],
    optional=True,icon_texture=img('herobrine'))
for path,name,kind,boss,source,use,hint in newitems:
    id='legendarybosses:'+path;key='E6_LB_GEAR_'+path.upper()
    v=add(key,'arsenal_t0','T0 · '+name,[gate],[it(id)],
        ['把'+name+'收入君王武库。','持有'+name+'1件，不消耗，不限附魔、名称或耐久。',hint,
         '首次鉴定奖励真菌残魂12枚，计入T0对应武库赏格。'],
        optional=True,icon=id,items=[['kubejs:spore_coin',12]],catalog_items=[id],tier='T0',ledger_kind=kind,
        sections=[sec('取得路线',source),sec('原生用途',use),sec('搭配提示',hint)],
        links=[link('E6_C_T0','T0赏格'),link('E6_LB_'+boss.upper()+'_VICTORY','对应传说首领')],hide_dependency_lines=True)
    for q in Q.values():
        for t in q['tasks']:
            if t.get('target')=='catalog_count' and q['key'].startswith('E6_C_T0_'+kind+'_'):
                t['quest_keys'].append(key)

# A reversible first-pass EF weapon type uses only types already installed.
# No entity MobPatch: replacing Geo combat with generic biped AI loses its moves.
for path,typ in [('herobrine_greatsword','epicfight:greatsword'),('entity_303_scythe','epicfight:scythe_x')]:
    p=R/f'config/openloader/data/svs/data/legendarybosses/capabilities/weapons/{path}.json';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({'type':typ},indent=2)+'\n',encoding='utf-8')

# Reflow affected campaign pages, preserve all existing logical IDs and rewards.
for ch in ['front','counterattack','finale']:
    subset=[q for q in Q.values() if q['chapter']==ch];done=set();ordered=[]
    while len(done)<len(subset):
        ready=[q for q in subset if q['key'] not in done and all(dep in done or Q[dep]['chapter']!=ch for dep in q['deps'])]
        assert ready,('cycle',ch)
        for q in ready:done.add(q['key']);ordered.append(q)
    for i,q in enumerate(ordered):
        row,col=divmod(i,5);q['position']=[(col if row%2==0 else 4-col)*3.4,row*4.2]
ys=[q['position'][1] for q in Q.values() if q['chapter']=='arsenal_t0' and q['key']!=gate and not q['key'].startswith('E6_LB_GEAR_')]
y=max(ys)+6;Q[gate]['position']=[3.2,y]
for i,entry in enumerate(newitems):Q['E6_LB_GEAR_'+entry[0].upper()]['position']=[3.2+(i%3)*3.2,y+3.0+(i//3)*2.5]
for q in Q.values():
    if q.get('links'):q['links']=[{**l,'label':Q[l['key']]['title']} for l in q['links']]
d['quests']=list(Q.values());d['story_version']=5;d['content_revision']='6.1-legendarybosses-20261018'
d['authority']+='；2026-10-18用户授权Legendary Bosses入包、四压轴节点、剧情/FTB及汉化'
(R/'docs/questbook_v2.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rank=json.loads((B/'before/docs/data/questbook_v6_rankings.json').read_text(encoding='utf-8'))
for path,name,kind,boss,source,use,hint in newitems:
    rank['entries'].append(dict(id='legendarybosses:'+path,name=name,kind=kind,tier='T0',reason='传说首领终盘战利品；功能与战技分档，非DPS实测',recipes=[],loot=['legendarybosses:entities/'+boss]))
(R/'docs/data/questbook_v6_rankings.json').write_text(json.dumps(rank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
facts=dict(download=download,bosses=bosses,changed_dependencies=changed,obtained_items=[x[0] for x in newitems],
           excluded_props=['herobrine_void_blade','herobrine_rune_greatsword','herobrine_crimson_greatsword','entity_303_inferno_scythe'],
           language_keys=len(zh),profile='MODDED (same as default AUTO with TConstruct)',
           evidence='Resources, registration and decompiled bytecode; no game combat acceptance',
           preserved_E6_ids=True,worldgen_resources=0)
(R/'docs/data/legendary_bosses_20261018.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'new_bosses':4,'new_quests':len(Q)-2470,'total_quests':len(Q),'language_keys':len(zh),'stable_existing_ids':True},ensure_ascii=False))
