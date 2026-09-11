// server_scripts/explorers_compass.js：Explorer's Compass 配方魔改 + 维度限制（/reload 热重载）
// 依据：整合包开发方案 3.7②（config 层 maxRadius/黑名单约束另行走 defaultconfigs，不在本脚本）
// 【待核实】模组尚未入包，脚本先行占位；入包后 /kubejs hand 确认物品 ID 再实测
const COMPASS_ID = 'explorerscompass:explorerscompass' // 【待核实】入包后 /kubejs hand 确认

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

ServerEvents.recipes(event => {
  // 【待核实】Item.exists 为 KubeJS 2001.6.x 待确认 API；若 /reload 报错，
  // 改为 try/catch Item.of(COMPASS_ID) 或直接删守卫（此时须保证模组先入包）
  if (!Item.exists(COMPASS_ID)) {
    console.warn('[explorers_compass] ' + COMPASS_ID + ' 尚未入包，配方魔改跳过（脚本先行占位）')
    return
  }
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

// 限制使用维度：仅主世界与暮色森林可用，其余维度拦截右键
// 注：服务端 cancel 是否足以拦住客户端预测打开 GUI，阶段⑤ 进游戏实测复核
ItemEvents.rightClicked(COMPASS_ID, event => {
  let dimId = getDimensionId(event.level)
  if (ALLOWED_DIMENSIONS.indexOf(dimId) < 0) {
    event.player.tell('§c指南针的魔力在这片空间紊乱，无法定位结构……')
    event.cancel()
  }
})
