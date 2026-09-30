// symbiote_counter.js — 共生体克制真菌 · 分期 1（魔改第一期 · 规格 3）
// 能力清单（只对 spore 命名空间实体生效）：
//   ① 伤害克制 / ② 受真菌减伤 —— 【已迁至 startup_scripts/svs_damage.js】
//      （LivingHurtEvent.setAmount 直改，取代下一 tick 补刀/回补；数值表在那边，改动请同步）
//   ③ 狩猎红利：狩猎状态下击杀真菌按档位回 饥饿/耐力/信赖（Boss 全满），写失败不崩只打日志
//   ④ 天敌仇恨：每秒 1 次、10% 概率，让 24 格内目标为空/非玩家的 spore Monster 改仇恨为已结合玩家
//   ⑤ 围城压力联动（决议五-3）：围城窗口内（siege.js 写 persistentData svs_siege_active_until）
//      已结合玩家压力每秒 +2（净 +1/s，约 70 秒到 70 高压线）

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

// ── 判定共生体玩家：优先 SymbioteTracker（真实 API），兜底 persistentData ──
function getProfile(player) {
  if (!SymbioteTracker) return null
  let gpTracker = null      // Rhino 守则：try 等块内不声明（第二次执行抛 redeclaration）
  try {
    gpTracker = SymbioteTracker.get(player.level)   // kjs$getLevel，服务端实例为 ServerLevel
    // player.uuid（KubeJS 注入属性）9-30 探针实证可用；getUUID() 连 ServerPlayer 都失败
    return gpTracker ? gpTracker.peek(player.uuid) : null
  } catch (e) {
    return null
  }
}

function getBondStage(player) {
  let pdStage = ''          // Rhino 守则：try 内不声明
  const prof = getProfile(player)
  if (prof && prof.stage) {
    try { return String(prof.stage.name()) } catch (e) { }   // Enum.name() 非 MC 成员，不受 SRG 影响
  }
  // 兜底：Forge IForgeEntity.getPersistentData（非 SRG）
  // TODO(K3-实测): 手动模拟档位可用 /kubejs persistent_data player <玩家> set svs_bond_stage INTEGRATED
  try {
    pdStage = player.getPersistentData().getString('svs_bond_stage')
    return pdStage ? String(pdStage) : null
  } catch (e) {
    return null
  }
}

// ── 狩猎状态：PredatorHunt / SymbioteFeedingHunt（开包实证均含 isHunting(UUID)）──
function isHunting(player) {
  let asked = false
  try {
    // player.uuid 探针实证可用（getUUID() 不可用，见 getProfile 注释）
    if (PredatorHunt) { asked = true; if (PredatorHunt.isHunting(player.uuid)) return true }
    if (FeedingHunt) { asked = true; if (FeedingHunt.isHunting(player.uuid)) return true }
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
  let atProf = null         // Rhino 守则：try 内不声明
  try {
    if (SymbioteTracker) {
      SymbioteTracker.adjustTrust(player.level, player, n, 'svs_symbiote_counter')
      return
    }
  } catch (e) { }
  try {
    atProf = getProfile(player)
    if (atProf) { atProf.addTrust(n); return }
  } catch (e) {
    warnOnce('信赖', e)
  }
}

// ── ③ 狩猎红利（EntityEvents.death）──
// 击杀归因（9-30 探针实证）：DamageSource.entity / getEntity() 不可解析 →
// 走 LivingEntity.getLastHurtByPlayer()（与 spore_coin.js 掉币同一修法）
EntityEvents.death(event => {
  const ent = event.entity
  if (!ent || !ent.monster || String(ent.type).indexOf(SPORE_NS) !== 0) return
  let killer = null
  try { killer = ent.getLastHurtByPlayer() } catch (e) { killer = null }
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

// ── 队列消费（每 tick）+ ④ 天敌仇恨（每秒）+ ⑤ 围城压力（每秒）──
let tickCounter = 0
const SC_SIEGE_STRESS = 2     // 围城窗口内每秒压力增量（决议五-3）。自然衰减 1/s → 净 +1/s，约 70 秒压到 70 高压线
                               // （评审实证：+3/s 时净 +2/s，35 秒必爆表，围城一开共生体必失控）

ServerEvents.tick(event => {
  tickCounter++

  if (tickCounter % 20 !== 0) return          // 每秒 1 次
  if (!event.server) return
  // gameTime 探针实证：Level.gameTime 字段=undefined → 改 getDayTime()（与 siege.js 同修法）
  let gameTime = -1
  try { gameTime = event.server.overworld().getDayTime() } catch (e) { }
  const players = event.server.getPlayers()
  let aggroTarget = null
  let stage = null
  let monsters = null
  let mob = null, mobTarget = null      // Rhino 守则：for 体内不声明
  for (let i = 0; i < players.size(); i++) {
    aggroTarget = players.get(i)
    stage = getBondStage(aggroTarget)
    if (!stage || stage === 'UNBONDED') continue
    // ⑤ 围城压力联动：围城窗口内压力加速上涨
    if (gameTime >= 0 && SymbioteTracker) {
      try {
        if (aggroTarget.getPersistentData().getInt('svs_siege_active_until') > gameTime) {
          SymbioteTracker.adjustStress(aggroTarget.level, aggroTarget, SC_SIEGE_STRESS, 'svs_siege')
        }
      } catch (e) { warnOnce('围城压力', e) }
    }
    try {
      // 24 格扫描：以玩家包围盒 inflate 24 取 spore Monster（与"怪物 24 格内找玩家"等价，范围对称）
      monsters = aggroTarget.level.getEntitiesOfClass(MonsterClass, aggroTarget.getBoundingBox().inflate(24))
    } catch (e) {
      continue
    }
    for (let j = 0; j < monsters.size(); j++) {
      mob = monsters.get(j)
      if (!mob || String(mob.type).indexOf(SPORE_NS) !== 0) continue
      mobTarget = mob.getTarget()
      if (mobTarget && mobTarget.player) continue   // 已锁定玩家 → 不抢
      if (Math.random() < 0.10) {
        mob.setTarget(aggroTarget)                      // 天敌仇恨（setTarget auto-remap → SRG m_20202_）
      }
    }
  }
})
