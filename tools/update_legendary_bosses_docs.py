from pathlib import Path
R=Path(__file__).resolve().parents[1]
note='> **2026-10-18 Legendary Bosses文件已就绪，安装待安全窗口：** 用户指定0.6.1-beta Forge1.20.1已下载审查；四Boss接为诸王篇Herobrine、机械武库实体303、母巢前Null、母巢后/大圣前Notch。剧情v5增补、FTB顺序/军资/T0鉴定、真实模型头像及190键简中已落仓库，旧E6任务ID与奖励保留。用户仍在游戏并明确“先完成文件”，所以未写test/母本、未启动或关闭游戏。入口：[审查与入包](Legendary_Bosses_审查与入包_2026-10-18.md) · [剧情v5](剧情重写_v5_旧世四传说与造界者.md)。实战品质与恢复机制待用户验收。\n\n'
for name in ['README.md','HANDOVER.md','资料库总索引.md','开发计划_执行状态.md','GLM_交接启动词.md','交接启动词_规划AI.md']:
    p=R/'docs'/name;s=p.read_text(encoding='utf-8')
    if '2026-10-18 Legendary Bosses文件已就绪' not in s:
        first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+rest.lstrip('\n'),encoding='utf-8')
for name in ['剧情重写_v4_天外成王篇.md','世界观设定_SvS.md']:
    p=R/'docs'/name;s=p.read_text(encoding='utf-8')
    change='> **2026-10-18剧情v5增补：** 新增旧世四传说作为后期关口，Notch在母巢之后、大圣之前。最新相关顺序见[剧情v5](剧情重写_v5_旧世四传说与造界者.md)，下方v4相应“压轴/唯一最后强敌”按增补覆盖；天外四客与大圣身份不变。\n\n'
    if '2026-10-18剧情v5增补' not in s:
        first,rest=s.split('\n',1);p.write_text(first+'\n\n'+change+rest.lstrip('\n'),encoding='utf-8')
p=R/'docs/模组清单.md';s=p.read_text(encoding='utf-8')
change='> **2026-10-18准备增量：** Legendary Bosses 0.6.1-beta（Forge1.20.1，GeckoLib4.4+）元数据与原始JAR已准备，用户仍在游戏，未安装到实例；不得提前把母本226/test229的旧快照各加1。具体依赖、SHA、四Boss战位与190键简中见[审查记录](Legendary_Bosses_审查与入包_2026-10-18.md)。当前增量JSON不冒充旧六表已全量刷新。\n\n'
if '2026-10-18准备增量' not in s:
    first,rest=s.split('\n',1);p.write_text(first+'\n\n'+change+rest.lstrip('\n'),encoding='utf-8')
p=R/'docs/交接启动词_通用规则.md';s=p.read_text(encoding='utf-8');change='\n\n2026-10-18用户新增Legendary Bosses：以《剧情v5_旧世四传说与造界者》及《Legendary_Bosses_审查与入包_2026-10-18》为当前入口。四新关口与汉化已写仓库，尚未安装；用户仍在游戏，明确先完成文件，不热覆盖。保留旧E6任务/领奖ID。不要误跑从v5重建的rewrite_questbook_v6.py覆盖新扩展；后续从当前源修改，完整重现需先对比本轮快照。模型与动画资源存在不等于EF兼容通过；Null图腾反制与恢复等实战交用户验收。\n'
if '2026-10-18用户新增Legendary Bosses' not in s:p.write_text(s.rstrip()+change,encoding='utf-8')
print('Updated story, task and install-state entry points; no instance write')
