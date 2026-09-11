// ============================================================================
// scripts/stages.zs —— GameStages 五阶段门控框架（方案 3.5「阶段化门控」）
// 技术底座：CraftTweaker 14.0.x（ZenScript）+ GameStages + Recipe Stages（+Bookshelf）
// 阶段授予：FTB Quests 里程碑任务的命令奖励执行 gamestage add（对照表见文件末尾）
// 配套设计稿：docs/任务线章节框架.md
// ============================================================================
//
// ★ 铁律（置顶，先于一切阶段调用）★
// 1. 本文件只门控【模组内容】；原版配方/物品（minecraft:*）一律不进门控。
// 2. 原版干预政策【待定】（方案 3.3 原版自由带：候选 A 完全不动 / B 仅 EF 侧对齐 /
//    C 极端项微调）。决策落地前（阶段⑤平衡实测拍板）禁止任何原版条目进入本文件；
//    木/石 → 铁 → 钻石 → 下界合金全程保持原版节奏、零门控零修改。
// 3. 本文件只负责「锁定」；阶段「授予」只发生在 FTB Quests 里程碑任务的命令奖励。
// 4. 凡标【待核实】的 ID，未在游戏内经 /ct hand（或 F3+H）核实前保持注释状态，禁止启用。
//
// 阶段总览（stage id ←→ 中文对照 ←→ 解锁里程碑，对应方案 3.5 表格）：
//   stage1_departure   Ⅰ 启程         进入世界（由序章「觉醒」收官任务授予）
//   stage2_nether      Ⅱ 深入下界     首次进入下界
//   stage3_twilight    Ⅲ 暮色森林     击败凋灵
//   stage4_calamity    Ⅳ 真菌天灾升级  击败暮色主线 Boss
//   stage5_endgame     Ⅴ 终局         共生体 Dominant（Bond≥400）+ 首个 Calamity 讨伐
//
// 语法说明：mods.recipestages.Recipes.addRecipeStage("阶段", <item:...>)
//   语义为「把全部产出该物品的配方锁进指定阶段」；若该物品配方尚未编写
//   （如 kubejs 自注册物品的锻造配方还在 server_scripts 待落地），调用为无害空操作，
//   配方落地后自动生效。物品使用/持有的锁定走 Item Stages、维度锁定走 Re-Dimension
//   Stages（CrT 集成 API 均为【待核实】，核实前不写入调用，仅在本文件以注释登记意图）。

// ----------------------------------------------------------------------------
// 阶段Ⅰ stage1_departure（启程）
// 中文对照：Ⅰ 启程；解锁里程碑：进入世界（序章「觉醒」收官任务授予）
// 本阶段门控内容（方案 3.5 表格）：
//   - 序章任务发放起始武器并教学 Epic Fight 操作（加成性质，不替代原版合成）
//   - Symbiote 坠星事件开放，进入 Attached 养成期（世界事件，非配方门控；
//     事件时点若需与阶段挂钩，机制【待核实】）
//   - 中世纪军备线（Epic Knights）基础件开放：方案 3.3 定为「无额外门控」，不设配方锁
//   - 动作武器收藏线（Nightfall/Resurrection/WoM/Battle Arts）基础件开放：
//     基础件经任务/战利品投放，不走配方锁
//   - 原版装备线（木/石→铁→钻石→下界合金）全程不设门控（干预政策【待定】，默认自由）
// 实际锁定：无。stage1 主要作为任务进度锚点存在，配方锁待阶段⑤逐线落地时补。
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// 阶段Ⅱ stage2_nether（深入下界）
// 中文对照：Ⅱ 深入下界；解锁里程碑：首次进入下界
// 本阶段门控内容（方案 3.5 表格）：
//   - 圣龙传说驯龙系统解锁（打晕驯服与骑乘；解锁属生成/驯服配置层而非配方阶段，
//     挂接方式【待核实】；EF 骑乘崩溃需 Mount Fix）
//   - 御剑修仙线技能书发放启动（技能书为任务奖励投放，不走配方锁）
//   - 下界向模组装备开放（下界主题武器等；配方锁待 ID 核实后补）
//   - 真菌感染维持低调生成率（sporeconfig 压制，配置层职责，非本文件）
// 示例占位（【待核实】，核实后逐条启用）：
// mods.recipestages.Recipes.addRecipeStage("stage2_nether", <item:待核实:下界主题武器>);  // 【待核实】下界向模组装备配方
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// 阶段Ⅲ stage3_twilight（暮色森林）
// 中文对照：Ⅲ 暮色森林；解锁里程碑：击败凋灵
// 本阶段门控内容（方案 3.5 表格）：
//   - DimensionStages 开放暮色森林维度：维度门控走 Re-Dimension Stages（API【待核实】），
//     核实前不写入本文件，仅在此登记意图：暮色森林维度拦截至 stage3_twilight
//   - 暮色武器线全链开放：铁木装 → 骑士金属/钢叶 → 炽焰装
//   - 主线锻造线中间产物（淬魔钢坯）配方解锁（本包自注册物品，见下方已启用调用）
//   - TiC 高阶武器材料解锁（玛玉灵等；冶炼炉/部件打造此前全开放，仅武器线门控，方案 3.9 ⑤）
// 示例占位（【待核实】，核实后逐条启用）：
// mods.recipestages.Recipes.addRecipeStage("stage3_twilight", <item:twilightforest:ironwood_sword>);      // 【待核实】
// mods.recipestages.Recipes.addRecipeStage("stage3_twilight", <item:twilightforest:knightmetal_sword>);   // 【待核实】
// mods.recipestages.Recipes.addRecipeStage("stage3_twilight", <item:twilightforest:fiery_sword>);         // 【待核实】
// mods.recipestages.Recipes.addRecipeStage("stage3_twilight", <item:tconstruct:manyullyn_ingot>);         // 【待核实】TiC 高阶武器材料（锭/熔融形态 ID 待核实）
// 已启用：本包自注册中间产物（kubejs/startup_scripts/items.js），配方落地后自动纳入本阶段
mods.recipestages.Recipes.addRecipeStage("stage3_twilight", <item:kubejs:tempered_steel_billet>);
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// 阶段Ⅳ stage4_calamity（真菌天灾升级）
// 中文对照：Ⅳ 真菌天灾升级；解锁里程碑：击败暮色主线 Boss
// 本阶段门控内容（方案 3.5 表格）：
//   - Mound 活跃化：放开 Mound 坠落/生成事件频率（Spore Inquisition 定点制 +
//     sporeconfig/In Control! 按阶段切换，配置层职责；切换机制【待核实】）
//   - Calamity 级 Boss 解锁（Sieger/Howitzer 等生成放开；同上，配置层）
//   - CDU 与防线装备配方解锁（CDU=冷却驱散装置；Spore 未入包，ID 全部【待核实】）
//   - 感染装备线（Living/Flesh 装备）随讨伐进度开放（ID【待核实】）
// 示例占位（【待核实】，Spore 入包后经 /ct hand 核实再启用）：
// mods.recipestages.Recipes.addRecipeStage("stage4_calamity", <item:待核实:CDU装置>);       // 【待核实】冷却驱散装置
// mods.recipestages.Recipes.addRecipeStage("stage4_calamity", <item:待核实:Living装备>);    // 【待核实】Living 装备
// mods.recipestages.Recipes.addRecipeStage("stage4_calamity", <item:待核实:Flesh装备>);     // 【待核实】Flesh 装备
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// 阶段Ⅴ stage5_endgame（终局）
// 中文对照：Ⅴ 终局；解锁里程碑：共生体达成 Dominant（Bond≥400，硬编码阈值见
// docs/Symbiote配置调频设计.md 附录）且完成首个 Calamity 讨伐（双重硬条件，
// 由阶段Ⅴ 里程碑任务检查并授予；Dominant 检测实现方式【待核实】）
// 本阶段门控内容（方案 3.5 表格）：
//   - abyss_ingot 终局锻造（主线锻造线毕业）→ 本包自注册物品，见下方已启用调用
//   - 共生体终局战斗能力（Dominant 形态，模组内部机制，无需配方门控）
//   - 动作武器收藏线终局件投放（Nightfall/Resurrection/WoM 经任务/战利品投放，
//     不走配方锁；如需锁「使用」再评估 Item Stages，API【待核实】）
//   - 灾变 Boss 讨伐最终挑战（Cataclysm Boss 生成/进度挂钩，非配方门控）
// 示例占位（【待核实】）：
// mods.recipestages.Recipes.addRecipeStage("stage5_endgame", <item:待核实:收藏线终局武器>);  // 【待核实】如个别终局件需配方锁
// 已启用：本包自注册终局材料（kubejs/startup_scripts/items.js），配方落地后自动纳入本阶段
mods.recipestages.Recipes.addRecipeStage("stage5_endgame", <item:kubejs:abyss_ingot>);
// ----------------------------------------------------------------------------

// ============================================================================
// 【FTB Quests 里程碑任务 → gamestage 授予命令对照表】
// 用法：在对应里程碑任务的奖励表中添加「命令奖励」（command reward），
//       选择器 @p 以完成任务玩家为中心解析，即授予本人（SevTech 先例）。
//       阶段名必须与本文件上方 stage id 完全一致。
//
//   序章「觉醒」收官任务（EF 教学完成 + 起始武器领取）：
//       gamestage add @p stage1_departure
//   战斗成长章Ⅱ 里程碑「第一次踏上下界」（到达类任务）：
//       gamestage add @p stage2_nether
//   战斗成长章Ⅲ 里程碑「击败凋灵」：
//       gamestage add @p stage3_twilight
//   战斗成长章Ⅳ 里程碑「击败暮色主线 Boss」：
//       gamestage add @p stage4_calamity
//   战斗成长章Ⅴ 里程碑「共生体 Dominant + 首个 Calamity 讨伐」：
//       gamestage add @p stage5_endgame
//
// 注意：维度门控（暮色森林）与 Mound/Calamity 生成切换不在本表——分别走
// Re-Dimension Stages 与 sporeconfig/In Control!（见各阶段注释，机制【待核实】）；
// 方案 3.5 的「阶段授予任务同时执行配置热切换/难度档触发」另立实现清单。
// ============================================================================
