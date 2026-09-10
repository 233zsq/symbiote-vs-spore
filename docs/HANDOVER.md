# 交接文档 · Symbiote vs Spore

> 最近更新：2026-09-10（阶段②收尾）。新会话/新模型接手时先读本文件，再读 `docs/` 下两份方案文档。

## 1. 仓库快照

- 仓库根 = packwiz 包根 = `D:\mcmp`，分支 `main`，远端未配置（纯本地）
- `pack.toml`：`Symbiote vs Spore` / 作者 233zsq / 版本 0.1.0 / **MC 1.20.1 + Forge 47.4.23（冻结）**
- 已入包模组（`mods/*.pw.toml`，精确文件版本 + sha512）：
  - Epic Fight **20.14.17**（20.14.x 系列最新；全包 EF 系列冻结基线，禁止单独升级）
  - Weapons of Miracles **2.0.171**
- 已下发配置：`config/epicfight-client.toml`（战斗相机：`camera_auto_switch=true`、`camera_mode=ALWAYS_BACK`，进战斗自动第三人称后背视角）
- 工程文件：`.gitignore`（全局 `*.jar` + 游戏目录污染防御）、`.packwizignore`（docs/tools/开发文件不进发布包）、`CONTRIBUTING.md`（纪律）、`tools/check_json.py`（JSON 入库校验）

## 2. 环境拓扑（别再踩坑）

| 项 | 位置 / 值 |
|---|---|
| 开发仓库 | `D:\mcmp`（**纯源码，游戏文件永远不该出现**） |
| PCL2 | `D:\mcmp_test\Plain Craft Launcher 2.exe`，游戏目录 = `D:\mcmp_test`，版本隔离已开 |
| 开发实例 | `D:\mcmp_test\versions\1.20.1-Forge_47.4.23\`（测试实例未建） |
| packwiz | `C:\Users\zhens\bin\packwiz.exe`（nightly.link 的 Actions 构建；官方无 Releases） |
| packwiz-installer | 实例目录内 `packwiz-installer.jar`；**必须经 bootstrap 启动**（直跑弹窗报错），bootstrap 在 GitHub `packwiz/packwiz-installer-bootstrap` Releases |
| Java / Python / pwsh | 17.0.12 / 3.13.0 / 7.6.6 |
| 代理 | TUN 模式：curl/git 直连 OK；**Java okhttp 的 HTTP/2 会被掐断**（EOFException），curl 大文件也会断 → 一律 `--http1.1` + `--retry` |

模组入包 → 实例的标准链路（当前）：
1. 仓库侧：`packwiz modrinth install -y <modrinth 版本页 URL>`（精确冻结版本）
2. 实例侧：jar 用 `curl --http1.1` 按 `.pw.toml` 里的 `download.url` 下载，`sha512sum` 比对一致后放实例 `mods/`（packwiz-installer 的 Java 下载受代理影响失败，暂未修；备选：导出 mrpack 让 PCL 导入）

## 3. 关键决策记录

| 决策 | 结论 | 出处 |
|---|---|---|
| 启动器 | PCL2（版本隔离双实例），模组增删只走 packwiz，禁用 PCL Mod 管理直改 | 方案 1.4 |
| Forge | 47.4.23 冻结（1.20.1 最新维护构建；曾被代理缓存的过期元数据误标 47.4.5，已修正） | pack.toml |
| EF 系列 | 锁定 20.14.x，当前 20.14.17 | commit `5d61e46` |
| 键位（实例已改，正式下发机制未定） | 切战斗模式=上侧键(mouse.5)、武器固有技能=R、闪避=LAlt、格挡=右键、锁定=G、技能编辑器=K | 实例 options.txt |
| 原版干预政策 | 【待定】默认完全自由，决策前任何脚本不得碰原版 | 方案 3.3 |

## 4. 阶段进度

- **阶段① 底座搭建 ✅**：空包启动、pack.toml 入库、首次 commit 全部验收
- **阶段② 核心战斗验证 ▶ 收尾**：手感基准实测通过（用户实测：连段/翻滚/格挡/体力/锁定全 y）；已修问题=战斗相机第三人称、键位；遗留待办见下。剩余动作：把已填的 `docs/EF手感基准测试清单.md` 交 glm5.3flash 整理成《战斗手感基准文档》后阶段②关闭
- **阶段③ 次核心攻坚（下一步）**：Symbiote → Sword Soaring/Nightfall → Fungal Infection: Spore，**各占一批单独验证**（方案 4.2）；每批启动实测过线才 commit

## 5. 待办池（按优先级）

1. **WoM 汉化缺失**：评估社区汉化资源包或自制 lang 文件（不急，但发布前必须有）
2. **键位/配置正式下发机制**：Default Options mod vs 随包 `options.txt`——阶段③ Symbiote 改键（R/K 冲突 EF）时一并定型；注意仓库根 `/options.txt` 当前被 ignore，随包下发需先解除
3. **性能栈五件套**（Embeddium/FerriteCore/ModernFix/spark/Chunky）未入包；方案 4.2 排第四批，但阶段① roadmap 说先入——建议阶段③开始前入包（调试与 TPS 监控需要 spark）
4. **处决未触发**：用户实测未发现处决（韧性条不显示）→ 确认 EF 20.14 处决/韧性机制触发条件，写入基准文档
5. **无敌帧难度分档**：用户希望按难度可调——阶段⑤平衡时评估（config 分档或任务奖励切换）
6. **格挡手感**：用户感觉不如成熟整合包——Impactful 附属入包（阶段④）后再评
7. **体力/无敌帧数值查证**：EF 源码/config 可查精确值，派 glm5.3 查证后写进基准文档
8. **packwiz-installer 同步链路**：Java 下载受代理影响，长期方案待修（或改走 mrpack 导出 + PCL 导入）

## 6. AI 协作要点（新会话必读）

- 工作流与模型路由：`docs/For User整合包开发AI工作流_模型分配与Prompts.md`（P0 上下文块 + P1–P13 任务 prompts）；K3 窗口到 9.25，仓库级任务优先 K3
- commit 规范：`type(scope): 描述 [模型批次]`；验收不过不 commit
- 红线：EF 版本锁定 / 原版政策【待定】/ ID 与键名现场核实（`/kubejs hand`、options.txt 实读）/ 合规人工拍板 / 实测优先于推断
- 并行注意：glm5.3flash 可能同时在仓库工作（README、实例配置说明），编辑共享文件前先重读，冲突以现场内容为准
