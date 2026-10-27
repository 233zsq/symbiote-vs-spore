"""Read generated Anvil chunks and render a real top-down map; never edits saves.

Requires numpy and Pillow. Run after save-all flush or after stopping the server.
"""
from __future__ import annotations
import argparse
from collections import Counter
import io
import json
from pathlib import Path
import struct
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".map-work"
STEP = 4


class NBT:
    def __init__(self, raw):
        self.stream = io.BytesIO(raw)

    def number(self, fmt):
        return struct.unpack(">" + fmt, self.stream.read(struct.calcsize(fmt)))[0]

    def string(self):
        return self.stream.read(self.number("H")).decode("utf-8")

    def payload(self, tag):
        if tag in (1, 2, 3, 4, 5, 6):
            return self.number({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[tag])
        if tag == 7:
            return self.stream.read(self.number("i"))
        if tag == 8:
            return self.string()
        if tag == 9:
            child, size = self.number("B"), self.number("i")
            return [self.payload(child) for _ in range(size)]
        if tag == 10:
            result = {}
            while True:
                child = self.number("B")
                if child == 0:
                    return result
                name = self.string()
                result[name] = self.payload(child)
        if tag in (11, 12):
            size = self.number("i")
            width = 4 if tag == 11 else 8
            return np.frombuffer(self.stream.read(size * width), dtype=">i4" if tag == 11 else ">i8")
        raise ValueError("Unsupported NBT tag " + str(tag))

    def root(self):
        tag = self.number("B")
        self.string()
        return self.payload(tag)


def chunks(folder):
    for path in sorted(folder.glob("r.*.*.mca")):
        raw = path.read_bytes()
        for slot in range(1024):
            address = int.from_bytes(raw[slot * 4:slot * 4 + 3], "big") * 4096
            if not address:
                continue
            length = int.from_bytes(raw[address:address + 4], "big")
            compression = raw[address + 4]
            data = raw[address + 5:address + 4 + length]
            if compression == 2:
                data = zlib.decompress(data)
            elif compression != 3:
                raise ValueError(f"Unsupported compression {compression} in {path}")
            yield NBT(data).root()


def packed_value(data, index, bits):
    per_long = 64 // bits
    word = int(data[index // per_long]) & ((1 << 64) - 1)
    return (word >> ((index % per_long) * bits)) & ((1 << bits) - 1)


def block_at(chunk, x, y, z):
    for section in chunk.get("sections", []):
        if section["Y"] != y // 16 or "block_states" not in section:
            continue
        states = section["block_states"]
        palette = states["palette"]
        index = (y % 16) * 256 + z * 16 + x
        p = 0 if len(palette) == 1 else packed_value(states["data"], index, max(4, (len(palette) - 1).bit_length()))
        return palette[p]["Name"]
    return "minecraft:air"


def color(name):
    if "water" in name or "bubble_column" in name:
        return (47, 104, 139)
    if "lava" in name:
        return (213, 91, 40)
    if any(x in name for x in ["snow", "ice"]):
        return (210, 224, 222)
    if any(x in name for x in ["sand", "terracotta"]):
        return (190, 165, 111)
    if any(x in name for x in ["stone", "deepslate", "gravel", "andesite", "granite"]):
        return (115, 119, 109)
    if any(x in name for x in ["path", "dirt", "mud", "podzol"]):
        return (132, 112, 77)
    if any(x in name for x in ["planks", "log", "wood", "fence"]):
        return (158, 123, 76)
    if "spore:" in name:
        return (110, 83, 105)
    return (99, 137, 78)


def font(size):
    for path in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", type=Path, default=WORK / "server/svs_first_light_v1")
    args = parser.parse_args()
    plan = json.loads((ROOT / "maps/first-light-v1/plan.json").read_text(encoding="utf-8"))
    if (WORK / "layout.json").exists():
        plan = json.loads((WORK / "layout.json").read_text(encoding="utf-8"))
    size, half = plan["size"], plan["size"] // 2
    h = np.full((size // STEP, size // STEP), -999, dtype=np.int16)
    rgb = np.zeros((*h.shape, 3), dtype=np.uint8)
    statuses, structures, entities, blocks = Counter(), Counter(), Counter(), Counter()
    road_requests = {}
    road_checks, road_missing = Counter(), []
    bed_checks, bed_missing = 0, []
    site_blocks = {s["id"]: Counter() for s in plan["sites"]}
    site_materials = {s["id"]: set() for s in plan["sites"]}
    for route, points in plan.get("paths", {}).items():
        for px, yy, pz in points:
            road_requests.setdefault((px//16, pz//16), []).append((route, px, yy, pz))
    home = next(s for s in plan["sites"] if s["id"] == "home")
    beds = []
    if "y" in home:
        for hx, hz in [(-15, -14), (6, -14), (-15, 6)]:
            for dx in [2, 3]:
                for dz in [3, 5]:
                    beds.append((home["x"]+hx+dx, home["y"], home["z"]+hz+dz))
    inside = 0
    site_samples = {}
    for chunk in chunks(args.world / "region"):
        cx, cz = chunk["xPos"], chunk["zPos"]
        if not (-half <= cx * 16 < half and -half <= cz * 16 < half):
            continue
        inside += 1
        statuses[chunk["Status"]] += 1
        for key, start in chunk.get("structures", {}).get("starts", {}).items():
            if start.get("id") != "INVALID":
                structures[key] += 1
        for entity in chunk.get("block_entities", []):
            blocks[entity.get("id", "unknown")] += 1
            for site in plan["sites"]:
                if abs(entity.get("x", 99999)-site["x"]) <= 128 and abs(entity.get("z", 99999)-site["z"]) <= 128:
                    site_blocks[site["id"]][entity.get("id", "unknown")] += 1
        for site in plan["sites"]:
            if abs(cx*16-site["x"]) <= 80 and abs(cz*16-site["z"]) <= 80:
                for section in chunk.get("sections", []):
                    for entry in section.get("block_states", {}).get("palette", []):
                        if not entry["Name"].startswith("minecraft:"):
                            site_materials[site["id"]].add(entry["Name"])
        for route, px, yy, pz in road_requests.get((cx, cz), []):
            if any(block_at(chunk, px % 16, sy, pz % 16) in {"minecraft:gravel", "minecraft:oak_planks", "minecraft:coarse_dirt"} for sy in range(yy-2, yy+3)):
                road_checks[route] += 1
            else:
                road_missing.append([route, px, yy, pz])
        for bx, by, bz in beds:
            if bx//16 == cx and bz//16 == cz:
                if block_at(chunk, bx % 16, by, bz % 16) == "minecraft:white_bed":
                    bed_checks += 1
                else:
                    bed_missing.append([bx, by, bz])
        heightmap = chunk.get("Heightmaps", {}).get("MOTION_BLOCKING_NO_LEAVES")
        if heightmap is None:
            continue
        for z in range(0, 16, STEP):
            for x in range(0, 16, STEP):
                y = packed_value(heightmap, z * 16 + x, 9) - 65
                gx, gz = (cx * 16 + x + half) // STEP, (cz * 16 + z + half) // STEP
                h[gz, gx] = y
                rgb[gz, gx] = color(block_at(chunk, x, y, z))
        for site in plan["sites"]:
            if site["x"] // 16 == cx and site["z"] // 16 == cz:
                x, z = site["x"] % 16, site["z"] % 16
                y = packed_value(heightmap, z * 16 + x, 9) - 65
                site_samples[site["id"]] = {"x": site["x"], "z": site["z"], "surface_y": y, "block": block_at(chunk, x, y, z)}
    residents = 0
    if (args.world / "entities").is_dir():
        for chunk in chunks(args.world / "entities"):
            for entity in chunk.get("Entities", []):
                entities[entity.get("id", "unknown")] += 1
                if "svs_map_resident" in entity.get("Tags", []):
                    residents += 1
    out = ROOT / "artifacts/maps"
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(WORK / "terrain.npz", height=h, color=rgb)
    report = {"inside_chunks": inside, "expected_chunks": (size // 16) ** 2,
              "statuses": dict(statuses), "sampled_columns": int((h != -999).sum()),
              "sites": site_samples, "natural_structure_starts": dict(structures),
              "block_entities": dict(blocks), "entities": dict(entities),
              "site_block_entities": {k: dict(v) for k, v in site_blocks.items()},
              "site_modded_palette_entries": {k: sorted(v) for k, v in site_materials.items()},
              "road_checks": dict(road_checks), "road_missing": road_missing,
              "bed_parts_checked": bed_checks, "bed_parts_missing": bed_missing,
              "map_residents": residents}
    (out / "world-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    safe_h = np.where(h == -999, 63, h).astype(float)
    dz, dx = np.gradient(safe_h)
    shade = np.clip(1.0 - dx * 0.045 - dz * 0.075, 0.64, 1.27)
    shaded = np.clip(rgb.astype(float) * shade[:, :, None], 0, 255).astype(np.uint8)
    image = Image.new("RGB", (1120, 1260), "#f2eddf")
    image.paste(Image.fromarray(shaded).resize((1024, 1024), Image.Resampling.NEAREST), (48, 112))
    draw = ImageDraw.Draw(image)
    draw.text((48, 25), plan["name"], font=font(34), fill="#243831")
    draw.text((50, 72), f"实生成地形 · 2048 × 2048 · Terralith 2.5.4 · seed {plan['seed']}", font=font(19), fill="#526054")
    sites = {s["id"]: s for s in plan["sites"]}
    def point(site):
        return (48 + (site["x"] + half) / 2, 112 + (site["z"] + half) / 2)
    for route in plan["routes"]:
        road = plan.get("paths", {}).get(route["id"])
        route_points = [(48+(p[0]+half)/2, 112+(p[2]+half)/2) for p in road] if road else [point(sites[route["from"]]), point(sites[route["to"]])]
        draw.line(route_points, fill="#e9b369", width=4)
    for i, site in enumerate(plan["sites"], 1):
        x, z = point(site)
        draw.ellipse((x-8, z-8, x+8, z+8), fill="#f3d6a0", outline="#243831", width=3)
        draw.text((x+14, z-16), f"{i}  {site['name']}", font=font(20), fill="#172b27", stroke_width=2, stroke_fill="#f2eddf")
    draw.text((50, 1160), "北 ↑   金线为制作路线；以存档中的路标与实际道路为准。", font=font(21), fill="#34483e")
    draw.text((50, 1200), "地图小样；FTB主线、整包平衡与玩家战斗验收尚未接入。", font=font(19), fill="#667365")
    image.save(out / "svs-first-light-v1-preview.png")
    print(json.dumps({k: report[k] for k in ["inside_chunks", "statuses", "sampled_columns", "sites", "road_checks", "bed_parts_checked", "map_residents"]}, ensure_ascii=False, indent=2))
    print("Missing road points:", len(road_missing), "Missing bed parts:", len(bed_missing))


if __name__ == "__main__":
    main()
