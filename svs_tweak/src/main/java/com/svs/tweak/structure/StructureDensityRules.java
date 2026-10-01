package com.svs.tweak.structure;

import java.util.Set;

/**
 * 结构密度提纯规则（决议一-6「远梦方案」：75 格半径最多 1 结构，空旷荒凉+地标感）。
 * 参数对齐远梦之棺 ash_of_sin/no_more_too_many_structures.toml（checkRadius=75, maxNearby=1）。
 * 半径按区块切比雪夫距离 5 区块（≈80 格）近似，TODO(调参) 如需贴 75 格精确值再改块级距离。
 */
public final class StructureDensityRules {
    /** 区块半径：|dx|,|dz| <= 5（≈80 格） */
    public static final int CHUNK_RADIUS = 5;
    /** 半径内最多结构数 */
    public static final int MAX_NEARBY = 1;

    /** 完全不参与（不检查、不记录）：路网/村庄/小型点缀/浮空岛 */
    public static final Set<String> IGNORE_PREFIX = Set.of(
            "roadweaver:"          // 阡陌路网全线（桥/营地/路村）——包的前期骨架，永不卡
    );
    public static final Set<String> IGNORE = Set.of(
            // 原版村庄与微结构
            "minecraft:village_plains", "minecraft:village_desert", "minecraft:village_savanna",
            "minecraft:village_snowy", "minecraft:village_taiga",
            "minecraft:ruined_portal", "minecraft:buried_treasure",
            // 匠魂浮空岛（悬在天上，不参与地面密度）
            "tconstruct:blood_island", "tconstruct:clay_island", "tconstruct:earth_slime_island",
            "tconstruct:end_slime_island", "tconstruct:ocean_skyslime_island", "tconstruct:sky_slime_island",
            // Terralith 小型点缀
            "terralith:rubble_desert", "terralith:rubble_forest", "terralith:rubble_jungle",
            "terralith:rubble_mesa", "terralith:rubble_mountain", "terralith:rubble_taiga",
            "terralith:igloo", "terralith:glacial_hut", "terralith:witch_hut", "terralith:underground_cabin",
            // jerotes 村庄（安全区，同原版村庄待遇）
            "jerotesvillage:botanize_village",
            "roadweaver:roadside_village"
    );

    /** 白名单（主线结构：永远生成，也不记录占坑——不影响其他结构）
     *  2026-10-01 用户裁决扩容 9 座：真菌线 spore 5 + SI 讨伐线 inqui 4（结构表拍板） */
    public static final Set<String> WHITELIST = Set.of(
            "symbiote:meteor_crash",                 // 共生体陨石（里程碑：共生）
            // 灾变主线 8 座（与远梦白名单一致）
            "cataclysm:soul_black_smith", "cataclysm:ruined_citadel", "cataclysm:burning_arena",
            "cataclysm:ancient_factory", "cataclysm:sunken_city", "cataclysm:cursed_pyramid",
            "cataclysm:frosted_prison", "cataclysm:acropolis",
            // 竞技场日课（中期主线）
            "pladailyboss:colosseum_arena", "skyarena:sky_arena", "skyarena:ice_arena",
            // 真菌线主线（阶段Ⅲ：前线→监狱→医院→实验室→大本营）
            "spore:military_camp", "spore:prison", "spore:hospital", "spore:lab", "spore:cathedral",
            // SI 定点讨伐线（阶段Ⅱ教学→Ⅲ 审判场）
            "inqui:tower", "inqui:underground", "inqui:entrance", "inqui:arena"
    );

    /** 黑名单（永不生成）。用户裁决：2026-09-26 禁 shipwreck + mineshaft（含变体）；
     *  2026-10-01 追加 bettermineshafts 全 13 变体（YUNG 矿井=原版矿井替代品语义重复，
     *  且 spacing=1 会垄断默认分支的淡化配额；结构表拍板）。
     *  spore:biomass_tower 维持默认档（实证只在蘑菇岛生成，淡化后即"被真菌吞噬的岛"） */
    public static final Set<String> BLACKLIST = Set.of(
            "minecraft:shipwreck", "minecraft:shipwreck_beached",
            "minecraft:mineshaft", "minecraft:mineshaft_mesa",
            "bettermineshafts:mineshaft_acacia", "bettermineshafts:mineshaft_desert",
            "bettermineshafts:mineshaft_ice", "bettermineshafts:mineshaft_jungle",
            "bettermineshafts:mineshaft_lush", "bettermineshafts:mineshaft_mesa",
            "bettermineshafts:mineshaft_mushroom", "bettermineshafts:mineshaft_oak",
            "bettermineshafts:mineshaft_red_desert", "bettermineshafts:mineshaft_spruce",
            "bettermineshafts:mineshaft_spruce_snowy", "bettermineshafts:mineshaft_overgrown",
            "bettermineshafts:mineshaft_dripstone"
    );

    private StructureDensityRules() {
    }

    /** 0=正常参与；1=忽略；2=白名单；3=黑名单 */
    public static int classify(String id) {
        if (BLACKLIST.contains(id)) return 3;
        if (WHITELIST.contains(id)) return 2;
        if (IGNORE.contains(id)) return 1;
        for (String p : IGNORE_PREFIX) {
            if (id.startsWith(p)) return 1;
        }
        return 0;
    }
}
