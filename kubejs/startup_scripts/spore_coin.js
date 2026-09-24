// spore_coin.js (startup) · 注册真菌币与火种绑定工具
// 魔改第一期：真菌币经济（规格书 E:\mcmp_test\魔改第一期规格书.md 第 1 条）
StartupEvents.registry('item', event => {
  event.create('spore_coin')
    .displayName('真菌币')
    .texture('minecraft:item/emerald')
  event.create('fireseed_token')
    .displayName('火种绑定工具')
    .texture('minecraft:item/name_tag')
    .maxStackSize(16)
})
