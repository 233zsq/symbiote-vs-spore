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

function applyDifficultyOne(player, tier, force) {
  // 评审修正：序章三选"选一锁二"——已选定后本人不可再改（force=控制台覆盖不受限）
  let cur = ''          // Rhino 守则：try 内不声明 const/let（第二次执行抛 redeclaration）
  try {
    cur = String(player.getPersistentData().getString('svs_difficulty'))
    if (!force && cur && cur !== tier) {
      player.tell(Text.red('难度已锁定为 ' + cur + '（序章选择不可更改）'))
      return
    }
  } catch (e) { }
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
  // event.commands = getCommands()（CommandRegistryEventJS 自带 ClassWrapper）；
  // 不要 Java.loadClass('net.minecraft.commands.Commands')——会触发 'java()' 弃用错误（实测 ×18）
  const Commands = event.commands
  const diff = Commands.literal('difficulty')
  TIERS.forEach(function (t) {
    diff.then(Commands.literal(t).executes(ctx => {
      let p = null
      let cPlayers = null       // Rhino 守则：else/try 内不声明 → 提到回调最外层（控制台全服分支）
      try { p = ctx.source.player } catch (e) { p = null }
      if (p) {
        applyDifficultyOne(p, t)
      } else {
        // 控制台执行 → 全服在线玩家
        try {
          cPlayers = ctx.source.getServer().getPlayerList().getPlayers()
          for (let i = 0; i < cPlayers.size(); i++) applyDifficultyOne(cPlayers.get(i), t, true)
        } catch (e) {
          console.error('[SVS-难度] 全服应用失败: ' + e)
        }
      }
      return 1
    }))
  })
  event.register(Commands.literal('svs').then(diff))
})
