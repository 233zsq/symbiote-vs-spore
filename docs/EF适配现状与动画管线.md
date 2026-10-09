# EF 适配现状与动画管线（2026-10-07 调查）

> 目的：弄清本包的史诗战斗（Epic Fight 20.14.17，1.20.1）适配是怎么做的、动画包是什么、以及如何自定义动画。
> 证据：215 个 mod jar + openloader 数据包的全量 zip/javap 解析（2026-10-07）。**未做游戏内端到端验证**——本文为资源/字节码级实证。

## 一、三层数据驱动（核心结论）

| 层 | 机制 | 本包实况 |
|---|---|---|
| 武器 capability | `data/<命名空间>/capabilities/weapons/<物品>.json`——极简 JSON：`{"type": "epicfight:sword", "attributes": {armor_negation/impact/max_strikes}}` | **557 个**（imfdata 包）：jerotesvillage 138 / simplyswords 121 / dungeons_and_combat 98 / jerotes 53 / cataclysm 26 / legendary_monsters 23 / bloodandmadness 17（血源武器）/ spore 12；svs 包另有 7 个真菌武器（cleaver/感染弓/弩/枪/锤/军刀/巨镰）。EF 本体自带 48 个原版武器 capability |
| 武器类型 | `data/epicfight/capabilities/weapons/types/<type>.json`——纯 JSON 定义：单双手切换条件（看副手）/连段动画序列 combos/判定盒 collider/命中粒子音效/固有技能 | mowzie_ef_compat 包定义了 dagger、dual_greatsword、slipper 三个自定义类型（先例：**新增武器类别零 Java**） |
| 生物补丁 | `data/<命名空间>/epicfight_mobpatch/<实体>.json`——借骨架+借动画+换渲染器（EF 的 MobPatchReloadListener，jar 字符串实证） | **10-09按.json资源文件重数：SLU74、EFMCompat21、w.o.w6**；此前75/24/7的目录条目数不作为JSON文件数。guardvillagers jar同目录JSON为0，是否Java侧适配另核，不能据零JSON断言无EF动作 |

生物补丁样例（SLU 亚托克斯）：`armature: epicfight:entity/biped` + `renderer: minecraft:zombie` + `default_livingmotions` 指向 `epicfight:biped/living/*`（走动/受击/硬直全借现成动画）+ `attributes.scale: 2.0`。

**EF 自带骨架**（jar 内 animmodels 目录实证）：biped（人形）+ zombie / skeleton / spider / enderman / piglin / illager / ravager / iron_golem / wither / wither_skeleton / vex / dragon / creeper——原版生物开箱即用。

**证据边界**：原调查在spore/cataclysm/jerotes怪物资源层未见对应通用mobpatch；此项不能排除Java侧或兼容附属的行为，不能仅由JSON缺失断言全走原版AI。新怪物适配范围/外观/战斗接管仍待裁决（规格书_EF怪物适配）。

## 二、附属动画包的作用（本包动画量榜，全 jar 合并）

`efn(nightfall) 875 / epicfightx(extra) 855 / wom 761 / epicfight_dd 607 / epicfight 本体 523 / cdmoveset 359 / epicfight_awaken 174 / womplus 171 / sword_soaring 141 / wukong 117 / refm 80 / woc_remastered 72 / p1nero_ec 68 / MobsPlus 60 / …`

四类作用：①武器连段动画库（capability 的 type 指向谁的动画，决定手感）；②生物骨架与动作（super_warden 给监守者、MobsPlus-EFM、Resurrection 魂系 boss）；③技能/固有技体系（SLM 三件套=写被动/技能/固有技的框架）；④纯兼容数据（EFMCompat、mowzie_ef_compat、epicfighttinkercompat）。

## 三、自定义动画的官方管线

1. **Blender 3.6 + EF 官方 JSON 导出插件**：`Antikythera-Studios/blender-json-addon`（支持 2.79~5.0，安装/教程见官方 wiki `epicfight-docs.readthedocs.io/uk/Guides/page2/`）；旧分支 `Yesssssman/blender-json-exporter`（3.6）。骨架文件从 EF Discord 取。
2. **导出格式**（jar 内实证）：骨骼名 + 时间数组 + 变换矩阵的 JSON，放 `assets/<命名空间>/animmodels/animations/<骨架>/<名>.json`（单个攻击动画 ~20KB）。导出时选 Attribute 格式（官方推荐，优于 Matrix）。
3. **落地 = 纯数据**（不碰 Java、不碰 jar）：资源包放动画 + 数据包 types/combos 引用 + 武器 capability 指过去——本包走已验证的 `config/openloader/` 通道即可。mowzie dagger 为先例。
4. **caveat**：mowzie 兼容包的类型引用了 `redirected_epicfight:*` 这类重定向 id，全包扫描无同名资源文件，字面量在 SLM-EpicFight/lazy_utilities 的 `EpicFightAssetsAccessorFinder` 类中——该机制未端到端验证；**自建类型时动画 id 应指向自产的明确资源**.

## 四、视频/AI转动画（原10-07工具线索，未作本轮现时核验）

原调查记录的候选流程：拍视频 → 云端出 FBX/BVH → Blender 重定向到 EF 骨架 → EF 插件导出 → 资源包。

| 工具 | 定位 |
|---|---|
| **Rokoko Vision**（rokoko.com/products/vision） | 免费单机位（FBX/BVH），升级版 Rokoko Create 带文字生成动作（历史线索，不是当前推荐） |
| Plask | 带手部捕捉，原调查记有手部捕捉；现额度未核 |
| Move AI | MoveOne/2~6 台 iPhone，生产级，可实时流 UE |
| DeepMotion Animate 3D | 原调查候选；现额度/价格未核 |
| 国内 V2Fun / 千面 | 云端视频动捕 |
| **Cascadeur**（现价格未核） | 非生成器：AI AutoPosing/AutoPhysics 打磨力量感动作；B 站 1.20.1 教程即 Cascadeur→EF 桥接流程 |

**三个坑**：单机位有脚滑/遮挡错误要手修；EF 骨架重定向要处理命名映射（Root/torso/head/arm.L/R…）；位移类动作要做**原地化**（root motion 归零，否则游戏里滑步）。

## 五、对本包的应用面

- **武器专属连段**（如血源 6 武器/终局神兵）：最小闭环 = Blender 动画 → 资源包 + 一个 type JSON + capability 指过去；先单武器打通链路再批量。
- **给真菌精英怪/boss 加 EF 动作**：写 mobpatch 借 biped 骨架 + 复用 EF 动画（SLU 同款做法），纯数据；需先确认怪的攻击动画与命中判定不冲突（mobpatch可能接管战斗行为，不能保证仅改表现；按现草案先获批实验验证）。
- **参考综合文档联动**：`docs/武器线与匠魂节奏_参考综合.md` 里各参照包的武器手感设计，需要用自定义动画落地时按本文管线执行。


## 六、旧差距与生物方案合并后的使用边界

- [9-21差距分析](archive/2026-10-09_整理前/EF适配差距分析.md)：武器1331/已适配947等为当时采样；“jerotes零覆盖、mobpatch零个”的旧结论不能覆盖后续imfdata与兼容件变化。旧表侧重API/采样标记，本报告侧重资源文件，均不是运行时完整验收。
- [9-22生物方案](archive/2026-10-09_整理前/生物EF适配方案.md)：19Boss/72小怪及“preset一行就必做”是旧建议；非人形“不可能适配”的绝对表述不沿用，现只在当前范围排除，无对应骨架则需另做骨架/动画。
- 两份旧报告独有的候选实体/统计数字原文完整保留，但不进入现执行队列；当前只认[搁置规格](规格书_EF怪物适配.md)的五问和批准条件，不能把本报告“纯数据可行”当用户批准。
- 静态JSON计数使用“包含/epicfight_mobpatch/且以.json结尾”口径；Java实现、资源覆盖顺序、模型/外观和实际AI行为仍须各自验证。本轮没有生成JSON或启动游戏。
- 外部工具版本、导出插件支持范围、服务额度与价格仅为原调查线索，执行前再核；本文不安排购买服务或新增动画工程。
