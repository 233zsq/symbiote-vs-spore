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

  // 自包含档位判定（与 symbiote_counter.getBondStage 同逻辑，不跨脚本依赖）
  function bondStage(player) {
    if (SymbioteTracker) {
      try {
        const tracker = SymbioteTracker.get(player.level)
        const prof = tracker ? tracker.peek(player.getUUID()) : null
        if (prof && prof.stage) return String(prof.stage.name())
      } catch (e) { }
    }
    try {
      const s = player.getPersistentData().getString('svs_bond_stage')
      return s ? String(s) : null
    } catch (e) {
      return null
    }
  }

  ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingHurtEvent', event => {
    const ent = event.entity
    if (!ent || !ent.type) return
    const src = event.source
    const srcEnt = src ? src.entity : null
    const type = String(ent.type)
    const fromSpore = !!(srcEnt && srcEnt.type && String(srcEnt.type).indexOf(SPORE_NS) === 0)
    let amount = event.amount

    // ① 共生体减伤：玩家被 spore 实体伤害 → 按档位减免
    if (ent.player && fromSpore) {
      const red = DMG_REDUCE[bondStage(ent)]
      if (red) amount = amount * (1 - red)
    }
    // ② 共生体增伤：已结合玩家打 spore Monster → 按档位乘伤
    else if (ent.monster && type.indexOf(SPORE_NS) === 0
      && srcEnt && srcEnt.player && srcEnt instanceof SD_ServerPlayer) {
      const mult = DMG_MULT[bondStage(srcEnt)]
      if (mult) amount = amount * mult
    }

    // ③ 远程加压：怪物的弹射物在飞行/水中命中 → ×1.5（玩家的不管）
    let isProj = false
    try { isProj = !!src.isProjectile() } catch (e) { }
    if (isProj && srcEnt && !srcEnt.player) {
      let press = false
      try { press = srcEnt.isInWater() || !srcEnt.onGround() } catch (e) { }
      if (press) amount = amount * RP_MULT
    }

    // ④ 限伤：精英/Boss 通用 10% cap + 母巢 8%+爬升（cataclysm 走原生 cap，跳过）
    if (!ent.player && type.indexOf(SKIP_NS) !== 0) {
      const maxHp = ent.maxHealth
      const isHive = HIVEMIND.indexOf(type) >= 0
      if (maxHp >= ELITE_MIN_HP || isHive) {
        let cap = ELITE_CAP
        let rate = 0
        if (isHive) {
          cap = HIVE_CAP
          const pd = ent.getPersistentData()
          let cum = pd.getDouble('svs_dc_cum')
          const last = pd.getLong('svs_dc_last')
          const now = ent.level.gameTime
          if (last > 0 && now - last > HIVE_DECAY_DELAY) {
            cum = Math.max(0, cum - (now - last - HIVE_DECAY_DELAY) / 20 * HIVE_DECAY_PER_SEC * maxHp)
          }
          rate = Math.min(HIVE_RATE_MAX, cum / maxHp)
          const effective = Math.min(amount, cap * maxHp) * (1 - rate)
          pd.putDouble('svs_dc_cum', cum + effective)
          pd.putLong('svs_dc_last', now)
        }
        amount = Math.min(amount, cap * maxHp) * (1 - rate)
      }
    }

    if (amount !== event.amount) event.setAmount(amount)
  })
  console.info('[SVS-伤害] 统一伤害层已注册：共生两向 + 远程加压 + 精英限伤 + 母巢爬升（LivingHurtEvent.setAmount 直改）')
})()
