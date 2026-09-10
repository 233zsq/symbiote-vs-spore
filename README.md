# Symbiote vs Spore

> 《我的世界》战斗 & 冒险整合包，以 **Epic Fight（史诗战斗）** 为战斗底座。
> 叙事主线「**以共生对寄生**」即包名由来——体内养成一个会反抗你的共生体（Symbiote），体外对抗一场不断进化的真菌天灾（Fungal Infection: Spore）；御剑修仙（Sword Soaring）与 Nightfall 动作武器提供 EF 原生战斗纵深。
>
> 版本基线：**Minecraft 1.20.1 + Forge 47.2.20+ · Java 17 · packwiz + Git 源码化管理**
> 作者：233zsq

## 项目简介

本包采用「1 个核心特色 mod + EF 附属战斗扩展层 + 3 个次核心支柱 + 数个大型内容 mod + 刚需辅助 mod」的结构。Epic Fight 将原版战斗重构为动作游戏式实时战斗（连段、翻滚、格挡、体力、技能树），是承托一切的战斗底座；次核心层支撑「体内共生体 vs 体外真菌天灾」的题材钩子；Boss、结构、维度类大型模组提供探索舞台。

设计上强调**引导式冒险与阶段成长**：任务线把「下矿备装 → 攻略低阶地牢 → 缔结共生体 → 挑战首个 Boss → 解锁新维度 → 迎击 Calamity 级天灾」串成成长阶梯，并通过关闭地图传送、重构指南针成本、道路网引导等手段重建「旅程本身即是内容」的冒险体验（详见方案 3.7）。

## 版本基线

| 项目 | 基线 |
|---|---|
| Minecraft | 1.20.1 |
| 加载器 | Forge 47.2.20+ |
| Java | 17（统一发行版，推荐 Temurin 17） |
| 内存 | 开发实例 6–8 GB；发布门槛：最低 4 GB / 推荐 6–8 GB |
| 开发工具 | Prism Launcher（开发/测试双实例）、packwiz、Git、spark |

## 内容体系

完整清单见方案第 2 章（共 106 个唯一条目：88 个功能模组/数据包 + 18 个前置库）。

| 层 | 代表模组 | 角色 |
|---|---|---|
| 核心特色 | Epic Fight（锁定 20.14.x） | 战斗底座 |
| EF 附属层 | Impactful、Battle Arts、Resurrection、Indestructible、Epic Foes（附属五件套）、Weapons of Miracles、CompatLink、EFMCompat | 打击感、流派、武器池、怪物 EF 化、武器适配主力 |
| 次核心 | Symbiote（共生体养成）、Sword Soaring / EpicFight-Nightfall（御剑修仙与动作武器）、Fungal Infection: Spore（真菌天灾） | 「以共生对寄生」主线 |
| 大型内容 | L_Ender's Cataclysm、暮色森林、Alex's Caves、Iron's Spells、Epic Knights、Saint's Dragons（推荐，赶路向）、Tinkers' Construct（仅工具向） | 探索舞台与装备线 |
| 刚需辅助 | JEI、Jade、AppleSkin、Sophisticated Backpacks、Xaero's 地图、Lootr、性能栈（Embeddium / Canary / FerriteCore / ModernFix / Spark / Chunky） | 体验与性能兜底 |

**装备流程（v4 改版）**：原版装备线（木/石 → 铁 → 钻石 → 下界合金）全程自由，干预政策【待定】；模组装备组织为 **9 条武器线**（主线锻造 / 暮色 / 御剑修仙 / 共生体强化 / 匠魂搭配 / 动作武器收藏 / 中世纪军备 / 法术 / 感染装备），每条线按「入门 → 进阶 → 大成」节点推进；阶段门控只锁模组内容，共五阶段：Ⅰ 启程 → Ⅱ 深入下界 → Ⅲ 暮色森林 → Ⅳ 真菌天灾升级 → Ⅴ 终局（方案 3.3 / 3.5）。

## 快速开始（开发者）

1. 前置：Prism Launcher、Java 17（Temurin）、[packwiz](https://packwiz.infra.link/)。
2. 克隆仓库后，在 Prism 建立 1.20.1 + Forge 47.2.20+ 实例，经 packwiz-installer 按 `pack.toml` 拉取模组（或用 packwiz 命令行同步）。
3. 仓库骨架（pack.toml、.gitignore、目录、提交规范、JSON 校验脚本）由仓库脚手架初始化任务建立，纪律细节见 `CONTRIBUTING.md`。

## 文档导航

| 文档 | 说明 |
|---|---|
| `docs/整合包开发方案_v4_装备流程改版.md` | **权威方案**：模组清单、魔改方案、工程实践、发布合规、路线图 |
| `docs/For User整合包开发AI工作流_模型分配与Prompts.md` | 多模型分工、任务分级路由、参考 Prompt 库（P0–P13） |
| [`docs/实例配置说明.md`](docs/实例配置说明.md) | 方案中示例配置/脚本的逐份详解：作用、落位、生效方式、验收清单 |
| `CONTRIBUTING.md` | 仓库纪律：分批添加、提交规范、EF 版本锁定红线（脚手架任务维护） |
| `docs/archive/` | 历史方案归档（v3 及更早，冲突时以 v4 为准） |

## 硬约束速查（红线）

1. **EF 版本锁定**：Epic Fight 全系列锁定 20.14.x，禁止单独升级本体或任一附属；任何 EF 升级必须触发全量武器动作回归测试。
2. **原版干预政策【待定】**：决策落地前，任何脚本与门控不得改动原版配方、数值与门控。
3. **门控只锁模组内容**：阶段门控不触碰原版装备流程。
4. **ID 即真理**：一切物品 ID、配置键名以 `/kubejs hand`、`/ct hand`、F3+H 现场核实为准，未核实不进版本库。
5. **分批添加**：模组分批入包、每批完整启动实测、每批一次 commit。
6. **世界生成先定型**：Terralith 等世界生成在正式存档创建前冻结，不在已有存档中途追加。
7. **次核心【需实测】**：Symbiote / Fungal Infection: Spore / Saint's Dragons 与 EF 无公开共存先例，相关改动首发前逐项实测。

## 许可与发布提示

发布走 CurseForge / Modrinth / MC百科三渠道。发布前须逐一核对每个模组的许可证与 modpack 条款：FTB 系仅限 CurseForge 分发；opt-out 模组引导玩家手动下载而非打包 jar；RoadWeaver 存在版权争议需单独评估。详见方案第 5 章。
