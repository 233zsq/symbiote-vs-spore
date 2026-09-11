# 交接文档 · Symbiote vs Spore

> 最近更新：2026-09-10（阶段②.5 **验收通过并关闭** + 协作拓扑变更）。新会话/新模型接手时先读本文件，再读 `docs/` 下两份方案文档。
>
> **协作拓扑（2026-09-10 起）**：**Kimi Code（K3）= 总设计师/调度者，可直接操控 Qoder 驱动其四个模型执行开发**（经 kimi-cu-win 等本机控制插件操作 Qoder 界面）。Kimi 负责：设计方案、拆解任务、按工作流文档路由模型、把 prompt 喂给 Qoder、审查产物、入库与 commit；Qoder 四模型按原路由表执行。工作流文档（`docs/For User整合包开发AI工作流_模型分配与Prompts.md`）的模型路由与 prompt 库继续有效，但"人工搬运 prompt"环节由 Kimi 代劳；该文档后续按此拓扑重写。

## 1. 仓库快照

- 仓库根 = packwiz 包根 = `D:\mcmp`，分支 `main`，远端未配置（纯本地）
- `pack.toml`：`Symbiote vs Spore` / 作者 233zsq / 版本 0.1.0 / **MC 1.20.1 + Forge 47.4.23（冻结）**
- 已入包模组（`mods/*.pw.toml`，精确文件版本 + sha512）：
  - 核心战斗：Epic Fight **20.14.17**（20.14.x 系列最新；全包 EF 系列冻结基线，禁止单独升级）、Weapons of Miracles **2.0.171**
  - 键位下发：Default Options **18.0.5**（+ 前置 Balm 7.3.42）
  - 阶段②.5 性能栈：Embeddium 0.3.31、FerriteCore 6.0.1、ModernFix 5.27.83、spark 1.10.53、Chunky 1.3.146
  - 阶段②.5 QoL：JEI 15.58.0.209、Jade 11.13.3、Controlling 12.0.2（+Searchables 1.0.3）、AppleSkin 2.5.1
- 已下发配置：`config/epicfight-client.toml`（战斗相机第三人称后背视角）；`config/defaultoptions/keybindings.txt`（EF 六键默认表，详见 3. 决策表）
- 工程文件：`.gitignore`、`.packwizignore`、`CONTRIBUTING.md`、`tools/check_json.py`（JSON 校验）、**`tools/sync_mods.py`（仓库→实例同步，见 2. 标准链路）**

## 2. 环境拓扑（别再踩坑）

| 项 | 位置 / 值 |
|---|---|
| 开发仓库 | `D:\mcmp`（**纯源码，游戏文件永远不该出现**） |
| PCL2 | `D:\mcmp_test\Plain Craft Launcher 2.exe`，游戏目录 = `D:\mcmp_test`，版本隔离已开。**启动游戏 = 直接运行 PCL2 选 `1.20.1-Forge_47.4.23` 启动**；建议分配 6–8 GB 内存；禁用 PCL 的 Mod 管理界面增删模组；仓库有模组变动时先跑 `python tools/sync_mods.py` 再启动 |
| 开发实例 | `D:\mcmp_test\versions\1.20.1-Forge_47.4.23\`（测试实例未建） |
| packwiz | `C:\Users\zhens\bin\packwiz.exe`（nightly.link 的 Actions 构建；官方无 Releases） |
| packwiz-installer | 实例目录内 `packwiz-installer.jar`；**必须经 bootstrap 启动**（直跑弹窗报错） |
| Java / Python / pwsh | 17.0.12 / 3.13.0 / 7.6.6 |
| 代理 | TUN 模式：curl/git 直连 OK；**Java okhttp 的 HTTP/2 会被掐断**（EOFException），curl 大文件也会断 → 一律 `--http1.1` + `--retry` |

模组入包 → 实例的标准链路（2026-09-10 起定型）：
1. 仓库侧：`packwiz modrinth install -y <slug>`（精确冻结版本；依赖自动解析入包）
2. 实例侧：**`python tools/sync_mods.py`**——读全部 `.pw.toml` 经 `curl --http1.1` 下载、sha512 校验后落位实例 `mods/`，并检测无元数据的"野 jar"。packwiz-installer 的 Java 下载受代理影响失败，不再作为主链路（备选：导出 mrpack 让 PCL 导入）

## 3. 关键决策记录

| 决策 | 结论 | 出处 |
|---|---|---|
| 启动器 | PCL2（版本隔离双实例），模组增删只走 packwiz，禁用 PCL Mod 管理直改 | 方案 1.4 |
| Forge | 47.4.23 冻结 | pack.toml |
| EF 系列 | 锁定 20.14.x，当前 20.14.17 | commit `5d61e46` |
| **键位/配置下发** | **定型：Default Options mod**（`config/defaultoptions/` 只对新安装生效，不覆盖玩家改键；不随包发根目录 options.txt——避免更新冲掉玩家设置）。EF 六键已入表：切战斗=mouse.5、武器固有技能=R、闪避=LAlt、格挡=右键、锁定=G、技能编辑器=K；Symbiote 键位改绑方案见待办池#7（jar 侦察后修正：实际冲突为 R/G/K+T/L 五处，非原估的 V/B 两键） | 阶段②.5 |
| **性能栈时点** | **提前至阶段②.5 入包**（原方案排第四批）：此后一切实测在最终性能/监控环境中进行，避免后期入包导致手感与兼容结论返工；spark 自此常驻支撑 Spore TPS 监控 | 阶段②.5 |
| 原版干预政策 | 【待定】默认完全自由，决策前任何脚本不得碰原版；当前倾向 A（完全不动），阶段⑤实测数据有反例再翻案 | 方案 3.3 |

## 4. 阶段进度

- **阶段① 底座搭建 ✅**：空包启动、pack.toml 入库、首次 commit 全部验收
- **阶段② 核心战斗验证 ▶ 收尾**：手感基准实测通过；已修=战斗相机、键位；处决/体力 jar 级查证 ✅ 完成并回填清单。剩余动作：斧 Guillotine / 匕首 Blade Rush 两项处决复测 → 交 glm5.3flash 整理《战斗手感基准文档》后关闭
- **阶段②.5 开发环境补齐 ✅（2026-09-10 人工验收通过）**：性能五件套 + QoL 四件 + Default Options 入包并同步实例；实例实测：启动无崩溃、Embeddium×EF 战斗动画/渲染正常、Controlling 可见 EF 键位分类、JEI/Jade 生效。此后一切实测均在最终性能/监控环境进行
- **阶段③ 次核心攻坚 ▶ 批1 Symbiote 待实测**：Symbiote **1.1.3**（Modrinth，ARR）已 packwiz 入包 + sync 入实例（2026-09-10，未 commit，实测过线才提交）；jar 侦察已完成（见待办池#7）。实测顺序：Symbiote → Sword Soaring/Nightfall（各占一批单独验证）→ Fungal Infection: Spore；Symbiote 实测同场合并阶段②遗留的处决复测两项。Sword Soaring 在 Modrinth 有官方页（`epic-fight-sword-soaring`，前置 Invincible Lib 已在 Modrinth）；**Nightfall 仅 CurseForge**，入包链路待批2再解。Spore 批次 spark 已就位。每批启动实测过线才 commit
- **批2/批3 入包链路侦察（2026-09-11 K3，Modrinth API 实证）**：Sword Soaring 1.20.1 最新 **20.14.2.8**（2026-04-25，版本号与 EF 20.14.x 同系），依赖 = Epic Fight + Invincible Lib（packwiz 自动解析，EF 已在包）→ `packwiz modrinth install epic-fight-sword-soaring` 即可；**Nightfall 确认不在 Modrinth**（搜索零命中），CurseForge 直连 403 需走 `packwiz curseforge install` 内建通道（若 opt-out 则引导手装），批2 执行时再解；Spore 在 Modrinth（slug `fungal-infectionspore`），1.20.1 最新稳定 **2.2.0j**（2026-06-29 release，无硬前置，2.2.0 系列 62 版迭代极快——锁 j 不再追新）；Spore Inquisition 数据包同在 Modrinth（slug `spore-inquisition`，137k 下载）

## 5. 待办池（按优先级）

1. ~~②.5 实例验证~~ **✅ 已通过（2026-09-10）**：启动无崩溃、渲染正常、Controlling/JEI/Jade 生效
2. ~~处决/韧性机制 + 体力数值查证~~ **✅ 已查证（K3，jar 级证据）**：EF 20.14 无通用"韧性→处决"机制（普通怪无韧性条属预期；处决仅斧 The Guillotine / 匕首双持 Blade Rush 两个固有技能）；体力表=上限 15、翻滚 4/跨步 3、回复 1.5s 延迟+前慢后快共约 5s，与实测全吻合。结论已回填 `docs/EF手感基准测试清单.md`，剩两项处决复测后可交 glm5.3flash 整理基准文档
3. ~~**WoM 汉化缺失**~~ **✅ 初稿已完成（2026-09-11，qoderclicn glm5.3flash×4 分片 + K3 校验）**：自译 zh_cn.json 335 条全键覆盖、占位符/§码零错位，已存 `config/openloader/resources/wom_zh_cn/`（pack_format 15）；**生效依赖 Open Loader 入包**（阶段④工具链），届时进游戏实读一遍校对润色
4. **处决设计缺口（设计决策待定）**：魂系玩家预期"打空韧性→处决"，EF 原生没有；候选：接受现状（以硬直/倒地呈现）/ 引入社区处决数据包或附属 / 阶段⑤用 KJS 自定义处决触发。建议阶段⑤平衡期与格挡手感（待办#6）一并评估
5. **无敌帧难度分档**：用户希望按难度可调——阶段⑤平衡时评估（config 分档或任务奖励切换）
6. **格挡手感**：用户感觉不如成熟整合包——Impactful 附属入包（阶段④）后再评
7. ~~**Symbiote 键位追加**~~ **✅ 已落地（2026-09-11，K3，字节码级确认）**：`SymbioteKeybinds.class` javap 复核——实际 **15 个键位**（原记 16+1 未名系误读，全名录与默认键码逐条提取自 `<clinit>`）。改绑五键已写入 `config/defaultoptions/keybindings.txt`：tendril_yank→Y、living_armor_toggle→I、apex→M、strain_power→;、arm_toggle→'。实测仅需 Controlling 复核 ID 拼写。⚠️ 遗留：apex→M 与阶段④ Xaero's 世界图默认 M 撞键，届时改 Xaero 侧、不动本表。**重大发现（推翻方案 3.9 假设）**：STRESS_*/DEFIANCE_*/OVERRIDE_* 等玩法数值全部**硬编码**（166 项 lambda 常量，不暴露 toml）——劫持调频不能调数值，只能开关行为入口；调频设计见 `docs/Symbiote配置调频设计.md`（EF 战斗安全档：关 hunger_stalk/curiosity/predator_hunt 三类移动劫持，保留救命兜底与 desires 养成），硬编码全表存 `docs/archive/symbiote_1.1.3_hardcoded_tuning.txt`（阶段⑤数值对齐引用源）
8. **packwiz-installer 同步链路**：Java 下载受代理影响，已被 `tools/sync_mods.py` 取代主链路；installer 修复降级为低优先级

## 6. AI 协作要点（新会话必读）

- **拓扑**：Kimi Code 为设计师/调度者并直控 Qoder（见文件头协作拓扑块）；新会话开工顺序 = 读本文件 → 读工作流文档取 P0 上下文块与对应 P 任务 prompt → 由 Kimi 喂给 Qoder 对应模型并审查产物
- 工作流与模型路由：`docs/For User整合包开发AI工作流_模型分配与Prompts.md`（P0 上下文块 + P1–P13 任务 prompts）；K3 窗口到 9.25，仓库级任务优先 K3
- commit 规范：`type(scope): 描述 [模型批次]`；验收不过不 commit
- 红线：EF 版本锁定 / 原版政策【待定】/ ID 与键名现场核实（`/kubejs hand`、options.txt 实读）/ 合规人工拍板 / 实测优先于推断
- 实例同步一律走 `tools/sync_mods.py`；实例 `mods/` 里出现"野 jar"（无 .pw.toml 对应）必须回仓库补 packwiz 手续
- 并行注意：glm5.3flash 可能同时在仓库工作（README、实例配置说明），编辑共享文件前先重读，冲突以现场内容为准
