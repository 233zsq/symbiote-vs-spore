// svs_spawn_control.js — SLU 生物生成管控（2026-10-04 用户裁决：禁止野刷，改召唤制）
// 自然生成禁令由 openloader/data/svs/data/slu/forge/biome_modifier/ 的 36 个
// 空 biomes 覆盖实现（数据包层，本脚本不管）。
// 本脚本职责：
//   ① 实体类型标签 svs:slu_hostile —— 存量清场命令：
//      /kill @e[type=#svs:slu_hostile]
//   ② SLU 敌对生物击杀掉落 1 枚真菌残魂（野刷禁了但击杀内容保留，
//      供悬赏/日课任务线引用；与 spore_coin.js 的真菌系掉落并行）
// 友善 NPC（patches/solaire_spawner/siegmeyer_spawner）不在敌对标签内。

const SC_HOSTILE = [
  'slu:armed_hollow', 'slu:bad_omen_giant', 'slu:castle_guard', 'slu:dark_knight',
  'slu:dark_spirit', 'slu:dungeon_knight', 'slu:elite_knight', 'slu:executor',
  'slu:ghost_samurai', 'slu:havel', 'slu:hollow', 'slu:hollow_knight',
  'slu:hollow_soldier_spear', 'slu:hollow_soldier_sword', 'slu:knight', 'slu:mad_knight',
  'slu:magma_giant', 'slu:monster_blasphemy_knight', 'slu:monster_crucible_knight',
  'slu:monster_crucible_knight_2', 'slu:monster_crusader', 'slu:monster_godrick_knight',
  'slu:monster_godrick_soldier', 'slu:monster_successor', 'slu:monster_tower_knight',
  'slu:nightmare_knight', 'slu:noble_knight', 'slu:ringed_knight', 'slu:shadow_assassin',
  'slu:temple_guard', 'slu:thief', 'slu:twisted_souls', 'slu:wither_skeleton_knight'
]

ServerEvents.tags('entity_type', event => {
  event.add('svs:slu_hostile', SC_HOSTILE)
})

// 击杀掉落：SLU 敌对生物死亡掉 1 真菌残魂
ServerEvents.entityLootTables(event => {
  SC_HOSTILE.forEach(id => {
    event.addEntity(id, loot => {
      loot.addPool(pool => {
        pool.rolls = 1
        pool.addItem('kubejs:spore_coin', 1, [1, 1])
      })
    })
  })
})

console.info('[SVS-刷怪管控] SLU 野刷禁令（openloader 36 覆盖）+ 敌对标签 svs:slu_hostile（33 实体）+ 击杀掉真菌残魂 已就绪')
