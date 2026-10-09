# CTI（Construct Technological Innovation）匠魂体系拆解与借鉴

> 对象：`C:\PCL 正式版 2.8.13\.minecraft\versions\Construct Technological Innovation`（MC **1.19.2** Forge，274 mod，匠魂 3.8.5.58 + Mantle 1.10.48）
> 日期：2026-09-21。注意版本代差：CTI 是 1.19.2，mod 版本不能照搬，学的是结构。

## 一、CTI 的匠魂生态（19 件相关 mod）

| 类别 | mod | 作用 |
|---|---|---|
| 本体 | TConstruct + Mantle | 匠魂 3 + 库 |
| 跨 mod 联动 | TCIntegrations、thermal_integration | 外来材料（龙钢/热力系）匠魂化 |
| 新材料 | Tinkers Reforged、Tinkers' Thinking、Tinkers Calibration | 大量新材料 |
| 新工具/部件 | Tinkers Ingenuity、cloudertinker（巨剑刃部件） | 激光/电池等自创 stat 类型 |
| 国产附属 | **etshtinker（CTI 特供版）**、solidarytinker、cherrytinker、tinkersinnovation（`_no_compat` 构建） | 作者直接找附属作者出**整合包特供构建**，把联动主导权收归自己 |
| 机制 | TinkersLevellingAddon | 工具升级 |
| 辅助 | TConJEI、Tinker's Planner | JEI 集成、材料搭配模拟器 |
| 内容 | Tinker Villager | 工匠村民 |

## 二、魔改方法论（教科书级数据包驱动）

1. **材料全部走 KubeJS 数据包**（515 个 tinkering JSON）：
   - `kubejs:` 命名空间 17 个全新材料 + `cti:` 22 个原创毕业材料（配 zh_cn lang 写材料名/风味文本）
   - 覆写原版材料数值（钢头耐久 1440、挖掘等级下界合金、挂自定义特性）
   - 自定义强化定义（如 `cti:cosmic` +5 升级槽 +2 能力槽）
2. **空 JSON 黑科技禁用工具**：`tool_definitions/war_pick.json` 等内容为 `{}` 直接禁用战镐/战斗牌子/熔炼锅
3. **跨 mod 兼容**：冶炼炉铸件配方 68 个（Thermal 板/齿轮/杆直接浇铸）、合金配方搬家、模板函数一次生成"熔炼+铸件+流体+材料"五种配方
4. **减法**：配方黑名单删 76 条匠魂配方，逼着走作者设计的产线
5. **配置收口**：TinkersLevelling 锁成"升级只给槽位不加属性"，防数值膨胀

## 三、对我们的借鉴

### 我们现状

匠魂 3.12.0.220 + Mantle + **EF Tinker Compat**（EF 联动已由它负责——CTI 没有 EF，这块无需借鉴）。匠魂附属一个都没有。

### 建议安装的匠魂附属（1.20.1 已核实有版）

| mod | 1.20.1 版本 | 作用 | 优先级 |
|---|---|---|---|
| TConJEI | 1.6.1 | 冶炼炉配方进 JEI，刚需辅助 | ★★★ |
| Tinkers Reforged | 2.20.0.7 | 大量新材料（含对常见 mod 矿物的兼容） | ★★★ |
| Tinkers' Thinking | 0.1.6.6.3 | 新材料 | ★★☆ |
| Tinkers' Ingenuity | 1.1.9 | 新工具/部件类型 | ★★☆ |
| TinkersLevellingAddon | 1.4.3 | 工具升级（需照 CTI 锁配置防膨胀） | ★★☆ |
| cloudertinker | 1.2.10 | 国产附属，巨剑刃部件（配 EF 大剑流） | ★★☆ |
| cherry-tinker | 1.0.0 | 国产附属 | ★☆☆ |
| TCIntegrations | 2.0.25.19 | 跨 mod 材料联动（我们没装热力/龙钢，意义打折） | ★☆☆ |
| Tinker's Planner / Tinkers Calibration / solidarytinker | 1.20.1 未找到 | — | 跳过 |

### 不装 mod 就能学的（KubeJS 数据包，我们已有 KubeJS）

1. **把我们包的特色材料注册成匠魂材料**：灾变炎魔锭、暮色骑士金属/铁木、血源菱铁锭/血钢锭、SLU 魂系材料、Jerotes 材料——照 CTI 的 `tinkering/materials/{definition,stats,traits}` 三件套格式写，材料名直接有现成汉化
2. **"打完 Boss 给匠魂材料"的任务奖励线落地后**，用自定义材料特性把这些材料做成毕业级匠魂部件（如炎魔锭部件自带燃魂特性）
3. 空 JSON 禁用与 EF 手感冲突的匠魂武器（如有必要）
4. TinkersLevelling 若装，配置锁"只给槽不加属性"
