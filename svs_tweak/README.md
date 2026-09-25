# SvS Tweaks —— 整合包自研 tweak mod

当前功能（5 个 mixin，配置见 `svs_tweak.mixins.json`）：
- `PotbWeaponryParticleRenderMixin` — POTB 粒子渲染 NPE 判空（`WeaponryParticleRender.onRenderParticleEvent` HEAD 注入，`getEntityPatch()` 为 null 即跳过；带自检探针）
- `PrimaryLevelDataSpawnMixin` — 记录世界出生点（供陨石距离限制）
- `StructureCheckSpawnLimitMixin` — 陨石只在出生点 3000 格内生成
- `StructureCheckDensityMixin` — 结构密度提纯（75 格半径最多 1 个结构，白名单/忽略/黑名单见 `StructureDensityRules`）
- `AStagesBadFileMixin` — ASTages 坏文件容错（readList 安全版）
- 另有 `SvsMixinCanceller`（MixinSquared ServiceLoader）运行时取消 2 个冲突 mixin

## ⚠️ 构建红线：jar manifest 必须带 MixinConfigs

Forge 1.20.1 靠 **MANIFEST 的 `MixinConfigs` 属性**注册 mixin 配置。`build.gradle` 的 jar 任务里已写入：

```groovy
tasks.named('jar', Jar).configure {
    manifest {
        attributes([
                'MixinConfigs': 'svs_tweak.mixins.json',   // ← 漏了这行 = 5 个 mixin 全部静默失效
                ...
```

**2026-09-25 踩坑实证**：1.0.0 的 jar 漏了这一行，导致 5 个 mixin 一个都没被应用（POTB NPE 因此复发并崩客户端三次）；
而 MixinSquared 的取消器走 ServiceLoader 通道、不读该属性，日志里照常打印"已取消 mixin"，让人误以为 mixin 在工作。
**自检**：启动日志里应出现 `[mixin/]: Mixin config svs_tweak.mixins.json ...`（"does not specify minVersion" 是无害告警，看到它=配置已注册）。

## 构建

```
JAVA_HOME=<JDK17> E:/mcmp_test/gradle-8.8/bin/gradle.bat --offline jar
```

- JDK 17；本地 Gradle 8.8 在 `E:/mcmp_test/gradle-8.8`（依赖已缓存，可离线构建）
- `libs/` 需放编译期签名依赖（只编译不打包）：`potb-2.3.1.jar`、`epicfight-20.14.17.jar`、`astages-2.5.3.jar`、
  `mixinsquared-0.2.0.jar` —— **mixinsquared 必须用 forge jar 内嵌的 `META-INF/jars/MixinSquared-0.2.0.jar`**，
  平台 jar 里没有 `com.bawnorton.mixinsquared.api` 包，直接用会编译失败
- 产物放副本 + test4 的 `mods/`，两处都要同步；jar 本体不入版本库（`.gitignore` 全局禁 jar）

## 探针（判断 mixin 是否真的生效）

`PotbWeaponryParticleRenderMixin` 首次被调用、首次拦到 null patch 时各打一行日志（**用 SLF4J**——本包 AsyncLogger
`wrapSysOutSysErr=false`，`System.out` 只进 `logs/console.log` 不进 `latest.log`）：

```
[svs_tweak/]: [svs_tweak] POTB 判空 mixin 已注入 WeaponryParticleRender.onRenderParticleEvent（首次调用）
[svs_tweak/]: [svs_tweak] POTB 判空生效：已拦截 entityPatch=null 的粒子渲染（该实体会崩，改为跳过；同类不再刷屏）
```

规划项见 `docs/HANDOVER.md` 待办"自研 tweak mod"。