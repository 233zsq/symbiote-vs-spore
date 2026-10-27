# 借火者之路 · 初行地图 v1

2026-10-14。**独立地图小样，已生成存档；不是完整整合包发行版。**

范围为 2048 × 2048 格，seed `23320261014`，Minecraft 1.20.1 / Forge 47.4.23 / Java 17。单用锁定的 Terralith 2.5.4，Epic Fight 保持 20.14.17。主包模组、任务 SNBT、脚本和世界生成配置没有被替换。

## 第一版包含什么

| 地点 | 作者布置锚点 X/Z | 内容 |
|---|---|---|
| 借火村 | 96 / 24 | 三间木屋、六张床、三位村民、工作台/炉子/锻造台/铁砧、容器、营火和方向路标 |
| 坠星坡 | 664 / 144 | `symbiote:meteor_crash`，距营地约 580 格；原预案坐标落水，已根据真实地形改到陆地 |
| 失联医院 | 640 / 512 | `spore:hospital`，用于感染场景与复杂建筑看样 |
| 砂谷遗迹 | -720 / 568 | `cataclysm:cursed_pyramid`，用于灾变 Boss 场地看样 |

出生位置为 `(96, 69, 28)`。上表是作者调试坐标；游戏中的路标只提示方位与目的地。三个结构按模组原生生成逻辑布置，实际边界、朝向和高程由结构实现决定，不把锚点当作入口位置。

三条道路按实际高度图寻路避水，约 3,000 个道路中心采样点，配路灯与目的地路标；营地和遗迹附近留出缓冲区域。路线不是直线连坐标，具体结果见 `layout.generated.json`。原生 RoadWeaver 背景道路保留。

## 本地交付件与试玩

制作成功后，本机 `artifacts/maps/` 下包含：

- `svs-first-light-v1-world.zip`：地图存档，不含游戏或模组 JAR。
- `svs-first-light-v1.mrpack`：独立试玩安装包，按标准清单下载锁定模组并携带预制存档；可供支持 mrpack 的启动器导入。
- `svs-first-light-v1-preview.png`：从实际 Anvil 区块读取高度/表层后绘制的俯视图。
- `world-audit.json`：区块、道路、床、村民、模组方块实体等存档检查结果。
- `release-manifest.json`：ZIP SHA-256、精确模组来源/哈希、布局和验证边界。

优先将 `.mrpack` 导入为独立实例，然后在世界列表选择 `svs_first_light_v1`。启动器实际导入和客户端进入尚未在本轮验证。也可以在 **Minecraft 1.20.1 + Forge 47.4.23 的独立客户端实例** 中，使用本目录 `plan.json` 的制图组合和仓库锁定版本，将 ZIP 顶层的 `svs_first_light_v1` 文件夹解压到该实例 `saves/`，选择该世界进入。所需模组可由 `tools/map_v1.py download` 下载并校验；源码仓库不携带 JAR。直接放入完整现有整合包的行为尚未验证，尤其不能把 Epic/Terralith 混合生成器视为本图已验证配置。

模板没有制作者的玩家背包、成就或统计数据，也不附带施工函数；它保留地图需要的世界数据和禁随机重复生成目标地标的数据包。不要整删世界 `data/`。

## 已验证与未验证

| 项目 | 边界 |
|---|---|
| 下载与依赖 | 15 个顶层制图 JAR 均按仓库 SHA-512 校验；JAR 声明中未发现缺失的服务端必需模组 ID。版本约束最终由 Forge 启动检查。 |
| 原生生成 | Chunky 完成 16,641 个区块，包含边界外生成余量；边界内 16,384 个区块均为 `minecraft:full`，预生成日志保存在 `.map-work/pregen.log`。 |
| 地标施工 | 三个 `/place structure` 调用的显式成功状态为 `1b`；全部 83 个批次完成，世界保存且服务端正常退出。命令成功不等于 Boss/融合/奖励功能验收。 |
| 存档与道路 | 打包工具要求道路中心采样均检测到铺装、12 个床方块部分（六张床）齐全、三名带制作标签的村民存在；缺失则拒绝打包。结果以本次 `world-audit.json` 为准。 |
| 地图导航 | 第一版使用实际道路和路标。原版 `/place structure` 不自动持久登记 StructureStart，本图不承诺 `/locate`、Explorer's Compass 或结构区域检测。 |
| 玩家行为 | 客户端视觉、融合交互、Boss 激活与掉落、战斗手感、感染长期扩散、围城、多人均待玩家实测。 |
| 整包接入 | FTB 主线、货币/职业/阶段脚本与整包平衡没有接入；原有 FTB 暂停状态继续保留。 |

制图组合没有包含 Spore Inquisition：首次尝试暴露其对不在组合中的实体/命令的函数引用，早期带其维度的失败草稿已留在 `.map-work/backups/initial-schema/`，随后重新创建了干净世界。Spore 原 JAR 的 Create / Farmer's Delight 等可选联动配方在最小组合中仍会报加载错误；未据此修改主包配方，也不把服务端开图成功写成完整内容验证。

首次存档检查发现四个床方块部分被家具覆盖、337 个道路中心采样点因砂砾落水缺失，随后执行 77 个修补批次：移开家具、恢复床位，低洼处改为 Y≥64 的木质栈道并加支柱，陆地改用不受重力影响的夯土。此修正也已回填正常生成器，后续新建不需要重现该缺陷；旧草稿如需同样修补，可先用 `map_v1_build.py --repair`，再用 `map_v1_run.py --phase repair`。

本次终检：道路中心 **2,979/2,979**（坠星旧道 1,493、失联支路 225、西境路线 1,261），缺失 0；床方块部分 **12/12**，缺失 0；带制作标签的村民 **3/3**。陨石区域存在 `symbiote:dormant_sample` 方块实体；医院包含 Spore 容器/培养器/手术台等方块实体，金字塔包含灾变机关方块实体。这些只证明保存了相应内容，不代替交互或战斗验收。

## 制作源码与重建顺序

| 文件 | 用途 |
|---|---|
| `plan.json` | 地图目标、种子、初始候选坐标、制图模组清单 |
| `layout.generated.json` | 本次实际拟合位置及道路点列；由打包步骤保存 |
| `../../tools/map_v1.py` | 下载、哈希/资源审计、隔离目录准备 |
| `../../tools/map_v1_world.py` | 只读解析区块、实地图预览和存档检查；需 numpy / Pillow |
| `../../tools/map_v1_build.py` | 从地形采样生成一次性施工函数和分区加载批次；需 numpy |
| `../../tools/map_v1_run.py` | 启动隔离服务端、执行批次、读取结构成功状态、保存并关闭 |
| `../../tools/map_v1_package.py` | 检查完成状态并导出无玩家进度的世界模板 |

重建在新的 `.map-work/server/` 中完成，不复用旧游戏存档：

1. 下载并核对官方 Forge 47.4.23 安装器。官方 Installer SHA-1 为 `ed31ce02ac69176f34353235cb2508d5a0f1e088`，运行 `--installServer .map-work/server`。
2. `python tools/map_v1.py download --reuse <已有实例的mods目录>`，然后运行 `python tools/map_v1.py inspect`。
3. `python tools/map_v1.py stage --lwjgl-core <lwjgl-3.3.1.jar路径>`。此 LWJGL 核心库的官方 SHA-1 为 `ae58664f88e18a9bb2c77b063833ca7aaec484cb`；RoadWeaver 的内嵌 OpenCL 模块需要它。只修正隔离服务端的模块路径，不修改模组 JAR。
4. EULA 由使用者自行确认。本次用户已于 2026-10-14 在会话中明确同意并授权写入；工具不会替其他使用者自动接受。
5. 从隔离目录启动 Java，使用 `@user_jvm_args.txt @libraries/net/minecraftforge/forge/1.20.1-47.4.23/win_args.txt nogui`。只监听本机 `127.0.0.1:25575`。RoadWeaver 配置 `performance.openclCoarseSamplingEnabled=false`，使用 CPU 采样。
6. 制作时临时关闭生物自然生成、破坏、昼夜/天气推进及随机刻，设置世界边界 2048；执行 `chunky world minecraft:overworld`、`chunky shape square`、`chunky center 0 0`、`chunky radius 1024`、`chunky start`。若有旧任务需先核对，不能直接续跑另一份存档的任务。
7. 预生成完成后 `save-all flush`、`stop`；运行 `python tools/map_v1_world.py`，再运行 `python tools/map_v1_build.py`。
8. `python tools/map_v1_run.py --java <Java17的java.exe路径>`。首次失败后先检查日志，明确继续时才加 `--resume`；已完成营地不重复生成村民。函数只手动调用，无 load/tick 自动触发。
9. 服务端关闭后再次运行 `map_v1_world.py`，核对实际结果，再运行 `map_v1_package.py`。施工完成时已恢复正常生物生成、破坏、昼夜/天气推进和随机刻。

源码只修改仓库中的制作材料；缓存、服务器、存档、预览和 ZIP 均在已忽略目录中。当前世界生成覆盖仅在该新世界的数据包内，未平铺到主包的 OpenLoader 配置。

版本依据：[Forge 官方下载](https://files.minecraftforge.net/net/minecraftforge/forge/index_1.20.1.html)、[Chunky 命令](https://github.com/pop4959/Chunky/wiki/Commands)、[1.19.4 高度图命令](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-19-4)、[mrpack 格式](https://support.modrinth.com/en/articles/8802351-modrinth-modpack-format-mrpack)、[先前来源核查](../../docs/预制地图流程_来源核查.md)。
