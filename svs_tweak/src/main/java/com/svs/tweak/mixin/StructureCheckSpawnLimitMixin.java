package com.svs.tweak.mixin;

import com.svs.tweak.structure.SpawnGuardState;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureCheck;
import net.minecraft.world.level.levelgen.structure.StructureCheckResult;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 共生体陨石距出生点生成限制（决议一-6）：
 * StructureCheck.checkStart（生产 SRG 名 m_226729_）是结构生成与 /locate 的统一入口，
 * HEAD 拦截：主世界内、目标为陨石结构、区块超出出生点 MAX_DISTANCE → 返回"无结构"。
 * remap=false：注入目标写 SRG 名（m_226729_ / 影子字段 f_197241_），本 mod 只面向生产环境，
 * 绕开 MixinGradle refmap 依赖。@Shadow 字段直接写 SRG 名（reobf 不改自有声明，生产环境字面匹配）。
 */
@Mixin(value = StructureCheck.class, remap = false)
public abstract class StructureCheckSpawnLimitMixin {

    @Shadow
    @Final
    private ResourceKey<Level> f_197241_;

    @Inject(method = "m_226729_", at = @At("HEAD"), cancellable = true)
    private void svs$limitMeteorDistance(ChunkPos chunkPos, Structure structure, boolean skipKnown,
                                         CallbackInfoReturnable<StructureCheckResult> cir) {
        if (f_197241_ != Level.OVERWORLD) return;
        if (!SpawnGuardState.METEOR_CLASS.equals(structure.getClass().getName())) return;
        if (SpawnGuardState.beyondLimit(chunkPos.x, chunkPos.z)) {
            cir.setReturnValue(StructureCheckResult.START_NOT_PRESENT);
        }
    }
}
