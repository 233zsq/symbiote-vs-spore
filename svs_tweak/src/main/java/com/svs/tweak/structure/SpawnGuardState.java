package com.svs.tweak.structure;

import net.minecraft.core.BlockPos;

/**
 * 共生体陨石距出生点生成限制的共享状态（决议一-6：关键结构距出生点生成限制）。
 * 方向解释（2026-09-25 实施时裁定）：限制为"只允许生成在出生点 MAX 距离内"——
 * 陨石是前期里程碑（任务文档理念 1），生成太远会找不到卡流程；密度提纯又把它压稀，更不能再远。
 * TODO(用户确认): 方向与数值 3000 格，若意为"离出生点至少 N 格"改这里即可。
 */
public final class SpawnGuardState {
    /** 目标结构类名（symbiote 陨石；用字符串避免对 symbiote 的编译期硬依赖） */
    public static final String METEOR_CLASS = "com.scout.symbiote.worldgen.MeteorCrashStructure";
    /** 允许生成的最大水平距离（格） */
    public static final int MAX_DISTANCE = 3000;
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

    /** 区块中心距出生点是否超限（水平面） */
    public static boolean beyondLimit(int chunkX, int chunkZ) {
        long bx = (long) chunkX * 16 + 8 - spawnX;
        long bz = (long) chunkZ * 16 + 8 - spawnZ;
        return bx * bx + bz * bz > MAX_DIST_SQ;
    }
}
