// server_scripts/explorers_compass.js：Explorer's Compass 三层削弱（2026-10-03 裁决落地）
//   第一层 配方成本（下界合金+淬魔钢坯）、第二层 维度白名单（主世界+暮色），
//   第三层 真菌币过路费（config 层 structureBlacklist 主线黑名单另见
//   config/explorerscompass-common.toml）。
// 定位（任务线规格书）：路网负责"带路"、Xaero 负责"记录"、线索书负责"主线指引"、
//   指南针只做"后期兜底"——主线结构已列入罗盘黑名单，此处收真菌币作使用摩擦。
// 注意：本脚本依赖 mod 已入包（ExplorersCompass 1.4.0 已实证在包），勿回退占位守卫。

const COMPASS_ID = 'explorerscompass:explorerscompass'
const COIN_ID = 'kubejs:spore_coin'
const COIN_COST = 2   // 每次定位消耗真菌之魂（2026-10-03 裁决"找结构耗真菌币"）
let ecCoins = 0       // Rhino 守则：块内不声明，计数变量提文件级

// 维度白名单：仅主世界与暮色森林可定位结构（防止跨维度抄近路）
const ALLOWED_DIMENSIONS = [
  'minecraft:overworld',
  'twilightforest:twilight_forest'
]

// 兼容 ResourceKey（toString 带 ResourceKey[...] 包裹）与 ResourceLocation 两种返回形态
function getDimensionId(level) {
  let dim = level.dimension
  if (dim.location) {
    return String(dim.location())
  }
  return String(dim)
}

// 创造模式判定（isCreativeMode 是旧版名，1.20.1 mojmap 为 isCreative；
// 该方法是 Player 声明/ServerPlayer 继承——9-30 经验：继承成员解析不稳，
// 故带兜底：解析失败视为非创造（照常收费），不崩）
function ecIsCreative(player) {
  let v = false
  try { v = player.isCreative() } catch (e) { v = false }
  return v
}

ServerEvents.recipes(event => {
  // 移除默认配方（原「一块铁 + 几根线」），改为中后期奖励级成本
  event.remove({ output: COMPASS_ID })
  event.shaped(COMPASS_ID, [
    'NDN',
    'DCD',
    'NDN'
  ], {
    N: 'minecraft:netherite_ingot',
    D: 'kubejs:tempered_steel_billet',
    C: 'minecraft:compass'
  })
})

// 右键拦截：维度白名单 + 真菌币过路费
ItemEvents.rightClicked(COMPASS_ID, event => {
  // 第二层：维度白名单
  let dimId = getDimensionId(event.level)
  if (ALLOWED_DIMENSIONS.indexOf(dimId) < 0) {
    event.player.tell('§7冒险者，指南针的魔力在这片空间紊乱，无法定位结构……')
    event.cancel()
    return
  }
  // 第三层：真菌币过路费（生存模式收费；创造模式免费）
  if (!ecIsCreative(event.player)) {
    ecCoins = 0
    try { ecCoins = event.player.inventory.count(COIN_ID) } catch (e) {
      console.warn('[explorers_compass] 背包计数失败（API 变动？）: ' + e)
      return   // 计数失败时宁可放行，不卡死玩家
    }
    if (ecCoins < COIN_COST) {
      event.player.tell('§c冒险者，定位一次需要 ' + COIN_COST + ' 枚真菌之魂（你还差 ' + (COIN_COST - ecCoins) + ' 枚）。')
      event.cancel()
      return
    }
    // 精确扣除走 vanilla clear 命令（clear <玩家> <物品> <数量>，实证可靠）
    event.server.runCommandSilent('clear ' + event.player.username + ' ' + COIN_ID + ' ' + COIN_COST)
    event.player.tell('§6支付 ' + COIN_COST + ' 枚真菌之魂，指南针开始指引……')
  }
})
