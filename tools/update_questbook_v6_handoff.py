"""Keep the current entry point distinct from the rejected, installed v5."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
note='> **2026-10-17 第6版任务已改写、尚未安装：** 用户再次退回第5版后，主线已按天外成王剧情改为连续征伐；收藏家与全鉴合并，T2基础/T1精锐/T0顶阶分档领奖，逐步显示；技能书、饰品、装备及军工军资已接入，运行时发现的16项失效物品已移除。具体内容、分档依据与未开放事件见[本轮说明](FTB任务v6_王途与分级武库重写.md)。test客户端仍在运行，未覆盖实例、未操作游戏或存档、母本未同步。下方第5版安装记录为已退回的历史版本，不代表第6版已在游戏中生效。\n\n'
for name in ['README.md','HANDOVER.md','资料库总索引.md']:
    p=R/'docs'/name;s=p.read_text(encoding='utf-8')
    if '第6版任务已改写、尚未安装' not in s:
        first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+rest.lstrip('\n'),encoding='utf-8')
p=R/'docs/交接启动词_通用规则.md';s=p.read_text(encoding='utf-8')
s=s.replace('玩家排行氛围化。改已定机制须明确提出重新裁决。','装备分档采用用户最新要求的T2基础/T1精锐/T0顶阶，按本轮清单逐件追溯；不得把历史属性冒充现版实测。改定范围以用户最新指示为准。')
extra='本轮用户明确改定：收藏家与军械全鉴合并；T0为最高档，按不同装备鉴定种数累计，不再按重复库存堆数；装备/技能书/饰品/残魂分档奖励；任务逐步可见。第6版入口见《FTB任务v6_王途与分级武库重写》。旧“收藏与图鉴分离、禁止Tier、任务不发技能书”等口径不得否定本次要求。当前游戏仍是第5版，不能声称第6版已安装。测试交给用户，不自行控制游戏。\n\n'
if '本轮用户明确改定：' not in s:s=s.replace('证据分别标记：',extra+'证据分别标记：')
p.write_text(s,encoding='utf-8')
for name in ['交接启动词_规划AI.md','GLM_交接启动词.md']:
    p=R/'docs'/name;s=p.read_text(encoding='utf-8')
    if '第6版任务已改写、尚未安装' not in s:
        first,rest=s.split('\n',1);s=first+'\n\n'+note+rest.lstrip('\n')
    s=s.replace('脚本限伤或数值Tier表。','脚本限伤或把历史DPS伪装成现版实测的Tier表。用户当前已要求T0/T1/T2实用分档及分档奖励，按第6版依据执行。')
    p.write_text(s,encoding='utf-8')
print('Updated current documentation entries and handoff rules; historical versions retained')
