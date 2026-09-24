package com.svs.tweak;

import net.minecraftforge.fml.common.Mod;

/**
 * SvS 整合包自研 tweak mod（Symbiote vs Spore）。
 * 当前功能：POTB 粒子渲染 NPE 判空（mixin）。
 * 规划：结构距出生点生成限制、ASTages 坏文件容错、mixin 冲突合规化（见 docs/HANDOVER.md 待办 #5）。
 */
@Mod(SvsTweak.MODID)
public class SvsTweak {
    public static final String MODID = "svs_tweak";

    public SvsTweak() {
        // 纯 mixin 修复，无注册内容
    }
}
