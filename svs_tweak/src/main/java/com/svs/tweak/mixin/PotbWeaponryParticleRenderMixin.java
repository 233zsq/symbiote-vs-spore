package com.svs.tweak.mixin;

import org.slf4j.LoggerFactory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import sleys.potb.system.events.RenderParticleEvent;

/**
 * POTB (ParticlesOnTheBlades) NPE 根治：
 * WeaponryParticleRender.onRenderParticleEvent 对 event.getEntityPatch() 未判空——
 * blade_config_tag:valid_entity 标签内、EpicFight 不打补丁的生物（piglin/vex 等）
 * 或补丁尚未 attach 的实体被 tick 到时必崩（2026-09-24 / 2026-09-25 三次实崩）。
 * 此处 HEAD 注入：patch 为 null 直接跳过该实体本次粒子渲染。
 *
 * 探针（svs$seen / svs$guardHits）用于确认本 mixin 真的被应用——
 * 因为 jar 曾漏配 MANIFEST 的 MixinConfigs，导致 5 个 mixin 静默失效：
 * 只有 MixinSquared 取消器（ServiceLoader 通道）生效，看起来"好像装了 mixin"。
 */
@Mixin(targets = "sleys.potb.system.engine.WeaponryParticleRender", remap = false)
public abstract class PotbWeaponryParticleRenderMixin {

    @Unique
    private static boolean svs$seen = false;

    @Unique
    private static int svs$guardHits = 0;

    @Inject(method = "onRenderParticleEvent", at = @At("HEAD"), cancellable = true, require = 0)
    private static void svs$nullPatchGuard(RenderParticleEvent.ParticleEvent event, CallbackInfo ci) {
        if (!svs$seen) {
            svs$seen = true;
            // 用 SLF4J 而非 System.out：本包 AsyncLogger 的 wrapSysOutSysErr=false，
            // System.out 只进 logs/console.log，不进 latest.log（排查时会找不到日志）
            LoggerFactory.getLogger("svs_tweak").info("[svs_tweak] POTB 判空 mixin 已注入 WeaponryParticleRender.onRenderParticleEvent（首次调用）");
        }
        if (event == null || event.getEntityPatch() == null) {
            svs$guardHits++;
            if (svs$guardHits == 1) {
                LoggerFactory.getLogger("svs_tweak").info("[svs_tweak] POTB 判空生效：已拦截 entityPatch=null 的粒子渲染（该实体会崩，改为跳过；同类不再刷屏）");
            }
            ci.cancel();
        }
    }
}
