# 沉浸战斗：天神剑技适配与坐骑系统研究

2026-10-26，只读研究本地`C:/PCL 正式版 2.8.13/.minecraft/versions/Immersive Fight 4.2.9`。结论只对应这份包，不推定其他版本相同；没有复制其模组到SvS，没有改参考包。

## 1. 天神剑技到底由什么适配

明确是**CELEpic，文件`celepic-1.0.jar`，modId `celepic`**。不是Celestisynth Fix，也不是只改武器类型的普通数据包。

| 部件 | IF本地版本 | SvS/用户候选 |
|---|---|---|
| Epic Fight | 20.14.17 | 20.14.17，保持固定 |
| Celestisynth | 1.3.1 | 候选1.3.4，尚未安装 |
| CELEpic | 1.0 | 未安装，且不能直接配候选1.3.4 |
| Celestisynth Fix | 不以此作为IF适配依据 | 候选0.1，仅清理缓存 |

CELEpic内有七份`data/celestisynth/capabilities/weapons/`能力定义：Aquaflora、Breezebreaker、Crescentia、Frostbound、Keres、Poltergeist、Solaris；配套武器类型、EF技能参数、动画与物品渲染资源。其Java代码注册EF武器能力和技能；Mixin还处理原生使用、蓄力、冷却、攻击位移、相机等。Rainfall Serenity另有Mixin，不应因为七份能力文件就宣称所有武器完整适配。

版本阻断已经明确：CELEpic常量池中26个Celestisynth类引用，全部在IF1.3.1存在，全部在候选1.3.4缺失。例如旧`com/aqutheseal/celestisynth/.../SkilledSwordItem`已迁到`org/thecelestialworkshop/celestisynth/...`。它的required Mixin和普通类调用都会受到影响；这不是只改JSON中的ID就能修好。

此外，它注入EF内部`PlayerEvents.lambda$itemUseStartEvent$10`等方法，说明即使EF版本相同，仍要检查整个附属组合。`mods.toml`没有声明EF强依赖，不代表它能脱离EF运行；宽泛的Celestisynth `[1.0,)`也不能证明二进制兼容。

## 2. 推荐的两条适配路线

| 路线 | 做法 | 评价 |
|---|---|---|
| 旧版成套复现 | 独立测试目录复现IF的CS1.3.1 + CELEpic1.0 + EF20.14.17，并核对所有前置 | 最接近已观察参考，但会放弃1.3.4新增/修复；参考包存在不等于SvS通过 |
| 保留1.3.4 | 寻找作者发布的新版适配，或另做基于当前API的适配层 | 当前推荐长期方向，工作量更大；须覆盖原生技能接管、动画、伤害和镜头，不能只做持握动作 |

本轮不自动切换用户文件版本，不修改CELEpic原JAR。它的许可声明为All Rights Reserved，且没有可用主页/更新链接；已检查用户给的CurseForge检索入口与公开检索，**未核实与本地这份CELEpic对应的独立官方项目链接**。因此不能把猜测的下载页、其他Celestisynth附属或转载当作来源。

候选Fix引用1.3.4的新`CSAnimator`包及三张公开Map，字段核对通过；选旧版路线时不能继续使用这份Fix。无论走哪条路线，都需核对EF普通连段、原生右键、双持/换手、空中招式、锁定、Leawind镜头、EFS-ISS耗蓝、法术和炮塔伤害归因。实战验收交给用户；未做游戏测试。

## 3. 坐骑系统实际分成四层

| 功能 | 本地模组/文件 | 证据与作用 |
|---|---|---|
| 物种与原生骑乘 | Saints Dragons 0.9.5、Alex's Mobs/Caves等 | 各物种自己的驯服、飞行/潜水和攻击逻辑 |
| 通用驯服与骑乘扩展 | **Super Duper Ultra Hyper Tamer**，`superdupertamer-2.0.1-hotfix.jar` | modId `superdupertamer`；能力保存归属、跟随/护主AI、通用骑乘 |
| 收录、召唤、轮盘和管理 | **Find me**，`Find me-1.2.1.jar` | modId **`find_me`**，元数据版本1.2，作者kuzhi；文件名与元数据版本分别记录 |
| Boss首胜后发放驯服副本 | **fight_more**，`fight_more-1.0.jar` + FTB命令奖励 | `/mytamed @s <实体ID>`生成新实体，再调用SuperDuperUtil.tame；不是去驯服场上Boss |

用户看到的“Z键召唤、长按轮盘、右键管理”，直接来自FTB“坐骑系统介绍”与Find me代码。参考包文案明确说明Find me为旧版且有修改，不能自行更新。这是包内定制版本的证据，不能替未核实的公共同名版本背书；也不能误认成用来找箱内物品的同名工具。

FTB文件`config/ftbquests/quests/chapters/787F35DCD2AFA778.snbt`中，碎船兽、锐爪兽、肆空龙等奖励均有`/mytamed`命令；设`elevate_perms: true`、`team_reward: false`。`fight_more`注册该命令时要求权限等级2，创建实体后调用通用驯服，并另调用自身的驯服生命增益逻辑。只复制FTB命令、只装Find me、或只装Tamer都不能复现这条完整流程。

## 4. 参考配置不是照搬模板

`config/super-duper-tamer.toml`的当前值：

- blacklist：`monsterexpansion:skrythe`、`rhyza`、`alexscaves:hullbreaker`、`monsterexpansion:ignathos`。
- `forceTame=true`，`handTame=false`；ridingBlacklist为空。
- 尸壳有腐肉驯服、80%概率、移动速度0.3和治疗量1等单独条目；`tameable.json`为空对象。

这些不是“全包只允许驯服尸壳”的证据。通用缰绳与命令是另外的入口；尤其`SuperDuperUtil.tame`本身没有黑名单检查，`fight_more`直接调用它，因此黑名单不自动约束命令奖励。参考包正是把部分野生Boss拉黑，再通过任务生成已驯服副本。

不宜原样移植的原因：SvS的Boss已有首胜、难度、围城、归因和重战流程。通用驯服可能改变敌对分类、AI、队友伤害与掉落；Boss副本还可能再次触发击杀奖励，召唤系统还涉及跨维度/卸载、同一UUID和死亡恢复。参考包的多层搭配是实现范例，不是我们已验收的机制。

## 5. SvS可以借鉴什么

建议先保留原生圣龙/未来龙之书的驯服和骑乘，只增加“已拥有坐骑的收录与召回”体验；采用可核实来源、许可与版本的实现，或制作轻量适配。先提供少量白名单物种，再决定是否扩展普通陆地/水生坐骑。

不默认开放野生Boss驯服。若以后做“首胜奖励坐骑”，使用明确的坐骑副本标记，排除首胜/悬赏/围城计数，禁复制战利品、禁战斗中重置血量，存取与召回由服务端校验主人和UUID。不得把世界中的主线Boss直接转换为宠物。原生龙和通用Tamer二选一管理同一个实体，避免两套主人/AI状态争用。

建议验收顺序：正常上下骑乘→保存重进→卸载区块后召回→跨维度→死亡与释放→双人归属→EF状态/Leawind相机。用户当前没有第二位玩家，联机继续保留待验。本轮只整理方案，未制作坐骑奖励或改FTB。

## 6. 证据入口

[原始JAR与参考配置盘点](data/模组9审查_2026-10-26.json)保存SHA-256；[专项证据](data/模组9专项研究_2026-10-26.json)列CELEpic类引用及Find me/fight_more选取的类。详细核对文件位于`backups/mods9_review_20261026/decompiled/`、`reference_resources/`。

官方原模组入口：[Celestisynth](https://www.curseforge.com/minecraft/mc-mods/celestisynth)、[Fix](https://www.curseforge.com/minecraft/mc-mods/celestisynth-fix)。CELEpic、Find me定制版和fight_more的确切分发来源本轮未核实；已知本地文件不等于获得修改/公开重分发许可。关联：[本批审查](模组9审查与合入建议_2026-10-26.md)、[DND方案](Otherworld_DND职业等级借鉴方案_2026-10-26.md)。
