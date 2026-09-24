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
- 游戏实测可进世界；FTB 九章任务线骨架在（暮色章已删待重排）；桌面表已按新包体重采

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
| 6 | d&c 装备没汉化 | **进行中**：IMF-Trans 的 zh 文件 913/1177 值是英文原文，GLM 补译 1048 条（dac_1~4+others）**已完成在 `i18n_work/translated/en_vals/`，但尚未合并进 zh 文件、未部署** ← 交接后第一件事 |
| 7 | monsterexpansion.test_sword 紫黑贴图 | mod 自带调试物品缺贴图（mod bug），后续可 JEI 隐藏，不紧急 |
| 8 | 怪物索敌有问题 | **根因已修**：symbiote_counter tick 每次循环 `const p` 重声明报错刷屏（同时是卡顿元凶之一）→ 已改变量提升；待复测 |

**Rhino 血泪教训（写 KubeJS 必记）**：循环体内禁用 `const`/`let` 声明（重声明报错）→ 循环外声明循环内赋值；跨脚本共享作用域，全局 `const` 必须加脚本前缀防撞；`Java.loadClass('java.lang.Class').forName` 不可用 → NativeJavaClass 直接读静态字段 `VillagerTrades.f_35627_`。

## 五、待办（按优先级）

1. **合并 d&c 补译**：`i18n_work/translated/en_vals/*.json` → 按 ns 合并进 `svs_zh_cn/assets/<ns>/lang/zh_cn.json`（只覆盖英文值，保留已有中文）→ 双写 → 交用户复测 #6
2. 通知用户复测 8 项修复（**重点**：重进世界看 `Loaded 5/5 0 errors`、真菌币掉落、/svs difficulty、FTB 任务、索敌）
3. **二期**：围城事件 + HUD 天数计时器（7日周期/回村5分钟预警/不强加载，规格在决议）→ 铁魔法禁用清单 → Gateways 连战+武器解锁
4. 打 test6.zip（打包脚本同 test5 版，版本号改 test6）
5. 自研 tweak mod 待办清单：结构距出生点生成限制、ASTages 坏文件容错、mixin 冲突合规化、POTB jar 层根治
6. bug 清单遗留：Blood And Madness TPS 性能+2武器EF适配、BOMD 虚空之花崩档、Relics×真菌 CME、真菌飞行怪崩档（等初版实测复现后 BadMobs 禁）

## 六、关键事实速查

- 启动：`python E:\mcmp_test\launch_test4.py --mem 10G`（quickPlay 世界 "test"；到主菜单约 200-350 秒，不是卡死）
- 日志：`test4/logs/latest.log` GBK 编码（python `decode("gbk")`）；崩溃报告 `test4/crash-reports/`
- 杀游戏：powershell `Get-CimInstance ... | Where CommandLine -match 'BootstrapLauncher' | Stop-Process`
- CF 下载：edge.forgecdn.net 直链（文件名要 URL 编码），cfwidget.com 数字项目 id 可用（`api.cfwidget.com/<id>`）
- qoder：`qoderclicn -m GLM-5.3-Flash -p --permission-mode bypass_permissions`，批量任务后台跑；复杂正则/中文**不要走 bash heredoc**（会转义炸，用 Write 工具写 .py）
- 共生体 API：`SymbioteTracker.get(level).peek(uuid)` → profile.stage/trust/stamina；`PredatorHunt.isHunting(uuid)`
- 工作原则：先修不删/手术式变更/目标驱动验收/简洁优先（见任务文档）
- 分工：K3 出规格+审查+验证，GLM 写批量码；mixin/字节码/多人/经济代码 K3 亲写
