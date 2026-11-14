"""One-time navigation update for questbook-v4 delivery; no game/instance access."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LINK='[FTB全书重写与图标记录](FTB任务v4_全书重写与图标_2026-10-17.md)'
NOTE=('> **2026-10-17全书重写交付：** 用户已将游戏测试接手，当前制作结果与待验边界见'+LINK+
      '。仓库任务已按剧情v4改为17章234项，含24场主线Boss、母巢／大圣事件和24席独立讨伐；'
      '44项物品检测使用对应物品图标，大圣16×16正面头像已出样，其余48张缺正面来源。'
      '18项未开放保持锁定。此次只落仓库与独立更新包，未同步母本/test；下方序章同步和FTB暂停按原日期阅读。')
for rel in ['docs/HANDOVER.md','docs/README.md','docs/资料库总索引.md','docs/FTB任务重置_v2.md']:
    p=ROOT/rel;s=p.read_text(encoding='utf-8')
    if NOTE not in s:
        title,tail=s.split('\n',1);p.write_text(title+'\n\n'+NOTE+'\n'+tail,encoding='utf-8')
p=ROOT/'docs/开发计划_执行状态.md';s=p.read_text(encoding='utf-8')
section=('## 当前切换：剧情v4全书重写，游戏验收交给用户（2026-10-17）\n\n'+NOTE+'\n\n'
         '前一轮已完成序章单人后端闭环；随后S01界面三选一、选择标准及重复点击不重领已有实际画面／日志证据。'
         '新全书只通过离线图与生成一致性检查，不能继承序章验收结论。'
         '当前可交付为`deliverables/FTB_v4_任务重写_待用户测试.zip`，安装、回退和剩余事件见上述记录。\n')
if section not in s:
    title,tail=s.split('\n',1);p.write_text(title+'\n\n'+section+'\n'+tail,encoding='utf-8')
p=ROOT/'docs/交接启动词_通用规则.md';s=p.read_text(encoding='utf-8')
old='FTB程序生成/校验已获授权，用户于2026-10-17恢复按方案制作并重写启读/序章；当前施工与实测范围见HANDOVER顶部及序章v4施工记录。旧暂停不覆盖新授权，也不据序章授权声称全线完成。既有源、ID映射、节点与pending状态须保留追溯；加载和引用检查不等于功能通过。'
new='FTB程序生成/校验已获授权；用户于2026-10-17要求按新世界观重写全书，并将游戏测试接手。当前交付与未开放事件见HANDOVER顶部及FTB任务v4全书记录。旧暂停不覆盖新授权；离线任务重写不等于全线游戏通过。Boss图标使用真实正面图缩为16×16并加深色描边，武器和材料节点使用对应物品图标。既有源、ID映射、节点与pending状态须保留追溯；不要继续自动操作客户端测试。'
if old in s:p.write_text(s.replace(old,new),encoding='utf-8')
p=ROOT/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('从村庄立足、远征与防卫，走向母巢反推。','建立军工要塞、掠夺诸王力量，走向母巢总攻与齐天终章。')
s=s.replace('**项目仍在制作中。v4启读与序章已落地并通过单人功能闭环，界面看样与联机仍有待验项；当前源码不代表已完成全流程游戏验收的发行版。** 进度见[序章施工与验收](docs/序章v4_施工与验收_2026-10-17.md)。',
 '**项目仍在制作中。FTB已按剧情v4重写为17章234项；序章有单人功能证据，新全书由用户接手测试。母巢、大圣及部分军工能力尚未开放。** 交付与边界见[全书重写记录](docs/FTB任务v4_全书重写与图标_2026-10-17.md)。')
s=s.replace('每阶段少数必打，其余作为可选讨伐。','主线24场核心Boss按阶段组织，另设24席独立讨伐。')
s=s.replace('主线四阶段为Ⅰ启程、Ⅱ磨砺、Ⅲ天灾防线、Ⅳ反推；序章负责入门。','主线四阶段为Ⅰ血肉筑基、Ⅱ疆域割据、Ⅲ劫火与神权、Ⅳ天基总攻与齐天终章；序章负责降临、融合与立旗。')
s=s.replace('这是已批设计方向，具体 Boss 名单及尚未实现的事件另有状态标注。终局先比较被诅咒者与斯库拉，尚未定选；SLU 薪王化身已排除为终局。依据：[框架](docs/任务线框架规格书_v1.md) §〇～三、[待裁决清单](docs/待裁决清单.md)、[Boss 研究](docs/主线深化研究_全模组与战斗筛选.md)。',
 '剧情与名单见[天外成王篇v4](docs/剧情重写_v4_天外成王篇.md)。咒翼灵骸为阶段Ⅲ压轴，斯库拉为独立讨伐，大圣残躯为两阶段最终试炼；任务页对尚未实现的入口、军工与事件保留开放状态提示。')
s=s.replace('| 任务系统 | v2为施工中间态，当前重写暂停；加载/引用审计通过，功能与全线未验 |',
 '| 任务系统 | 剧情v4全书已重写并生成，17章234项；仓库及独立更新包已更新，新全书游戏验收由用户负责 |')
s=s.replace('| 后期流程 | SLU 定点竞技场、母巢事件、随机召唤券与部分胜利检测仍需实现或验收 |',
 '| 后期流程 | 炮塔演练、劫火运用、天基打击、母巢事件、大圣终战与传承、SLU入口及循环券仍有未开放项 |')
s=s.replace('| 新模组与优化 | 在独立 `svs_lab` 试验；实验实例内容不整包回灌母本 |',
 '| 新模组与优化 | 按专项记录选择目标实例；用户游玩时不覆盖，独立测试内容不整包回灌母本 |')
s=s.replace('任务 v2 的可维护源、真实 ID 映射、构建与验收方法见 [FTB任务重置_v2](docs/FTB任务重置_v2.md)。',
 '任务源保留`docs/questbook_v2.json`工程名；剧情v4迁移、图标与独立更新包见[全书重写记录](docs/FTB任务v4_全书重写与图标_2026-10-17.md)。历史构建说明见 [FTB任务重置_v2](docs/FTB任务重置_v2.md)。')
p.write_text(s,encoding='utf-8')
print('Updated current navigation, execution log, stable handoff rules and root README.')
