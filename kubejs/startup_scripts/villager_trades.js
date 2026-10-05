// villager_trades.js — 村民交易注册（魔改第一期 · 规格 1③）
//   农民加 12 币→8 匠魂 grout，工具匠加 20 币→1 火种绑定工具（kubejs:fireseed_token），
//   制图师加 15 币→1 探险家指南针（2026-10-01 裁决：线索书链路放弃——Rhino NPE/空标签/
//   空白页三连，改直接给指南针，探索自由度更高）。
//
// ⚠️ 两条实踩（2026-09-25，crash-2026-09-25_22.17.08-server.txt）：
//   ① 别碰 VillagerTradesEvent 的 trades：它是 fastutil Int2ObjectMap，KubeJS Rhino 会把它
//      包成 NativeJavaMap，**任何属性访问都会走 map.containsKey(String)** →
//      ClassCastException（NativeJavaMap.java:55 → Int2ObjectFunction.containsKey）。
//      该异常产生于 Rhino 内部而非反射调用，**JS try/catch 兜不住**，Forge 总线记录后重抛 → 崩服。
//   ② 故改走 architectury 的 TradeRegistry（本包已装 architectury-9.2.14-forge）：
//      纯静态方法登记，由 architectury 自己在 VillagerTradesEvent 里合并进各职业表，JS 侧零 Map 访问。
//      登记必须在世界加载（ServerAboutToStart → VillagerTradingManager.loadTrades）之前完成，
//      所以本文件留在 startup_scripts（server 脚本加载太晚）。
// TODO(K3-调参): maxUses=16（评审修正：9999 无限兑会削掉"匠魂保底线靠打 Boss 补材料"的定位）、
//   villagerXp=2、priceMult=0.05

;(function registerVillagerTrades() {
  let ItemListing, MerchantOffer, ForgeRegistries, TradeRegistry, ResourceLocation
  try {
    ItemListing = Java.loadClass('net.minecraft.world.entity.npc.VillagerTrades$ItemListing')
    MerchantOffer = Java.loadClass('net.minecraft.world.item.trading.MerchantOffer')
    ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
    TradeRegistry = Java.loadClass('dev.architectury.registry.level.entity.trade.TradeRegistry')
    ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
  } catch (e) {
    console.error('[SVS-真菌残魂] 交易依赖类加载失败，村民交易跳过: ' + e)
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
        console.error('[SVS-真菌残魂] ItemListing 适配失败，村民交易跳过: ' + e2)
        return null
      }
    }
  }
  // 第二价用空气堆（isEmpty）等效单件收购，避开 ItemStack.EMPTY 的字段名。
  const farmerListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 12), Item.of('minecraft:air'), Item.of('tconstruct:grout', 8), 16, 2, 0.05)
  })
  const toolsmithListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 20), Item.of('minecraft:air'), Item.of('kubejs:fireseed_token', 1), 16, 2, 0.05)
  })
  if (!farmerListing || !toolsmithListing) return

  // 制图师 15 币 → 探险家指南针（2026-10-01 裁决：线索书链路放弃，改直接给指南针；
  // 指南针可自主搜索任意结构，探索自由度高于单条线索书）
  const cartographerListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 15), Item.of('minecraft:air'), Item.of('explorerscompass:explorerscompass', 1), 16, 2, 0.05)
  })

  // ── SLU 三魂兑换（规格书_真菌之魂 B 节，2026-10-05）：单向不回兑，打通"前期刷真菌攒家底 → 末期换魂补短板"
  //   工具匠 24 币→活尸之魂 / 盔甲匠 48 币→骑士之魂 / 武器匠 64 币→巨人之魂（比率初版默认，实测可微调）
  const toolsHollowListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 24), Item.of('minecraft:air'), Item.of('slu:hollow_soul', 1), 16, 2, 0.05)
  })
  const armorerKnightListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 48), Item.of('minecraft:air'), Item.of('slu:knight_soul', 1), 16, 2, 0.05)
  })
  const weaponsmithGiantListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 64), Item.of('minecraft:air'), Item.of('slu:giant_soul', 1), 16, 2, 0.05)
  })

  // ── 登记（architectury 静态 API；见文件头 ②）────────────────────────────────
  const VILLAGER_PROFESSIONS = ForgeRegistries.VILLAGER_PROFESSIONS
  function registerTrade(profId, listing) {
    const prof = VILLAGER_PROFESSIONS.getValue(new ResourceLocation('minecraft', profId))
    if (!prof) {
      console.error('[SVS-真菌残魂] 职业 id 不存在，交易跳过: ' + profId)
      return false
    }
    try {
      TradeRegistry.registerVillagerTrade(prof, 1, listing)
      return true
    } catch (e) {
      console.error('[SVS-真菌残魂] 交易登记失败(' + profId + '): ' + e)
      return false
    }
  }
  const okFarmer = registerTrade('farmer', farmerListing)
  const okToolsmith = registerTrade('toolsmith', toolsmithListing)
  const okCartographer = cartographerListing ? registerTrade('cartographer', cartographerListing) : false
  const okHollow = toolsHollowListing ? registerTrade('toolsmith', toolsHollowListing) : false
  const okKnight = armorerKnightListing ? registerTrade('armorer', armorerKnightListing) : false
  const okGiant = weaponsmithGiantListing ? registerTrade('weaponsmith', weaponsmithGiantListing) : false
  console.info('[SVS-真菌残魂] 村民交易登记：农民 ' + okFarmer + ' / 工具匠 ' + okToolsmith + ' / 制图师 ' + okCartographer +
    ' / 工具匠-活尸魂 ' + okHollow + ' / 盔甲匠-骑士魂 ' + okKnight + ' / 武器匠-巨人魂 ' + okGiant +
    '（12币→8grout、20币→1火种工具、15币→探险家指南针、24/48/64币→三魂；maxUses=16）')
})()