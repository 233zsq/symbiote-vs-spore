package com.svs.tweak.kubejs;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.tags.DamageTypeTags;

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
}
