# Symbiote vs Spore 交接文档（写给下一个 AI）

> **当前指示（2026-10-15 交接待续 AI）：** 用户正在实机游玩验收（开发实例 test）。近期节奏＝**改动直落 test（svs_lab 已退出工作流，仅留沙箱/旧世界快照）→ 无头加载验证 → 用户看样**；正式同步＝母本→test→仓库三腿一致。FTB 任务重写仍暂停（用户明确恢复前不生成/替换/测试任务；SNBT 程序生成/校验已授权）。**动 test/母本任何文件前必须先查 java 进程**——用户随时在玩，且 `tasklist` 单次检查有假阴性（10-15 两次竞态教训），须多方法、多次确认。数据入口见 [数据与采样说明](数据与采样说明.md)；叙事现状＝[剧情重写v3](剧情重写_v3_陨星之后.md)（待批注）；近三日批次报告（模组6-7、模组8、EF复查、Voxy）见 docs 根目录同日期文件。
> 更新：**2026-10-15（交接收整；游戏证据按各记录日期）**。本文件是唯一权威交接面。
> 主规格：`docs/任务文档.txt`（设计理念 13 条 + 工作原则）；机制定稿：`docs/魔改设计决议.md`（变更记录节效力最高）。
> 任务线权威：`docs/任务线框架规格书_v1.md`（2026-10-03 定稿）。

## 〇、30 秒版

> **最新剧情方向（用户再次直接要求，2026-10-12登记）：** 约半数Boss主线/半数支线，特别优先点名的特色Boss；**沉降领主/二轮制霸移支线，不再卡主线推进；SLU、灾变等经典Boss竞争战位，不默认占核心或固定名额。** 不再重复询问是否允许这些方向。模型动作优先、技能特效其次、数值最后，实际EF可玩性为前提，具体质量与名单仍看样后定。大圣保留大圣身份与异世传承，不是真菌造物。完整故事、22位主线Boss＋母巢事件/23场支线候选见剧情重写v3；原创动机与终场资格待批，不是Boss验收或任务施工授权。目录差异与大圣未见入包沿用同日v2§九只读快照，不自动同步或合入。

> **当前任务切换（用户要求暂停FTB重写，2026-10-12登记）：** 暂停继续生成、替换、测试和完善FTB任务。先更新整合docs全部资料，包括5份数值Excel＋全模组Excel、模组/武器/Boss/实体/EF/结构清单，完成后供后续任务重写使用。现有v2保留施工中间态，不等于用户验收通过。此前已重载16章210节点，运行时引用审计`missing=[]`，仅证明当时加载及引用；起步、发奖、计数和全线未验。禁止因旧启动词自动恢复任务施工。

> **2026-10-11 任务重建新授权：** 用户要求整本FTB任务重置并重写仓库README，随后明确批准“允许程序生成和校验SNBT；保留已批机制，全面重做任务结构、内容与引导”。原编辑器唯一生成、旧ID保留和M2节点数约束在本次重建中失效；机制裁决继续有效。当前施工入口改为 [FTB任务重置_v2.md](FTB任务重置_v2.md)，具体节点/ID见其链接。下文旧M2施工排队及“等待总体批注”是历史状态，不得继续据此覆盖v2。

1. 你在维护一个 MC 1.20.1 Forge 整合包（**母本 225／test 226 jar**（2026-10-15 计；test 另含用户所加 mobbattle、未同步母本）），共生体 vs 真菌题材，类魂 ARPG，Epic Fight 战斗底座。
2. **历史全绿基线：`E:\mcmp_test\dist\test19.zip`（10-05）**；当前开发/游玩实例 **test**——**必须 JDK 21 启动**（voxy 换装硬要求：`launch_test4.py … --java "C:\Program Files\Java\jdk-21\bin\java.exe"`，PCL 同理选 jdk-21；svs_tweak 构建仍用 jdk-17）。testN.zip 仅作里程碑/交付验证。
3. **先读第五节"血泪教训"再写任何一行脚本**——本环境 KubeJS/Rhino 的坑全部实踩过。
4. 改动三处同步：`E:\SvS_整合包_副本`（母本）→ `C:\PCL 正式版 2.8.13\.minecraft\versions\test`（开发实例）→ git 仓库（推送状态须当次核对）。
5. 用户在 `docs/任务文档.txt` 写了四条工作原则（三思/简洁/手术式/目标驱动），那是圣旨。

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
| `docs/任务线实装核对.md` | M2三件合并；8个批注点，仍待批；阶段Ⅰ16可见/hidden方案20物理节点 |
| `docs/任务设计总稿_v1.md` | **任务设计总稿 v1.1（待批）**：Ⅱ~Ⅳ 74 主线节点＋职业 79＋日课 8＝161 候选；替换旧 C/D/E 提案；Q01–Q14 批注入口 |
| `docs/主线深化研究_全模组与战斗筛选.md` | 215 jar 逐项角色索引 + Boss 四级看样门槛（模型动作→特效技能→可玩流程→数值）+ 夜临/WOC 替换提案 + 终焉决斗(DOTE)拆解 |
| `docs/任务参考研究_五整合包FTB.md` | 五参考包 FTB 任务结构研究（总稿设计依据之一） |
| `docs/刀光与新增模组6_优化合入综合审查.md` | 刀光资源核查 + 15 新 jar 逐项 + B0–B6 分批 + 5 项待裁决（2026-10-11，待批） |
| `docs/Rapid_Optimization_合入评估与执行交接.md` | Rapid 优化包 29 模组逐项与“择项借用”结论（2026-10-10） |
| `docs/EF适配现状与动画管线.md` | EF 适配三层数据驱动 + 自定义动画/视频动捕管线（2026-10-07 调查） |
| `docs/数据与采样说明.md` | 10-12离线更新的六表/目录/统一JSON源；历史属性与现版静态证据分列；完整入口：资料库总索引.md |
| `docs/剧情重写_v3_陨星之后.md` | 10-12再次重写的最新叙事提案；特色优先、沉降移支、经典Boss竞争；完整剧情、主支候选、六份样稿；待批注，不回填FTB |
| `docs/剧情重写_v2_借火者之路.md` | 前稿与只读快照证据；旧二轮必经、部分分流与配额问题已由用户新指示和v3替代，不继续照旧施工 |
| `docs/README.md`／`验收与风险登记.md` | 制作导航、未决边界与历史资料去向 |

## 二、目录布局与同步铁律（勿乱）

| 位置 | 角色 |
|---|---|
| `E:\SvS_整合包_副本` | 整合包母本，所有改动第一落点，打 zip 从这出 |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\test` | **开发/游玩实例**（2026-10-06 由 test20.zip 导入建立；2026-10-15 计 226 jar）：**须 JDK21 启动**（voxy 换装）；launch_test4.py 默认 test |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\svs_lab` | **实验沙箱**（2026-10-11 建；10-15 计 230 jar）：模组6/7/8 与原生 voxy 都曾在此先行试验；批八起工作流直落 test，lab 已退出工作流（保留作沙箱，**另存旧 test 世界 10-12 快照——误删恢复用**）；**绝不同步回母本** |
| ~~test4~~ | **已由用户删除**（2026-10-11 前清理；证据区核查无归档留痕，如需找回查回收站） |
| `E:\mcmp` | Git 仓库（GitHub 233zsq/symbiote-vs-spore） |
| `E:\mcmp_test` | 工具区：launch_test4.py（默认test，支持`--world`/`--version`）、pack_mcbbs.py、dist/testN.zip、i18n_work/、错误报告/、dl/ |

**铁律**：
1. 改 mod/配置/KubeJS → 副本 + **test** 双写 → 仓库 commit。三方漂移是历史重灾区。
2. **数据包类覆盖（结构 JSON/标签/biome_modifier）一律走 `config/openloader/data/svs/data/`**——`kubejs/data/` 在本环境**不是数据包**（实证见第五节教训 10）。
3. 打包：`python E:\mcmp_test\pack_mcbbs.py testN`（MCBBS 格式），打完核对 overrides 内脚本与 jar 版本；**testN.zip 降级为里程碑/交付验证用途**（验证打包通道不漏文件），日常验证全走 test 实例（永远最新）。
4. 并发会话共用仓库：commit 前 `git log --oneline -5`，**只 add 自己改过的文件路径**（曾误扫入他人文件）。
5. **动 test/母本前先查 java**：用户名 `Ultraman_0`＝用户实例（勿动）、`Tester`＝工具实例；`tasklist` 单次检查有假阴性（10-15 两次竞态），须 un-filtered+filtered 多方法、间隔多次确认后才能碰文件/启动实例。

## 三、当前状态（2026-10-07 起滚动；10-15 交接口径见下首行）

- **2026-10-15 计（交接口径）**：母本 225／test 226／svs_lab 230 jar；**母本与 test 须 JDK21 启动**；世界生成维持禁用（模组7＋iss 辉石洞，用户裁决）；模组7/模组8、Voxy 换装（DW 0.2.14 移植＋信雅互联）、EF 附属已在包——裁决与细节见 §四「2026-10-14/15」；近三日报告（模组6-7批次／模组8／EF复查／Voxy）在 docs 根目录。以下为历史快照。

- 215 mod（副本 mods/ jar 实数）；**最近全绿基线 dist/test19.zip**；test20.zip 已打（里程碑包：围城修复+三魂补挂+EFS-ISS，已导入为开发实例 **test**）；**test4 已删除**（2026-10-11 前，用户执行）
- KubeJS：startup 5 + server 13 脚本（另有 TEMP 件：`_siege_fast.js` 与 siege.js 的 TRACE 行，M1.5 收敛后删）
- 自研 mod **svs_tweak-1.0.6.jar**：6 功能（POTB 判空+探针 / 陨石 400~800 环带 / 结构密度提纯 75 格 / AStages 容错 / MixinSquared 取消器 / **SvsDamageHelper 伤害归因助手** + villagerTradeDump 诊断），源码在仓库 `svs_tweak/`
- Inquisition **3.2.0** + 官方配套 config 已装（sporeconfig/sporedata.toml，历史安装记录为副本+test4；当前同步目标为副本+test，作者偏离默认清单在 `E:\mcmp_test\i18n_work\inquisition_author_delta.txt`）
- 指南针三层已落地：配方（下界合金+淬魔钢坯）/维度白名单（主世界+暮色）/真菌币过路费 2 枚（右键钩子）/config structureBlacklist 34 条（主线 21+垃圾通配 13）
- 收藏家标签 `#svs:collect_t1~t5`（**1291 件**武器 DPS 五分位；2026-10-11 E4 收紧剔除 39 条失效 id）：**ServerEvents.tags 事件注册**（生成器 `tools/gen_collect_tags.py`，含 REMOVED_MOD_PREFIXES/EXCLUDE_IDS/FIXED_CUTS）
- 文案：货币统一叫**真菌残魂**（id `kubejs:spore_coin` 不变）
- SLU 三魂兑换已落地（2efc7db 表注册 + **10-06 补挂扩展**）：工具匠 24 币→活尸之魂 / 盔甲匠 48 币→骑士之魂 / 武器匠 64 币→巨人之魂（单向不回兑，maxUses=16）。**10-06 审查发现并修复**：DeepSeek 只注册了候选池没进必现补挂——vanilla 随机抽 2 笔机制下约 33~50% 村民永不显示魂交易（F2 同类）；trade_guarantee.js 已扩为六笔 per-trade flag（旧单标记会把工具匠第二笔锁死）。slu zh_cn 三魂九键同链异名瑕疵一并修正（规格书定名"活尸之魂/骑士之魂/巨人之魂"）
- SLU：36 个生成修饰器空覆盖=**全部生物禁野刷**（含友善 NPC 索拉尔/齐格迈尔/帕奇生成器），封印石禁用；清场命令 `/kill @e[type=#svs:slu_hostile]`
- 围城村庄级共享（9b3c1ec 重构 + a3b4adb 根因修复）：**M1.1 已验证通过**（10-07 日志：新村庄注册 svs_siege_v_1_-60/-61、TRACE rem 每 10 秒 -200 递减、`!siege` 后两波开波 8→10 只）；根因两处见第五节 14；**未验证子项**=失守判定/回村回拨（等自然触发或专门测试）
- EFS-ISS 1.0.3 已入包（ba2e9ba）：**M1.3 已验证通过**（10-07 用户视觉验收：4 砍掉技能拿不到 / 保留技能可用 / 魔法战刃联动法术；KubeJS 错误 0）；收藏家标签无需重跑（jar 实证 0 个 item 类）
- **开发实例转制完成（10-06）**：新实例 test（PCL 导入 test20.zip，1418.6MB/2403 文件，overrides md5 全对）已建；同步规则=母本副本+test+仓库；test4 后由用户删除（10-11 前）
- **计划获批 + M1 大半收敛（10-07）**：开发计划 v1 获批（批注 §四 1~5 全案通过）；M1.1 围城（注册/递减/开波日志实证）、M1.2 三魂必现（两村补挂日志实证）、M1.3 EFS-ISS（用户视觉）**全部通过**——详见 `docs/开发计划_执行状态.md`（滚动登记）。未验证：失守/回拨子项、M1.4 两人同村；M1.5 TEMP 清理挂起等 M1.4
- **E1 已收口（10-07）**：三处 `config/simplyswords_main/{gem_effects,general}.json5` 原为纯 NUL 损坏文件 → 已替换为最小合法 `{}`（三方 md5 `99914b93` 一致）；两轮启动实证：mod **不会**自动重建这两个文件，且 `ConfigWrapper Failed to load config` 错误在"NUL/已删除/合法空配置"三种状态下均出现 = **mod 侧既有现象**（始终走内置默认值，与处置无关）
- M1.6 启动脚本已适配且已验证进入test（执行状态§三）；M1.7 **闭环：test4 已由用户删除**（2026-10-11 前，核查无归档留痕）
- **M2 三件交付（10-07，待用户批注）**：M2.1 唯一节点清单（序章 22/阶段Ⅰ 16/preface 11，含 3 批注点）、M2.2 阶段 id 映射表（影响面普查+迁移方案）、M2.3 八项证据（**skillbook 技能存 NBT→职业卖指定书可行**；DailyBoss 0 advancement→桥方案；SkyArena 奖杯奖励/无钉鞋）。合并文件：docs/任务线实装核对.md（§一/二/三分别为M2.1/2/3；静态证据不等于功能验收）
- **任务深化批（10-10，待用户批注）**：《任务设计总稿 v1.1》交付（Ⅱ~Ⅳ 74 主线节点＋职业 79＋日课 8；撤回固定 SLU 名人三连，改两场差异化战位待批；序章/Ⅰ 5 处教学补正并入批注）＋《主线深化研究_全模组与战斗筛选》《任务参考研究_五整合包FTB》入库。提交 `8d1b664`；开发计划升 v1.2。
- **合入审查批（10-11，待用户批注）**：刀光（现有三资源包未启用待核实）＋新模组6（15 jar；排除 NeoForge MobsPlus 与 Streams）＋Rapid（择项借用：首批 BadOptimizations/0Pack2Reload）；B0–B6 分批与 5 项裁决。提交 `f179690`；开发计划升 v1.3。
- **下一交付：等用户批注**（M2 三件 8 点 + 总稿 v1.1 Q01–Q14）→ 编辑器实装（M2.4）→ 桥激活（M2.5）
- GitHub推送记录：文档重整批次已提交并推送（2026-10-09，`4978dc5` + 同日收尾提交）；后续以 `git log origin/main..main` 实际状态为准

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

## 七、待办队列

**推进队列（各项须满足注明前置；待批项不自动获批）**：
1. **模组6 三项并入正式包**（SoulsHUD／匠魂compat 20.2.10 受控替换／WM＋EFM 桥；lab 已装待批）——用户一句话后走 test+母本+仓库+pw 一条龙
2. **模组7 汉化上生产**（aquamirae 66 缺键＋slb 13 键 overlay → svs_zh_cn，test+母本+仓库）——待批；lab 已有效果可看
3. **资料欠账**：六份 xlsx 工作簿随模组7/8 批次更新（模组清单.md 与协议登记已更新，xlsx 未跟）
4. SLU v2 定点化（主线 Boss 竞技场结构+路网，随任务线Ⅳ章；Boss 召唤券已进日课+悬赏两池设计）
5. （搁置）EF 怪物适配——见"等用户"区；FTB 线（M2.4 编辑器实装→M2.5 桥激活，八批注点与总稿批注已于 10-11 完成）待用户解除暂停

**等用户**：
- **看样清单（test 226 直接开玩，JDK21）**：CarianStyle（K 键百科）／iss 法术观感／SPBR＋Bliss 画面（SPBR 要求关 Mipmap）／"新的世界 (1)"稳定性／Voxy 远景
- **模组6 并包批**、**mod7 汉化上生产批**（各一句话即可）
- 旧世界快照：test／M2_Editor_20261011／新的世界 若疑误删，lab 存有旧 test 世界 10-12 快照可恢复（用户未确认前不动）
- 存量看样队列：夜临/WOC 替换名单、SLU 两场人选、B5 看样圈（WOH/Oddities/NotSoShrimple/英雄之证/Celestisynth/Anka）、大圣残躯 r8-test1 实测；**剧情 v3 批注**（V3-A～D）
- **EF 怪物适配**（`docs/规格书_EF怪物适配.md`，**搁置待裁决**）：范围/外观底线/战斗接管/排期/验收人五问未答；实验批 3 只怪（约半小时）待批准后再动
- 任务恢复施工待用户指示（2026-10-11 已授权程序生成/校验/替换 SNBT；旧"编辑器唯一生成"条目作废）
- pauseOnLostFocus：test 现值随用户游玩偏好；后台无头测试时临时改 false、测完还原（test4 已由用户删除：2026-10-11 前、无归档留痕）

**实测触发才有下文**：真菌飞行怪崩档（复现后填 badmobs）、Relics×真菌 CME、BaM TPS、FA boss 函数 aether 引用（休眠代码无实际影响）

## 八、工作方式要求（用户定的，务必遵守）

1. 任务文档四条工作原则是圣旨：三思而后行/简洁优先/手术式变更/目标驱动。
2. **先修不删**；ARR mod 不改 jar（MixinSquared 取消器或数据包）。
3. 大型机械任务（批量翻译/批量 JSON）才派子代理；决策和验收自己把关。
4. 改动要有 commit；协议合规登记 `docs/开源协议审查.md`。
5. **多交流**：用户明确要求设计问题多讨论、呈现多种解读、必要时反驳（2026-10-03 起生效）。
6. 历史档案：本文件 git 历史可溯；2026-10-04 前的旧版教训已并入第五节。

## 九、关键事实速查

- 实例计数（2026-10-15）：母本 225／test 226／svs_lab 230 jar；**test/母本 须 JDK21**（`--java "C:\Program Files\Java\jdk-21\bin\java.exe"`）
- 启动测试：`python E:\mcmp_test\launch_test4.py --version test --world <世界名> --java "C:\Program Files\Java\jdk-21\bin\java.exe"`（quickPlay；世界必须已存在；`--noworld` 仅到标题屏不进世界）；到主菜单约 110~200 秒正常
- 日志：`test/logs/latest.log`（UTF-8，跨天轮转 .gz）；崩溃报告 `test/crash-reports/`；用户错误报告包在 `E:\mcmp_test\错误报告/`
- 杀残留游戏进程：**先多方法确认**（`tasklist | grep -i java` 单次有假阴性；`Ultraman_0`=用户勿动、`Tester`=工具），确认后 powershell `Stop-Process -Name java -Force`
- Gradle：`JAVA_HOME=C:/Program Files/Java/jdk-17 E:/mcmp_test/gradle-8.8/bin/gradle.bat --offline jar`（svs_tweak 构建）
- CFR 反编译器：/tmp/cfr.jar 或 E:/mcmp_test；javap 用 jdk-21
- 共生体 API：`SymbioteTracker.get(level).peek(uuid)` → stage/trust/stamina；`adjustTrust/adjustStress(ServerLevel,ServerPlayer,int,String)`；`PredatorHunt.isHunting(uuid)`
- 文礼 API：`civil.civilization.BaseScoreApi.add(ServerLevel, BlockPos min/max, double, sourceKey)` / `remove(sourceKey)`
- CF 下载：edge.forgecdn.net 直链（文件名 URL 编码）；Modrinth API 正常；CFPA 汉化仓库走 jsDelivr 或稀疏克隆（已克隆在 i18n_work/cfpa_repo）
