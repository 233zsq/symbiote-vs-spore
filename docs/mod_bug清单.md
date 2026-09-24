# Mod 质量调研报告 — 整合包《Symbiote vs Spore》（MC 1.20.1 Forge）

- 调研日期：2026-09-24
- 调研方式：纯网络调研（MC百科 mcmod.cn、CurseForge、GitHub issues、Modrinth、Reddit、B站专栏/百科论坛），未做任何游戏内实测
- 重点：1.20.1 Forge 版本问题、与 Epic Fight 20.14.17 的兼容性、崩溃隐患、数值崩坏点
- 严重程度图例：**[崩溃级]** 可致游戏/服务端崩溃或存档无法进入；**[体验级]** 明显影响游玩（性能、功能失效、联机异常）；**[小毛病]** 细节缺陷/数值问题；**[EF兼容备注]** 与 Epic Fight 相关的兼容信息

> 局限性说明：① MC百科评论区为 JS 动态加载，多数只能抓到页面正文与标注的已知问题；② CurseForge 站点受 Cloudflare 拦截，部分版本信息经 cfwidget API 与搜索摘要交叉核实；③ 多个小众 mod（中文/独立分发）公开信息极少，"未查到"≠"没有问题"；④ 每条问题均附来源，无法核实的已标注"存疑"。

---

## 一、Boss 类

### 1. L_Ender's Cataclysm（灾变）｜mod id: cataclysm
- 名称/作者：L_Ender's Cataclysm，作者 L_Ender（GitHub lender544）
- 1.20.1 Forge：支持（2026-09 仍在更新）
- 协议：CC BY-NC-ND 4.0
- 已知问题：
  - [崩溃级] 与 Rubidium 同装时，Cataclysm Boss 战期间触发崩溃循环（Rubidium 侧 issue，1.20.1 上下文）。（来源：https://github.com/Asek3/Rubidium/issues/662 、https://github.com/Asek3/Rubidium/issues/695 ）
  - [崩溃级] 与 Iron's Spells 附属 T.O Magic 'n Extras 存在崩溃冲突，社区已出专用兼容补丁"L_Ender's Cataclysm x T.O Magic 'n Extras compability fix"。（来源：https://www.mcmod.cn/class/30590.html ）
  - [EF兼容备注] 本体 Boss 无 EF 动画适配；社区有 EF 补丁"史诗战斗灾变兼容"（作者 frfefefe，1.20.1 Forge，为炎葬、绞肉锯等武器加 EF 动画）。（来源：https://www.mcmod.cn/class/20892.html ）
  - 备注：未查到 Ignis/Leviathan 专属崩溃报告；百科评论区未能抓取原文。

### 2. Legendary Monsters（传奇怪物）｜mod id: legendary_monsters
- 名称/作者：Legendary Monsters，作者 Miauczel
- 1.20.1 Forge：支持（最新 2.2.3，2026-09-17）
- 协议：Modrinth 标 All Rights Reserved，MC百科标 CC BY-NC-SA 3.0（两处不一致，存疑）
- 已知问题（均提在作者 1.21.1 NeoForge 仓库，1.20.1 是否同样受影响未证实）：
  - [崩溃级·存疑] Boss Annihilator 崩溃。（来源：https://github.com/Miauczel/Legendary-Monsters-1.21.1-NeoForge/issues/13 ）
  - [崩溃级·存疑] Sable 实体 Ticking Entity 崩溃。（来源：https://github.com/Miauczel/Legendary-Monsters-1.21.1-NeoForge/issues/8 ）
  - [崩溃级·存疑] Boss 血条（HP bar）触发崩溃。（来源：https://github.com/Miauczel/Legendary-Monsters-1.21.1-NeoForge/issues/6 ）
  - [EF兼容备注] 未查到 EF 相关适配或冲突报告。

### 3. Bosses'Rise（首领崛起）｜mod id: block_factorys_bosses
- 名称/作者：Bosses'Rise，作者 BlockFactoryStudio（另存在 B站作者 xiaoputong 的 EF 适配数据包版）
- 1.20.1 Forge：支持（5 个类魂 Boss，内置翻滚 Z 键）
- 协议：All Rights Reserved（未开源）
- 已知问题：
  - [EF兼容备注] 百科页面提及兼容 Epic Fight；另有社区数据包"Bosses'Rise | 史诗战斗"（xiaoputong，1.20.1）专门做 EF 动作适配。（来源：https://www.mcmod.cn/class/21050.html 、https://www.mcmod.cn/class/23637.html ）
  - [小毛病] 未开源、部分渠道网盘分发，更新依赖作者手动搬运。（来源：https://www.mcmod.cn/class/23637.html ）
  - MC百科论坛汉化帖反馈与 EF 无冲突。（来源：https://bbs.mcmod.cn/thread-22011-1-1.html ）
  - 崩溃级：未查到公开报告（评论区无法抓取，存疑）。

### 4. Bosses of Mass Destruction（祸乱鬼魅）｜mod id: bosses_of_mass_destruction
- 名称/作者：BOMD，Barribob 原作，Forge 版由 Cerbon（CerbonXD）维护
- 1.20.1 Forge：支持（Forge 专版，2026-07 更新）
- 协议：LGPL-3.0-only
- 已知问题（原 Barribob 仓库）：
  - [崩溃级] Void Blossom 战斗中崩溃（Forge 1.20.1-1.1.2 实测），崩溃后无法进存档除非传送走；未修复。（来源：https://github.com/Barribob/Bosses-of-Mass-Destruction/issues/164 ）
  - [体验级] Boss 判定箱（hitbox）异常，玩家吐槽"stupid hitbox"。（来源：https://github.com/Barribob/Bosses-of-Mass-Destruction/issues/165 ）
  - [崩溃级] BOMD 抛错被 neruina 捕获后导致机械动力部署器（Create Deployer）停工。（来源：https://github.com/Barribob/Bosses-of-Mass-Destruction/issues/169 ）
  - [EF兼容备注] 未查到 EF 专用兼容补丁或已知冲突（CerbonXD 仓库禁用 issue，无法进一步查证）；Night Lich/Obsidilith/Gauntlet 未检索到针对性 bug 报告。

### 5. Souls Like Bosses｜mod id: souls_like_bosses
- 名称/作者：查证到两个同名候选，需以整合包实际 jar 文件核实：
  - A. **Souls Like Bosses**（Bananaph0ne/b4nanaph0ne76），Forge/Fabric 1.20.1，类魂 Boss 生成于新结构。（来源：http://mcmod.cn/class/30070.html ）
  - B. **soul like boss: epic fight addon**（sunwoolove777，MCreator 制作），1.20.1 Forge，以 Epic Fight 为前置，含 Ornstein、屠龙者盔甲等 Boss。（来源：https://www.mcmod.cn/class/12590.html ）
- 1.20.1 Forge：两者均支持
- 协议：A 为 All Rights Reserved（未开源）；B 为 MC百科站规 BY-NC-SA 3.0
- 已知问题：
  - [体验级]（A）材质加载异常时需手动将 "Mod Resources" 资源包置顶。（来源：https://modrinth.com/mod/souls-like-bosses 官方自述）
  - [体验级]（A）Boss 可能冻结卡死，需 scoreboard 命令修复。（来源：同上，Modrinth 页面官方自述）
  - [小毛病·存疑]（B）MCreator 制作，性能与手感存疑。
  - [EF兼容备注]（B）本身即 EF 附属；（A）未查到 EF 适配。

### 6. Demi's Sky Arena（天空竞技场）｜mod id: skyarena
- 名称/作者：Demi's Sky Arena，作者 JrDemiurge（Modrinth 分发）
- 1.20.1 Forge：支持（1.20.x Forge，最新 2025-08-05）
- 协议：MIT
- 已知问题：
  - [小毛病] 官方要求同时安装 AttributeFix，否则部分 Boss 血量超原版 1024 上限被截断。（来源：https://modrinth.com/mod/demis-sky-arena ；https://www.mcmod.cn/class/19400.html ）
  - 其余：未查到崩溃级或兼容性反馈；无独立 CurseForge 页；EF 兼容信息未查到任何来源提及。

### 7. 罪业余烬系列（Ash Of Sin）｜mod id: ash_of_sin
- 名称/作者：主模组"罪业余烬：类魂BOSS战"（Ash Of Sin: Soul Like Boss Battle）与"罪业余烬：不死者之王"（Ash Of Sin: Overlord）等，作者 Windrinn 等
- 1.20.1 Forge：类魂BOSS战支持（Forge 1.20.1）；**不死者之王仅支持 Forge 1.19.2，不支持 1.20.1** —— 若整合包同时收录该子模组需注意版本不符
- 协议：未查到（百科页面未标注）
- 已知问题：
  - 未查到崩溃级/体验级/EF 兼容的公开反馈；通用 EF 兼容 mod efmcompat 的支持列表中不含 Ash Of Sin。（来源：https://modrinth.com/mod/efmcompat ）
  - [小毛病·存疑] 系列含多个"自定义反XX实体"类附属库模组，同类附属性质、同装可能冲突，仅为结构推测，无具体冲突报告。（来源：https://www.mcmod.cn/class/14109.html ）

### 8. EEEAB's Mobs（EEEAB的生物）｜mod id: eeeabsmobs
- 名称/作者：EEEAB's Mobs，作者 EEEAB
- 1.20.1 Forge：支持（Forge 1.19.2/1.20.1，2026-05 更新）
- 协议：LGPL-3.0-only
- 已知问题：
  - [体验级·存疑] Boss 数值偏高、依赖自定义 Boss 栏机制，社区衍生出 Death Mode（更难）与 Custom Bossbars 等附属，侧面反映原版平衡有争议（间接推断，无直接差评原文）。（来源：http://mcmod.cn/class/21343.html ；https://www.mcmod.cn/class/25568.html ）
  - [EF兼容备注] 无专用 EF 动画补丁；efmcompat 支持列表包含 EEEAB's Mobs（提供武器兼容而非怪物动画）。（来源：https://modrinth.com/mod/efmcompat ）
  - 崩溃级：未查到公开报告。

### 9. Monster Expansion｜mod id: monsterexpansion
- 名称/作者：Monster Expansion，作者 Saksolm（纹理署名 Cliosow）
- 1.20.1 Forge：支持（MC百科指出其 1.20.2+ 版本标注有误，实际仅 1.20.1 可用）
- 协议：All Rights Reserved
- 已知问题：
  - [体验级] Skrythe/Rhyza 等怪物的生存模式驯服途径被移除，正常游玩无法驯服，只能用指令或保留已驯服个体。（来源：https://www.mclists.cn/mod/OSlNyqiW/monster-expansion.html ）
  - [EF兼容备注·存疑] 打击部位（hitzone）与断肢机制为自定义战斗逻辑，与 EF 攻击判定/动画可能叠加异常，但无任何具体兼容报告，仅提示实测。（来源：https://modrinth.com/mod/monster-expansion 简介机制描述）
  - 崩溃级：未查到（百科页"暂无日志"、评论区无内容）。

---

## 二、主题类

### 1. Fungal Infection: Spore（真菌感染：孢子）｜mod id: spore
- 名称/作者：Fungal Infection: Spore，作者 the_harbinger69
- 1.20.1 Forge：支持（Forge/NeoForge 双端）
- 协议：All Rights Reserved（未开源）
- 已知问题：
  - [体验级] 方块感染会持续把地表转化为菌丝/感染块，配置文件中**没有"完全关闭扩散"的选项**，对存档地形是设计内的长期破坏。（来源：https://www.mcmod.cn/post/6518.html ）
  - [体验级] 感染实体堆积是主要性能负担；官方提供 Despawning system 限制实体数量降延迟，需手动调优。（来源：https://www.mcmod.cn/post/6518.html ）
  - [体验级] 历史版本多项性能/崩溃修复记录：Phayres 曾是"lag machine"、方块感染性能多次优化、Mound 死亡崩溃、XP 掉落崩溃、成就处理崩溃、多次服务器崩溃修复——旧 1.20.1 文件风险高于新版。（来源：https://www.zitbbs.com/forum.php?mod=viewthread&tid=13986 ）
  - [小毛病] 部分实体加载/强制加载区块曾有存档数据异常记录；配置对 Sculk/Faw 类模组方块设有感染黑名单，跨模组兼容需留意。（来源：https://www.mcmod.cn/post/6518.html ）
  - [EF兼容备注] 未查到官方 EF 适配或已知冲突；感染者为原版体型/普通 AI，未见 EF 动画异常报告。

### 2. Symbiote: A Bonding Experience（共生体）｜mod id: symbiote
- 名称/作者：作者 kitigawa（Modrinth/CurseForge 分发）
- 1.20.1 Forge：支持（仅 1.20.1 Forge，2026-09-08 仍有更新）
- 协议：All Rights Reserved（闭源，无源码仓库）
- 已知问题：
  - [小毛病] Predator（捕食者）能力存在 BUG：部分情况误判目标伤害/血量，直接触发斩杀、意外秒杀不该被斩杀的目标。（来源：https://www.mcmod.cn/class/30078.html ）
  - [体验级] 与 Physics Mod 冲突：共生体触须特效引发异常，官方处理方式是配置中把 `symbiote:tendril_fx` 设为 false 关闭触须特效。（来源：https://www.mcmod.cn/class/30078.html ）
  - [EF兼容备注] 套装技能与 EF 姿态的冲突：未查到任何来源记载（mod 闭源，仅 MC百科一个有效来源，置信度中等）。

### 3. Blood And Madness｜mod id: bloodandmadness
- 名称/作者：作者 Nitespring（GitHub: Nitespring/Blood-And-Madness-2.0）
- 1.20.1 Forge：支持（1.20.1 最新 v2.1.5.2，**2023-06 后停更**）
- 协议：BY-NC-SA
- 已知问题：
  - [体验级] 1.20.1 服务端性能问题严重：GitHub issue #5 实测 TPS 掉到 8–13，该 mod 占用 35–40% 服务器性能（open）。（来源：https://api.github.com/repos/Nitespring/Blood-And-Madness-2.0/issues/5 ）
  - [体验级] 性能类 open issues 还有 #7 "Lag"、#4 "Spawning"（刷怪异常），均未关闭。（来源：https://github.com/Nitespring/Blood-And-Madness-2.0/issues ）
  - [EF兼容备注] 装 Epic Fight 后，Threaded Cane（线杖）和 Beast Cutter（兽斩）两把武器没有对应动画（百科正文注明）。（来源：https://www.mcmod.cn/class/4748.html ）
  - [EF兼容备注·存疑] 1.20.1 文件两年多未更新，与 Epic Fight 20.14.x 的兼容性无任何官方表态；未查到 1.20.1 崩溃级报告。

### 4. souls-like universe: epic fight｜mod id: slu
- 名称/作者：souls-like universe: epic fight，作者 sunwoolove777（MCreator 制作）；前置 Epic Fight 与 WoM/奇迹武器
- 1.20.1 Forge：支持（版本跨度 1.19.2–1.21.1，Forge/NeoForge）
- 协议：未查到
- 已知问题：
  - [体验级] **官方 CurseForge/Modrinth 页面已被删除**（MC百科特别注明"官方页面删除，下载需直链"），分发渠道不稳定，存在拿到旧版/无修复版的风险。（来源：https://www.mcmod.cn/class/15360.html ）
  - [小毛病] MCreator 制作，质量上限存疑；百科评论区无内容，未查到具体 bug 报告。
  - [EF兼容备注] 本身即 EF 附属，与 EF 20.14.17 的版本匹配要求无从查证（发布页已删），存疑，需实测。

### 5. Weapons of Cataclysm: Remastered｜mod id: woc_remastered
- 名称/作者：WoC: Remastered，作者 HAVNNek（CurseForge 分发）；定位为 L_Ender's Cataclysm 武器附属
- 1.20.1 Forge：支持
- 协议：未查到
- 已知问题：
  - [EF兼容备注] 官方明示兼容 Epic Fight（新增独特攻击/连招），前置 Cataclysm + 奇迹武器（WoM）——主题组里少数"官方声明 EF 兼容"的 mod。（来源：https://www.mcmod.cn/class/28729.html ）
  - [小毛病·存疑] 与 WoM、Epic Fight、Cataclysm 四方版本需同时匹配，任一方更新可能造成连招失效（推断性提醒，无具体报告）。
  - 未查到崩溃/bug 报告（百科评论区"暂无日志"；B站介绍视频评论区无崩溃反馈）。

### 6. EpicFight: Dawnday｜mod id: epicfight_dd
- 名称/作者：EpicFight: Dawnday，作者未查到，CurseForge 分发；前置 geckolib + epic-fight
- 1.20.1 Forge：未知 —— CurseForge 页面因 Cloudflare 403 无法访问，MC百科/Modrinth 均无收录，版本/加载器无法核实
- 协议：未查到
- 已知问题：
  - [EF兼容备注] 内容为 EF 附属：41 件新武器、33 套动作组。
  - [EF兼容备注·存疑] 与 EF 20.14.17 的版本匹配要求完全无法查证；EF 附属对本体小版本敏感，EF 升级后弱附属常见武器动作失效，需实测。
  - 未查到任何崩溃/冲突报告（发布页不可达、无百科条目、无 issue 渠道，属"零可核实信息"状态）。

---

## 三、生物类

### 1. [JW] Jerotes实用仓库｜mod id: jerotes
- 名称/作者：Jerotes Warehouse，作者 Jerotes_
- 1.20.1 Forge：支持（最新 v2.0，仅 Forge 1.20.x）
- 协议：GPL-3.0-only
- 已知问题：未查到明显问题。系"铜刻佣兵团"系列通用前置库（功能从主 mod 拆出以提升兼容性），无公开崩溃/bug 报告。（来源：https://www.mcmod.cn/class/19502.html ）

### 2. [JV] Jerotes村庄-二轮世界｜mod id: jerotesvillage
- 名称/作者：Jerotes Village - Second Round World，作者 Jerotes_
- 1.20.1 Forge：支持（最新 v1.1.5.20）
- 协议：GPL-3.0（MC百科标注，主 mod 本体在 Modrinth 未直接命中，存疑）
- 已知问题：
  - [体验级] 设计如此：其它 mod 的结构会生成进"二轮世界"维度，可能显得杂乱。（来源：https://www.mcmod.cn/class/14086.html ）
  - [小毛病] 强依赖前置 Jerotes实用仓库，缺前置直接无法启动。（来源：同上）
  - [EF兼容备注] 未查到与 EF 的公开冲突报告；含自定义 Boss 与佣兵 NPC，无官方 EF 兼容补丁。

### 3. Saint's Dragons（Saint的群龙）｜mod id: saintsdragons
- 名称/作者：作者 LilRicefield（MC百科署名 SaintVanWinkle，谁是主作者存疑）；前置 GeckoLib
- 1.20.1 Forge：支持（2025-10 首发，2026-09-23 仍更新，非常活跃）
- 协议：Dual License（Modrinth 标注）
- 已知问题（GitHub issues）：
  - [崩溃级] Ignivorus 咬死龙群单位时 DraconianSwarmCoordinator 抛 ConcurrentModificationException（#48，已修复）。（来源：https://github.com/LilRicefield/saints-dragons/issues/48 ）
  - [崩溃级] Raevyx 蓄力攻击触发 Ticking Entity 崩溃（#46，已修复）；Volitans 崩溃（#35）；0.8.2 进入旧存档崩溃（#37）——均已关闭。（来源：同仓库 issues 列表）
  - [体验级] Volitans 实际生成数量超过配置上限（#45，仍 open）；龙突然消失/隐形（#30、#34，closed）；破坏性模式关闭不生效（#40）。（来源：同上）
  - [体验级] 与 brutality mod 不兼容（#42，closed）。（来源：同上）
  - [EF兼容备注] 未查到与 EF 的公开冲突报告；龙类为 GeckoLib 大体型实体，EF 无官方适配。

### 4. Alex's Mobs（Alex的生物）｜mod id: alexsmobs
- 名称/作者：作者 Alexthe668 / LudoCrypt
- 1.20.1 Forge：支持（1.20.1 最终版 1.22.9，**2024-09 起停更**）
- 协议：GPL-3.0-only
- 已知问题（GitHub issues，1.20.1 相关）：
  - [崩溃级] 蜈蚣（Centipede）1.20.1 崩溃（#2273）；骨蛇生成时崩溃（#2270）；FlightMoveController 相关崩溃（#2085）。（来源：https://github.com/AlexModGuy/AlexsMobs/issues/2273 等）
  - [崩溃级] Rocky Roller 与 Untamed Wilds 的熊同场崩溃（#2247，跨 mod 冲突）；末地生物游向 Spelunkery 维度裂隙时崩溃（#2177）。（来源：同上）
  - [崩溃级] AMWorldData.searchForPupfishChun 相关崩溃（#2325，open）。（来源：https://github.com/AlexModGuy/AlexsMobs/issues ）
  - [小毛病] 彩虹水母与 OptiFine 同用有渲染故障（#1986）。（来源：https://github.com/AlexModGuy/AlexsMobs/issues/1986 ）
  - [EF兼容备注] 未查到公开 EF 专项冲突；85+ 生物体量大，EF 不会为其生成动画。停更后问题修复依赖社区补丁或自行规避。

### 5. Mowzie's Mobs（Mowzie的生物）｜mod id: mowziesmobs
- 名称/作者：作者 Bob Mowzie 团队（非开源）
- 1.20.1 Forge：支持（1.20.1 最新 1.7.3，2025-05-28；近期更新集中在 1.21.x NeoForge）
- 协议：All Rights Reserved
- 已知问题：
  - [EF兼容备注] Epic Fight 官方曾修复与 Mowzie's Mobs 的兼容问题（1.16.5 时代左手手套渲染异常，EF 16.6.0 修复，issue #933）；1.20.1 / EF 20.14.x 下未查到公开专项崩溃，但两者均重度接管 AI/动画，建议实测。（来源：https://github.com/Yesssssman/epicfightmod/issues/933 ）
  - [体验级] 中文社区报告：整合包中"雕刻家/通臂大师"的石柱特效显示异常（1.20.1）。（来源：https://bbs.mcmod.cn/forum.php?mod=viewthread&tid=22868 ）
  - [小毛病] 1.20.1 遗留问题基本不再修，更新重心在 1.21.x。（来源：https://modrinth.com/mod/mowzies-mobs 版本历史）

### 6. Dungeons And Combat｜mod id: dungeons_and_combat
- 名称/作者：作者 Tohirogosu（MCreator 制作，闭源）
- 1.20.1 Forge：支持（Forge 专属）
- 协议：All Rights Reserved
- 已知问题：
  - [EF兼容备注·存疑] 依赖 PlayerAnimator 动画库，与 EF 的动画/事件体系存在叠加风险，未查到公开冲突报告，建议实测。（来源：https://www.mcmod.cn/class/17750.html ）
  - [小毛病] MCreator 生成代码 + 闭源，出问题只能等作者更新；前置多（GeckoLib、Cloth Config、Curios、PlayerAnimator），配置负担大。（来源：同上）
  - 崩溃/功能性 bug：未查到公开报告。

### 7. Guard Villagers（警卫村民）｜mod id: guardvillagers
- 名称/作者：作者 seymourimadeit
- 1.20.1 Forge：支持（1.20.1 线最新 1.6.15）
- 协议：Custom（GitHub LICENSE，非标准开源协议）
- 已知问题（GitHub issues）：
  - [崩溃级] 1.20.1 实体加载时重复添加 AI 目标触发 ConcurrentModificationException（#314，已修复）；警卫被箭击中即时 CTD（#299）；"RepairGolem"动作相关崩溃（#301）。（来源：https://github.com/seymourimadeit/guardvillagers/issues/314 等）
  - [体验级] 1.20.1 存在性能问题，作者要求提供 spark 分析（#305）；警卫频繁卡进房屋或卡死（#297、#282）；1.6.15 配置文件损坏（#281）。（来源：同上）
  - [体验级] 与 Carry On 不兼容（#313）；给村民拔刀剑(Slashblade)导致村民消失（#306）；无业村民换装后隐形（#310）。（来源：同上）
  - [EF兼容备注] 未查到与 EF 的公开冲突报告；警卫为持械人形生物，EF 侧无官方适配补丁。

---

## 四、装备类

### 1. Simply Swords（简易刀剑）｜mod id: simplyswords
- 名称/作者：作者 Sweenus
- 1.20.1 Forge：支持（1.53.0，2024-02 为 1.20.1 线末版，**已停更近两年**，开发转向 1.21.1）
- 协议：MC百科标 BY-NC-SA 3.0；Modrinth 标自定义（两处不一致，存疑）
- 已知问题：
  - [崩溃级] 与 Epic Fight 同时安装曾在 Forge 1.20.1 启动即崩（issue #309，已修复关闭）。（来源：https://github.com/Sweenus/SimplySwords/issues/309 ）
  - [体验级] Storm's Edge 在 1.20.1 Forge 出现 Mixin 注入错误致无法启动的记录（#311）；Star's Edge 有卡顿报告（#298）。（来源：https://github.com/Sweenus/SimplySwords/issues/311 ）
  - [EF兼容备注] 无官方 EF 动作组：EF 姿态下走通用动作，专属技能（右键类）可能不触发；社区数据包"简易刀剑|史诗战斗"/"附属"/"修复"（作者 xiaoputong）补动作，评论区吐槽"一把剑25个形态、平底锅击退过强"。（来源：https://www.mcmod.cn/class/23510.html 、https://www.mcmod.cn/class/23586.html 、https://www.mcmod.cn/class/23509.html ）
  - [EF兼容备注] 通用兼容 mod efmcompat（1.20.1 Forge）亦提供其武器适配。（来源：https://modrinth.com/mod/efmcompat ）

### 2. Epic Knights: Shields, Armor and Weapons｜mod id: magistuarmory
- 名称/作者：查证确认 slug「magistuarmory」即 Epic Knights 本体（issue #69 标题直接写 "(magistuarmory)"），作者 Magistu
- 1.20.1 Forge：支持（如 10.11）
- 协议：All Rights Reserved（闭源但代码公开）
- 已知问题：
  - [崩溃级] **缺失或版本不匹配 Epic Fight 时加载崩溃**：NoClassDefFoundError yesman/epicfight/api/asset/AssetAccesor（#69，open）——说明其内置 EF 联动是硬依赖点，EF 版本必须与包内 20.14.17 匹配。（来源：https://github.com/Magistu/Epic-Knights/issues/69 ）
  - [体验级] 骑士长枪冷却覆盖背包其它物品冷却（#77，1.20.1 Forge 10.11，open）。（来源：https://github.com/Magistu/Epic-Knights/issues/77 ）
  - [体验级] 与 Better Combat 在 1.20.1 Forge 冲突（#72，open）；有"武器无法合成"报告（#71，open）。（来源：https://github.com/Magistu/Epic-Knights/issues/72 ）
  - [EF兼容备注] 自带 EF 兼容资产；efmcompat 另提供 1.20.1 武器动作适配（作者自述 "things may break"）。（来源：https://modrinth.com/mod/efmcompat ）
  - [小毛病] 模型/材质缺失刷日志（#66，open）。

### 3. Tinkers' Construct（匠魂3）｜mod id: tconstruct
- 名称/作者：SlimeKnights 团队
- 1.20.1 Forge：支持，主线持续维护（3.12.x，1.20.1 移植完成度高）
- 协议：MIT
- 已知问题：
  - [崩溃级] 有 1.20.1 + Forge 47.4.10 启动崩溃报告（#5728，因缺日志标"信息不足"未解决）。（来源：https://github.com/SlimeKnights/TinkersConstruct/issues/5728 ）
  - [体验级] 下界合金护甲会被火焰损坏（#5729，1.20 Bug）。（来源：https://github.com/SlimeKnights/TinkersConstruct/issues/5729 ）
  - [EF兼容备注] 无官方 EF 适配；社区数据包"[ETF]史诗匠魂战斗"（1.20.1）仅复用原版动作。（来源：https://www.mcmod.cn/class/15892.html ）
  - [小毛病] 官方声明 1.16.5 起永不兼容 OptiFine/高清修复；百科页面另注明"工具制造配方会失效"（具体触发环境存疑）。（来源：https://www.mcmod.cn/class/3725.html ）
  - 合金/冶炼机制专项 bug：未查到 1.20.1 明确案例。

### 4. Relics（遗物）｜mod id: relics
- 名称/作者：SSKirillSS 等（注意 Modrinth 上同名 "relics" 是另一数据包，勿混淆）
- 1.20.1 Forge：支持（0.8.0.9，2025-04-02）
- 协议：自定义（GitHub NOASSERTION）
- 已知问题（GitHub issues，均 open）：
  - [崩溃级] 1.20.1 SporeEntity 在 onRemovedFromWorld 中生成克隆实体导致 CME 崩溃（#254）。（来源：https://github.com/SSKirillSS/Relics/issues/254 ）
  - [崩溃级] 皮革腰带：进服务器时客户端崩溃 "No model for layer relics:leather_belt"（#262）。（来源：https://github.com/SSKirillSS/Relics/issues/262 ）
  - [体验级] 与水晶之心组合，脱下腰带后最大生命加成不回收（#352，1.20.1）。（来源：https://github.com/SSKirillSS/Relics/issues/352 ）
  - [小毛病] 遗物掉率偏高、长期缺"稀有度"配置（#292）。（来源：https://github.com/SSKirillSS/Relics/issues/292 ）
  - [EF兼容备注] 未查到与 EF 的专门适配或冲突记录。

### 5. Artifacts（奇异饰品）｜mod id: artifacts
- 名称/作者：ochotonida、florens
- 1.20.1 Forge：支持（9.5.x 线；依赖 Curios 前置）
- 协议：Modrinth 标 MIT；MC百科标 BY-NC-SA 3.0（两处不一致，存疑）
- 已知问题：
  - [崩溃级] 1.20.1 装备潜水镜（Snorkel）崩溃，系旧版 Forge Origins 引起，9.5.19 已修复（#453）。（来源：https://github.com/ochotonida/artifacts/issues/453 ）
  - [小毛病] 曾有 1.20.1 "Strange Bug"/启动失败报告，均判定为报告者环境问题关闭（#438）；其余多数 issue 集中在 1.21.x。（来源：https://github.com/ochotonida/artifacts/issues/438 ）
  - [EF兼容备注] 与其它饰品栏 mod 冲突及 EF 冲突：均未查到明确公开案例。

### 6. Spoorn Armor Attributes｜mod id: spoornarmorattributes
- 名称/作者：作者 spoorn
- 1.20.1 Forge：MC百科标注支持；**存疑** —— GitHub 仓库 README 现只写新版 MC / Fabric+NeoForge，且无 releases/tags，1.20.1 Forge 文件仅见于 CurseForge（访问被拦未直接核对）
- 协议：MIT
- 已知问题：
  - [体验级] **已停更**：百科状态标"停更"，仓库重心转向新版加载器，1.20.1 线无维护。（来源：https://www.mcmod.cn/class/10118.html ；https://github.com/spoorn/SpoornArmorAttributes ）
  - [小毛病·存疑] 与其它属性/饰品 mod 的具体冲突案例未查到公开记录；长期停更意味着新 mod 组合下无回归测试。
  - [EF兼容备注] 未查到与 EF 的兼容或冲突记录。

---

## 五、玩法类

### 1. Iron's Spells 'n Spellbooks｜mod id: irons_spellbooks
- 名称/作者：作者 Iron431 团队
- 1.20.1 Forge：支持
- 协议：All Rights Reserved
- 已知问题：
  - [崩溃级/EF兼容备注] 1.20.1 与 Epic Fight 同用曾导致**服务端随机崩溃**（动画播放正常但偶发 crash），issue #787 已关闭修复。（来源：https://github.com/iron431/Irons-Spells-n-Spellbooks/issues/787 ）
  - [EF兼容备注] 仓库历史上有十余个 Epic Fight 兼容 issue（#543、#519、#412、#315 等，全部已关闭）——EF 姿态/动画适配长期高频修补，旧版本组合的风险集中在此。（来源：https://github.com/iron431/Irons-Spells-n-Spellbooks/issues ）
  - [崩溃级] "Forge 1.20.1 Crash when starting fresh world"（#1060，已修复）。（来源：同上 issues 列表）
  - [体验级] 与 L_Ender's Cataclysm 的联动本体未内置，需第三方附属（T.O Magic 'n Extras 及其专用兼容修复补丁）才能打通，属常见痛点。（来源：https://www.mcmod.cn/class/30590.html ）

### 2. FTB Quests｜mod id: ftbquests
- 名称/作者：FTB 团队
- 1.20.1 Forge：支持
- 协议：未查到
- 已知问题：
  - [体验级] 1.20.1 联机进服后任务书无法打开，报 "no quest book data received from server"（#1478，因缺日志关闭未修复）。（来源：https://github.com/FTBTeam/FTB-Mods-Issues/issues/1478 ）
  - [体验级] 未查到 1.20.1 明确确认的进度丢失/不保存 issue；追踪器近期待处理 1.20.1 bug 存在（#2085、#2052 等）但不指向进度丢失。（来源：https://github.com/FTBTeam/FTB-Mods-Issues/issues ）
  - [EF兼容备注] 与 Lootr：仅见 1.19+（#1097）、1.21+（#2091）各一条且均已关闭，未见 1.20.1 确认冲突。（来源：https://github.com/FTBTeam/FTB-Mods-Issues/issues?q=lootr ）

### 3. Daily Boss｜mod id: dailyboss
- 名称/作者：作者 pla_is_me
- 1.20.1 Forge：支持
- 协议：未查到
- 已知问题：未查到明显问题。**注意**：独立信息源极少（仅 MC百科词条与 B站演示视频），无 issue 渠道可查，风险以"未知"为主，并非确认无 bug。（来源：http://mcmod.cn/class/25040.html ）

### 4. Waystones（传送石碑/指路石）｜mod id: waystones
- 名称/作者：作者 BlayTheNinth
- 1.20.1 Forge：支持
- 协议：未查到
- 已知问题：未查到明显问题（1.20.1 Forge 专项检索与百科评论区均未见崩溃/传送点丢失报告）。备注：作者 GitHub 仓库访问 404，issue 渠道未能核查；CTOV 村庄不生成传送石碑的 issue（#230）属 Fabric 版，不列入。

### 5. Bonfires（篝火）｜mod id: bonfires
- 名称/作者：作者 Wehavecookies（黑暗之魂篝火主题：重生/传送点）
- 1.20.1 Forge：支持（仅 MC百科词条佐证；百科未获下载授权、CurseForge/Modrinth 未能核实，存疑）
- 协议：未查到（百科页面所标 BY-NC-SA 3.0 是词条协议，非 mod 协议）
- 已知问题：未查到明显问题。信息源单一，1.20.1 实际兼容性建议以实测为准。

### 6. Lootr｜mod id: lootr
- 名称/作者：作者 Noobanidus
- 1.20.1 Forge：支持
- 协议：未查到
- 已知问题：
  - [体验级·多人] 联机中不同玩家看到的箱子内容不一致，常被误解为同步 bug——实为 Lootr"每人独立战利品"设计，配置不当即出现"人手一份/内容对不上"的观感（B站专栏正文未能抓取，仅标题可证，存疑）。（来源：https://www.bilibili.com/read/mobile?id=35782163 ）
  - [小毛病] 双箱被拆分为两个独立 Lootr 箱（issue #886 标注 1.21.1、open；是否波及 1.20.1 存疑）。（来源：https://github.com/Noobanidus/lootr/issues ）
  - [EF兼容备注] 与 FTB Quests：官方追踪器无 1.20.1 确认冲突。

### 7. Sophisticated Backpacks（精妙背包）｜mod id: sophisticatedbackpacks
- 名称/作者：P3pp3rF1y、WinDanesz、Ridanisaurus
- 1.20.1 Forge：支持
- 协议：未查到
- 已知问题：
  - [崩溃级·存疑] 近期仍有崩溃修复记录：更新后新建世界崩溃（#1768）、打开创造背包崩溃（#1766）、与 Create 打包器 StackOverflowError（#1770），均已关闭；但 issue 未标注 MC 版本（疑为 1.21.x NeoForge），对 1.20.1 仅作"作者响应快、同类崩溃可修"的参考。（来源：https://github.com/P3pp3rF1y/SophisticatedBackpacks/issues ）
  - [体验级] 1.20.1 Forge 专项检索未见确认的复制漏洞与性能缺陷报告（搜索无果，非确认清白）。

---

## 六、世界类

### 1. Terralith｜mod id: terralith
- 名称/作者：Stardust Labs
- 1.20.1 Forge：支持
- 协议：Stardust Labs License（自定义，非开源许可）
- 已知问题：
  - [体验级] 与 Tectonic 同用会生成错误区块/巨大地形"墙"，官方解决方式是移除 Tectonic（#171）。（来源：https://github.com/Stardust-Labs-MC/Terralith/issues/171 ）
  - [体验级] Forge 下 FPS 随时间掉到 10-20（特定朝向触发，已关闭，#242）；warm_river 群系卡顿（#235）。（来源：https://github.com/Stardust-Labs-MC/Terralith/issues/242 、#235 ）
  - [体验级·存疑] 区块地形缺失/不完全生成（#249；报告版本为 1.20 Fabric，1.20.1 Forge 未确证）。（来源：https://github.com/Stardust-Labs-MC/Terralith/issues/249 ）
  - [小毛病] 与 Faithful Backrooms 不兼容（已修复，#236）。（来源：同仓库）
  - [EF兼容备注] 与 YUNG 系列：未查到确证冲突案例；与 Distant Horizons 官方兼容（DH 描述列明支持 modded terrain）。官方"Terralith: No Structures"关闭结构可作为冲突规避手段。（来源：https://www.mcmod.cn/class/24632.html ）

### 2. [ETN] Epic Terrain（史诗地形）｜mod id: epicterrain
- 名称/作者：Wonderful艾晨；另有第三方兼容补丁"史诗地形兼容版 (Epic Terrain Compatible)"（SodaMC/潮涌核心，Modrinth sc69VpnK）——用户标注的 "Epic Terrain Compatible" 应对应该补丁
- 1.20.1 Forge：支持
- 协议：BY-NC-SA 3.0
- 已知问题：
  - [崩溃级] Beta 阶段存在不兼容与崩溃，页面明确"**不建议用于生存**"。（来源：https://www.mcmod.cn/class/15808.html ）
  - [体验级] 页面注明**与 TerraBlender 不兼容**——若整合包含 TerraBlender 系群系 mod 需特别注意。（来源：同上）
  - [体验级·存疑] 河流生成存在问题，需置顶加载顺序规避。（来源：https://sodamc.com/128860-00041600.html ）
  - 补丁侧印证：第三方"Epic Terrain Compatible"更新后才"可尝试玩生存"，侧面说明原版处于不可完整生存状态。（来源：https://pd.qq.com/g/6b4851a96d/post/B_c54c2e6764f905001441152187666108800X60 ）

### 3. [RW] RoadWeaver（阡陌交通）｜mod id: roadweaver
- 名称/作者：作者 shiroha（GitHub: shiroha-233/RoadWeaver）
- 1.20.1 Forge：支持
- 协议：MIT
- 已知问题：
  - [崩溃级] Forge 1.20.1 上与 Integrated Villages 同用会破坏世界生成：区块预生成未完成即继续（#90，open）。（来源：https://github.com/shiroha-233/RoadWeaver/issues/90 ）
  - [崩溃级] 旧版本启动即服务器崩溃（LWJGL 模块冲突，已修复，#84）。（来源：https://github.com/shiroha-233/RoadWeaver/issues/84 ）
  - [体验级] 与 Tectonic V3 不兼容；旧版 C2ME 下出现浮空树；加载慢/地图空白。（来源：https://www.mcmod.cn/class/22551.html ）
  - [小毛病] 道路直接穿过结构生成（#89）；水域道路处理不佳（#68）。（来源：同仓库）

### 4. YUNG's Better 系列结构（四件套）｜mod id: yungs（组合未指明）
- 名称/作者：YUNG / YUNG-GANG。**用户未指明具体四个**，按 1.20.1 Forge 常见组合调研：Better Dungeons / Better Mineshafts / Better Strongholds / Better Ocean Monuments（另可选 Desert Temples、Witch Huts、Nether Fortresses）；均需前置 YUNG's API
- 1.20.1 Forge：支持
- 协议：LGPL-3.0-only
- 已知问题（系列共性，1.20.1 Forge 为主）：
  - [体验级] Better Mineshafts 在模组自定义群系中浮空生成（Alex's Caves 的 Abyssal Chasm，[1.20.1] 标注，open）——同类地形适配问题在任意自定义地形/群系 mod（含 Terralith）组合下都可能复现。（来源：https://github.com/YUNG-GANG/YUNGs-Better-Mineshafts/issues/99 ）
  - [小毛病] Better Dungeons 1.20.1 版曾"无战利品"（已修复，#84）。（来源：https://github.com/YUNG-GANG/YUNGs-Better-Dungeons/issues/84 ）
  - [崩溃级·存疑] Better Dungeons #67 启动/点击崩溃（报告为 1.20.1 Fabric，Forge 未确证）。（来源：https://github.com/YUNG-GANG/YUNGs-Better-Dungeons/issues/67 ）
  - [体验级] Better Mineshafts 更新 mod 后旧世界损坏（#102，细节不详）。（来源：https://github.com/YUNG-GANG/YUNGs-Better-Mineshafts/issues/102 ）
  - 与 Terralith 之间未查到确证结构重叠报告；**结构悬空/嵌入地形是 YUNG 系列在自定义地形下的主要风险点**。

### 5. Distant Horizons｜mod id: distanthorizons
- 名称/作者：James Seibel / jeseibel
- 1.20.1 Forge：支持
- 协议：LGPL-3.0-only
- 已知问题：
  - [崩溃级] Forge 1.20.1 上 **Oculus 1.7.0 + DH 2.2.0-a 启动即崩溃**；解决：改用 DH 2.1.2-a 或 Oculus 1.6.15a。（来源：https://github.com/Asek3/Oculus/issues/683 ）
  - [体验级] 光影支持有版本门槛（Forge 侧依赖 Oculus 配对版本）；LOD 生成期掉帧/卡顿，需调 JVM 参数或加大内存，生成慢的反馈常见。（来源：https://modrinth.com/mod/distanthorizons ）
  - [体验级] "overloaded, too many chunks queued for updating"（LOD 更新队列过载提示）时有出现。（来源：https://wenku.csdn.net/answer/77p446kakm ）
  - [体验级] LOD 数据库文件体积巨大，拖慢存档备份，服务器场景尤甚。（来源：https://bbs.mcmod.cn/forum.php?action=printable&mod=viewthread&tid=21461 ）
  - [小毛病] 与 Cubic Chunks 不兼容；与 Alex's Caves 需改配置。（来源：https://www.mcmod.cn/class/5009.html ）
  - 与 Terralith 兼容（DH 官方描述支持该类 modded terrain）。

---

## 高风险 TOP3

**TOP 1 — Epic Fight 20.14.17 附属/兼容链（系统性风险，贯穿全包）**
- Epic Knights（magistuarmory）**硬依赖 EF API**：EF 缺失或版本不匹配即 NoClassDefFoundError 启动崩溃（GitHub #69，open）。
- Iron's Spellbooks：与 EF 同用曾致服务端随机崩溃（#787 已修，但历史十余个 EF 兼容 issue，风险集中）。
- Simply Swords：EF 同装启动崩溃先例（#309 已修）；无官方 EF 动作组，右键技能可能不触发。
- Cataclysm：本体 Boss 无 EF 动画，需社区补丁；其法术附属 T.O Magic 'n Extras 与本体崩溃需专用修复补丁。
- slu（souls-like universe）与 Dawnday：**官方发布页已删/不可达**，与 20.14.17 的版本匹配完全无法核实。
- 建议：锁定 EF 20.14.17 不轻易升级，附属逐一进存档实测；优先采用有社区 EF 适配数据包生态的组合（Bosses'Rise、Simply Swords、Cataclysm 均有）。

**TOP 2 — Epic Terrain（史诗地形，epicterrain）**
- 官方页面明示 Beta 阶段崩溃、"不建议用于生存"；**与 TerraBlender 不兼容**（包内若有 TerraBlender 系群系 mod 即踩雷）；必须依赖第三方 "Epic Terrain Compatible" 补丁才可生存，且河流生成需加载顺序规避。崩溃级风险全组最高。

**TOP 3 — Blood And Madness（bloodandmadness）**
- 1.20.1 停更两年以上（v2.1.5.2，2023-06）；GitHub #5 实测服务端 TPS 掉至 8–13、本 mod 占 35–40% 服务器性能（open），#7 Lag、#4 刷怪异常均未关闭；装 EF 后线杖/兽斩两武器无动画，对 EF 20.14.x 无官方表态。性能与 EF 兼容双重风险，建议配置限制刷怪+压测后再定去留。

**候补关注**（未进 TOP3 但需留意）：
- Bosses of Mass Destruction：Void Blossom 战斗崩溃且崩后无法进存档（Forge 1.20.1 实测，未修复 #164）。
- Relics：两条 1.20.1 open 崩溃（SporeEntity CME #254、皮革腰带客户端崩溃 #262）。
- Spore：感染扩散无总开关（地形破坏不可逆）+ 感染实体堆积性能负担，需调 Despawning 配置。
- Legendary Monsters：三个崩溃 issue 仅见于 1.21.1 仓库，1.20.1 未证实，入包需实测 Boss 战与血条。
- Distant Horizons：必须与 Oculus 版本配对（DH 2.2.0-a + Oculus 1.7.0 启动即崩），另有 LOD 生成卡顿与存档体积问题。
- Alex's Mobs / Guard Villagers：1.20.1 均有已修复的崩溃史与遗留性能 issue（AMWorldData #2325、spark #305 仍 open），且两者均已停更或放缓 1.20.1 维护。

*报告完*
