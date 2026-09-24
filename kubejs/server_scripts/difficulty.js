// difficulty.js — 难度三档（魔改第一期 · 规格 2，K3 修订：个人难度，多人不互扰）
// 命令：/svs difficulty <easy|normal|hard>
// 本人执行 → 只改自己（FTB 序章任务奖励即此路径）；控制台执行 → 全服玩家
const STAGE_PREFIX = 'svs_difficulty_'
const TIERS = ['easy', 'normal', 'hard']

let GameStageHelper = null
try {
  GameStageHelper = Java.loadClass('net.darkhax.gamestages.GameStageHelper')
} catch (e) {
  console.error('[SVS-难度] GameStageHelper 加载失败，仅 persistentData 兜底: ' + e)
}

function applyDifficultyOne(player, tier) {
  const stage = STAGE_PREFIX + tier
  try { player.getPersistentData().putString('svs_difficulty', tier) } catch (e) { }
  if (GameStageHelper) {
    try {
      GameStageHelper.removeStage(player, STAGE_PREFIX + 'easy', STAGE_PREFIX + 'normal', STAGE_PREFIX + 'hard')
      GameStageHelper.addStage(player, stage)
    } catch (e) {
      console.warn('[SVS-难度] GameStages 写入失败（' + player.name + '）: ' + e)
    }
  }
  try { player.tell(Text.of('难度已切换为：' + tier)) } catch (e) { }
  console.info('[SVS-难度] ' + player.name + ' -> ' + tier)
}

ServerEvents.commandRegistry(event => {
  const Commands = Java.loadClass('net.minecraft.commands.Commands')
  const diff = Commands.literal('difficulty')
  for (const t of TIERS) {
    diff.then(Commands.literal(t).executes(ctx => {
      let p = null
      try { p = ctx.source.player } catch (e) { p = null }
      if (p) {
        applyDifficultyOne(p, t)
      } else {
        // 控制台执行 → 全服在线玩家
        try {
          const players = ctx.source.getServer().getPlayerList().getPlayers()
          for (let i = 0; i < players.size(); i++) applyDifficultyOne(players.get(i), t)
        } catch (e) {
          console.error('[SVS-难度] 全服应用失败: ' + e)
        }
      }
      return 1
    }))
  }
  event.register(Commands.literal('svs').then(diff))
})
