# EF 适配差距分析（对照 DOTE / Immersive Fight）

> 日期：2026-09-21。数据：桌面四张表同一数据源（test4 实测）+ 两包拆解。

## 一、两个参照包的方法论

**Immersive Fight 4.2.9**（1.20.1 / EF 20.14.17，308 mod，与我们同代）三层分工：
- mod 层供给能力：EF 本体 + 24 个附属（WoM/剑仙/EFN/Resurrection/弯刀/刺剑/悟空等与我们重合）
- **数据包层做适配**：imfdata 343 个武器 capability JSON 覆盖 36 个 mod + 99 个自定义武器类型 + indestructible 的 advanced_mobpatch 给 15 种生物做动作——**第三方武器一律不改 jar，全走数据包**（我们已继承这套 imfdata）
- 资源包层做表现：IMF-Trail 249 个 item_skins 统一外观、IMF-Modify 276 个动画覆写、刀光粒子

**DUEL OF THE END**（1.18.2 / EF 18.5，260 mod）：
- Paxi 数据包：125 武器 + 118 护甲 + 29 盾牌 capability；46 个 mobpatch（13 个自制 Boss 用**玩家模型+阶段化武器动作组**）
- 自制 mod 链（jobinsmobs/stellarisdlc/guhao/star）撑私有人形 Boss
- 但它是 EF18 时代，**文件不可直接搬，只能学思路**

## 二、我们的缺口（实测覆盖率）

### 武器 EF 覆盖（总 1331 件，已适配 947）

| mod | 已适配/总数 | 缺口 | 优先级 |
|---|---|---|---|
| jerotesvillage | 0/155 | **155** | ★★★ 最大缺口 |
| jerotes | 0/55 | **55** | ★★★ |
| dungeons_and_combat | 112/211 | 99 | ★★☆（有 CompatLink 底子，补剩余） |
| legendary_monsters | 15/26 | 11 | ★☆☆ |
| bloodandmadness | 0/17 | 17 | ★☆☆（枪械/变形武器，部分不适合近战化） |
| spore | 6/19 | 13 | ★☆☆ |
| irons_spellbooks | 5/17 | 12 | 低（法术杖不必全适配） |
| twilightforest | 16/20 | 4 | 低 |

（史诗骑士/简易刀剑/灾变/WoM/SLU/EFN/悟空/弯刀等 100% 已覆盖；jerotes 两 mod、血源、孢子 jar 内零 EF 适配，已开包实证）

### 生物 EF 覆盖（敌对 560 个）

- 有动作适配的：仅 EF 原生 mod 内 91 个（SLU 77 + WoM/EFN/弯刀等）
- **mobpatch 数据包：0 个**——我们一个都没做
- 但注意：mobpatch 只对**人形怪**有意义（DOTE 也只做了 46 个，IF 15 个）。真菌巨兽/龙类不需要

## 三、行动建议

### A. 建议安装的 EF 附属 mod（1.20.1 均已确认有版，IF 同款）

| mod | CF 文件 | 作用 |
|---|---|---|
| Epic Fight - Mobs Plus | MobsPlus-Forge-EFM-20.14.11-1.1.5（id 8152400） | EF 风怪物群，自带 65 个动画模型 |
| Epic Fight - Super Warden | super_warden-20.13.0（id 7144759） | EF 化超级监守者 Boss |
| Tactical Imbuements | tactical-imbuements-1.20.1-0.12.1（id 6043747） | 战术附魔 × EF 联动 |

DOTE 的 impactful/epicacg/ef_irp 等是 1.18 限定，装不了；IF 的 fight_more/epicgoop/celepic 是作者私货，外部不可得（我们 imfdata 里对它的引用残留靠懒加载容忍，无害）。

### B. 需要我们写数据包适配的（照 imfdata 现成格式抄）

1. **jerotesvillage + jerotes（210 件武器）**：最大工程。两件 mod 的武器多为特效型，按 IF 极简格式 `{"type": "epicfight:xxx", "attributes": {...}}` 批量生成即可，先用脚本按攻击/攻速自动分型（剑/大剑/斧/枪）再人工修特殊件
2. **dungeons_and_combat 剩余 99 件**：CompatLink 已覆盖一半，照抄补齐
3. bloodandmadness 17 件近战（锯齿猎刀/千阴/葬仪之刃等适合 EF，枪械除外）
4. legendary_monsters 11 + spore 13 + twilightforest 4：零散补齐

### C. 生物 mobpatch（可选增强）

用包里已有的 **indestructible（advanced_mobpatch 加载器）**，给类人 Boss 写动作补丁，候选：灾变先驱者/燃魂、传奇怪物人形 Boss、Jerotes 人形精英、Bosses'Rise 人形件。参考 DOTE 的 `advanced_mobpatch/*.json` 阶段化写法（血量阶段切武器动作组）。

### D. 不建议做的

- 全量小怪 mobpatch（IF/DOTE 都没做，性价比低）
- 真菌巨兽/龙类的 EF 动作化（非人形，EF 骨架不适用）
- 为 irons_spellbooks 法杖做近战适配（法术模组定位不同）
