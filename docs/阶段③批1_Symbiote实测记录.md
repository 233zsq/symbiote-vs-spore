# Symbiote: A Bonding Experience 1.1.3 实测记录（阶段③批1 · 人工实测用）

> 日期：____（待填）
> 测试环境：PCL2 实例 `1.20.1-Forge_47.4.23`（版本隔离已开），模组 = Epic Fight **20.14.17** + Weapons of Miracles **2.0.171** + Symbiote: A Bonding Experience **1.1.3** + 性能五件套 Embeddium / FerriteCore / ModernFix / spark / Chunky + QoL JEI / Jade / Controlling / AppleSkin + Default Options。
> 测试方法：对齐《EF手感基准测试清单》——创造+生存各开一个存档；每项记录 ✅通过 / ⚠️异常 / ❌失败 + 一句话备注。**顺序：先在默认键位下做第 3 节"键位冲突实爆"，再按第 1 节改绑方案改绑后复测全项。**
> 依据与纪律：Symbiote 机制项以官方 FAQ 为依据；键位为 jar 侦察数据（K3，2026-09-10 修正：实际冲突为 R/G/K + T/L 五处，非原估的 V/B 两键）。键位 ID 与实际行为以进游戏 Controlling 现场核实为准，**不许凭记忆**；超出本模板给出信息的表现一律标【待核实】。

---

## 0. 准备项（进游戏先做）

- [ ] 实例能正常启动到主菜单（崩溃则先走 P2 归因流程）
- [ ] Mod 列表确认与头部清单一致（重点：Symbiote 1.1.3 在列）
- [ ] Controlling 里找到 Symbiote 分类，逐条核对第 1 节键位表并回填键位 ID
- [ ] 确认 `config/defaultoptions/keybindings.txt` 当前内容（EF 六键已在表：切战斗=mouse.5、武器固有技能=R、闪避=LAlt、格挡=右键、锁定=G、技能编辑器=K）

## 1. 键位核实表（15 键 · jar 侦察已确认全名录）

> 冲突背景见头部。改绑落地方式：已按改绑方案追加进 `config/defaultoptions/keybindings.txt`（jar 级确认，进游戏后仅需在 Controlling 复核 ID 拼写一致）。
> **2026-09-11 K3 复核修正**：`SymbioteKeybinds.class` 字节码确认共 **15 个键位**（原记 16 +1 未名系误读，无未名键）；默认键码逐条提取自 `<clinit>`，与下表一致。

| 功能名 | 键位ID（jar 字节码已确认，Controlling 复核即可） | 默认键 | 冲突对象 | 改绑方案 | 实测结果 |
|---|---|---|---|---|---|
| Tendril Yank（触手拉拽/弹射） | `tendril_yank` | R | EF 六键表·weapon_innate_skill | 改绑 **Y**（已入表） | 待填 |
| Wall Cling（贴墙攀附） | `wall_cling` | C | 无 | 保持默认 | 待填 |
| Living Armor 开关 | `living_armor_toggle` | G | EF 六键表·lock_on | 改绑 **I**（已入表） | 待填 |
| 径向菜单 | `radial_menu` | X | 无 | 保持默认 | 待填 |
| 喂食 | `feed` | B | 无 | 保持默认 | 待填 |
| Tendril Lash（触手鞭击，细节待现场核实） | `tendril_lash` | Z | 无 | 保持默认 | 待填 |
| Carapace（功能待现场核实） | `carapace` | H | 无 | 保持默认 | 待填 |
| Frenzy（功能待现场核实） | `frenzy` | J | 无 | 保持默认 | 待填 |
| Apex Form（顶端形态） | `apex` | K | EF 六键表·skill_gui | 改绑 **M**（已入表；⚠️ 阶段④ Xaero's 世界图默认也是 M，届时把 Xaero 侧改走，不动本表） | 待填 |
| Consume（吞噬） | `consume` | U | 无 | 保持默认 | 待填 |
| Strain Power（与 strain 资源相关，细节待现场核实） | `strain_power` | T | 原版聊天 | 改绑 **;**（已入表） | 待填 |
| 臂槽分配 | `arm_assign` | O | 无 | 保持默认 | 待填 |
| 臂 mantle 收放 | `arm_toggle` | L | 原版进度 | 改绑 **'**（已入表） | 待填 |
| 共生体建造（墙/桥/楼梯） | `arm_wall` | N | 无 | 保持默认 | 待填 |
| graft_ask（功能待现场核实；en_us 名为 "Ask the Graft to strike"） | `graft_ask` | V | 无 | 保持默认 | 待填 |

## 2. Symbiote 核心机制实测（官方 FAQ 依据）

- [ ] **小行星发现与 bonding**：找到小行星并完成初始绑定。实测结果：待填
- [ ] **INTEGRATING 整合期（约 20 分钟）**：整合期内的表现（外观/行为/能否操作）。实测结果：待填
- [ ] **X 径向菜单**：Protect Me / Hunt / Hide 三指令；Status 面板显示 strain / stage / mood / Bond / Trust / Stress / Hunger。实测结果：待填
- [ ] **B 喂食**：手持肉喂食，观察各状态条变化。实测结果：待填
- [ ] **G Living Armor 开关**：开关正常，外观变化符合预期。实测结果：待填
- [ ] **R Tendril Yank**：拉怪 / 弹射两种用法。实测结果：待填
- [ ] **C Wall Cling**：贴墙攀附。实测结果：待填
- [ ] **U Consume**：吞噬。实测结果：待填
- [ ] **K Apex Form**：顶端形态。实测结果：待填
- [ ] **O 臂槽分配**：分配/更换臂槽。实测结果：待填
- [ ] **L mantle 收放**：收起/放出 mantle。实测结果：待填
- [ ] **N 共生体建造**：墙 / 桥 / 楼梯。实测结果：待填
- [ ] **请求系统**（共生体向玩家发起）：要肉 / 要猎杀 / 要下矿 / 要夜空狩猎 / 要被穿戴——逐项记录触发与响应。实测结果：待填
- [ ] **劫持（hijack）**：表现含按键失灵、被带走、挖洞、强制注视——记录触发条件（Bond/Trust/Stress 等状态关联）与解除方式。触发条件：待填；表现：待填；解除方式：待填
- [ ] **死亡后 rebond**：死亡后共生体守在死亡点，重新 bonding。实测结果：待填

## 3. Symbiote × EF 兼容实测

- [ ] **渲染**：EF 战斗模式下 Symbiote 触手 / Living Armor 渲染是否正常（Embeddium 环境下）。实测结果：待填
- [ ] **劫持 × EF 输入**：劫持发生时 EF 战斗模式的输入表现（战斗动作/技能键是否受按键失灵影响）。实测结果：待填
- [ ] **键位冲突实爆（改绑前）**：R/G/K 分别同时按下，观察 EF 与 Symbiote 双方是否都触发——R：EF weapon_innate_skill & Tendril Yank；G：EF lock_on & Living Armor；K：EF skill_gui & Apex Form。实测结果：待填
- [ ] **改绑后复测**：Y / I / M / ; / ' 五键生效，EF 六键与原版聊天/进度不再被 Symbiote 占用，无新冲突。实测结果：待填
- [ ] **吞输入**：EF 战斗动作（连段/翻滚/格挡）进行中，Symbiote 技能是否吞输入（反向亦测）。实测结果：待填

## 4. EF 处决复测（阶段②遗留两项）

> 依据：jar 级查证（2026-09-10，K3）——EF 20.14 真正的处决只有两个武器固有技能（证据链见《EF手感基准测试清单》第 6 节）。

### 4.1 斧类 The Guillotine

- 步骤：取斧类武器 → 将怪打到残血（低于本击伤害）→ 按固有技能键（EF 六键表中 = R）。
- 预期：即死斩杀，耗 **24** 体力。
- 实测结果：待填

### 4.2 匕首双持 Blade Rush

- 步骤：双持匕首 → 连击叠 **3 层"不稳定"** → 锁定目标（EF lock_on = G）→ 释放技能。
- 预期：触发终结动画，耗 **25** 体力。
- 实测结果：待填

## 5. 异常记录（崩溃/卡死/吞输入/渲染错误）

> 日志位置：实例目录 `D:\mcmp_test\versions\1.20.1-Forge_47.4.23\` 下 `logs/latest.log`、`logs/debug.log`、`crash-reports/`。

| 现象 | 复现步骤 | 日志位置 | 处理（留空给归因） |
|---|---|---|---|
| | | | |
| | | | |

## 6. 实测结论（测完填）

- Symbiote 1.1.3 三项关键实测（键位 / 劫持 / 渲染）是否过线：待填
- 是否 commit 留包（不过线 → 启动降级预案 P12）：待填
- 改绑方案是否按第 1 节落地追加进 `config/defaultoptions/keybindings.txt`：待填
- 遗留问题：待填
