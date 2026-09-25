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
            "minecraft:ruined_portal", "minecraft:buried_treasure", "minecraft:mineshaft", "minecraft:mineshaft_mesa",
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

    /** 白名单（主线结构：永远生成，也不记录占坑——不影响其他结构） */
    public static final Set<String> WHITELIST = Set.of(
            "symbiote:meteor_crash",                 // 共生体陨石（里程碑：共生）
            // 灾变主线 8 座（与远梦白名单一致）
            "cataclysm:soul_black_smith", "cataclysm:ruined_citadel", "cataclysm:burning_arena",
            "cataclysm:ancient_factory", "cataclysm:sunken_city", "cataclysm:cursed_pyramid",
            "cataclysm:frosted_prison", "cataclysm:acropolis",
            // 竞技场日课（中期主线）
            "pladailyboss:colosseum_arena", "skyarena:sky_arena", "skyarena:ice_arena"
    );

    /** 黑名单（永不生成）：待用户裁决后填入。候选：minecraft:shipwreck、minecraft:mineshaft（远梦同款） */
    public static final Set<String> BLACKLIST = Set.of();

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
