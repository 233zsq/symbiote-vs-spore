// villager_trades.js — 村民交易注册（魔改第一期 · 规格 1③）
//   农民加 12 币→8 匠魂 grout，工具匠加 20 币→1 火种绑定工具（kubejs:fireseed_token），
//   制图师加 15 币→共生体陨石线索成书（理念 1"交易获得结构线索"，交易时实时寻址）。
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
    console.error('[SVS-真菌币] 交易依赖类加载失败，村民交易跳过: ' + e)
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
  // 带 trader 上下文的变体（制图师要用交易者位置实时寻址陨石）
  function makeListingCtx(factory) {
    try {
      return new ItemListing(function (trader, random) { return factory(trader) })
    } catch (e1) {
      try {
        return new JavaAdapter(ItemListing, function (trader, random) { return factory(trader) })
      } catch (e2) {
        console.error('[SVS-真菌币] ItemListing(ctx) 适配失败，制图师交易跳过: ' + e2)
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

  // 共生体陨石线索（理念 1：交易获得结构线索）：制图师 15 币 → 成书，
  // 交易瞬间按交易者位置计算最近陨石坐标写入书页。
  // 初版用成书不用探索地图（vanilla TreasureMapForEmeralds 强绑绿宝石+指南针计价链，
  // 自绘地图链路长；成书承载同等信息，TODO 升级真地图）。
  let BlockPos, SvsTweakHelper
  try {
    BlockPos = Java.loadClass('net.minecraft.core.BlockPos')
    SvsTweakHelper = Java.loadClass('com.svs.tweak.kubejs.SvsDamageHelper')   // 1.0.6：locateStructure 纯 Java 寻址
  } catch (e) {
    console.error('[SVS-真菌币] 线索书依赖类加载失败（svs_tweak ≥1.0.6 缺失？），制图师交易跳过: ' + e)
    SvsTweakHelper = null
  }

  const cartographerListing = SvsTweakHelper ? makeListingCtx(function (trader) {
    // Rhino 守则：块（try）内不声明 const/let（第二次执行抛 redeclaration）→ 声明提到函数最外层
    let lv = null, pos = null, coords = ''
    let text = '', page = '', book = null
    try {
      lv = trader.level    // level 是属性不是方法（C5 探针实证）
      pos = new BlockPos(Math.floor(trader.x), Math.floor(trader.y), Math.floor(trader.z))
      // 寻址链整体走 svs_tweak 1.0.6 locateStructure（Rhino 里 HolderSet.direct 必 NPE）
      coords = SvsTweakHelper.locateStructure(lv, 'symbiote', 'meteor_crash', pos)
      if (coords) {
        text = '最近共生体陨石坐标：' + coords.replace('|', '，') + '。愿真菌与你无缘。'
      } else {
        text = '方圆 1600 格内未发现共生体陨石……往更远的荒野去吧。'
      }
      page = '{"text":"' + text + '"}'
      book = Item.of('minecraft:written_book', '{title:"共生体线索",author:"制图师",pages:[' + page + ']}')
      return new MerchantOffer(Item.of('kubejs:spore_coin', 15), Item.of('minecraft:air'), book, 16, 2, 0.05)
    } catch (e) {
      console.error('[SVS-真菌币] 线索书生成失败（本笔交易不生成）: ' + e)
      return null      // SAM 返回 null = 该交易位空缺，不崩
    }
  }) : null

  // ── 登记（architectury 静态 API；见文件头 ②）────────────────────────────────
  const VILLAGER_PROFESSIONS = ForgeRegistries.VILLAGER_PROFESSIONS
  function registerTrade(profId, listing) {
    const prof = VILLAGER_PROFESSIONS.getValue(new ResourceLocation('minecraft', profId))
    if (!prof) {
      console.error('[SVS-真菌币] 职业 id 不存在，交易跳过: ' + profId)
      return false
    }
    try {
      TradeRegistry.registerVillagerTrade(prof, 1, listing)
      return true
    } catch (e) {
      console.error('[SVS-真菌币] 交易登记失败(' + profId + '): ' + e)
      return false
    }
  }
  const okFarmer = registerTrade('farmer', farmerListing)
  const okToolsmith = registerTrade('toolsmith', toolsmithListing)
  const okCartographer = cartographerListing ? registerTrade('cartographer', cartographerListing) : false
  console.info('[SVS-真菌币] 村民交易登记：农民 ' + okFarmer + ' / 工具匠 ' + okToolsmith + ' / 制图师 ' + okCartographer +
    '（12币→8grout、20币→1火种工具、15币→陨石线索书；maxUses=16）')
})()