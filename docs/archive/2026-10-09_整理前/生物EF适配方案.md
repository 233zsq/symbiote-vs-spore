# 生物 EF 适配方案（未适配 Boss/生物清单 + 做法）

> 数据源：test4 实测 941 个实体（敌对 560）。EF 适配定义：mod 字节码引用 EF API（EF 原生附属）。
> 日期：2026-09-22。

## 〇、先说三个前提

1. **原版生物不用我们做**：EF 20.14 自带原版人形怪（僵尸/骷髅/掠夺者等）的 mobpatch，minecraft 命名空间那 37 个"未适配"是统计口径问题，实际已被 EF 本体覆盖。
2. **mobpatch 只对人形怪有意义**：双足直立体型才能套 EF 玩家动画骨架。龙、真菌巨兽、蠕虫、多段体 Boss 做不了也不该做。
3. **我们包里有两个加载器**：
   - **indestructible → `advanced_mobpatch`**（DOTE/IF 同款格式）：完整自定义——模型/渲染器/体力/硬直/格挡/行为树/阶段切换
   - **CombatEvolution → `ce_mobpatch`**：CE 自己的 AI 补丁格式，偏行为层

## 一、Boss 级优先适配清单（P0，主线要打的人形 Boss）

| Boss | mod | 血量/攻击 | 适配建议 |
|---|---|---|---|
| 加斯科因神父 | bloodandmadness | 1000/12 | **必做**。血源招牌人形 Boss，advanced_mobpatch 玩家模型+斧/枪双阶段 |
| 噩梦之主密寇赖许 | bloodandmadness | 1500/12 | 必做，人形，法系动作组 |
| 焰魔 Ignis | cataclysm | 450/14 | 必做。DOTE 已把它当决斗 Boss 用，人形大剑模板 |
| 先驱者 | cataclysm | 390/9 | 人形机械，做 |
| 咒翼灵骸 | cataclysm | 420/13 | 人形，做 |
| 末影守卫 | cataclysm | 333/16 | 人形守卫，做 |
| 钢铁守护者 | mowziesmobs | 40/30 | 人形骑士（DOTE 同款已做过），preset 引用即可 |
| 太阳鸟·乌姆武提 | mowziesmobs | 150/2 | 双足鸟人，可做（DOTE 做过） |
| 巫妖 | twilightforest | 100/3 | 人形法师，做（暮色章节主线 Boss） |
| 冰雪女王 | twilightforest | 200/7 | 人形，做 |
| 米诺菇 | twilightforest | 120/2 | 双足牛头，可做 |
| 堕落圣骑 | legendary_monsters | 400/15 | 人形骑士 Boss，做 |
| 无头骑士 | legendary_monsters | 195/10 | 做 |
| 死者之王 | irons_spellbooks | 500/10 | 人形，做（提洛斯前置线） |
| 无名守卫者 | eeeabsmobs | 350/15 | 做 |
| 不朽者 | eeeabsmobs | 400/12 | 待定（体型可能非标准人形） |
| 沉降领主 | jerotesvillage | 170/6 | 做 |
| High Priest / Pyro Knight | dungeons_and_combat | 320/240 | 人形，做 |
| 卡玛斯 / 苏蕾娅 | dungeons_and_combat | 320/320 | 待定（体型待确认） |

**不建议做**：下界合金巨兽、利维坦、斯库拉、暝煌龙、撼地斯拉、圣龙全系、Spore 大型感染体（破舰魔/菌械空堡等）、黑夜君临系——非人形骨架，EF 不适用，用数值/机制平衡即可。

## 二、精英/小怪级清单（P1，preset 引用式 mobpatch 即可）

格式极简（`{"preset": "minecraft:zombie"}` 一行继承原版 EF 动作），适合做一批：

- **spore 菌染人形系**（11 个）：菌染村民/僵尸村民/卫道士/唤魔者/女巫/掠夺者、菌骑士、铁斧投手、邪菌术士——preset 各对应原版同族。**这批最划算**：菌线全程都在打人形感染体，做完真菌战手感质变
- **jerotesvillage**（12 个）：二轮僵尸/骷髅、行刑者、女巫系、术士系
- **twilightforest**（12 个）：狗头人、骷髅德鲁伊、巨魔、牛头人、哥布林骑士、幽灵等
- **legendary_monsters**（10 个）：守卫/骑士系小怪
- **eeeabsmobs**（7 个）：不朽骷髅系、死尸村民
- **irons_spellbooks**（6 个）：邪教徒、高位唤魔者、狩魔人卫道士等
- **block_factorys_bosses**（4 个）：海盗系、灵魂骷髅
- **alexscaves**（4 个）：深潜者骑士/法师、甘草女巫
- **dungeons_and_combat**（4 个）：血腥教徒、隐士女巫等
- **cataclysm**（3 个）：炽燃狂魂、渊灵祭司
- **symbiote**（1 个）：感染僵尸

小计约 **72 个**，preset 引用式每个 1 个 JSON 搞定。

## 三、落点与格式规范

- 路径：`config/openloader/data/imfdata/data/<modid>/mobpatch/<实体路径>.json`（preset 式）或 `.../advanced_mobpatch/<实体路径>.json`（完整自定义式）
- preset 式内容：`{"preset": "minecraft:zombie"}`（或 pillager/vindicator/skeleton/wither_skeleton，按原型选）
- advanced_mobpatch 参考 DOTE：`config/paxi/datapacks/StellarisCraft/data/jobinsmobs/advanced_mobpatch/*.json`（阶段化武器动作组写法）
- Boss 级建议附数值字段：max_stamina / impact / armor_negation / stun_shield，体力条让 Boss 战有架势博弈

## 四、工作量估计与建议顺序

| 批 | 内容 | 文件数 | 预计 |
|---|---|---|---|
| 1 | P1 preset 式 72 个（脚本批量生成） | 72 | 半小时（脚本） |
| 2 | P0 人形 Boss advanced_mobpatch（照 DOTE 模板改） | ~19 | 每个手工调，分批做 |
| 3 | 进游戏实测手感、调体力/硬直数值 | — | 迭代 |

先做批 1 性价比最高（菌线+暮色小怪立刻 EF 化）；批 2 按主线章节顺序做（暮色 Boss → 血源 → 灾变 → 其他）。
