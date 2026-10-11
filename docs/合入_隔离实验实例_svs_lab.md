# 合入线隔离实验实例 svs_lab（2026-10-11 建立）

> 依据：《刀光与新增模组6_优化合入综合审查》§三"隔离看样必须独立游戏目录" + 2026-10-11 批复（合-3：**用独立游戏目录隔离看样**）。
> 目的：B0–B6 合入试验全部在 `svs_lab` 内进行，**不碰 test**（test 保留给主线编辑器实装 M2.4）。

## 一、实例构成

| 项 | 值 |
|---|---|
| 位置 | `C:\PCL 正式版 2.8.13\.minecraft\versions\svs_lab`（PCL 可直接选；`launch_test4.py --version svs_lab`） |
| 基线 | test 实例全量复制（215 mod + config/kubejs/scripts/resourcepacks 等；**排除** saves/logs/`test-natives`） |
| 身份文件 | `svs_lab.jar` / `svs_lab.json`（json `id` 已改 `svs_lab`） |
| 当前 mods | **217** = 215 基线 + **B2 首批两项**（BadOptimizations 2.4.1 `304007dc…` / 0Pack2Reload 1.0.1 `5d57174a…`；已与 mrpack 索引 SHA-1 逐位核对） |
| options | `pauseOnLostFocus:false`（录制/后台友好）；`resourcePacks:[]`（刀光 B1 基线态） |
| 刀光资源 | `resourcepacks/` 含 IMF-Trail（`a007a050…`）/ IMF-Modify（`a6a08ce0…`）/ epicfightx_better_trail1.5（`20ba4215…`）三个包，**均未启用**（与母本/test 现状一致） |

## 二、套件与换批规则（`svs_lab/_kits/`）

**铁律：换批 = 从 `_kits` 拷入 `mods` → 跑 → 拷出还原**；每批独立验收、失败回退到该批之前。

| 套件 | 内容 | 会话规程 |
|---|---|---|
| `B2_对照副本/` | B2 两项的副本（现已在 mods 内） | A/B：把 mods 里两项移出→测对照；再拷回→测加装；同硬件/世界/画质记加载时间、帧时间、内存 |
| `B3a_SoulsHUD/` | souls_combat_hud-forge-1.3.4.jar | **前置未齐**：先出按键冲突对照方案 + 补 46 缺键，再装 |
| `B4a_匠魂兼容/` | epicfighttinkercompat-20.2.10 + `_旧版20.2.8/` 备份 | 移出 20.2.8 → 拷入 20.2.10（**不可共装**）→ 回归旧工具 NBT/换件/黏液套装/刀光 |
| `B5_看样/` | WOH（单份）/ Oddities / NotSoShrimple / 英雄之证 / Celestisynth | **一次一模组**：拷入一个→创造档召唤看样（模型动作→特效→数值）→移出→下一个 |
| 排除（勿装） | MobsPlus-NeoForge-EFM-21.17.2（NeoForge/1.21 错版）、StreamsReflowing（触 worldgen 冻结） | 留在 `E:\mcmp_test\dl\新加入的模组6\`，禁止拷入 |
| 待补前置 | Anka Mobs 2.0 缺 **vzling**（Forge 1.20.1 版待下载核实，不得用 Fabric/NeoForge 顶替） | 补齐前不装 |

## 三、B1 刀光会话（无新模组；本实例的重点首验）

1. **现状基线录制**（resourcePacks:[]）：创造档取 普通剑/太刀/WoM 武器/匠魂武器 各一件 → 同镜头录：普通连击 + 技能 + 第一/第三人称（有/无光影各一组）。
2. **启用最小刀光范围**：options 里勾选 **仅 IMF-Trail**（IMF-Modify 含大量非刀光内容，**不整包启用**）→ 资源重载（F3+T / 重启）→ 同场景同镜头复录。
3. 判定：轨迹贴合刀刃、无缺贴图/闪烁、关键敌人前摇可辨；如同一动画被多包覆盖，逐个加包做覆盖顺序对照；重载日志无相关错误。
4. 结论只记"现状/差距/是否需要最小补丁"，不需要补丁就不加。

## 四、使用与边界

- **启动前提**：test 的游戏不在运行（避免同机双客户端抢资源）；首次使用需创建/拷入测试世界（关游戏后拷 test 存档副本到 `svs_lab/saves/`，或实例内新建创造档）。
- **绝不同步回母本**：本实例任何改动都只是试验；正式入包（副本+test+仓库）必须另行批复逐批执行。
- 录制/验收证据按 B0 基线层级记录（日志/截图/用户确认）；未实测不写"已验收"。
- 变更本实例的批次状态时，同步更新本文件与《开发计划_执行状态》§六。
