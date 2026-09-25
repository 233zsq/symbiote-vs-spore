package com.svs.tweak;

import com.bawnorton.mixinsquared.api.MixinCanceller;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Set;

/**
 * MixinSquared 取消器：运行时禁用两个冲突 mixin，替代此前直接改 jar 内 mixin json 的做法
 * （两 mod 均为 ARR，改 jar 属演绎作品越界；本方案不动对方 jar 一个字节，见 docs/开源协议审查.md）。
 * <p>
 * 被取消的 mixin（原版 jar 内的 .class 仍在，只是不注册应用）：
 * 1. monsterexpansion: PlayerDefenseDamageReductionMixin —— @Redirect Player.actuallyHurt 的 setHealth，
 *    与本包减伤体系冲突
 * 2. cataclysmic_arsenal: CMItemStackRendererMixins —— @Redirect CMItemstackRenderer.renderByItem 的
 *    RenderType 调用（焚化者/炎雷武器状态贴图），与渲染管线冲突
 */
public class SvsMixinCanceller implements MixinCanceller {
    private static final Logger LOGGER = LoggerFactory.getLogger("svs_tweak");
    private static final Set<String> CANCEL = Set.of(
            "net.saksolm.monsterexpansion.mixin.PlayerDefenseDamageReductionMixin",
            "sleys.cataclysmicarsenal.mixins.CMItemStackRendererMixins"
    );

    @Override
    public boolean shouldCancel(List<String> targetClassNames, String mixinClassName) {
        if (CANCEL.contains(mixinClassName)) {
            LOGGER.info("[svs_tweak] 已按冲突清单取消 mixin: {}", mixinClassName);
            return true;
        }
        return false;
    }
}
