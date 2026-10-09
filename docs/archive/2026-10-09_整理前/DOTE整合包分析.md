# DUEL OF THE END（终焉决斗）整合包拆解分析

> 分析对象：`C:\PCL 正式版 2.8.13\.minecraft\versions\DUEL OF THE END`（MC 1.18.2 / Forge / EF 18.5.26，260 mod）
> 日期：2026-09-20。注意：该包为 1.18.2/EF18 时代，数据包格式不可直接搬，**借鉴的是设计框架**。

## 一、技术栈分工（魔改主力不在 KubeJS）

| 工具 | 承担功能 |
|---|---|
| InControl `spawn.json`（1843 行） | **数值核心**：按 gamestage × 维度 乘血量/加伤害/配装备 |
| CraftTweaker `crafting.zs`（1134 行） | 配方封禁/重构、ItemStages 物品阶段锁、回复道具加冷却 |
| Paxi 数据包 StellarisCraft | EF 武器 capability 数值、技能体力调平、Boss advanced_mobpatch |
| PropertyModifier | 80 件装备耐久/堆叠/修理材料重写 |
| GameStages（fight_a/b/c/d/e） | 阶段主轴，由 FTB 任务奖励发放 |
| RestrictedPortals | 维度凭证门禁 |
| DeathButThree | Boss 限次击杀（1~5 次） |
| Champions | 随机精英全关，改固定词条精英 |
| 自制 mod | stellariscraft（材料/维度/祭坛）、stellarisdlc（37 把 EF 武器）、jobinsmobs（40 个自制 Boss）、guhao（神器） |

## 二、阶段 × Boss 组成

| 阶段 | 门控 | Boss 阵容 |
|---|---|---|
| T1 主界 | 开局 | 决斗场一梯队（赤焰魔使/黑暗先遣/狂沙之枪）+ 大世界 BOMD/Mowzie 三王 |
| T1.5 决斗场天梯 | 进决斗场 | 森白影魔(130血)→杀戮将军(200)→金焰神王(280)，各发 fight_a/b/c |
| T2 下界 | 下界之证（两部件分挂两条线） | 灾变三 Boss + 凋零×4 + BOMD 手掌 |
| T2.5 蔚蓝 | 蔚蓝之证 | Blue Skies 四 Boss |
| T3 末地 | 末地之证（跨章节拼接解锁） | EF 化末影龙(500血/+50伤) + 末影守卫 + 黑曜巨石柱 |
| T4 终局 | 终焉决斗场 | 凝渊人·流光 → 杀戮将军H（750 血 ×8.0 伤，全包最高压） |
| 连战 | 古老远征 | Gateways 三门 Boss Rush，消耗前序 Boss 掉落物换门票 |

## 三、数值设计要点

- **三圈层**：大世界 Boss 削弱（血×0.2~0.7）当材料靶子 → 决斗场自制 Boss 强化（血×5~15）当真正挑战 → 武器走"高耐久 + EF 参数（穿甲/冲击）微调"而非堆面板。
- **阶段反爬升**：无阶段小怪 ×0.7~0.85（新手保护），fight_c 阶段 ×1.5~2.0 且发铁/钻武器——玩家越强世界越难。
- **玩家侧压血**：SoL Carrot 开局 5 心，吃满 100 种食物才 32 HP——血量成长绑死在生活内容上。
- **双向防秒杀护栏**：AttributeFix 上限 10⁷ + ArmorCurve 减伤封顶（护甲 60%/附魔 45%）+ 灾变系 Boss 单次受伤上限 20~22。
- **回复压制**：心/药水/图腾全部加 10~60s CD，瞬疗和图腾流被明确针对。
- **数值膨胀四道闸**：删铁魔法全配方、锁 ACG/WoM 武器配方进阶段门、技能书掉落率 -100、DeathButThree 限刷。

## 四、FTB 任务书写得好的细节（可照抄）

1. "猜你在搜"副标题给英文结构关键词（配探险家指南针）
2. Boss 描述写"推荐最次装备"准入线，颜色分品质
3. 危招色谱教学（橙危可招架/红危精确闪避/紫刀跳跃/蓝危招架）
4. 每个 Boss 标 BGM 出处 + 隐藏任务击杀后自动 stopsound
5. quest_links 跨章镜像，终局画布聚合前置条件
6. `/say` 广播章节解锁仪式感；尺寸 0.1 的隐藏可重复任务做自动化
7. 属性碎片全包定量 88 个并公开，方便平衡审计
8. 维度"证"拆两部件、分挂两条进度线后强制双线推进

## 五、可借鉴 mod（按主题适配排序，均已核对我方未装）

**难度/阶段管理**
1. Death But Three — Boss 限次挑战，防堆尸磨血（1.20.1 有版）
2. Champions + Extra Champions — 精英词缀，可做"真菌感染精英变体"，接 gamestage
3. Spawn Balance Utility — 刷怪压力曲线
4. Restricted Portals — 维度物品门禁（"净化徽章进感染区"）
5. More MobGriefing Options — 细粒度防爆

**Boss 战机制**
6. Gateways to Eternity — Boss Rush 波次门（连战终局内容）
7. Summoning Rituals — 祭坛配方化召唤 Boss，KubeJS 原生事件，零成本接入
8. Mowzie's Mobs — Boss 设计标杆，自带倍率配置与防磨血机制
9. Blue Skies — 双维度 4 Boss + 独立竞技场结构
10. BrassAmber BattleTowers — 爬塔+塔顶傀儡，可做感染哨塔

**装备/掉落手感**
11. Tiered — 武器随机品质词条+重铸（数据包驱动词条库可直接仿写）
12. Spoorn Armor Attributes — 盔甲随机词条
13. Armor Curve — 减伤封顶公式可直接搬
14. Property Modifier — 纯配置改耐久/实体属性修正（比 kubejs 脚本轻）
15. AttributeFix — 属性上限解放（高倍率环境必须品）
16. Legendary Tooltips + Item Borders + Equipment Compare + Loot Beams — 掉落仪式感四件套
17. Tool Leveling — 武器使用升级

**魂系机制/养成**
18. Baubley Heart Canisters — 心容器闭环（Boss 掉材料→做心）
19. Spice of Life: Carrot Edition — 吃多样性食物涨血上限，联动农夫乐事系
20. Void Totem / Curio of Undying / Better Totem of Undying — 图腾体系
21. Shield Expansion — 盾牌招架窗口配置化
22. Diet — 食物五维 buff 软性养成线

**注意**：DOTE 的 EF 私货 mod（guhao/heaven-burner/skybreaker/star 等）全部是 1.18.2/EF18 时代社区件，与我方 1.20.1/EF20 不兼容，只能借鉴"Boss 即玩家模型 + advanced_mobpatch"的制作范式。
