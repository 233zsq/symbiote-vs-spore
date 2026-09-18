// bloodandmadness_fix.js — Blood and Madness 吸脑怪（Brainsucker）崩溃热修
// 病因（字节码实证，javap 扫 jar 内 179 个类）：Brainsucker.positionRider(Entity, MoveFunction)
// 体内调用 super.positionRider(Entity)，而原版单参 positionRider 又会虚调回双参版本，
// 形成无限递归 → StackOverflowError 崩服。它的抓取技会让玩家骑乘它，被抓即必崩。
// 全 jar 仅此一个类带此缺陷，故只禁用这一种生物，等作者修复后再放开。
// 三层拦截：① 生成期取消（自然/刷怪笼/结构生成）② 入世界即移除（覆盖 /summon 与
// 旧存档磁盘加载，可救回已被抓崩的存档）③ 生成开关见 config/bloodandmadness-common.toml
EntityEvents.checkSpawn('bloodandmadness:brainsucker', event => {
  event.cancel()
})

EntityEvents.spawned(event => {
  if (event.entity.type === 'bloodandmadness:brainsucker') {
    event.entity.discard()
  }
})
