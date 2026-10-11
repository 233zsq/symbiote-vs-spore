# Rapid Optimization：SvS 合入评估与执行交接

> 2026-10-10，只读评估。结论：**可以择项借用；不建议将整个优化包或其 overrides 覆盖进 SvS。首批只建议小范围试验，不能宣称整套已兼容。** 本轮没有修改母本、实例、模组、配置或启动游戏。下文“建议”“候选”均不是已完成记录。

## 一、核对对象与证据边界

| 项目 | 本次实证 |
|---|---|
| 用户附件 | `C:\Users\ZGJ\Downloads\Rapid Optimization 20.1Fo.2.3.3.mrpack`，3,005,332 字节 |
| 附件 SHA-256 | `128989ee60d020b6856eb38a8f19e5ae3dfcb74b403e9a62999487ab0ec96829` |
| 官方来源核对 | 附件 SHA-512 与 Modrinth 官方版本 `vuPNPhXZ` 的发行文件完全一致；索引中 27 个下载项的 SHA-1 均匹配对应官方版本文件 |
| 游戏与加载器 | 索引要求 Minecraft 1.20.1 / Forge 47.4.23；当前 `test/test.json` 的 Forge 为 47.4.23，版本基础匹配，无须为此升级 Forge |
| 包内实际组成 | 索引 26 个模组下载项＋1 个资源包；另在 overrides 中直接嵌入 3 个 jar；合计 **29 个模组＋1 个资源包** |
| 与母本对账 | 母本顶层 215 个 jar；按 jar 元数据和完整文件 SHA-1 对账：**8 个文件已完全相同、2 个为更新候选、19 个为新增候选** |
| 检查层级 | 已检查索引、覆盖配置、嵌入 jar 元数据、现有 jar 元数据与哈希、官方项目/版本说明；**未进行加载验证、实战验收或性能 A/B 测试** |

本地依据：附件 `modrinth.index.json`、`overrides/`；母本 `mods/`；开发实例 `test/test.json`。线上依据：[官方精确发行版本](https://modrinth.com/modpack/rapid_optimization/version/vuPNPhXZ)、Modrinth API `/v2/version/{版本ID}` 的文件哈希、依赖与游戏版本字段。

原包的性能展示来自其作者的特定机器和场景，其中主页示例为 **1.21.1**；不能换算成 SvS 1.20.1、215 模组、史诗战斗 Boss 场景的收益承诺。官方版本标注兼容 Forge 1.20.1，也不能替代与 SvS 的组合测试。（依据：[原包说明](https://modrinth.com/modpack/rapid_optimization)“Performance / Known issues”；本次未开展运行时测试）

项目边界仍取自 [HANDOVER](HANDOVER.md)§二、四、五、八和[实例配置说明](实例配置说明.md)§一、二：母本→test→仓库；EF **20.14.17 固定**；保留 svs_tweak / MixinSquared；worldgen 冻结；不改原版配方、数值和门禁，不覆盖用户按键。`test4` 保留，不因优化工作顺手清理。

## 二、29 个模组逐项处理建议

### A. 8 个相同文件：保留 SvS 现状，不重复安装或导入对方配置

| 模组 | 两边相同版本 |
|---|---|
| Cloth Config | 11.1.136 |
| Embeddium | 0.3.31+mc1.20.1 |
| ImmediatelyFast | 1.5.5+1.20.4（官方该文件明确支持 1.20.1；不能仅凭文件名判错版） |
| Krypton Reno | 26.1.1-1.20.1 |
| Oculus | 1.8.0 |
| ModernFix | 5.27.83+mc1.20.1 |
| Embeddium Extra | 0.5.4.4+mc1.20.1-build.131（附件名为 rubidium-extra，实际 modId 为 `embeddium_extra`） |
| Accelerated Rendering | 1.0.14-1.20.1-alpha（附件直接嵌入的 jar 之一） |

依据：本次完整文件 SHA-1 比对；索引项及嵌入 jar 的 `META-INF/mods.toml`；[ImmediatelyFast 精确版本](https://modrinth.com/mod/immediatelyfast/version/rvsLEEZU)。**相同 jar 不代表两边配置相同，也不代表已经做过本包全部验收。**

### B. 2 个更新候选：按功能分别验证

| 模组 | SvS → 附件版本 | 建议与验收重点 |
|---|---|---|
| Async Logger | 2.2.1 → 2.2.2 | 首批可选小版本替换。官方修复的是开启 `filtering.sysout` 时的崩溃，不宣称当前 SvS 已遇到该问题或会因此提高 FPS。保留原日志策略；检查正常启动/退出，`latest.log`、`debug.log` 和异常栈仍可获取。 |
| Entity Culling | 1.10.5 → 1.11.2 | 第二批候选，单独测试。1.11.2 修复部分旧版 MC 方块实体剔除失效，但官方也提示特殊客户端实体、超出包围盒渲染的方块实体需要白名单；须看 Boss、模型部件、展示实体及第三人称动画。不要直接复制对方的剔除白名单。 |

依据：本次母本元数据；[Async Logger 2.2.2](https://modrinth.com/mod/asynclogger/version/v8ouTH1m)变更记录；[Entity Culling 1.11.2](https://modrinth.com/mod/entityculling/version/HPDH6g5B)变更记录及[官方说明](https://modrinth.com/mod/entityculling)“Known Issues”。

### C. 19 个新增候选：只有首批名单建议直接进入试验

| 模组／附件版本 | 建议 | 理由与应验证的对象 |
|---|---|---|
| **BadOptimizations 2.4.1** | **首批：单项试验** | 客户端光照贴图、天空颜色等缓存优化，无额外依赖。验证跨维度、昼夜/天气、药水状态及光影开关后画面正确；保留 `ignore_mod_incompatibilities=false`。不是零风险承诺。 |
| **0Pack2Reload Forge 1.20.1-1.0.1** | **首批：单项试验** | 避免资源包列表未改变却触发重载。验收“未改列表不多余重载；真正增删/调序仍正确重载”；收益是操作等待时间，不是 Boss 战 FPS。 |
| Better Biome Blend 1.4.0 | 第二批候选 | 客户端生物群系颜色混合，官方声明支持 Embeddium。它不等于改变生物群系生成；验证树叶/草水颜色、跨群系边缘与光影，保持相同混合半径比较。 |
| AllTheLeaks 1.1.3+1.20.1-forge（嵌入） | 第二批候选 | 面向内存泄漏，不应当作直接 FPS 模组。当前 GeckoLib 4.8.4、Moonlight 1.20-2.16.35 满足附件所声明的可选依赖版本范围；仍须核对该旧版实际修复项与现有 MemoryLeakFix/ModernFix，观察重复进出世界后的堆内存和退出清理。 |
| Gnetum 2.5.0 | 暂缓，HUD 瓶颈证实后再试 | 将 HUD 更新摊到多帧；对耐力、锁定、Boss 血条和围城倒计时，刷新响应本身也是验收对象。其新版说明中的 4.x 配置界面不能直接套到 2.5.0。 |
| GpuTape 1.0.5.1 | 暂缓，单独图形专项 | 当前项目已称 GPUBooster；不能把现行新版功能、JVM 要求和跑分照搬到附件旧版。须与 Embeddium/Oculus/Accelerated Rendering 的实际图形路径核对。现有 GPUmemleakfix 的名字相近，并不足以证明两者重复或硬冲突。 |
| Harium 2.0 cumulative hotfix v2 | 本轮不加 | 官方说明为 Lithium 派生、改写 AI/实体/碰撞等系统；SvS 已有 Canary 0.3.3。存在同类改写重叠，**本次没有证明两者可共存，也没有取得硬不兼容结论**。若需要替换 Canary，另交有依据的替换方案，不双装试运气。 |
| Ixeris 4.6.8 | 暂缓，输入瓶颈证实后再试 | 官方说明涉及原始输入缓冲、分离事件轮询与渲染线程。重点检查高回报率鼠标转视角、锁定切目标、全屏切换、输入手感、光影。不要照抄原包线程配置。 |
| LightSpeedRe 1.2.3 | 暂缓，启动瓶颈证实后再试 | 1.2.0 起引入并发资源加载；原包还启用了针对 `*` listener 的失败隔离配置。本次未核定该键源码语义，不能沿用它并把被隔离的重载错误当成功；先确认与 ModernFix、OpenLoader 和各资源加载器的关系。 |
| Mixin Booster 0.1.3 | 本轮不加 | 官方说明是运行时替换 Forge 的 Mixin 实现，不是普通渲染开关。没有本包所需依赖证据，不应为“优化齐全”改动 svs_tweak / MixinSquared 的运行底座。**未判定二者必然冲突。** |
| Particle Core 0.3.3 | 暂缓，粒子专项候选 | 剔除、渲染和按类型减量均可配置；原包还开启异步 ticking。不能以减少刀光、攻击预警、魔法特效换取跑分；先明确 aaa_particles、EF 及其附属粒子表现。 |
| Fzzy Config 0.7.7 | 只随确需的依赖加入 | Particle Core 的必需依赖；自身不是一项应单独追求的性能收益，且继续依赖 Kotlin for Forge。 |
| Kotlin for Forge 4.12.0 | 只随确需的依赖加入 | Particle Core / Fzzy Config 依赖；首批两项新增不需要它，不为凑齐原包而装。 |
| AsyncParticles 20.1.4.0-beta.2 | 暂缓，独立粒子专项候选 | 官方保持 beta 状态，现行说明将 Particle Core 列为兼容对象，所以不能断言二者必然冲突；但该声明不等于验证 SvS 全部粒子。附件给 EF 的 TrailParticle/AbstractTrailParticle 配了锁，仍需 Boss、aaa_particles、魔法及长时间实战验证。 |
| Starlight 1.1.2 | 本轮不加 | 作者明确提示侵入式光照引擎重写，且 1.20 原版与其在生成光照测试上已很接近。无本包光照瓶颈数据，不优先扩大变量。这是本次建议，不冒充 HANDOVER 已拍板的禁用裁决。 |
| Cull Less Leaves Reforged 1.0.5 | 本轮不加 | SvS 已有 CullLeaves 4.1.1，均涉及树叶剔除。无替换收益证据，保持现状；不是已经证明硬冲突。 |
| Smooth Boot Reloaded 0.0.4 | 暂缓，启动 CPU 瓶颈证实后再试 | 改启动线程数量/优先级；附件固定 `threadCount.main=11`，不能跨机器照抄。若试验，应根据本机线程数和加载过程测量。 |
| Fast Noise / zfastnoise 1.0.13 | 本轮排除 | 作者称保持原版生成一致，但实现确实替换噪声/群系生成相关路径；当前 worldgen 冻结。不能仅凭“优化”名称纳入本轮，须用户重新裁决范围后再谈。 |
| RuOK Pre-Release 6 / modId `ruokmod` 1.7.4（嵌入） | 本轮不加 | 官方说明含实体渲染数量/范围限制及全局画质预设；附件启用动态实体预算，且 `RenderDisplayItem=false`、`CullParticle=true`。可能影响战斗可读性和展示实体，尚未经本包实测。不给性能统计优先于完整模型与攻击预警的权限。 |

功能依据（均为官方项目说明；不将最新说明当作旧版每个配置键的合同）：[BadOptimizations](https://modrinth.com/mod/badoptimizations)、[0Pack2Reload](https://modrinth.com/mod/0pack2reload)、[Better Biome Blend](https://modrinth.com/mod/better-biome-blend)、[AllTheLeaks 1.20.1 分支](https://github.com/pietro-lopes/AllTheLeaks/tree/1.20.1)、[Gnetum](https://modrinth.com/mod/gnetum)、[GpuTape / GPUBooster](https://modrinth.com/mod/gputape)、[Harium](https://modrinth.com/mod/harium)、[Ixeris](https://modrinth.com/mod/ixeris)、[LightSpeedRe](https://modrinth.com/mod/lightspeedre)、[Mixin Booster](https://modrinth.com/mod/mixinbooster)、[Particle Core](https://modrinth.com/mod/particle-core)、[Fzzy Config](https://modrinth.com/mod/fzzy-config)、[Kotlin for Forge](https://modrinth.com/mod/kotlin-for-forge)、[AsyncParticles](https://modrinth.com/mod/asyncparticles)、[Starlight](https://modrinth.com/mod/starlight-forge)、[Cull Less Leaves](https://modrinth.com/mod/cull-less-leaves-reforged)、[Smooth Boot](https://modrinth.com/mod/smooth-boot-reloaded)、[Fast Noise](https://modrinth.com/mod/zfastnoise)、[RuOK](https://github.com/MCTeamPotato/RuOK)。精确发行版本和依赖另以附件下载 URL 中的 version ID 对应官方 API 为准。现有模组、版本和覆盖参数来自本次本地静态核对。

## 三、不要整份复制 overrides

| 路径／内容 | 处理建议及实证理由 |
|---|---|
| `options.txt` | 不导入。附件会带入自己的按键、资源包列表、视距、FPS 上限与粒子档位，并将 `pauseOnLostFocus` 设为 true；SvS 当前后台验收需要 false。 |
| `PCL/config.v1.yml`、`.bak` | 不导入。它们属于原包的启动器配置，不是性能模组依赖。 |
| `embeddium-fingerprint.json` | 不导入机器生成的指纹文件。 |
| `fml.toml`、`forge-client.toml` | 不整份替换 Forge 配置。附件还包含 `disableOptimizedDFU=true`，不能把“来自优化包”当成该值对 SvS 有益的证明。 |
| Embeddium / Oculus / ImmediatelyFast / Accelerated Rendering / Krypton Reno / ModernFix 配置 | 保留 SvS。需要某个键时做逐键差异和单项验证；不要让相同 jar 的对方配置悄悄成为新基线。 |
| `smoothboot.json` | 不复制固定 `threadCount.main=11` 的机器参数。 |
| AsyncParticles / Particle Core / RuOK 配置 | 不随包导入。附件包含异步 tick、剔除/预算等显著改变运行路径或可见效果的参数，应由对应专项验证决定。 |
| `modernfix-mixins.properties` | 其中关闭“缺少性能模组”的警告，不等于性能提升；本轮无须覆盖。 |
| 日志过滤与错误隔离选项 | 保留 SvS 可诊断性。不能关闭 debug.log、压制 CME 或隔离失败后报告全绿。附件 AsyncParticles 本身为 `suppressCME=false`、`failBehavior=RAISE_CRASH`，也不能讹称原包默认吞掉这些异常。 |
| `transition.json` 及其他未采用模组的遗留配置 | 不导入无明确归属/收益的配置，不更改崩溃报告发送同意项。 |
| `EUJT-v0.3.1.zip` | 属于 Embeddium/Sodium 非官方翻译资源包，**不是性能模组**；本轮不导入也不重写 SvS 资源包启用列表。如后续需要界面翻译，单独核对语言键和优先级。 |

依据：附件相应配置；[HANDOVER](HANDOVER.md)§五第 11 条、[实例配置说明](实例配置说明.md)§二；[EUJT 项目说明](https://modrinth.com/resourcepack/eujt-continued)。原包作者自己还列出 ImmediatelyFast 在部分设备可能负收益、Accelerated Rendering 与部分光影的第三人称模型问题，说明这些设置也需要按机器与光影检验。（[原包说明](https://modrinth.com/modpack/rapid_optimization)“Known issues”）

## 四、建议执行顺序与验收口径

1. **建立可回滚对照。** 读取当前 HANDOVER 和执行状态，重新盘点实际 jar/配置哈希；备份本轮会改的文件和测试世界副本，记录基线日志。不得拿旧 test19 的 FPS 与当前 test 直接作性能对照。
2. **首批只有两项新增和一项可选更新。** BadOptimizations 2.4.1、0Pack2Reload 1.0.1 分别加入验证；Async Logger 2.2.2 可单独替换，保留原配置。新增模组优先从官方索引 URL 获取并核验 SHA-1；不运行附件/网页中的未知指令。
3. **一次定位一个变量。** 先按官方默认生成新模组配置，按需作最小差异；不把原包整套参数当默认答案。功能或画面出错就回滚对应项，再判断是否有局部配置解法，不通过移除战斗模组、改 EF 版本或屏蔽错误解决。
4. **用同条件实证判断收益。** 同一机器/Java/内存/分辨率/光影/视距/粒子设置，同一测试世界与路线；基线和候选均先暖机，至少重复两次。观察普通探索、实体较多的村庄及代表性 Boss 战的帧时间中位数和 P95/P99；没有合适采样工具则报告采样限制，不编造百分位或提升比例。客户端优化不能直接宣称修复 TPS；若追查服务端瓶颈，用相同负载的 spark TPS/MSPT 数据另议。
5. **功能目标分别验收。** BadOptimizations 检查颜色/光照缓存刷新与帧时间；0Pack2Reload 检查未修改与已修改资源包列表的两条路径；Async Logger 检查日志完整及正常退出。工具型收益不强求 FPS 提升。
6. **完成本批战斗回归。** EF 第一/第三人称、锁定/闪避/格挡/刀光，代表性 Boss 主要动作与阶段特效，魔法粒子，耐力/Boss 血条/围城 HUD；不以降低画质或减少攻击预警作为通过条件。检查 svs_tweak / MixinSquared 原有加载和取消器证据仍成立。只有日志和标题界面不能写“实战全绿”；已有围城多人等待测项维持原状态。
7. **通过后收口。** 按母本→test→仓库核对新增/替换项与配置差异，登记版本、来源、许可证据、测试条件、结果及回滚方法。仅提交本轮自有路径，不夹带其他会话改动；是否打里程碑 zip 依 HANDOVER 的交付需要决定。
8. **第二批另交结果再选。** Entity Culling、Better Biome Blend、AllTheLeaks 有条件进入下一批；HUD/输入/粒子/并发加载等专项须先证明对应瓶颈。暂缓和排除项不因首批通过而自动获准。

以上为本次执行建议和验收草案，并非历史已拍板的优化名单。同步、诊断日志、EF 固定版本及已有验收状态的要求依据 [HANDOVER](HANDOVER.md)§二至五、八；其余方法用于使本次建议可验证。

许可证据随变更记录即可，不把原包 MIT 当成所有内含模组的许可。Entity Culling 当前官方页面特别区分 Modrinth/CurseForge 托管整合包与其他 jar 再分发；这不妨碍本地兼容测试，但 MCBBS zip 交付方式须核对具体版本条款。现有 1.10.5 也已声明 Protective License，不能描述成此次升级才新引入的问题。依据：[原包许可说明](https://modrinth.com/modpack/rapid_optimization)、[Entity Culling 官方许可段落](https://modrinth.com/mod/entityculling)、现有 jar `LICENSE-EntityCulling`、[开源协议审查](开源协议审查.md)§二至四。

## 五、用户可直接发送给执行 agent 的启动词

```text
请为《Symbiote vs Spore》执行 Rapid Optimization 的首批择项合入测试。

先读 E:\mcmp\docs\HANDOVER.md，再读 任务文档.txt、开发计划_执行状态.md、实例配置说明.md，以及 E:\mcmp\docs\Rapid_Optimization_合入评估与执行交接.md。以后者第二至四节为本次范围和验收草案；如与更新的已拍板裁决或本机实证冲突，报告冲突并按 HANDOVER 处理。

来源文件：C:\Users\ZGJ\Downloads\Rapid Optimization 20.1Fo.2.3.3.mrpack
官方精确版本：https://modrinth.com/modpack/rapid_optimization/version/vuPNPhXZ

本次授权的首批范围：分别试验新增 BadOptimizations 2.4.1、0Pack2Reload Forge 1.20.1-1.0.1；可单独将 Async Logger 2.2.1 更新至附件对应的 2.2.2。先核对现状，做文件备份/哈希与回滚清单，再逐项验证。优先用官方默认生成新配置，保留现有日志设置，不照搬原包参数。若无可重复收益、功能不符合目标或出现回归，撤回对应改动并说明证据。

不要整体导入 mrpack/overrides，不复制 options.txt、PCL 配置、Forge 整份配置、机器指纹或资源包启用列表，不重复安装相同 jar。不要更换 EF 20.14.17，不改 worldgen、玩法数值、任务 SNBT、按键和现有战斗资源。保留 svs_tweak/MixinSquared。暂缓项、排除项和第二批候选只提出建议，不顺手实施；不删除 test4。

按评估文档第四节做同条件基线和战斗/资源重载/日志验证；重点保护模型动作、刀光特效、锁定与 HUD 的完整性。不能用减画质、藏实体/粒子、关闭日志或压制异常换取“优化成功”。游戏内无法完成的检查明确列为待我实测，不能将静态检查或能启动写成全绿。

改动遵守母本 E:\SvS_整合包_副本 → 开发实例 C:\PCL 正式版 2.8.13\.minecraft\versions\test → 仓库 E:\mcmp 的同步规则。只提交自己改过的路径，更新实际模组/许可/执行记录，不夹带其他会话改动。最终交付实际保留/撤回清单、精确版本和来源、配置差异、实测结果/待测项、三方一致性及回滚方法。完成首批后向我报告，再讨论第二批。
```
