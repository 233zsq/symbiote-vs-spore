// spore_coin.js — 真菌币经济（魔改第一期 · 规格 1）
// 交付三件事：
//   ① 物品 kubejs:spore_coin（真菌币），基础贴图用原版绿宝石兜底（TODO: 后续换自定义贴图）
//   ② 击杀 spore 命名空间敌对生物掉真菌币，按血量分档（<50: 1~2 / 50~200: 3~5 / >200: 15~25），
//      只认玩家击杀，且对掉落物 setOwner 只归击杀者本人拾取
//   ③ 村民交易：农民加 12 币→8 匠魂 grout，工具匠加 20 币→1 火种绑定工具（kubejs:fireseed_token）
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

// ── 村民交易 ─────────────────────────────────────────────────────────────────
// 方案：Forge 原生 VillagerTradesEvent（每个村民生成交易时触发），向 1 级交易列表追加。
// 职业判别：ForgeRegistries.VILLAGER_PROFESSIONS.getKey(职业) 按 id 比对。
// 全部成员访问写 mojmap 名，交给 KubeJS Rhino 自动 remap（见文件头注释）。
;(function registerVillagerTrades() {
  let ItemListing, MerchantOffer, ForgeRegistries, JInteger
  try {
    ItemListing = Java.loadClass('net.minecraft.world.entity.npc.VillagerTrades$ItemListing')
    MerchantOffer = Java.loadClass('net.minecraft.world.item.trading.MerchantOffer')
    ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
    JInteger = Java.loadClass('java.lang.Integer')
  } catch (e) {
    console.error('[SVS-真菌币] 原版交易类加载失败，村民交易跳过: ' + e)
    return
  }

  // ItemListing 是 SAM 接口（getOffer(Entity, RandomSource)）。
  // 用"函数→SAM"适配避免在代码里写死 SRG 方法名；new 不可用则退 JavaAdapter，都失败只报错不崩。
  // 注意：factory 每次调用 new MerchantOffer——同一个 offer 实例不能复用给多个村民。
  function makeListing(factory) {
    try {
      return new ItemListing(function (trader, random) { return factory() })
    } catch (e1) {
      try {
        return new JavaAdapter(ItemListing, function (trader, random) { return factory() })
      } catch (e2) {
        console.error('[SVS-真菌币] ItemListing 适配失败，村民交易跳过: ' + e2)
        return null
      }
    }
  }

  // TODO(K3-调参): maxUses=9999、villagerXp=2、priceMult=0.05 为初版数值
  // 第二价用空气堆（isEmpty）等效单件收购，避开 ItemStack.EMPTY 的字段名。
  const farmerListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 12), Item.of('minecraft:air'), Item.of('tconstruct:grout', 8), 9999, 2, 0.05)
  })
  const toolsmithListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 20), Item.of('minecraft:air'), Item.of('kubejs:fireseed_token', 1), 9999, 2, 0.05)
  })
  if (!farmerListing || !toolsmithListing) return

  ForgeEvents.onEvent('net.minecraftforge.event.village.VillagerTradesEvent', event => {
    try {
      const key = String(ForgeRegistries.VILLAGER_PROFESSIONS.getKey(event.type))
      let listing = null
      if (key === 'minecraft:farmer') listing = farmerListing
      else if (key === 'minecraft:toolsmith') listing = toolsmithListing
      if (!listing) return
      // getTrades() 是 Int2ObjectMap<List<ItemListing>>；用 Integer 装箱明确走 get(Object)，
      // 避免 Rhino 在 get(int)/get(Object) 重载间选错
      const list = event.trades.get(JInteger.valueOf(1))
      if (!list) {
        console.warn('[SVS-真菌币] ' + key + ' 无 1 级交易列表，本村民跳过')
        return
      }
      list.add(listing)
    } catch (e) {
      console.error('[SVS-真菌币] 村民交易追加失败: ' + e)
    }
  })
  console.info('[SVS-真菌币] 村民交易监听已挂：农民 12币→8grout，工具匠 20币→1火种绑定工具')
})()
