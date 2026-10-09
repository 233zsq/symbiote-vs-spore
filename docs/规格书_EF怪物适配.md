# 规格书（草案）：EF 怪物适配——真菌与 jerotes

> **状态：搁置 · 待用户裁决（2026-10-07 起草）**。用户指示：暂不拍板、搁置、先留档。**批准前不写任何数据包/JSON/配置**。
> 批准后本文转为规格书并进入执行队列；五问未答期间本文仅作方案记录。
> 依据：EF 官方 wiki（Custom Entity Datapack）+ 本机 215 jar 全量实证（2026-10-07）。证据附录见§八。

## 一、目标

给真菌（spore）与 jerotes 的怪物套用史诗战斗（Epic Fight 20.14.17）的已有动画动作：
- 有原版原型的（感染僵尸/感染村民/感染卫道士 等）→ 套对应家族动作；
- 无原型但为人形骨架的 → 套相似人形家族（zombie/villager/humanoid）；
- 非人形自绘怪 → 本方案建议不碰（见 §四 C 档）。

**明确不做**：不改 mod jar、不写 Java、不动 EF 本体；只通过 openloader 数据包（`config/openloader/data/`）加补丁 JSON。

## 二、机制实证（决定方案边界的四条）

1. **补丁 = 一个 JSON**：`data/<命名空间>/epicfight_mobpatch/<实体>.json`（EF 的 MobPatchReloadListener 目录，jar 字符串实证）。
   字段（wiki + SLU 样例实证）：`preset`（一行借用某原版怪全套）/ `renderer`（借哪个家族的渲染映射）/ `model`+`armature`（动画骨架）/ `isHumanoid`（持械动画）/ `faction`（阵营防友伤；可选值 enderman/piglins/wither/neutral/undead/illager/villager）/ `attributes`（impact/armor_negation/max_strikes/chasing_speed/scale）/ `default_livingmotions`（走跑待机死亡挂点）/ `stun_animations`（受击硬直）/ `combat_behavior`+`behaviors`+`conditions`（攻击连段）。
2. **动画映射靠骨架**：怪模型必须能被目标骨架驱动（标准人形关节）。自绘非人形怪没有对应骨架——硬套走形。EF 官方立场（Werewolves 案例）：自定义骨架=必须配套全新动画。
3. **战斗行为会被接管**：补丁定义怪的近战动画/硬直/击退（`CustomMobPatch` 含 getHitAnimation/getSwingSound/getWeaponHitSound）。对纯近战小怪=表现升级；对带特殊攻击的精英/boss=行为改变，有与自身 AI 冲突的风险。
4. **外观归属待实测**（唯一未钉死的点）：借家族后是"保原模型+贴图、只借动作映射"，还是"渲染形状被替换成借用家族"——静态证据两向（EF 渲染代码 `PatchedLivingEntityRenderer.render(E,T,R,...)` 收原渲染器参数，倾向保原模型；wiki 文字称 renderer"决定实际渲染形状"）。**由实验批定案**。

## 三、先例实证（本包内已通行的三条路）

| 先例 | 做法 | 文件 |
|---|---|---|
| EFMCompat 2.0 | 自定义召唤物一行补丁：`{"preset": "minecraft:skeleton"}` | `data/irons_spellbooks/epicfight_mobpatch/summoned_skeleton.json` |
| SLU（74 个） | 全部 boss/精英：`renderer: minecraft:zombie` + `model: epicfight:entity/biped`——"人形怪一律借僵尸家族" | slu jar 内 74 个 mobpatch |
| guardvillagers / w.o.w | 原调查1/7为目录项口径；10-09精确.json重数：guardvillagers该目录0、w.o.w6；零JSON不能排除Java侧实现 | 对应 jar 内 |

jerotes 的**部分怪模型本就继承原版家族**（`Modeladventurer extends Modelillager`——灾厄系；另有自研人形基类 `Modelhumanoid`）→ A 档同族直通候选。

## 四、分档方案

### 实验批（先做，3 只）
| # | 怪 | 补丁要点 | 验证目标 |
|---|---|---|---|
| 1 | `spore:inf_human` | 完整版：renderer=zombie 家族 + faction=undead | 外观是否保留、动作是否顺、战斗是否正常 |
| 2 | `spore:inf_villager` | 同上（villager/zombie 家族） | 同上 + 与"村民"语义接近度 |
| 3 | jerotes 冒险家（`AdventurerEntity`，illager 系，id 待核实） | `{"preset": "minecraft:vindicator"}` 或 illager 家族完整版 | 同族直通档效果 |

另在实验批顺带验证**轻量档**：只填 `default_livingmotions`+`stun_animations`、不填 `combat_behavior` 是否可行（若可行=怪保留自身 AI 攻击、只在移动/受击时用 EF 动画，"只升表现不改玩法"的理想档）。

### A 档 · 同族直通（低风险）
模型本就继承原版家族的怪：jerotes 灾厄系 / 自研人形基类系。做法=照抄 preset 或 illager 家族参数。

### B 档 · 人形借用（中风险）
真菌感染人形系（模型类名实证，约 14 个候选）：InfectedHuman / InfectedVillager / InfectedHusk / InfectedPillager / InfectedVindicator(hVindicator) / InfectedEvoker / InfectedWitch / InfectedTechno / InfectedHazmat / InfectedDrown / InfectedWanderer / InfectedPillagerCaptain / InfectedZombieVillager / InfectedPlayer。
做法=借 zombie/villager 家族 + 调 scale/faction。**必须等实验批确认外观归属后再铺开。**

### C 档 · 不动（零风险）
非人形自绘怪（真菌：claw 系/leaper/howler 系/griefer/conductor/braiomil/各类 boss 与精英）——无对应骨架，不加补丁。boss 若将来要做，单独评估（轻量档或 Blender 重导 mesh 路线）。

## 五、成本 / 风险 / 验收

- **成本**：每怪一个 JSON（preset 一行 ~ 完整版 ~30 行）；一批 10~20 只 ≈ 半天；实验批 3 只 ≈ 半小时。
- **风险**：①战斗接管改变精英/boss 手感（分档规避）；②外观不确定性（实验批定案）；③与围城系统联动——围城波次撒的就是 spore:inf_* 这批怪，适配后需一次围城夜测（观感/手感/批量刷怪性能）。
- **验收**：进游戏目视（外观/动作/战斗）+ 围城夜测；模板参照 M1 验收标准（日志+实测记录，不靠"文件存在"）。
- **回滚**：删对应 JSON 即回滚，无残留。

## 六、排期建议（待裁决）

独立批次，建议排在 M2 编辑器实装之后（不阻塞主线任务线）；用户如要求插队，实验批可随时先做（半小时）。

## 七、待用户裁决（五问，原文保留）

1. **外观底线**：若实验显示"形状被替换成借用家族"，可接受吗？还是必须保留原模型（→ Blender 重导 mesh 路线，工作量翻倍，只能挑重点怪）？
2. **范围**：真菌只做人形系约 14 种？还是先只做实验批 3 只看效果？
3. **战斗接管**：接受小怪近战被 EF 统一吗？精英/boss 是否排除？
4. **排期**：独立批次排 M2 之后，还是现在插队做实验批？
5. **验收人**：外观/手感由用户进游戏判定（约 5 分钟）——何时有空？

## 八、证据附录

- EF mobpatch 目录与字段：`epic-fight-20.14.17-mc1.20.1-forge.jar` → `MobPatchReloadListener`（字段字符串：armature/attributes/combat_behavior/default_livingmotions/faction/humanoid/isHumanoid/model/preset/renderer/stun_animations/registerCustomEntityRenderer）
- 渲染类：`client/renderer/patched/entity/` 24 个（PZombieVillager/PIllager/PRavager/PHumanoid/PCustomEntityRenderer/PCustomHumanoidEntityRenderer/PresetRenderer…）
- 骨架与动画：`assets/epicfight/animmodels/animations/`（biped/zombie/piglin/spider/enderman/ravager/iron_golem/wither/dragon/illager/vex/creeper 等骨架）
- 三个先例文件路径见 §三；真菌模型类清单见 spore jar `com/Harbinger/Spore/Client/Models/`（244 个）
- 相关调查：`docs/EF适配现状与动画管线.md`（三层数据驱动与自定义动画管线）
- 外部：Epic Fight Wiki（Custom Entity Datapack）、Werewolves #181（自定义骨架兼容性）

> 10-09整理：旧EF差距/生物方案已归档，当前资源计数与证据边界合入EF适配现状与动画管线。本文五问未答状态不变，工作量估计仅原草案判断，不作为排期承诺。
