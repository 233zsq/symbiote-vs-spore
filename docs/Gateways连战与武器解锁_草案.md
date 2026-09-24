# Gateways Boss Rush 连战 + EF 武器解锁 · 规格草案

> 依据：任务文档设计理念 12 + 决议一-7——"重点武器初始锁技能，Gateways Boss Rush 连战（终局支线）击败对应人形 Boss『解放全部力量』，奖励毕业级材料"。
> **本表是草案，待拍板后实施。**

## 0. 前置：mod 未进包（需你先点头）

- **Gateways to Eternity 未安装**（副本/test4/仓库 pw 均无）。1.20.1 Forge 最新线 4.x（Shadows_of_Fire），需前置 **Placebo**（也未装）
- 加 mod 要过开源协议审查（任务一流程）：Gateways = MIT（待核实）、Placebo = MIT（待核实）
- 若确认：CF 直链下载 + pw 条目 + 双写 + 审查登记，一波做完

## 1. 武器解锁制（机制已定，名单待裁决）

- 机制：重点 EF 武器的**技能**初始锁（GameStages `svs_weapon_<名>`，AStages/Item Stages 落地），Boss Rush 过门奖励执行 `gamestage add` 解锁
- 锁的是"技能/全部力量"不是武器本体——武器照常能拿能挥，解放后才解锁 EF 招式槽/特殊技
- **待裁决：锁哪些武器**。候选池（按"毕业级+有 EF 专属技能"筛）：血源 6 件（兽斩/电锯/手杖系）、SimplySwords 符文独特件、WOM/cataclysmic_arsenal 顶级件。建议每门解放 2~3 件，具体名单你圈

## 2. Boss Rush 三门梯度（人形 Boss 车轮战）

| 门 | 定位 | Boss 候选（数值表实采） | 解锁奖励 |
|---|---|---|---|
| 门Ⅰ 试炼 | B3~B2 人形连战 ×3 | `bloodandmadness:father_gascoigne`(1000 血)、`irons_spellbooks:dead_king`(500) 等 | 武器解放 A 组 + 匠魂顶级材料 |
| 门Ⅱ 轮回 | B1 人形连战 ×4 | `souls_like_bosses:nightlord`(500)、血源二线人形 | 武器解放 B 组 + 毕业饰品 |
| 门Ⅲ 终焉 | B0 混编连战 ×5 | `slu:boss_minecraft_lord`(1000)、`bloodandmadness:micolash`(1500) 等 | 武器解放 C 组 + 大量真菌币/稀有材料 |

- Boss 全部是**人形**（贴 EF 招式对战的主题）；巨兽型（netherite_monstrosity 等）不进连战
- 门的 JSON 走 svs 数据包 `data/svs/gateways/*.json`（waves/entities/rewards 结构以 mod 自带示例校准）
- 门钥匙（gateway pearl）由末期任务线发放，不进战利品表（防逃课提前开）
- **多人**：门奖励按参与判定（Gateways 原生支持附近玩家奖励），解锁 stage 只给完成者

## 3. 待你裁决清单

1. 加不加 Gateways + Placebo 两个 mod（协议 MIT 待核实后登记）
2. 锁武器名单（从第 1 节候选池圈，或指定其他）
3. 三门 Boss 编排（第 2 节候选可换）与每门奖励分量
4. 门钥匙投放点（建议：jerotes 二轮制霸里程碑任务奖励）

## 4. 实施顺序（裁决后）

1. 加 mod + 协议登记 → 验证: 进游戏 /gateways 命令可用
2. 门 JSON ×3 + 实测开门 → 验证: 三门各通一次，奖励到账
3. 武器锁 + stage 挂钩 → 验证: 新档武器技能锁定、过门后解锁
