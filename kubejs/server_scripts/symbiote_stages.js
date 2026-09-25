// symbiote_stages.js — 共生体分期 1：进化阶段数值加成（魔改二期 · 决议一-10）
// 按 BondStage（ATTACHED/INTEGRATED/COOPERATIVE/DOMINANT）给玩家挂三系加成：
//   穿甲 = epicfight:armor_negation（百分比，EF 原生属性）
//   韧性 = minecraft:generic.armor_toughness（护甲韧性）
//   回复 = 每 5 秒回血（0.5/1/1.5/2 HP）
// 同时把 BondStage 镜像成 GameStage（svs_bond_<stage>），供任务/门控读取。
// 依赖：symbiote_counter.js 的全局 getBondStage（同包 Rhino 共享作用域，字母序它先加载）。
// 数值为初版默认，TODO(K3-调参) 实测后微调。
// Rhino 守则：循环体外声明；枚举常量经 valueOf 静态方法取（字符串不受 SRG 影响），
//   不直读 AttributeModifier.Operation.ADDITION 静态字段。

const SS_OP_ADD = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation').valueOf('ADDITION')
const SS_AttributeModifier = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier')
const SS_UUID = Java.loadClass('java.util.UUID')
const SS_ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
const SS_ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
const SS_GameStageHelper = Java.loadClass('net.darkhax.gamestages.GameStageHelper')

// 固定 UUID（移除旧加成用；勿改）
const SS_UUID_NEG = SS_UUID.fromString('7f2a1c3e-5b4d-4e6f-8a0b-1c2d3e4f5a01')
const SS_UUID_TOUGH = SS_UUID.fromString('7f2a1c3e-5b4d-4e6f-8a0b-1c2d3e4f5a02')

const SS_BONUS = {
  ATTACHED:    { neg: 2,  tough: 1, regen: 0.5 },
  INTEGRATED:  { neg: 4,  tough: 2, regen: 1.0 },
  COOPERATIVE: { neg: 7,  tough: 4, regen: 1.5 },
  DOMINANT:    { neg: 10, tough: 6, regen: 2.0 }
}
const SS_STAGES = ['svs_bond_attached', 'svs_bond_integrated', 'svs_bond_cooperative', 'svs_bond_dominant']

function ssApplyAttr(player, attrId, uuid, name, value) {
  try {
    const attr = SS_ForgeRegistries.ATTRIBUTES.getValue(new SS_ResourceLocation(attrId))
    if (!attr) { console.warn('[SVS-共生加成] 属性不存在: ' + attrId); return }
    const inst = player.getAttribute(attr)
    if (!inst) return
    const cur = inst.getModifier(uuid)
    if (cur && Math.abs(cur.getAmount() - value) < 0.0001) return   // 已是目标值，不动
    if (cur) inst.removeModifier(uuid)
    if (value > 0) inst.addTransientModifier(new SS_AttributeModifier(uuid, name, value, SS_OP_ADD))
  } catch (e) {
    console.warn('[SVS-共生加成] 属性写入失败(' + attrId + '): ' + e)
  }
}

function ssApplyStage(player, stage) {
  // stage 为 null/UNBONDED 时清零
  const b = stage ? SS_BONUS[stage] : null
  ssApplyAttr(player, 'epicfight:armor_negation', SS_UUID_NEG, 'svs_symbiote_negation', b ? b.neg : 0)
  ssApplyAttr(player, 'minecraft:generic.armor_toughness', SS_UUID_TOUGH, 'svs_symbiote_tough', b ? b.tough : 0)

  // GameStage 镜像
  let lower = null, gs = null, want = false, has = false
  try {
    lower = stage ? stage.toLowerCase() : null
    for (let i = 0; i < SS_STAGES.length; i++) {
      gs = SS_STAGES[i]
      want = ('svs_bond_' + lower) === gs
      has = SS_GameStageHelper.hasStage(player, gs)
      if (want && !has) SS_GameStageHelper.addStage(player, gs)
      else if (!want && has) SS_GameStageHelper.removeStage(player, gs)
    }
  } catch (e) { /* GameStages 缺失时静默 */ }
}

let ssTick = 0
let ssPlayer = null, ssStage = null, ssBonus = null
ServerEvents.tick(event => {
  ssTick++
  if (ssTick % 20 !== 0) return
  if (!event.server) return
  const players = event.server.getPlayers()
  for (let i = 0; i < players.size(); i++) {
    ssPlayer = players.get(i)
    ssStage = null
    try { ssStage = getBondStage(ssPlayer) } catch (e) { continue }
    if (ssStage === 'UNBONDED') ssStage = null

    // 变化才动（pd 缓存档位，避免每秒重复改属性）
    let last = ''
    try { last = String(ssPlayer.getPersistentData().getString('svs_bond_applied')) } catch (e) { }
    const cur = ssStage || ''
    if (last !== cur) {
      ssApplyStage(ssPlayer, ssStage)
      try { ssPlayer.getPersistentData().putString('svs_bond_applied', cur) } catch (e) { }
      console.info('[SVS-共生加成] ' + ssPlayer.username + ' 档位 ' + (last || '无') + ' → ' + (cur || '无'))
    }

    // 回复：每 5 秒（挂在每秒循环里数 5 格）
    if (ssStage && ssTick % 100 === 0) {
      ssBonus = SS_BONUS[ssStage]
      try {
        if (ssPlayer.health < ssPlayer.maxHealth) ssPlayer.heal(ssBonus.regen)
      } catch (e) { }
    }
  }
})

// 保险：重生后属性修饰符清空（死亡清空 transient 修饰符），pd 缓存重置让下秒重挂
PlayerEvents.respawned(event => {
  try { event.player.getPersistentData().putString('svs_bond_applied', '') } catch (e) { }
})
