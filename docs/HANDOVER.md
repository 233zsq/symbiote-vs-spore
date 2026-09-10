# 交接文档 · Symbiote vs Spore

> 最近更新：2026-09-10（阶段②.5 落地）。新会话/新模型接手时先读本文件，再读 `docs/` 下两份方案文档。

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
| PCL2 | `D:\mcmp_test\Plain Craft Launcher 2.exe`，游戏目录 = `D:\mcmp_test`，版本隔离已开 |
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
| **键位/配置下发** | **定型：Default Options mod**（`config/defaultoptions/` 只对新安装生效，不覆盖玩家改键；不随包发根目录 options.txt——避免更新冲掉玩家设置）。EF 六键已入表：切战斗=mouse.5、武器固有技能=R、闪避=LAlt、格挡=右键、锁定=G、技能编辑器=K；Symbiote 键位（拟 V/B）待其入包后追加进同一文件 | 阶段②.5 |
| **性能栈时点** | **提前至阶段②.5 入包**（原方案排第四批）：此后一切实测在最终性能/监控环境中进行，避免后期入包导致手感与兼容结论返工；spark 自此常驻支撑 Spore TPS 监控 | 阶段②.5 |
| 原版干预政策 | 【待定】默认完全自由，决策前任何脚本不得碰原版；当前倾向 A（完全不动），阶段⑤实测数据有反例再翻案 | 方案 3.3 |

## 4. 阶段进度

- **阶段① 底座搭建 ✅**：空包启动、pack.toml 入库、首次 commit 全部验收
- **阶段② 核心战斗验证 ▶ 收尾**：手感基准实测通过；已修=战斗相机、键位。剩余动作：① 处决/韧性机制与体力数值的 jar 级查证（进行中，结论回填实测清单）→ ② 交 glm5.3flash 整理《战斗手感基准文档》后关闭
- **阶段②.5 开发环境补齐 ▶ 待实测**：性能五件套 + QoL 四件 + Default Options 已入包并同步实例；**待人工启动实例验证**：进主菜单无崩溃、Embeddium×EF 战斗动画渲染正常、Controlling 可见 EF 键位、JEI/Jade 生效 → 通过后本阶段关闭
- **阶段③ 次核心攻坚（下一步）**：Symbiote → Sword Soaring/Nightfall → Fungal Infection: Spore，**各占一批单独验证**；Symbiote 实测间隙可并行准备御剑/Nightfall 的入包手续（实测批次仍分开）；Spore 批次 spark 已就位。每批启动实测过线才 commit

## 5. 待办池（按优先级）

1. **②.5 实例验证**：启动开发实例跑一遍（崩溃/渲染/键位/JEI），过线后关闭②.5
2. **处决/韧性机制 + 体力数值查证**：jar 级查证进行中（K3）；结论回填 `docs/EF手感基准测试清单.md` 后交 glm5.3flash 整理基准文档
3. **WoM 汉化缺失**：评估社区汉化资源包或自制 lang 文件（不急，但发布前必须有）
4. **处决机制设计缺口（待查证结论）**：若 EF 20.14 确无处决系统，基准文档需调整预期，评估是否引入社区处决数据包/附属
5. **无敌帧难度分档**：用户希望按难度可调——阶段⑤平衡时评估（config 分档或任务奖励切换）
6. **格挡手感**：用户感觉不如成熟整合包——Impactful 附属入包（阶段④）后再评
7. **Symbiote 键位追加**：入包后把 V/B 改绑写进 `config/defaultoptions/keybindings.txt`（Controlling 现场核 ID）
8. **packwiz-installer 同步链路**：Java 下载受代理影响，已被 `tools/sync_mods.py` 取代主链路；installer 修复降级为低优先级

## 6. AI 协作要点（新会话必读）

- 工作流与模型路由：`docs/For User整合包开发AI工作流_模型分配与Prompts.md`（P0 上下文块 + P1–P13 任务 prompts）；K3 窗口到 9.25，仓库级任务优先 K3
- commit 规范：`type(scope): 描述 [模型批次]`；验收不过不 commit
- 红线：EF 版本锁定 / 原版政策【待定】/ ID 与键名现场核实（`/kubejs hand`、options.txt 实读）/ 合规人工拍板 / 实测优先于推断
- 实例同步一律走 `tools/sync_mods.py`；实例 `mods/` 里出现"野 jar"（无 .pw.toml 对应）必须回仓库补 packwiz 手续
- 并行注意：glm5.3flash 可能同时在仓库工作（README、实例配置说明），编辑共享文件前先重读，冲突以现场内容为准
