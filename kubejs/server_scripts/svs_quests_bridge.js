// FTB v2 bridge. User authorized generated SNBT on 2026-10-11.
// No command-based fake wins, once flags, per-session completion caches or old-stage migration.
// Binding IDs are 52-bit: no Java-long -> JS-number rounding at the Rhino boundary.
const QV2_TeamData = Java.loadClass('dev.ftb.mods.ftbquests.quest.TeamData')
const QV2_ServerQuestFile = Java.loadClass('dev.ftb.mods.ftbquests.quest.ServerQuestFile')
const QV2_Monster = Java.loadClass('net.minecraft.world.entity.monster.Monster')
const QV2_ServerPlayer = Java.loadClass('net.minecraft.server.level.ServerPlayer')
const QV2_Villager = Java.loadClass('net.minecraft.world.entity.npc.Villager')
const QV2_Tracker = Java.loadClass('com.scout.symbiote.tracker.SymbioteTracker')
const QV2_Helper = Java.loadClass('com.svs.tweak.kubejs.SvsDamageHelper')
const QV2_Stages = Java.loadClass('net.darkhax.gamestages.GameStageHelper')
const QV2_ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
const QV2_ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
let QV2_Hunt = null
let QV2_FeedingHunt = null
try { QV2_Hunt = Java.loadClass('com.scout.symbiote.ability.PredatorHunt') } catch (e) { }
try { QV2_FeedingHunt = Java.loadClass('com.scout.symbiote.ability.SymbioteFeedingHunt') } catch (e) { }
const QV2_RANK = { UNBONDED: 0, ATTACHED: 1, INTEGRATED: 2, COOPERATIVE: 3, DOMINANT: 4 }
const QV2_Armor = [
  'minecraft:iron_helmet', 'minecraft:iron_chestplate', 'minecraft:iron_leggings', 'minecraft:iron_boots',
  'minecraft:diamond_helmet', 'minecraft:diamond_chestplate', 'minecraft:diamond_leggings', 'minecraft:diamond_boots',
  'minecraft:netherite_helmet', 'minecraft:netherite_chestplate', 'minecraft:netherite_leggings', 'minecraft:netherite_boots',
  'saintsdragons:dragonlord_helmet', 'saintsdragons:dragonlord_chestplate',
  'saintsdragons:dragonlord_leggings', 'saintsdragons:dragonlord_boots'
]
const QV2_Eggs = ['raevyx', 'cindervane', 'atroxiia', 'stegonaut', 'varasuchus', 'ignivorus', 'volitans']
let QV2_Ticks = 0
let QV2_Warned = {}
let QV2_Audited = false

function qv2Warn(key, err) {
  if (QV2_Warned[key]) return
  QV2_Warned[key] = true
  console.warn('[SVS-QV2] ' + key + ': ' + err)
}
function qv2Dim(level) {
  const dim = level.dimension
  if (dim.location) return String(dim.location())
  return String(dim)
}
function qv2Task(binding) {
  const file = QV2_ServerQuestFile.INSTANCE
  if (!file) return null
  const task = file.getTask(file.getID(binding.task_id))
  if (!task) return null
  // CustomTask fields are NOT serialized in this installed version. Configure through real API.
  task.setEnableButton(false)
  task.setMaxProgress(binding.count || 1)
  return task
}
function qv2Progress(player, binding, amount) {
  let team = null, task = null
  try {
    team = QV2_TeamData.get(player)
    task = qv2Task(binding)
    if (!team || !task || !team.canStartTasks(task.getQuest()) || team.isCompleted(task)) return
    team.addProgress(task, amount)
  } catch (e) { qv2Warn('progress/' + binding.key, e) }
}
function qv2Rank(player) {
  let tracker = null, profile = null
  try {
    tracker = QV2_Tracker.get(player.level)
    profile = tracker ? tracker.peek(player.uuid) : null
    return profile && profile.stage ? (QV2_RANK[String(profile.stage.name())] || 0) : 0
  } catch (e) { qv2Warn('bond', e) }
  return 0
}
function qv2Village(player) {
  let villagers = null
  if (qv2Dim(player.level) !== 'minecraft:overworld') return false
  try {
    villagers = player.level.getEntitiesOfClass(QV2_Villager, player.getBoundingBox().inflate(128))
    return villagers && villagers.size() >= 3
  } catch (e) { qv2Warn('village', e) }
  return false
}
function qv2Count(player, items) {
  let total = 0
  for (let i = 0; i < items.length; i++) total += player.inventory.count(items[i])
  return total
}
function qv2Hunting(player) {
  try {
    return (QV2_Hunt && QV2_Hunt.isHunting(player.uuid)) ||
      (QV2_FeedingHunt && QV2_FeedingHunt.isHunting(player.uuid))
  } catch (e) { qv2Warn('hunt', e) }
  return false
}

function qv2Stages(player) {
  const milestones = global.svsQuestV2Stages || []
  const file = QV2_ServerQuestFile.INSTANCE
  let team = null, quest = null, entry = null
  try {
    team = QV2_TeamData.get(player)
    if (!team || !file) return
    for (let i = 0; i < milestones.length; i++) {
      entry = milestones[i]
      quest = file.getQuest(file.getID(entry.quest_id))
      // Only new v2 team progress qualifies. Old stage IDs never enter this path.
      if (quest && team.isCompleted(quest) && !QV2_Stages.hasStage(player, entry.stage)) {
        QV2_Stages.addStage(player, entry.stage)
      }
    }
  } catch (e) { qv2Warn('stage-sync', e) }
}
function qv2Audit() {
  const manifest = global.svsQuestV2Audit
  const file = QV2_ServerQuestFile.INSTANCE
  let missing = [], id = '', binding = null
  if (!manifest || !file) return
  try {
    for (let i = 0; i < manifest.quests.length; i++) {
      id = manifest.quests[i]
      if (!file.getQuest(file.getID(id))) missing.push('quest:' + id)
    }
    for (let i = 0; i < manifest.items.length; i++) {
      id = manifest.items[i]
      if (!QV2_ForgeRegistries.ITEMS.containsKey(new QV2_ResourceLocation(id))) missing.push('item:' + id)
    }
    for (let i = 0; i < manifest.entities.length; i++) {
      id = manifest.entities[i]
      if (!QV2_ForgeRegistries.ENTITY_TYPES.containsKey(new QV2_ResourceLocation(id))) missing.push('entity:' + id)
    }
    for (let i = 0; i < global.svsQuestV2Bindings.length; i++) {
      binding = global.svsQuestV2Bindings[i]
      if (!qv2Task(binding)) missing.push('task:' + binding.task_id)
    }
    console.info('[SVS-QV2-AUDIT] quests=' + manifest.quests.length + ' missing=' + JSON.stringify(missing))
    QV2_Audited = true
  } catch (e) { qv2Warn('audit', e) }
}

ServerEvents.tick(event => {
  QV2_Ticks++
  if (QV2_Ticks % 40 !== 0) return
  if (!QV2_Audited) qv2Audit()
  const bindings = global.svsQuestV2Bindings || []
  const players = event.server.getPlayers()
  let player = null, binding = null, eligible = false, rank = 0, village = false
  for (let pi = 0; pi < players.size(); pi++) {
    player = players.get(pi)
    if (!player || !player.level) continue
    rank = qv2Rank(player)
    qv2Stages(player)
    village = false
    for (let bi = 0; bi < bindings.length; bi++) {
      binding = bindings[bi]
      if (binding.kind !== 'bridge') continue // pending goals deliberately have no completion path
      eligible = false
      try {
        if (binding.target === 'bond') eligible = rank >= QV2_RANK[binding.stage]
        else if (binding.target === 'fireseed') eligible = String(player.getPersistentData().getString('svs_fireseeds')).length > 0
        else if (binding.target === 'village') {
          village = qv2Village(player)
          eligible = village
        } else if (binding.target === 'dimension') eligible = qv2Dim(player.level) === binding.dimension
        else if (binding.target === 'armor_count') eligible = qv2Count(player, QV2_Armor) >= binding.count
        else if (binding.target === 'tag_count') eligible = player.inventory.count(Ingredient.of('#' + binding.tag)) >= binding.count
        else if (binding.target === 'dragon_egg') {
          for (let ei = 0; ei < QV2_Eggs.length; ei++) {
            if (player.inventory.count('saintsdragons:' + QV2_Eggs[ei] + '_egg') > 0) eligible = true
          }
        }
        if (eligible) qv2Progress(player, binding, binding.count || 1)
        else qv2Task(binding) // synchronize counters before GUI display / first death
      } catch (e) { qv2Warn('poll/' + binding.key, e) }
    }
  }
})

EntityEvents.death(event => {
  const entity = event.entity
  let killer = null, binding = null, match = false
  if (!entity || !(entity instanceof QV2_Monster)) return
  try { killer = QV2_Helper.attackerOf(event.source) } catch (e) { qv2Warn('attacker', e) }
  // Exact fatal-blow attribution; no stale last-hurt-player fallback for environmental deaths.
  if (!killer || !(killer instanceof QV2_ServerPlayer)) return
  const type = String(entity.type)
  const spore = type.indexOf('spore:') === 0
  const hunting = spore && qv2Hunting(killer)
  const bindings = global.svsQuestV2Bindings || []
  for (let bi = 0; bi < bindings.length; bi++) {
    binding = bindings[bi]
    if (binding.kind !== 'bridge') continue
    match = binding.target === 'hostile_kills' || (binding.target === 'spore_kills' && spore) ||
      (binding.target === 'spore_elite' && (type === 'spore:brute' || type === 'spore:knight')) ||
      (binding.target === 'hunting_kill' && hunting)
    if (match) qv2Progress(killer, binding, 1)
  }
})

console.info('[SVS-QV2] bridge loaded; generated bindings configure custom goals; pending victories stay closed')
