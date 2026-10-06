// siege.js — 真菌围城 + HUD 天数计时器（魔改二期 · 决议一-1）
// 2026-10-05 村庄级共享重构（规格书_围城村庄级共享）：
//   计时从玩家 pd 迁移到主世界 level persistentData（键 svs_siege_v_<gx>_<gz>，
//   村庄身份 = 村民质心按 64 格网格量化）；多人同村共享同一倒计时（每秒只扣一次）；
//   波次生成以村民质心为圆心 32~48 格环带（村外生成向村推进）；失守判定随村庄走。
// 旧玩家 pd 键（svs_siege_*）废弃不迁移（规格书 C 节：村庄计时从零开始，旧键无害留存）。
// 2026-10-06 修正两处（test4 复盘）：① 维度判定改走 siegeDimensionId——level.dimension 是
//   ResourceKey，String() 带 "ResourceKey[...]" 包裹，旧的直比写法恒判"不在主世界"，
//   村庄从未注册过；② 回拨条件改"村庄空置间隙 > 1 分钟"——旧条件在村连续推进时每秒恒真，
//   把倒计时无限钉在 5:00，围城永不触发。
// 规格（docs/魔改设计决议.md 一-1）：① 7 天一周期；② 只在玩家于村（128 格）时走动、
//   离村/跨维度冻结；③ 回村回拨 5:00 预警；④ 不强加载；⑤ HUD 第 X 天/距围城 N 天；
//   ⑥ 失守（腰斩线）：文明 -15 + 在村者均摊罚款（单人全额）。
// 环境：KubeJS 2001.6.5 Rhino——全部声明在回调最外层（check_kubejs_rhino.py 约束）；
//   时间读法用 getDayTime()（9-30 探针实证唯一可用）；Level persistentData 走 getPersistentData()。

const SIEGE_Villager = Java.loadClass('net.minecraft.world.entity.npc.Villager')

// civillis 文明强度通道（与 fireseed.js 同一 API；独立 loadClass 避免依赖脚本加载顺序）
let SIEGE_BaseScoreApi = null
let SIEGE_BlockPos = null
try {
  SIEGE_BaseScoreApi = Java.loadClass('civil.civilization.BaseScoreApi')
  SIEGE_BlockPos = Java.loadClass('net.minecraft.core.BlockPos')
} catch (e) {
  console.warn('[SVS-围城] civillis BaseScoreApi 不可用，失守文明处罚关闭: ' + e)
}
const SIEGE_DEF_FINE_TOTAL = 40       // 失守罚款真菌残魂总额（在村玩家均摊，单人全额）
const SIEGE_DEF_SCORE = -15           // 失守文明分
const SIEGE_DEF_RANGE = 64

const SIEGE_PERIOD = 7 * 24000          // 7 个游戏日（tick）
const SIEGE_WARN = 5 * 60 * 20          // 5 分钟红色预警线（tick）
const SIEGE_RADIUS = 128                // 村庄区域半径（玩家在村判定 + 失守在场判定）
const SIEGE_MIN_VILLAGERS = 3
const SIEGE_ACTIVE_TICKS = 2 * 60 * 20  // 触发后"围城中"状态持续 2 分钟（HUD 用）
const SIEGE_GRID = 64                   // 村庄身份量化网格（格）——玩家与村民各自独立量化，对不上时以村民为准
const SIEGE_WAVE_RING_MIN = 32          // 波次环带内半径（质心起，村外）
const SIEGE_WAVE_RING_MAX = 48          // 波次环带外半径

const SIEGE_BASIC = [
  'spore:inf_human', 'spore:inf_villager', 'spore:inf_husk', 'spore:inf_pillager',
  'spore:claw', 'spore:howler', 'spore:braiomil', 'spore:conductor', 'spore:griefer', 'spore:leaper'
]
const SIEGE_ELITE = ['spore:brute', 'spore:knight', 'spore:inquisitor', 'spore:ogre', 'spore:hvindicator']
const SIEGE_ELITE_FROM_DAY = 14         // 世界第 14 天起精英掺入
const SIEGE_ELITE_RATIO = 0.2

const siegeWarned = {}
function siegeWarnOnce(tag, e) {
  if (siegeWarned[tag]) return
  siegeWarned[tag] = true
  console.warn('[SVS-围城] ' + tag + ' 失败（只提示一次）: ' + e)
}

function siegeFmt(ticks) {
  if (ticks >= 24000) return Math.ceil(ticks / 24000) + ' 天'
  const s = Math.ceil(ticks / 20)
  const m = Math.floor(s / 60)
  return m + ':' + ('0' + (s % 60)).slice(-2)
}

// 维度 id 读取（与 explorers_compass.js 同款已验收写法）：level.dimension 是 ResourceKey，
// String() 带 "ResourceKey[minecraft:dimension / ...]" 包裹，不能直接与 'minecraft:overworld' 比。
function siegeDimensionId(level) {
  let dim = level.dimension
  if (dim.location) {
    return String(dim.location())
  }
  return String(dim)
}

// ── 村庄实体（量化 key + 质心 + 村民数）───────────────────────────────────
// 村民质心按 64 格网格量化为村庄 key；玩家在村=128 格内村民 ≥3（沿旧判定）。
// 玩家的村庄 key 用"其 128 格内村民质心"计算（而非玩家自身坐标）——保证同村的
// 多个玩家算出同一 key（哪怕分立村庄两端）。
function siegeVillageOf(player) {
  let list = null
  if (siegeDimensionId(player.level) !== 'minecraft:overworld') return null
  try {
    list = player.level.getEntitiesOfClass(SIEGE_Villager, player.getBoundingBox().inflate(SIEGE_RADIUS))
  } catch (e) { siegeWarnOnce('村庄扫描', e); return null }
  const n = list ? list.size() : 0
  if (n < SIEGE_MIN_VILLAGERS) return null
  let sx = 0, sz = 0, v = null
  for (let i = 0; i < n; i++) {
    v = list.get(i)
    sx += v.x
    sz += v.z
  }
  const cx = sx / n, cz = sz / n
  return { key: 'svs_siege_v_' + Math.floor(cx / SIEGE_GRID) + '_' + Math.floor(cz / SIEGE_GRID), cx: cx, cz: cz, n: n }
}

// ── 村庄状态存取（主世界 level persistentData）────────────────────────────
// CompoundTag 键：remaining / lastTick / activeUntil / cycle / defeatDone / startVillagers
//（规格书 A.2；整村一个 CompoundTag，键名 svs_siege_v_<gx>_<gz>）
function siegeVillagePd(level) { return level.getPersistentData() }

//（siegeLoadVillage 已并入主循环的"首见村庄注册"段——村庄状态直接读写主世界 persistentData）

// ── HUD（KubeJS Painter，服务端驱动）──────────────────────────────────────
function siegeHud(player, text, color) {
  try {
    player.paint({ svs_siege: { type: 'text', text: text, x: 10, y: 10, alignX: 'left', alignY: 'top', scale: 1.0, color: color, shadow: true } })
  } catch (e) {
    siegeWarnOnce('HUD', e)   // Painter 不可用时只提示一次，机制照常
  }
}

// ── 波次生成：村民质心为圆心的村外环带（规格书 B）──────────────────────────
function siegeSpawnWave(server, cx, cz, worldDay, cycle, key) {
  const count = Math.min(8 + 2 * cycle, 20)
  const eliteOk = worldDay >= SIEGE_ELITE_FROM_DAY
  let pool = null, id = null
  const fx = Math.floor(cx), fz = Math.floor(cz)
  for (let i = 0; i < count; i++) {
    pool = (eliteOk && Math.random() < SIEGE_ELITE_RATIO) ? SIEGE_ELITE : SIEGE_BASIC
    id = pool[Math.floor(Math.random() * pool.length)]
    server.runCommandSilent('execute positioned ' + fx + ' 0 ' + fz + ' run summon ' + id + ' ~ ~ ~ {Tags:["svs_siege_wave"]}')
  }
  // 环带撒点：质心起 32~48 格（村外）地表；用 execute positioned 保证以村庄质心执行
  server.runCommandSilent('execute positioned ' + fx + ' 0 ' + fz + ' run spreadplayers ~ ~ ' + SIEGE_WAVE_RING_MIN + ' ' + SIEGE_WAVE_RING_MAX + ' false @e[tag=svs_siege_wave]')
  server.runCommandSilent('tag @e[tag=svs_siege_wave] remove svs_siege_wave')
  // 广播以质心为圆心（村内 128 格全员）
  server.runCommandSilent('execute positioned ' + fx + ' 0 ' + fz + ' run title @a[distance=..128] title {"text":"真菌围城！","color":"red","bold":true}')
  server.runCommandSilent('execute positioned ' + fx + ' 0 ' + fz + ' run title @a[distance=..128] subtitle {"text":"第 ' + (cycle + 1) + ' 波 · 守住村庄","color":"gold"}')
  console.info('[SVS-围城] ' + key + ' 触发第 ' + (cycle + 1) + ' 波围城：' + count + ' 只（世界第 ' + worldDay + ' 天，质心 ' + fx + ',' + fz + '）')
}

// ── 失守：文明扣分（质心区域）+ 在村者均摊罚款（规格书 B.3）────────────────
function siegeApplyDefeat(server, cx, cz, worldDay, key) {
  let dfMin = null, dfMax = null
  if (SIEGE_BaseScoreApi) {
    try {
      dfMin = new SIEGE_BlockPos(cx - SIEGE_DEF_RANGE, 0, cz - SIEGE_DEF_RANGE)
      dfMax = new SIEGE_BlockPos(cx + SIEGE_DEF_RANGE, 256, cz + SIEGE_DEF_RANGE)
      SIEGE_BaseScoreApi.add(server.overworld(), dfMin, dfMax, SIEGE_DEF_SCORE, 'svs_siege_defeat_' + worldDay + '_' + key)
    } catch (e) {
      console.warn('[SVS-围城] 失守文明扣分失败: ' + e)
    }
  }
  // 在场玩家 = 质心 128 格内、主世界
  const players = server.getPlayers()
  const present = []
  let p2 = null, dx = 0, dz = 0
  for (let i = 0; i < players.size(); i++) {
    p2 = players.get(i)
    if (siegeDimensionId(p2.level) !== 'minecraft:overworld') continue
    dx = p2.x - cx
    dz = p2.z - cz
    if (dx * dx + dz * dz <= SIEGE_RADIUS * SIEGE_RADIUS) present.push(p2)
  }
  const share = Math.max(1, Math.floor(SIEGE_DEF_FINE_TOTAL / Math.max(1, present.length)))
  for (let i = 0; i < present.length; i++) {
    p2 = present[i]
    server.runCommandSilent('clear ' + p2.username + ' kubejs:spore_coin ' + share)
    p2.tell(Text.darkRed('【围城失守】村庄生灵涂炭…… -' + share + ' 真菌残魂（在场均摊）'))
  }
  server.runCommandSilent('execute positioned ' + Math.floor(cx) + ' 0 ' + Math.floor(cz) + ' run title @a[distance=..128] title {"text":"村庄失守……","color":"dark_red","bold":true}')
  console.info('[SVS-围城] ' + key + ' 失守：文明 ' + SIEGE_DEF_SCORE + '，' + present.length + ' 人均摊 -' + share + ' 真菌残魂')
}

// ── 主循环（每秒）────────────────────────────────────────────────────────
let siegeTick = 0
// 循环体外声明（Rhino 循环体 const/let 重声明血泪教训）
let siegePlayer = null
let siegeNow = 0, siegeWorldDay = 1
let siegeVillage = null, siegeKey = '', siegeTag = null
let siegeRemaining = 0, siegeLast = 0, siegeCycle = 0, siegeDelta = 0
let siegeWasIn = false
let siegeStartN = 0
let siegeTraceP = null, siegeTraceV = null, siegeTraceTag = null   // TEMP-TRACE-VERIFY（验证轮读数后删）
const siegeProcessedKeys = {}   // 每秒内已处理的村庄 key（多人同村只扣一次）

ServerEvents.tick(event => {
  siegeTick++
  if (siegeTick % 20 !== 0) return          // 每秒 1 次
  const server = event.server
  if (!server) return

  try {
    // 9-30 探针实证：dayTime 属性解析成 Function（NaN 根因）、gameTime=undefined、
    // getGameTime() 不可用；可用读法是 getDayTime()。/time set 会拨动它（围城窗口内
    // 拨时间会错位一次，自愈）
    siegeNow = server.overworld().getDayTime()
    siegeWorldDay = Math.floor(siegeNow / 24000) + 1
  } catch (e) {
    siegeWarnOnce('overworld 读取', e)
    return
  }

  // 每秒重置已处理标记
  for (let k in siegeProcessedKeys) delete siegeProcessedKeys[k]

  const players = server.getPlayers()
  const overworldPd = siegeVillagePd(server.overworld())

  // TEMP-TRACE-VERIFY（验证轮读数后删）：维度原始串 + 主玩家村庄 key + 共享剩余
  if (siegeTick % 200 === 0) {
    try {
      siegeTraceP = players.size() >= 1 ? players.get(0) : null
      siegeTraceV = siegeTraceP ? siegeVillageOf(siegeTraceP) : null
      siegeTraceTag = siegeTraceV ? overworldPd.get(siegeTraceV.key) : null
      console.info('[SVS-围城][TRACE] tick=' + siegeTick + ' now=' + siegeNow + ' dimRaw=' + (siegeTraceP ? String(siegeTraceP.level.dimension) : 'n/a') + ' key=' + (siegeTraceV ? siegeTraceV.key : '无') + ' rem=' + (siegeTraceTag ? siegeTraceTag.getLong('remaining') : 'null'))
    } catch (e) { console.info('[SVS-围城][TRACE] 诊断行异常: ' + e) }
  }

  for (let i = 0; i < players.size(); i++) {
    siegePlayer = players.get(i)

    // 村庄判定（128 格内村民 ≥3 + 质心量化 key）
    siegeVillage = siegeVillageOf(siegePlayer)
    siegeKey = siegeVillage ? siegeVillage.key : ''

    if (siegeVillage && !siegeProcessedKeys[siegeKey]) {
      // ── 每村每秒只处理一次 ──
      siegeProcessedKeys[siegeKey] = true

      siegeTag = overworldPd.get(siegeKey)
      if (!siegeTag) {
        // 首见村庄：注册满周期状态（CompoundTag）
        try {
          overworldPd.put(siegeKey, new (Java.loadClass('net.minecraft.nbt.CompoundTag'))())
        } catch (e) { siegeWarnOnce('NBT 初始化', e); continue }
        siegeTag = overworldPd.get(siegeKey)
        try { siegeTag.putLong('remaining', SIEGE_PERIOD) } catch (e) {}
        try { siegeTag.putLong('lastTick', siegeNow) } catch (e) {}
        try { siegeTag.putLong('activeUntil', 0) } catch (e) {}
        try { siegeTag.putInt('cycle', 0) } catch (e) {}
        try { siegeTag.putInt('defeatDone', 0) } catch (e) {}
        try { siegeTag.putInt('startVillagers', 0) } catch (e) {}
        console.info('[SVS-围城] 新村庄注册：' + siegeKey + '（质心 ' + Math.floor(siegeVillage.cx) + ',' + Math.floor(siegeVillage.cz) + '，村民 ' + siegeVillage.n + '）')
      }

      try {
        siegeRemaining = siegeTag.getLong('remaining')
        siegeLast = siegeTag.getLong('lastTick')
        siegeCycle = siegeTag.getInt('cycle')

        // 回村回拨（规格书 A.4）：村庄空置过（lastTick 落后 gameTime 超 1 分钟）+ 剩余不足
        // 5 分钟 → 拉回 5:00 并向村内广播预警。在村连续推进时每秒间隙恒为 20 tick，
        // 必须用"大间隙"判定（旧条件 (now-last)>0 每秒恒真，倒计时被钉死在 5:00——10-06 修正）。
        if (siegeLast >= 0 && siegeRemaining < SIEGE_WARN && siegeRemaining > 0 && (siegeNow - siegeLast) > 20 * 60) {
          siegeRemaining = SIEGE_WARN
          server.runCommandSilent('execute positioned ' + Math.floor(siegeVillage.cx) + ' 0 ' + Math.floor(siegeVillage.cz) + ' run title @a[distance=..128] title {"text":"围城迫近……村庄外的孢子正在聚集","color":"red"}')
          console.info('[SVS-围城] ' + siegeKey + ' 回村回拨：剩余拉回 5:00（村庄空置 ' + (siegeNow - siegeLast) + ' tick）')
        }

        // 推进（规格书 A.3）：本 tick 该 key 未处理 → remaining -= (now - last)
        siegeDelta = siegeLast < 0 ? 20 : Math.max(0, Math.min(20 * 40, siegeNow - siegeLast))   // 首次=20；反向拨（/time set 回拨）不动；异常大跳（>40 秒）封顶
        siegeRemaining -= siegeDelta
        siegeTag.putLong('lastTick', siegeNow)

        if (siegeRemaining <= 0) {
          // ── 开波 ──
          siegeSpawnWave(server, siegeVillage.cx, siegeVillage.cz, siegeWorldDay, siegeCycle, siegeKey)
          siegeTag.putInt('cycle', siegeCycle + 1)
          siegeTag.putLong('activeUntil', siegeNow + SIEGE_ACTIVE_TICKS)
          siegeTag.putInt('startVillagers', siegeVillage.n)
          siegeTag.putInt('defeatDone', 0)
          siegeRemaining = SIEGE_PERIOD
        }
        siegeTag.putLong('remaining', siegeRemaining)
      } catch (e) {
        siegeWarnOnce('村庄状态读写（' + siegeKey + '）', e)
      }
    }

    // ── 失守判定（随村庄；每玩家检查一次该村的 defeatDone/activeUntil）──
    if (siegeVillage) {
      siegeTag = overworldPd.get(siegeKey)
      if (siegeTag) {
        try {
          if (siegeTag.getLong('activeUntil') > siegeNow && siegeTag.getInt('defeatDone') === 0) {
            siegeStartN = siegeTag.getInt('startVillagers')
            // 村民数以判定时刻该村 128 格实数为准（用当前玩家的扫描结果）
            if (siegeStartN > 0 && siegeVillage.n * 2 < siegeStartN) {
              siegeTag.putInt('defeatDone', 1)
              siegeApplyDefeat(server, siegeVillage.cx, siegeVillage.cz, siegeWorldDay, siegeKey)
            }
          }
        } catch (e) { siegeWarnOnce('失守判定（' + siegeKey + '）', e) }
      }
    }

    // ── HUD（共享值）─────────────────────────────────────────────────────
    try {
      if (siegeVillage) {
        siegeTag = overworldPd.get(siegeKey)
        if (siegeTag) {
          siegeRemaining = siegeTag.getLong('remaining')
          if (siegeTag.getLong('activeUntil') > siegeNow && siegeTag.getInt('defeatDone') === 1) {
            siegeHud(siegePlayer, '村庄失守……', 0xAA0000)
          } else if (siegeTag.getLong('activeUntil') > siegeNow) {
            siegeHud(siegePlayer, '真菌围城中！', 0xFF5555)
          } else {
            siegeHud(siegePlayer, '第 ' + siegeWorldDay + ' 天 · 距围城 ' + siegeFmt(siegeRemaining), siegeRemaining <= SIEGE_WARN ? 0xFF5555 : 0xFFFFFF)
          }
        }
      } else {
        siegeHud(siegePlayer, '第 ' + siegeWorldDay + ' 天 · 围城暂缓（离村冻结）', 0xAAAAAA)
      }
    } catch (e) {
      siegeWarnOnce('HUD 数据', e)
    }
  }
})

console.info('[SVS-围城] 村庄级共享计时已装载（64 格量化村庄身份 / 主世界 persistentData / 村外 32~48 格环带生成）')
