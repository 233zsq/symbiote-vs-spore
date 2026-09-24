package com.svs.tweak.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import sleys.potb.system.events.RenderParticleEvent;

/**
 * POTB (ParticlesOnTheBlades) NPE 根治：
 * WeaponryParticleRender.onRenderParticleEvent 对 event.getEntityPatch() 未判空——
 * blade_config_tag:valid_entity 标签内、EpicFight 不打补丁的生物（piglin/vex 等）
 * 或补丁尚未 attach 的实体被 tick 到时必崩（2026-09-24 两次实崩，crash report 实证）。
 * 此处 HEAD 注入：patch 为 null 直接跳过该实体本次粒子渲染。
 */
@Mixin(targets = "sleys.potb.system.engine.WeaponryParticleRender", remap = false)
public abstract class PotbWeaponryParticleRenderMixin {

    @Inject(method = "onRenderParticleEvent", at = @At("HEAD"), cancellable = true, require = 0)
    private static void svs$nullPatchGuard(RenderParticleEvent.ParticleEvent event, CallbackInfo ci) {
        if (event == null || event.getEntityPatch() == null) {
            ci.cancel();
        }
    }
}
