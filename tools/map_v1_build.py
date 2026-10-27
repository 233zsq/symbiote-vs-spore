"""Fit the v1 layout to sampled terrain and emit explicit, one-shot build jobs.

No load/tick hooks are installed. Requires numpy; reads .map-work/terrain.npz.
"""
from __future__ import annotations
import heapq
import json
import math
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".map-work"
SOURCE = ROOT / "maps/first-light-v1"


def line(a, b):
    steps = max(abs(b[0]-a[0]), abs(b[1]-a[1]))
    return [(round(a[0]+(b[0]-a[0])*t/max(1, steps)), round(a[1]+(b[1]-a[1])*t/max(1, steps))) for t in range(steps+1)]


def astar(h, water, start, end):
    queue, cost, previous = [(0, start)], {start: 0.0}, {}
    while queue:
        _, node = heapq.heappop(queue)
        if node == end:
            path = [node]
            while node in previous:
                node = previous[node]
                path.append(node)
            return path[::-1]
        x, z = node
        for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nxt = (x+dx, z+dz)
            nx, nz = nxt
            if not (8 <= nx < h.shape[1]-8 and 8 <= nz < h.shape[0]-8):
                continue
            slope = abs(int(h[nz, nx])-int(h[z, x]))
            value = cost[node] + 1 + slope * 6 + slope*slope + (80 if water[nz, nx] else 0)
            if value < cost.get(nxt, float("inf")):
                cost[nxt] = value
                previous[nxt] = node
                heapq.heappush(queue, (value + abs(nx-end[0])+abs(nz-end[1]), nxt))
    raise ValueError("No route found")


def sign(x, y, z, texts):
    messages = ",".join("'"+json.dumps({"text": t}, ensure_ascii=False, separators=(",", ":"))+"'" for t in texts)
    return f"setblock {x} {y} {z} minecraft:oak_sign[rotation=0]{{front_text:{{messages:[{messages}]}}}}"


def main():
    plan = json.loads((SOURCE / "plan.json").read_text(encoding="utf-8"))
    terrain = np.load(WORK / "terrain.npz")
    raw_h, rgb = terrain["height"], terrain["color"]
    if np.any(raw_h == -999):
        raise ValueError("Terrain sampling is incomplete; finish pre-generation first")
    padded = np.pad(raw_h, 2, mode="edge")
    h = np.median(np.lib.stride_tricks.sliding_window_view(padded, (5, 5)), axis=(-2, -1)).astype(int)
    water = np.all(rgb == [47, 104, 139], axis=2)
    half = plan["size"] // 2
    sites = {}
    for site in plan["sites"]:
        tx, tz = (site["x"]+half)//4, (site["z"]+half)//4
        radius = 5 if site["id"] == "home" else (6 if site["id"] == "meteor" else 12)
        search = 40 if site["id"] == "meteor" else 24
        best = None
        for dz in range(-search, search+1, 2):
            for dx in range(-search, search+1, 2):
                x, z = tx+dx, tz+dz
                if site["id"] == "meteor":
                    home = sites["home"]
                    distance = math.hypot(x*4-half-home["x"], z*4-half-home["z"])
                    if not 420 <= distance <= 780:
                        continue
                patch = h[z-radius:z+radius+1, x-radius:x+radius+1]
                wet = water[z-radius:z+radius+1, x-radius:x+radius+1].mean()
                if water[z, x] or wet > 0.05:
                    continue
                score = patch.std()*3 + wet*1000 + math.hypot(dx, dz)*0.1
                if best is None or score < best[0]:
                    best = (score, x, z, round(float(np.median(patch))))
        if best is None:
            raise ValueError("No suitable dry site near " + site["id"])
        _, x, z, y = best
        sites[site["id"]] = {**site, "x": x*4-half, "z": z*4-half, "y": y+1}
    home, meteor = sites["home"], sites["meteor"]
    distance = math.hypot(meteor["x"]-home["x"], meteor["z"]-home["z"])
    if not 400 <= distance <= 800:
        raise ValueError(f"Meteor distance outside approved ring: {distance}")
    layout = {**plan, "sites": list(sites.values()), "meteor_distance": round(distance, 2)}
    dp = WORK / "server" / plan["id"] / "datapacks/svs_map_v1/data/svs_map/functions"
    jobs = []

    def emit(name, commands, bounds):
        path = dp / (name + ".mcfunction")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(commands)+"\n", encoding="utf-8")
        jobs.append({"id": name.replace("/", "_"), "function": "svs_map:"+name, "bounds": bounds})

    x, y, z = home["x"], home["y"], home["z"]
    def fill(x1, y1, z1, x2, y2, z2, material):
        return f"fill {x+x1} {y+y1} {z+z1} {x+x2} {y+y2} {z+z2} {material}"
    def block(dx, dy, dz, material):
        return f"setblock {x+dx} {y+dy} {z+dz} {material}"
    commands = [
        fill(-20, -3, -20, 20, -2, 20, "minecraft:dirt"),
        fill(-20, -1, -20, 20, -1, 20, "minecraft:coarse_dirt"),
        fill(-20, 0, -20, 20, 18, 20, "minecraft:air"),
        fill(-20, 0, -20, 20, 0, -20, "minecraft:oak_fence"),
        fill(-20, 0, 20, 20, 0, 20, "minecraft:oak_fence"),
        fill(-20, 0, -20, -20, 0, 20, "minecraft:oak_fence"),
        fill(20, 0, -20, 20, 0, 20, "minecraft:oak_fence"),
        fill(-2, 0, 20, 2, 2, 20, "minecraft:air"),
        fill(20, 0, -2, 20, 2, 2, "minecraft:air"),
        fill(-20, 0, -2, -20, 2, 2, "minecraft:air"),
    ]
    for hx, hz in [(-15, -14), (6, -14), (-15, 6)]:
        commands += [fill(hx, 0, hz, hx+8, 3, hz+8, "minecraft:oak_planks"),
                     fill(hx+1, 0, hz+1, hx+7, 3, hz+7, "minecraft:air"),
                     fill(hx-1, 4, hz-1, hx+9, 4, hz+9, "minecraft:oak_slab"),
                     fill(hx+3, 1, hz, hx+5, 2, hz, "minecraft:glass_pane"),
                     fill(hx+4, 0, hz+8, hx+4, 1, hz+8, "minecraft:air"),
                     block(hx+4, 0, hz+8, "minecraft:oak_door[facing=south,half=lower]"),
                     block(hx+4, 1, hz+8, "minecraft:oak_door[facing=south,half=upper]"),
                     block(hx+2, 0, hz+3, "minecraft:white_bed[facing=east,part=foot]"),
                     block(hx+3, 0, hz+3, "minecraft:white_bed[facing=east,part=head]"),
                     block(hx+2, 0, hz+5, "minecraft:white_bed[facing=east,part=foot]"),
                     block(hx+3, 0, hz+5, "minecraft:white_bed[facing=east,part=head]"),
                     block(hx+6, 3, hz+6, "minecraft:lantern[hanging=true]")]
    commands += [block(0, 0, 0, "minecraft:campfire"), block(7, 0, -8, "minecraft:crafting_table"),
                 block(8, 0, -8, "minecraft:furnace"), block(9, 0, -8, "minecraft:smithing_table"),
                 block(10, 0, -8, "minecraft:anvil"), block(11, 0, -8, "minecraft:blast_furnace"),
                 block(-14, 0, -8, "minecraft:barrel"),
                 block(-13, 0, -8, "minecraft:chest"),
                 f"setworldspawn {x} {y+1} {z+4}", "gamerule spawnRadius 0",
                 sign(x+2, y, z+3, ["借火村", "东 · 坠星旧道", "东南 · 失联医院", "西南 · 砂谷遗迹"]),
                 sign(x+2, y, z+5, ["初行地图 v1", "先安顿，再远征", "营地可休息与整备", "主线任务尚未接入"])]
    for vx, vz in [(-10, -9), (10, -9), (-10, 11)]:
        commands.append(f'summon minecraft:villager {x+vx} {y} {z+vz} {{Tags:["svs_map_resident"],PersistenceRequired:1b}}')
    emit("build/home", commands, [x-32, z-32, x+32, z+32])
    for site in sites.values():
        if not site.get("structure"):
            continue
        sx, sz = site["x"], site["z"]
        emit("build/"+site["id"], [f"data modify storage svs_map:build {site['id']} set value 0b", f"execute store success storage svs_map:build {site['id']} byte 1 positioned {sx} 0 {sz} positioned over motion_blocking_no_leaves run place structure {site['structure']} ~ ~ ~"], [sx-112, sz-112, sx+112, sz+112])
    paths = {}
    for route in plan["routes"]:
        a, b = sites[route["from"]], sites[route["to"]]
        ga = ((a["x"]+half)//4, (a["z"]+half)//4)
        gb = ((b["x"]+half)//4, (b["z"]+half)//4)
        grid_path = astar(h, water, ga, gb)
        points = []
        for aa, bb in zip(grid_path, grid_path[1:]):
            pa, pb = (aa[0]*4-half, aa[1]*4-half), (bb[0]*4-half, bb[1]*4-half)
            for px, pz in line(pa, pb)[:-1]:
                yy = max(64, int(h[(pz+half)//4, (px+half)//4]))
                points.append((px, yy, pz))
        # Limit one-block steps on the finished path in both directions.
        for indices in [range(1, len(points)), range(len(points)-2, -1, -1)]:
            for i in indices:
                neighbor = i-1 if isinstance(indices, range) and indices.step == 1 else i+1
                px, yy, pz = points[i]
                points[i] = (px, max(points[neighbor][1]-1, min(points[neighbor][1]+1, yy)), pz)
        keep = []
        for px, yy, pz in points:
            if any(abs(px-s["x"]) < (24 if s["id"] == "home" else 96) and abs(pz-s["z"]) < (24 if s["id"] == "home" else 96) for s in [a, b]):
                continue
            keep.append((px, yy, pz))
        paths[route["id"]] = keep
        for number, start in enumerate(range(0, len(keep), 40)):
            batch = keep[start:start+40]
            commands = []
            for j, (px, yy, pz) in enumerate(batch):
                material = "minecraft:oak_planks" if yy <= 64 or water[(pz+half)//4, (px+half)//4] else "minecraft:coarse_dirt"
                commands += [f"fill {px-1} {yy-4} {pz-1} {px+1} {yy-1} {pz+1} minecraft:stone replace minecraft:air",
                             f"fill {px-1} {yy} {pz-1} {px+1} {yy} {pz+1} {material}",
                             f"fill {px-1} {yy+1} {pz-1} {px+1} {yy+5} {pz+1} minecraft:air"]
                if material == "minecraft:oak_planks" and (start+j) % 16 == 0:
                    commands.append(f"fill {px} {yy-12} {pz} {px} {yy-1} {pz} minecraft:oak_log replace minecraft:water")
                if (start+j) % 48 == 0:
                    commands += [f"setblock {px+2} {yy+1} {pz} minecraft:oak_fence", f"setblock {px+2} {yy+2} {pz} minecraft:lantern"]
            if batch:
                bx = [p[0] for p in batch]; bz = [p[2] for p in batch]
                emit(f"roads/{route['id']}_{number:03d}", commands, [min(bx)-4, min(bz)-4, max(bx)+4, max(bz)+4])
        if keep:
            px, yy, pz = keep[-1]
            emit("signs/"+route["id"], [sign(px+2, yy+1, pz, [b["name"], "前方区域", "沿遗迹边缘寻找入口", "原路可返回借火村"])], [px-16, pz-16, px+16, pz+16])
    layout["paths"] = {key: [list(p) for p in value] for key, value in paths.items()}
    (WORK / "layout.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (WORK / "build-jobs.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"sites": layout["sites"], "meteor_distance": distance, "jobs": len(jobs), "road_blocks": {k: len(v) for k, v in paths.items()}}, ensure_ascii=False, indent=2))


def repair():
    """Repair the existing v1 draft without refitting or regenerating landmarks."""
    layout = json.loads((WORK / "layout.json").read_text(encoding="utf-8"))
    dp = WORK / "server" / layout["id"] / "datapacks/svs_map_v1/data/svs_map/functions"
    jobs = []
    def emit(name, commands, bounds):
        path = dp / (name+".mcfunction")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(commands)+"\n", encoding="utf-8")
        jobs.append({"id": name.replace("/", "_"), "function": "svs_map:"+name, "bounds": bounds})
    home = next(s for s in layout["sites"] if s["id"] == "home")
    x, y, z = home["x"], home["y"], home["z"]
    def block(dx, dz, name):
        return f"setblock {x+dx} {y} {z+dz} {name}"
    commands = [block(dx, dz, "minecraft:air") for dx, dz in [(7, -11), (7, -10), (8, -11), (9, -11), (10, -11), (-14, -11), (-13, -11)]]
    for hx, hz in [(-15, -14), (6, -14), (-15, 6)]:
        for dz in [3, 5]:
            commands += [block(hx+2, hz+dz, "minecraft:white_bed[facing=east,part=foot]"), block(hx+3, hz+dz, "minecraft:white_bed[facing=east,part=head]")]
    for dx, dz, material in [(7,-8,"crafting_table"),(8,-8,"furnace"),(9,-8,"smithing_table"),(10,-8,"anvil"),(11,-8,"blast_furnace"),(-14,-8,"barrel"),(-13,-8,"chest")]:
        commands.append(block(dx, dz, "minecraft:"+material))
    emit("repairs/home", commands, [x-32,z-32,x+32,z+32])
    for route, old in layout["paths"].items():
        points = [(px,max(64,yy),pz) for px,yy,pz in old]
        layout["paths"][route] = points
        for number, start in enumerate(range(0,len(points),40)):
            batch = points[start:start+40]
            commands = []
            for j, (px,yy,pz) in enumerate(batch):
                material = "minecraft:oak_planks" if yy <= 64 else "minecraft:coarse_dirt"
                commands += [f"fill {px-1} {yy-4} {pz-1} {px+1} {yy-1} {pz+1} minecraft:stone replace minecraft:air",
                             f"fill {px-1} {yy} {pz-1} {px+1} {yy} {pz+1} {material}",
                             f"fill {px-1} {yy+1} {pz-1} {px+1} {yy+5} {pz+1} minecraft:air"]
                if yy <= 64 and (start+j)%16 == 0:
                    commands.append(f"fill {px} {yy-12} {pz} {px} {yy-1} {pz} minecraft:oak_log replace minecraft:water")
                if (start+j)%48 == 0:
                    commands += [f"setblock {px+2} {yy+1} {pz} minecraft:oak_fence",f"setblock {px+2} {yy+2} {pz} minecraft:lantern"]
            bx=[p[0] for p in batch];bz=[p[2] for p in batch]
            emit(f"repairs/{route}_{number:03d}",commands,[min(bx)-4,min(bz)-4,max(bx)+4,max(bz)+4])
    (WORK / "layout.json").write_text(json.dumps(layout,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (WORK / "repair-jobs.json").write_text(json.dumps(jobs,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Prepared repair jobs:",len(jobs))


if __name__ == "__main__":
    repair() if "--repair" in sys.argv else main()
