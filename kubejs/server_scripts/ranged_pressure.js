// ranged_pressure.js — 飞天/水下怪物远程加压（魔改二期 · 决议一-4 末条）
// 规则：怪物发射的弹射物（箭/火球/三叉戟等）在"飞行中或水中"命中时伤害 ×1.5。
//   - 只认弹射物（isProjectile），近战/魔法直击不管；攻击者是玩家则跳过
//   - 飞行判定：离地且不在水里（blaze/ghast/vex 等悬停怪全程满足；跳跃近战怪不发射击物不影响）
//   - 水下判定：isInWater（溺尸三叉戟等）
// 机制：hurt 事件 damage 只读（javap 实证）→ 溢出部分下一 tick 补刀（同 symbiote_counter 实证方案）
// TODO(K3-调参): 1.5 为初版默认；守卫激光（魔法直击非弹射物）未覆盖，实测后按需扩展

const RP_MULT = 1.5
const RP_EXTRA = {}        // uuid → { ent, source, amount }
let rpApplying = false

EntityEvents.hurt(event => {
  const ent = event.entity
  if (!ent) return
  if (rpApplying) return
  const src = event.source
  if (!src) return
  let isProj = false
  try { isProj = !!src.isProjectile() } catch (e) { return }
  if (!isProj) return
  const shooter = src.entity
  if (!shooter || shooter.player) return          // 玩家射的不管
  let pressurized = false
  try {
    pressurized = shooter.isInWater() || !shooter.onGround()
  } catch (e) { return }
  if (!pressurized) return

  const extra = event.amount * (RP_MULT - 1)
  const k = String(ent.getUUID())
  RP_EXTRA[k] = { ent: ent, source: src, amount: (RP_EXTRA[k] ? RP_EXTRA[k].amount : 0) + extra }
})

ServerEvents.tick(event => {
  for (const k in RP_EXTRA) {
    const rec = RP_EXTRA[k]
    delete RP_EXTRA[k]
    try {
      if (rec.ent && rec.ent.isAlive()) {
        rpApplying = true
        rec.ent.hurt(rec.source, rec.amount)
        rpApplying = false
      }
    } catch (e) {
      rpApplying = false
      console.warn('[SVS-远程加压] 补刀失败: ' + e)
    }
  }
})
