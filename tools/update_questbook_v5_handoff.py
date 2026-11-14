"""Point current documentation at the replacement of the rejected draft."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
note=('> **2026-10-17用户验收退回后重建：** 上一版234项被用户指出粗糙，已重新精读指定三包63章，'
      '重建主线／Boss情报、四职业、军工与全军械档案。当前仓库95章2286项，覆盖2673件定义清单装备；'
      '50个战位有独立介绍，图标改为对应实际物品徽记，大圣保留16像素正面图，新增低透明度背景分区。'
      '详见[第5版精读与完整重建](FTB任务v5_三包精读与完整重建_2026-10-17.md)。'
      '新版尚未写入实例，游戏中的上一版不代表本轮结果；游戏验收仍由用户负责。')
for rel in ['docs/HANDOVER.md','docs/README.md','docs/开发计划_执行状态.md','docs/资料库总索引.md','docs/FTB任务重置_v2.md']:
    p=ROOT/rel;s=p.read_text(encoding='utf-8')
    if note not in s:
        title,tail=s.split('\n',1);p.write_text(title+'\n\n'+note+'\n'+tail,encoding='utf-8')
p=ROOT/'docs/交接启动词_通用规则.md';s=p.read_text(encoding='utf-8')
append='\n本轮用户退回234节点草稿并要求学习龙之冒险、Immersive Fight、DUEL OF THE END后完整重写。当前入口为《FTB任务v5_三包精读与完整重建_2026-10-17》；装备图鉴按新要求完整展开，覆盖清单与排除原因须可审查，不沿用旧“绝不逐件开任务”限制去缩减本轮范围。完整图鉴仍为可选，不增加主线毕业门槛，不重跑既定收藏家标签。新版任务未安装前不得把用户正在看的旧版当成新结果。\n'
if append not in s:p.write_text(s+append,encoding='utf-8')
p=ROOT/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('**项目仍在制作中。FTB已按剧情v4重写为17章234项；序章有单人功能证据，新全书由用户接手测试。母巢、大圣及部分军工能力尚未开放。** 交付与边界见[全书重写记录](docs/FTB任务v4_全书重写与图标_2026-10-17.md)。',
 '**项目仍在制作中。用户退回上一版后，任务书已重新研究三包并重建为95章2286项，包含主线、四职业与完整可选军械档案。新版仅落仓库，游戏验收由用户负责；母巢、大圣及部分军工能力仍未开放。** 见[第5版重建记录](docs/FTB任务v5_三包精读与完整重建_2026-10-17.md)。')
s=s.replace('剧情v4全书已重写并生成，17章234项；仓库及独立更新包已更新，新全书游戏验收由用户负责','第5版重建为95章2286项，含2673件定义清单装备；新版仓库及更新包已生成，尚未安装，游戏验收由用户负责')
s=s.replace('剧情v4迁移、图标与独立更新包见[全书重写记录](docs/FTB任务v4_全书重写与图标_2026-10-17.md)','剧情v4的第5版任务书、图标、档案与更新包见[重建记录](docs/FTB任务v5_三包精读与完整重建_2026-10-17.md)')
p.write_text(s,encoding='utf-8')
coverage=json.loads((ROOT/'docs/data/questbook_v5_coverage.json').read_text(encoding='utf-8'))
(ROOT/'docs/FTB任务v5_图标清单.json').write_text(json.dumps(dict(
    version=5,boss_icons=coverage['boss_icons'],equipment_rule='全部物品检测以第一目标真实ItemStack作图标；护甲为实际部件，保留原生模型',
    background='minecraft:textures/block/deepslate_tiles.png，alpha34，order-100',
    portrait_limit='大圣有真实正面16px图；其余为实际物品徽记，不是新制作的Boss正面肖像'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated current handoff and explicit icon manifest.')
