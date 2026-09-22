# 优化 mod 增补清单（对照 IF / DOTE / CTI 差集分析）

> 方法：对三个参照包的 mods 目录做 modid 级差集扫描，筛性能类，再逐个核实 1.20.1 Forge 可用性。
> 我包现有优化件（参照系）：Embeddium、ModernFix、FerriteCore、MemoryLeakFix、Canary、chunksending、Chunky、Clumps、CullLeaves、EntityCulling、DynamicFPS、ImmediatelyFast、PacketFixer、spark。
> 日期：2026-09-22。

## 一档 · IF 4.2.9 实证在用（同 MC 1.20.1，零版本风险）

| mod | 版本 | 作用 | 理由 |
|---|---|---|---|
| **Embeddium Extra**（rubidium-extra） | 0.5.4.3+1.20.1 | 粒子/实体渲染细化开关 | Embeddium 官方生态扩展，IF 在用 |
| **Krypton FNP** | 0.2.25 | 网络栈优化 | IF 在用；联机/局域网受益 |
| **Async Logger** | 2.2.1 | 异步日志写盘 | 大日志量包（我们就是）减少卡顿尖刺 |
| **FastChunkGen** | 0.21 | 区块生成提速 | 配 Terralith/Epic Terrain 跑图有感 |
| **Structure Layout Optimizer** | 1.0.10 | 结构生成提速 | CTI 也在用；我们结构 mod 多 |
| **GPU Memory Leak Fix** | 1.8 | 显存泄漏修复 | 长时间游玩稳定性 |
| **Timeout Fixes** | 1.0.0 | 网络超时修复 | 联机防掉线 |
| **Ultimine Line Render Fix** | 1.0.0 | 修 FTB 连锁挖矿选框渲染 bug | **我们装了 FTB Ultimine，强相关** |
| **TerraBlenderFix** | 0.0.1 | 修 TerraBlender 的 bug | 我们装了 TerraBlender，对症 |
| **Accelerated Rendering** | 1.0.14 alpha | 激进渲染加速 | IF 在用但为 alpha 版，建议最后装、单独测 |

## 二档 · DOTE/CTI 在用，1.20.1 Forge 版已核实

| mod | 作用 | 理由 |
|---|---|---|
| **Entity Collision FPS Fix** | 实体碰撞挤压卡顿修复 | 实体多的战斗包（孢子海）受益明显 |
| **Async Locator** | 结构定位异步化 | 配 Explorer's Compass，找 Boss 房不卡主线程 |
| **NetherPortalFix** | 下界门传送卡顿修复 | QoL 顺带 |

## 三档 · 可选/专项

| mod | 说明 |
|---|---|
| **Oculus 1.8.0 + Oculus Flywheel Compat** | 光影支持。IF 在用且与 EF 拖尾兼容已实证；**想要光影才装**，不装零损失 |
| **Embeddium++** | 与 Embeddium Extra 功能重叠，**二选一**，别都装 |

## 明确不装（附理由）

| mod | 理由 |
|---|---|
| Starlight | 1.20.1 已过时（原版光照重写后无收益，且与新渲染管线冲突风险） |
| LazyDFU | 1.20.1 不需要（DFU 已提速，ModernFix 覆盖） |
| betterfpsdist | 无 1.20.1 Forge 版（停留在 1.18/1.19） |
| TickChanger / TickAccelerate | 改 tick 速率对战斗手感包太危险 |
| NaNHealthFixer | 1.18/1.19 限定，1.20.1 无此问题 |
| smoothswapping 等 Fabric 件 | IF 靠 Sinytra Connector 跑 Fabric mod；我们没装 Connector，用不了 |

## 建议

一档全装（10 件都是 IF 正在跑的同版本件，风险最低），二档全装（3 件对症），三档看你要不要光影。合计 13 件，装完跑一轮启动+跑图实测即可。
