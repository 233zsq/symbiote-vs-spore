package com.svs.tweak.mixin;

import com.alessandro.astages.api.util.AFileIOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * AStages 坏文件容错（2.5.3 实证）：
 * AFileIOUtils.readFileContent 只 catch IOException，Gson 的 JsonParseException（RuntimeException）
 * 会穿透 readFromFile 的 forEach 导致加载崩溃；且 IOException 路径返回 null，
 * readFromFile 里 for (restriction : null) 照样 NPE。
 * 此处把 lambda$readFromFile$6 里的 readList 调用换成安全版：任何异常/null → 空表 + 打日志。
 * require=0：astages 版本升级导致 lambda 序号漂移时静默失效（退回原版行为），不崩游戏。
 */
@Mixin(targets = "com.alessandro.astages.engine.ASimpleRestrictionManager", remap = false)
public abstract class AStagesBadFileMixin {

    private static final Logger SVS_LOGGER = LoggerFactory.getLogger("svs_tweak");

    @Redirect(
            method = "lambda$readFromFile$6",
            at = @At(value = "INVOKE", target = "Lcom/alessandro/astages/api/util/AFileIOUtils;readList(Ljava/nio/file/Path;Ljava/lang/Class;)Ljava/util/List;"),
            require = 0
    )
    private static List<?> svs$readListSafe(Path file, Class<?> elementClazz) {
        try {
            List<?> r = AFileIOUtils.readList(file, elementClazz);
            return r != null ? r : new ArrayList<>();
        } catch (Throwable t) {
            SVS_LOGGER.error("[svs_tweak] AStages 限制文件损坏已跳过: {} ({})", file, t.toString());
            return new ArrayList<>();
        }
    }
}
