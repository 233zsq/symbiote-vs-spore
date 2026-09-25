// spore_coin.js — 真菌币经济（魔改第一期 · 规格 1）
// 交付三件事：
//   ① 物品 kubejs:spore_coin（真菌币），基础贴图用原版绿宝石兜底（TODO: 后续换自定义贴图）
//   ② 击杀 spore 命名空间敌对生物掉真菌币，按血量分档（<50: 1~2 / 50~200: 3~5 / >200: 15~25），
//      只认玩家击杀，且对掉落物 setOwner 只归击杀者本人拾取
//   ③ 村民交易：农民加 12 币→8 匠魂 grout，工具匠加 20 币→1 火种绑定工具（kubejs:fireseed_token），
//      制图师加 15 币→共生体陨石线索成书（理念 1"交易获得结构线索"，交易时实时寻址）
//      【已迁至 startup_scripts/villager_trades.js——ForgeEvents 只在 startup 脚本注入
//        （BuiltinKubeJSForgePlugin 字节码实证），server 脚本里是 not defined】
// 环境（开包实证）：KubeJS 2001.6.5(Rhino) + Forge 47.4.23（1.20.1，运行时 SRG 名）；
//   TConstruct 3.12（tconstruct:grout ✓）、spore 2.2.0j、spore_inquisition 3.1、symbiote 1.1.3。
//   包内无 MoreJS，但 Forge 有原生 VillagerTradesEvent（KubeJS ForgeEvents.onEvent 可监听），
//   每村民生成交易时向 1 级列表追加即可，完全不碰原版 TRADES 内部表。
//   成员名一律写 mojmap——KubeJS Rhino 生产环境自动 remap 到 SRG；直写 SRG 名（f_35627_）
//   反而查不到成员（2026-09-24 22:39 实踩 no public instance field），java.lang.Class/reflect
//   反射则被类过滤器拦截，两条路都不要走。


const SP_ServerPlayer = Java.loadClass('net.minecraft.server.level.ServerPlayer')
const SP_Monster = Java.loadClass('net.minecraft.world.entity.monster.Monster')

// 血量分档：[最小, 最大]；普通 <50 / 精英 50~200（含）/ Boss >200
function coinTier(maxHp) {
  if (maxHp < 50) return [1, 2]
  if (maxHp <= 200) return [3, 5]
  return [15, 25]
}

// 掉落：KubeJS 2001.6.5 的 LivingEntityDrops 事件脚本名为 EntityEvents.drops
// （javap 实证 dev.latvian.mods.kubejs.entity.forge.LivingEntityDropsEventJS：
//   entity / source / lootingLevel / recentlyHit，addDrop(ItemStack) → ItemEntity）
// TODO(K3-实测): spore 命名空间若有非 Monster 的敌对单位会被 isMonster 过滤漏掉，实测后按需放宽
EntityEvents.drops(event => {
  const ent = event.entity
  if (!ent || !ent.type || String(ent.type).indexOf('spore:') !== 0) return
  if (!(ent instanceof SP_Monster)) return                  // 只掉敌对生物（instanceof Monster，属性存在性实踩过）
  const killer = event.source ? event.source.entity : null
  if (!killer || !killer.player || !(killer instanceof SP_ServerPlayer)) return   // 只认玩家击杀
  const tier = coinTier(ent.maxHealth)
  const n = tier[0] + Math.floor(Math.random() * (tier[1] - tier[0] + 1))
  const drop = event.addDrop(Item.of('kubejs:spore_coin', n))
  try {
    // 只给击杀者本人：ItemEntity.setOwner（auto-remap → SRG m_32058_）设置拾取归属
    drop.setOwner(killer.getUUID())
  } catch (e) {
    console.warn('[SVS-真菌币] setOwner 不可用，本枚掉落未限归属: ' + e)
  }
})
