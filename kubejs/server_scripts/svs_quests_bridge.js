// svs_quests_bridge.js — FTB 任务 KubeJS 桥（任务线框架规格书 v1 §1.2 检测模式三）
// 职责：系统状态类任务（FTB 原生做不了的）轮询 → /ftbquests change_progress 完成隐形任务
// ⚠️ 框架期：QUEST_TASKS 的任务 id 是占位符——用户在编辑器实装序章设计稿后，
//   把真实任务 id（章节文件里的 hex id）填进来才生效。占位期间本脚本零操作（只打一行装载日志）。
//
// 通道说明（HANDOVER 血泪教训）：
//   - 共生体阶段：SymbioteTracker.get(level).peek(player.uuid).stage（实证可用）
//   - 完成任务命令：/ftbquests change_progress <玩家> <任务id> <complete|progress> <数值>
//     【待核实：本版 FTB Quests 的命令签名——编辑器实装后用 /ftbquests change_progress 无参
//     触发命令补全确认】
// 轮询频率：每 2 秒（%40），复用 symbiote_counter.js 的节流模式，零性能开销设计。

const QB_SymbioteTracker = Java.loadClass('com.scout.symbiote.tracker.SymbioteTracker')

// ── 任务 id 配置表（占位符=待编辑器实装后回填）──────────────────────────────
// 键=桥检测 id；值={ questId: 'FTB 任务 hex id', once: true/false }
// once=true 的任务完成后写玩家 pd 标记（svs_qb_done_<桥id>）防重复结算
const QUEST_TASKS = {
  // 序章 A5.1 陨石的低语：共生体达成 ATTACHED（融合成功）即完成
  prologue_bond:      { questId: '__PLACEHOLDER_A5_1__', once: true, stage: 'ATTACHED' },
  // 阶段Ⅰ-Ⅳ 例（占位）：共生使支线的阶段攀升任务们
  symbiote_integrated: { questId: '__PLACEHOLDER__', once: true, stage: 'INTEGRATED' },
  symbiote_cooperative:{ questId: '__PLACEHOLDER__', once: true, stage: 'COOPERATIVE' },
  symbiote_dominant:  { questId: '__PLACEHOLDER__', once: true, stage: 'DOMINANT' }
}

let QB_TICK = 0
let QB_P = null
let QB_PLAYERS = null
let QB_TRACKER = null
let QB_PROF = null
let QB_STAGE = ''
let QB_TASK = null
let QB_PD = null
let QB_COMPLETED_CACHE = {}   // 任务 id → 已完成（本会话内不再发命令；跨会话靠 once 的 pd 标记）

function qbLog(msg) { console.info('[SVS-任务桥] ' + msg) }

// 共生体阶段读取（自包含，不依赖 symbiote_counter——桥脚本独立存活）
function qbBondStage(player) {
  try {
    QB_TRACKER = QB_SymbioteTracker.get(player.level)
    if (!QB_TRACKER) return null
    QB_PROF = QB_TRACKER.peek(player.uuid)
    if (QB_PROF && QB_PROF.stage) return String(QB_PROF.stage.name())
  } catch (e) { }
  return null
}

ServerEvents.tick(event => {
  QB_TICK++
  if (QB_TICK % 40 !== 0) return          // 每 2 秒
  const srv = event.server
  if (!srv) return
  QB_PLAYERS = srv.getPlayers()
  for (let i = 0; i < QB_PLAYERS.size(); i++) {
    QB_P = QB_PLAYERS.get(i)
    if (!QB_P || !QB_P.level) continue
    // 阶段类任务
    QB_STAGE = qbBondStage(QB_P)
    if (!QB_STAGE) continue
    for (let key in QUEST_TASKS) {
      QB_TASK = QUEST_TASKS[key]
      if (QB_TASK.stage !== QB_STAGE) continue
      if (!QB_TASK.questId || QB_TASK.questId.indexOf('PLACEHOLDER') >= 0) continue   // 占位符跳过
      if (QB_COMPLETED_CACHE[QB_TASK.questId]) continue
      QB_PD = QB_P.getPersistentData()
      if (QB_TASK.once) {
        try {
          if (QB_PD.getBoolean('svs_qb_done_' + key)) continue
          QB_PD.putBoolean('svs_qb_done_' + key, true)
        } catch (e) { continue }
      }
      // 完成命令（【待核实】本版 FTB 签名；占位期间不会执行到这里）
      srv.runCommandSilent('ftbquests change_progress ' + QB_P.username + ' ' + QB_TASK.questId + ' complete')
      QB_COMPLETED_CACHE[QB_TASK.questId] = true
      qbLog('阶段任务完成：' + QB_P.username + ' @ ' + key + '（' + QB_STAGE + '）→ 任务 ' + QB_TASK.questId)
    }
  }
})

qbLog('任务桥已装载（占位模式——QUEST_TASKS 待回填真实任务 id 后激活；当前 0 个生效）')
