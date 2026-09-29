# Symbiote vs Spore 交接文档（写给下一个 AI）

> 更新：2026-09-29。整合包开发移交给下一个 AI。本文件是唯一权威交接面。
> 主规格：`docs/任务文档.txt`（设计理念 13 条+工作原则）；机制定稿：`docs/魔改设计决议.md`。

## 〇、30 秒版

1. 你在维护一个 MC 1.20.1 Forge 整合包（213 mod），共生体 vs 真菌题材，类魂 ARPG。
2. **先读第五节"血泪教训"再写任何一行脚本**——90% 的坑都趟过了，别再踩。
3. 改动一律三处同步：副本 → test4 → git 仓库（见第二节）。
4. 用户在 `docs/任务文档.txt` 写了四条工作原则（三思/简洁/手术式/目标驱动），那是圣旨。
5. 待办队列在第七节，其中 4 份规格书可直接执行。

## 一、项目与主文档索引

| 文档 | 内容 |
|---|---|
| `docs/任务文档.txt` | 设计理念 + 工作原则（最高优先级） |
| `docs/魔改设计决议.md` | 机制定稿（2026-09-23 逐条拍板） |
| `docs/数值表_武器.md` 等、桌面 5 张 xlsx | 数值基准（重采口径见 9-19 实采记录） |
| `docs/武器线与匠魂节奏_参考综合.md` | 四参考包拆包结论（任务线重写用） |
| `docs/任务线重排迁移清单.md` | FTB 任务线重写工单（用户裁决：全部重写） |
| `docs/铁魔法禁用清单.md` | ISS 禁 78/留 36（已定稿落地） |
| `docs/规格书_*.md` ×4 | 可直接执行的开发规格书（见第七节） |
| `docs/开源协议审查.md` | 协议合规；改动 mod 清单必须同步登记 |
| `docs/HANDOVER.md` 历史段落（四点五~四点十一） | 历次事故与修复的完整档案（git 历史可溯） |

## 二、目录布局与同步铁律（勿乱）

| 位置 | 角色 |
|---|---|
| `E:\SvS_整合包_副本` | 整合包母本，所有改动第一落点，打 zip 从这出 |
| `C:\PCL 正式版 2.8.13\.minecraft\versions\test4` | 用户实测实例（PCL 管理） |
| `E:\mcmp` | Git 仓库（GitHub 233zsq/symbiote-vs-spore） |
| `E:\mcmp_test` | 工具区：launch_test4.py、pack_mcbbs.py、dist/testN.zip、i18n_work/、backup/、svs_tweak 构建环境 |

**铁律**：
1. 改 mod/配置/KubeJS → 副本+test4 双写 → 仓库 commit。三方漂移是历史重灾区（坑过两次）
2. 用户在 PCL 侧加减的 mod（.disabled / 手动删 jar）以用户为准，对账后同步副本
3. 打包：`python E:\mcmp_test\pack_mcbbs.py testN`（MCBBS 格式，manifest+mcbbs.packmeta(SHA-1)+overrides）
4. kubejs 脚本双写注意：`explorers_compass.js`/`weapon_balance.js` 是阶段⑤骨架，只在仓库+副本，不进 test4（有意豁免）；`example.js` 只在副本（KubeJS 自动生成）

## 三、当前状态（2026-09-29）

- 213 mod（jar 实数）；最新包 `dist/test9.zip`（含全部修复）
- KubeJS：startup 5 个（example/items/spore_coin/villager_trades/svs_damage）+ server 7 个+example
- 自研 mod `svs_tweak-1.0.2.jar`：5 个功能（POTB 判空/陨石距出生点 400~800 待 GLM 改/密度提纯 75 格 1 结构/AStages 容错/MixinSquared 取消器），源码在仓库 `svs_tweak/`，构建用 `E:/mcmp_test/gradle-8.8` + JDK17
- 用户首测（9-26）：稳定性全过；交易/火种/共生加成/真菌币掉落/HUD 有失败项 → 修复规格书已出待 GLM 执行

## 四、已拍板裁决记录（不许推翻，不许重做调研）

- 视角：Leawind's Third Person 2.2.0（IF 同款配置已在包内），ShoulderSurfing 已删
- 不加 Gateways/Placebo，不锁武器；末期武器毕业走任务线直发（内容用户自定）
- 铁魔法：禁 78 留 36（定稿 `docs/铁魔法禁用清单.md`）；机动/隐身作逃课保留
- souls_like_bosses 已删（用户裁决；SLU souls-like-universe 是主线，别搞混）
- EFS-ISS 入包（剑术耗蓝=它），砍 4 个过强技能（二次呼吸/连通根源/自动回复/备用魔力）
- 真菌币改名"真菌之魂"（只改显示名不动 id），单向兑换 SLU 三魂
- 删除通用 10% 限伤层（保留灾变原生 cap+母巢 proto 模板）；结构黑名单禁 shipwreck+mineshaft
- 陨石限出生点 400~800 格环带；SI 开局 spreadplayers 撒人用数据包覆盖 start4 去除
- FTB 任务线全部重写；stage2 下界章删除；阶段Ⅲ灾变 Boss 序列承接
- Structurify 不加（密度互斥/陨石限制 svs_tweak 已覆盖，它只能当黑名单面板）
- 难度三选取一锁二；交易限量 16；火种 7 天=离线时长；限伤只认敌对

## 五、血泪教训（KubeJS/Rhino/Forge，全部实踩）

**写 KubeJS 前必读，每条都崩过或静默失效过**：

1. **声明规则（最终版）**：控制流块（if/else/for/while/**try**/catch）**内部**不得出现 const/let——第二次执行到同一行必抛 redeclaration。声明一律提到函数/回调最外层。函数最外层随便用
2. **ForgeEvents 只在 startup 脚本注入**（BuiltinKubeJSForgePlugin 字节码实证）——server/client 脚本里 ForgeEvents 是 not defined
3. **成员访问一律写 mojmap 名**：KubeJS Rhino 生产环境自动 remap mojmap→SRG；直写 SRG 名（f_35627_）反而报 no public instance field
4. **getUUID 在非玩家实体上解析失败**（Cannot find function）——实体标识用自发 pd id（如 `svs_fireseed_id`）；玩家 getUUID 正常
5. **java.lang.Class / java.lang.reflect 被类过滤器拦截**——forName/getClass 扫描/reflect.Array 全不可用；静态字段用 NativeJavaClass 直读（mojmap 名），数组扩容用 java.util.Arrays.copyOf
6. **fastutil Int2ObjectMap 不可碰**（NativeJavaMap 包一层，任何属性访问都 CCE，JS try/catch 兜不住）——村民交易走 architectury `TradeRegistry.registerVillagerTrade`（静态方法零 Map 访问），别碰 VillagerTradesEvent.trades
7. **KubeJS 自有事件吞异常**（功能静默失效只刷日志），**Forge 总线事件重抛异常**（=崩游戏）——ForgeEvents 监听器体必须整体 try/catch
8. **入库前跑扫描器**：`python E:/mcmp/tools/check_kubejs_rhino.py`（块内声明检查，已写进 CONTRIBUTING）
9. **svs_tweak 验证**：MANIFEST 必须有 `MixinConfigs: svs_tweak.mixins.json`（漏了=5 个 mixin 全静默失效，实崩过）；验收看日志 `Mixing ... from svs_tweak.mixins.json` 行，不能只看 mod 加载成功
10. 启动到主菜单约 200~350 秒（DH+全量 mod，不是卡死）；日志 GBK 编码（python decode("gbk")）

## 六、已落地魔改清单（详表见各 commit 与历史段落）

- 一期：LootBeams 静音、InControl 难度规则、FTB 序章难度三选（选一锁二）、真菌币经济（掉落+3 笔村民交易+陨石线索书）、个人难度 /svs、共生体克制真菌四件套、火种绑定+civillis 文明分、血源 6 武器 EF 适配、POTB 根治、d&c 等 92 ns 汉化
- 二期：围城系统全套（倒计时/HUD/波次/失守惩罚/文明分/共生压力联动）、铁魔法禁用 78、灾变限伤对齐 DOTE（活配置 cataclysm-common.toml）、母巢限伤爬升（proto）、远程加压、统一伤害层（LivingHurtEvent.setAmount 直改）、共生体分期 1 数值加成+GameStage 镜像
- tweak mod 五件套 + 双指南针入包+全量汉化

## 七、待办队列

**可直接执行的规格书（喂给写码的 AI）**：
1. `docs/规格书_修复批_0926.md`（F1~F10：币不掉落/交易缺失/火种奖励/HUD NaN/删通用限伤/黑名单/陨石 400~800+SI 撒人/stages.zs 改名/EFS-ISS/贴图已交付）**← 最高优先级**
2. `docs/规格书_真菌之魂.md`（改名+SLU 三魂兑换）
3. `docs/规格书_围城村庄级共享.md`（多人共享计时+村外环带生成）
4. `docs/规格书_EFS_ISS.md`（入包+砍技能+耗蓝调参）

**等用户**：首测失败项复测（修复后）；FTB 任务线重写（游戏内编辑器，用户/指导进行）；阶段Ⅲ承接细化；末期武器毕业内容（先更新武器表，需一次游戏内 dump）

**实测触发才有下文**：真菌飞行怪崩档（复现后填 badmobs）、BOMD 虚空之花、Relics×真菌 CME、BaM TPS

## 八、工作方式要求（用户定的，务必遵守）

1. 任务文档四条工作原则是圣旨：三思而后行（不确定就问、呈现多种解读、必要时反驳、困惑就停）/ 简洁优先 / 手术式变更（不顺手改无关项、发现无关问题只上报）/ 目标驱动（每个任务有可验证的验收标准）
2. **先修不删**：崩溃/冲突优先修复；修不了保留并报告
3. 大型机械任务（批量翻译/批量 JSON）才派子代理；决策和验收自己把关
4. 改动要有 commit 记录，信息写清"改了什么/为什么/验收点"
5. 协议合规：mod 清单变动必须登记 `docs/开源协议审查.md`；ARR mod 不改 jar（用 MixinSquared 取消器或数据包）
6. 历史档案：本文件四点五~四点十一节（git 历史）有全部事故记录——排查同类问题先查档案

## 九、关键事实速查

- 启动测试：`python E:\mcmp_test\launch_test4.py --mem 10G`（quickPlay 进世界 "test"）
- 日志：`test4/logs/latest.log`（GBK）；崩溃报告 `test4/crash-reports/`
- 杀残留游戏进程：`E:\mcmp_test\kill_zombies.ps1`（powershell -ExecutionPolicy Bypass -File）
- CF 下载：edge.forgecdn.net 直链（文件名 URL 编码）；cfwidget 数字 id 可用（api.cfwidget.com/<id>）；Modrinth API 正常
- Gradle：services.gradle.org 被墙，用腾讯镜像本地包 `E:/mcmp_test/gradle-8.8`
- 共生体 API：`SymbioteTracker.get(level).peek(uuid)` → stage/trust/stamina；`adjustTrust/adjustStress(ServerLevel,ServerPlayer,int,String)`；`PredatorHunt.isHunting(uuid)`
- 文礼 API：`civil.civilization.BaseScoreApi.add(ServerLevel, BlockPos min/max, double, sourceKey)` / `remove(sourceKey)`
- CFR 反编译器：`E:/mcmp_test/` 或 /tmp 的 cfr.jar（0.152）；javap 用 `C:/Program Files/Java/jdk-21/bin/javap.exe`
