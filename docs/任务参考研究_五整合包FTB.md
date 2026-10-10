# 五个整合包的 FTB 任务实证研究

> 采样2026-10-09，交付复核2026-10-10；供《任务设计总稿_v1.md》引用。只读研究，未启动游戏、未修改参考包、母本、test 或任务 SNBT。统计为磁盘资源，不表示这些任务在各包中全部可完成。

> 10-10主线深化补充见[全模组与战斗筛选](主线深化研究_全模组与战斗筛选.md)§二～七：215jar重扫、DOTE真实战斗依赖、SLU动作引用同质风险与特殊AI候选。总稿已修为v1.1；本文保留参考任务原始实证，不将旧固定Boss三连当已批准流程。

## 一、研究范围与证据口径

参考实例根目录：`C:\PCL 正式版 2.8.13\.minecraft\versions`。各包任务根目录均为其下的 `config/ftbquests/quests/`。本轮逐文件读取并解析全部章节、奖励表和元数据：**308 份 SNBT，100 章，6,960 个任务，198 份奖励表；解析失败 0**。任务数按 `quests` 数组计，包含隐藏、说明、商店任务，不能当作必做任务数。重复数按实际字段 `can_repeat:true` 计，不按名称“日课”推定。

| 证据代号／实例名 | 章节 | 任务 | 奖励表 | 可重复任务 | 设计观察的取样范围 |
|---|---:|---:|---:|---:|---|
| R-龙／龙之冒险：新征程v2.4a | 14 | 1,719 | 64 | 156 | 主线、挑战、结构、装备、饰品、商店及其奖励定义 |
| R-远／远梦之棺 | 8 | 232 | 1 | 1 | 全章依赖；武器、装备、重要物品与轮回章 |
| R-CTI／Construct Technological Innovation | 29 | 3,362 | 92 | 50 | 匠魂入门、材料、工具、强化、饰品及章组 |
| R-DOTE／DUEL OF THE END | 26 | 741 | 18 | 42 | 基础、武器、盔甲饰品、技能与探索章 |
| R-IF／Immersive Fight 4.2.9 | 23 | 906 | 23 | 149 | 基础教学、武器派生、技能书、饰品、Boss 清单 |

以上计数均已按同一字段复核。MC/EF 跨版本边界继续服从《武器线与匠魂节奏_参考综合.md》卷首、§七：学习组织方式，不拷 ID、API、材料温度或门禁。

### 1.1 本包与 GitHub 对照

- GitHub 仓库确认为公开的 [233zsq/symbiote-vs-spore](https://github.com/233zsq/symbiote-vs-spore)，默认分支 main。本轮读取 GitHub API 最近五次提交；远端首条与本地 HEAD 均为 [ec2ecf0](https://github.com/233zsq/symbiote-vs-spore/commit/ec2ecf0a0f891cb14ded8aaf8f7d0dc04dd83874)，其前为文档整理提交 4978dc5。未执行 fetch、pull、commit 或 push。
- 在该提交固定引用读取了 [任务桥源码](https://github.com/233zsq/symbiote-vs-spore/blob/ec2ecf0a0f891cb14ded8aaf8f7d0dc04dd83874/kubejs/server_scripts/svs_quests_bridge.js)。它仍含占位 ID；围城/火种只有配置入口，实际轮询只处理共生体阶段，不能把“有键名”当作已经接通。其阶段精确相等、缓存未按玩家隔离、先写防重标记等问题仍由执行侧处理。依据：《任务线实装核对.md》卷首、《开发计划_执行状态.md》§四/五及远端源码。
- test 实际读取 **19 章、344 任务**。awakening 9、stage1_departure 7、preface 16，与 M2 对账一致；souls_codex 43、weapon_guide 59，超过新框架每章≤40的要求，须在用户编辑器重组。其余旧章不因存在就视为完成重写。依据：test 的章节 SNBT；《任务线实装核对.md》§一；《任务线框架规格书_v1.md》§1.3。

## 二、五包中值得采用的做法

### 2.1 龙之冒险：任务告诉玩家“下一件有用的事”

**实证。** `chapters/716C86B2D2A52F2A.snbt` 主线 502 节点。根任务 `74F517C5F28546AD` 后，`0DA5D4A00063EC79` 讲前期回复来源并补基础防具；`200B91F344A6097B` 解释探索与下矿的选择。`chapters/a_5.snbt` 饰品章 135 节点，诸如 `5E13F8317BAA5E90` 把来源写在副标题；`chapters/boss.snbt` 68 节点，说明任务 `1E884F9F3E93C8CC` 明确 Boss 图鉴只负责顺序/定位，主要奖励去主线领。以上是该包自己的机制，不能把七咒、特殊回复和特供武器套到 SvS。

**采用建议。** SvS 每个作业完成后给下一步会用到的材料；“去哪找、为什么值得做”直接写在提示和副标题。攻略页与主线共用一个完成/奖励来源，图鉴只做导航。将大图的阅读优势缩成≤40节点章节。（提案；依据：R-龙上述任务；框架§1.1/1.3。）

**不采用。** 502 节点主线、135 饰品逐件集齐及该包货币；挑战章 `17D9CB919F284685.snbt` 的重复多杀 Boss 目标不进入 SvS 必做主线。用户本次已选择“每阶段少数必打，其余可选”。

### 2.2 CTI：先给能操作的设备，再讲材料系统

**实证。** `chapters/mainchapter0.snbt`：`388FD9256DBF317D` 收基础物资后奖励部件制造台、工匠站与模具；`26CAE8F089150BDB` 分页解释部件台槽位；`05A59435093F9730` 介绍组装，任务物品设置 `match_nbt:false`。`chapters/toolcollection.snbt` 的 `36D970A6B8A24E1C` 同样不要求样例工具的材质 NBT。当前磁盘 `curiocollection.snbt` 实际是 **244 节点**，旧研究中的“246种”不作为本轮计数。

**采用建议。** 匠魂作业按“炉子可运行→铸锭→部件→成品→升级”递进；材料等级用独立注册材料证明，工具外观/耐久不作精确 NBT 门槛。困难术语可分页，第一屏只给当前操作。（提案；依据：R-CTI上述文件；框架§3.2。）

**不采用。** CTI 的科技/魔法全家桶、海量全收集、特供材料和其 MC1.19.2 温度数值。本包材料需读本包 jar；已核实本包钴熔点950、玛玉灵1200，不能把钴假装成必须升级燃料的材料。（见本文§四 E-匠。）

### 2.3 IF：派生关系比强度榜有用

**实证。** `chapters/51686875CAC7512B.snbt` 武器派生树118节点：`77A3C29A355D3C95`→`78F04A88EB6C1C2B` 展示符文武器派生并奖励镶嵌资源。`chapters/669F16D5421BFE1C.snbt` 技能书兑换67节点，`77916C8367FD96D1` 等设置 `can_repeat:true`。`chapters/6943FD9046CEB8EE.snbt` 饰品兑换31节点，`213B122315EAA536` 用券兑换猎人腰带且奖励 `team_reward:false`。`chapters/129869D15D3F7CF8.snbt` 的 `19CBA384DDE48548` 用可点击文本跨章指向设置页。

**采用建议。** 收藏家按“普通锻造→符文升级→Boss材料→魂系合成”分带；名品奖励补下一步材料。职业饰品提供功能与槽位说明；教学链接到本包真实章节。（提案；依据：R-IF上述节点；框架§3.1。）

**边界。** IF 的任务商店不能成为 SvS 第三个 EF 技能书渠道；技能书仍只走村民与 DailyBoss。`team_reward:false` 只证明参考包有个人领取设置，不能单独证明本包队伍拆分/重建后的防重复行为。重复任务也不自动等于“24小时重置”。

### 2.4 DOTE：来源、用途和风险一起教

**实证。** `chapters/400FD1D97704A941.snbt` 技能指南33节点，根 `5EFDFEF722E0E839` 说明颜色含义，并明确右侧图示不是免费教学奖励。`chapters/7074902D721B9745.snbt` 武器63节点，类型锚点采用 OR 物品过滤。`chapters/3061409469F4E28D.snbt` 护甲34节点，`598073173493EB5C` 按套装四部件组织。其技能来源对应职业的具体列表见《武器线与匠魂节奏_参考综合.md》§3.3。

**采用建议。** 每种作战方案解释一项用途和一项代价；护甲按“套装/用途”说明。技能指南每类合并成一页，列本包实际来源；不按书逐件制造大量领奖节点。（提案；依据：R-DOTE上述文件；框架§1.1/1.3。）

**不采用。** 旧 EF18 的技能 ID、数值上限、饰品锻造炉、维度证、原版改动与 Boss 门禁。本包不恢复下界章，不借颜色包装成数值 Tier 榜。

### 2.5 远梦：来源分带清楚，但隐藏总闸应谨慎

**实证。** `chapters/wu_qi.snbt` 武器71节点、`zhuang_bei.snbt` 装备12节点（含入口，旧报告“11”为入口之外条目）。`chapters/cui_ling.snbt` 的根 `721C4011155C1854` 是隐藏进度任务，下接大量系统项；`chapters/lun_hui.snbt` 的 `048CB00656EE47EF` 为隐藏入口，`3825BFB29CCBF7E9` 文案列 Boss 顺序。文本大量使用翻译键，原 SNBT 的键名不是空文案。

**采用建议。** 收藏家各阶段按取得路径分带，末期展示毕业直发的目标；锁定后段保持可见，并说明解锁条件，减少玩家找不到下一步的情况。（提案；依据：R-远上述文件；框架§1.4。）

**不采用。** 武器解放制、隐形总闸导致整页消失、特供人形 Boss/维度/票据 ID。SvS 的图鉴开放查阅、职业进度分段锁定，两者需区分。

## 三、本包旧任务的实际迁移面

下表不是执行授权。用户在编辑器逐项迁移，保留有用的真实 ID；先有新去向，再关闭重复奖励。依据：test 全19章SNBT；框架§〇/1.3；《任务线实装核对.md》§一。

| 当前章／节点数 | 设计中的去向 |
|---|---|
| preface／16 | M2方案留11、移5；难度入口保留，说明页更新本包实际渠道 |
| awakening／9 | 现有序章稿与M2唯一清单；本文不新增第二套序章 |
| stage1_departure／7 | M2删2迁4留1；新阶段Ⅰ主链仍按原稿审定 |
| symbiote_bond／12 | 共生使；改掉未注册能力键、强迫特定菌株与错误狩猎作业 |
| tinkers_workshop／27 | 锻造师；核实旧 stencil_table、fantastic_foundry 等 ID 后清掉无效目标 |
| dragons_guide／12 | 狩龙人作业＋开放圣龙资料页，避免重复发毕业奖 |
| souls_codex／43 | Ⅳ必打短链＋可选讨伐索引；不把全43条挂主线收官 |
| stage5_endgame／15 | 灾变8项迁Ⅲ；终局重新承接母巢；材料与收藏迁对应职业 |
| stage4_calamity／3、calamity_front／15 | Ⅲ真菌防线及Ⅳ母巢；旧Incoming等自报事件不冒充已接桥 |
| sword_soaring／12 | 可选玩法资料；不占四阶段主线，不新增第五职业 |
| exploration／6、souls_structures／14、structure_guide／19 | 开放结构资料，主线节点链接到相应条目；不改结构密度 |
| boss_guide／35 | 开放讨伐索引；奖励归所属主线/委托，图鉴不重复发 |
| weapon_guide／59 | 收藏家聚合＋24个名品；余下资料按来源分页/分章≤40 |
| arcane_guide／14、kitchen_guide／10 | 开放辅助指南；法术只列禁用清单允许项，口粮教学短化 |

## 四、新设计使用的本包静态证据

所有 jar 路径均在 `E:\SvS_整合包_副本\mods\`。下面是静态资源或字节码，不是本轮游戏验收。设计稿引用 E-代号可回溯具体文件。

### E-二轮：Jerotes Village 1.1.5.20

`jerotesvillage-1.20.1-1.1.5.20.jar`：

- `data/jerotesvillage/dimension/second_round_world.json`：维度存在。
- `advancements/second_round_world_key.json`＝持有钥匙；`second_round_world_come.json`＝切入该维度；`three_saints.json`＝分别击杀二轮僵尸/骷髅/蜘蛛；`round_trip_freely.json`＝持有传送石。最后一项**不证明已经成功往返**。
- `advancements/overlord.json`＝`minecraft:player_killed_entity`，目标 `jerotesvillage:sediment_lord`；其掉落表 `loot_tables/entities/sediment_lord.json` 含袍布。`worldgen/structure/sediment_catacombs.json` 及同名地图tag存在；**尚未把结构内领主的具体刷出/召唤路径验通**。
- 追加核对维度归属：`tags/worldgen/biome/has_structure/sediment_catacombs.json`指向bright_grassland/bitter_cold/sand_beach，三者都列在二轮维度biome_source中；zh_cn结构名标为“[二轮世界]沉降墓穴(BOSS)”。因此它具有二轮代表战的静态依据，不是把主世界Jerotes大世界Boss误塞入主线。`block/ResurrectSediment/SedimentLordCoffin.class`有SEDIMENT_LORD创建/生成及成功后换空棺逻辑；具体触发、自然棺出现与失败重试仍待游戏验证，不把字节码调用等同于已验通。
- 原生定位链：`recipes/sediment_catacombs_map_craft.json`＝腐肉＋second_rounder_map→sediment_catacombs_map；`loot_tables/gameplay/jerotesvillage_magic_map/sediment_catacombs_map.json`生成以该结构tag为destination的探索地图。基础二轮地图有MerorMerchantEntity/WildernessGiantHunterEntity类引用及mapmaker掉落/guide_gift等资源引用，但本轮尚未核商人必现条件/价格及地图实际使用行为；玩家提示只写已证配方与来源线索，不许诺任一村民必卖。
- 钥匙配方 `recipes/second_round_world_key_craft.json` 使用村民金属、石英或闪长岩、末影之眼或珍珠；传送石 `second_round_world_teleport_stone_smith.json` 用二轮宝石＋对应技艺模板＋末影之眼。不改这些配方。
- 钥匙原生zh_cn说明：右键村民金属块转为二轮世界方块；在主世界，对二轮世界方块组成的门框使用以激活。框架尺寸和本包实际往返仍待测，不能把“探索指南（未完成）”当现成完整攻略。
- `lang/zh_cn.json` 把二轮傀儡描述为“一点都没完成”；不选它做本包通关唯一必打。沉降领主作为“二轮制霸”代表目标是**本包设计提案**，不是模组官方结局断言。

### E-龙：Saints Dragons 0.9.6

`saintsdragons-0.9.6+forge-1.20.1.jar`：

- `data/saintsdragons/advancements/tame_<龙种>.json` 八个驯服进度存在；`encounter_dragon`、驯服、孵化等使用 `minecraft:impossible`，意味着要由程序授予，不能只凭文件名断定有效。
- 本轮 `javap -p -c` 读取 `com.leon.saintsdragons.server.entity.dragons.cindervane.handlers.CindervaneInteractionHandler`，发现对 `tame_cindervane` 的进度管理器查询和 `PlayerAdvancements` 授予调用；雷翼交互类也含对应资源字符串。**烬羽已有授予调用的静态证据，八种实测仍待做**。
- `acquire_dragon_scale.json` 为原生库存检测，接受七种鳞；`dragonlord_armor_set.json` 检测四件龙领主护甲。拥有龙鳞不等于亲自驯服，拥有装备也不等于穿戴试飞。
- 实际四个结构资源为 `ignivorus_roost`、`varasuchus_roost`、`ivy_house`、`draconian_nucleus`。因此框架“4个龙巢”的数量不能直接解释成四种天然巢穴；仅前两项名字为 roost。资料页按真实生态分别介绍，不改生成。

### E-灾变：Cataclysm 3.31

`L_Enders_Cataclysm-3.31.jar` 的 `data/cataclysm/advancements/kill_monstrosity / kill_harbinger / kill_ender_guardian / kill_ignis / kill_leviathan / kill_remnant / kill_maledictus / kill_scylla.json` 均明确为对应实体的玩家击杀；可优先用原生进度，或编辑器 kill 任务。

八结构候选映射：soul_black_smith→下界合金巨兽；ancient_factory→先驱者；ruined_citadel→末影守卫；burning_arena→伊格尼斯；sunken_city→利维坦；cursed_pyramid→远古遗骸；frosted_prison→被诅咒者；acropolis→斯库拉。结构资源与Boss实体均存在；**逐结构实际遇敌/激活路径仍待游戏确认**。白名单不保证近点生成，也不保证阡陌道路已经逐座接通。（结构表§三；HANDOVER§四10-03。）

掉落资源证明：巨兽→infernal_forge/monstrous_horn；守卫→gauntlet_of_guard；先驱者→witherite_block；伊格尼斯→ignitium_ingot；被诅咒者→cursium_ingot。`recipes/meat_shredder.json`、`wither_assault_shoulder_weapon.json`、`soul_render.json`、`the_incinerator.json` 证明后四件是**材料合成**，不把它们全写成Boss直接掉落。

### E-魂：SLU 当前 remade jar

`slu_9990.3.1.20.1-remade.jar`：`assets/slu/lang/en_us.json` 含 `boss_gundyr`、`boss_artorias`、`boss_gael`、`boss_soul_of_cinder`、`boss_minecraft_lord` 等实体名。相应猎杀进度多为 `minecraft:impossible`，本轮未证明其程序授予链；设计优先用本包实际实体的 kill/场次桥，不依赖这些进度冒充击杀。

`data/slu/recipes/{gundyr_axespear,margit_wand,moonlight_sword,soul_of_cinder_sword,cinder_king_greatsword,grand_trial_sword}_recipe.json` 均存在。三魂交易卖的是基础魂；月光剑配方明确要求 `knight_soul_3`，不能写“48币直接换一把月光剑”。Boss 掉落大多不能由本轮找到的少数loot JSON解释，须继续核原生流程/实际掉落，不能从魂名字反推其来源已验通。

### E-真菌：Spore 2.2.0j / Inquisition 3.2

`spore_1.20.1_2.2.0j.jar` 的 `data/spore/advancements/{mound,proto,howitzer}.json` 检测攻击/被攻击，**不是击杀**；母巢成功必须另判。`spore_inquisition_3.2.jar` 的 `data/inqui/advancements/ending.json` 为 impossible；`a_1～a_7` 不能凭叙事标题当本包完整结局自动检测。

现有 `kubejs/server_scripts/siege.js` 是村庄围城，怪池包括 inf_human/inf_villager，精英有 brute/knight 等；不等于已有“远征母巢三波事件”。新攻坚事件只在稿中提出，必须单独获批、实装和验收。不新增限伤。

### E-匠：TConstruct 3.12.0.220

`TConstruct-1.20.1-3.12.0.220.jar`：`data/tconstruct/recipes/smeltery/casting/seared/smeltery_controller.json` 要在浇铸盆向冶炼炉砖浇铜（360）；`recipes/tables/part_builder.json` 与 `tinker_station.json` 存在，旧 `stencil_table` 不可直接沿用。钴/玛玉灵的 `smeltery/melting/metal/<材料>/ingot.json` 分别为950/1200。礼包只有“32焦黑砖＋工作台”不足以证明新玩家已有一座可工作的冶炼炉；控制器、燃料容器、排液口/龙头、浇铸台和模具链都需交代。

### E-藏：Simply Swords 与收藏标签

`simplyswords-forge-1.56.0-1.20.1.jar` 的 `data/simplyswords/recipes/iron_<longsword,spear,rapier,katana,twinblade,glaive>.json` 有六种铁武器配方；对应 `runic_*.json` 使用下界合金同型底材＋符文石板＋钻石。故符文组放中后段收藏，不当开局奖励。

`tools/gen_collect_tags.py`、`kubejs/server_scripts/svs_collect_tags.js` 及框架§四为聚合标签来源；t1运行时257与生成268差11仍待裁决，不在本轮重生成。指定名品有配方不代表必属预期t档：名品固定ID检测与聚合标签独立，进入编辑器前再核运行时存在与EF手感。

### E-饰／E-共／E-币

- 四毕业饰品候选：`artifacts:universal_attractor`、`artifacts:obsidian_skull`、`relics:hunter_belt`、`artifacts:cross_necklace`。Artifacts9.5.19的 `data/artifacts/tags/items/slot/belt.json`、`slot/necklace.json` 与 Relics0.8.0.7的 `data/curios/tags/items/belt.json` 有槽位依据。它们仍可能原生获取，不宣称独占；四件彼此不同、改名lore不新增属性。具体功能、槽位冲突与其他保证奖励重复性要游戏检查。
- 共生体四阶、个人档案、狩猎状态与红利：`kubejs/server_scripts/symbiote_counter.js`；实际可按键与硬编码边界：《Symbiote配置调频设计.md》§五。Bond与Trust不混称，饥饿条回复不冒称共生体内部hunger已回填；未注册五键不布置必做按键作业。
- 六笔现有交易：`kubejs/startup_scripts/villager_trades.js`；必现补挂 `server_scripts/trade_guarantee.js`。目前没有EF技能书交易，书的职业/价目仍待M2批注。指南针使用范围/费用见 `server_scripts/explorers_compass.js` 与母本 `config/explorerscompass-common.toml`；二轮/下界/末地不能靠这把罗盘随意定位，主线黑名单也不能让玩家搜索。

## 五、研究到设计的取舍

1. 主线使用少数代表战斗，装备材料、竞技场与四职业提供多种准备路线。用户本次已选该方向；具体Boss名单仍以稿件批注为准。
2. 第一屏只放一个动作目标；复杂系统提示分页，资料页不重复收大额奖励。来源：R-CTI、R-龙、R-DOTE；框架§1.1。
3. 避免“学会格挡”先于可取得格挡能力、“启动祭坛”即通关、“攻击母巢”即陷落。检测必须匹配作业；动作教学允许明确自报，关键胜利不自报。来源：E-真菌、M2.3#5、现序章稿、战斗手感基准。
4. 让可选内容有实用收益，但不要求完成四职业才能结局；剧情收官与职业毕业独立。来源：用户本次选项；框架§〇/1.4。
5. 未证明的可达路径、随机券/母巢事件、日课新增奖励、技能书交易都显式标“待实装/待测”，不能靠写进任务说明宣布它们存在。来源：HANDOVER§二/五；任务文档工作原则。

## 六、校验记录

统计脚本只在标准输入执行，未写入仓库或实例；SNBT没有改写。各包全部SNBT读取解析通过，R-IF可重复任务复核为149。研究不以参考包的超大章节或历史数值为本包玩法裁决。

## 七、补充研究：Boss 流程与收官方式

用户反馈：**SLU薪王化身的模型和动作不足以承担本包终局**；撤回该候选，不把原作地位等同于本模组的呈现质量。以下仍是只读任务/资源证据，未做五包或本包的游戏战斗验收。（依据：本次用户答复；任务文档“原则一/四”。）

| 参考包 | 可定位的实际证据 | 对本包有用的取舍 |
|---|---|---|
| DOTE | `chapters/331563382650DECB.snbt`：`71F5E866BCCEB9A9`进入终焉场→`5174127C13F71B7C`流光（击杀gazeabysser＋核心物品）→`10CACCAB1428EA4E`战后材料；其后`130907FFE3A9607F`明确“支线boss，非必打”。`l.snbt`的圣堂入口也明确非主线；`4A5BC2F53DA2FB69.snbt`的古老远征是可选刷物资Boss连战 | 入口准备、真正胜利、战后奖励分成不同节点；最终战后再放高难挑战，不用“更难的隐藏Boss”否定已完成结局。参考包的单人维度、专用Boss和Gateways不能搬入本包 |
| 龙之冒险 | `chapters/716C86B2D2A52F2A.snbt`：`538ECE438A51DCBC`之后开材料补领`0C59659BA85321D1`、主世界使徒`7E7BF75561272485`及圣堂线`0D7364F8F80E59BE`；后二者同时作为“最终圣战”`70D5EE72D67B0EB4`前置。文案要求主世界形态后再挑战下界完全体，列召唤材料、失败风险、战后再召来源；最终任务本身检测战利品，不应误称它是严格击杀桥 | 决战前有铺垫、准备清单和可恢复召唤资源；失败能再挑战。SvS不照抄13种材料清单、属性回归/限伤或抢饰品机制，也不把无该模组的使徒当现有候选 |
| 远梦 | `lun_hui.snbt`八个人形Boss任务共同依赖隐藏入口`048CB00656EE47EF`；`3825BFB29CCBF7E9`文案给出“先驱者→斯库拉→巨兽→被诅咒者→远古遗骸→末影守卫→伊格尼斯→利维坦”。Boss节点之间没有对应的逐项击杀依赖。`shen_mo.snbt`灾变诸Boss也以共同入口展开 | 可以借鉴短推荐顺序、不同战斗形式，但必须把“建议顺序”与任务硬依赖分开；不能据此断言利维坦是该包唯一终局或最强者，更不能把其人形改版当本包原生灾变模型 |
| IF | `2E5D94068E13BBEE.snbt`灾变章的伊格尼斯`66789CB9CBAFBB7F`依赖焰魔`26499A1DD2086A84`；其他灾变Boss不是一条八连硬链。`boss_2.snbt`52节点为无依赖Boss索引，含不朽者`1B72023B4D5100E5`与无名守卫`687D2E2912A2CC2F` | Boss图鉴给定位和备战，主线只挑代表战；不能把图鉴最后一个图标当剧情最终Boss |
| CTI | `boss.snbt`70节点多为图鉴/局部前置；伊格尼斯`4090B4DEDD8A3726`依赖焰魔`202C2E9501CF8B69`。`mainchapter4.snbt`最终章26节点，“万物之终”`551214D011551305`承接无尽材料成果；“击杀全部灾变boss”`61643E8D7F91E6F7`是独立checkmark，不能当严格全杀检测 | 收官应回顾一路所学，之后保留自由目标。CTI的材料毕业符合其主题；SvS应把这种成果感转为母巢反推、最终战和武器直发，不接入科技长链 |

**流程建议（推论，待批）：** 少数代表战→魂系准备短链→母巢攻坚→单场最终决战→武器毕业/结局→可选高难与日课。若把某一灾变Boss留作最终战，Ⅲ章只保留其资料入口，避免先给一次完成奖励、结局又要求同一Boss再刷一次。任务顺序仅引导，不改实体生成或提前挑战权利。（依据：上表；框架§二；用户“少数必打，其余可选”答复；原版/worldgen边界。）

### 7.1 本包终局候选的资源证据与边界

本轮只读母本 `mods/L_Enders_Cataclysm-3.31.jar`，用jar目录和javap核对：

- **被诅咒者 `cataclysm:maledictus`**：`client/model/entity/Maledictus_Model.class`；四组`Maledictus_*Animation.class`；实体`InternalAnimationMonster/IABossMonsters/Maledictus/Maledictus_Entity.class`具有弓射/飞射、后撤冲刺、连击、戟击、抓取成功/失败等动画状态及`WEAPON`、`RAGE`字段。可作为偏近战节奏的候选；这些类与字段证明有相应资源，**不证明在本包中读招清楚、性能合格或比其他Boss更强**。
- **斯库拉 `cataclysm:scylla`**：`Scylla_Model.class`及`Scylla_Normal/Lightning/Projectile_Animation.class`；实体有`PHASE`、挥击、锚投掷/牵拉、水/雷长枪、闪电爆发、连跳等状态与阶段切换目标类。可作为偏大场面与空间变化的候选；空中状态还涉及本包“飞行Boss可受远程增伤”的既定规则，不能偷偷取消它来抬难度。
- **伊格尼斯 `cataclysm:ignis`**：实体`AnimationMonster/BossMonsters/Ignis_Entity.class`有`PHASE_2/PHASE_3`、盾击、反击、连击、跳砸等字段。总稿暂放Ⅲ章代表战；如用户更认可其呈现，可改留最终，Ⅲ章另选已有灾变代表战，避免重复强制击杀。
- `data/cataclysm/advancements/kill_maledictus.json`、`kill_scylla.json`、`kill_ignis.json`及对应实体掉落表存在；结构路径见E-灾变。完整到达、激活、死亡结算与队伍归因仍要实测。
- EEEAB的当前jar确有不朽者/无名守卫/境域守卫模型动画类；但《魔改设计决议.md》§二“Boss mod分流”把EEEAB放野外探索线。若选入强制终局，须明确列为**需用户重新裁决**，不能借“终局待定”绕开分流。DOTE专用Boss、龙之冒险使徒等不在当前215模组范围内，不安排新增模组。

候选验收建议：同等本包阶段装备、EF20.14.17、原生AI下，各观察完整招式循环、状态/阶段变化、近战与可用逃课路径；记录模型穿模、动作与伤害时机、场地干扰、死亡/重试、多人延迟感受。**不做纸面HP/DPS强度排名，不以动画类数量判优。**最终选谁、是否采用指定场次由用户批注；薪王化身已排除。（依据：任务文档理念8/工作原则四；HANDOVER§四；本次用户反馈。）
