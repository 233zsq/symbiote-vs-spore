// difficulty.js — 难度三档（魔改第一期 · 规格 2）
// 命令：/svs difficulty <easy|normal|hard>（权限 2，管理员/序章任务奖励表执行）
// 落地双轨（互为备份，写失败不崩只打日志）：
//   ① GameStages（规格优先）：net.darkhax.gamestages.GameStageHelper.addStage/removeStage
//      （javap 实证 GameStages-Forge-1.20.1-15.0.2 提供该直接 API，不走命令、不猜 SRG）
//   ② Forge IForgeEntity.getPersistentData()（Forge 扩展，非 SRG）记 svs_difficulty=<档>
// 消费方（按规格，本脚本不写任何配置文件）：
//   TODO(K3): config/incontrol/spawn.json 追加规则（只动新增行）——
//     easy: 敌对生物血量×0.8、伤害×0.6；normal: 不加规则；hard: 血量×1.5、伤害×2.0；
//     玩家无 stage 时按 normal。
//     示意行（键名以 incontrol-1.20-9.5.0 实际支持为准，K3 校对后追加）：
//       { "hostile": true, "player": { "gamestage": "svs_difficulty_hard" },
//         "result": { "health_multiplier": 1.5, "damage_multiplier": 2.0 } }
//   TODO(K3): FTB Quests 序章"难度选择"三个可重复 checkmark 任务，奖励表执行本命令
//     （SNBT 由 K3 另出，本规格不含）

const STAGE_PREFIX = 'svs_difficulty_'
const TIERS = ['easy', 'normal', 'hard']

let GameStageHelper = null
try {
  GameStageHelper = Java.loadClass('net.darkhax.gamestages.GameStageHelper')
} catch (e) {
  console.error('[SVS-难度] GameStageHelper 加载失败，仅 persistentData 兜底: ' + e)
}

function applyDifficulty(target, tier) {
  const stage = STAGE_PREFIX + tier
  let count = 0
  const players = (target.getPlayers ? target.getPlayers() : java.util.Collections.singletonList(target))
  for (let i = 0; i < players.size(); i++) {
    const p = players.get(i)
    try {
      // Forge IForgeEntity.getPersistentData + 原版 CompoundTag.putString（auto-remap → SRG）
      p.getPersistentData().putString('svs_difficulty', tier)
    } catch (e) {
      console.warn('[SVS-难度] persistentData 写入失败（' + p.name + '）: ' + e)
    }
    if (GameStageHelper) {
      try {
        // 清三档旧 stage 再写新档，保证档位互斥（varargs String... 多参直传）
        GameStageHelper.removeStage(p, STAGE_PREFIX + 'easy', STAGE_PREFIX + 'normal', STAGE_PREFIX + 'hard')
        GameStageHelper.addStage(p, stage)
      } catch (e) {
        console.warn('[SVS-难度] GameStages 写入失败（' + p.name + '）: ' + e)
      }
    }
    count++
  }
  console.info('[SVS-难度] 难度已切换: ' + tier + '（stage=' + stage + '，覆盖在线玩家 ' + count + '）。敌对怪血量/伤害变化由 InControl 规则消费——验收 3 需 K3 先挂 spawn.json 规则行')
}

ServerEvents.commandRegistry(event => {
  const Commands = Java.loadClass('net.minecraft.commands.Commands')
  const diff = Commands.literal('difficulty')
  for (const t of TIERS) {
    diff.then(Commands.literal(t).executes(ctx => {
      const p = ctx.source.player
      if (p) applyDifficulty(p, t)      // 本人个人难度（多人不互扰）
      else applyDifficulty(ctx.source.getServer(), t)  // 控制台执行 → 全服
      return 1
    }))
  }
  event.register(Commands.literal('svs')
    .requires(src => src.hasPermission(2))    // 权限 2：管理员 / 任务奖励表（控制台）执行
    .then(diff))
})

// TODO(K3-可选): 新加入玩家无 stage → InControl 按 normal 兜底；如需继承当前档位，可挂
// PlayerEvents.logged_in，把 persistentData 里的 svs_difficulty 同步补成对应 stage
