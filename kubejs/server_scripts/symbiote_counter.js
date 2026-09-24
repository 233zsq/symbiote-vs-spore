// symbiote_counter.js — 共生体克制真菌 · 分期 1（魔改第一期 · 规格 3）
// 能力四件套（只对 spore 命名空间实体生效）：
//   ① 伤害克制：已结合玩家对真菌伤害 ×1.1 / ×1.2 / ×1.35 / ×1.5
//      （ATTACHED / INTEGRATED / COOPERATIVE / DOMINANT）
//   ② 受真菌减伤：玩家被 spore 实体伤害减免 10% / 15% / 22% / 30%
//   ③ 狩猎红利：狩猎状态下击杀真菌按档位回 饥饿/耐力/信赖（Boss 全满），写失败不崩只打日志
//   ④ 天敌仇恨：每秒 1 次、10% 概率，让 24 格内目标为空/非玩家的 spore Monster 改仇恨为已结合玩家
// 事件名与规格差异（javap 实证：KubeJS 2001.6.5 的 EntityEvents 仅有 death/hurt/checkSpawn/spawned）：
//   规格写的 EntityEvents.damaged → 实际为 EntityEvents.hurt
//   规格写的 EntityEvents.tick  → 不存在，用 ServerEvents.tick 等价实现（每 tick 清队列 + 每秒扫描）
//   TODO(K3-知悉): 两处事件名差异已按可加载实现，规格侧请同步修订
// 伤害系数落地方式：KubeJS 6.5 的 hurt 事件 damage 只读（LivingEntityHurtEventJS 无 setter，javap 实证），
//   不碰 mixin/字节码、不反射私有字段的方案：
//   增伤 → 下一 tick 对目标补 hurt(原伤×倍率)：原版无敌帧"差值结算"分支只吃 (倍率-1)×原伤，等效乘区
//   减伤 → 下一 tick 原地 heal(原伤×减免)，延迟 1 tick 生效
//   TODO(K3-实测): 该方案对"同 tick 致命伤"不提供保护；若要求即时/致命保护，规格需另给事件前拦截手段

// 反射点（开包 javap 实证 symbiote-1.1.3 真实 API，全部带兜底，失败不崩只打日志）：
//   com.scout.symbiote.tracker.SymbioteTracker.get(ServerLevel) / peek(UUID)
//     / adjustTrust(ServerLevel, ServerPlayer, int, String)
//   com.scout.symbiote.tracker.SymbioteProfile 公开字段 stage/trust/stamina + 方法
//     regenStamina(int) / staminaMax() / addTrust(int)
//   com.scout.symbiote.tracker.BondStage 枚举：UNBONDED/ATTACHED/INTEGRATED/COOPERATIVE/DOMINANT
//   com.scout.symbiote.ability.PredatorHunt.isHunting(UUID) / SymbioteFeedingHunt.isHunting(UUID)
let SymbioteTracker = null
let PredatorHunt = null
let FeedingHunt = null
try {
  SymbioteTracker = Java.loadClass('com.scout.symbiote.tracker.SymbioteTracker')
} catch (e) {
  console.error('[SVS-共生体] SymbioteTracker 加载失败，档位走 persistentData 兜底: ' + e)
}
try { PredatorHunt = Java.loadClass('com.scout.symbiote.ability.PredatorHunt') } catch (e) { }
try { FeedingHunt = Java.loadClass('com.scout.symbiote.ability.SymbioteFeedingHunt') } catch (e) { }
// TODO(K3-实测): symbiote 后续更新若改包名/类名，只需调整上面三条类路径

const MonsterClass = Java.loadClass('net.minecraft.world.entity.monster.Monster')
const SC_ServerPlayer = Java.loadClass('net.minecraft.server.level.ServerPlayer')
const SPORE_NS = 'spore:'

const DMG_MULT = { ATTACHED: 1.1, INTEGRATED: 1.2, COOPERATIVE: 1.35, DOMINANT: 1.5 }
const DMG_REDUCE = { ATTACHED: 0.10, INTEGRATED: 0.15, COOPERATIVE: 0.22, DOMINANT: 0.30 }
// 狩猎红利 [饥饿, 耐力, 信赖]；-1 表示"全满"（饥饿→20，耐力→staminaMax）
const HUNT_BONUS = {
  minor: [3, 8, 3],      // 真菌小怪（血量 <50）
  elite: [6, 20, 8],     // 真菌精英（血量 50~200）
  boss: [-1, -1, 25]     // 真菌 Boss（血量 >200）
}

const warned = {}
function warnOnce(tag, e) {
  if (warned[tag]) return
  warned[tag] = true
  console.warn('[SVS-共生体] ' + tag + ' 写入失败（只提示一次，不影响运行）: ' + e)
}

function uuidOf(ent) {
  return String(ent.getUUID())      // getUUID auto-remap → SRG m_20148_
}

// ── 判定共生体玩家：优先 SymbioteTracker（真实 API），兜底 persistentData ──
function getProfile(player) {
  if (!SymbioteTracker) return null
  try {
    const tracker = SymbioteTracker.get(player.level)   // kjs$getLevel，服务端实例为 ServerLevel
    return tracker ? tracker.peek(player.getUUID()) : null
  } catch (e) {
    return null
  }
}

function getBondStage(player) {
  const prof = getProfile(player)
  if (prof && prof.stage) {
    try { return String(prof.stage.name()) } catch (e) { }   // Enum.name() 非 MC 成员，不受 SRG 影响
  }
  // 兜底：Forge IForgeEntity.getPersistentData（非 SRG）
  // TODO(K3-实测): 手动模拟档位可用 /kubejs persistent_data player <玩家> set svs_bond_stage INTEGRATED
  try {
    const s = player.getPersistentData().getString('svs_bond_stage')
    return s ? String(s) : null
  } catch (e) {
    return null
  }
}

// ── 狩猎状态：PredatorHunt / SymbioteFeedingHunt（开包实证均含 isHunting(UUID)）──
function isHunting(player) {
  let asked = false
  try {
    if (PredatorHunt) { asked = true; if (PredatorHunt.isHunting(player.getUUID())) return true }
    if (FeedingHunt) { asked = true; if (FeedingHunt.isHunting(player.getUUID())) return true }
  } catch (e) { }
  if (!asked) {
    // TODO(K3-实测): 狩猎 API 不可用 → 按规格退化为"已结合即视为狩猎"
    return getBondStage(player) !== null
  }
  return false
}

// ── 狩猎红利三写：写失败不崩、只打日志 ──
function addFood(player, n) {
  try { player.foodLevel = Math.min(20, player.foodLevel + n) }   // kjs$get/setFoodLevel
  catch (e) { warnOnce('饥饿', e) }
}
function fillFood(player) {
  try { player.foodLevel = 20 } catch (e) { warnOnce('饥饿', e) }
}
function addStamina(player, n) {
  const prof = getProfile(player)
  if (!prof) { warnOnce('耐力', new Error('无共生体档案')); return }
  try { prof.regenStamina(n) } catch (e) { warnOnce('耐力', e) }
}
function fillStamina(player) {
  const prof = getProfile(player)
  if (!prof) { warnOnce('耐力', new Error('无共生体档案')); return }
  try { prof.regenStamina(prof.staminaMax()) } catch (e) { warnOnce('耐力', e) }
}
function addTrust(player, n) {
  // 优先 mod 自带 adjustTrust（带来源标记，内部含钳制），失败退 SymbioteProfile.addTrust
  try {
    if (SymbioteTracker) {
      SymbioteTracker.adjustTrust(player.level, player, n, 'svs_symbiote_counter')
      return
    }
  } catch (e) { }
  try {
    const prof = getProfile(player)
    if (prof) { prof.addTrust(n); return }
  } catch (e) {
    warnOnce('信赖', e)
  }
}

// ── ①② 伤害两向（EntityEvents.hurt）──
const pendingHeal = {}      // uuid → { ent, amount } 待回血
const pendingExtra = {}     // uuid → { ent, source, amount } 待补刀
let applyingExtra = false   // 补刀重入闸：补刀自身触发的 hurt 事件不得再排队

EntityEvents.hurt(event => {
  const ent = event.entity
  if (!ent || !ent.type) return
  const srcEnt = event.source ? event.source.entity : null
  const fromSpore = !!(srcEnt && srcEnt.type && String(srcEnt.type).indexOf(SPORE_NS) === 0)

  // 方向 A：玩家被 spore 实体伤害 → 按档位减伤（下一 tick 回血）
  if (ent.player && fromSpore) {
    const stage = getBondStage(ent)
    const red = DMG_REDUCE[stage]
    if (red) {
      const k = uuidOf(ent)
      pendingHeal[k] = { ent: ent, amount: (pendingHeal[k] ? pendingHeal[k].amount : 0) + event.amount * red }
      console.info('[SVS-共生体][debug] 受真菌减伤生效: 档位 ' + stage + ' 减免 ' + Math.round(red * 100) + '%（下一 tick 回复）')
      // TODO(K3-上线前): 验收 4 需要此 debug 行，转正式时删除或降频
    }
    return
  }

  // 方向 B：已结合玩家打 spore Monster → 按档位增伤（下一 tick 补刀，无敌帧差值结算）
  if (applyingExtra) return
  if (ent.monster && String(ent.type).indexOf(SPORE_NS) === 0
    && srcEnt && srcEnt.player && srcEnt instanceof ServerPlayerClass) {
    const stage = getBondStage(srcEnt)
    const mult = DMG_MULT[stage]
    if (mult && !pendingExtra[uuidOf(ent)]) {
      pendingExtra[uuidOf(ent)] = { ent: ent, source: event.source, amount: event.amount * mult }
      console.info('[SVS-共生体][debug] 伤害克制生效: 档位 ' + stage + ' ×' + mult)
      // TODO(K3-上线前): 同上，转正式时删除或降频
    }
  }
})

// ── ③ 狩猎红利（EntityEvents.death）──
EntityEvents.death(event => {
  const ent = event.entity
  if (!ent || !ent.monster || String(ent.type).indexOf(SPORE_NS) !== 0) return
  const killer = event.source ? event.source.entity : null
  if (!killer || !killer.player || !(killer instanceof SC_ServerPlayer)) return
  const stage = getBondStage(killer)
  if (!stage || stage === 'UNBONDED') return
  if (!isHunting(killer)) return
  const maxHp = ent.maxHealth
  const tierName = maxHp < 50 ? 'minor' : (maxHp <= 200 ? 'elite' : 'boss')
  const bonus = HUNT_BONUS[tierName]
  if (bonus[0] < 0) fillFood(killer); else addFood(killer, bonus[0])
  if (bonus[1] < 0) fillStamina(killer); else addStamina(killer, bonus[1])
  addTrust(killer, bonus[2])
  console.info('[SVS-共生体][debug] 狩猎红利: 档位 ' + tierName + '，饥饿+' + bonus[0] + ' 耐力+' + bonus[1] + ' 信赖+' + bonus[2])
  // TODO(K3-决策): symbiote 档案自身另有 hunger 字段（SymbioteTracker.adjustHunger），规格只要求
  // player.foodLevel；是否同步喂 symbiote 内部饥饿值，待 K3 定夺后在此补一行
})

// ── 队列消费（每 tick）+ ④ 天敌仇恨（每秒）──
let tickCounter = 0

ServerEvents.tick(event => {
  tickCounter++

  // 增伤补刀：无敌帧差值分支只结算 amount - lastHurt = (倍率-1)×原伤
  for (const k in pendingExtra) {
    const rec = pendingExtra[k]
    delete pendingExtra[k]
    try {
      if (rec.ent && rec.ent.isAlive()) {
        applyingExtra = true
        rec.ent.hurt(rec.source, rec.amount)
        applyingExtra = false
      }
    } catch (e) {
      applyingExtra = false
      warnOnce('补刀', e)
    }
  }
  // 减伤回血
  for (const k in pendingHeal) {
    const rec = pendingHeal[k]
    delete pendingHeal[k]
    try {
      if (rec.ent && rec.ent.isAlive()) rec.ent.heal(rec.amount)
    } catch (e) {
      warnOnce('回血', e)
    }
  }

  if (tickCounter % 20 !== 0) return          // 每秒 1 次
  if (!event.server) return
  const players = event.server.getPlayers()
  let aggroTarget = null
  for (let i = 0; i < players.size(); i++) {
    aggroTarget = players.get(i)
    const stage = getBondStage(aggroTarget)
    if (!stage || stage === 'UNBONDED') continue
    let monsters
    try {
      // 24 格扫描：以玩家包围盒 inflate 24 取 spore Monster（与"怪物 24 格内找玩家"等价，范围对称）
      monsters = aggroTarget.level.getEntitiesOfClass(MonsterClass, aggroTarget.getBoundingBox().inflate(24))
    } catch (e) {
      continue
    }
    for (let j = 0; j < monsters.size(); j++) {
      const mob = monsters.get(j)
      if (!mob || String(mob.type).indexOf(SPORE_NS) !== 0) continue
      const target = mob.getTarget()
      if (target && target.player) continue   // 已锁定玩家 → 不抢
      if (Math.random() < 0.10) {
        mob.setTarget(aggroTarget)                      // 天敌仇恨（setTarget auto-remap → SRG m_20202_）
      }
    }
  }
})
