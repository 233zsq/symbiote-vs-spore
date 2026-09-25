package com.svs.tweak.mixin;

import com.svs.tweak.structure.StructureDensityData;
import com.svs.tweak.structure.StructureDensityRules;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureCheck;
import net.minecraft.world.level.levelgen.structure.StructureCheckResult;
import net.minecraftforge.server.ServerLifecycleHooks;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 结构密度提纯（决议一-6「远梦方案」75 格最多 1 结构）：
 * HEAD：非白名单结构在半径内已有结构记录 → START_NOT_PRESENT；
 * RETURN：实际生成的结构写入该维度 SavedData 占坑（只进不出）。
 * 全部 SRG 名 remap=false（生产环境专用），@Shadow 字段写 SRG 名。
 */
@Mixin(value = StructureCheck.class, remap = false)
public abstract class StructureCheckDensityMixin {

    @Shadow
    @Final
    private ResourceKey<Level> f_197241_;   // dimension

    @Shadow
    @Final
    private Registry<Structure> f_204945_;  // structure registry

    @Inject(method = "m_226729_", at = @At("HEAD"), cancellable = true)
    private void svs$densityCheck(ChunkPos chunkPos, Structure structure, boolean skipKnown,
                                  CallbackInfoReturnable<StructureCheckResult> cir) {
        ResourceLocation id = f_204945_.getKey(structure);
        if (id == null) return;
        int cls = StructureDensityRules.classify(id.toString());
        if (cls == 3) {                       // 黑名单：永不生成
            cir.setReturnValue(StructureCheckResult.START_NOT_PRESENT);
            return;
        }
        if (cls != 0) return;                 // 忽略/白名单：放行
        ServerLevel level = svs$level();
        if (level == null) return;
        if (StructureDensityData.get(level).countNearby(chunkPos.x, chunkPos.z, StructureDensityRules.CHUNK_RADIUS) >= StructureDensityRules.MAX_NEARBY) {
            cir.setReturnValue(StructureCheckResult.START_NOT_PRESENT);
        }
    }

    @Inject(method = "m_226729_", at = @At("RETURN"))
    private void svs$densityRecord(ChunkPos chunkPos, Structure structure, boolean skipKnown,
                                   CallbackInfoReturnable<StructureCheckResult> cir) {
        if (cir.getReturnValue() != StructureCheckResult.START_PRESENT) return;
        ResourceLocation id = f_204945_.getKey(structure);
        if (id == null) return;
        if (StructureDensityRules.classify(id.toString()) != 0) return;
        ServerLevel level = svs$level();
        if (level == null) return;
        StructureDensityData.get(level).record(chunkPos.x, chunkPos.z, id.toString());
    }

    private ServerLevel svs$level() {
        try {
            if (ServerLifecycleHooks.getCurrentServer() == null) return null;
            return ServerLifecycleHooks.getCurrentServer().getLevel(f_197241_);
        } catch (Throwable t) {
            return null;
        }
    }
}
