// fireseed.js · 火种绑定系统（任务文档第 3 条 / 魔改设计决议）
// 机制：
//   右键村民（手持 kubejs:fireseed_token）→ 绑定为火种（改名"火种"），消耗 1 工具，
//   立刻获得该村民当前最贵可交易物品 ×1（职业等级越高奖励越肥的落地件）
//   每人最多绑定 5 个火种；绑定记录存玩家 persistentData（id|毫秒 时间戳，id=玩家name+时间戳）
//   火种村民死亡 → 扣绑定者真菌币（连续死亡递减 100%/50%/25%…）；绑定者不在线 → 文明度 -10（civillis BaseScoreApi）
//   绑定者超过 7 天未上线 → 登录时自动解绑（文明不降级）
//   文明强度（决议一-2）：绑定 → 村民周边 ±64 格 +5 分；死亡/解绑 → 撤分
// 多人/经济逻辑，K3 亲写（分工规则）。数值为初版默认，实测可调。
// 已知简化（TODO）：绑定期奖励只发一次；文明分区域为村民位置 ±64 近似，未对齐城镇中心实际边界。

const FS_TOKEN = 'kubejs:fireseed_token'
const FS_COIN = 'kubejs:spore_coin'
const FS_MAX = 5
const FS_PENALTY_BASE = 20          // 首次死亡扣 20 真菌币，之后 50%/25% 递减
const FS_OFFLINE_DAYS = 7
const FS_VILLAGER = 'minecraft:villager'

function fsLog(msg) { console.info('[SVS-火种] ' + msg) }
function fsTell(player, msg) {
  try { player.statusMessage = Text.of(msg) } catch (e) { }
}

// 绑定记录：persistentData.svs_fireseeds = "uuid|ms;uuid|ms;..."
function fsLoad(player) {
  let raw = ''
  try { raw = player.getPersistentData().getString('svs_fireseeds') } catch (e) { return [] }
  if (!raw) return []
  return raw.split(';').filter(s => s.indexOf('|') > 0)
}
function fsSave(player, list) {
  try { player.getPersistentData().putString('svs_fireseeds', list.join(';')) } catch (e) { }
}
function fsNowMs() {
  return String(Java.loadClass('java.lang.System').currentTimeMillis())
}

// ── civillis 文明强度挂钩（BaseScoreApi 公开静态方法，反编译实证）──
// 绑定 → 村民周边 ±64 格区域 +5 分（sourceKey=svs_fireseed_<村民uuid>）；
// 死亡/解绑 → remove(sourceKey) 撤分；绑定者离线死亡 → 另加 -10 分区（决议一-5 文明小幅下降）
const FS_SCORE_BIND = 5
const FS_SCORE_DEAD = -10
const FS_SCORE_RANGE = 64
let FS_BaseScoreApi = null
let FS_BlockPos = null
try {
  FS_BaseScoreApi = Java.loadClass('civil.civilization.BaseScoreApi')
  FS_BlockPos = Java.loadClass('net.minecraft.core.BlockPos')
} catch (e) {
  console.warn('[SVS-火种] civillis BaseScoreApi 不可用，文明强度挂钩关闭: ' + e)
}
function fsScoreKey(uuid) { return 'svs_fireseed_' + uuid }
function fsScoreAdd(entity, value, key) {
  if (!FS_BaseScoreApi) return
  // Rhino 守则：try/if 等块内不声明 const/let（第二次执行抛 redeclaration）→ 声明提前
  let px = 0, py = 0, pz = 0, pMin = null, pMax = null
  try {
    px = entity.x; py = entity.y; pz = entity.z
    pMin = new FS_BlockPos(px - FS_SCORE_RANGE, py - 32, pz - FS_SCORE_RANGE)
    pMax = new FS_BlockPos(px + FS_SCORE_RANGE, py + 32, pz + FS_SCORE_RANGE)
    FS_BaseScoreApi.add(entity.level, pMin, pMax, value, key)
  } catch (e) {
    fsLog('文明强度写入失败(' + key + '): ' + e)
  }
}
function fsScoreRemove(key) {
  if (!FS_BaseScoreApi) return
  try { FS_BaseScoreApi.remove(key) } catch (e) {
    fsLog('文明强度移除失败(' + key + '): ' + e)
  }
}

// 取村民当前最贵可交易物品（按买价总数量估价），返回结果物品或 null
function fsPriciestWare(villager) {
  // Rhino 守则：块内不声明——本函数每个村民调一次，第二次执行即抛 redeclaration
  // （曾会让"绑定即送最贵交易物"从第 2 个火种起静默失效）
  let offers = null, best = null, bestCost = -1
  let o = null, a = null, b = null, cost = 0
  try {
    offers = villager.getOffers()
    for (let i = 0; i < offers.size(); i++) {
      o = offers.get(i)
      a = o.getCostA()
      b = o.getCostB()
      cost = (a ? a.getCount() : 0) + (b ? b.getCount() : 0)
      if (cost > bestCost) { bestCost = cost; best = o.getResult() }
    }
    return best
  } catch (e) {
    fsLog('读取村民交易失败: ' + e)
    return null
  }
}

// ── 绑定（右键实体）─────────────────────────────────────────────────────────
ItemEvents.entityInteracted(event => {
  const player = event.player
  const target = event.target ? event.target : event.entity
  if (!player || !player.player || !target) return
  if (String(target.type) !== FS_VILLAGER) return
  const item = event.item
  if (!item || String(item.id) !== FS_TOKEN) return

  // 已绑定判定（村民侧标记）
  try {
    if (target.getPersistentData().getString('svs_fireseed_owner')) {
      fsTell(player, '§e该村民已是火种，无需重复绑定。')
      return
    }
  } catch (e) { }

  // 数量上限（评审修正：不再按绑定时间戳过滤——7 天判定的是"绑定者离线时长"，
  // 见 loggedIn/loggedOut 钩子；天天上线的玩家不应被解绑）
  let list = fsLoad(player)
  if (list.length >= FS_MAX) {
    fsTell(player, '§c火种已达上限（' + FS_MAX + '）。老火种死亡或你连续 ' + FS_OFFLINE_DAYS + ' 天未上线才会腾出名额。')
    return
  }

  // 消耗工具
  try { item.shrink(1) } catch (e) {
    try { player.mainHandItem.count = player.mainHandItem.count - 1 } catch (e2) { }
  }

  // 标记村民 + 改名
  // 火种 ID 用自发标识（玩家 name + 时间戳）：原版继承方法 getUUID 在本环境 Rhino 里
  // 连 ServerPlayer 都解析失败（9-26 实测 'Cannot find function getUUID' ×8），不能拿它当键；
  // player.name 已实证可用（日志打印 literal{Ultraman_0}）
  const uuid = String(player.name) + '_' + fsNowMs()
  try {
    target.getPersistentData().putString('svs_fireseed_owner', String(player.name))
    target.getPersistentData().putString('svs_fireseed_id', uuid)
  } catch (e) { }
  try { player.getPersistentData().putString('svs_fireseed_streak', '0') } catch (e) { }   // 新绑定=好消息，递减重置
  try {
    target.setCustomName(Text.of('火种'))
    target.setCustomNameVisible(true)
  } catch (e) { }

  list.push(uuid + '|' + fsNowMs())
  fsSave(player, list)

  // 文明强度 +N（绑定即加分，区域 = 村民周边）
  fsScoreAdd(target, FS_SCORE_BIND, fsScoreKey(uuid))

  // 奖励：该村民当前最贵可交易物品 ×1
  const ware = fsPriciestWare(target)
  if (ware && !ware.isEmpty()) {
    try { player.give(ware.copy()) } catch (e) { player.give(Item.of(ware)) }
    fsTell(player, '§a火种已绑定！献上村民压箱底的宝贝：§6' + String(ware.id))
  } else {
    fsTell(player, '§a火种已绑定！（该村民暂无可交易物品，奖励跳过）')
  }
  fsLog('绑定: ' + player.name + ' <- 村民 ' + uuid + '（当前 ' + list.length + '/' + FS_MAX + '）')
})

// ── 死亡惩罚（真菌币递减）───────────────────────────────────────────────────
EntityEvents.death(event => {
  const mob = event.entity
  if (!mob || String(mob.type) !== FS_VILLAGER) return
  let ownerUuid = ''
  let releaseList = null      // Rhino 守则：块（try）内不声明，提到回调最外层
  try { ownerUuid = mob.getPersistentData().getString('svs_fireseed_owner') } catch (e) { return }
  if (!ownerUuid) return

  // 火种熄灭：绑定带来的文明加分先撤掉（在线离线都撤）
  // 村民标识读回绑定时写入的 svs_fireseed_id（不用 getUUID，见绑定处注释）
  let mobUuid = ''
  try { mobUuid = String(mob.getPersistentData().getString('svs_fireseed_id')) } catch (e) { }
  if (mobUuid) fsScoreRemove(fsScoreKey(mobUuid))

  // 连续死亡递减（绑定者侧 streak，跨火种累计；0=首死全额 / 1=50% / >=2=25%）

  // 找绑定者（在线才扣钱；离线 → 文明度处罚）
  // ownerUuid 是绑定时写入的 String(player.name)（见绑定处注释，getUUID 不可用）
  const players = event.server.getPlayers()
  let owner = null
  for (let i = 0; i < players.size(); i++) {
    if (String(players.get(i).name) === ownerUuid) { owner = players.get(i); break }
  }
  if (!owner) {
    // 绑定者离线 → 村庄文明等级小幅下降（决议一-5）：死亡点区域追加负分区
    fsScoreAdd(mob, FS_SCORE_DEAD, 'svs_fireseed_dead_' + mobUuid)
    fsLog('火种死亡（绑定者离线，文明度 ' + FS_SCORE_DEAD + '）: ' + ownerUuid)
    return
  }

  let streak = 0
  try { streak = parseInt(owner.getPersistentData().getString('svs_fireseed_streak'), 10) || 0 } catch (e) { }
  let mult = 1.0
  if (streak === 1) mult = 0.5
  else if (streak >= 2) mult = 0.25
  const penalty = Math.max(1, Math.round(FS_PENALTY_BASE * mult))

  // 扣真菌币（/clear 上限语义：最多清 penalty 枚，不足全扣）
  try {
    event.server.runCommandSilent('clear ' + owner.name + ' ' + FS_COIN + ' ' + penalty)
    try { owner.getPersistentData().putString('svs_fireseed_streak', String(streak + 1)) } catch (e) { }
    fsTell(owner, '§c你的火种阵亡了！§4-' + penalty + ' 真菌币§c（连续第 ' + (streak + 1) + ' 次，惩罚递减）')
  } catch (e) {
    fsLog('扣款失败: ' + e)
  }

  // 名额释放 + streak 递进（用玩家记录留存 streak 以支持跨村民递减？初版按村民独立计）
  try {
    releaseList = fsLoad(owner).filter(function (e2) { return e2.split('|')[0] !== mobUuid })
    fsSave(owner, releaseList)
  } catch (e) { }
  fsLog('火种阵亡: ' + owner.name + ' <- 村民 ' + mobUuid + ' 扣 ' + penalty)
})

// ── 7 天未上线自动解绑（登录时清理）──────────────────────────────────────────
// ── 7 天未上线自动解绑（决议一-5："绑定者 7 天未上线"——按离线时长，不按绑定时长）──
// loggedOut 记下线时刻；loggedIn 算离线时长，超 7 天 → 全部火种熄灭（撤文明加分）
PlayerEvents.loggedOut(event => {
  try { event.player.getPersistentData().putString('svs_fs_last_logout', fsNowMs()) } catch (e) { }
})
PlayerEvents.loggedIn(event => {
  const player = event.player
  if (!player) return
  const list = fsLoad(player)
  if (list.length === 0) return
  let lastMs = 0
  try { lastMs = parseInt(player.getPersistentData().getString('svs_fs_last_logout'), 10) || 0 } catch (e) { }
  if (lastMs <= 0) return                       // 首次登录/无记录，不清
  const offlineMs = Date.now() - lastMs
  if (offlineMs < FS_OFFLINE_DAYS * 86400000) return
  // 解绑全部 + 撤文明加分（remove 只需 key，无需村民坐标）
  let dropped = null
  for (let i = 0; i < list.length; i++) {
    dropped = list[i]
    fsScoreRemove(fsScoreKey(dropped.split('|')[0]))
  }
  fsSave(player, [])
  fsTell(player, '§7久违了……§8有 ' + list.length + ' 个火种因你连续 ' + FS_OFFLINE_DAYS + ' 天未归而熄灭。')
})
