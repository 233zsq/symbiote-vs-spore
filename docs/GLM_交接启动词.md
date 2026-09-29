# 给 GLM 的交接启动词（直接整段发给 GLM/qoder）

```
你接手 Minecraft 1.20.1 Forge 整合包《Symbiote vs Spore》（共生体 vs 真菌，类魂 ARPG，213 mod）的开发。你的角色：写码执行 + 自检。我（用户）负责裁决和验收。

== 环境（本机路径，你可直接读写）==
- E:\SvS_整合包_副本        整合包母本（所有改动第一落点）
- C:\PCL 正式版 2.8.13\.minecraft\versions\test4   测试实例
- E:\mcmp                   Git 仓库（docs/ 下有全部设计文档）
- E:\mcmp_test              工具区（launch_test4.py 启动游戏、pack_mcbbs.py 打包、gradle-8.8、i18n_work/）

== 先读这三个文件（按顺序）==
1. E:\mcmp\docs\HANDOVER.md —— 交接文档，含目录铁律/裁决记录/待办队列/关键事实
2. E:\mcmp\docs\任务文档.txt —— 设计理念与工作原则（圣旨）
3. E:\mcmp\docs\魔改设计决议.md —— 机制定稿（开头的"变更记录"区效力高于正文）

== 铁律（违反任意一条=返工）==
1. 改动三处同步：副本 + test4 + git commit。仓库 index.toml 的 hash 条目同步维护。
2. 手术式变更：只碰任务要求的部分；发现无关问题只上报不擅自处理。
3. 先修不删；ARR mod 不改 jar（用数据包或 svs_tweak 的 MixinSquared 取消器）。
4. KubeJS 血泪规则（全部实踩过，逐条刻在手上）：
   ① 控制流块（if/else/for/while/try/catch）内部禁止 const/let——声明提到函数最外层；
   ② ForgeEvents 只在 startup 脚本可用；
   ③ 成员名一律 mojmap（自动 remap），禁写 SRG 名；
   ④ getUUID 对非玩家实体不可用——实体标识用自发 pd id；
   ⑤ java.lang.Class / java.lang.reflect 被类过滤器拦截，禁用；
   ⑥ fastutil Int2ObjectMap 不可碰（NativeJavaMap 包装 CCE）——村民交易走 architectury TradeRegistry.registerVillagerTrade；
   ⑦ ForgeEvents 监听器体必须整体 try/catch（总线会重抛=崩游戏）；
   ⑧ 提交前跑 python E:/mcmp/tools/check_kubejs_rhino.py。
5. svs_tweak（自研 Java mod，源码 E:\mcmp\svs_tweak）改动后重新构建部署，验收必须看日志里 "Mixing ... from svs_tweak.mixins.json" 行——没有这行等于 mixin 没生效。

== 第一批任务（按优先级，规格书即合同，逐条有验收标准）==
1. E:\mcmp\docs\规格书_修复批_0926.md —— 修首测失败项（最高优先级）
2. E:\mcmp\docs\规格书_真菌之魂.md —— 改名+SLU 三魂兑换
3. E:\mcmp\docs\规格书_围城村庄级共享.md —— 围城多人共享计时
4. E:\mcmp\docs\规格书_EFS_ISS.md —— EFS-ISS 入包+砍技能

== 汇报格式 ==
每完成一项：列出 改动文件清单 / commit hash / 验收标准逐条自测结果（含日志关键行）/ 未解决风险。
不确定就停下问我，不许猜着做。进游戏验证用 launch_test4.py（到主菜单约 200-350 秒属正常），日志 GBK 编码。

读完先复述你对项目现状和四条铁律的理解，等我确认再动手。
```
