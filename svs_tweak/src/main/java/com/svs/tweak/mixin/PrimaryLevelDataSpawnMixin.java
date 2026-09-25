package com.svs.tweak.mixin;

import com.svs.tweak.structure.SpawnGuardState;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.storage.PrimaryLevelData;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 记录主世界出生点（ServerLevelData.setSpawn 由 PrimaryLevelData 实现，世界创建与
 * /setworldspawn 都会走到；remap=false 因目标为 SRG 生产名 m_7250_）。
 */
@Mixin(value = PrimaryLevelData.class, remap = false)
public abstract class PrimaryLevelDataSpawnMixin {

    @Inject(method = "m_7250_", at = @At("TAIL"))
    private void svs$recordSpawn(BlockPos pos, float angle, CallbackInfo ci) {
        SpawnGuardState.setSpawn(pos);
    }
}
