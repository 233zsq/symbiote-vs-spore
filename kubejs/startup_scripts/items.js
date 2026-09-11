// startup_scripts/items.js：本包独占战斗向物品注册（startup 阶段，改动需重启游戏生效）
// 依据：整合包开发方案 3.4「自定义内容注册：战斗向独占物品」
// 产物链定位：Boss 掉落素材 → 淬魔钢坯 → 深渊合金锭 → 终局武器锻造（方案 3.3 主线锻造线）
StartupEvents.registry('item', event => {
  // 终局武器材料：由 Cataclysm 等 Boss 掉落物合成的顶级锻造材料（阶段Ⅴ 终局解锁）
  event.create('abyss_ingot')
    .displayName('深渊合金锭')
    .maxStackSize(16)
    .glow(true)
    .rarity('epic')

  // 中间产物：下界/暮色 Boss 素材的初步锻造件（配方阶段Ⅲ 解锁，见方案 3.5）
  event.create('tempered_steel_billet')
    .displayName('淬魔钢坯')
    .maxStackSize(32)
    .rarity('uncommon')

  // 任务叙事物：终局武器的「破损前身」，任务线叙事用，不参与战斗
  event.create('broken_hero_blade')
    .displayName('破损的英雄之刃')
    .maxStackSize(1)
    .rarity('rare')

  // 模组武器材料收束件：数值/成本倒挂的模组武器核心部件统一收束到本物品
  // （使用方：server_scripts/weapon_balance.js 的 replaceInput 材料收束）
  event.create('refined_iron_ingot')
    .displayName('精制铁锭')
    .maxStackSize(64)
})
