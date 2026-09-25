// svs_damage.js — 伤害结算统一层（魔改二期 · 决议一-4/五-1 合并落地）
// ⚠️ 必须在 startup 脚本：ForgeEvents 只在 startup 注入（字节码实证）。
// 监听 Forge 原生 LivingHurtEvent，直接 event.setAmount——javap 实证 1.20.1 的
// LivingHurtEvent/LivingDamageEvent 都有 setAmount(float)。彻底取代"下一 tick 补刀/回补"
// 方案：那条路的两大病灶——补刀被无敌帧差值分支整段吃掉（远程加压空转）、
// 增伤补刀与限伤回补互相抵消（400 伤害打 Boss 实际只结一半）——在本层不复存在。
// 评审建议的 EF 原生钩子不需要：EF 事件只覆盖 EF 玩家出手，盖不住怪物弹射物与 Boss 受击。
// 结算顺序：乘区（①共生减伤 ②共生增伤 ③远程加压）→ 限伤（④精英 cap + 母巢爬升）。
// cataclysm 命名空间整体跳过④（原生 cap_config 已对齐 DOTE，双重结算会变成打 Boss 回血）。

;(function registerSvsDamage() {
  const Monster = Java.loadClass('net.minecraft.world.entity.monster.Monster')
  const SD_ServerPlayer = Java.loadClass('net.minecraft.server.level.ServerPlayer')
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
  // 远程加压（决议一-4）
  const RP_MULT = 1.5
  // 精英/Boss 限伤（决议一-4）
  const ELITE_MIN_HP = 200, ELITE_CAP = 0.10, SKIP_NS = 'cataclysm:'
  // 母巢模板（spore mound→proto 线；8% 上限 + 累计爬升减伤封顶 90% + 停手 5s 衰减）
  const HIVEMIND = ['spore:proto']
  const HIVE_CAP = 0.08, HIVE_RATE_MAX = 0.90, HIVE_DECAY_DELAY = 100, HIVE_DECAY_PER_SEC = 0.20

  // ── Rhino 守则（2026-09-25 崩服实证）──────────────────────────────────────
  // 控制流块（if / for / while / try / catch）**内部**不得声明 const/let：
  // 第二次执行到同一行必抛 "TypeError: redeclaration of var X"。
  // 本文件挂 Forge 原生总线，未捕获的脚本异常被总线记录后重新抛出 → 直接崩游戏
  // （曾以 svs_damage.js#83 `const maxHp` 崩过一次：Ticking entity / ElderGuardian）。
  // 故：块内只做赋值，声明一律提到所属函数最外层；校验 tools/check_kubejs_rhino.py。
  let bsTracker = null, bsProf = null, bsPdStage = ''
  let sdEnt = null, sdSrc = null, sdSrcEnt = null, sdType = '', sdFromSpore = false, sdAmount = 0
  let sdRed = 0, sdMult = 1, sdIsProj = false, sdPress = false
  let sdMaxHp = 0, sdIsHive = false, sdCap = 0, sdRate = 0
  let sdPd = null, sdCum = 0, sdLast = 0, sdNow = 0, sdEffective = 0

  // 自包含档位判定（与 symbiote_counter.getBondStage 同逻辑，不跨脚本依赖）
  function bondStage(player) {
    if (SymbioteTracker) {
      try {
        bsTracker = SymbioteTracker.get(player.level)
        bsProf = bsTracker ? bsTracker.peek(player.getUUID()) : null
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
      sdSrcEnt = sdSrc ? sdSrc.entity : null
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

      // ③ 远程加压：怪物的弹射物在飞行/水中命中 → ×1.5（玩家的不管）
      sdIsProj = false
      try { sdIsProj = !!sdSrc.isProjectile() } catch (e) { }
      if (sdIsProj && sdSrcEnt && !sdSrcEnt.player) {
        sdPress = false
        try { sdPress = sdSrcEnt.isInWater() || !sdSrcEnt.onGround() } catch (e) { }
        if (sdPress) sdAmount = sdAmount * RP_MULT
      }

      // ④ 限伤：精英/Boss 通用 10% cap + 母巢 8%+爬升（cataclysm 走原生 cap，跳过）
      // 评审修正：只认敌对生物（Monster），中立/召唤物/坐骑不误伤；母巢名单例外（proto 是 organoid）
      if (!sdEnt.player && sdType.indexOf(SKIP_NS) !== 0) {
        sdMaxHp = sdEnt.maxHealth
        sdIsHive = HIVEMIND.indexOf(sdType) >= 0
        if ((sdIsHive || sdEnt instanceof Monster) && (sdMaxHp >= ELITE_MIN_HP || sdIsHive)) {
          sdCap = ELITE_CAP
          sdRate = 0
          if (sdIsHive) {
            sdCap = HIVE_CAP
            sdPd = sdEnt.getPersistentData()
            sdCum = sdPd.getDouble('svs_dc_cum')
            sdLast = sdPd.getLong('svs_dc_last')
            sdNow = sdEnt.level.gameTime
            if (sdLast > 0 && sdNow - sdLast > HIVE_DECAY_DELAY) {
              sdCum = Math.max(0, sdCum - (sdNow - sdLast - HIVE_DECAY_DELAY) / 20 * HIVE_DECAY_PER_SEC * sdMaxHp)
            }
            sdRate = Math.min(HIVE_RATE_MAX, sdCum / sdMaxHp)
            sdEffective = Math.min(sdAmount, sdCap * sdMaxHp) * (1 - sdRate)
            sdPd.putDouble('svs_dc_cum', sdCum + sdEffective)
            sdPd.putLong('svs_dc_last', sdNow)
          }
          sdAmount = Math.min(sdAmount, sdCap * sdMaxHp) * (1 - sdRate)
        }
      }

      if (sdAmount !== event.amount) event.setAmount(sdAmount)
    } catch (e) {
      console.error('[SVS-伤害] 监听器异常（已兜住，不崩游戏）: ' + e)
    }
  })
  console.info('[SVS-伤害] 统一伤害层已注册：共生两向 + 远程加压 + 精英限伤 + 母巢爬升（LivingHurtEvent.setAmount 直改）')
})()
