// dump_stats.js · KubeJS startup：导出全包武器数值（攻击伤害/攻速）到 kubejs/dump_stats.json
// 运行时为 SRG 命名环境：MC 成员方法必须用 SRG 名（m_7167_ = Item.getDefaultAttributeModifiers 等）
(function () {
  var rows = []
  try {
    var ForgeRegistries = Java.loadClass("net.minecraftforge.registries.ForgeRegistries")
    var EquipmentSlot = Java.loadClass("net.minecraft.world.entity.EquipmentSlot")
    var ItemStack = Java.loadClass("net.minecraft.world.item.ItemStack")
    var RL = Java.loadClass("net.minecraft.resources.ResourceLocation")
    var ATTR_DMG = ForgeRegistries.ATTRIBUTES.getValue(new RL("minecraft:generic.attack_damage"))
    var ATTR_SPD = ForgeRegistries.ATTRIBUTES.getValue(new RL("minecraft:generic.attack_speed"))

    rows.push("===WEAPONS===")
    var items = ForgeRegistries.ITEMS.iterator()
    var cnt = 0
    while (items.hasNext()) {
      var item = items.next()
      try {
        var id = ForgeRegistries.ITEMS.getKey(item).toString()
        var mods = item.getClass().getMethod("getAttributeModifiers", EquipmentSlot, ItemStack).invoke(item, EquipmentSlot.MAINHAND, new ItemStack(item))   // IForgeItem.getAttributeModifiers（Forge 有效值）
        if (mods == null || mods.isEmpty()) continue
        var dmg = null, spd = null
        var it = mods.entries().iterator()
        while (it.hasNext()) {
          var en = it.next()
          var val = en.getValue().getClass().getMethod("m_22218_").invoke(en.getValue())  // AttributeModifier.getAmount
          if (en.getKey().equals(ATTR_DMG)) dmg = val
          if (en.getKey().equals(ATTR_SPD)) spd = val
        }
        if (dmg != null && dmg > 0) {
          rows.push([id, dmg, spd == null ? "" : spd])
          cnt++
        }
      } catch (e) {
        if (cnt == 0 && rows.length < 6) rows.push("DBG " + e)
      }
    }
    rows.push("武器条数: " + cnt)
    // 探针：点名已知模组武器看反射通不通
    var probes = ["simplyswords:iron_longsword", "wom:ruine", "efn:yamato_dmc_in_sheath", "cataclysm:the_incinerator", "twilightforest:ironwood_sword", "tconstruct:cleaver", "spore:saber"]
    for (var pi = 0; pi < probes.length; pi++) {
      try {
        var pit = ForgeRegistries.ITEMS.getValue(new RL(probes[pi]))
        if (pit == null) { rows.push("PROBE " + probes[pi] + " -> 注册表无此物"); continue }
        var pm = pit.getClass().getMethod("getAttributeModifiers", EquipmentSlot, ItemStack).invoke(pit, EquipmentSlot.MAINHAND, new ItemStack(pit))
        var pd = null
        var keys = []
        var pit2 = pm.entries().iterator()
        while (pit2.hasNext()) {
          var pen = pit2.next()
          keys.push("" + pen.getKey())
          if (pen.getKey().equals(ATTR_DMG)) pd = pen.getValue().getClass().getMethod("m_22218_").invoke(pen.getValue())
        }
        rows.push("PROBE " + probes[pi] + " -> dmg=" + pd + " | keys=" + keys.join(","))
      } catch (e) {
        rows.push("PROBE " + probes[pi] + " -> ERR " + e)
      }
    }
  } catch (e) {
    rows.push("FATAL " + e)
  }
  // JsonIO 落盘不可靠（类过滤器/路径解析坑），直接打日志，由外部采集
  for (var i = 0; i < rows.length; i++) console.log("[DUMP_W] " + rows[i])
  console.log("[dump_stats] 共 " + rows.length + " 行已入日志")
})()
