package com.svs.tweak.structure;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.ArrayList;
import java.util.List;

/**
 * 结构密度记录（每维度一份 SavedData）：chunkKey → 该区块已生成的结构 id 列表。
 * 只进不出——已生成的结构永久占坑，保证"75 格最多 1 个"对历史区块同样成立。
 */
public class StructureDensityData extends SavedData {
    private static final String DATA_NAME = "svs_structure_density";

    private final CompoundTag byChunk = new CompoundTag();

    public static StructureDensityData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(StructureDensityData::load, StructureDensityData::new, DATA_NAME);
    }

    public static StructureDensityData load(CompoundTag tag) {
        StructureDensityData d = new StructureDensityData();
        for (String k : tag.getAllKeys()) {
            d.byChunk.put(k, tag.getList(k, Tag.TAG_STRING));
        }
        return d;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        for (String k : byChunk.getAllKeys()) {
            tag.put(k, byChunk.getList(k, Tag.TAG_STRING));
        }
        return tag;
    }

    private static String key(int chunkX, int chunkZ) {
        return chunkX + "," + chunkZ;
    }

    /** 半径内的结构记录数 */
    public int countNearby(int chunkX, int chunkZ, int radius) {
        int n = 0;
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                ListTag l = byChunk.getList(key(chunkX + dx, chunkZ + dz), Tag.TAG_STRING);
                n += l.size();
            }
        }
        return n;
    }

    public void record(int chunkX, int chunkZ, String structureId) {
        String k = key(chunkX, chunkZ);
        ListTag l = byChunk.getList(k, Tag.TAG_STRING);
        if (l.isEmpty()) {
            l = new ListTag();
        } else {
            // 防重复记录（checkStart 会被反复调用）
            for (Tag t : l) {
                if (t.getAsString().equals(structureId)) return;
            }
            ListTag copy = new ListTag();
            copy.addAll(l);
            l = copy;
        }
        l.add(StringTag.valueOf(structureId));
        byChunk.put(k, l);
        setDirty();
    }

    /** 调试用：总记录数 */
    public int totalRecords() {
        int n = 0;
        for (String k : byChunk.getAllKeys()) {
            n += byChunk.getList(k, Tag.TAG_STRING).size();
        }
        return n;
    }

    public List<String> debugDump() {
        List<String> out = new ArrayList<>();
        for (String k : byChunk.getAllKeys()) {
            out.add(k + " -> " + byChunk.getList(k, Tag.TAG_STRING));
        }
        return out;
    }
}
