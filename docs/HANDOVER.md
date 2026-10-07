# Symbiote vs Spore 交接文档（写给下一个 AI）

> 更新：**2026-10-05**。本文件是唯一权威交接面。
> 主规格：`docs/任务文档.txt`（设计理念 13 条 + 工作原则）；机制定稿：`docs/魔改设计决议.md`（变更记录节效力最高）。
> 任务线权威：`docs/任务线框架规格书_v1.md`（2026-10-03 定稿）。

## 〇、30 秒版

1. 你在维护一个 MC 1.20.1 Forge 整合包（**215 mod**，副本 mods/ 实数（EFS-ISS 入包）），共生体 vs 真菌题材，类魂 ARPG，Epic Fight 战斗底座。
2. **当前测试基线：`E:\mcmp_test\dist\test19.zip`**（用户以 dist/testN.zip 导入实例实测，不是 test4 开发实例）。
3. **先读第五节"血泪教训"再写任何一行脚本**——本环境 KubeJS/Rhino 的坑全部实踩过。
4. 改动三处同步：`E:\SvS_整合包_副本`（母本）→ `C:\PCL 正式版 2.8.13\.minecraft\versions\test4`（开发实例）→ git 仓库（GitHub 已推送）。
5. 用户在 `docs/任务文档.txt` 写了四条工作原则（三思/简洁/手术式/目标驱动），那是圣旨。

## 一、项目与主文档索引

| 文档 | 内容 |
|---|---|
| `docs/任务文档.txt` | 设计理念 + 工作原则（最高优先级） |
| `docs/魔改设计决议.md` | 机制定稿（变更记录节效力最高，已更新至 2026-10-04） |
| `docs/任务线框架规格书_v1.md` | 任务线重写权威（四职业支线 + 四段式写作规范 + 检测模式三选一，2026-10-03 定稿） |
| `docs/整合包结构表.md` | 274 mod 结构 + 33 原版结构全量枚举、四档密度、线性主线设计 |
| `docs/武器线与匠魂节奏_参考综合.md` | 四参考包拆包结论（任务线重写用） |
| `docs/实例配置说明.md` | 配置生效方式速查（§8.1 sporeconfig 三档调参=P8' 待做） |
| `docs/规格书_修复批_0926.md` | 修复批规格（**已全部完成**，留档） |
| `docs/开源协议审查.md` | 协议合规；改动 mod 清单必须同步登记 |
| 5 张 xlsx（武器/Boss/敌对生物/中立生物/EF 适配） | 数值基准（9 月实采，EFS-ISS 入包后需重采） |

## 二、目录布局与同步铁律（勿乱）

| 位置 | 角色 |
|---|---|
| `E:\SvS_整合包_副本` | 整合包母本，所有改动第一落点，打 zip 从这出 |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\test` | **开发实例（2026-10-06 起）**：用户以 PCL 导入 dist/test20.zip 建（1418.6MB/2403 文件已核对），替代 test4 的角色；launch 脚本待适配新名 |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\test4` | 旧开发实例（遗留，历史世界/验证记录，删留待用户定） |
| `E:\mcmp` | Git 仓库（GitHub 233zsq/symbiote-vs-spore） |
| `E:\mcmp_test` | 工具区：launch_test4.py（支持 `--world`，待适配 test）、pack_mcbbs.py、dist/testN.zip、i18n_work/、错误报告/、dl/ |

**铁律**：
1. 改 mod/配置/KubeJS → 副本 + **test** 双写 → 仓库 commit。三方漂移是历史重灾区。
2. **数据包类覆盖（结构 JSON/标签/biome_modifier）一律走 `config/openloader/data/svs/data/`**——`kubejs/data/` 在本环境**不是数据包**（实证见第五节教训 10）。
3. 打包：`python E:\mcmp_test\pack_mcbbs.py testN`（MCBBS 格式），打完核对 overrides 内脚本与 jar 版本；**testN.zip 降级为里程碑/交付验证用途**（验证打包通道不漏文件），日常验证全走 test 实例（永远最新）。
4. 并发会话共用仓库：commit 前 `git log --oneline -5`，**只 add 自己改过的文件路径**（曾误扫入他人文件）。

## 三、当前状态（2026-10-06）

- 215 mod（副本 mods/ jar 实数）；**测试基线 dist/test19.zip**；开发实例 test4
- KubeJS：startup 5 + server 11 脚本（新增 svs_collect_tags.js 生成物、svs_spawn_control.js、trade_guarantee.js）
- 自研 mod **svs_tweak-1.0.6.jar**：6 功能（POTB 判空+探针 / 陨石 400~800 环带 / 结构密度提纯 75 格 / AStages 容错 / MixinSquared 取消器 / **SvsDamageHelper 伤害归因助手** + villagerTradeDump 诊断），源码在仓库 `svs_tweak/`
- Inquisition **3.2.0** + 官方配套 config 已装（sporeconfig/sporedata.toml，覆盖在副本+test4 的 config/，作者偏离默认清单在 `E:\mcmp_test\i18n_work\inquisition_author_delta.txt`）
- 指南针三层已落地：配方（下界合金+淬魔钢坯）/维度白名单（主世界+暮色）/真菌币过路费 2 枚（右键钩子）/config structureBlacklist 34 条（主线 21+垃圾通配 13）
- 收藏家标签 `#svs:collect_t1~t5`（1330 件武器 DPS 五分位）：**ServerEvents.tags 事件注册**（生成器 `tools/gen_collect_tags.py`，重跑可再生）
- 文案：货币统一叫**真菌残魂**（id `kubejs:spore_coin` 不变）
- SLU 三魂兑换已落地（2efc7db 表注册 + **10-06 补挂扩展**）：工具匠 24 币→活尸之魂 / 盔甲匠 48 币→骑士之魂 / 武器匠 64 币→巨人之魂（单向不回兑，maxUses=16）。**10-06 审查发现并修复**：DeepSeek 只注册了候选池没进必现补挂——vanilla 随机抽 2 笔机制下约 33~50% 村民永不显示魂交易（F2 同类）；trade_guarantee.js 已扩为六笔 per-trade flag（旧单标记会把工具匠第二笔锁死）。slu zh_cn 三魂九键同链异名瑕疵一并修正（规格书定名"活尸之魂/骑士之魂/巨人之魂"）
- SLU：36 个生成修饰器空覆盖=**全部生物禁野刷**（含友善 NPC 索拉尔/齐格迈尔/帕奇生成器），封印石禁用；清场命令 `/kill @e[type=#svs:slu_hostile]`
- 围城村庄级共享（9b3c1ec 重构 + **a3b4adb 根因修复**）：村庄级计时/村外环带已码完；根因两处=维度 ResourceKey 门卫恒真（村庄扫描 13 分钟从未执行，见第五节 14）+ 回拨条件把倒计时钉死 5:00。**待用户重载验证**（日志应见 `[SVS-围城][TRACE] ... key=svs_siege_v_3_115 rem=` 递减；开波快进=聊天 `!siege`，TEMP 工具 _siege_fast.js）
- EFS-ISS 1.0.3 已入包（ba2e9ba）：4 过强技能切断 + 保留技能蓝耗参数（openloader）+ 协议登记；**游戏内验收待做**；收藏家标签**无需重跑**（jar 实证 0 个 item 类）
- **开发实例转制完成（10-06）**：新实例 test（PCL 导入 test20.zip，1418.6MB/2403 文件，overrides md5 全对）已建；同步规则=母本副本+test+仓库；test4 遗留
- **计划获批 + M1 大半收敛（10-07）**：开发计划 v1 获批（批注 §四 1~5 全案通过）；M1.1 围城（注册/递减/开波日志实证）、M1.2 三魂必现（两村补挂日志实证）、M1.3 EFS-ISS（用户视觉）**全部通过**——详见 `docs/开发计划_执行状态.md`（滚动登记）。未验证：失守/回拨子项、M1.4 两人同村；M1.5 TEMP 清理挂起等 M1.4
- **E1 已执行（10-07 裁决=删除重生成）**：三处 `config/simplyswords_main/{gem_effects,general}.json5`（577/269 字节纯 NUL 损坏文件）已删；再生验证=下次启动核对 simplyswords 重建默认文件
- M1.6 启动脚本已适配（launch_test4.py 默认 test，--version 可指定；实测验证待窗口）；M1.7 test4 保留至 M1.6 实测后
- **M2 三件交付（10-07，待用户批注）**：M2.1 唯一节点清单（序章 22/阶段Ⅰ 16/preface 11，含 3 批注点）、M2.2 阶段 id 映射表（影响面普查+迁移方案）、M2.3 八项证据（**skillbook 技能存 NBT→职业卖指定书可行**；DailyBoss 0 advancement→桥方案；SkyArena 奖杯奖励/无钉鞋）。文件：docs/M2.1_唯一节点清单.md、M2.2_阶段id映射表.md、M2.3_待核实证据.md
- **下一交付：等用户批注 M2 三件**（M2.1 三点/M2.2 两点/M2.3 三点，全部有推荐答案）→ 编辑器实装（M2.4）→ 桥激活（M2.5）
- GitHub 已全量推送（2026-10-07，origin/main == local main）

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

## 五、血泪教训（KubeJS/Rhino/Forge，全部实踩）

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

## 七、待办队列

**可直接执行**：
1. 序章任务设计稿（四段式规范首秀，纯 Markdown 不碰 SNBT——三步走第一步，见任务线规格书）
2. ~~规格书_围城村庄级共享.md~~ **已执行**（9b3c1ec + a3b4adb）——剩余：验证局读数 + 收敛后删 TEMP-TRACE-VERIFY
3. ~~EFS-ISS 入包~~ **已落地**（ba2e9ba）——剩余：游戏内验收（技能界面 4 砍掉技能拿不到 / 保留技能可用 / 魔法战刃）；无需重跑 gen_collect_tags.py
5. SLU v2 定点化（主线 Boss 竞技场结构+路网，随任务线Ⅳ章；Boss 召唤券已进日课+悬赏两池设计）

**等用户**：
- simplyswords 两个空白 config（gem_effects/general.json5）处置裁决（删掉重生成 or 给值）
- 围城验证局：游戏内 `/kubejs reload server_scripts`（免重启，jar 实证命令存在）→ 看 `[SVS-围城][TRACE]` 行 rem 递减；**开波快进=聊天发 `!siege` 或手持真菌残魂右键**（TEMP 工具 `_siege_fast.js`，只在副本+test4 不进仓库）；注：`/time add` **不能**快进（推进增量封顶 800，跳变只扣一次）；收敛后删 TEMP-TRACE-VERIFY + _siege_fast.js
- 任务编辑器开搭（FTB SNBT 只由编辑器生成，铁律）
- pauseOnLostFocus 当前=false（后台测试需要），全部收敛后还原 true

**实测触发才有下文**：真菌飞行怪崩档（复现后填 badmobs）、Relics×真菌 CME、BaM TPS、FA boss 函数 aether 引用（休眠代码无实际影响）

## 八、工作方式要求（用户定的，务必遵守）

1. 任务文档四条工作原则是圣旨：三思而后行/简洁优先/手术式变更/目标驱动。
2. **先修不删**；ARR mod 不改 jar（MixinSquared 取消器或数据包）。
3. 大型机械任务（批量翻译/批量 JSON）才派子代理；决策和验收自己把关。
4. 改动要有 commit；协议合规登记 `docs/开源协议审查.md`。
5. **多交流**：用户明确要求设计问题多讨论、呈现多种解读、必要时反驳（2026-10-03 起生效）。
6. 历史档案：本文件 git 历史可溯；2026-10-04 前的旧版教训已并入第五节。

## 九、关键事实速查

- 启动测试：`python E:\mcmp_test\launch_test4.py --mem 10G --world <世界名>`（quickPlay；世界必须已存在，新世界用 level.dat 拷贝造骨架**并改 Difficulty 字节**）；到主菜单 200~350 秒正常
- 日志：`test4/logs/latest.log`（UTF-8，跨天轮转 .gz）；崩溃报告 `test4/crash-reports/`
- 杀残留游戏进程：powershell `Stop-Process -Name java -Force`（先确认没有用户实例在跑）
- Gradle：`JAVA_HOME=C:/Program Files/Java/jdk-17 E:/mcmp_test/gradle-8.8/bin/gradle.bat --offline jar`（svs_tweak 构建）
- CFR 反编译器：/tmp/cfr.jar 或 E:/mcmp_test；javap 用 jdk-21
- 共生体 API：`SymbioteTracker.get(level).peek(uuid)` → stage/trust/stamina；`adjustTrust/adjustStress(ServerLevel,ServerPlayer,int,String)`；`PredatorHunt.isHunting(uuid)`
- 文礼 API：`civil.civilization.BaseScoreApi.add(ServerLevel, BlockPos min/max, double, sourceKey)` / `remove(sourceKey)`
- CF 下载：edge.forgecdn.net 直链（文件名 URL 编码）；Modrinth API 正常；CFPA 汉化仓库走 jsDelivr 或稀疏克隆（已克隆在 i18n_work/cfpa_repo）
