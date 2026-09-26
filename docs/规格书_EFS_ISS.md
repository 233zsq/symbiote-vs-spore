# 规格书：EFS-ISS 入包 + 剑术耗蓝弱化（2026-09-26，用户裁决选 ①）

> 执行方：GLM。依据：理念 9"剑术耗蓝开启+冷却 2 倍"——用户确认指向 EFS-ISS（远梦同款）。

## 1. 入包

- 文件：`efs_iss-1.0.3.jar`（CF 项目 epic-fight-skill-irons-spells-n-spellbooks，作者 merlin204，
  1.20.1 Forge；**远梦之棺 mods/ 里有同版 jar 可直接拷**，CF 下载亦可）
- 协议：**ARR**（jar mods.toml 实证）——CF 生态整合包默认可用，登记进《开源协议审查》变更记录
- 依赖：EpicFight + Iron's Spells（都有）；无其他前置
- pw 条目 + index 登记 + 双写副本/test4

## 2. 技能裁剪（弱化铁律：4 个过强技能不给玩家）

| 技能 | 处置 | 理由 |
|---|---|---|
| Second Wind 二次呼吸（烧蓝免死） | 切断获取 | 直接违反"伪高难"死亡惩罚体系 |
| Connect to the Root 连通根源（无限蓝） | 切断获取 | 耗蓝体系被架空 |
| Auto Heal 自动回复（蓝转血） | 切断获取 | 强回复，同禁用清单 C 区精神 |
| Reserve Mana 备用魔力（低于 10% 回满） | 切断获取 | 同上 |
| Magic Blade 魔法战刃 / Rapid Chant / Hasty Casting / Blood into Mana / Mana Shield / Magic Immunity | 保留 | 耗蓝联动本体 |

切断方式：GLM 实测这些技能的获取途径（技能书战利品/配方/指令），用 svs 数据包移除其配方与战利品项；
若技能本身注册即自动解锁，再报 K3 走 MixinSquared 取消器路线。

## 3. 耗蓝与冷却调参

- EFS-ISS 无 TOML 配置（jar 实证），可调面在数据包 `data/efs_iss/skill_parameters/*.json`
  （jar 自带 breathe_again/reserve_mana 两条，格式 `{"consumption": 20.0}`）
- 用 svs 数据包给**保留技能**补 skill_parameters：GLM 先实测各技能基础蓝耗，
  再按"耗蓝有感但不卡手"上调（初版：现有值 ×2）
- "冷却 2 倍"：EF 技能冷却在 EF 侧，GLM 实测 `epicfight-common.toml` 与技能 JSON 可调范围后回报参数，不要硬写

## 4. 验收

1. 进游戏无错；EF 技能界面能看到保留的 EFS-ISS 技能，4 个砍掉的拿不到
2. 魔法战刃挥剑释放当前法术且蓝耗可见下降
3. 协议审查已登记
