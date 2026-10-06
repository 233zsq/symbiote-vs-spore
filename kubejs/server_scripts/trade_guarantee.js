// trade_guarantee.js — 自定村民交易必现补挂（F2 修复 · 2026-10-01；三魂扩展 · 2026-10-06）
// 根因（P7 探针实证）：architectury 合并成功（交易表 L1 里能看到我们的 adapter listing），
//   但 vanilla 构建村民 offers 时从列表**随机抽 2 笔**（farmer L1 有 8 项，中签率仅 25%），
//   规格"新村民三职业各带新交易"的必现要求无法靠注册达成。
// 修法：每秒扫描玩家 64 格内职业村民；offers 已构建但缺我们那笔 → 直接
//   getOffers().add(MerchantOffer)（MerchantOffers 是 List，add 持久化进村民 NBT，
//   交易界面打开即见；maxUses=16 限量语义保留）。补挂成功打 pd 标记防重。
// 六笔：农民 12 币→8 grout / 工具匠 20 币→1 火种绑定工具 / 制图师 15 币→1 探险家指南针
//   （2026-10-01 裁决：线索书链路放弃——Rhino NPE/空标签/空白页三连，改直接给指南针）；
//   SLU 三魂（2efc7db，规格书_真菌之魂 B 节）：工具匠 24 币→活尸之魂 /
//   盔甲匠 48 币→骑士之魂 / 武器匠 64 币→巨人之魂。
//   10-06 扩展原因：三魂此前只进了表注册候选池——vanilla 随机抽 2 笔机制下
//   工具匠（L1 原版 2 笔+我们 2 笔=4 抽 2）单笔中签约 50%、盔甲匠/武器匠约 67%，
//   大量村民永不出现魂交易（与 F2 同机制）；且规格书 B 节成文于 F2 发现之前，
//   按"实证优先"原则补挂。标记从单一 svs_tg_done 改为**按笔独立 flag**
//   （工具匠有两笔，旧单标记补挂火种后会把活尸魂永久锁死）。
// 与 villager_trades.js 的表注册共存：随机抽中也算"已有"，不重复补。

const TG_Villager = Java.loadClass('net.minecraft.world.entity.npc.Villager')
let TG_MerchantOffer = null
try { TG_MerchantOffer = Java.loadClass('net.minecraft.world.item.trading.MerchantOffer') } catch (e) { }

// 六笔交易定义（与 villager_trades.js 表注册保持同参数；同职业多笔——按笔独立 flag）
const TG_TRADES = [
  { prof: 'farmer', flag: 'svs_tg_farmer', match: 'grout', cost: 12, result: 'tconstruct:grout', n: 8 },
  { prof: 'toolsmith', flag: 'svs_tg_toolsmith', match: 'fireseed_token', cost: 20, result: 'kubejs:fireseed_token', n: 1 },
  { prof: 'cartographer', flag: 'svs_tg_cartographer', match: 'explorerscompass', cost: 15, result: 'explorerscompass:explorerscompass', n: 1 },
  { prof: 'toolsmith', flag: 'svs_tg_hollow', match: 'hollow_soul', cost: 24, result: 'slu:hollow_soul', n: 1 },
  { prof: 'armorer', flag: 'svs_tg_knight', match: 'knight_soul', cost: 48, result: 'slu:knight_soul', n: 1 },
  { prof: 'weaponsmith', flag: 'svs_tg_giant', match: 'giant_soul', cost: 64, result: 'slu:giant_soul', n: 1 }
]
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
let TG_DEF = null

function TGGuarantee(v) {
  try {
    TG_PROFESSION = String(v.getVillagerData().getProfession())
    TG_PD = v.getPersistentData()
    TG_OFFERS = v.getOffers()
    if (!TG_OFFERS || TG_OFFERS.size() === 0) return          // offers 尚未构建（未认领职业/无工作站）
    if (!TG_MerchantOffer) return
    for (let t = 0; t < TG_TRADES.length; t++) {
      TG_DEF = TG_TRADES[t]
      if (TG_DEF.prof !== TG_PROFESSION) continue
      if (TG_PD.getBoolean(TG_DEF.flag)) continue
      TG_HAS = false
      for (let k = 0; k < TG_OFFERS.size(); k++) {
        if (String(TG_OFFERS.get(k).getResult()).indexOf(TG_DEF.match) >= 0) {
          TG_HAS = true
          break
        }
      }
      if (TG_HAS) { TG_PD.putBoolean(TG_DEF.flag, true); continue }
      TG_OFFER = new TG_MerchantOffer(Item.of('kubejs:spore_coin', TG_DEF.cost), Item.of('minecraft:air'), Item.of(TG_DEF.result, TG_DEF.n), TG_MAX_USES, TG_XP, TG_MULT)
      TG_OFFERS.add(TG_OFFER)
      TG_PD.putBoolean(TG_DEF.flag, true)
      console.info('[SVS-交易] 补挂自定交易：' + TG_PROFESSION + ' ' + TG_DEF.cost + ' 币→' + TG_DEF.result + '（随机抽取未中签，已强制补挂）')
    }
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
