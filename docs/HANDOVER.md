# Symbiote vs Spore 交接文档

更新：2026-10-31。当前工作以本页〇、三、七及用户最新指示为准；历史事实保留来源。

## 〇、30秒接手

用户于2026-10-31要求执行已确认计划。当前只完成本批六模组／前置入包、文档整理和后续计划；剧情与FTB施工未恢复。地图与EF由其他对话负责，不合并其源工作树或替它们施工。

- 本批状态和精确文件见[入包记录](模组9_入包与回退记录_2026-10-31.md)、[安装核对](data/模组9安装核对_2026-10-31.json)。母本234／test237个顶层JAR，E0；未启动游戏。
- Spawn暂存，不在启用索引；worldgen继续冻结。CS1.3.4已安装，不能据此认定EF适配；旧CELEpic未装。
- 任务基线为v6.1（源文件名仍是questbook_v2.json）。原任务、ID和领奖记录不因本轮安装改变；后续从[计划F0](剧情与FTB施工计划_2026-10-31.md)开始。
- [DeepSeek指南采纳对照](DeepSeek建议_采纳对照_2026-10-31.md)区分参考、旧口径和已采用部分；围城重构／地图／EF建议不自动成为本轮任务。
- 整理前的全部状态段在[旧HANDOVER快照](archive/2026-10-31_入口整理前/HANDOVER.md)；以下技术和历史裁决保留原日期，不把旧数量当作当前数量。

## 一、项目与主文档索引

| 文档 | 内容 |
|---|---|
| `docs/任务文档.txt` | 设计理念 + 工作原则（最高优先级） |
| `docs/魔改设计决议.md` | 机制定稿（变更记录节效力最高，变更记录已补10-07执行结果） |
| `docs/任务线框架规格书_v1.md` | 任务线重写权威（四职业支线 + 四段式写作规范 + 检测模式三选一，2026-10-03 定稿） |
| `docs/整合包结构表.md` | 10-12当前资源键索引＋9-30历史样本；密度裁决保留，worldgen冻结 |
| `docs/武器线与匠魂节奏_参考综合.md` | 四参考包拆包结论（任务线重写用） |
| `docs/实例配置说明.md` | 当前落点与生效方式；P8′仍等spark数据和裁决 |
| `docs/archive/2026-10-09_整理前/规格书_修复批_0926.md` | 历史修复规格，须连同同目录补正阅读 |
| `docs/开源协议审查.md` | 协议合规；改动 mod 清单必须同步登记 |
| `docs/开发计划_v2.md`（2026-10-12 重写接替 v1；v1 留对照）＋`docs/开发计划_执行状态.md` | 现行开发计划与滚动执行登记 |
| `docs/任务线实装核对.md` | M2三件合并；8个批注点已于10-11批复，旧状态留史；阶段Ⅰ16可见/hidden方案20物理节点 |
| `docs/任务设计总稿_v1.md` | **任务设计总稿 v1.1（已批原则、具体条件另查）**：Ⅱ~Ⅳ 74 主线节点＋职业 79＋日课 8＝161 候选；替换旧 C/D/E 提案；Q01–Q14 批注入口 |
| `docs/主线深化研究_全模组与战斗筛选.md` | 215 jar 逐项角色索引 + Boss 四级看样门槛（模型动作→特效技能→可玩流程→数值）+ 夜临/WOC 替换提案 + 终焉决斗(DOTE)拆解 |
| `docs/任务参考研究_五整合包FTB.md` | 五参考包 FTB 任务结构研究（总稿设计依据之一） |
| `docs/刀光与新增模组6_优化合入综合审查.md` | 刀光资源核查 + 15 新 jar 逐项 + B0–B6 分批 + 5 项待裁决（2026-10-11，待批） |
| `docs/Rapid_Optimization_合入评估与执行交接.md` | Rapid 优化包 29 模组逐项与“择项借用”结论（2026-10-10） |
| `docs/EF适配现状与动画管线.md` | EF 适配三层数据驱动 + 自定义动画/视频动捕管线（2026-10-07 调查） |
| `docs/数据与采样说明.md` | 10-12离线更新的六表/目录/统一JSON源；历史属性与现版静态证据分列；完整入口：资料库总索引.md |
| `docs/剧情重写_v4_天外成王篇.md` | 10-17用户更新的最新叙事：天外成王/军工要塞/劫火天基/大圣终章；实现边界见接手核对，FTB暂停 |
| `docs/剧情重写_v2_借火者之路.md` | 前稿与只读快照证据；旧二轮必经、部分分流与配额问题已由用户新指示和v3替代，不继续照旧施工 |
| `docs/README.md`／`验收与风险登记.md` | 制作导航、未决边界与历史资料去向 |

## 二、目录布局与同步铁律（勿乱）

| 位置 | 角色 |
|---|---|
| `E:\SvS_整合包_副本` | 整合包母本，正式出包与同步目标；日常开发落点按顶部最新工作流 |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\test` | **开发/游玩实例**（2026-10-06 由 test20.zip 导入建立；2026-10-15 计 226 jar）：**须 JDK21 启动**（voxy 换装）；launch_test4.py 默认 test |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\svs_lab` | **实验沙箱**（2026-10-11 建；10-15 计 230 jar）：模组6/7/8 与原生 voxy 都曾在此先行试验；批八起工作流直落 test，lab 已退出工作流（保留作沙箱，**另存旧 test 世界 10-12 快照——误删恢复用**）；**绝不同步回母本** |
| ~~test4~~ | **已由用户删除**（2026-10-11 前清理；证据区核查无归档留痕，如需找回查回收站） |
| `E:\mcmp` | Git 仓库（GitHub 233zsq/symbiote-vs-spore） |
| `E:\mcmp_test` | 工具区：launch_test4.py（默认test，支持`--world`/`--version`）、pack_mcbbs.py、dist/testN.zip、i18n_work/、错误报告/、dl/ |

**铁律**：
1. 获准实施后，日常开发直落 **test**；正式同步须逐文件核对并收敛母本、test、仓库。先比较与备份，禁止按方向批量覆盖用户差异。本轮只改资料。
2. **数据包类覆盖（结构 JSON/标签/biome_modifier）一律走 `config/openloader/data/svs/data/`**——`kubejs/data/` 在本环境**不是数据包**（实证见第五节教训 10）。
3. 打包：`python E:\mcmp_test\pack_mcbbs.py testN`（MCBBS 格式），打完核对 overrides 内脚本与 jar 版本；**testN.zip 降级为里程碑/交付验证用途**（验证打包通道不漏文件），日常验证全走 test 实例（永远最新）。
4. 并发会话共用仓库：commit 前 `git log --oneline -5`，**只 add 自己改过的文件路径**（曾误扫入他人文件）。
5. **动 test/母本前先查 java**：用户名 `Ultraman_0`＝用户实例（勿动）、`Tester`＝工具实例；`tasklist` 单次检查有假阴性（10-15 两次竞态），须 un-filtered+filtered 多方法、间隔多次确认后才能碰文件/启动实例。

## 三、当前状态（2026-10-31）

| 项目 | 现状与证据 |
|---|---|
| 本批安装 | 六个内容／修复模组＋两个前置，25文件三处对应；两实例原有JAR与清单外资源未变，E0 |
| 生成与特殊能力 | 独立外置数据包限制8结构、6feature注入；Super-Tier按批准保守值配置；实际行为待验 |
| 当前任务 | 仓库v6.1，test为先前安装v6；母本任务未随本轮同步；Legendary Bosses先前文件仍待独立安装 |
| 地图 | 地图v2由其他对话维护，本次未同步；远端保留[初行地图v1交接](初行地图_v1_交接.md)；不改seed、坐标、设计源或地图工具 |
| EF | 20.14.17固定；本轮不改模型、动画、mobpatch、适配规格或svs_tweak源码 |
| 游戏／联机 | 未启动或操作游戏；用户负责验收，双人仍待验 |
| 六表 | 仍是原采样快照；新增模组独立记录，不填造运行时属性 |

原10-07～10-30执行细节见对应专项和[整理前快照](archive/2026-10-31_入口整理前/HANDOVER.md)。

## 四、已拍板裁决记录（不许推翻，不许重做调研）

### 9-29 及以前
见 `docs/魔改设计决议.md` 变更记录节（9-25 Gateways 否决/9-26 铁魔法定稿等/9-29 任务线全部重写）。

### 2026-09-30（修复批复测批）
- 伤害归因重构：DamageSource.getEntity 在本环境 Rhino 不可解析（mojmap/SRG 全不通）→ svs_tweak SvsDamageHelper 静态助手（JS 传原生对象给静态方法，TradeRegistry 同款模式）
- 远程加压反转：被弹射物打一律 ×0.5（此后 10-01 细化为方向结算）
- svs_tweak 1.0.3（黑名单 shipwreck+mineshaft / 陨石 400~800 环带）

### 2026-10-01（复测回归 + 裁决 2/3/4/8）
- 拾取归属限制：**放弃**（多人不做限制）
- ③ 远程方向结算（10-01 二次裁决）：玩家被弹射物打 ×0.5；玩家远程打飞行/水中怪（inWater||!onGround）**×2 不免疫**；地面 Boss 免疫归零；地面怪 ×0.5；怪内战不动
- Boss 免疫名单：cataclysm: 全前缀 + bosses_of_mass_destruction: + slu:boss_ 前缀（42）+ 血源四 Boss（cleric_beast/father_gascoigne/gascoigne_beast/micolash）+ spore:proto；**只对地面 Boss 生效**
- 限伤：脚本层全部删除（proto 8% 模板删；灾变原生 cap 实证已=1000000 无上限）
- "不接受一刀盲区"→ SvsDamageHelper 精确归因（svs_tweak 1.0.4）

### 2026-10-03（结构 + Inquisition + 任务线）
- 结构表拍板：bettermineshafts 13 变体黑名单；主线白名单扩容 9 座（spore 5 + inqui 4）；biomass_tower 维持默认（只在蘑菇岛生成）；探索线=淡化（默认分支配额制即设计意图）
- SLU 定点化：**选 v2**（主线 Boss 竞技场结构+路网，随任务线Ⅳ章出；封印石右键是随机 Boss 池——反编译实证，定点化不能用原版方块）；随机 Boss 召唤券进**日课+悬赏两池**（待任务线实装）
- 制图师交易：线索书废弃（Rhino NPE/空标签/空白页三连）→ 改**探险家指南针**（15 币，explorerscompass:explorerscompass）
- Inquisition 3.1→3.2.0 + 官方配套 config（必装件，随版本重下；3.x config 只在 YouTube 视频简介）
- 任务线规格书 v1 四批注裁决：分档 8/15/20+名品 5~8 接受；共生使奖励从现有饰品库挑；职业徽章=现成饰品改名展示；文案称呼="冒险者"

### 2026-10-04（SLU 野刷 + 改名 + 检修）
- SLU 全部生物**禁止野刷**（36 个 forge:add_spawns 空 biomes 覆盖，含友善 NPC 生成器），改召唤制：随机 Boss 召唤券（日课+悬赏两池）；存量清场 `/kill @e[type=#svs:slu_hostile]`
- SLU 敌对击杀掉 1 真菌残魂（svs_spawn_control.js，悬赏/日课钩子）
- 改名：真菌之魂/真菌币 → **真菌残魂**（id 不变）
- FA（Final Adversaries）检修：树埋地下 30 格→0、start_jigsaw_name 不匹配任何池元素（全部池 name=None）→ 删除该字段、biomes 扩森林系；勘误：所谓"aether 引用"全 jar 搜索不存在

### 2026-10-11（待裁决清单批复）
- 《待裁决清单》（`docs/待裁决清单.md`）**总体按执行侧推荐采纳，作为初版执行方案**；5 处修正：① **合-3** 新增生成隔离看样改用**独立游戏目录**（不在 test 实例内直接召唤）；② **合-4** 锻造石成长（NotSoShrimple）**暂缓**、英雄之证 **先做兼容验证**（不因生命上限钩子直接否决）；③ **Q10** 毕业 choice **以实际选择并领取到账为准**（不做"完成即领取"简化）；④ **test4** **先归档核验再删除**；⑤ **Q09** 按总稿"**两池独立、每队每池滚动 24 小时首胜 1 券**"执行
- 其余"待看样/待名单/待数值/待实测"的条件继续有效；**任务 SNBT 仍只由用户在编辑器生成**
- 生效要点：M2 八批注点（A1.6 改造、迁4 hidden、preface 改题、阶段 id 映射、炉礼包按修正版 id `tconstruct:seared_table` 等）、序章/Ⅰ 五处补正（含 A1.6 精制铁锭由见面礼发 3 枚）、合入审查 5 问（含**批准 EF 匠魂兼容 20.2.8→20.2.10 受控替换**、刀光先验现有资源、先试 Souls HUD 单项、镜头模组暂缓）均按清单推荐生效

### 2026-10-14/15（模组7、Voxy 换装、EF 附属、模组8；细节见各批次报告）
- **模组7 入包**（10-14 用户批示）：aquamirae／souls_like_bosses（重入，用户确认）／fragmentum（补硬依赖）入母本+test；**世界生成＝维持禁用**（10-15 用户明确裁决；aquamirae 用标签空覆盖、slb 用结构本体 `"biomes":[]`——后者为 10-15 修复的超限值 bug，教训见批次报告 §2.2）；汉化（aquamirae 66 缺键＋slb 13 键）已上 lab，**上生产待批**
- **Voxy 换装**（10-14 用户批「换」）：DH 移出（备份 `backups/prod_migration_20261014/`），信雅互联四件＋DW voxy 0.2.14 移植入；`canary.properties` 加 `mixin.chunk.palette=false`（Canary 选项按**优化组名**开关）；**母本/test 自此须 JDK21 启动**。10-15 补实证：原生 voxy 0.2.15（KNaiFen）与 Oculus 1.8.0 硬冲突、VoxySeedGen 与光影互斥——**用户裁决＝选 A：保光影、弃 seedgen**（详见 Voxy 报告 §六/§七，勿重试此线）
- **EF 附属**（10-15 用户批「装」）：efiscompat 2.6.0、epicfight-skilltree 20.2.9 入包（技能树替换技能书获取，与职业设计关系待实机观察）；**impactful 装后即撤**（mixin FATAL，与 EF 20.14.17 不兼容——EF 旧线附属的 versionRange 声明不可信，一律实跑验证）
- **模组8 直并 test**（10-15 用户指示「不需要 lab、直接合并用 test」）：CarianStyle 2.2.0（法环附魔 113、自带全量中文）／iss_elden_ring 1.0.3（法环法术、自带全量中文、辉石洞维持禁用、上游 9+1 JSON 缺陷登记）入包；SPBR PBR 材质包＋Bliss 光影调参随包启用；**VoxySeedGen 未入**。**此后新批直接落 test，lab 工作流停用**

### 2026-10-31（本对话已确认的执行范围）

- 六模组＋两个必要前置入包，Spawn待接；正式包继续冻结新增生成，采用本批外置限制与Super-Tier保守配置。
- 只整理资料并制定剧情／FTB后续计划；不改剧情正文、任务源／SNBT／桥脚本，不扩地图、EF、围城或其他工程。
- 收藏家与军械全鉴合并、T0／T1／T2及奖励方向沿用用户10-17后续要求；指南旧“禁止Tier”不能覆盖它们。
- 参考指南的证据分级与轻量DND方向按[采纳对照](DeepSeek建议_采纳对照_2026-10-31.md)使用；原文中其他“已定”不自动变成新机制裁决。

## 五、血泪教训（KubeJS/Rhino/Forge，全部实踩）

2026-10-11任务专项补充：本机FTB2001.4.22 KillTask只支持单实体，ObservationTask不是AdvancementTask，CheckmarkTask不能作为防跳过桥；CustomTask上限/按钮须用API设置，不序列化到SNBT。详见任务v2说明；不据方法名猜胜利含义。

**写 KubeJS 前必读，每条都崩过或静默失效过**：

1. **声明规则**：控制流块（if/else/for/while/**try**/catch）内部不得 const/let（第二次执行抛 redeclaration）——扫描器 `python tools/check_kubejs_rhino.py`（夹具应报 17 处），入库前必跑。
2. **ForgeEvents 只在 startup 脚本注入**；Forge 总线监听器体必须整体 try/catch（重抛=崩游戏）。
3. **kubejs/data 不是数据包**（10-03 实证三条独立测试）：数据包类覆盖（结构 JSON/标签/biome_modifier）**一律走 `config/openloader/data/svs/data/`**；注册标签用 `ServerEvents.tags` 事件（实证 t1=257 非零）。
4. **DamageSource 攻击者不可读**（.entity/getEntity/getDirectEntity/SRG 名全不通，330 条样本）→ 归因走 svs_tweak SvsDamageHelper（JS 传原生对象给静态方法，TradeRegistry 同款模式）；事件层 getLastHurtByMob 是"上一刀"（新目标首刀盲区，不可接受时用助手）。
5. **类过滤器拦 java.lang.System**（不止 Class/reflect）——时间戳用 `Date.now()`。
6. **成员解析**：mojmap 名写法 + 只信 KubeJS 注入成员（kjs$）/接收者自类方法；继承成员实测翻车清单：getUUID（所有实体含 ServerPlayer）、dayTime（解析成 Function→NaN）、getGameTime、getScoreboardName、isCreativeMode（旧名，**正名 isCreative()** 可用）、Item.getTags、DamageSource.getEntity。实测可用：player.uuid/username/x-y-z/level.dimension（属性非方法）/getVillagerData().getProfession()/getOffers()/inventory.count(id)、level.getDayTime()/getSharedSpawnPos()、mob.getTarget()/setTarget()、registry.getOrCreateTag(TagKey)。
7. **HolderSet.direct 在 Rhino 必 NPE**（varargs/List 重载都炸）——结构寻址走 svs_tweak locateStructure（纯 Java）或 registry.getOrCreateTag。
8. **fastutil Int2ObjectMap 不可碰**（NativeJavaMap 包装器 CCE 兜不住）——村民交易走 architectury TradeRegistry；遍历交易表走 SvsDamageHelper.villagerTradeDump（Java 侧）。
9. **vanilla 村民 offers 构建=等级列表随机抽 2 笔**——注册进交易表只是候选，必现需求用 trade_guarantee.js 补挂模式（getOffers().add() + pd 标记防重）。
10. **svs_tweak 验证**：jar manifest 必须 `MixinConfigs: svs_tweak.mixins.json`；验收看 **debug.log** 的 `Mixing <Mixin> from svs_tweak.mixins.json`（latest.log 没有）。
11. **后台无头测试**：`pauseOnLostFocus:false`（否则实例失焦即冻结；当前= false，测试收敛后还原）；`--quickPlaySingleplayer` 对不存在的世界停在标题界面（造世界：拷 level.dat=同设置全新地形，**注意改 Difficulty 字节**，和平会清怪）；launch_test4.py 支持 `--world`。
12. **日志跨天轮转**（2026-MM-DD-N.log.gz），跨零点调试翻 .gz；grep 本机对长行日志不可靠，用 python 逐行。
13. **imfdata 适配包覆盖文件曾含缺 id 空对象**（`{"required":false}` 无 id）→ tag 整体加载失败——同类覆盖文件改完要逐字段核。
14. **`level.dimension` 的值形态跨会话不稳定**（10-06 复盘 + 10-07 修正）：10-06 会话 `String(level.dimension)` 返回 `ResourceKey[minecraft:dimension / minecraft:overworld]` 包裹串（与 `'minecraft:overworld'` 直比**恒真失败**，村庄扫描 13 分钟静默不执行）；10-07 会话同写法却返回纯串 `minecraft:overworld`——两种形态都实测出现过，成因未定位。**任何直比写法都不可靠**，一律用双形态兼容写法：`let dim = level.dimension; if (dim.location) return String(dim.location()); return String(dim)`（explorers_compass.js/siege.js 同款，两种形态都正确）。教训：探针表里"可用"只代表可解析不抛错，**参与比较的读取必须打印实际值**。
15. **并发会话产出必须过"必现性"审查**（10-06 三魂审查）：往交易/掉落/生成里加内容时，表注册（TradeRegistry/loot table）只是**候选**——vanilla 随机抽取后未必出现。凡是"玩家必须见到"的内容，都要同时挂补挂/直发通道并打 pd 防重标记；同实体多笔交易用 per-trade flag（单一 done 标记会在第一笔补挂后锁死其余笔）。另：architectury TradeRegistry 是 append 语义（computeIfAbsent+addAll，javap 实证），同职业多笔注册安全。

## 六、已落地魔改清单（详表见各 commit 与 docs）

- 一期：LootBeams 静音、InControl 难度规则、FTB 序章难度三选、真菌残魂经济（掉落+3 笔村民交易）、个人难度 /svs、共生体克制真菌四件套、火种绑定+civillis 文明分、血源 6 武器 EF 适配、POTB 根治、92 ns 汉化
- 二期：围城系统全套、铁魔法禁用 78、灾变限伤对齐 DOTE、母巢限伤爬升（**已删**，10-01 裁决）、远程加压（**已反转**，10-01）、统一伤害层（LivingHurtEvent.setAmount）
- 修复批 0926（10 月闭环）：击杀归因重构、火种绑定 name 基、HUD getDayTime、限伤全删、封印石/矿井黑名单、陨石环带、SI 撒人取消、stages.zs 正名、指南针交易、线索书废弃改指南针
- 三批（10 月）：SvsDamageHelper 1.0.6、结构全量汉化 346 键、SLU 野刷禁令、封印石禁用、FA 结构修复、imfdata tag 修复、Inquisition 3.2+官方 config、收藏家标签（事件注册）、任务线规格书 v1、围城村庄级共享（9b3c1ec+a3b4adb）、EFS-ISS 入包（ba2e9ba）

## 七、后续队列

1. 本批加载和功能由用户在独立测试世界验收；先确认模组／数据包启用，再测试界面、骑乘、战斗与特殊能力，不能用E0代替E1—E3。
2. 用户恢复剧情／FTB施工后，从[施工计划F0](剧情与FTB施工计划_2026-10-31.md)整理总纲、主支线／奖励矩阵和三处差异；接着F1样章，确认后扩F2／F3，F4统一验收。
3. Spawn、结构／材料取得链、CS武器可用性是外部待接项；地图／EF交付由对应对话负责，本轮不发消息催办或代做。
4. DND后续只按等级成长／GameStages、加点和少量子职业能力研究；不实施完整13职业移植。具体数值和冲突须另列规格，不悄悄改现有远程、法术、围城等规则。
5. 旧M1～M6、围城失守／回拨、多人与优化队列保留专项记录，但本轮不处理；不能据历史待办顺带施工。

## 八、工作方式要求（用户定的，务必遵守）

1. 任务文档四条工作原则是圣旨：三思而后行/简洁优先/手术式变更/目标驱动。
2. **先修不删**；ARR mod 不改 jar（MixinSquared 取消器或数据包）。
3. 大型机械任务（批量翻译/批量 JSON）才派子代理；决策和验收自己把关。
4. 改动要有 commit；协议合规登记 `docs/开源协议审查.md`。
5. **多交流**：用户明确要求设计问题多讨论、呈现多种解读、必要时反驳（2026-10-03 起生效）。
6. 历史档案：本文件 git 历史可溯；2026-10-04 前的旧版教训已并入第五节。

## 九、历史事实速查（按原记录日期使用）

- 实例计数（2026-10-15）：母本 225／test 226／svs_lab 230 jar；**test/母本 须 JDK21**（`--java "C:\Program Files\Java\jdk-21\bin\java.exe"`）
- 启动测试：`python E:\mcmp_test\launch_test4.py --version test --world <世界名> --java "C:\Program Files\Java\jdk-21\bin\java.exe"`（quickPlay；世界必须已存在；`--noworld` 仅到标题屏不进世界）；到主菜单约 110~200 秒正常
- 日志：`test/logs/latest.log`（UTF-8，跨天轮转 .gz）；崩溃报告 `test/crash-reports/`；用户错误报告包在 `E:\mcmp_test\错误报告/`
- 杀残留游戏进程：**先多方法确认**（`tasklist | grep -i java` 单次有假阴性；`Ultraman_0`=用户勿动、`Tester`=工具），只对本次工具启动且已核对命令行、实例归属的 PID 操作，禁止按 java 名称批量结束
- Gradle：`JAVA_HOME=C:/Program Files/Java/jdk-17 E:/mcmp_test/gradle-8.8/bin/gradle.bat --offline jar`（svs_tweak 构建）
- CFR 反编译器：/tmp/cfr.jar 或 E:/mcmp_test；javap 用 jdk-21
- 共生体 API：`SymbioteTracker.get(level).peek(uuid)` → stage/trust/stamina；`adjustTrust/adjustStress(ServerLevel,ServerPlayer,int,String)`；`PredatorHunt.isHunting(uuid)`
- 文礼 API：`civil.civilization.BaseScoreApi.add(ServerLevel, BlockPos min/max, double, sourceKey)` / `remove(sourceKey)`
- CF 下载：edge.forgecdn.net 直链（文件名 URL 编码）；Modrinth API 正常；CFPA 汉化仓库走 jsDelivr 或稀疏克隆（已克隆在 i18n_work/cfpa_repo）
