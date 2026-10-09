# 给 GLM 的交接启动词（直接整段发给 GLM/qoder）

```
你接手 Minecraft 1.20.1 Forge 整合包《Symbiote vs Spore》（共生体 vs 真菌，类魂 ARPG，214 mod）的开发。你的角色：写码执行 + 自检。我（用户）负责裁决和验收。**规格书即合同**；若规格书与本机实证冲突，以实证为准并立即上报，不许按错的规格书硬做。

== 环境（本机路径，你可直接读写）==
- E:\SvS_整合包_副本            整合包母本（所有改动第一落点）
- C:\PCL 正式版 2.8.13\.minecraft\versions\test4   测试实例（我在玩的）
- E:\mcmp                       Git 仓库（docs/ 下全部设计文档；svs_tweak 源码在 E:\mcmp\svs_tweak）
- E:\mcmp_test                  工具区：launch_test4.py（启动，quickPlay 世界 test）、pack_mcbbs.py（打包）、gradle-8.8、i18n_work/、错误报告/（我发来的崩溃包都在这里）
- C:\PCL 正式版 2.8.13\.minecraft\versions\{Immersive Fight 4.2.9, DUEL OF THE END, Construct Technological Innovation, 远梦之棺} —— 四个参照包（**只读**；MC 版本各不相同：IF/远梦 1.20.1、DOTE 1.18.2、CTI 1.19.2 → **抄结构不抄 id**）
⚠️ E:\mcmp_test\svs_tweak 是 9-25 的旧副本（build/libs 里只有 1.0.0）——svs_tweak 一律用 E:\mcmp\svs_tweak。

== 先读这六个文件（按顺序）==
1. E:\mcmp\docs\HANDOVER.md —— 交接文档。**效力最高的是四点七（分工）与四点十（用户裁决汇总）**；四点五/四点六/四点八/四点八五/四点九/四点九五当背景读。
2. E:\mcmp\docs\任务文档.txt —— 设计理念与工作原则（圣旨）。
3. E:\mcmp\docs\魔改设计决议.md —— 机制定稿（开头"变更记录"效力高于正文）。
4. E:\mcmp\docs\修复批补正_0926.md —— 对修复批规格书的实证核对（F1 的假设已证伪、F3 真因已定位、F4 要先探针定名、F6 的构建路径写错了）→ **读规格书必须连它一起读**。
5. E:\mcmp\docs\对抗式审查_2026-09-26.md —— 三处崩服修复的对抗式审查，"已验证 / 未验证"边界与专项排查都在里面。
6. E:\mcmp\docs\武器线与匠魂节奏_参考综合.md —— 四参照包的武器线/匠魂节奏/护甲/饰品/技能书拆解与建议（任务线重写的设计输入）。

== 铁律（违反任一条 = 返工）==
1. 改动三处同步：副本 + test4 + git commit；index.toml / mods/*.pw.toml 按需同步维护。
2. 手术式变更：只碰任务要求的部分；发现无关问题**只上报不擅自处理**；自己产生的孤儿（未被引用的 reward_table、未部署的脚本、空目录）要清掉。
3. 先修不删；ARR mod 不改 jar（用数据包或 svs_tweak 的 MixinSquared 取消器）。

4. KubeJS 血泪规则（全部实踩过）：
   ① 控制流块（if/else/for/while/try/catch）内部禁止 const/let——声明提到所属函数最外层。
   ② ForgeEvents 只在 startup 脚本可用；其监听器体必须整体 try/catch（Forge 总线会重抛 = 崩游戏）。但该 try 只挡脚本级异常与 Java 方法调用异常，**挡不住 Rhino 包装器内部异常**（如 Int2ObjectMap 那类 CCE）——那类 API 只能不碰。
   ③ 成员解析是本环境最大的坑，按此优先级选：**KubeJS 注入成员**（.type/.player/.monster/.name/.level/.persistentData/.foodLevel…，已实证可靠）> **Forge 自有成员**（getPersistentData / runCommandSilent / setAmount…，名称未混淆）> **声明在接收者自身类的方法**（getPlayers / getPlayerList / getValue…可靠）。**"继承自父类的成员"不可靠**：getUUID() 对**所有实体都失败（含 ServerPlayer）**、dayTime 读成 NaN → 一律不用，实体标识改用自发 pd id 或 player.name。拿不准就先写一次性探针脚本打印实际值定名，不许猜。
   ④ java.lang.Class / java.lang.reflect 被类过滤器拦截，禁用（forName / getClass / 反射全断）。
   ⑤ 别碰 fastutil Int2ObjectMap（Rhino 把 Map/List 都包一层，属性访问走 containsKey(String) → CCE 且兜不住）：村民交易走 architectury TradeRegistry.registerVillagerTrade(profession, 1, listing)（本包已装）。泛化：只有 String 键的 Map 与 List 的数字下标安全。另注意 /kubejs reload startup_scripts 会让 startup 脚本重跑 → 静态登记会重复（交易翻倍）。
   ⑥ 提交前跑 python E:/mcmp/tools/check_kubejs_rhino.py（仓库根或传目录）；回归夹具 tools/fixtures/kubejs_rhino_fixture.js 应恰好报 17 处。
   ⑦ startup_scripts 的改动需重启游戏生效（reload 无效）。

5. svs_tweak（自研 Java mod，源码 E:\mcmp\svs_tweak）改动后必须重建部署：
   - 构建（在 E:\mcmp\svs_tweak 里跑，可离线）：JAVA_HOME=<JDK17> E:/mcmp_test/gradle-8.8/bin/gradle.bat --offline jar
   - 只改 gradle.properties 的 mod_version（mods.toml 里是 ${mod_version} 模板，自动展开）
   - libs/ 四个编译期依赖的重建法见 svs_tweak/README.md（**mixinsquared 必须用 forge jar 内嵌的 META-INF/jars/MixinSquared-0.2.0.jar**，平台 jar 会编译失败）
   - **jar manifest 必须带 MixinConfigs: svs_tweak.mixins.json**（build.gradle 已写）——曾因漏这行导致 5 个 mixin 静默失效数周，POTB NPE 复发崩档三次
   - 验收生效（硬标准）：debug.log 里搜 svs_tweak.mixins.json，应有 5 行 `Mixing <Mixin> from svs_tweak.mixins.json into <目标类>`（**只有 debug.log 有，latest.log/console.log 里 0 行**）。latest.log 侧的辅助信号：`[mixin/]: Mixin config svs_tweak.mixins.json ...`（= 配置已注册）+ svs_tweak 自带的 POTB 探针两行。**只看到"取消器 ×2"不算数**——那是 ServiceLoader 通道，与自家 mixin 是否生效无关（正是这点让人误判了很久）。

6. 并发与归属：仓库另有会话在提交。提交前 git log --oneline -5，只 git add 自己的文件（别把别人的 index.toml / *.pw.toml 带上）；新增 HANDOVER 小节前先 grep -n "^## " docs/HANDOVER.md 取现有编号（已撞号两次）。

7. 实机操作安全：动手前先 Get-Process java——**我可能正在玩**（之前出现过）。别杀我的游戏、别起第二个实例、别改正在被读的文件。需要实机验证用 launch_test4.py（到主菜单 200-350 秒属正常；若世界目录被改名/删除，quickPlay 会停在标题界面——日志末尾停在 ModernFix "Game took … to start" 就是没进世界）。它用实例自带 profile（UUID 与我同一档），会正常加载/保存存档。日志编码**先试 utf-8、失败再 gbk**（9-25 之后多为 UTF-8）；console.log 是唯一收 System.out 的；latest.log 每次启动覆盖，要留档得重命名。

8. 红线与证据分级：
   - EF 锁 20.14.17：任何"升级 EF 或某附属"的提议一律拒绝；原版干预政策【待定】——不许动原版配方/数值/门禁；worldgen 冻结（除我已裁决的 F6/F7）。
   - 只有**日志 / 存档 / javap 字节码实证**才算"通过"；只能由我体感确认的必须显式标"**未验证**"。本项目最大的失败模式是"看着接上了、其实没生效"——"加载 0 errors"不是证据，"命令返回 true"也不是。

== 第一批任务（按优先级，规格书即合同，逐条有验收标准）==
1. E:\mcmp\docs\规格书_修复批_0926.md —— 修首测失败项（最高优先级）。**先读 docs/修复批补正_0926.md 再动手**：F1 的假设已被证伪（掉币代码与 9-25 可用版本逐字节相同、日志 0 异常 → 查击杀归因，不是代码回归）；F3 真因是 getUUID 连玩家也失败（且 fireseed 在标记村民前就抛错 → "无奖励"可能是"整个绑定没完成"）；F4 的三个候选读法很可能都不行（先跑补正文档给的一次性探针定名）；F6 的构建路径写错了（见铁律 5）。
2. E:\mcmp\docs\规格书_真菌之魂.md —— 改名 + SLU 三魂兑换
3. E:\mcmp\docs\规格书_围城村庄级共享.md —— 围城多人共享计时
4. E:\mcmp\docs\规格书_EFS_ISS.md —— EFS-ISS 入包 + 砍技能
5. 任务线重写（等我把内容稿给你；设计输入 = docs/武器线与匠魂节奏_参考综合.md，依据 HANDOVER 四点十 裁决：全重写、stage2 删除、阶段Ⅲ灾变承接、末期武器任务线直发）。**排行一律氛围化**（颜色/点评/带宽），不做数值 Tier 表——四个参照包都是这么干的。

== 汇报格式（每完成一项）==
1. 改动文件清单 + 三处是否同步（附 md5 一致性一句话）
2. commit hash
3. 验收标准逐条自测结果：**贴日志关键行原文**，"未通过 / 未验证"如实标注
4. 未解决风险 + 需要我裁决的点

不确定就停下问我，不许猜着做。
读完先复述你对项目现状与这八条铁律的理解，等我确认再动手。
```

---

**本版（第二稿）相对第一稿的改动**（每处都有实证，第一稿的原始版本见 git 历史）：

| # | 改动 | 依据 |
|---|---|---|
| 1 | 铁律 5 验收信号：`Mixing ...` 行**指定 debug.log**，并写死"应 5 行"、"取消器 ×2 不算数" | 实测：`latest.log`/`console.log` 里 Mixing 行 **0 条**；`debug.log` 里恰好 5 条（五个 mixin 各一条，目标类都对得上） |
| 2 | 铁律 5 补 manifest 红线 + 构建命令 + libs 陷阱 | 漏 `MixinConfigs` 导致 5 个 mixin 静默失效数周（POTB NPE 崩档三次）；`mixinsquared` 用平台 jar 会编译失败 |
| 3 | 铁律 4③ **重写**为成员解析优先级 | 本机已为 API 名烧掉 4 轮：getUUID×2、addRecipeStage、dayTime |
| 4 | 铁律 4④ 订正：getUUID **对所有实体都失败** | 9-26 日志 `Cannot find function getUUID in object ServerPlayer[...]` ×8（第一稿写"非玩家"，会误导 F3 的修法） |
| 5 | 铁律 7（新增）实机操作安全 | 会话中用户正在玩（进程实测）；曾遇 quickPlay 世界被删而停在标题界面 |
| 6 | 铁律 6（新增）并发与归属 | 仓库同时有另一个会话提交，HANDOVER 小节**已撞号两次** |
| 7 | 铁律 8（新增）红线与证据分级 | EF/原版政策/worldgen 三条冻结；本项目的失败模式是"看着接上了其实没生效" |
| 8 | 先读 3 → **6** 个文件；任务补第 5 项（任务线重写） | 新增 `修复批补正_0926`、`对抗式审查_2026-09-26`、`武器线与匠魂节奏_参考综合`；四点十 已裁决任务线全重写 |
| 9 | mod 数 213 → **214** | 当前副本 jar 实数 |