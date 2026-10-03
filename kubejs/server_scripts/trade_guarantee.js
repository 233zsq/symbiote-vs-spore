// trade_guarantee.js — 自定村民交易必现补挂（F2 修复 · 2026-10-01）
// 根因（P7 探针实证）：architectury 合并成功（交易表 L1 里能看到我们的 adapter listing），
//   但 vanilla 构建村民 offers 时从列表**随机抽 2 笔**（farmer L1 有 8 项，中签率仅 25%），
//   规格"新村民三职业各带新交易"的必现要求无法靠注册达成。
// 修法：每秒扫描玩家 64 格内职业村民；offers 已构建但缺我们那笔 → 直接
//   getOffers().add(MerchantOffer)（MerchantOffers 是 List，add 持久化进村民 NBT，
//   交易界面打开即见；maxUses=16 限量语义保留）。补挂成功打 pd 标记防重。
// 三笔：农民 12 币→8 grout / 工具匠 20 币→1 火种绑定工具 /
//       制图师 15 币→1 探险家指南针（2026-10-01 裁决：线索书链路放弃——
//       Rhino NPE/空标签/空白页三连，改直接给指南针）。
// 与 villager_trades.js 的表注册共存：随机抽中也算"已有"，不重复补。

const TG_Villager = Java.loadClass('net.minecraft.world.entity.npc.Villager')
let TG_MerchantOffer = null
try { TG_MerchantOffer = Java.loadClass('net.minecraft.world.item.trading.MerchantOffer') } catch (e) { }

// 三笔交易定义（与 villager_trades.js 表注册保持同参数）
const TG_COST = { farmer: 12, toolsmith: 20, cartographer: 15 }
const TG_RESULT_STR = { farmer: 'grout', toolsmith: 'fireseed_token', cartographer: 'explorerscompass' }
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
let TG_V = null, TG_PD = null, TG_OFFERS = null, TG_OFFER = null
let TG_PROFESSION = '', TG_HAS = false

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
      TG_OFFER = new TG_MerchantOffer(Item.of('kubejs:spore_coin', TG_COST.cartographer), Item.of('minecraft:air'), Item.of('explorerscompass:explorerscompass', 1), TG_MAX_USES, TG_XP, TG_MULT)
    }
    TG_OFFERS.add(TG_OFFER)
    TG_PD.putBoolean('svs_tg_done', true)
    console.info('[SVS-交易] 补挂自定交易：' + TG_PROFESSION + '（随机抽取未中签，已强制补挂）')
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
