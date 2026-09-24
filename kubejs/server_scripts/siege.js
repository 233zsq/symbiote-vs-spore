// siege.js — 真菌围城 + HUD 天数计时器（魔改二期 · 决议一-1）
// 规格（docs/魔改设计决议.md 一-1）：
//   ① 7 天一周期，真菌怪潮冲村庄；② 倒计时只在玩家位于村庄区域（128 格）时走动，
//   离村/跨维度冻结（HUD 显示"围城暂缓"）；③ 回村时倒计时不足 5 分钟 → 回拨 5:00 红色预警；
//   ④ 怪在玩家附近自然加载区块生成，不强加载；⑤ HUD "第 X 天 / 距围城 N 天"，围城日红色。
// 落地选择：
//   - "村庄区域"判定：128 格内村民（minecraft:villager）≥ 3，且维度为主世界
//   - 倒计时：存玩家 persistentData（svs_siege_timer，tick），每玩家独立（多人各算各的）
//   - HUD：KubeJS Painter（player.paint），服务端驱动，无需客户端脚本
//   - 波次：基础池为主，世界第 14 天起掺 20% 精英（决议四 Ⅲ"围城加压"）；只生成不指路，
//     真菌怪敌对 AI 自然会扑向村庄/玩家
// TODO(K3-实测): Painter 文本属性（alignX/scale/color）以实测为准微调；波次构成待数值评审
// TODO(K3-二期后半): 失守判定与文明降级惩罚（决议一-5）未在本文件，另起脚本

const SIEGE_Villager = Java.loadClass('net.minecraft.world.entity.npc.Villager')

const SIEGE_PERIOD = 7 * 24000          // 7 个游戏日（tick）
const SIEGE_WARN = 5 * 60 * 20          // 5 分钟红色预警线（tick）
const SIEGE_RADIUS = 128                // 村庄区域半径
const SIEGE_MIN_VILLAGERS = 3
const SIEGE_ACTIVE_TICKS = 2 * 60 * 20  // 触发后"围城中"状态持续 2 分钟（HUD 用）

const SIEGE_BASIC = [
  'spore:inf_human', 'spore:inf_villager', 'spore:inf_husk', 'spore:inf_pillager',
  'spore:claw', 'spore:howler', 'spore:braiomil', 'spore:conductor', 'spore:griefer', 'spore:leaper'
]
const SIEGE_ELITE = ['spore:brute', 'spore:knight', 'spore:inquisitor', 'spore:ogre', 'spore:hvindicator']
const SIEGE_ELITE_FROM_DAY = 14         // 世界第 14 天起精英掺入
const SIEGE_ELITE_RATIO = 0.2

function siegePd(player) { return player.getPersistentData() }

function siegeInVillage(player) {
  if (String(player.level.dimension) !== 'minecraft:overworld') return false
  let n = 0
  try {
    const list = player.level.getEntitiesOfClass(SIEGE_Villager, player.getBoundingBox().inflate(SIEGE_RADIUS))
    n = list.size()
  } catch (e) { return false }
  return n >= SIEGE_MIN_VILLAGERS
}

function siegeFmt(ticks) {
  if (ticks >= 24000) return Math.ceil(ticks / 24000) + ' 天'
  const s = Math.ceil(ticks / 20)
  const m = Math.floor(s / 60)
  return m + ':' + ('0' + (s % 60)).slice(-2)
}

// 生成一波：先在玩家脚下 summon 打 tag，再 spreadplayers 撒到 24~48 格地表（自然加载区块，不落虚空），
// 最后摘掉 tag——否则下一波 spread 会把上一波还活着的怪再传送一次
function siegeSpawnWave(player, worldDay, cycle) {
  const count = Math.min(8 + 2 * cycle, 20)
  const eliteOk = worldDay >= SIEGE_ELITE_FROM_DAY
  const name = player.username
  let pool = null, id = null
  for (let i = 0; i < count; i++) {
    pool = (eliteOk && Math.random() < SIEGE_ELITE_RATIO) ? SIEGE_ELITE : SIEGE_BASIC
    id = pool[Math.floor(Math.random() * pool.length)]
    player.server.runCommandSilent(`execute at ${name} run summon ${id} ~ ~ ~ {Tags:["svs_siege_wave"]}`)
  }
  player.server.runCommandSilent(`execute at ${name} run spreadplayers ~ ~ 24 48 false @e[tag=svs_siege_wave]`)
  player.server.runCommandSilent(`tag @e[tag=svs_siege_wave] remove svs_siege_wave`)
  player.server.runCommandSilent(`execute at ${name} run title @a[distance=..128] title {"text":"真菌围城！","color":"red","bold":true}`)
  player.server.runCommandSilent(`execute at ${name} run title @a[distance=..128] subtitle {"text":"第 ${cycle + 1} 波 · 守住村庄","color":"gold"}`)
  console.info('[SVS-围城] ' + name + ' 触发第 ' + (cycle + 1) + ' 波围城：' + count + ' 只（世界第 ' + worldDay + ' 天）')
}

function siegeHud(player, text, color) {
  try {
    player.paint({ svs_siege: { type: 'text', text: text, x: 10, y: 10, alignX: 'left', alignY: 'top', scale: 1.0, color: color, shadow: true } })
  } catch (e) {
    siegeWarnOnce('HUD', e)   // Painter 不可用时只提示一次，机制照常
  }
}

const siegeWarned = {}
function siegeWarnOnce(tag, e) {
  if (siegeWarned[tag]) return
  siegeWarned[tag] = true
  console.warn('[SVS-围城] ' + tag + ' 失败（只提示一次）: ' + e)
}

let siegeTick = 0
// 循环体外声明（Rhino 循环体 const/let 重声明血泪教训，见 symbiote_counter.js 同款处理）
let siegePlayer = null, siegePd2 = null, siegeNow = 0, siegeTimer = 0
let siegeIn = false, siegeWas = false, siegeCycle = 0
ServerEvents.tick(event => {
  siegeTick++
  if (siegeTick % 20 !== 0) return          // 每秒 1 次
  if (!event.server) return
  let worldDay = 1
  let gameTime = 0
  try {
    worldDay = Math.floor(event.server.overworld().dayTime / 24000) + 1
    gameTime = event.server.overworld().gameTime
  } catch (e) {
    siegeWarnOnce('overworld 读取', e)
    return
  }

  const players = event.server.getPlayers()
  for (let i = 0; i < players.size(); i++) {
    siegePlayer = players.get(i)
    try { siegePd2 = siegePd(siegePlayer) } catch (e) { continue }
    siegeNow = gameTime

    siegeTimer = siegePd2.getInt('svs_siege_timer')
    if (siegeTimer <= 0) siegeTimer = SIEGE_PERIOD   // 首次初始化/旧档 0 值兜底（发射后立即重置回满，不会卡 0）

    siegeIn = siegeInVillage(siegePlayer)
    siegeWas = siegePd2.getBoolean('svs_siege_was_in')

    // 回村回拨：倒计时不足 5 分钟 → 拉回 5:00 并预警
    if (siegeIn && !siegeWas && siegeTimer < SIEGE_WARN && siegeTimer > 0) {
      siegeTimer = SIEGE_WARN
      siegePlayer.tell(Text.red('【围城预警】真菌躁动不安——距围城 5:00！'))
    }
    siegePd2.putBoolean('svs_siege_was_in', siegeIn)

    if (siegeIn) {
      siegeTimer -= 20                              // 每秒走 20 tick
      if (siegeTimer <= 0) {
        siegeCycle = siegePd2.getInt('svs_siege_cycle')
        siegeSpawnWave(siegePlayer, worldDay, siegeCycle)
        siegePd2.putInt('svs_siege_cycle', siegeCycle + 1)
        siegePd2.putInt('svs_siege_active_until', siegeNow + SIEGE_ACTIVE_TICKS)
        siegeTimer = SIEGE_PERIOD
      }
    }
    siegePd2.putInt('svs_siege_timer', siegeTimer)

    // HUD
    if (siegePd2.getInt('svs_siege_active_until') > siegeNow) {
      siegeHud(siegePlayer, '真菌围城中！', 0xFF5555)
    } else if (!siegeIn) {
      siegeHud(siegePlayer, '第 ' + worldDay + ' 天 · 围城暂缓（离村冻结）', 0xAAAAAA)
    } else {
      siegeHud(siegePlayer, '第 ' + worldDay + ' 天 · 距围城 ' + siegeFmt(siegeTimer), siegeTimer <= SIEGE_WARN ? 0xFF5555 : 0xFFFFFF)
    }
  }
})
