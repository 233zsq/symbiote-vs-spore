package com.svs.tweak.kubejs;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.entity.npc.VillagerTrades;
import net.minecraft.world.entity.npc.VillagerTrades.ItemListing;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.structure.Structure;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;

import java.util.List;
import java.util.Map;

/**
 * 伤害结算辅助（2026-09-30 用户裁决"不接受一刀盲区"落地）：
 * KubeJS Rhino 无法解析 DamageSource.getEntity()/getDirectEntity()/is(TagKey)（mojmap 与
 * SRG 名直呼都查不到——9-30 五个探针局实证），也无法稳定解析实体的 isInWater()/onGround()。
 * 但把调用放进纯 Java 静态方法、由 JS 传入原生对象（architectury TradeRegistry 同款模式，
 * 参数传原生对象在本包已实证可行），就绕开了名称解析——伤害层的攻击者归因由此从
 * "getLastHurtByMob（上一刀，新目标首刀盲区）"升级为精确归因。
 */
public final class SvsDamageHelper {
    private SvsDamageHelper() {
    }

    /** 伤害来源的致害实体（causing：近战=攻击者本体，弹射物=射手） */
    public static Entity attackerOf(DamageSource source) {
        return source == null ? null : source.getEntity();
    }

    /** 伤害来源的直接实体（弹射物本体；近战与 attackerOf 相同） */
    public static Entity directOf(DamageSource source) {
        return source == null ? null : source.getDirectEntity();
    }

    /** 是否弹射物伤害（官方 DamageTypeTags.IS_PROJECTILE，1.19.4 伤害类型重构的标准判定） */
    public static boolean isProjectile(DamageSource source) {
        return source != null && source.is(DamageTypeTags.IS_PROJECTILE);
    }

    /** 实体是否在水中（Rhino 对该继承方法解析不稳，走本通道） */
    public static boolean inWater(Entity entity) {
        return entity != null && entity.isInWater();
    }

    /** 实体是否在地面 */
    public static boolean onGround(Entity entity) {
        return entity != null && entity.onGround();
    }

    /**
     * 村民交易表诊断（F2 排查用，2026-10-01）：dump VillagerTrades 静态表里各职业各等级的
     * listing 类名（Java 侧遍历 fastutil，绕开 Rhino 的 Int2ObjectMap 禁区）。
     * 传入职业名过滤（如 "farmer"，null=全部）。返回紧凑字符串供日志打印。
     */
    public static String villagerTradeDump(String profFilter) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<VillagerProfession, Int2ObjectMap<ItemListing[]>> e
                : VillagerTrades.TRADES.entrySet()) {
            String prof = String.valueOf(e.getKey());
            if (profFilter != null && !prof.contains(profFilter)) continue;
            sb.append('[').append(prof).append("] ");
            for (Int2ObjectMap.Entry<ItemListing[]> level : e.getValue().int2ObjectEntrySet()) {
                sb.append("L").append(level.getIntKey()).append('=');
                ItemListing[] arr = level.getValue();
                for (int i = 0; i < arr.length; i++) {
                    sb.append(i == 0 ? "" : ",").append(arr[i].getClass().getSimpleName());
                }
                sb.append(' ');
            }
        }
        return sb.length() == 0 ? "(无匹配职业)" : sb.toString();
    }

    /**
     * 结构寻址（2026-10-01 制图师线索书根治）：整条链（registry → HolderSet.direct →
     * findNearestMapStructure）放进纯 Java——Rhino 里 HolderSet.direct 的 varargs/List
     * 重载都 NPE，getOrCreateTag 走标签又难诊断空标签。返回 "X=..|Z=.." 或 null（未找到）。
     */
    public static String locateStructure(ServerLevel level, String ns, String path, BlockPos pos) {
        Registry<Structure> reg = level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        ResourceKey<Structure> key = ResourceKey.create(Registries.STRUCTURE, new ResourceLocation(ns, path));
        Holder<Structure> holder = reg.getHolderOrThrow(key);
        var found = level.getChunkSource().getGenerator()
                .findNearestMapStructure(level, HolderSet.direct(List.of(holder)), pos, 100, false);
        if (found == null) {
            return null;
        }
        BlockPos bp = found.getFirst();
        return "X=" + bp.getX() + "|Z=" + bp.getZ();
    }
}
