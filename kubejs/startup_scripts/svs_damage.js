// svs_damage.js — 伤害结算统一层（魔改二期 · 决议一-4/五-1 合并落地）
// ⚠️ 必须在 startup 脚本：ForgeEvents 只在 startup 注入（字节码实证）。
// 监听 Forge 原生 LivingHurtEvent，直接 event.setAmount——javap 实证 1.20.1 的
// LivingHurtEvent/LivingDamageEvent 都有 setAmount(float)。彻底取代"下一 tick 补刀/回补"
// 方案：那条路的两大病灶——补刀被无敌帧差值分支整段吃掉（远程加压空转）、
// 增伤补刀与限伤回补互相抵消（400 伤害打 Boss 实际只结一半）——在本层不复存在。
// 评审建议的 EF 原生钩子不需要：EF 事件只覆盖 EF 玩家出手，盖不住怪物弹射物与 Boss 受击。
// 结算顺序：乘区（①共生减伤 ②共生增伤 ③远程减压）。
// 用户裁决 2026-10-01：③由"远程加压"反转为"远程减压"——本包主打近战（EF），
// 敌我双方受到的弹射物伤害一律 ×0.5，主线 Boss 直接免疫远程；并取消全部脚本层限伤
//（母巢 8% 爬升模板已删；灾变原生 cap 是 mod 配置层，是否同步取消待用户确认）。

;(function registerSvsDamage() {
  const SD_ServerPlayer = Java.loadClass('net.minecraft.server.level.ServerPlayer')
  // 伤害归因助手（svs_tweak ≥1.0.4）：DamageSource.getEntity()/is(TagKey)/实体 isInWater/onGround
  // 在 KubeJS Rhino 里名称解析全部失败（mojmap/SRG 名都不通，9-30 五探针局实证）→
  // 调用放进纯 Java 静态方法、JS 传原生对象（architectury TradeRegistry 同款已实证模式）。
  // 2026-09-30 用户裁决"不接受一刀盲区"的落地：攻击者归因由此从 getLastHurtByMob
  //（上一刀，新目标首刀盲区）升级为精确归因；助手缺失时退回旧通道（保留首刀盲区）。
  let SvsDamageHelper = null
  try {
    SvsDamageHelper = Java.loadClass('com.svs.tweak.kubejs.SvsDamageHelper')
  } catch (e) {
    console.error('[SVS-伤害] SvsDamageHelper 加载失败（svs_tweak ≥1.0.4 缺失？），归因退化为 getLastHurtByMob: ' + e)
  }
  let SymbioteTracker = null
  try {
    SymbioteTracker = Java.loadClass('com.scout.symbiote.tracker.SymbioteTracker')
  } catch (e) {
    console.error('[SVS-伤害] SymbioteTracker 加载失败，共生两向关闭: ' + e)
  }

  const SPORE_NS = 'spore:'
  // 共生体克制（决议五-1，与 symbiote_counter 共享数值源——改这里要同步改那边的注释）
  const DMG_MULT = { ATTACHED: 1.1, INTEGRATED: 1.2, COOPERATIVE: 1.35, DOMINANT: 1.5 }
  const DMG_REDUCE = { ATTACHED: 0.10, INTEGRATED: 0.15, COOPERATIVE: 0.22, DOMINANT: 0.30 }
  // 远程减压（2026-10-01 裁决：EF 近战包，远程一律减压）——敌我双方弹射物伤害 ×0.5
  const RP_MULT = 0.5
  // 主线 Boss 远程免疫名单（裁决原文"boss直接免疫远程"，逼近战）：
  // 灾变全命名空间（含 DailyBoss-Cataclysm 复用的灾变怪）+ BOMD 三 Boss + 母巢 proto。
  // 名单待用户增删（SLU/血源/竞技场 Boss 未收，见汇报）
  const RP_IMMUNE_PREFIX = ['cataclysm:', 'bosses_of_mass_destruction:']
  const RP_IMMUNE_EXACT = ['spore:proto']

  // ── Rhino 守则（2026-09-25 崩服实证）──────────────────────────────────────
  // 控制流块（if / for / while / try / catch）**内部**不得声明 const/let：
  // 第二次执行到同一行必抛 "TypeError: redeclaration of var X"。
  // 本文件挂 Forge 原生总线，未捕获的脚本异常被总线记录后重新抛出 → 直接崩游戏
  // （曾以 svs_damage.js#83 `const maxHp` 崩过一次：Ticking entity / ElderGuardian）。
  // 故：块内只做赋值，声明一律提到所属函数最外层；校验 tools/check_kubejs_rhino.py。
  let bsTracker = null, bsProf = null, bsPdStage = ''
  let sdEnt = null, sdSrc = null, sdSrcEnt = null, sdType = '', sdFromSpore = false, sdAmount = 0
  let sdRed = 0, sdMult = 1, sdIsProj = false, sdImmune = false

  // Boss 远程免疫判定（前缀 + 精确名单）
  function remoteImmune(typeStr) {
    for (let i = 0; i < RP_IMMUNE_PREFIX.length; i++) {
      if (typeStr.indexOf(RP_IMMUNE_PREFIX[i]) === 0) return true
    }
    return RP_IMMUNE_EXACT.indexOf(typeStr) >= 0
  }

  // 自包含档位判定（与 symbiote_counter.getBondStage 同逻辑，不跨脚本依赖）
  function bondStage(player) {
    if (SymbioteTracker) {
      try {
        bsTracker = SymbioteTracker.get(player.level)
        // player.uuid（KubeJS 注入属性）9-30 探针实证可用；getUUID() 连 ServerPlayer 都失败
        bsProf = bsTracker ? bsTracker.peek(player.uuid) : null
        if (bsProf && bsProf.stage) return String(bsProf.stage.name())
      } catch (e) { }
    }
    try {
      bsPdStage = player.getPersistentData().getString('svs_bond_stage')
      return bsPdStage ? String(bsPdStage) : null
    } catch (e) {
      return null
    }
  }

  // 兜底 try/catch：Forge 总线收到脚本异常会重新抛出（=崩游戏），
  // 这里自兜一次，任何 JS 失误只留一行日志，不打断伤害结算、不崩档。
  // 注意：try 也是一层块——回调体内不得再出现 const/let（否则又踩 redeclaration 坑）。
  ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingHurtEvent', event => {
    try {
      sdEnt = event.entity
      if (!sdEnt || !sdEnt.type) return
      sdSrc = event.source
      // 攻击者（致害实体）：优先 svs_tweak 静态助手精确取（近战=攻击者本体、弹射物=射手）；
      // 助手不可用时退回受害者侧 getLastHurtByMob（上一刀的攻击者，新目标首刀盲区）
      sdSrcEnt = null
      if (SvsDamageHelper) {
        try { sdSrcEnt = SvsDamageHelper.attackerOf(sdSrc) } catch (e) { sdSrcEnt = null }
      }
      if (!sdSrcEnt) {
        try { sdSrcEnt = sdEnt.getLastHurtByMob() } catch (e) { sdSrcEnt = null }
      }
      sdType = String(sdEnt.type)
      sdFromSpore = !!(sdSrcEnt && sdSrcEnt.type && String(sdSrcEnt.type).indexOf(SPORE_NS) === 0)
      sdAmount = event.amount

      // ① 共生体减伤：玩家被 spore 实体伤害 → 按档位减免
      if (sdEnt.player && sdFromSpore) {
        sdRed = DMG_REDUCE[bondStage(sdEnt)]
        if (sdRed) sdAmount = sdAmount * (1 - sdRed)
      }
      // ② 共生体增伤：已结合玩家打 spore Monster → 按档位乘伤
      else if (sdEnt.monster && sdType.indexOf(SPORE_NS) === 0
        && sdSrcEnt && sdSrcEnt.player && sdSrcEnt instanceof SD_ServerPlayer) {
        sdMult = DMG_MULT[bondStage(sdSrcEnt)]
        if (sdMult) sdAmount = sdAmount * sdMult
      }

      // ③ 远程减压（2026-10-01 裁决反转：主打近战的 EF 包，远程是逃课手段要压）：
      // 弹射物伤害敌我双方一律 ×0.5；Boss 免疫名单内直接归零（逼近战）。
      // isProjectile 走 svs_tweak 助手官方 DamageTypeTags.IS_PROJECTILE 判定。
      sdIsProj = false
      if (SvsDamageHelper) {
        try { sdIsProj = SvsDamageHelper.isProjectile(sdSrc) } catch (e) { }
      }
      if (sdIsProj) {
        sdImmune = remoteImmune(sdType)
        if (sdImmune) {
          sdAmount = 0
        } else {
          sdAmount = sdAmount * RP_MULT
        }
      }

      if (sdAmount !== event.amount) event.setAmount(sdAmount)
    } catch (e) {
      console.error('[SVS-伤害] 监听器异常（已兜住，不崩游戏）: ' + e)
    }
  })
  console.info('[SVS-伤害] 统一伤害层已注册：共生两向 + 远程减压×0.5 + Boss 免疫远程（LivingHurtEvent.setAmount 直改；全部脚本层限伤已按 10-01 裁决移除；归因走 svs_tweak 助手）')
})()
