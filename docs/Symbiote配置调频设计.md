# Symbiote 1.1.3 配置调频设计（阶段③批1 配套）

> 2026-09-11 K3，全部证据来自 `symbiote-1.1.3.jar` 字节码（`com.scout.symbiote.config.SymbioteConfig`，javap -v 提取）。
> 用途：阶段③批1 实测后的 config 落地依据；今晚实测只需确认实例首次启动生成的 `symbiote*.toml` 键名/分组与本文一致。

## 0. 推翻原假设的关键发现

方案 3.9 ①的调频设想是"下调压力积累速度、上调劫持触发阈值"——**不成立**：
`STRESS_*` / `DEFIANCE_*` / `OVERRIDE_*` / `LIVING_ARMOR_*` 等全部玩法数值是 `SymbioteConfig` 里的**硬编码常量**（166 个 lambda 供应器，见附录），**不暴露在 toml**。

config 实际暴露的只有两类杠杆：
1. **行为开关**（布尔）：逐项启停各种"夺取身体"行为——这才是劫持调频的真正抓手；
2. **阶段阈值与杂项**：阶段 Bond 阈值、死亡机制、陨石坑密度等。

## 1. 可调键清单（define 键 · 默认值已确认）

| toml 键 | 默认 | 含义（字节码注释译） |
|---|---|---|
| bond_decay_per_day | 0 | 无 Bond 事件时每日 Bond 流失 |
| stage_integrated_bond | 120 | Attached→Integrated 阈值 |
| stage_cooperative_bond | 240 | Integrated→Cooperative（开始 defy 你） |
| stage_dominant_bond | 400 | Cooperative→Dominant（力量最大、失控最多） |
| crater_rarity | 16 | 陨石坑密度倍率（2=减半，4=1/4…） |
| rejection_chance | 0.1 | 缔结时被样本反杀的概率 |
| control_struggles | **false** | Dominant 短暂夺方向盘（出厂已关） |
| defiance_shoves | **false** | 无预警 defiance 物理推动身体（出厂已关） |
| fire_panic_pull | true | 着火恐慌后物理把身体拉出火 |
| fire_panic_contact_only | true | 仅真的着火/在岩浆里才恐慌 |
| hunger_stalk_range | 64.0 | 饥饿且无猎物时强制行走找食物，**0=禁用** |
| walk_door_rip | true | 强制行走撞木门时撕门（铁门始终挡停） |
| walk_terrain_bite | true | 强制行走被地形卡住时咬碎挡路方块 |
| drowning_save_enabled | true | 溺水时夺体上浮换气 |
| suffocation_dig_enabled | true | 掩埋时臂破土自救 |
| freeze_escape_enabled | true | 细雪冻结时破雪自救 |
| desires_enabled | true | 共生体主动提要求（喂食/猎杀/下矿/夜空/被穿戴） |
| desire_hints | true | 需求的灰色提示 |
| curiosity_enabled | true | 对新物种好奇，**有时会拽你走过去看** |
| fidget_enabled | true | 久站时的触手小动作（纯表现） |
| slam_enabled | true | 被两个近身威胁夹击时抓起来对撞 |
| protect_allies | true | Lash/猎食跳过驯服宠、命名生物、玩家 |
| jealousy_enabled | true | 对其他玩家/宠物/村民 lingering 时吃醋 |
| death_keeps_bond | false | true=死亡不断羁绊（与 death_mass 互斥） |
| death_mass_enabled | true | 死亡后共生体守尸（含全部物品），回去 rebond |
| mantle_moods_enabled | true | Cooperative+ 肩部触手随情绪姿态变化 |
| predator_hunt_enabled | true | Predator 菌株**夜间夺体巡游** |
| tendril_cap | 200 | 单维度触手上限（40–2000） |
| verbose_logging | false | 调试日志（报告 bug 时开） |
| tendril_overlay | true | 屏幕边缘触手膜（客户端） |
| sculk_echo_blips | true | 声波回响钻石粒子（客户端） |

## 2. 本包调频方案（EF 战斗安全档）

设计目标（方案 3.9）：劫持应是"疏于养成的惩罚"与"救命兜底"，**不能在 EF Boss 战中随机夺走移动/输入**。硬编码数值动不了，就关掉所有**无预警移动劫持**的行为入口：

```toml
# config/symbiote-common.toml（实际文件名/分组以首启动生成物为准，【待核实】）
# —— 移动劫持四件套：全关 ——
hunger_stalk_range = 0.0        # 饥饿强制行走找食：禁用（0=禁用是官方给的语义）
curiosity_enabled = false       # 好奇拽人：关
predator_hunt_enabled = false   # Predator 夜间夺体巡游：关
sleep 相关无可调键，见 §3 遗留
# —— 强制行走的衍生破坏：随行走禁用而失效，仍显式关闭防漏 ——
walk_door_rip = false
walk_terrain_bite = false
# —— 出厂已关，复核保持关闭即可 ——
control_struggles = false
defiance_shoves = false
# —— 保留项（救命兜底，不动）——
# fire_panic_pull / drowning_save / suffocation_dig / freeze_escape：保命机制，触发条件苛刻，保留
# slam_enabled：替玩家反击的防御 override，是收益不是打断，保留
# desires_enabled / desire_hints：养成线核心（任务线教学素材），保留
# jealousy / mantle_moods / fidget：纯表现与情绪，保留
```

保留劫持感的叙事闭环：desires（忽略→Stress 积累）+ 救命 override + Living Armor 体系仍在，共生体"有脾气"的体验不丢；被删掉的只是"探索/Boss 战中突然被拽走"的负体验。

## 3. 硬编码、改不了的风险项（需实测评估）

| 项 | 硬编码值 | 风险 | 处置 |
|---|---|---|---|
| SLEEP_TAKEOVER_BASE_CHANCE | 0.2 | 睡觉 20% 概率被夺体（表现待核实） | 实测观察；若恶劣，回退项=任务线教学"睡觉前的状态管理"，极端项=KJS 拦截 |
| LOW_HEALTH_OVERRIDE_HP_FRAC | 0.2 | 低血量自动 override（救命向） | 保留，属保命机制 |
| DEFIANCE_BASE_CHANCE / INTERVAL | 0.25 / 600t | Cooperative 起 defiance 频率 | 移动类已随 defiance_shoves=false 关掉，言语类保留 |
| STRESS_HIGH_THRESHOLD | 70 | 高压阈值 | 改不了；靠任务线教学 Stress 管理 |
| 共生体 Stamina/DR/伤害全套 | 见附录 | 数值平衡 | 阶段⑤对齐武器线时引用附录表 |

## 4. 今晚实测配套动作

1. 首次启动实例后，把生成的 `config/symbiote-*.toml` 与 §1 键名对照（重点：分组名、hunger_stalk_range 是否为 Double 键）。
2. 实测记录第 2 节"劫持"项按新认知观察：移动劫持只剩 救命类/desires 衍生 应触发不到"被拽走"（在 §2 配置落地后）。
3. 配置文件下发方式【待定，实测后拍板】：defaultconfigs/ 随包下发（对新存档生效）或直接进 config/ 随包（强制所有玩家）。倾向 defaultconfigs/，与 Default Options 同一哲学。

## 附录 · 硬编码数值全表（166 项，javap -v 提取自 lambda 供应器）

> 用途：阶段⑤ 武器线数值对齐、共生体强度评估、任务线设计的唯一事实源。改不了，只能引用。

全表（166 项）：`docs/archive/symbiote_1.1.3_hardcoded_tuning.txt`。节选关键项：

- Bond/Trust：BOND_MAX=500；击杀+1/喂食+1/睡觉+2/救命+2；TRUST 服从+1/违抗+2/override 助益+3/受损+4
- Hunger：日耗 25；生肉+15/敌对击杀+5；饥饿阈值 15
- Stress：着火 4/t、低血 1/t、衰减 1/60t；高压线 70；忽略需求 +8
- 阶段阈值：120 / 240 / 400（BOND_MAX 500）；复活最低 Bond 275、休眠 12000t
- 共生体体力：60/85/115/150（按阶段）；回复 1/8t；技能耗 Yank18/Cling12/Lash30/Carapace28/Frenzy50/Apex65/Consume33
- 技能参数：Lash 范围4.5 CD60t；Carapace 80t/400t；Frenzy 100t/1200t；Apex 200t/2400t；Consume CD120t 上限目标HP100
- Living Armor：体力100；减伤 0.5/0.65/0.8（按阶段）；自动 Lash 45t/3.0/5.0；荆棘3.0；单次受击上限 0.5（Royal 0.4）
- 菌株：Predator 伤1.4/饥耗1.5/触手CD×0.6；Royal 伤1.5/defiance×1.6/减伤+0.1；Guardian 减伤+0.05；Shadow 夜速+0、白日Stress+1；Sculk 声波抗0.5、感知+8
- Strain 技能（默认关 STRAIN_POWERS_ENABLED=0）：Aegis/Rupture/Nightstep/Screech/Onslaught 全套耗体与参数
- 其他：Slam 10.0伤/5.0范围/600t；Bell 半径16 眩晕8s Stress+15；村民恐惧（阶段≥3，范围8）；铁傀儡敌视 Dominant
