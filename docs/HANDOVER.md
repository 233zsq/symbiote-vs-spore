# Symbiote vs Spore 交接文档（HANDOVER）

> 更新：2026-09-24 晚。魔改阶段进行中，测试由用户在 PCL `test4` 实例上进行。
> 主规格：`docs/任务文档.txt`（设计理念 13 条 + 任务 5 项 + 工作原则）；决议：`docs/魔改设计决议.md`。

## 一、目录布局（勿乱）

| 位置 | 角色 | 规则 |
|---|---|---|
| `E:\SvS_整合包_副本` | **整合包母本** | 所有改动第一落点，打 zip 从这出 |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\test4` | **测试实例** | 用户玩的；我每次改动**双写**到此 |
| `E:\mcmp` | Git 仓库（GitHub 233zsq/symbiote-vs-spore） | pw 条目/KubeJS 脚本/文档 |
| `E:\mcmp_test` | 工具区 | launch_test4.py、dl/各批次下载、dist/testN.zip、i18n_work/（翻译工作区）、glm_out/（GLM 代码初稿）、规格书、backup/ |
| 桌面 5 张 Excel | 数值基准表 | 武器/敌对/Boss/中立/EF适配统计 |

**改 mod/配置/KubeJS 后：副本 + test4 双写 → 仓库 commit →（打 zip 从副本）。** 用户在 PCL 加减的 mod 要导出发来对账合并。

## 二、当前状态

- **162 件 mod**（副本/test4 一致）+ Modern Mizuno 材质包 + Bliss 光影（DH 兼容）
- 打包：MCBBS 格式脚本（manifest+mcbbs.packmeta+overrides），最新产物 `dist/test5.zip`（**已过期**：之后又加了村民美化4件、魔改脚本、POTB修复包——下次打包用同一脚本从副本重打，版本号 test6）
- 游戏实测可进世界；FTB 任务线骨架在（暮色章已删；**重排迁移清单已出** `docs/任务线重排迁移清单.md`：仓库已同步删 stage3_twilight.snbt，游戏内编辑器照单改 8 处文本/任务，另发现 stage2_nether 章缺失；阶段Ⅲ承接方案待用户裁决）；桌面表已按新包体重采

## 三、魔改一期已完成（全部双写+commit）

1. **LootBeams** 关 Play Sounds（config/lootbeams-client.toml `sounds=false`）
2. **InControl 难度规则**（config/incontrol/spawn.json）：easy 血×0.8伤×0.6 / hard 血×1.5伤×2.0，`gamestage` 条件（**onjoin 关键字已删**——InControl 9.5 不认）
3. **FTB 序章难度三选任务**（preface.snbt 三个 checkmark，奖励 `/svs difficulty <档>`）
4. **KubeJS 五个脚本**（kubejs/，三侧同步，加载应为 `Loaded 5/5 ... 0 errors`）：
   - `startup_scripts/spore_coin.js` — 注册 `kubejs:spore_coin`（绿宝石贴图占位）+ `kubejs:fireseed_token`
   - `server_scripts/spore_coin.js` — 真菌怪掉币（血量分档 1-2/3-5/15-25，instanceof Monster 判定）+ 村民交易（农民 12币→8 grout、工具匠 20币→火种工具，TRADES 直连 `VillagerTrades.f_35627_` 静态字段）
   - `server_scripts/difficulty.js` — `/svs difficulty <easy|normal|hard>` 个人难度（本人=改自己，控制台=全服），GameStages stage `svs_difficulty_*`
   - `server_scripts/symbiote_counter.js` — 共生体克制真菌：4 阶段伤害 ×1.1→1.5、减伤 10%→30%、狩猎红利（小怪+3饿+8耐+3信/精英+6+20+8/BOSS满回+25）、天敌仇恨（24格10%概率）；SymbioteTracker/PredatorHunt 反射已实证
   - `server_scripts/fireseed.js` — 火种绑定：右键村民绑定（上限5、改名"火种"、送最贵可交易物）、死亡扣真菌币（20起步连续递减50%/25%）、7天未上线解绑
5. **血源 6 件武器 EF 适配补齐**（兽斩/电锯/手杖变体，imfdata）
6. **POTB 崩溃修复**：`openloader/resources/svs_fixes` 空粒子映射覆盖（NPE崩溃+粒子泛滥根因，mod 保留未删）

## 四、用户测试反馈 8 项的处理状态

| # | 问题 | 状态 |
|---|---|---|
| 1 | KubeJS errors + InControl onjoin 无效 | **已修**（见三-2、三-4） |
| 2 | 真菌币不掉、掉原版绿宝石 | **已修**（ent.monster 属性不存在 → 改 instanceof；绿宝石是生物自身掉落非本脚本） |
| 3 | /svs difficulty 意外错误 | **已修**（重写为 applyDifficultyOne，去掉 getPlayers/singletonList） |
| 4 | "控制台"是不是聊天界面 | **已答**：debug 日志在 latest.log/console.log（非聊天）；饥饿回复正常=狩猎红利已生效 |
| 5 | FTB 难度任务点完无效 | 同 #3 根因，**已修** |
| 6 | d&c 装备没汉化 | **已合并部署**：1048 条补译（d&c 913 + boss_checklist 62 + saintsdragons 15 + 25 ns 零星）已合入 `svs_zh_cn`（只覆盖英文值），副本/test4/仓库三处同步，commit e0d7c5d；合并脚本 `mcmp_test/merge_translations.py`（可复用）。待用户进游戏复测确认 |
| 7 | monsterexpansion.test_sword 紫黑贴图 | mod 自带调试物品缺贴图（mod bug），后续可 JEI 隐藏，不紧急 |
| 8 | 怪物索敌有问题 | **根因已修**：symbiote_counter tick 每次循环 `const p` 重声明报错刷屏（同时是卡顿元凶之一）→ 已改变量提升；待复测 |

**Rhino 血泪教训（写 KubeJS 必记）**：循环体内禁用 `const`/`let` 声明（重声明报错）→ 循环外声明循环内赋值；跨脚本共享作用域，全局 `const` 必须加脚本前缀防撞；`java.lang.Class`（含 forName/getClass 扫描）和 `java.lang.reflect` 被类过滤器拦截；**成员访问一律写 mojmap 名**（KubeJS Rhino 生产环境自动 remap mojmap→SRG，直写 SRG 名反而报 no public instance field）；优先用 Forge 原生事件（如 VillagerTradesEvent）零反射。

## 四点五、9-24 错误报告分析（22:08 + 22:42 两份，均已处理）

- **POTB NPE 崩溃（22:07 与 22:42 两次，第二次硬崩在游戏中）**：`WeaponryParticleRender.onRenderParticleEvent:48` 对 `getEntityPatch()` 未判空。CFR 反编译实证：tick 循环对 `blade_config_tag:valid_entity` 标签生物发事件，EF 不给 piglin/vex 等打补丁 → patch 为 null 必崩；ParticleEvent 无 @Cancelable 事件层拦不住，配置无实体开关。**已修**：svs 数据包置空该标签（replace:true values:[]，commit b1ef352），只保留玩家（必有 EF 补丁）。代价：怪物武器不再冒粒子（纯装饰）。根治收尾：自研 tweak mod mixin 给 onRenderParticleEvent 补判空后可恢复标签
- **KubeJS 1 error（spore_coin 村民交易）两轮失败**：① `java.lang.Class.forName` 被类过滤器拦（22:05）→ ② 改直读静态字段仍挂（22:39）——实踩结论：**KubeJS Rhino 生产环境自动 remap mojmap→SRG，直写 SRG 名（f_35627_）反而报 "no public instance field"，成员访问必须写 mojmap 名** → ③ 最终改 Forge 原生 `VillagerTradesEvent`（ForgeEvents.onEvent）零反射（commit cd77c4c），待复测村民交易
- **SimplySwords 配置损坏**：test4 的 `simplyswords_main` 里 gem_effects/general/status_effects 三个 json5 被刷成全空白（mod 回退默认值）→ 已从副本完好文件覆盖修复
- **symbiote_counter 确认修好**：22:42 日志无 tick 刷屏错误（#8 索敌/卡顿复测通过一半，剩游戏内体感确认）
- 无害噪音（不修）：fancymenu 枚举 6 个 ns 资源失败、epic_fight_avalon 1 个空 JSON、l2weaponry 3 个 cloggrum 武器 JSON 解析失败、EF 一批 "Skill xxx doesn't exist"（mod 自带引用缺失技能）、woc_remastered refmap 警告

## 五、待办（按优先级）

0. **结构密度提纯已落地**（决议一-6 远梦方案，commit 见日志）：svs_tweak 新增 StructureCheckDensityMixin——75 格（≈5 区块半径）最多 1 结构，记录存维度 SavedData 只进不出；白名单=陨石+灾变 8 座+竞技场 3 座（通行且不占坑），忽略=roadweaver 全线/原版村庄/小型点缀/匠魂浮空岛；**黑名单留空待用户裁决**（候选：shipwreck、mineshaft）

1. ~~合并 d&c 补译~~ **已完成**（见四-#6）；注意：副本里还有约 60 个 ns 的汉化目录未进 git 仓库（仓库只收了本次改的 28 个），下次大同步时一并 commit
2. 通知用户复测（**重点**：`Loaded 5/5 0 errors`、真菌币掉落、**村民交易（农民12币→8grout/工具匠20币→火种工具，本次新修）**、/svs difficulty、FTB 任务、索敌、d&c 汉化、POTB 是否还崩）
3. **二期**：~~围城事件 + HUD 天数计时器~~ **初版已落地**（`siege.js`，commit e7937ba：7日倒计时/在村才走（村民≥3+主世界）/回村回拨5分钟/Painter HUD/波次 8+2递增+14天起掺精英；待实测）→ 失守惩罚（文明降级+均摊扣款，决议一-5；**civillis API 已打通**：`BaseScoreApi.add/remove`，火种侧已挂钩 commit 66eb43f）**失守判定+惩罚已落地**（commit 2f47193：村民腰斩判失守、文明 -15、在场均摊 40 币单人全额、失守 HUD/标题；待实测）→ ~~铁魔法禁用清单~~ **已定稿落地**（commit 见日志：`docs/铁魔法禁用清单.md`，禁 78/留 36，数据包已三处同步；用户裁决：机动/隐身作逃课保留、召唤流禁、直伤全禁）→ ~~Gateways 连战+武器解锁~~ **用户裁决否决**（9-25）：不加 Gateways/Placebo、不锁武器。草案文档留档备查。末期武器毕业改由任务线直接发放（待细化）。共生体围城压力联动**已接**（commit cd11c7c：围城内已结合玩家 stress +3/s，SymbioteTracker.adjustStress javap 实证）
4. ~~打 test6.zip~~ **已完成**：`dist/test6.zip`（2132 文件 / 1425.8 MB）。旧打包脚本丢失，新写 `E:/mcmp_test/pack_mcbbs.py`（从副本出包，结构对齐 test5 逆向：manifest.json + mcbbs.packmeta(SHA-1) + overrides/，包含清单=test5 的 16 项 + scripts/）。**含全部最新修复**（补译/POTB 标签置空/spore_coin 事件版/siege.js）。注意：test6 以副本为准，**含 souls_like_bosses-1.0.3.jar**（test4 没有，对账问题仍待用户裁决）
5. 自研 tweak mod 待办清单：~~结构距出生点生成限制~~（**已落地** commit cfbfc5c：陨石限出生点 3000 格内，方向/数值待用户确认）、~~ASTages 坏文件容错~~（**已落地** commit dd06e12：readList 换安全版，坏 JSON 跳过打日志不崩，require=0 防版本漂移）、~~mixin 冲突合规化~~（**已落地** commit 1748317：MixinSquared 取消器运行时禁 2 个冲突 mixin，两 jar 已恢复官方原版+hash 回正；MixinSquared 0.2.0 作库 mod 进包；**复测要点：日志找 [svs_tweak] 已按冲突清单取消 mixin ×2，且这两个 mixin 原本治的冲突不复发**）、~~POTB jar 层根治~~（**已构建部署** commit 772f6f3：`svs_tweak-1.0.0.jar` 已进副本+test4 mods/，源码收在仓库 `svs_tweak/`；POTB 判空 mixin 已生效待实测。**验证无 POTB 崩溃后**：删 `svs/data/blade_config_tag` 置空覆盖即可恢复怪物武器粒子。构建：本地 Gradle 8.8（E:/mcmp_test/gradle-8.8，services.gradle.org 超时改用腾讯镜像）+ JDK 17，libs/ 放 potb/epicfight jar 作编译期签名依赖）
6. `scripts/stages.zs`（GameStages 门控框架，目前全注释零效果）**只在仓库、未双写**（副本/test4 的 scripts/ 是空目录）；等有实质内容再同步，届时 test 包要确认 scripts/ 进 overrides
7. bug 清单遗留：Blood And Madness TPS 性能+2武器EF适配、BOMD 虚空之花崩档、Relics×真菌 CME、真菌飞行怪崩档（等初版实测复现后 BadMobs 禁）

## 六、关键事实速查

- 启动：`python E:\mcmp_test\launch_test4.py --mem 10G`（quickPlay 世界 "test"；到主菜单约 200-350 秒，不是卡死）
- 日志：`test4/logs/latest.log` GBK 编码（python `decode("gbk")`）；崩溃报告 `test4/crash-reports/`
- 杀游戏：powershell `Get-CimInstance ... | Where CommandLine -match 'BootstrapLauncher' | Stop-Process`
- CF 下载：edge.forgecdn.net 直链（文件名要 URL 编码），cfwidget.com 数字项目 id 可用（`api.cfwidget.com/<id>`）
- qoder：`qoderclicn -m GLM-5.3-Flash -p --permission-mode bypass_permissions`，批量任务后台跑；复杂正则/中文**不要走 bash heredoc**（会转义炸，用 Write 工具写 .py）
- 共生体 API：`SymbioteTracker.get(level).peek(uuid)` → profile.stage/trust/stamina；`PredatorHunt.isHunting(uuid)`
- 工作原则：先修不删/手术式变更/目标驱动验收/简洁优先（见任务文档）
- 分工：K3 出规格+审查+验证，GLM 写批量码；mixin/字节码/多人/经济代码 K3 亲写
