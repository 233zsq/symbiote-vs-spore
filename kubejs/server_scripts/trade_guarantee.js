// trade_guarantee.js — 自定村民交易必现补挂（F2 修复 · 2026-10-01）
// 根因（P7 探针实证）：architectury 合并成功（交易表 L1 里能看到我们的 adapter listing），
//   但 vanilla 构建村民 offers 时从列表**随机抽 2 笔**（farmer L1 有 8 项，中签率仅 25%），
//   规格"新村民三职业各带新交易"的必现要求无法靠注册达成。
// 修法：每秒扫描玩家 64 格内职业村民；offers 已构建但缺我们那笔 → 直接
//   getOffers().add(MerchantOffer)（MerchantOffers 是 List，add 持久化进村民 NBT，
//   交易界面打开即见；maxUses=16 限量语义保留）。补挂成功打 pd 标记防重。
// 与 villager_trades.js 的表注册共存：随机抽中也算"已有"，不重复补。
// 线索书在补挂时按村民位置实时寻址陨石（原 ctx 交易同款逻辑）。

const TG_Villager = Java.loadClass('net.minecraft.world.entity.npc.Villager')
let TG_MerchantOffer = null
try { TG_MerchantOffer = Java.loadClass('net.minecraft.world.item.trading.MerchantOffer') } catch (e) { }
let TG_ResourceKey = null, TG_Registries = null, TG_TagKey = null, TG_ResourceLocation = null, TG_BlockPos = null
try {
  TG_ResourceKey = Java.loadClass('net.minecraft.resources.ResourceKey')
  TG_Registries = Java.loadClass('net.minecraft.core.registries.Registries')
  TG_TagKey = Java.loadClass('net.minecraft.tags.TagKey')
  TG_ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
  TG_BlockPos = Java.loadClass('net.minecraft.core.BlockPos')
} catch (e) {
  console.warn('[SVS-交易] 线索书依赖类加载失败，制图师补挂跳过: ' + e)
}

// 三笔交易定义（与 villager_trades.js 表注册保持同参数）
const TG_COST = { farmer: 12, toolsmith: 20, cartographer: 15 }
const TG_RESULT_STR = { farmer: 'grout', toolsmith: 'fireseed_token', cartographer: 'written_book' }
const TG_MAX_USES = 16, TG_XP = 2, TG_MULT = 0.05

const TG_VLIST_WARNED = {}
function TGWarnOnce(tag, e) {
  if (TG_VLIST_WARNED[tag]) return
  TG_VLIST_WARNED[tag] = true
  console.warn('[SVS-交易] ' + tag + '（只提示一次）: ' + e)
}

// Rhino 守则：以下声明全部函数/回调最外层，块内只赋值
let TG_TICK = 0
let TG_Players = null, TG_P = null, TG_VLIST = null
let TG_V = null, TG_PD = null, TG_OFFERS = null, TG_OFFER = null, TG_BOOK = null
let TG_PROFESSION = '', TG_HAS = false
let TG_LV = null, TG_REG = null, TG_HOLDERSET = null, TG_FOUND = null, TG_BP = null, TG_POS = null
let TG_TEXT = '', TG_PAGE = ''

// 造线索书（按村民位置寻址最近陨石；与 villager_trades.js cartographer 交易同逻辑）
function TGMakeBook(trader) {
  if (!TG_TagKey) return null
  try {
    TG_LV = trader.level    // level 是属性不是方法（探针 C5 实证：level() 调用报错）
    TG_REG = TG_LV.registryAccess().registryOrThrow(TG_Registries.STRUCTURE)
    // HolderSet.direct 在 Rhino 里调 varargs/List 重载都会 NPE（10-01 两轮实证）→
    // 走 vanilla 同款结构 TAG（openloader svs 包 svs:meteor_clue = symbiote:meteor_crash）
    TG_HOLDERSET = TG_REG.getOrCreateTag(TG_TagKey.create(TG_Registries.STRUCTURE, new TG_ResourceLocation('svs', 'meteor_clue')))
    TG_POS = new TG_BlockPos(Math.floor(trader.x), Math.floor(trader.y), Math.floor(trader.z))   // blockPosition() 未实证，用实证过的 x/y/z
    TG_FOUND = TG_LV.getChunkSource().getGenerator()
      .findNearestMapStructure(TG_LV, TG_HOLDERSET, TG_POS, 100, false)
    if (TG_FOUND) {
      TG_BP = TG_FOUND.getFirst()
      TG_TEXT = '最近共生体陨石坐标：X=' + TG_BP.getX() + '，Z=' + TG_BP.getZ() + '。愿真菌与你无缘。'
    } else {
      TG_TEXT = '方圆 1600 格内未发现共生体陨石……往更远的荒野去吧。'
    }
    TG_PAGE = '{"text":"' + TG_TEXT + '"}'
    return Item.of('minecraft:written_book', '{title:"共生体线索",author:"制图师",pages:[' + TG_PAGE + ']}')
  } catch (e) {
    TGWarnOnce('线索书生成', e)
    return null
  }
}

function TGGuarantee(v) {
  try {
    TG_PROFESSION = String(v.getVillagerData().getProfession())
    if (!TG_COST[TG_PROFESSION]) return
    TG_PD = v.getPersistentData()
    if (TG_PD.getBoolean('svs_tg_done')) return
    TG_OFFERS = v.getOffers()
    if (!TG_OFFERS || TG_OFFERS.size() === 0) return          // offers 尚未构建（未认领职业/无工作站）
    TG_HAS = false
    for (let k = 0; k < TG_OFFERS.size(); k++) {
      if (String(TG_OFFERS.get(k).getResult()).indexOf(TG_RESULT_STR[TG_PROFESSION]) >= 0) {
        TG_HAS = true
        break
      }
    }
    if (TG_HAS) { TG_PD.putBoolean('svs_tg_done', true); return }
    if (!TG_MerchantOffer) return
    if (TG_PROFESSION === 'farmer') {
      TG_OFFER = new TG_MerchantOffer(Item.of('kubejs:spore_coin', TG_COST.farmer), Item.of('minecraft:air'), Item.of('tconstruct:grout', 8), TG_MAX_USES, TG_XP, TG_MULT)
    } else if (TG_PROFESSION === 'toolsmith') {
      TG_OFFER = new TG_MerchantOffer(Item.of('kubejs:spore_coin', TG_COST.toolsmith), Item.of('minecraft:air'), Item.of('kubejs:fireseed_token', 1), TG_MAX_USES, TG_XP, TG_MULT)
    } else {
      TG_BOOK = TGMakeBook(v)
      if (!TG_BOOK) return
      TG_OFFER = new TG_MerchantOffer(Item.of('kubejs:spore_coin', TG_COST.cartographer), Item.of('minecraft:air'), TG_BOOK, TG_MAX_USES, TG_XP, TG_MULT)
    }
    TG_OFFERS.add(TG_OFFER)
    TG_PD.putBoolean('svs_tg_done', true)
    console.info('[SVS-交易] 补挂自定交易：' + TG_PROFESSION + ' ← ' + TG_RESULT_STR[TG_PROFESSION] + '（随机抽取未中签，已强制补挂）')
  } catch (e) {
    TGWarnOnce('补挂', e)
  }
}

ServerEvents.tick(event => {
  TG_TICK++
  if (TG_TICK % 20 !== 0) return          // 每秒 1 次
  const srv = event.server
  if (!srv) return
  TG_Players = srv.getPlayers()
  for (let i = 0; i < TG_Players.size(); i++) {
    TG_P = TG_Players.get(i)
    if (!TG_P || !TG_P.level) continue
    try {
      TG_VLIST = TG_P.level.getEntitiesOfClass(TG_Villager, TG_P.getBoundingBox().inflate(64))
    } catch (e) {
      TGWarnOnce('村民扫描', e)
      continue
    }
    for (let j = 0; j < TG_VLIST.size(); j++) {
      TG_V = TG_VLIST.get(j)
      if (TG_V) TGGuarantee(TG_V)
    }
  }
})
