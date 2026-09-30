package com.svs.tweak.structure;

import net.minecraft.core.BlockPos;

/**
 * 共生体陨石距出生点生成限制的共享状态（决议一-6：关键结构距出生点生成限制）。
 * 用户裁决 2026-09-26（修复批 F7）：只允许生成在出生点 400~800 格环带内——
 * 离出生点太近会开局白捡，太远会找不到卡流程（前期里程碑）。
 */
public final class SpawnGuardState {
    /** 目标结构类名（symbiote 陨石；用字符串避免对 symbiote 的编译期硬依赖） */
    public static final String METEOR_CLASS = "com.scout.symbiote.worldgen.MeteorCrashStructure";
    /** 允许生成的最小水平距离（格）——环带内环 */
    public static final int MIN_DISTANCE = 400;
    /** 允许生成的最大水平距离（格）——环带外环 */
    public static final int MAX_DISTANCE = 800;
    public static final long MIN_DIST_SQ = (long) MIN_DISTANCE * MIN_DISTANCE;
    public static final long MAX_DIST_SQ = (long) MAX_DISTANCE * MAX_DISTANCE;

    /** 主世界出生点；setSpawn 被调用前回退 (0,0)（原版出生点本来就在原点附近） */
    private static volatile int spawnX = 0;
    private static volatile int spawnZ = 0;

    private SpawnGuardState() {
    }

    public static void setSpawn(BlockPos pos) {
        spawnX = pos.getX();
        spawnZ = pos.getZ();
    }

    /** 区块中心距出生点是否在 400~800 环带之外（水平面；太近或太远都拒绝） */
    public static boolean beyondLimit(int chunkX, int chunkZ) {
        long bx = (long) chunkX * 16 + 8 - spawnX;
        long bz = (long) chunkZ * 16 + 8 - spawnZ;
        long distSq = bx * bx + bz * bz;
        return distSq < MIN_DIST_SQ || distSq > MAX_DIST_SQ;
    }
}
