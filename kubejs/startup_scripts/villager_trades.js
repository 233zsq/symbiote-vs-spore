// villager_trades.js — 村民交易注册（魔改第一期 · 规格 1③）
//   农民加 12 币→8 匠魂 grout，工具匠加 20 币→1 火种绑定工具（kubejs:fireseed_token），
//   制图师加 15 币→共生体陨石线索成书（理念 1"交易获得结构线索"，交易时实时寻址）。
// ⚠️ 必须在 startup 脚本：ForgeEvents 绑定只在 ScriptType.isStartup() 注入
//   （BuiltinKubeJSForgePlugin.registerBindings 字节码实证），server 脚本里 ForgeEvents
//   是 not defined——本段此前放 spore_coin.js(server) 导致 8/9 加载中断，交易全灭。
// 方案：Forge 原生 VillagerTradesEvent（每个村民生成交易时触发），向 1 级交易列表追加。
// 职业判别：ForgeRegistries.VILLAGER_PROFESSIONS.getKey(职业) 按 id 比对。
// 成员名一律写 mojmap——KubeJS Rhino 生产环境自动 remap 到 SRG；直写 SRG 名反而查不到
// （2026-09-24 实踩），java.lang.Class/reflect 反射则被类过滤器拦截。
// TODO(K3-调参): maxUses=9999、villagerXp=2、priceMult=0.05 为初版数值（限量/阶梯价见评审 P2）

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

  // 第二价用空气堆（isEmpty）等效单件收购，避开 ItemStack.EMPTY 的字段名。
  const farmerListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 12), Item.of('minecraft:air'), Item.of('tconstruct:grout', 8), 9999, 2, 0.05)
  })
  const toolsmithListing = makeListing(function () {
    return new MerchantOffer(Item.of('kubejs:spore_coin', 20), Item.of('minecraft:air'), Item.of('kubejs:fireseed_token', 1), 9999, 2, 0.05)
  })
  if (!farmerListing || !toolsmithListing) return

  // 共生体陨石线索（理念 1：交易获得结构线索）：制图师 15 币 → 成书，
  // 交易瞬间按制图师位置计算最近陨石坐标写入书页。
  // 初版用成书不用探索地图（vanilla TreasureMapForEmeralds 强绑绿宝石+指南针计价链，
  // 自绘地图链路长；成书承载同等信息，TODO 升级真地图）。
  let ResourceKey, ResourceLocation, Registries, HolderSet
  try {
    ResourceKey = Java.loadClass('net.minecraft.resources.ResourceKey')
    ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
    Registries = Java.loadClass('net.minecraft.core.registries.Registries')
    HolderSet = Java.loadClass('net.minecraft.core.HolderSet')
  } catch (e) {
    console.error('[SVS-真菌币] 线索书依赖类加载失败，制图师交易跳过: ' + e)
    ResourceKey = null
  }

  // 带 trader 上下文的 SAM 适配（与 makeListing 同构，多传 trader 用于定位）
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

  const cartographerListing = ResourceKey ? makeListingCtx(function (trader) {
    try {
      const level = trader.level()
      const structReg = level.registryAccess().registryOrThrow(Registries.STRUCTURE)
      const holder = structReg.getHolderOrThrow(ResourceKey.create(Registries.STRUCTURE, new ResourceLocation('symbiote', 'meteor_crash')))
      const found = level.getChunkSource().getGenerator()
        .findNearestMapStructure(level, HolderSet.direct(holder), trader.blockPosition(), 100, false)
      let text
      if (found) {
        const bp = found.getFirst()
        text = '最近共生体陨石坐标：X=' + bp.getX() + '，Z=' + bp.getZ() + '。愿真菌与你无缘。'
      } else {
        text = '方圆 1600 格内未发现共生体陨石……往更远的荒野去吧。'
      }
      const page = '{"text":"' + text + '"}'
      const book = Item.of('minecraft:written_book', '{title:"共生体线索",author:"制图师",pages:[' + page + ']}')
      return new MerchantOffer(Item.of('kubejs:spore_coin', 15), Item.of('minecraft:air'), book, 9999, 2, 0.05)
    } catch (e) {
      console.error('[SVS-真菌币] 线索书生成失败（本笔交易不生成）: ' + e)
      return null      // SAM 返回 null = 该交易位空缺，不崩
    }
  }) : null

  ForgeEvents.onEvent('net.minecraftforge.event.village.VillagerTradesEvent', event => {
    try {
      const key = String(ForgeRegistries.VILLAGER_PROFESSIONS.getKey(event.type))
      let listing = null
      if (key === 'minecraft:farmer') listing = farmerListing
      else if (key === 'minecraft:toolsmith') listing = toolsmithListing
      else if (key === 'minecraft:cartographer') listing = cartographerListing
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
  console.info('[SVS-真菌币] 村民交易监听已挂：农民 12币→8grout，工具匠 20币→1火种绑定工具，制图师 15币→陨石线索书')
})()
