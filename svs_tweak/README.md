# SvS Tweaks —— 整合包自研 tweak mod

当前功能：POTB 粒子渲染 NPE 判空 mixin（WeaponryParticleRender.onRenderParticleEvent HEAD 注入，getEntityPatch() 为 null 即跳过）。

构建：`gradle build`（JDK 17，本地 Gradle 8.8 在 E:/mcmp_test/gradle-8.8；libs/ 需放 potb 与 epicfight 的 jar 作编译期签名依赖，见 build.gradle）。

规划项见 docs/HANDOVER.md 待办"自研 tweak mod"。
