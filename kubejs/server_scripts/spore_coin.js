// spore_coin.js — 真菌币经济（魔改第一期 · 规格 1）
// 交付三件事：
//   ① 物品 kubejs:spore_coin（真菌币），基础贴图用原版绿宝石兜底（TODO: 后续换自定义贴图）
//   ② 击杀 spore 命名空间敌对生物掉真菌币，按血量分档（<50: 1~2 / 50~200: 3~5 / >200: 15~25），
//      只认玩家击杀，且对掉落物 setOwner 只归击杀者本人拾取
//   ③ 村民交易：农民加 12 币→8 匠魂 grout，工具匠加 20 币→1 火种绑定工具（kubejs:fireseed_token）
// 环境（开包实证）：KubeJS 2001.6.5(Rhino) + Forge 47.4.23（1.20.1，运行时 SRG 名）；
//   TConstruct 3.12（tconstruct:grout ✓）、spore 2.2.0j、spore_inquisition 3.1、symbiote 1.1.3。
//   包内无 MoreJS、KubeJS 无原生村民交易事件 → 交易走反射改原版 VillagerTrades.TRADES
//   （SRG 字段名 f_35627_，javap 实证），职业与 SAM 均按签名/函数适配定位，不猜 SRG 名。

 ─────────────────────────────────────────────────────────────────────────────

const ServerPlayerClass = Java.loadClass('net.minecraft.server.level.ServerPlayer')

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
  if (!ent.monster) return                                  // 只掉敌对生物（kjs$isMonster）
  const killer = event.source ? event.source.entity : null
  if (!killer || !killer.player || !(killer instanceof ServerPlayerClass)) return   // 只认玩家击杀
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
// 反射方案：取 VillagerTrades.TRADES（SRG f_35627_）。外层 Map 不可变、内层 Int2ObjectMap
// 可变（原版数据包 trades.json 重载即走此路径），故只对目标职业 put 追加，不动其他行。
// 职业定位不硬编码 SRG：VillagerProfession 是 record，其 String 组件（name）的访问器在运行时
// 可能被 SRG 重命名，按"无参、非静态、返回 String"的签名反射扫描取职业 id。
;(function registerVillagerTrades() {
  let VillagerTrades, ItemListing, MerchantOffer
  try {
    VillagerTrades = Java.loadClass('net.minecraft.world.entity.npc.VillagerTrades')
    ItemListing = Java.loadClass('net.minecraft.world.entity.npc.VillagerTrades$ItemListing')
    MerchantOffer = Java.loadClass('net.minecraft.world.item.trading.MerchantOffer')
  } catch (e) {
    console.error('[SVS-真菌币] 原版交易类加载失败，村民交易跳过: ' + e)
    return
  }

  let trades
  try {
    const f = VillagerTrades.class.getDeclaredField('f_35627_')   // VillagerTrades.TRADES（javap 实证）
    f.setAccessible(true)
    trades = f.get(null)
  } catch (e) {
    console.error('[SVS-真菌币] TRADES(f_35627_) 反射失败，村民交易跳过: ' + e)
    return
  }

  function professionId(p) {
    try {
      const ms = p.getClass().getDeclaredMethods()
      for (let i = 0; i < ms.length; i++) {
        const m = ms[i]
        if (m.getParameterCount() !== 0 || m.isSynthetic()) continue
        if (String(m.getReturnType().getName()) !== 'java.lang.String') continue
        if (java.lang.reflect.Modifier.isStatic(m.getModifiers())) continue
        if (String(m.getName()) === 'toString') continue
        m.setAccessible(true)
        return String(m.invoke(p))
      }
    } catch (e) { }
    return null
  }

  let farmer = null, toolsmith = null
  const it = trades.keySet().iterator()
  while (it.hasNext()) {
    const p = it.next()
    const id = professionId(p)
    if (id === 'farmer') farmer = p
    else if (id === 'toolsmith') toolsmith = p
  }
  if (!farmer || !toolsmith) {
    console.error('[SVS-真菌币] 未定位到农民/工具匠职业，村民交易跳过')
    return
  }

  // ItemListing 是 SAM 接口（运行时方法名 m_213663_ = 源码 getOffer(Entity, RandomSource)）。
  // 用"函数→SAM"适配避免在代码里写死 SRG 方法名；new 不可用则退 JavaAdapter，都失败只报错不崩。
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

  function addTrade(profession, level, listing) {
    if (!listing) return
    try {
      const intMap = trades.get(profession)
      if (!intMap) {
        console.error('[SVS-真菌币] 职业无交易表，跳过: ' + profession)
        return
      }
      const old = intMap.get(level)
      const arr = []
      if (old) {
        for (let i = 0; i < old.length; i++) arr.push(old[i])
      }
      arr.push(listing)
      const out = java.lang.reflect.Array.newInstance(ItemListing, arr.length)
      for (let i = 0; i < arr.length; i++) out[i] = arr[i]
      intMap.put(level, out)
    } catch (e) {
      console.error('[SVS-真菌币] 追加交易失败: ' + e)
    }
  }

  // TODO(K3-审改): 规格写"农民/工具匠各加 1 条"，按"农民一条 grout、工具匠一条火种工具"理解；
  // 若要求两条都挂两个职业，把下面两行各自再 addTrade 一次即可。
  // TODO(K3-调参): maxUses=9999、villagerXp=2、priceMult=0.05 为初版数值
  // 第二价用空气堆（isEmpty）等效单件收购，避开 ItemStack.EMPTY 的 SRG 字段名。
  addTrade(farmer, 1, makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 12), Item.of('minecraft:air'), Item.of('tconstruct:grout', 8), 9999, 2, 0.05)
  }))
  addTrade(toolsmith, 1, makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 20), Item.of('minecraft:air'), Item.of('kubejs:fireseed_token', 1), 9999, 2, 0.05)
  }))
  console.info('[SVS-真菌币] 村民交易已追加：农民 12币→8grout，工具匠 20币→1火种绑定工具')
})()
