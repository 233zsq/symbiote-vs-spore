// dump_entities.js · 进存档导出实体数值（血量/攻击/护甲），全部反射调 SRG 名
(function () {
  try {
    var ForgeRegistries = Java.loadClass("net.minecraftforge.registries.ForgeRegistries")
    var RL = Java.loadClass("net.minecraft.resources.ResourceLocation")
    var DefaultAttributes = Java.loadClass("net.minecraft.world.entity.ai.attributes.DefaultAttributes")
    var AttributeCls = Java.loadClass("net.minecraft.world.entity.ai.attributes.Attribute")
    var EntityTypeCls = Java.loadClass("net.minecraft.world.entity.EntityType")
    var ATR = ForgeRegistries.ATTRIBUTES
    var ATTR_HP = ATR.getValue(new RL("minecraft:generic.max_health"))
    var ATTR_ATK = ATR.getValue(new RL("minecraft:generic.attack_damage"))
    var ATTR_ARMOR = ATR.getValue(new RL("minecraft:generic.armor"))

        // 诊断：注册表规模 + 探针单个实体的调用链
    var esz = ForgeRegistries.ENTITY_TYPES.entrySet().size()
    console.log("[DUMP_E] SRC_SIZE=" + esz)
    try {
      var zombie = ForgeRegistries.ENTITY_TYPES.getValue(new RL("minecraft:zombie"))
      console.log("[DUMP_E] zombie=" + (zombie == null ? "null" : zombie.getClass().getName()))
      var zsup = DefaultAttributes.m_22297_(zombie)
      console.log("[DUMP_E] zombie sup=" + (zsup == null ? "null" : "ok"))
      if (zsup != null) {
        console.log("[DUMP_E] zombie hp=" + zsup.getClass().getMethod("m_22253_", AttributeCls).invoke(zsup, ATTR_HP))
      }
    } catch (e) {
      console.log("[DUMP_E] probe ERR " + e)
    }
    var rows = []
    var types = ForgeRegistries.ENTITY_TYPES.iterator()
    var cnt = 0
    while (types.hasNext()) {
      var et = types.next()
      try {
        var eid = ForgeRegistries.ENTITY_TYPES.getKey(et).toString()
        var cat = "" + et.getClass().getMethod("m_20674_").invoke(et).toString()   // getCategory
        var sup = DefaultAttributes.m_22297_(et)   // getSupplier 静态直调（NativeJavaClass 支持静态）
        if (sup == null) continue
        var sc = sup.getClass()
        var hp = sc.getMethod("m_22258_", AttributeCls).invoke(sup, ATTR_HP) ? sc.getMethod("m_22253_", AttributeCls).invoke(sup, ATTR_HP) : ""
        var atk = sc.getMethod("m_22258_", AttributeCls).invoke(sup, ATTR_ATK) ? sc.getMethod("m_22253_", AttributeCls).invoke(sup, ATTR_ATK) : ""
        var armor = sc.getMethod("m_22258_", AttributeCls).invoke(sup, ATTR_ARMOR) ? sc.getMethod("m_22253_", AttributeCls).invoke(sup, ATTR_ARMOR) : ""
        if (hp !== "") { rows.push([eid, cat, hp, atk, armor]); cnt++ }
      } catch (e) {
        if (rows.length < 4) rows.push("DBG " + eid + " " + e)
      }
    }
    for (var i = 0; i < rows.length; i++) console.log("[DUMP_E] " + rows[i].join("|"))
    console.log("[dump_entities] 共 " + cnt + " 条已入日志")
  } catch (e) {
    console.log("[dump_entities] 失败: " + e)
  }
})()
