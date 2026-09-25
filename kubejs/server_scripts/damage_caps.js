// damage_caps.js — 单次受伤上限 + 真菌母巢限伤爬升模板（魔改二期 · 决议一-4）
// 两层限伤（取更严者生效）：
//   ① 灾变 Boss：走 cataclysm.toml 原生 DamageCap（已对 DOTE 调参：22/22/20/22×5），本脚本不碰
//      （重要：cataclysm 命名空间整体跳过——原生前置 cap 与本脚本后置回补叠加会变成"打 Boss 回血"）
//   ② 其余精英/Boss（HP≥200，见数值表等级带 B2+）：单次受伤 ≤ 10% 最大生命
// 机制约束：KubeJS 2001.6.5 hurt 事件 damage 只读（javap 实证）→ 与 symbiote_counter 同款
//   "下一 tick 回补溢出差额"方案；同 tick 致命伤不保护（继承该 TODO）。
// 母巢模板（决议一-4，远梦 Arterius 参数）：单次 ≤ 8% 最大生命 + 累计受伤爬升减伤（封顶 90%）
//   + 停手 5 秒后累计值每秒衰减 20% 最大生命。适用名单为 spore 天灾级（Calamity 档）主实体；
//   分段实体（_seg）只走通用 10%，TODO(K3-实测) 是否并入本体累计。

const DC_ELITE_MIN_HP = 200            // 精英/Boss 门槛（等级带 B2）
const DC_ELITE_CAP = 0.10              // 通用单次受伤上限（最大生命比例）
const DC_SKIP_NS = 'cataclysm:'        // 有原生 cap 的命名空间，跳过防双重结算

// 母巢模板名单（评审实证修正）：spore 的真"母巢"线是 mound → proto（Proto Hivemind）。
// proto 仅 100 血 < 精英门槛 200，正是需要专属模板的对象；mound(20 血) 太小不套。
// 原名单 6 只天灾级回归通用 10% cap（HP≥200 自动生效）。TODO(K3-实测): proto 进化后形态是否需并入
const DC_HIVEMIND = ['spore:proto']
const DC_HIVE_CAP = 0.08               // 母巢单次受伤上限 8%
const DC_HIVE_RATE_MAX = 0.90          // 爬升减伤封顶 90%
const DC_HIVE_DECAY_DELAY = 100        // 停手 5 秒（tick）后开始衰减
const DC_HIVE_DECAY_PER_SEC = 0.20     // 累计值每秒衰减 20% 最大生命

// 减伤率 = min(90%, 累计受伤 / 最大生命)（每累计一管血 → +100% 减伤直至封顶）
function dcHiveRate(cum, maxHp) {
  const r = cum / maxHp
  return r > DC_HIVE_RATE_MAX ? DC_HIVE_RATE_MAX : r
}

// 溢出差额回补队列（下一 tick 执行）
// 队列用数组不用 uuid 键表：getUUID 在非玩家实体上 Rhino 解析失败（实测 Cannot find function）
const dcPendingHeal = []   // [{ ent, amount }]
let dcApplying = false

EntityEvents.hurt(event => {
  const ent = event.entity
  if (!ent || !ent.type || ent.player) return
  const type = String(ent.type)
  if (type.indexOf(DC_SKIP_NS) === 0) return
  const maxHp = ent.maxHealth
  if (!maxHp || maxHp < DC_ELITE_MIN_HP) return

  let cap = DC_ELITE_CAP
  let rate = 0
  if (DC_HIVEMIND.indexOf(type) >= 0) {
    cap = DC_HIVE_CAP
    // 母巢模板：先衰减后读率，再累计本次有效伤害
    const pd = ent.getPersistentData()
    let cum = pd.getDouble('svs_dc_cum')
    const last = pd.getLong('svs_dc_last')
    const now = ent.level.gameTime
    if (last > 0 && now - last > DC_HIVE_DECAY_DELAY) {
      cum = Math.max(0, cum - (now - last - DC_HIVE_DECAY_DELAY) / 20 * DC_HIVE_DECAY_PER_SEC * maxHp)
    }
    rate = dcHiveRate(cum, maxHp)
    const effective = Math.min(event.amount, cap * maxHp) * (1 - rate)
    pd.putDouble('svs_dc_cum', cum + effective)
    pd.putLong('svs_dc_last', now)
  }

  const allowed = Math.min(event.amount, cap * maxHp) * (1 - rate)
  const excess = event.amount - allowed
  if (excess <= 0.001) return
  if (dcApplying) return                        // 回补自身触发的 hurt 不再排队（防御）
  let merged = false
  for (let i = 0; i < dcPendingHeal.length; i++) {
    if (dcPendingHeal[i].ent === ent) { dcPendingHeal[i].amount += excess; merged = true; break }
  }
  if (!merged) dcPendingHeal.push({ ent: ent, amount: excess })
  console.info('[SVS-限伤][debug] ' + type + ' 单次受伤 ' + event.amount + ' → 封顶 ' + allowed.toFixed(1) + '（回补 ' + excess.toFixed(1) + '）')
  // TODO(K3-上线前): debug 行转正式时删除或降频
})

ServerEvents.tick(event => {
  while (dcPendingHeal.length > 0) {
    const rec = dcPendingHeal.shift()
    try {
      if (rec.ent && rec.ent.isAlive()) {
        dcApplying = true
        rec.ent.heal(rec.amount)
        dcApplying = false
      }
    } catch (e) {
      dcApplying = false
      console.warn('[SVS-限伤] 回补失败: ' + e)
    }
  }
})
